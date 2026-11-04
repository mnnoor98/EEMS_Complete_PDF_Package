using EEMS.Modules.Identity.Domain;

namespace EEMS.UnitTests.Identity;

public sealed class RoleTests
{
    [Fact]
    public void CreateNormalizesRoleCode()
    {
        var role = Role.Create(Guid.NewGuid(), " area_manager ", "Area Manager");

        Assert.Equal("AREA_MANAGER", role.Code);
        Assert.True(role.IsActive);
    }

    [Fact]
    public void CreateRejectsEmptyTenant()
    {
        Assert.Throws<ArgumentException>(() => Role.Create(Guid.Empty, "ADMIN", "Administrator"));
    }
}
