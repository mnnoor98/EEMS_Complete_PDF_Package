using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Tenants.Domain;
using EEMS.Modules.Tenants.Infrastructure;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace EEMS.Api.Bootstrap;

public static class BootstrapExtensions
{
    private static readonly Action<ILogger, Guid, Exception?> LogAdministratorCreated =
        LoggerMessage.Define<Guid>(
            LogLevel.Information,
            new EventId(1001, "InitialAdministratorCreated"),
            "Initial administrator created for tenant {TenantId}. Disable Bootstrap:Enabled now.");

    public static IServiceCollection AddInitialBootstrap(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddOptions<BootstrapOptions>()
            .Bind(configuration.GetSection(BootstrapOptions.SectionName))
            .Validate(IsValid, "Enabled bootstrap requires tenant and administrator settings, including a password of at least 6 characters.")
            .ValidateOnStart();
        return services;
    }

    public static async Task BootstrapInitialAdminAsync(this IServiceProvider services, CancellationToken cancellationToken = default)
    {
        await using var scope = services.CreateAsyncScope();
        var options = scope.ServiceProvider.GetRequiredService<IOptions<BootstrapOptions>>().Value;
        if (!options.Enabled) return;

        var identityDb = scope.ServiceProvider.GetRequiredService<IdentityDbContext>();
        if (await identityDb.Users.AnyAsync(cancellationToken)) return;

        var tenantDb = scope.ServiceProvider.GetRequiredService<TenantsDbContext>();
        var tenantCode = options.TenantCode.Trim().ToUpperInvariant();
        var tenant = await tenantDb.Tenants.SingleOrDefaultAsync(item => item.Code == tenantCode, cancellationToken);
        if (tenant is null)
        {
            tenant = Tenant.Create(tenantCode, options.TenantName);
            tenantDb.Tenants.Add(tenant);
            await tenantDb.SaveChangesAsync(cancellationToken);
        }

        await using var transaction = await identityDb.Database.BeginTransactionAsync(cancellationToken);
        await identityDb.Database.ExecuteSqlInterpolatedAsync(
            $"SELECT set_config('app.tenant_id', {tenant.Id.ToString()}, true)",
            cancellationToken);

        if (await identityDb.Users.AnyAsync(cancellationToken)) return;
        var user = User.Create(options.AdminUsername, options.AdminDisplayName, options.AdminEmail);
        var passwordHasher = scope.ServiceProvider.GetRequiredService<IPasswordHasher<User>>();
        var credential = PasswordCredential.Create(user.Id, passwordHasher.HashPassword(user, options.AdminPassword));

        identityDb.Users.Add(user);
        identityDb.TenantUsers.Add(TenantUser.Create(tenant.Id, user.Id));
        identityDb.PasswordCredentials.Add(credential);
        await identityDb.SaveChangesAsync(cancellationToken);
        await transaction.CommitAsync(cancellationToken);

        var logger = scope.ServiceProvider.GetRequiredService<ILoggerFactory>().CreateLogger("InitialBootstrap");
        LogAdministratorCreated(logger, tenant.Id, null);
    }

    private static bool IsValid(BootstrapOptions options) =>
        !options.Enabled ||
        (!string.IsNullOrWhiteSpace(options.TenantCode) &&
         !string.IsNullOrWhiteSpace(options.TenantName) &&
         !string.IsNullOrWhiteSpace(options.AdminUsername) &&
         !string.IsNullOrWhiteSpace(options.AdminDisplayName) &&
         options.AdminPassword.Length >= 6);
}
