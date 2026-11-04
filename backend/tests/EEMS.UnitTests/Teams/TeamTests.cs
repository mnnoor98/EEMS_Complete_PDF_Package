using EEMS.Modules.Teams.Domain;
namespace EEMS.UnitTests.Teams;
public sealed class TeamTests
{
    [Fact]public void CreateRequiresElection()=>Assert.Throws<ArgumentException>(()=>Team.Create(Guid.NewGuid(),Guid.Empty,1,"Team"));
    [Fact]public void TaskRequiresAssignee()=>Assert.Throws<ArgumentException>(()=>TeamTask.Create(Guid.NewGuid(),Guid.NewGuid(),null,null,1,1,"Task"));
    [Fact]public void TrainingRequiresValidRange(){var now=DateTimeOffset.UtcNow;Assert.Throws<ArgumentException>(()=>Training.Create(Guid.NewGuid(),Guid.NewGuid(),"Training",now,now));}
    [Fact]public void TaskTransitionIncrementsVersion(){var task=TeamTask.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),null,1,1,"Task");task.MoveTo(2);Assert.Equal(2,task.Version);}
    [Fact]public void FieldMemberUpdateTrimsValues(){var member=FieldMember.Create(Guid.NewGuid(),Guid.NewGuid()," Jamal "," 01700000000 "," Volunteer ",null,null,null);member.Update(" Jamal Uddin "," 01800000000 "," Coordinator ",1," Dhaka ",null);Assert.Equal("Jamal Uddin",member.FullName);Assert.Equal("01800000000",member.Phone);Assert.Equal("Dhaka",member.Address);}
    [Fact]public void FieldMemberDeactivateRetainsIdentity(){var member=FieldMember.Create(Guid.NewGuid(),Guid.NewGuid(),"Jamal","01700000000","Volunteer",null,null,null);var id=member.Id;member.Deactivate();Assert.False(member.IsActive);Assert.Equal(id,member.Id);}
    [Fact]public void FieldAttendanceNormalizesStatus(){var attendance=FieldMemberAttendance.Record(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),new DateOnly(2026,11,4)," present ",Guid.NewGuid()," On time ");Assert.Equal("PRESENT",attendance.Status);Assert.Equal("On time",attendance.Note);}
    [Fact]public void WorkVerificationIncrementsVersionAndCapturesReviewer(){var reviewer=Guid.NewGuid();var work=MemberWorkAssignment.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),1,1,"Door-to-door",null,null);work.Verify(reviewer,"Checked");Assert.Equal(2,work.Version);Assert.Equal(reviewer,work.VerifiedByUserId);Assert.NotNull(work.VerifiedAtUtc);Assert.Equal("Checked",work.VerificationNote);}
}
