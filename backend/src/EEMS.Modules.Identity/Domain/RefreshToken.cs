using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Identity.Domain;

public sealed class RefreshToken : Entity<Guid>
{
    private RefreshToken() { }

    private RefreshToken(Guid tenantId, Guid userId, string tokenHash, DateTimeOffset expiresAtUtc)
    {
        Id = Guid.NewGuid();
        TenantId = tenantId == Guid.Empty ? throw new ArgumentException("Tenant is required.", nameof(tenantId)) : tenantId;
        UserId = userId == Guid.Empty ? throw new ArgumentException("User is required.", nameof(userId)) : userId;
        TokenHash = string.IsNullOrWhiteSpace(tokenHash) ? throw new ArgumentException("Token hash is required.", nameof(tokenHash)) : tokenHash;
        CreatedAtUtc = DateTimeOffset.UtcNow;
        ExpiresAtUtc = expiresAtUtc > CreatedAtUtc ? expiresAtUtc : throw new ArgumentOutOfRangeException(nameof(expiresAtUtc));
    }

    public Guid TenantId { get; private set; }
    public Guid UserId { get; private set; }
    public string TokenHash { get; private set; } = string.Empty;
    public DateTimeOffset CreatedAtUtc { get; private set; }
    public DateTimeOffset ExpiresAtUtc { get; private set; }
    public DateTimeOffset? RevokedAtUtc { get; private set; }
    public Guid? ReplacedByTokenId { get; private set; }
    public bool IsActive => RevokedAtUtc is null && ExpiresAtUtc > DateTimeOffset.UtcNow;

    public static RefreshToken Create(Guid tenantId, Guid userId, string tokenHash, DateTimeOffset expiresAtUtc) =>
        new(tenantId, userId, tokenHash, expiresAtUtc);

    public void Revoke(Guid? replacementTokenId = null)
    {
        if (RevokedAtUtc is not null) return;
        RevokedAtUtc = DateTimeOffset.UtcNow;
        ReplacedByTokenId = replacementTokenId;
    }
}
