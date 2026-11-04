using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Polling.Domain;
public sealed class AgentAssignment:Entity<Guid>
{
    private AgentAssignment(){} private AgentAssignment(Guid id,Guid tenantId,Guid electionCenterId,Guid userId,DateTimeOffset startsAtUtc,DateTimeOffset endsAtUtc){if(tenantId==Guid.Empty||electionCenterId==Guid.Empty||userId==Guid.Empty)throw new ArgumentException("Tenant, center and user are required.");if(endsAtUtc<=startsAtUtc)throw new ArgumentException("Assignment end must be after start.");Id=id;TenantId=tenantId;ElectionCenterId=electionCenterId;UserId=userId;StartsAtUtc=startsAtUtc;EndsAtUtc=endsAtUtc;IsActive=true;}
    public Guid TenantId{get;private set;}public Guid ElectionCenterId{get;private set;}public Guid UserId{get;private set;}public DateTimeOffset StartsAtUtc{get;private set;}public DateTimeOffset EndsAtUtc{get;private set;}public bool IsActive{get;private set;}
    public static AgentAssignment Create(Guid tenantId,Guid electionCenterId,Guid userId,DateTimeOffset startsAtUtc,DateTimeOffset endsAtUtc)=>new(Guid.NewGuid(),tenantId,electionCenterId,userId,startsAtUtc,endsAtUtc);
    public void Deactivate()=>IsActive=false;
}
