using EEMS.Modules.Elections.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EEMS.Modules.Elections;

public static class ElectionsModule
{
    public static IServiceCollection AddElectionsModule(this IServiceCollection services,IConfiguration configuration)
    {var connection=configuration.GetConnectionString("EemsDatabase");if(string.IsNullOrWhiteSpace(connection))throw new InvalidOperationException("ConnectionStrings:EemsDatabase is required.");services.AddDbContext<ElectionsDbContext>(options=>options.UseNpgsql(connection));return services;}
}
