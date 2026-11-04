using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class EventType : Entity<short>
{
    private EventType() { }
    private EventType(short id, string code, string name)
    {
        if (id <= 0) throw new ArgumentOutOfRangeException(nameof(id));
        Id = id;
        Code = Required(code, 40);
        Name = Required(name, 100);
        IsActive = true;
    }

    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public bool IsActive { get; private set; }

    public static EventType Create(short id, string code, string name) => new(id, code, name);
    private static string Required(string value, int max) => TextRules.Required(value, max);
}
