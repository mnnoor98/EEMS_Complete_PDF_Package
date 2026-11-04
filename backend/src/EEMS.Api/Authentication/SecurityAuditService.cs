using EEMS.Modules.Reporting.Domain;
using EEMS.Modules.Reporting.Infrastructure;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Authentication;

public sealed class SecurityAuditService(
    ReportingDbContext dbContext,
    IHttpContextAccessor httpContextAccessor)
{
    public async Task RecordAsync(
        Guid tenantId,
        Guid? userId,
        string eventType,
        string detail,
        CancellationToken cancellationToken)
    {
        var ownsTransaction = dbContext.Database.CurrentTransaction is null;
        await using var transaction = ownsTransaction
            ? await dbContext.Database.BeginTransactionAsync(cancellationToken)
            : null;
        if (ownsTransaction)
        {
            await dbContext.Database.ExecuteSqlInterpolatedAsync(
                $"SELECT set_config('app.tenant_id', {tenantId.ToString()}, true)",
                cancellationToken);
        }

        var httpContext = httpContextAccessor.HttpContext;
        var source = httpContext?.Connection.RemoteIpAddress?.ToString() ?? "unknown";
        var correlationId = httpContext?.TraceIdentifier ?? Guid.NewGuid().ToString("N");
        dbContext.SecurityEvents.Add(SecurityEvent.Record(
            tenantId,
            userId,
            eventType,
            source,
            detail,
            correlationId));
        await dbContext.SaveChangesAsync(cancellationToken);
        if (transaction is not null) await transaction.CommitAsync(cancellationToken);
    }
}
