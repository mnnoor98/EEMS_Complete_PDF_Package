using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Identity.Domain;

public sealed class User : Entity<Guid>
{
    private User() { }

    private User(Guid id, string externalSubject, string displayName, string? email)
    {
        Id = id;
        ExternalSubject = Require(externalSubject, nameof(externalSubject), 200);
        DisplayName = Require(displayName, nameof(displayName), 200);
        Email = NormalizeOptional(email, 320);
        IsActive = true;
        CreatedAtUtc = DateTimeOffset.UtcNow;
    }

    public string ExternalSubject { get; private set; } = string.Empty;
    public string DisplayName { get; private set; } = string.Empty;
    public string? Email { get; private set; }
    public bool IsActive { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; private set; }

    public static User Create(string externalSubject, string displayName, string? email) =>
        new(Guid.NewGuid(), externalSubject, displayName, email);

    public void Disable() => IsActive = false;
    public void Enable() => IsActive = true;

    private static string Require(string value, string parameter, int maximumLength)
    {
        var normalized = value?.Trim() ?? string.Empty;
        if (normalized.Length is 0 || normalized.Length > maximumLength)
        {
            throw new ArgumentException($"{parameter} must contain between 1 and {maximumLength} characters.", parameter);
        }
        return normalized;
    }

    private static string? NormalizeOptional(string? value, int maximumLength)
    {
        var normalized = value?.Trim();
        if (string.IsNullOrEmpty(normalized)) return null;
        if (normalized.Length > maximumLength) throw new ArgumentException($"Value exceeds {maximumLength} characters.");
        return normalized.ToLowerInvariant();
    }
}
