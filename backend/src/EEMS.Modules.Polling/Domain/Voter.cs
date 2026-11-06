using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Polling.Domain;

public sealed class Voter : Entity<Guid>
{
    private Voter() { }

    private Voter(
        Guid id,
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid? boothId,
        Guid? candidateId,
        string voterNumber,
        int serialNumber,
        string fullName,
        string? fatherOrSpouseName,
        string gender,
        int? age,
        string? areaName,
        string category,
        bool slipIssued,
        bool hasVoted,
        string? phone,
        string? notes,
        DateTimeOffset createdAtUtc)
    {
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        CenterId = centerId;
        BoothId = boothId;
        CandidateId = candidateId;
        VoterNumber = voterNumber;
        SerialNumber = serialNumber;
        FullName = fullName;
        FatherOrSpouseName = fatherOrSpouseName;
        Gender = gender;
        Age = age;
        AreaName = areaName;
        Category = category;
        SlipIssued = slipIssued;
        HasVoted = hasVoted;
        Phone = phone;
        Notes = notes;
        CreatedAtUtc = createdAtUtc;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public Guid CenterId { get; private set; }
    public Guid? BoothId { get; private set; }
    public Guid? CandidateId { get; private set; }
    public string VoterNumber { get; private set; } = string.Empty;
    public int SerialNumber { get; private set; }
    public string FullName { get; private set; } = string.Empty;
    public string? FatherOrSpouseName { get; private set; }
    public string Gender { get; private set; } = "MALE";
    public int? Age { get; private set; }
    public string? AreaName { get; private set; }
    public string Category { get; private set; } = "SUPPORTER";
    public bool SlipIssued { get; private set; }
    public bool HasVoted { get; private set; }
    public string? Phone { get; private set; }
    public string? Notes { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Voter Create(
        Guid tenantId,
        Guid electionId,
        Guid centerId,
        Guid? boothId,
        string voterNumber,
        int serialNumber,
        string fullName,
        string? fatherOrSpouseName,
        string gender,
        int? age,
        string? areaName,
        string category,
        string? phone,
        string? notes = null,
        Guid? candidateId = null) =>
        new(
            Guid.NewGuid(),
            tenantId,
            electionId,
            centerId,
            boothId,
            candidateId,
            voterNumber,
            serialNumber,
            fullName,
            fatherOrSpouseName,
            gender,
            age,
            areaName,
            category,
            false,
            false,
            phone,
            notes,
            DateTimeOffset.UtcNow);

    public void AssignCandidate(Guid? candidateId) => CandidateId = candidateId;

    public void UpdateDetails(
        Guid centerId,
        Guid? boothId,
        string voterNumber,
        int serialNumber,
        string fullName,
        string? fatherOrSpouseName,
        string gender,
        int? age,
        string? areaName,
        string category,
        string? phone,
        string? notes)
    {
        CenterId = centerId;
        BoothId = boothId;
        VoterNumber = voterNumber;
        SerialNumber = serialNumber;
        FullName = fullName;
        FatherOrSpouseName = fatherOrSpouseName;
        Gender = gender;
        Age = age;
        AreaName = areaName;
        Category = category;
        Phone = phone;
        Notes = notes;
    }

    public void MarkSlipIssued(bool issued)
    {
        SlipIssued = issued;
    }

    public void MarkVoted(bool voted)
    {
        HasVoted = voted;
    }
}

