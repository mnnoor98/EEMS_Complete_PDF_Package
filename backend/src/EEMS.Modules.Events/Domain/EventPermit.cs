using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class EventPermit : Entity<Guid>
{
    private EventPermit() { }
    private EventPermit(Guid id, Guid tenantId, Guid eventId, short stateId, string authority,
        string referenceNumber, DateOnly? expiresOn)
    {
        if (tenantId == Guid.Empty || eventId == Guid.Empty) throw new ArgumentException("Tenant and event are required.");
        if (stateId <= 0) throw new ArgumentOutOfRangeException(nameof(stateId));
        Id = id;
        TenantId = tenantId;
        EventId = eventId;
        StateId = stateId;
        IssuingAuthority = TextRules.Required(authority, 160);
        ReferenceNumber = TextRules.Required(referenceNumber, 100);
        ExpiresOn = expiresOn;
    }

    public Guid TenantId { get; private set; }
    public Guid EventId { get; private set; }
    public short StateId { get; private set; }
    public string IssuingAuthority { get; private set; } = string.Empty;
    public string ReferenceNumber { get; private set; } = string.Empty;
    public DateOnly? ExpiresOn { get; private set; }

    public static EventPermit Create(Guid tenantId, Guid eventId, short stateId, string authority,
        string referenceNumber, DateOnly? expiresOn = null) =>
        new(Guid.NewGuid(), tenantId, eventId, stateId, authority, referenceNumber, expiresOn);
}
