namespace EEMS.Modules.Finance.Domain;
internal static class FinanceRules
{
    public static string Text(string value, int max) { var text=value?.Trim()??string.Empty; return text.Length is >0 && text.Length<=max?text:throw new ArgumentException("Value is invalid."); }
    public static decimal Amount(decimal value) => value>0?decimal.Round(value,2):throw new ArgumentOutOfRangeException(nameof(value));
}
