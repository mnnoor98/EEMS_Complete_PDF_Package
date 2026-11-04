using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Events.Infrastructure;
using EEMS.Modules.Finance.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Inventory.Infrastructure;
using EEMS.Modules.Operations.Infrastructure;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Reporting.Infrastructure;
using EEMS.Modules.Results.Infrastructure;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.Modules.Tenants.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;

namespace EEMS.Api.Tenancy;

public sealed class TenantTransactionMiddleware(RequestDelegate next)
{
    private static readonly Type[] TenantDbContextTypes =
    [
        typeof(TenantsDbContext),
        typeof(IdentityDbContext),
        typeof(GeographyDbContext),
        typeof(ElectionsDbContext),
        typeof(CandidatesDbContext),
        typeof(PollingDbContext),
        typeof(TeamsDbContext),
        typeof(EventsDbContext),
        typeof(FinanceDbContext),
        typeof(InventoryDbContext),
        typeof(OperationsDbContext),
        typeof(ResultsDbContext),
        typeof(ReportingDbContext)
    ];

    public async Task InvokeAsync(HttpContext httpContext, ITenantContext tenantContext)
    {
        if (!tenantContext.IsAvailable)
        {
            await next(httpContext);
            return;
        }

        var transactions = new List<IDbContextTransaction>(TenantDbContextTypes.Length);

        try
        {
            foreach (var contextType in TenantDbContextTypes)
            {
                var dbContext = (DbContext)httpContext.RequestServices.GetRequiredService(contextType);
                var transaction = await dbContext.Database.BeginTransactionAsync(httpContext.RequestAborted);
                transactions.Add(transaction);

                await dbContext.Database.ExecuteSqlInterpolatedAsync(
                    $"SELECT set_config('app.tenant_id', {tenantContext.TenantId.ToString()}, true)",
                    httpContext.RequestAborted);
            }

            await next(httpContext);

            foreach (var transaction in transactions)
            {
                await transaction.CommitAsync(httpContext.RequestAborted);
            }
        }
        catch
        {
            foreach (var transaction in transactions)
            {
                await transaction.RollbackAsync(CancellationToken.None);
            }

            throw;
        }
        finally
        {
            foreach (var transaction in transactions)
            {
                await transaction.DisposeAsync();
            }
        }
    }
}
