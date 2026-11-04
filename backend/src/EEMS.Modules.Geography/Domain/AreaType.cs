using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Geography.Domain;

public sealed class AreaType : Entity<short>
{
    private AreaType() { }
    private AreaType(short id, string code, string name, short level)
    {
        if (id <= 0) throw new ArgumentOutOfRangeException(nameof(id));
        if (level <= 0) throw new ArgumentOutOfRangeException(nameof(level));
        Id = id; Code = NormalizeCode(code); Name = Require(name, nameof(name), 120); Level = level; IsActive = true;
    }
    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public short Level { get; private set; }
    public bool IsActive { get; private set; }
    public static AreaType Create(short id, string code, string name, short level) => new(id, code, name, level);
    private static string NormalizeCode(string value) => Require(value, nameof(value), 40).ToUpperInvariant();
    private static string Require(string value, string parameter, int max)
    { var text=value?.Trim()??string.Empty; return text.Length is >0 && text.Length<=max ? text : throw new ArgumentException($"{parameter} is invalid.", parameter); }
}
