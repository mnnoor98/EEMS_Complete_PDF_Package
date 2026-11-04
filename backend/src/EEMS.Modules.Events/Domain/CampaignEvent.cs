using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class CampaignEvent : Entity<Guid>
{
    private CampaignEvent() { }
    private CampaignEvent(Guid id, Guid tenantId, Guid electionId, short eventTypeId, short stateId,
        long areaId, Guid? venueId, Guid? taskId, string title, DateTimeOffset startsAtUtc, DateTimeOffset endsAtUtc)
    {
        if (tenantId == Guid.Empty || electionId == Guid.Empty || areaId <= 0)
            throw new ArgumentException("Tenant, election and area are required.");
        if (eventTypeId <= 0 || stateId <= 0) throw new ArgumentOutOfRangeException(nameof(eventTypeId));
        if (endsAtUtc <= startsAtUtc) throw new ArgumentException("Event end must be after start.");
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        EventTypeId = eventTypeId;
        StateId = stateId;
        AreaId = areaId;
        VenueId = venueId;
        TaskId = taskId;
        Title = TextRules.Required(title, 200);
        StartsAtUtc = startsAtUtc;
        EndsAtUtc = endsAtUtc;
        CreatedAtUtc = DateTimeOffset.UtcNow;
        Version = 1;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public short EventTypeId { get; private set; }
    public short StateId { get; private set; }
    public long AreaId { get; private set; }
    public Guid? VenueId { get; private set; }
    public Guid? TaskId { get; private set; }
    public string Title { get; private set; } = string.Empty;
    public DateTimeOffset StartsAtUtc { get; private set; }
    public DateTimeOffset EndsAtUtc { get; private set; }
    public string? CompletionReport { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }
    public int Version { get; private set; }

    public static CampaignEvent Create(Guid tenantId, Guid electionId, short eventTypeId, short stateId,
        long areaId, string title, DateTimeOffset startsAtUtc, DateTimeOffset endsAtUtc,
        Guid? venueId = null, Guid? taskId = null) =>
        new(Guid.NewGuid(), tenantId, electionId, eventTypeId, stateId, areaId, venueId, taskId,
            title, startsAtUtc, endsAtUtc);

    public void MoveTo(short stateId)
    {
        if (stateId <= 0) throw new ArgumentOutOfRangeException(nameof(stateId));
        StateId = stateId;
        Version++;
    }

    public void Complete(string report, short completedStateId)
    {
        CompletionReport = TextRules.Required(report, 4000);
        MoveTo(completedStateId);
    }
}
