namespace EEMS.Modules.Identity.Domain;

public sealed class RolePermission
{
    private RolePermission() { }
    public RolePermission(Guid tenantId, Guid roleId, Guid permissionId)
    {
        if (tenantId == Guid.Empty || roleId == Guid.Empty || permissionId == Guid.Empty)
            throw new ArgumentException("Tenant, role and permission are required.");
        TenantId = tenantId; RoleId = roleId; PermissionId = permissionId;
    }
    public Guid TenantId { get; private set; }
    public Guid RoleId { get; private set; }
    public Guid PermissionId { get; private set; }
}
