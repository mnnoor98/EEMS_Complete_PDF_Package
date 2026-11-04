using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Tenants.Domain;

public sealed class Tenant : Entity<Guid>
{
    private Tenant() { }

    private Tenant(Guid id, string code, string name)
    {
        Id = id;
        Code = NormalizeCode(code);
        Name = RequireText(name, nameof(name), 200);
        Status = TenantStatus.Active;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public TenantStatus Status { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Tenant Create(string code, string name) => new(Guid.NewGuid(), code, name);

    public void Rename(string name) => Name = RequireText(name, nameof(name), 200);

    public void ChangeStatus(TenantStatus status) => Status = status;

    private static string NormalizeCode(string code)
    {
        var value = RequireText(code, nameof(code), 40).ToUpperInvariant();
        return value.All(character => char.IsAsciiLetterOrDigit(character) || character is '-' or '_')
            ? value
            : throw new ArgumentException("Tenant code contains unsupported characters.", nameof(code));
    }

    private static string RequireText(string value, string parameter, int maximumLength)
    {
        var normalized = value?.Trim() ?? string.Empty;
        if (normalized.Length is 0 || normalized.Length > maximumLength)
        {
            throw new ArgumentException($"{parameter} must contain between 1 and {maximumLength} characters.", parameter);
        }

        return normalized;
    }
}
