using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Teams.Domain;
public sealed class Training:Entity<Guid>
{
    private Training(){}private Training(Guid id,Guid tenantId,Guid electionId,string title,DateTimeOffset startsAtUtc,DateTimeOffset endsAtUtc){if(tenantId==Guid.Empty||electionId==Guid.Empty)throw new ArgumentException("Tenant and election are required.");if(endsAtUtc<=startsAtUtc)throw new ArgumentException("Training end must be after start.");Id=id;TenantId=tenantId;ElectionId=electionId;Title=Text(title,200);StartsAtUtc=startsAtUtc;EndsAtUtc=endsAtUtc;}
    public Guid TenantId{get;private set;}public Guid ElectionId{get;private set;}public string Title{get;private set;}=string.Empty;public DateTimeOffset StartsAtUtc{get;private set;}public DateTimeOffset EndsAtUtc{get;private set;}public static Training Create(Guid tenantId,Guid electionId,string title,DateTimeOffset startsAtUtc,DateTimeOffset endsAtUtc)=>new(Guid.NewGuid(),tenantId,electionId,title,startsAtUtc,endsAtUtc);private static string Text(string v,int m){var t=v?.Trim()??string.Empty;return t.Length is >0&&t.Length<=m?t:throw new ArgumentException("Value is invalid.");}
}
