namespace EEMS.Api.ReferenceData;

public sealed class ReferenceDataOptions
{
    public const string SectionName = "ReferenceData";
    public ElectionTypeDefinition[] ElectionTypes { get; init; } = [];
    public LifecycleDefinition[] LifecycleStates { get; init; } = [];
    public PositionDefinition[] Positions { get; init; } = [];
    public AreaTypeDefinition[] AreaTypes { get; init; } = [];
    public AreaDefinition[] Areas { get; init; } = [];
    public TaskStateDefinition[] TaskStates { get; init; } = [];
    public TaskPriorityDefinition[] TaskPriorities { get; init; } = [];
    public ReadinessStateDefinition[] ReadinessStates { get; init; } = [];
    public SubmissionStateDefinition[] SubmissionStates { get; init; } = [];
    public ExportStateDefinition[] ExportStates { get; init; } = [];
    public MovementTypeDefinition[] MovementTypes { get; init; } = [];
    public AllocationStateDefinition[] AllocationStates { get; init; } = [];
}

public sealed class ElectionTypeDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
}
public sealed class LifecycleDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public bool IsTerminal { get; init; }
}
public sealed class PositionDefinition
{
    public long Id { get; init; }
    public short ElectionTypeId { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
}
public sealed class AreaTypeDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public short Level { get; init; }
}
public sealed class AreaDefinition
{
    public long Id { get; init; }
    public long? ParentAreaId { get; init; }
    public short AreaTypeId { get; init; }
    public string Code { get; init; } = string.Empty;
    public string NameBn { get; init; } = string.Empty;
    public string? NameEn { get; init; }
}
public sealed class TaskStateDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public bool IsTerminal { get; init; }
}
public sealed class TaskPriorityDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public short Rank { get; init; }
}
public sealed class ReadinessStateDefinition
{
    public short Id { get; init; }
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public short Rank { get; init; }
}
public sealed class SubmissionStateDefinition { public short Id { get; init; } public string Code { get; init; } = string.Empty; public string Name { get; init; } = string.Empty; public bool IsVerified { get; init; } }
public sealed class ExportStateDefinition { public short Id { get; init; } public string Code { get; init; } = string.Empty; public string Name { get; init; } = string.Empty; public bool IsTerminal { get; init; } }
public sealed class MovementTypeDefinition { public short Id { get; init; } public string Code { get; init; } = string.Empty; public string Name { get; init; } = string.Empty; public bool RequiresSource { get; init; } public bool RequiresDestination { get; init; } }
public sealed class AllocationStateDefinition { public short Id { get; init; } public string Code { get; init; } = string.Empty; public string Name { get; init; } = string.Empty; public bool IsTerminal { get; init; } }
