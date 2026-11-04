using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Identity.Domain;

public sealed class Role : Entity<Guid>
{
    private Role() { }
    private Role(Guid id, Guid tenantId, string code, string name)
    {
        Id = id;
        TenantId = tenantId == Guid.Empty ? throw new ArgumentException("Tenant is required.", nameof(tenantId)) : tenantId;
        Code = NormalizeCode(code);
        Name = Require(name, nameof(name), 120);
        IsActive = true;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid TenantId { get; private set; }
    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public bool IsActive { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static Role Create(Guid tenantId, string code, string name) => new(Guid.NewGuid(), tenantId, code, name);

    private static string NormalizeCode(string code)
    {
        var value = Require(code, nameof(code), 80).ToUpperInvariant();
        return value.All(character => char.IsAsciiLetterOrDigit(character) || character is '.' or '-' or '_')
            ? value
            : throw new ArgumentException("Role code contains unsupported characters.", nameof(code));
    }

    private static string Require(string value, string parameter, int maximumLength)
    {
        var normalized = value?.Trim() ?? string.Empty;
        if (normalized.Length is 0 || normalized.Length > maximumLength)
            throw new ArgumentException($"{parameter} must contain between 1 and {maximumLength} characters.", parameter);
        return normalized;
    }
}
