using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class Payment:Entity<Guid>
{
    private Payment(){} private Payment(Guid id,Guid tenantId,Guid expenseId,Guid paidByUserId,decimal amount,string reference,DateTimeOffset paidAtUtc){if(tenantId==Guid.Empty||expenseId==Guid.Empty||paidByUserId==Guid.Empty)throw new ArgumentException("Payment references are required.");Id=id;TenantId=tenantId;ExpenseId=expenseId;PaidByUserId=paidByUserId;Amount=FinanceRules.Amount(amount);Reference=FinanceRules.Text(reference,120);PaidAtUtc=paidAtUtc;}
    public Guid TenantId{get;private set;} public Guid ExpenseId{get;private set;} public Guid PaidByUserId{get;private set;} public decimal Amount{get;private set;} public string Reference{get;private set;}=string.Empty; public DateTimeOffset PaidAtUtc{get;private set;}
    public static Payment Record(Guid tenantId,Guid expenseId,Guid paidByUserId,decimal amount,string reference,DateTimeOffset paidAtUtc)=>new(Guid.NewGuid(),tenantId,expenseId,paidByUserId,amount,reference,paidAtUtc);
}
