using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Teams.Domain;
public sealed class Team:Entity<Guid>
{
    private Team(){} private Team(Guid id,Guid tenantId,Guid electionId,long areaId,string name){if(tenantId==Guid.Empty||electionId==Guid.Empty)throw new ArgumentException("Tenant and election are required.");ArgumentOutOfRangeException.ThrowIfNegativeOrZero(areaId);Id=id;TenantId=tenantId;ElectionId=electionId;AreaId=areaId;Name=Require(name,160);IsActive=true;CreatedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;}public Guid ElectionId{get;private set;}public long AreaId{get;private set;}public string Name{get;private set;}=string.Empty;public bool IsActive{get;private set;}public DateTimeOffset CreatedAtUtc{get;private set;}
    public static Team Create(Guid tenantId,Guid electionId,long areaId,string name)=>new(Guid.NewGuid(),tenantId,electionId,areaId,name);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
