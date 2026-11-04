using Microsoft.AspNetCore.Authorization;

namespace EEMS.Modules.Identity.Security;

public sealed class PermissionAuthorizationHandler : AuthorizationHandler<PermissionRequirement>
{
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, PermissionRequirement requirement)
    {
        if (context.User.Identity?.IsAuthenticated == true &&
            context.User.Claims.Any(claim => claim.Type == IdentityClaimTypes.Permission &&
                                             string.Equals(claim.Value, requirement.PermissionCode, StringComparison.OrdinalIgnoreCase)))
        {
            context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}
