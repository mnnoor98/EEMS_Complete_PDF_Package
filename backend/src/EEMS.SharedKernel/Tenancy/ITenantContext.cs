namespace EEMS.SharedKernel.Tenancy;

public interface ITenantContext
{
    Guid TenantId { get; }
    bool IsAvailable { get; }
}
