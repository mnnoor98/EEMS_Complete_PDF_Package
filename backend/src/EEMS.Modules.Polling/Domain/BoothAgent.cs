using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Polling.Domain;

public sealed class BoothAgent : Entity<Guid>
{
    private BoothAgent() { }

    private BoothAgent(
        Guid id,
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid boothId,
        Guid candidateId,
        string agentType,
        string fullName,
        string nidNumber,
        string phone,
        string? voterNumber,
        string? photoUrl,
        bool appointmentLetterIssued,
        DateTimeOffset? checkedInAtBooth,
        string status,
        string? notes,
        DateTimeOffset createdAtUtc)
    {
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        CenterId = centerId;
        BoothId = boothId;
        CandidateId = candidateId;
        AgentType = agentType;
        FullName = fullName;
        NidNumber = nidNumber;
        Phone = phone;
        VoterNumber = voterNumber;
        PhotoUrl = photoUrl;
        AppointmentLetterIssued = appointmentLetterIssued;
        CheckedInAtBooth = checkedInAtBooth;
        Status = status;
        Notes = notes;
        CreatedAtUtc = createdAtUtc;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public Guid CenterId { get; private set; }
    public Guid BoothId { get; private set; }
    public Guid CandidateId { get; private set; }
    public string AgentType { get; private set; } = "PRIMARY";
    public string FullName { get; private set; } = string.Empty;
    public string NidNumber { get; private set; } = string.Empty;
    public string Phone { get; private set; } = string.Empty;
    public string? VoterNumber { get; private set; }
    public string? PhotoUrl { get; private set; }
    public bool AppointmentLetterIssued { get; private set; }
    public DateTimeOffset? CheckedInAtBooth { get; private set; }
    public string Status { get; private set; } = "ASSIGNED";
    public string? Notes { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static BoothAgent Create(
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid boothId,
        Guid candidateId,
        string agentType,
        string fullName,
        string nidNumber,
        string phone,
        string? voterNumber,
        string? notes = null) =>
        new(
            Guid.NewGuid(),
            tenantId,
            electionId,
            centerId,
            boothId,
            candidateId,
            agentType,
            fullName,
            nidNumber,
            phone,
            voterNumber,
            null,
            false,
            null,
            "ASSIGNED",
            notes,
            DateTimeOffset.UtcNow);

    public void UpdateStatus(string status, bool letterIssued)
    {
        Status = status;
        AppointmentLetterIssued = letterIssued;
        if (status == "PRESENT" && CheckedInAtBooth == null)
        {
            CheckedInAtBooth = DateTimeOffset.UtcNow;
        }
    }

    public void UpdateDetails(string fullName, string nidNumber, string phone, string? voterNumber, string agentType, string? notes)
    {
        FullName = fullName;
        NidNumber = nidNumber;
        Phone = phone;
        VoterNumber = voterNumber;
        AgentType = agentType;
        Notes = notes;
    }
}
