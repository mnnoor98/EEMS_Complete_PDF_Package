using EEMS.Modules.Identity.Domain;

namespace EEMS.UnitTests.Identity;

public sealed class PermissionTests
{
    [Fact]
    public void CreateNormalizesPermissionCode()
    {
        var permission = Permission.Create(" Election.Read ", "Read elections", "Elections");

        Assert.Equal("election.read", permission.Code);
        Assert.True(permission.IsActive);
    }

    [Theory]
    [InlineData("election read")]
    [InlineData("election/read")]
    public void CreateRejectsInvalidPermissionCode(string code)
    {
        Assert.Throws<ArgumentException>(() => Permission.Create(code, "Read elections", "Elections"));
    }
}
