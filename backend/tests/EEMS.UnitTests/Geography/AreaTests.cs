using EEMS.Modules.Geography.Domain;

namespace EEMS.UnitTests.Geography;

public sealed class AreaTests
{
    [Fact]
    public void CreateRejectsSelfParent()
    {
        Assert.Throws<ArgumentException>(() => Area.Create(10, 10, 1, "A10", "এলাকা"));
    }

    [Fact]
    public void CreateNormalizesCode()
    {
        var area = Area.Create(10, null, 1, " dhaka ", "ঢাকা", "Dhaka");
        Assert.Equal("DHAKA", area.Code);
    }
}
