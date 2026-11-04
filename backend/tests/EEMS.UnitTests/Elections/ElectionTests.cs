using EEMS.Modules.Elections.Domain;

namespace EEMS.UnitTests.Elections;

public sealed class ElectionTests
{
    [Fact]
    public void CreateRequiresTenant()
    {
        Assert.Throws<ArgumentException>(() => Election.Create(Guid.Empty, 1, 1, 1, "Election", new DateOnly(2027, 1, 1)));
    }

    [Fact]
    public void MoveToIncrementsVersion()
    {
        var election = Election.Create(Guid.NewGuid(), 1, 1, 1, "Election", new DateOnly(2027, 1, 1));
        election.MoveTo(2);
        Assert.Equal(2, election.Version);
        Assert.Equal(2, election.LifecycleStateId);
    }
}
