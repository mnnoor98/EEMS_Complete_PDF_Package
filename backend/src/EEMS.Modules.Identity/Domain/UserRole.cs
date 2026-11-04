namespace EEMS.Modules.Identity.Domain;

public sealed class UserRole
{
    private UserRole() { }
    public UserRole(Guid tenantId, Guid userId, Guid roleId)
    {
        if (tenantId == Guid.Empty || userId == Guid.Empty || roleId == Guid.Empty)
            throw new ArgumentException("Tenant, user and role are required.");
        TenantId = tenantId; UserId = userId; RoleId = roleId; AssignedAtUtc = DateTimeOffset.UtcNow;
    }
    public Guid TenantId { get; private set; }
    public Guid UserId { get; private set; }
    public Guid RoleId { get; private set; }
    public DateTimeOffset AssignedAtUtc { get; private set; }
}
