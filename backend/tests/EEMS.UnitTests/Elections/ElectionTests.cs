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

    [Fact]
    public void UpdateDetailsChangesEditableFieldsAndIncrementsVersion()
    {
        var election = Election.Create(Guid.NewGuid(), 1, 1, 1, "Election", new DateOnly(2027, 1, 1));
        election.UpdateDetails(2, 3, "Updated election", new DateOnly(2027, 2, 1));
        Assert.Equal(2, election.ElectionTypeId);
        Assert.Equal(3, election.AreaId);
        Assert.Equal("Updated election", election.Name);
        Assert.Equal(new DateOnly(2027, 2, 1), election.ElectionDate);
        Assert.Equal(2, election.Version);
    }
}
