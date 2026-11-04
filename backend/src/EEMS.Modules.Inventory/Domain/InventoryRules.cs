namespace EEMS.Modules.Inventory.Domain;
internal static class InventoryRules{public static string Text(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}}
