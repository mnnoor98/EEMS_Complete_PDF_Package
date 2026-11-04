using EEMS.Modules.Identity.Security;

namespace EEMS.Api.Authentication;

public sealed class PasswordChangeMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context)
    {
        var changeRequired = context.User.FindFirst(IdentityClaimTypes.PasswordChangeRequired)?.Value;
        var permittedPath = context.Request.Path.Equals("/api/v1/auth/change-password", StringComparison.OrdinalIgnoreCase) ||
                            context.Request.Path.Equals("/api/v1/auth/logout", StringComparison.OrdinalIgnoreCase);

        if (string.Equals(changeRequired, bool.TrueString, StringComparison.OrdinalIgnoreCase) && !permittedPath)
        {
            context.Response.StatusCode = StatusCodes.Status403Forbidden;
            await context.Response.WriteAsJsonAsync(new { error = "password_change_required" });
            return;
        }

        await next(context);
    }
}
