using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Candidates.Domain;

public sealed class Candidate : Entity<Guid>
{
    private Candidate() { }
    private Candidate(
        Guid id,
        Guid tenantId,
        string name,
        string? externalReference,
        int? symbolId = null,
        string? partyNameBn = null,
        string? partyNameEn = null,
        string? slogan = null,
        string? phone = null,
        string? photoUrl = null,
        string? campaignOffice = null)
    {
        if (tenantId == Guid.Empty) throw new ArgumentException("Tenant is required.", nameof(tenantId));
        Id = id;
        TenantId = tenantId;
        Name = Require(name, 200);
        ExternalReference = Optional(externalReference, 100);
        SymbolId = symbolId;
        PartyNameBn = Optional(partyNameBn, 150);
        PartyNameEn = Optional(partyNameEn, 150);
        Slogan = Optional(slogan, 300);
        Phone = Optional(phone, 30);
        PhotoUrl = Optional(photoUrl, 500);
        CampaignOffice = Optional(campaignOffice, 300);
        IsActive = true;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string? ExternalReference { get; private set; }
    public int? SymbolId { get; private set; }
    public string? PartyNameBn { get; private set; }
    public string? PartyNameEn { get; private set; }
    public string? Slogan { get; private set; }
    public string? Phone { get; private set; }
    public string? PhotoUrl { get; private set; }
    public string? CampaignOffice { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Candidate Create(
        Guid tenantId,
        string name,
        string? externalReference = null,
        int? symbolId = null,
        string? partyNameBn = null,
        string? partyNameEn = null,
        string? slogan = null,
        string? phone = null,
        string? photoUrl = null,
        string? campaignOffice = null) =>
        new(Guid.NewGuid(), tenantId, name, externalReference, symbolId, partyNameBn, partyNameEn, slogan, phone, photoUrl, campaignOffice);

    public void UpdateProfile(
        string name,
        int? symbolId,
        string? partyNameBn,
        string? partyNameEn,
        string? slogan,
        string? phone,
        string? photoUrl,
        string? campaignOffice)
    {
        Name = Require(name, 200);
        SymbolId = symbolId;
        PartyNameBn = Optional(partyNameBn, 150);
        PartyNameEn = Optional(partyNameEn, 150);
        Slogan = Optional(slogan, 300);
        Phone = Optional(phone, 30);
        PhotoUrl = Optional(photoUrl, 500);
        CampaignOffice = Optional(campaignOffice, 300);
    }

    private static string Require(string value, int max)
    {
        var text = value?.Trim() ?? string.Empty;
        return text.Length is > 0 && text.Length <= max ? text : throw new ArgumentException("Value is invalid.");
    }

    private static string? Optional(string? value, int max)
    {
        var text = value?.Trim();
        if (string.IsNullOrEmpty(text)) return null;
        return text.Length <= max ? text : throw new ArgumentException("Value is too long.");
    }
}
