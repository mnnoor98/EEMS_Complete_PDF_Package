using EEMS.Modules.Finance.Domain;
namespace EEMS.UnitTests.Finance;
public sealed class FinanceTests
{
 [Fact]public void ExpenseRequiresPositiveAmount()=>Assert.Throws<ArgumentOutOfRangeException>(()=>Expense.Create(Guid.NewGuid(),Guid.NewGuid(),null,Guid.NewGuid(),1,"INV",0,DateOnly.FromDateTime(DateTime.UtcNow)));
 [Fact]public void MakerCannotApproveOwnExpense(){var user=Guid.NewGuid();Assert.Throws<InvalidOperationException>(()=>ExpenseApproval.Record(Guid.NewGuid(),Guid.NewGuid(),user,user,2,"Approved"));}
 [Fact]public void AdjustmentCannotBeZero()=>Assert.Throws<ArgumentOutOfRangeException>(()=>ExpenseAdjustment.Create(Guid.NewGuid(),Guid.NewGuid(),Guid.NewGuid(),0,"Correction"));
 [Fact]public void CurrencyIsNormalized(){var budget=Budget.Create(Guid.NewGuid(),Guid.NewGuid(),"Campaign","bdt");Assert.Equal("BDT",budget.Currency);}
}
