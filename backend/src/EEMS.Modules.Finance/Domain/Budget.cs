using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class Budget:Entity<Guid>
{
    private Budget(){} private Budget(Guid id,Guid tenantId,Guid electionId,string name,string currency){if(tenantId==Guid.Empty||electionId==Guid.Empty)throw new ArgumentException("Tenant and election are required.");Id=id;TenantId=tenantId;ElectionId=electionId;Name=FinanceRules.Text(name,160);Currency=FinanceRules.Text(currency,3).ToUpperInvariant();CreatedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;} public Guid ElectionId{get;private set;} public string Name{get;private set;}=string.Empty; public string Currency{get;private set;}=string.Empty; public DateTimeOffset CreatedAtUtc{get;private set;}
    public static Budget Create(Guid tenantId,Guid electionId,string name,string currency)=>new(Guid.NewGuid(),tenantId,electionId,name,currency);
}
