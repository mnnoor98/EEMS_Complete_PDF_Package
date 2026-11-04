namespace EEMS.Modules.Identity.Domain;

public sealed class PasswordCredential
{
    private PasswordCredential() { }

    private PasswordCredential(Guid userId, string passwordHash, bool mustChangePassword)
    {
        UserId = userId == Guid.Empty ? throw new ArgumentException("User is required.", nameof(userId)) : userId;
        PasswordHash = RequireHash(passwordHash);
        MustChangePassword = mustChangePassword;
        UpdatedAtUtc = DateTimeOffset.UtcNow;
    }

    public Guid UserId { get; private set; }
    public string PasswordHash { get; private set; } = string.Empty;
    public DateTimeOffset UpdatedAtUtc { get; private set; }
    public bool MustChangePassword { get; private set; }
    public int FailedLoginCount { get; private set; }
    public DateTimeOffset? LockoutEndUtc { get; private set; }

    public static PasswordCredential Create(Guid userId, string passwordHash, bool mustChangePassword = true) =>
        new(userId, passwordHash, mustChangePassword);

    public void ChangePassword(string passwordHash)
    {
        PasswordHash = RequireHash(passwordHash);
        UpdatedAtUtc = DateTimeOffset.UtcNow;
        MustChangePassword = false;
        FailedLoginCount = 0;
        LockoutEndUtc = null;
    }

    public bool IsLockedOut(DateTimeOffset now) => LockoutEndUtc > now;

    public void RecordFailedLogin(int maximumAttempts, DateTimeOffset lockoutEndUtc)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(maximumAttempts);
        FailedLoginCount++;
        if (FailedLoginCount >= maximumAttempts) LockoutEndUtc = lockoutEndUtc;
    }

    public void RecordSuccessfulLogin()
    {
        FailedLoginCount = 0;
        LockoutEndUtc = null;
    }

    private static string RequireHash(string value) =>
        string.IsNullOrWhiteSpace(value) || value.Length > 1000
            ? throw new ArgumentException("A valid password hash is required.", nameof(value))
            : value;
}
