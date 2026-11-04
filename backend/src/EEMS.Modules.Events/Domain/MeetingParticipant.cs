namespace EEMS.Modules.Events.Domain;

public sealed class MeetingParticipant
{
    private MeetingParticipant() { }
    private MeetingParticipant(Guid tenantId, Guid meetingId, Guid userId)
    {
        if (tenantId == Guid.Empty || meetingId == Guid.Empty || userId == Guid.Empty)
            throw new ArgumentException("Tenant, meeting and user are required.");
        TenantId = tenantId;
        MeetingId = meetingId;
        UserId = userId;
    }

    public Guid TenantId { get; private set; }
    public Guid MeetingId { get; private set; }
    public Guid UserId { get; private set; }
    public bool Attended { get; private set; }
    public DateTimeOffset? AttendanceRecordedAtUtc { get; private set; }

    public static MeetingParticipant Create(Guid tenantId, Guid meetingId, Guid userId) =>
        new(tenantId, meetingId, userId);

    public void MarkAttended()
    {
        Attended = true;
        AttendanceRecordedAtUtc = DateTimeOffset.UtcNow;
    }
}
