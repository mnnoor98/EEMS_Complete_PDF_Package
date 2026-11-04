using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using EEMS.Api.Authentication;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using EEMS.Api.Security;
using EEMS.Modules.Tenants.Infrastructure;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Controllers;

[ApiController]
[Route("api/v1/auth")]
public sealed class AuthenticationController(
    LocalAuthenticationService authenticationService,
    TenantsDbContext tenantsDbContext,
    ITenantContext tenantContext) : ControllerBase
{
    [AllowAnonymous]
    [HttpPost("login")]
    [EnableRateLimiting(ApiSecurityExtensions.AuthenticationRateLimitPolicy)]
    [ProducesResponseType<TokenResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<TokenResponse>> Login(LoginRequest request, CancellationToken cancellationToken)
    {
        var tenantId = await tenantsDbContext.Tenants
            .Where(tenant => tenant.Code == request.TenantId)
            .Select(tenant => (Guid?)tenant.Id)
            .SingleOrDefaultAsync(cancellationToken);
        if (tenantId is null) return Unauthorized();

        var result = await authenticationService.LoginAsync(tenantId.Value, request.Username, request.Password, cancellationToken);
        return result is null ? Unauthorized() : Ok(TokenResponse.From(result));
    }

    [AllowAnonymous]
    [HttpPost("refresh")]
    [EnableRateLimiting(ApiSecurityExtensions.AuthenticationRateLimitPolicy)]
    [ProducesResponseType<TokenResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<TokenResponse>> Refresh(RefreshRequest request, CancellationToken cancellationToken)
    {
        var result = await authenticationService.RefreshAsync(request.TenantId, request.RefreshToken, cancellationToken);
        return result is null ? Unauthorized() : Ok(TokenResponse.From(result));
    }

    [Authorize]
    [HttpPost("logout")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> Logout(LogoutRequest request, CancellationToken cancellationToken)
    {
        var subject = User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
        if (!Guid.TryParse(subject, out var userId)) return Unauthorized();
        await authenticationService.LogoutAsync(tenantContext.TenantId, userId, request.RefreshToken, cancellationToken);
        return NoContent();
    }

    [Authorize]
    [HttpPost("change-password")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> ChangePassword(ChangePasswordRequest request, CancellationToken cancellationToken)
    {
        var subject = User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
        if (!Guid.TryParse(subject, out var userId)) return Unauthorized();
        var changed = await authenticationService.ChangePasswordAsync(
            tenantContext.TenantId,
            userId,
            request.CurrentPassword,
            request.NewPassword,
            cancellationToken);
        return changed ? NoContent() : BadRequest(new { error = "password_change_failed" });
    }
}

public sealed record LoginRequest(
    [Required, RegularExpression("^[0-9]{10}$")] string TenantId,
    [Required, MaxLength(200)] string Username,
    [Required, MaxLength(200)] string Password);

public sealed record RefreshRequest(Guid TenantId, [Required, MaxLength(500)] string RefreshToken);

public sealed record LogoutRequest([Required, MaxLength(500)] string RefreshToken);

public sealed record ChangePasswordRequest(
    [Required, MaxLength(200)] string CurrentPassword,
    [Required, MinLength(12), MaxLength(200)] string NewPassword);

public sealed record TokenResponse(
    string AccessToken,
    DateTimeOffset AccessTokenExpiresAtUtc,
    string RefreshToken,
    DateTimeOffset RefreshTokenExpiresAtUtc,
    bool PasswordChangeRequired)
{
    public static TokenResponse From(TokenPair pair) =>
        new(
            pair.AccessToken,
            pair.AccessTokenExpiresAtUtc,
            pair.RefreshToken,
            pair.RefreshTokenExpiresAtUtc,
            pair.PasswordChangeRequired);
}
