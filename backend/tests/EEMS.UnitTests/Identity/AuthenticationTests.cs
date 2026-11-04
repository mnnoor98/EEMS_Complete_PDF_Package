using EEMS.Modules.Identity.Domain;

namespace EEMS.UnitTests.Identity;

public sealed class AuthenticationTests
{
    [Fact]
    public void PasswordCredentialRejectsEmptyHash()
    {
        Assert.Throws<ArgumentException>(() => PasswordCredential.Create(Guid.NewGuid(), string.Empty));
    }

    [Fact]
    public void PasswordCredentialLocksAfterConfiguredFailures()
    {
        var credential = PasswordCredential.Create(Guid.NewGuid(), "valid-hash");
        var lockoutEnd = DateTimeOffset.UtcNow.AddMinutes(15);

        credential.RecordFailedLogin(2, lockoutEnd);
        Assert.False(credential.IsLockedOut(DateTimeOffset.UtcNow));
        credential.RecordFailedLogin(2, lockoutEnd);

        Assert.True(credential.IsLockedOut(DateTimeOffset.UtcNow));
        Assert.Equal(2, credential.FailedLoginCount);
    }

    [Fact]
    public void ChangingPasswordClearsForcedChangeAndLockout()
    {
        var credential = PasswordCredential.Create(Guid.NewGuid(), "old-hash");
        credential.RecordFailedLogin(1, DateTimeOffset.UtcNow.AddMinutes(15));

        credential.ChangePassword("new-hash");

        Assert.False(credential.MustChangePassword);
        Assert.Equal(0, credential.FailedLoginCount);
        Assert.Null(credential.LockoutEndUtc);
    }

    [Fact]
    public void RefreshTokenCanBeRevokedWithReplacement()
    {
        var replacementId = Guid.NewGuid();
        var token = RefreshToken.Create(
            Guid.NewGuid(),
            Guid.NewGuid(),
            new string('A', 64),
            DateTimeOffset.UtcNow.AddDays(1));

        token.Revoke(replacementId);

        Assert.False(token.IsActive);
        Assert.NotNull(token.RevokedAtUtc);
        Assert.Equal(replacementId, token.ReplacedByTokenId);
    }

    [Fact]
    public void RefreshTokenRejectsPastExpiry()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => RefreshToken.Create(
            Guid.NewGuid(),
            Guid.NewGuid(),
            new string('A', 64),
            DateTimeOffset.UtcNow.AddMinutes(-1)));
    }
}
