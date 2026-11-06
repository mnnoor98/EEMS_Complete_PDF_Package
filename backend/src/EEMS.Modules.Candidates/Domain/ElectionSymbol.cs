namespace EEMS.Modules.Candidates.Domain;

public sealed class ElectionSymbol
{
    private ElectionSymbol() { }

    public ElectionSymbol(int id, string code, string nameBn, string nameEn, string category, string iconEmoji)
    {
        Id = id;
        Code = code.Trim().ToUpperInvariant();
        NameBn = nameBn.Trim();
        NameEn = nameEn.Trim();
        Category = category.Trim().ToUpperInvariant();
        IconEmoji = string.IsNullOrWhiteSpace(iconEmoji) ? "🗳️" : iconEmoji.Trim();
        IsActive = true;
    }

    public int Id { get; private set; }
    public string Code { get; private set; } = string.Empty;
    public string NameBn { get; private set; } = string.Empty;
    public string NameEn { get; private set; } = string.Empty;
    public string Category { get; private set; } = string.Empty;
    public string IconEmoji { get; private set; } = "🗳️";
    public bool IsActive { get; private set; }

    public static ElectionSymbol Create(int id, string code, string nameBn, string nameEn, string category, string iconEmoji) =>
        new(id, code, nameBn, nameEn, category, iconEmoji);
}
