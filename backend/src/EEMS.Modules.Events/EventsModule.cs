using EEMS.Modules.Events.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace EEMS.Modules.Events;

public static class EventsModule
{
    public static IServiceCollection AddEventsModule(this IServiceCollection services, IConfiguration configuration)
    {
        var connection = configuration.GetConnectionString("EemsDatabase");
        if (string.IsNullOrWhiteSpace(connection))
            throw new InvalidOperationException("ConnectionStrings:EemsDatabase is required.");
        services.AddDbContext<EventsDbContext>(options => options.UseNpgsql(connection));
        return services;
    }
}
