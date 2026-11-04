using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Candidates.Domain;

public sealed class CandidateElection : Entity<Guid>
{
    private CandidateElection() { }
    private CandidateElection(Guid id,Guid tenantId,Guid electionId,Guid candidateId,long positionId,long areaId,string? nominationReference)
    {
        if(tenantId==Guid.Empty||electionId==Guid.Empty||candidateId==Guid.Empty)throw new ArgumentException("Tenant, election and candidate are required.");
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(positionId);ArgumentOutOfRangeException.ThrowIfNegativeOrZero(areaId);
        Id=id;TenantId=tenantId;ElectionId=electionId;CandidateId=candidateId;PositionId=positionId;AreaId=areaId;NominationReference=Optional(nominationReference,120);IsActive=true;CreatedAtUtc=DateTimeOffset.UtcNow;
    }
    public Guid TenantId{get;private set;} public Guid ElectionId{get;private set;} public Guid CandidateId{get;private set;}
    public long PositionId{get;private set;} public long AreaId{get;private set;} public string? NominationReference{get;private set;}
    public bool IsActive{get;private set;} public DateTimeOffset CreatedAtUtc{get;private set;}
    public static CandidateElection Create(Guid tenantId,Guid electionId,Guid candidateId,long positionId,long areaId,string? nominationReference=null)=>new(Guid.NewGuid(),tenantId,electionId,candidateId,positionId,areaId,nominationReference);
    private static string? Optional(string? value,int max){var text=value?.Trim();if(string.IsNullOrEmpty(text))return null;return text.Length<=max?text:throw new ArgumentException("Value is too long.");}
}
