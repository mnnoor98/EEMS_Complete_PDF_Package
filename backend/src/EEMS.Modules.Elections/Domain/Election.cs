using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Elections.Domain;

public sealed class Election : Entity<Guid>
{
    private Election() { }
    private Election(Guid id,Guid tenantId,short electionTypeId,long areaId,short lifecycleStateId,string name,DateOnly electionDate)
    {if(tenantId==Guid.Empty)throw new ArgumentException("Tenant is required.",nameof(tenantId));if(electionTypeId<=0||areaId<=0||lifecycleStateId<=0)throw new ArgumentException("Election references are required.");Id=id;TenantId=tenantId;ElectionTypeId=electionTypeId;AreaId=areaId;LifecycleStateId=lifecycleStateId;Name=Require(name,200);ElectionDate=electionDate;CreatedAtUtc=DateTimeOffset.UtcNow;Version=1;}
    public Guid TenantId{get;private set;} public short ElectionTypeId{get;private set;} public long AreaId{get;private set;} public short LifecycleStateId{get;private set;}
    public string Name{get;private set;}=string.Empty; public DateOnly ElectionDate{get;private set;} public DateTimeOffset CreatedAtUtc{get;private set;} public int Version{get;private set;}
    public static Election Create(Guid tenantId,short electionTypeId,long areaId,short lifecycleStateId,string name,DateOnly electionDate)=>new(Guid.NewGuid(),tenantId,electionTypeId,areaId,lifecycleStateId,name,electionDate);
    public void UpdateDetails(short electionTypeId,long areaId,string name,DateOnly electionDate)
    {
        if(electionTypeId<=0||areaId<=0)throw new ArgumentException("Election references are required.");
        ElectionTypeId=electionTypeId;AreaId=areaId;Name=Require(name,200);ElectionDate=electionDate;Version++;
    }
    public void MoveTo(short lifecycleStateId){if(lifecycleStateId<=0)throw new ArgumentOutOfRangeException(nameof(lifecycleStateId));LifecycleStateId=lifecycleStateId;Version++;}
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
