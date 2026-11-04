using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Identity.Security;
using EEMS.Modules.Tenants.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace EEMS.Api.Authorization;

public static class AuthorizationSetupExtensions
{
    public static IServiceCollection AddPermissionAuthorization(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddOptions<AuthorizationOptions>()
            .Bind(configuration.GetSection(AuthorizationOptions.SectionName))
            .Validate(IsValid, "Authorization setup requires valid tenant, administrator, role, and permission definitions.")
            .ValidateOnStart();
        services.AddAuthorization(options =>
        {
            AddPolicy(options, PermissionCodes.UsersRead);
            AddPolicy(options, PermissionCodes.UsersManage);
            AddPolicy(options, PermissionCodes.RolesRead);
            AddPolicy(options, PermissionCodes.RolesManage);
            AddPolicy(options, PermissionCodes.DashboardRead);
            AddPolicy(options, PermissionCodes.ElectionsRead);
            AddPolicy(options, PermissionCodes.ElectionsManage);
            AddPolicy(options, PermissionCodes.WorkforceRead);
            AddPolicy(options, PermissionCodes.WorkforceManage);
            AddPolicy(options, PermissionCodes.PollingRead);
            AddPolicy(options, PermissionCodes.PollingManage);
            AddPolicy(options, PermissionCodes.ResultsRead);
            AddPolicy(options, PermissionCodes.ResultsManage);
            AddPolicy(options, PermissionCodes.ReportingRead);
            AddPolicy(options, PermissionCodes.ReportingManage);
        });
        return services;
    }

    public static async Task InitializePermissionAuthorizationAsync(this IServiceProvider services, CancellationToken cancellationToken = default)
    {
        await using var scope = services.CreateAsyncScope();
        var options = scope.ServiceProvider.GetRequiredService<IOptions<AuthorizationOptions>>().Value;
        var tenantDb = scope.ServiceProvider.GetRequiredService<TenantsDbContext>();
        var tenantCode = options.InitialTenantCode.Trim().ToUpperInvariant();
        var tenant = await tenantDb.Tenants.SingleAsync(item => item.Code == tenantCode, cancellationToken);
        var identityDb = scope.ServiceProvider.GetRequiredService<IdentityDbContext>();

        foreach (var definition in options.Permissions)
        {
            var code = definition.Code.Trim().ToLowerInvariant();
            if (!await identityDb.Permissions.AnyAsync(item => item.Code == code, cancellationToken))
                identityDb.Permissions.Add(Permission.Create(code, definition.Name, definition.Module));
        }
        await identityDb.SaveChangesAsync(cancellationToken);

        await using var transaction = await identityDb.Database.BeginTransactionAsync(cancellationToken);
        await identityDb.Database.ExecuteSqlInterpolatedAsync(
            $"SELECT set_config('app.tenant_id', {tenant.Id.ToString()}, true)", cancellationToken);
        var administrator = await identityDb.Users.SingleAsync(
            item => item.ExternalSubject == options.InitialAdministratorUsername, cancellationToken);
        var roleCode = options.AdministratorRoleCode.Trim().ToUpperInvariant();
        var role = await identityDb.Roles.SingleOrDefaultAsync(
            item => item.TenantId == tenant.Id && item.Code == roleCode, cancellationToken);
        if (role is null)
        {
            role = Role.Create(tenant.Id, roleCode, options.AdministratorRoleName);
            identityDb.Roles.Add(role);
            await identityDb.SaveChangesAsync(cancellationToken);
        }

        var configuredCodes = options.Permissions.Select(item => item.Code.Trim().ToLowerInvariant()).ToArray();
        var permissionIds = await identityDb.Permissions
            .Where(item => configuredCodes.Contains(item.Code)).Select(item => item.Id).ToListAsync(cancellationToken);
        var assignedIds = await identityDb.RolePermissions
            .Where(item => item.TenantId == tenant.Id && item.RoleId == role.Id)
            .Select(item => item.PermissionId).ToListAsync(cancellationToken);
        foreach (var permissionId in permissionIds.Except(assignedIds))
            identityDb.RolePermissions.Add(new RolePermission(tenant.Id, role.Id, permissionId));

        if (!await identityDb.UserRoles.AnyAsync(
                item => item.TenantId == tenant.Id && item.UserId == administrator.Id && item.RoleId == role.Id,
                cancellationToken))
            identityDb.UserRoles.Add(new UserRole(tenant.Id, administrator.Id, role.Id));

        await identityDb.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);
    }

    private static void AddPolicy(Microsoft.AspNetCore.Authorization.AuthorizationOptions options, string code) =>
        options.AddPolicy(code, policy => policy.AddRequirements(new PermissionRequirement(code)));

    private static bool IsValid(AuthorizationOptions options) =>
        !string.IsNullOrWhiteSpace(options.InitialTenantCode) &&
        !string.IsNullOrWhiteSpace(options.InitialAdministratorUsername) &&
        !string.IsNullOrWhiteSpace(options.AdministratorRoleCode) &&
        !string.IsNullOrWhiteSpace(options.AdministratorRoleName) &&
        options.Permissions.Length > 0 &&
        options.Permissions.All(item => !string.IsNullOrWhiteSpace(item.Code) &&
                                        !string.IsNullOrWhiteSpace(item.Name) &&
                                        !string.IsNullOrWhiteSpace(item.Module));
}
