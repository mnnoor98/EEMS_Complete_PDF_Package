using EEMS.SharedKernel.Domain;
namespace EEMS.Modules.Finance.Domain;
public sealed class ExpenseState:Entity<short>
{
    private ExpenseState(){} private ExpenseState(short id,string code,string name,bool isApproved,bool isTerminal){if(id<=0)throw new ArgumentOutOfRangeException(nameof(id));Id=id;Code=FinanceRules.Text(code,40);Name=FinanceRules.Text(name,100);IsApproved=isApproved;IsTerminal=isTerminal;IsActive=true;}
    public string Code{get;private set;}=string.Empty; public string Name{get;private set;}=string.Empty; public bool IsApproved{get;private set;} public bool IsTerminal{get;private set;} public bool IsActive{get;private set;}
    public static ExpenseState Create(short id,string code,string name,bool isApproved=false,bool isTerminal=false)=>new(id,code,name,isApproved,isTerminal);
}
