using EEMS.Modules.Events.Domain;

namespace EEMS.UnitTests.Events;

public sealed class EventTests
{
    [Fact]
    public void EventRequiresValidRange()
    {
        var now = DateTimeOffset.UtcNow;
        Assert.Throws<ArgumentException>(() => CampaignEvent.Create(
            Guid.NewGuid(), Guid.NewGuid(), 1, 1, 1, "Campaign", now, now));
    }

    [Fact]
    public void CompletingEventRecordsReportAndIncrementsVersion()
    {
        var now = DateTimeOffset.UtcNow;
        var campaignEvent = CampaignEvent.Create(
            Guid.NewGuid(), Guid.NewGuid(), 1, 1, 1, "Campaign", now, now.AddHours(1));

        campaignEvent.Complete("Completed safely.", 2);

        Assert.Equal("Completed safely.", campaignEvent.CompletionReport);
        Assert.Equal(2, campaignEvent.StateId);
        Assert.Equal(2, campaignEvent.Version);
    }

    [Fact]
    public void MeetingRequiresValidRange()
    {
        var now = DateTimeOffset.UtcNow;
        Assert.Throws<ArgumentException>(() => Meeting.Create(
            Guid.NewGuid(), Guid.NewGuid(), Guid.NewGuid(), "Meeting", "Agenda", now, now));
    }

    [Fact]
    public void ParticipantCanBeMarkedAttended()
    {
        var participant = MeetingParticipant.Create(Guid.NewGuid(), Guid.NewGuid(), Guid.NewGuid());
        participant.MarkAttended();
        Assert.True(participant.Attended);
        Assert.NotNull(participant.AttendanceRecordedAtUtc);
    }
}
