using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Polling.Domain;
public sealed class CenterVerification:Entity<Guid>
{
    private CenterVerification(){}
    private CenterVerification(Guid id,Guid tenantId,Guid electionCenterId,Guid verifiedByUserId,DateTimeOffset verifiedAtUtc)
    {
        if(tenantId==Guid.Empty||electionCenterId==Guid.Empty||verifiedByUserId==Guid.Empty)throw new ArgumentException("Verification references are required.");
        Id=id;TenantId=tenantId;ElectionCenterId=electionCenterId;VerifiedByUserId=verifiedByUserId;VerifiedAtUtc=verifiedAtUtc;
    }
    public Guid TenantId{get;private set;}public Guid ElectionCenterId{get;private set;}public Guid VerifiedByUserId{get;private set;}public DateTimeOffset VerifiedAtUtc{get;private set;}
    public static CenterVerification Record(Guid tenantId,Guid electionCenterId,Guid userId)=>new(Guid.NewGuid(),tenantId,electionCenterId,userId,DateTimeOffset.UtcNow);
}
