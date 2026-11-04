using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using EEMS.Modules.Tenants.Infrastructure;

namespace EEMS.Modules.Tenants;

public static class TenantsModule
{
    public static IServiceCollection AddTenantsModule(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("EemsDatabase");
        if (string.IsNullOrWhiteSpace(connectionString))
        {
            throw new InvalidOperationException("ConnectionStrings:EemsDatabase must be provided through user secrets or environment configuration.");
        }

        services.AddDbContext<TenantsDbContext>(options => options.UseNpgsql(connectionString));
        return services;
    }
}
