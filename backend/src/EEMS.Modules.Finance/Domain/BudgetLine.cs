using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class BudgetLine:Entity<Guid>
{
    private BudgetLine(){} private BudgetLine(Guid id,Guid tenantId,Guid budgetId,string category,decimal allocatedAmount){if(tenantId==Guid.Empty||budgetId==Guid.Empty)throw new ArgumentException("Tenant and budget are required.");Id=id;TenantId=tenantId;BudgetId=budgetId;Category=FinanceRules.Text(category,120);AllocatedAmount=FinanceRules.Amount(allocatedAmount);}
    public Guid TenantId{get;private set;} public Guid BudgetId{get;private set;} public string Category{get;private set;}=string.Empty; public decimal AllocatedAmount{get;private set;}
    public static BudgetLine Create(Guid tenantId,Guid budgetId,string category,decimal amount)=>new(Guid.NewGuid(),tenantId,budgetId,category,amount);
}
