using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class Expense:Entity<Guid>
{
    private Expense(){} private Expense(Guid id,Guid tenantId,Guid budgetLineId,Guid? vendorId,Guid submittedByUserId,short stateId,string invoiceNumber,decimal amount,DateOnly expenseDate){if(tenantId==Guid.Empty||budgetLineId==Guid.Empty||submittedByUserId==Guid.Empty)throw new ArgumentException("Tenant, budget line and submitter are required.");if(stateId<=0)throw new ArgumentOutOfRangeException(nameof(stateId));Id=id;TenantId=tenantId;BudgetLineId=budgetLineId;VendorId=vendorId;SubmittedByUserId=submittedByUserId;StateId=stateId;InvoiceNumber=FinanceRules.Text(invoiceNumber,100);Amount=FinanceRules.Amount(amount);ExpenseDate=expenseDate;CreatedAtUtc=DateTimeOffset.UtcNow;Version=1;}
    public Guid TenantId{get;private set;} public Guid BudgetLineId{get;private set;} public Guid? VendorId{get;private set;} public Guid SubmittedByUserId{get;private set;} public short StateId{get;private set;} public string InvoiceNumber{get;private set;}=string.Empty; public decimal Amount{get;private set;} public DateOnly ExpenseDate{get;private set;} public DateTimeOffset CreatedAtUtc{get;private set;} public int Version{get;private set;}
    public static Expense Create(Guid tenantId,Guid budgetLineId,Guid? vendorId,Guid submitterId,short stateId,string invoiceNumber,decimal amount,DateOnly date)=>new(Guid.NewGuid(),tenantId,budgetLineId,vendorId,submitterId,stateId,invoiceNumber,amount,date);
    public void MoveTo(short stateId){if(stateId<=0)throw new ArgumentOutOfRangeException(nameof(stateId));StateId=stateId;Version++;}
}
