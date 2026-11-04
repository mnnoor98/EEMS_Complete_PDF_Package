namespace EEMS.Modules.Events.Domain;

internal static class TextRules
{
    public static string Required(string value, int maxLength)
    {
        var text = value?.Trim() ?? string.Empty;
        return text.Length is > 0 && text.Length <= maxLength
            ? text
            : throw new ArgumentException("Value is required and exceeds no configured length.");
    }

    public static string? Optional(string? value, int maxLength)
    {
        var text = value?.Trim();
        if (string.IsNullOrEmpty(text)) return null;
        return text.Length <= maxLength ? text : throw new ArgumentException("Value exceeds configured length.");
    }
}
