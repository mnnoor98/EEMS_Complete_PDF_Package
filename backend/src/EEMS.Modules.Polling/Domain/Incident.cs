using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Polling.Domain;

public sealed class Incident : Entity<Guid>
{
    private Incident() { }

    private Incident(
        Guid id,
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid? boothId,
        Guid? candidateId,
        string incidentType,
        string severity,
        string title,
        string description,
        string reportedBy,
        string? reportedByPhone,
        DateTimeOffset reportedAt,
        string status,
        string? evidenceAttachmentUrl,
        string? magistrateName,
        string? actionTaken,
        bool officialComplaintGenerated,
        DateTimeOffset createdAtUtc)
    {
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        CenterId = centerId;
        BoothId = boothId;
        CandidateId = candidateId;
        IncidentType = incidentType;
        Severity = severity;
        Title = title;
        Description = description;
        ReportedBy = reportedBy;
        ReportedByPhone = reportedByPhone;
        ReportedAt = reportedAt;
        Status = status;
        EvidenceAttachmentUrl = evidenceAttachmentUrl;
        MagistrateName = magistrateName;
        ActionTaken = actionTaken;
        OfficialComplaintGenerated = officialComplaintGenerated;
        CreatedAtUtc = createdAtUtc;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public Guid CenterId { get; private set; }
    public Guid? BoothId { get; private set; }
    public Guid? CandidateId { get; private set; }
    public string IncidentType { get; private set; } = "OTHER";
    public string Severity { get; private set; } = "HIGH";
    public string Title { get; private set; } = string.Empty;
    public string Description { get; private set; } = string.Empty;
    public string ReportedBy { get; private set; } = string.Empty;
    public string? ReportedByPhone { get; private set; }
    public DateTimeOffset ReportedAt { get; private set; }
    public string Status { get; private set; } = "REPORTED";
    public string? EvidenceAttachmentUrl { get; private set; }
    public string? MagistrateName { get; private set; }
    public string? ActionTaken { get; private set; }
    public bool OfficialComplaintGenerated { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Incident Create(
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid? boothId,
        string incidentType,
        string severity,
        string title,
        string description,
        string reportedBy,
        string? reportedByPhone,
        string? evidenceAttachmentUrl = null,
        Guid? candidateId = null) =>
        new(
            Guid.NewGuid(),
            tenantId,
            electionId,
            centerId,
            boothId,
            candidateId,
            incidentType,
            severity,
            title,
            description,
            reportedBy,
            reportedByPhone,
            DateTimeOffset.UtcNow,
            "REPORTED",
            evidenceAttachmentUrl,
            null,
            null,
            false,
            DateTimeOffset.UtcNow);

    public void AssignCandidate(Guid? candidateId) => CandidateId = candidateId;

    public void UpdateStatus(
        string status,
        string? actionTaken,
        string? magistrateName,
        bool? officialComplaintGenerated)
    {
        Status = status;
        if (actionTaken != null) ActionTaken = actionTaken;
        if (magistrateName != null) MagistrateName = magistrateName;
        if (officialComplaintGenerated.HasValue) OfficialComplaintGenerated = officialComplaintGenerated.Value;
    }
}

