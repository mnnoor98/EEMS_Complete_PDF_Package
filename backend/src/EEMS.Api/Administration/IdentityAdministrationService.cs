using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Reporting.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Administration;

public sealed class IdentityAdministrationService(
    IdentityDbContext dbContext,
    CandidatesDbContext candidatesDbContext,
    ReportingDbContext reportingDbContext,
    ITenantContext tenantContext,
    IPasswordHasher<User> passwordHasher)
{
    public async Task<IReadOnlyList<UserSummary>> GetUsersAsync(CancellationToken cancellationToken)
    {
        var users = await (from membership in dbContext.TenantUsers
               join user in dbContext.Users on membership.UserId equals user.Id
               where membership.TenantId == tenantContext.TenantId
               orderby user.DisplayName
               select new { User = user, membership.IsActive, membership.CandidateId })
            .AsNoTracking().ToListAsync(cancellationToken);

        var candidateIds = users.Where(u => u.CandidateId.HasValue).Select(u => u.CandidateId!.Value).Distinct().ToList();
        var candidates = await candidatesDbContext.Candidates
            .Where(c => c.TenantId == tenantContext.TenantId && candidateIds.Contains(c.Id))
            .ToDictionaryAsync(c => c.Id, c => c.Name, cancellationToken);

        var roles = await (from assignment in dbContext.UserRoles join role in dbContext.Roles on assignment.RoleId equals role.Id
                           where assignment.TenantId == tenantContext.TenantId
                           select new { assignment.UserId, role.Code }).AsNoTracking().ToListAsync(cancellationToken);
        return users.Select(item => new UserSummary(
            item.User.Id,
            item.User.ExternalSubject,
            item.User.DisplayName,
            item.User.Email,
            item.IsActive,
            roles.Where(role => role.UserId == item.User.Id).Select(role => role.Code).Order().ToArray(),
            item.CandidateId,
            item.CandidateId.HasValue && candidates.TryGetValue(item.CandidateId.Value, out var cName) ? cName : null
        )).ToArray();
    }

    public async Task<UserSummary?> CreateUserAsync(CreateUserCommand command, CancellationToken cancellationToken)
    {
        var username = command.Username.Trim();
        if (await dbContext.Users.AnyAsync(item => item.ExternalSubject == username, cancellationToken)) return null;
        var user = User.Create(username, command.DisplayName, command.Email);
        dbContext.Users.Add(user);
        dbContext.TenantUsers.Add(TenantUser.Create(tenantContext.TenantId, user.Id, command.CandidateId));
        dbContext.PasswordCredentials.Add(PasswordCredential.Create(
            user.Id,
            passwordHasher.HashPassword(user, command.InitialPassword)));
        await dbContext.SaveChangesAsync(cancellationToken);

        string? candidateName = null;
        if (command.CandidateId.HasValue)
        {
            var candidate = await candidatesDbContext.Candidates
                .SingleOrDefaultAsync(c => c.TenantId == tenantContext.TenantId && c.Id == command.CandidateId.Value, cancellationToken);
            candidateName = candidate?.Name;
        }

        return new UserSummary(user.Id, user.ExternalSubject, user.DisplayName, user.Email, true, [], command.CandidateId, candidateName);
    }

    public async Task<bool> SetUserActiveAsync(Guid userId, bool active, CancellationToken cancellationToken)
    {
        var membership = await dbContext.TenantUsers.SingleOrDefaultAsync(
            item => item.TenantId == tenantContext.TenantId && item.UserId == userId, cancellationToken);
        if (membership is null) return false;
        if (active) membership.Enable(); else membership.Disable();
        if (!active)
        {
            var tokens = await dbContext.RefreshTokens
                .Where(item => item.TenantId == tenantContext.TenantId && item.UserId == userId && item.RevokedAtUtc == null)
                .ToListAsync(cancellationToken);
            foreach (var token in tokens) token.Revoke();
        }
        await dbContext.SaveChangesAsync(cancellationToken);
        return true;
    }

    public async Task<IReadOnlyList<RoleSummary>> GetRolesAsync(CancellationToken cancellationToken)
    {
        var roles = await dbContext.Roles.Where(item => item.TenantId == tenantContext.TenantId)
            .OrderBy(item => item.Name).AsNoTracking().ToListAsync(cancellationToken);
        var assignments = await (from rolePermission in dbContext.RolePermissions
                                 join permission in dbContext.Permissions on rolePermission.PermissionId equals permission.Id
                                 where rolePermission.TenantId == tenantContext.TenantId
                                 select new { rolePermission.RoleId, permission.Code })
            .AsNoTracking().ToListAsync(cancellationToken);
        return roles.Select(role => new RoleSummary(
            role.Id,
            role.Code,
            role.Name,
            role.IsActive,
            assignments.Where(item => item.RoleId == role.Id).Select(item => item.Code).Order().ToArray())).ToArray();
    }

    public async Task<IReadOnlyList<PermissionSummary>> GetPermissionsAsync(CancellationToken cancellationToken) =>
        await dbContext.Permissions.Where(item => item.IsActive).OrderBy(item => item.Module).ThenBy(item => item.Name)
            .Select(item => new PermissionSummary(item.Code, item.Name, item.Module)).AsNoTracking().ToListAsync(cancellationToken);

    public async Task<RoleSummary?> CreateRoleAsync(string code, string name, CancellationToken cancellationToken)
    {
        var normalized = code.Trim().ToUpperInvariant();
        if (await dbContext.Roles.AnyAsync(
                item => item.TenantId == tenantContext.TenantId && item.Code == normalized, cancellationToken)) return null;
        var role = Role.Create(tenantContext.TenantId, normalized, name);
        dbContext.Roles.Add(role);
        await dbContext.SaveChangesAsync(cancellationToken);
        return new RoleSummary(role.Id, role.Code, role.Name, role.IsActive, []);
    }

    public async Task<bool> AssignPermissionAsync(Guid roleId, string permissionCode, CancellationToken cancellationToken)
    {
        var roleExists = await dbContext.Roles.AnyAsync(
            item => item.TenantId == tenantContext.TenantId && item.Id == roleId, cancellationToken);
        var normalized = permissionCode.Trim().ToLowerInvariant();
        var permission = await dbContext.Permissions.SingleOrDefaultAsync(item => item.Code == normalized, cancellationToken);
        if (!roleExists || permission is null) return false;
        if (!await dbContext.RolePermissions.AnyAsync(item => item.TenantId == tenantContext.TenantId &&
                                                               item.RoleId == roleId && item.PermissionId == permission.Id,
                cancellationToken))
        {
            dbContext.RolePermissions.Add(new RolePermission(tenantContext.TenantId, roleId, permission.Id));
            await dbContext.SaveChangesAsync(cancellationToken);
        }
        return true;
    }

    public async Task<bool> AssignRoleAsync(Guid userId, Guid roleId, CancellationToken cancellationToken)
    {
        var userExists = await dbContext.TenantUsers.AnyAsync(
            item => item.TenantId == tenantContext.TenantId && item.UserId == userId, cancellationToken);
        var roleExists = await dbContext.Roles.AnyAsync(
            item => item.TenantId == tenantContext.TenantId && item.Id == roleId, cancellationToken);
        if (!userExists || !roleExists) return false;
        if (!await dbContext.UserRoles.AnyAsync(item => item.TenantId == tenantContext.TenantId &&
                                                        item.UserId == userId && item.RoleId == roleId,
                cancellationToken))
        {
            dbContext.UserRoles.Add(new UserRole(tenantContext.TenantId, userId, roleId));
            await dbContext.SaveChangesAsync(cancellationToken);
        }
        return true;
    }

    public async Task<bool> AssignCandidateAsync(Guid userId, Guid? candidateId, CancellationToken cancellationToken)
    {
        var membership = await dbContext.TenantUsers.SingleOrDefaultAsync(
            item => item.TenantId == tenantContext.TenantId && item.UserId == userId, cancellationToken);
        if (membership is null) return false;

        if (candidateId.HasValue)
        {
            var candExists = await candidatesDbContext.Candidates.AnyAsync(
                c => c.TenantId == tenantContext.TenantId && c.Id == candidateId.Value, cancellationToken);
            if (!candExists) return false;
        }

        membership.AssignCandidate(candidateId);
        await dbContext.SaveChangesAsync(cancellationToken);
        return true;
    }

    public async Task<AdministrationDashboard> GetDashboardAsync(CancellationToken cancellationToken) =>
        new(
            await dbContext.TenantUsers.CountAsync(item => item.TenantId == tenantContext.TenantId, cancellationToken),
            await dbContext.TenantUsers.CountAsync(item => item.TenantId == tenantContext.TenantId && item.IsActive, cancellationToken),
            await dbContext.Roles.CountAsync(item => item.TenantId == tenantContext.TenantId && item.IsActive, cancellationToken),
            await reportingDbContext.SecurityEvents.Where(item => item.TenantId == tenantContext.TenantId).OrderByDescending(item => item.OccurredAtUtc).Take(25)
                .Select(item => new SecurityEventSummary(item.Id, item.UserId, item.EventType, item.Source, item.Detail, item.CorrelationId, item.OccurredAtUtc)).ToListAsync(cancellationToken));
}

public sealed record CreateUserCommand(string Username, string DisplayName, string? Email, string InitialPassword, Guid? CandidateId = null);
public sealed record UserSummary(Guid UserId, string Username, string DisplayName, string? Email, bool IsActive, IReadOnlyList<string> RoleCodes, Guid? CandidateId = null, string? CandidateName = null);
public sealed record RoleSummary(Guid RoleId, string Code, string Name, bool IsActive, IReadOnlyList<string> Permissions);
public sealed record PermissionSummary(string Code, string Name, string Module);
public sealed record SecurityEventSummary(Guid SecurityEventId, Guid? UserId, string EventType, string Source, string Detail, string CorrelationId, DateTimeOffset OccurredAtUtc);
public sealed record AdministrationDashboard(int TotalUsers, int ActiveUsers, int ActiveRoles, IReadOnlyList<SecurityEventSummary> RecentSecurityEvents);
