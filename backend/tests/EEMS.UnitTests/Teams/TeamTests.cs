using EEMS.Modules.Teams.Domain;
namespace EEMS.UnitTests.Teams;
public sealed class TeamTests
{
    [Fact]public void CreateRequiresElection()=>Assert.Throws<ArgumentException>(()=>Team.Create(Guid.NewGuid(),Guid.Empty,1,"Team"));
    [Fact]public void TaskRequiresAssignee()=>Assert.Throws<ArgumentException>(()=>TeamTask.Create(Guid.NewGuid(),Guid.NewGuid(),null,null,1,1,"Task"));
    [Fact]public void TrainingRequiresValidRange(){var now=DateTimeOffset.UtcNow;Assert.Throws<ArgumentException>(()=>Training.Create(Guid.NewGuid(),Guid.NewGuid(),"Training",now,now));}
    [Fact]public void TaskTransitionIncrementsVersion(){var task=TeamTask.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),null,1,1,"Task");task.MoveTo(2);Assert.Equal(2,task.Version);}
}
