using EEMS.Modules.Tenants.Domain;

namespace EEMS.UnitTests.Tenants;

public sealed class TenantTests
{
    [Fact]
    public void CreateNormalizesCodeAndSetsActiveStatus()
    {
        var tenant = Tenant.Create(" demo_org ", "Demo Organization");

        Assert.Equal("DEMO_ORG", tenant.Code);
        Assert.Equal("Demo Organization", tenant.Name);
        Assert.Equal(TenantStatus.Active, tenant.Status);
        Assert.NotEqual(Guid.Empty, tenant.Id);
    }

    [Theory]
    [InlineData("")]
    [InlineData("contains spaces")]
    [InlineData("invalid/code")]
    public void CreateRejectsInvalidCode(string code)
    {
        Assert.Throws<ArgumentException>(() => Tenant.Create(code, "Demo Organization"));
    }

    [Fact]
    public void RenameRejectsBlankName()
    {
        var tenant = Tenant.Create("DEMO", "Demo Organization");

        Assert.Throws<ArgumentException>(() => tenant.Rename("  "));
    }
}
