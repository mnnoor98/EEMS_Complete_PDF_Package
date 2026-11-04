using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class ExpenseAdjustment:Entity<Guid>
{
    private ExpenseAdjustment(){} private ExpenseAdjustment(Guid id,Guid tenantId,Guid expenseId,Guid createdByUserId,decimal amount,string reason){if(tenantId==Guid.Empty||expenseId==Guid.Empty||createdByUserId==Guid.Empty)throw new ArgumentException("Adjustment references are required.");ArgumentOutOfRangeException.ThrowIfZero(amount);Id=id;TenantId=tenantId;ExpenseId=expenseId;CreatedByUserId=createdByUserId;Amount=decimal.Round(amount,2);Reason=FinanceRules.Text(reason,1000);CreatedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;} public Guid ExpenseId{get;private set;} public Guid CreatedByUserId{get;private set;} public decimal Amount{get;private set;} public string Reason{get;private set;}=string.Empty; public DateTimeOffset CreatedAtUtc{get;private set;}
    public static ExpenseAdjustment Create(Guid tenantId,Guid expenseId,Guid userId,decimal amount,string reason)=>new(Guid.NewGuid(),tenantId,expenseId,userId,amount,reason);
}
