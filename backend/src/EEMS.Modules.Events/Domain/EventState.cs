using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class EventState : Entity<short>
{
    private EventState() { }
    private EventState(short id, string code, string name, bool isTerminal)
    {
        if (id <= 0) throw new ArgumentOutOfRangeException(nameof(id));
        Id = id;
        Code = TextRules.Required(code, 40);
        Name = TextRules.Required(name, 100);
        IsTerminal = isTerminal;
        IsActive = true;
    }

    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public bool IsTerminal { get; private set; }
    public bool IsActive { get; private set; }

    public static EventState Create(short id, string code, string name, bool isTerminal = false) =>
        new(id, code, name, isTerminal);
}
