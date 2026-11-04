using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Identity.Domain;

public sealed class Permission : Entity<Guid>
{
    private Permission() { }
    private Permission(Guid id, string code, string name, string module)
    {
        Id = id;
        Code = NormalizeCode(code);
        Name = Require(name, nameof(name), 160);
        Module = Require(module, nameof(module), 80);
        IsActive = true;
    }

    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public string Module { get; private set; } = string.Empty;
    public bool IsActive { get; private set; }

    public static Permission Create(string code, string name, string module) => new(Guid.NewGuid(), code, name, module);

    private static string NormalizeCode(string code)
    {
        var value = Require(code, nameof(code), 120).ToLowerInvariant();
        return value.All(character => char.IsAsciiLetterOrDigit(character) || character is '.' or '-' or '_')
            ? value
            : throw new ArgumentException("Permission code contains unsupported characters.", nameof(code));
    }

    private static string Require(string value, string parameter, int maximumLength)
    {
        var normalized = value?.Trim() ?? string.Empty;
        if (normalized.Length is 0 || normalized.Length > maximumLength)
            throw new ArgumentException($"{parameter} must contain between 1 and {maximumLength} characters.", parameter);
        return normalized;
    }
}
