using EEMS.Modules.Elections.Domain;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Events.Domain;
using EEMS.Modules.Events.Infrastructure;
using EEMS.Modules.Geography.Domain;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Inventory.Domain;
using EEMS.Modules.Inventory.Infrastructure;
using EEMS.Modules.Teams.Domain;
using EEMS.Modules.Teams.Infrastructure;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.MasterData;

public sealed class MasterDataService(
    GeographyDbContext geography,
    ElectionsDbContext elections,
    TeamsDbContext teams,
    EventsDbContext events,
    InventoryDbContext inventory)
{
    public async Task<MasterDataWorkspace> Get(CancellationToken ct) => new(
        await geography.AreaTypes.Where(x => x.IsActive).OrderBy(x => x.Level).Select(x => new AreaTypeItem(x.Id, x.Code, x.Name, x.Level)).ToListAsync(ct),
        await geography.Areas.OrderBy(x => x.NameEn ?? x.NameBn).Select(x => new AreaItem(x.Id, x.ParentAreaId, x.AreaTypeId, x.Code, x.NameBn, x.NameEn, x.IsActive)).ToListAsync(ct),
        await elections.ElectionTypes.OrderBy(x => x.Name).Select(x => new ElectionTypeItem(x.Id, x.Code, x.Name, x.IsActive)).ToListAsync(ct),
        await elections.LifecycleStates.OrderBy(x => x.Id).Select(x => new LifecycleStateItem(x.Id, x.Code, x.Name, x.IsTerminal, x.IsActive)).ToListAsync(ct),
        await elections.Positions.OrderBy(x => x.Name).Select(x => new PositionItem(x.Id, x.ElectionTypeId, x.Code, x.Name, x.IsActive)).ToListAsync(ct),
        await teams.TaskStates.OrderBy(x => x.Id).Select(x => new TaskStateItem(x.Id, x.Code, x.Name, x.IsTerminal, x.IsActive)).ToListAsync(ct),
        await teams.TaskPriorities.OrderBy(x => x.Rank).Select(x => new TaskPriorityItem(x.Id, x.Code, x.Name, x.Rank, x.IsActive)).ToListAsync(ct),
        await events.EventTypes.OrderBy(x => x.Id).Select(x => new EventTypeItem(x.Id, x.Code, x.Name, x.IsActive)).ToListAsync(ct),
        await inventory.MovementTypes.OrderBy(x => x.Id).Select(x => new MovementTypeItem(x.Id, x.Code, x.Name, x.RequiresSource, x.RequiresDestination, x.IsActive)).ToListAsync(ct));

    public async Task<AreaItem?> AddArea(CreateAreaCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (await geography.Areas.MaxAsync(x => (long?)x.Id, ct) ?? 0) + 1;
        if (await geography.Areas.AnyAsync(x => x.Id == id || x.Code == code, ct) ||
            !await geography.AreaTypes.AnyAsync(x => x.Id == c.AreaTypeId && x.IsActive, ct) ||
            c.ParentAreaId is not null && !await geography.Areas.AnyAsync(x => x.Id == c.ParentAreaId && x.IsActive, ct))
            return null;
        var x = Area.Create(id, c.ParentAreaId, c.AreaTypeId, code, c.NameBn, c.NameEn);
        geography.Areas.Add(x);
        await geography.SaveChangesAsync(ct);
        return new(x.Id, x.ParentAreaId, x.AreaTypeId, x.Code, x.NameBn, x.NameEn, x.IsActive);
    }

    public async Task<AreaTypeItem?> AddAreaType(CreateAreaTypeCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await geography.AreaTypes.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await geography.AreaTypes.AnyAsync(x => x.Id == id || x.Code == code || x.Level == c.Level, ct))
            return null;
        var x = AreaType.Create(id, code, c.Name, c.Level);
        geography.AreaTypes.Add(x);
        await geography.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.Level);
    }

    public async Task<ElectionTypeItem?> AddElectionType(CreateElectionTypeCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await elections.ElectionTypes.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await elections.ElectionTypes.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = ElectionType.Create(id, code, c.Name);
        elections.ElectionTypes.Add(x);
        await elections.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.IsActive);
    }

    public async Task<LifecycleStateItem?> AddLifecycleState(CreateLifecycleStateCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await elections.LifecycleStates.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await elections.LifecycleStates.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = ElectionLifecycleState.Create(id, code, c.Name, c.IsTerminal);
        elections.LifecycleStates.Add(x);
        await elections.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.IsTerminal, x.IsActive);
    }

    public async Task<PositionItem?> AddPosition(CreatePositionCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (await elections.Positions.MaxAsync(x => (long?)x.Id, ct) ?? 0) + 1;
        if (!await elections.ElectionTypes.AnyAsync(x => x.Id == c.ElectionTypeId && x.IsActive, ct) ||
            await elections.Positions.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = Position.Create(id, c.ElectionTypeId, code, c.Name);
        elections.Positions.Add(x);
        await elections.SaveChangesAsync(ct);
        return new(x.Id, x.ElectionTypeId, x.Code, x.Name, x.IsActive);
    }

    public async Task<TaskStateItem?> AddTaskState(CreateTaskStateCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await teams.TaskStates.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await teams.TaskStates.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = TaskState.Create(id, code, c.Name, c.IsTerminal);
        teams.TaskStates.Add(x);
        await teams.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.IsTerminal, x.IsActive);
    }

    public async Task<TaskPriorityItem?> AddTaskPriority(CreateTaskPriorityCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await teams.TaskPriorities.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await teams.TaskPriorities.AnyAsync(x => x.Id == id || x.Code == code || x.Rank == c.Rank, ct))
            return null;
        var x = TaskPriority.Create(id, code, c.Name, c.Rank);
        teams.TaskPriorities.Add(x);
        await teams.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.Rank, x.IsActive);
    }

    public async Task<EventTypeItem?> AddEventType(CreateEventTypeCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await events.EventTypes.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await events.EventTypes.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = EventType.Create(id, code, c.Name);
        events.EventTypes.Add(x);
        await events.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.IsActive);
    }

    public async Task<MovementTypeItem?> AddMovementType(CreateMovementTypeCommand c, CancellationToken ct)
    {
        var code = c.Code.Trim().ToUpperInvariant();
        var id = c.Id > 0 ? c.Id : (short)((await inventory.MovementTypes.MaxAsync(x => (short?)x.Id, ct) ?? 0) + 1);
        if (await inventory.MovementTypes.AnyAsync(x => x.Id == id || x.Code == code, ct))
            return null;
        var x = MovementType.Create(id, code, c.Name, c.RequiresSource, c.RequiresDestination);
        inventory.MovementTypes.Add(x);
        await inventory.SaveChangesAsync(ct);
        return new(x.Id, x.Code, x.Name, x.RequiresSource, x.RequiresDestination, x.IsActive);
    }
}

public sealed record MasterDataWorkspace(
    IReadOnlyList<AreaTypeItem> AreaTypes,
    IReadOnlyList<AreaItem> Areas,
    IReadOnlyList<ElectionTypeItem> ElectionTypes,
    IReadOnlyList<LifecycleStateItem> LifecycleStates,
    IReadOnlyList<PositionItem> Positions,
    IReadOnlyList<TaskStateItem> TaskStates,
    IReadOnlyList<TaskPriorityItem> TaskPriorities,
    IReadOnlyList<EventTypeItem> EventTypes,
    IReadOnlyList<MovementTypeItem> MovementTypes);

public sealed record AreaTypeItem(short Id, string Code, string Name, short Level);
public sealed record AreaItem(long Id, long? ParentAreaId, short AreaTypeId, string Code, string NameBn, string? NameEn, bool IsActive);
public sealed record ElectionTypeItem(short Id, string Code, string Name, bool IsActive);
public sealed record LifecycleStateItem(short Id, string Code, string Name, bool IsTerminal, bool IsActive);
public sealed record PositionItem(long Id, short ElectionTypeId, string Code, string Name, bool IsActive);
public sealed record TaskStateItem(short Id, string Code, string Name, bool IsTerminal, bool IsActive);
public sealed record TaskPriorityItem(short Id, string Code, string Name, short Rank, bool IsActive);
public sealed record EventTypeItem(short Id, string Code, string Name, bool IsActive);
public sealed record MovementTypeItem(short Id, string Code, string Name, bool RequiresSource, bool RequiresDestination, bool IsActive);

public sealed record CreateAreaCommand(long Id, long? ParentAreaId, short AreaTypeId, string Code, string NameBn, string? NameEn);
public sealed record CreateAreaTypeCommand(short Id, string Code, string Name, short Level);
public sealed record CreateElectionTypeCommand(short Id, string Code, string Name);
public sealed record CreateLifecycleStateCommand(short Id, string Code, string Name, bool IsTerminal);
public sealed record CreatePositionCommand(long Id, short ElectionTypeId, string Code, string Name);
public sealed record CreateTaskStateCommand(short Id, string Code, string Name, bool IsTerminal);
public sealed record CreateTaskPriorityCommand(short Id, string Code, string Name, short Rank);
public sealed record CreateEventTypeCommand(short Id, string Code, string Name);
public sealed record CreateMovementTypeCommand(short Id, string Code, string Name, bool RequiresSource, bool RequiresDestination);
