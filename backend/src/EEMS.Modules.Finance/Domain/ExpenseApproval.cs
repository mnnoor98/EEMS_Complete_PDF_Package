using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class ExpenseApproval:Entity<Guid>
{
    private ExpenseApproval(){} private ExpenseApproval(Guid id,Guid tenantId,Guid expenseId,Guid makerUserId,Guid checkerUserId,short resultingStateId,string note){if(tenantId==Guid.Empty||expenseId==Guid.Empty||makerUserId==Guid.Empty||checkerUserId==Guid.Empty)throw new ArgumentException("Approval references are required.");if(makerUserId==checkerUserId)throw new InvalidOperationException("Maker cannot approve own expense.");if(resultingStateId<=0)throw new ArgumentOutOfRangeException(nameof(resultingStateId));Id=id;TenantId=tenantId;ExpenseId=expenseId;MakerUserId=makerUserId;CheckerUserId=checkerUserId;ResultingStateId=resultingStateId;Note=FinanceRules.Text(note,1000);DecidedAtUtc=DateTimeOffset.UtcNow;}
    public Guid TenantId{get;private set;} public Guid ExpenseId{get;private set;} public Guid MakerUserId{get;private set;} public Guid CheckerUserId{get;private set;} public short ResultingStateId{get;private set;} public string Note{get;private set;}=string.Empty; public DateTimeOffset DecidedAtUtc{get;private set;}
    public static ExpenseApproval Record(Guid tenantId,Guid expenseId,Guid makerId,Guid checkerId,short stateId,string note)=>new(Guid.NewGuid(),tenantId,expenseId,makerId,checkerId,stateId,note);
}
