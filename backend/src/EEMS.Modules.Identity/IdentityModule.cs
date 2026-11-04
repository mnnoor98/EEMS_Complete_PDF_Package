using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Identity.Security;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EEMS.Modules.Identity;

public static class IdentityModule
{
    public static IServiceCollection AddIdentityModule(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("EemsDatabase");
        if (string.IsNullOrWhiteSpace(connectionString))
            throw new InvalidOperationException("ConnectionStrings:EemsDatabase must be provided through user secrets or environment configuration.");

        services.AddHttpContextAccessor();
        services.AddScoped<ITenantContext, ClaimsTenantContext>();
        services.AddScoped<IAuthorizationHandler, PermissionAuthorizationHandler>();
        services.AddDbContext<IdentityDbContext>(options => options.UseNpgsql(connectionString));
        return services;
    }
}
