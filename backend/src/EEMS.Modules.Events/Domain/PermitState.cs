using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Events.Domain;

public sealed class PermitState : Entity<short>
{
    private PermitState() { }
    private PermitState(short id, string code, string name)
    {
        if (id <= 0) throw new ArgumentOutOfRangeException(nameof(id));
        Id = id;
        Code = TextRules.Required(code, 40);
        Name = TextRules.Required(name, 100);
        IsActive = true;
    }

    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public bool IsActive { get; private set; }

    public static PermitState Create(short id, string code, string name) => new(id, code, name);
}
