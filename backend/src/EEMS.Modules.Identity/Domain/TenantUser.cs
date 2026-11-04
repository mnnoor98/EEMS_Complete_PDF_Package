namespace EEMS.Modules.Identity.Domain;

public sealed class TenantUser
{
    private TenantUser() { }
    private TenantUser(Guid tenantId, Guid userId)
    {
        TenantId = tenantId;
        UserId = userId;
        IsActive = true;
        JoinedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public Guid UserId { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset JoinedAtUtc { get; private set; }

    public static TenantUser Create(Guid tenantId, Guid userId)
    {
        if (tenantId == Guid.Empty || userId == Guid.Empty) throw new ArgumentException("Tenant and user are required.");
        return new TenantUser(tenantId, userId);
    }

    public void Disable() => IsActive = false;
    public void Enable() => IsActive = true;
}
