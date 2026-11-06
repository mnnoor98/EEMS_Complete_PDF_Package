using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Candidates.Domain;

public sealed class CandidateElection : Entity<Guid>
{
    private CandidateElection() { }
    private CandidateElection(
        Guid id,
        Guid tenantId,
        Guid electionId,
        Guid candidateId,
        long positionId,
        long areaId,
        string? nominationReference,
        int? symbolId = null,
        string? partyName = null,
        string? slogan = null)
    {
        if (tenantId == Guid.Empty || electionId == Guid.Empty || candidateId == Guid.Empty)
            throw new ArgumentException("Tenant, election and candidate are required.");
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(positionId);
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(areaId);
        Id = id;
        TenantId = tenantId;
        ElectionId = electionId;
        CandidateId = candidateId;
        PositionId = positionId;
        AreaId = areaId;
        NominationReference = Optional(nominationReference, 120);
        SymbolId = symbolId;
        PartyName = Optional(partyName, 150);
        Slogan = Optional(slogan, 300);
        IsActive = true;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public Guid ElectionId { get; private set; }
    public Guid CandidateId { get; private set; }
    public long PositionId { get; private set; }
    public long AreaId { get; private set; }
    public string? NominationReference { get; private set; }
    public int? SymbolId { get; private set; }
    public string? PartyName { get; private set; }
    public string? Slogan { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static CandidateElection Create(
        Guid tenantId,
        Guid electionId,
        Guid candidateId,
        long positionId,
        long areaId,
        string? nominationReference = null,
        int? symbolId = null,
        string? partyName = null,
        string? slogan = null) =>
        new(Guid.NewGuid(), tenantId, electionId, candidateId, positionId, areaId, nominationReference, symbolId, partyName, slogan);

    public void UpdateCampaignDetails(int? symbolId, string? partyName, string? slogan)
    {
        SymbolId = symbolId;
        PartyName = Optional(partyName, 150);
        Slogan = Optional(slogan, 300);
    }

    private static string? Optional(string? value, int max)
    {
        var text = value?.Trim();
        if (string.IsNullOrEmpty(text)) return null;
        return text.Length <= max ? text : throw new ArgumentException("Value is too long.");
    }
}
