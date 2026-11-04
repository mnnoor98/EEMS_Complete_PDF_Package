namespace EEMS.SharedKernel.Tenancy;

public sealed class UnresolvedTenantContext : ITenantContext
{
    public Guid TenantId => throw new InvalidOperationException("A verified tenant context is required.");
    public bool IsAvailable => false;
}
