using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Polling.Domain;
public sealed class ElectionCenter:Entity<Guid>
{
    private ElectionCenter(){} private ElectionCenter(Guid id,Guid tenantId,Guid electionId,Guid centerId){if(tenantId==Guid.Empty||electionId==Guid.Empty||centerId==Guid.Empty)throw new ArgumentException("Tenant, election and center are required.");Id=id;TenantId=tenantId;ElectionId=electionId;CenterId=centerId;IsVerified=false;CreatedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;}public Guid ElectionId{get;private set;}public Guid CenterId{get;private set;}public bool IsVerified{get;private set;}public DateTimeOffset CreatedAtUtc{get;private set;}
    public static ElectionCenter Create(Guid tenantId,Guid electionId,Guid centerId)=>new(Guid.NewGuid(),tenantId,electionId,centerId);public void Verify()=>IsVerified=true;
}
