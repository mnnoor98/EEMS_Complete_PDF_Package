using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class Meeting : Entity<Guid>
{
    private Meeting() { }
    private Meeting(Guid id, Guid tenantId, Guid electionId, Guid organizerUserId, Guid? eventId,
        string title, string agenda, DateTimeOffset startsAtUtc, DateTimeOffset endsAtUtc)
    {
        if (tenantId == Guid.Empty || electionId == Guid.Empty || organizerUserId == Guid.Empty)
            throw new ArgumentException("Tenant, election and organizer are required.");
        if (endsAtUtc <= startsAtUtc) throw new ArgumentException("Meeting end must be after start.");
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        OrganizerUserId = organizerUserId;
        EventId = eventId;
        Title = TextRules.Required(title, 200);
        Agenda = TextRules.Required(agenda, 4000);
        StartsAtUtc = startsAtUtc;
        EndsAtUtc = endsAtUtc;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public Guid OrganizerUserId { get; private set; }
    public Guid? EventId { get; private set; }
    public string Title { get; private set; } = string.Empty;
    public string Agenda { get; private set; } = string.Empty;
    public string? Minutes { get; private set; }
    public DateTimeOffset StartsAtUtc { get; private set; }
    public DateTimeOffset EndsAtUtc { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Meeting Create(Guid tenantId, Guid electionId, Guid organizerUserId, string title,
        string agenda, DateTimeOffset startsAtUtc, DateTimeOffset endsAtUtc, Guid? eventId = null) =>
        new(Guid.NewGuid(), tenantId, electionId, organizerUserId, eventId, title, agenda, startsAtUtc, endsAtUtc);

    public void RecordMinutes(string minutes) => Minutes = TextRules.Required(minutes, 8000);
}
