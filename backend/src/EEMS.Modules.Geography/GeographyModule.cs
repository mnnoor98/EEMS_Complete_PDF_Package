using EEMS.Modules.Geography.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EEMS.Modules.Geography;

public static class GeographyModule
{
    public static IServiceCollection AddGeographyModule(this IServiceCollection services,IConfiguration configuration)
    {
        var connection=configuration.GetConnectionString("EemsDatabase");
        if(string.IsNullOrWhiteSpace(connection)) throw new InvalidOperationException("ConnectionStrings:EemsDatabase is required.");
        services.AddDbContext<GeographyDbContext>(options=>options.UseNpgsql(connection)); return services;
    }
}
