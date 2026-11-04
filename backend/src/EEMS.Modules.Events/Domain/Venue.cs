using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class Venue : Entity<Guid>
{
    private Venue() { }
    private Venue(Guid id, Guid tenantId, long areaId, string name, string address, int? capacity)
    {
        if (tenantId == Guid.Empty || areaId <= 0) throw new ArgumentException("Tenant and area are required.");
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        Id = id;
        TenantId = tenantId;
        AreaId = areaId;
        Name = TextRules.Required(name, 160);
        Address = TextRules.Required(address, 300);
        Capacity = capacity;
        IsActive = true;
    }

    public Guid TenantId { get; private set; }
    public long AreaId { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string Address { get; private set; } = string.Empty;
    public int? Capacity { get; private set; }
    public bool IsActive { get; private set; }

    public static Venue Create(Guid tenantId, long areaId, string name, string address, int? capacity = null) =>
        new(Guid.NewGuid(), tenantId, areaId, name, address, capacity);
}
