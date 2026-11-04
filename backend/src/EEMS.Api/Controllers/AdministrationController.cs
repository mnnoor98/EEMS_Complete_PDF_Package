using System.ComponentModel.DataAnnotations;
using EEMS.Api.Administration;
using EEMS.Api.Authorization;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/admin")]
public sealed class AdministrationController(IdentityAdministrationService administration) : ControllerBase
{
    [HttpGet("users")]
    [Authorize(Policy = PermissionCodes.UsersRead)]
    public async Task<ActionResult<IReadOnlyList<UserSummary>>> GetUsers(CancellationToken cancellationToken) =>
        Ok(await administration.GetUsersAsync(cancellationToken));

    [HttpPost("users")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<ActionResult<UserSummary>> CreateUser(CreateUserRequest request, CancellationToken cancellationToken)
    {
        var created = await administration.CreateUserAsync(
            new CreateUserCommand(request.Username, request.DisplayName, request.Email, request.InitialPassword), cancellationToken);
        return created is null ? Conflict(new { error = "username_exists" }) : CreatedAtAction(nameof(GetUsers), created);
    }

    [HttpPut("users/{userId:guid}/active")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<IActionResult> SetUserActive(Guid userId, SetActiveRequest request, CancellationToken cancellationToken) =>
        await administration.SetUserActiveAsync(userId, request.IsActive, cancellationToken) ? NoContent() : NotFound();

    [HttpPost("users/{userId:guid}/roles/{roleId:guid}")]
    [Authorize(Policy = PermissionCodes.RolesManage)]
    public async Task<IActionResult> AssignRole(Guid userId, Guid roleId, CancellationToken cancellationToken) =>
        await administration.AssignRoleAsync(userId, roleId, cancellationToken) ? NoContent() : NotFound();

    [HttpGet("roles")]
    [Authorize(Policy = PermissionCodes.RolesRead)]
    public async Task<ActionResult<IReadOnlyList<RoleSummary>>> GetRoles(CancellationToken cancellationToken) =>
        Ok(await administration.GetRolesAsync(cancellationToken));

    [HttpPost("roles")]
    [Authorize(Policy = PermissionCodes.RolesManage)]
    public async Task<ActionResult<RoleSummary>> CreateRole(CreateRoleRequest request, CancellationToken cancellationToken)
    {
        var created = await administration.CreateRoleAsync(request.Code, request.Name, cancellationToken);
        return created is null ? Conflict(new { error = "role_code_exists" }) : CreatedAtAction(nameof(GetRoles), created);
    }

    [HttpPost("roles/{roleId:guid}/permissions")]
    [Authorize(Policy = PermissionCodes.RolesManage)]
    public async Task<IActionResult> AssignPermission(
        Guid roleId,
        AssignPermissionRequest request,
        CancellationToken cancellationToken) =>
        await administration.AssignPermissionAsync(roleId, request.PermissionCode, cancellationToken) ? NoContent() : NotFound();

    [HttpGet("dashboard")]
    [Authorize(Policy = PermissionCodes.DashboardRead)]
    public async Task<ActionResult<AdministrationDashboard>> GetDashboard(CancellationToken cancellationToken) =>
        Ok(await administration.GetDashboardAsync(cancellationToken));
}

public sealed record CreateUserRequest(
    [Required, MaxLength(200)] string Username,
    [Required, MaxLength(200)] string DisplayName,
    [EmailAddress, MaxLength(320)] string? Email,
    [Required, MinLength(12), MaxLength(200)] string InitialPassword);
public sealed record SetActiveRequest(bool IsActive);
public sealed record CreateRoleRequest([Required, MaxLength(80)] string Code, [Required, MaxLength(120)] string Name);
public sealed record AssignPermissionRequest([Required, MaxLength(120)] string PermissionCode);
