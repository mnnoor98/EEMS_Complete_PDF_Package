using EEMS.Modules.Polling.Domain;
namespace EEMS.UnitTests.Polling;
public sealed class PollingTests
{
    [Fact] public void CenterNormalizesCode(){var center=PollingCenter.Create(1," c-1 ","Center");Assert.Equal("C-1",center.Code);}
    [Fact] public void AgentAssignmentRejectsInvalidTimeRange(){var now=DateTimeOffset.UtcNow;Assert.Throws<ArgumentException>(()=>AgentAssignment.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),now,now));}
    [Fact] public void AgentAssignmentCanBeDeactivated(){var now=DateTimeOffset.UtcNow;var assignment=AgentAssignment.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),now,now.AddHours(8));assignment.Deactivate();Assert.False(assignment.IsActive);}
    [Fact] public void CenterVerificationCapturesAuditReferences(){var tenantId=Guid.NewGuid();var centerId=Guid.NewGuid();var userId=Guid.NewGuid();var verification=CenterVerification.Record(tenantId,centerId,userId);Assert.Equal(tenantId,verification.TenantId);Assert.Equal(centerId,verification.ElectionCenterId);Assert.Equal(userId,verification.VerifiedByUserId);}
}
