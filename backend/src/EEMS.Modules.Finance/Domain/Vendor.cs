using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class Vendor:Entity<Guid>
{
    private Vendor(){} private Vendor(Guid id,Guid tenantId,string name,string registrationNumber){if(tenantId==Guid.Empty)throw new ArgumentException("Tenant is required.");Id=id;TenantId=tenantId;Name=FinanceRules.Text(name,180);RegistrationNumber=FinanceRules.Text(registrationNumber,100);IsActive=true;}
    public Guid TenantId{get;private set;} public string Name{get;private set;}=string.Empty; public string RegistrationNumber{get;private set;}=string.Empty; public bool IsActive{get;private set;}
    public static Vendor Create(Guid tenantId,string name,string registrationNumber)=>new(Guid.NewGuid(),tenantId,name,registrationNumber);
}
