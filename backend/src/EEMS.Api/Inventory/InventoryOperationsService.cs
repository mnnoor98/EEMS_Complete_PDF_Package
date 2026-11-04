using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Inventory.Domain;
using EEMS.Modules.Inventory.Infrastructure;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Inventory;

public sealed class InventoryOperationsService(InventoryDbContext inventoryDb, ElectionsDbContext electionsDb, GeographyDbContext geographyDb, TeamsDbContext teamsDb, PollingDbContext pollingDb, IdentityDbContext identityDb, ITenantContext tenantContext)
{
    public async Task<InventoryLookups?> GetLookupsAsync(Guid electionId, CancellationToken token)
    {
        if (!await ElectionExists(electionId, token)) return null;
        var centers = await (from link in pollingDb.ElectionCenters join center in pollingDb.Centers on link.CenterId equals center.Id where link.TenantId == tenantContext.TenantId && link.ElectionId == electionId orderby center.Name select new NamedReference(link.Id, center.Name)).ToListAsync(token);
        return new(
            await geographyDb.Areas.Where(x => x.IsActive).OrderBy(x => x.NameEn ?? x.NameBn).Select(x => new AreaReference(x.Id, x.NameEn ?? x.NameBn)).ToListAsync(token),
            await teamsDb.Teams.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.IsActive).OrderBy(x => x.Name).Select(x => new NamedReference(x.Id, x.Name)).ToListAsync(token), centers,
            await identityDb.Users.Where(x => x.IsActive).OrderBy(x => x.DisplayName).Select(x => new NamedReference(x.Id, x.DisplayName)).ToListAsync(token),
            await inventoryDb.MovementTypes.Where(x => x.IsActive).OrderBy(x => x.Id).Select(x => new MovementTypeReference(x.Id, x.Code, x.Name, x.RequiresSource, x.RequiresDestination)).ToListAsync(token),
            await inventoryDb.AllocationStates.Where(x => x.IsActive).OrderBy(x => x.Id).Select(x => new AllocationStateReference(x.Id, x.Code, x.Name, x.IsTerminal)).ToListAsync(token));
    }

    public async Task<IReadOnlyList<WarehouseSummary>> GetWarehousesAsync(CancellationToken token) => await inventoryDb.Warehouses.Where(x => x.TenantId == tenantContext.TenantId && x.IsActive).OrderBy(x => x.Name).Select(x => new WarehouseSummary(x.Id, x.AreaId, x.Name)).ToListAsync(token);
    public async Task<WarehouseSummary?> CreateWarehouseAsync(long areaId, string name, CancellationToken token)
    {
        if (!await geographyDb.Areas.AnyAsync(x => x.Id == areaId && x.IsActive, token) || await inventoryDb.Warehouses.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.AreaId == areaId && x.Name == name.Trim(), token)) return null;
        var item = Warehouse.Create(tenantContext.TenantId, areaId, name); inventoryDb.Warehouses.Add(item); await inventoryDb.SaveChangesAsync(token); return new(item.Id, item.AreaId, item.Name);
    }
    public async Task<IReadOnlyList<ItemSummary>> GetItemsAsync(CancellationToken token) => await inventoryDb.Items.Where(x => x.TenantId == tenantContext.TenantId && x.IsActive).OrderBy(x => x.Name).Select(x => new ItemSummary(x.Id, x.Sku, x.Name, x.Unit)).ToListAsync(token);
    public async Task<ItemSummary?> CreateItemAsync(string sku, string name, string unit, CancellationToken token)
    {
        var normalized = sku.Trim().ToUpperInvariant(); if (await inventoryDb.Items.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Sku == normalized, token)) return null;
        var item = InventoryItem.Create(tenantContext.TenantId, normalized, name, unit); inventoryDb.Items.Add(item); await inventoryDb.SaveChangesAsync(token); return new(item.Id, item.Sku, item.Name, item.Unit);
    }
    public async Task<IReadOnlyList<MovementSummary>> GetMovementsAsync(CancellationToken token) => await inventoryDb.Movements.Where(x => x.TenantId == tenantContext.TenantId).OrderByDescending(x => x.OccurredAtUtc).Select(x => new MovementSummary(x.Id, x.ItemId, x.MovementTypeId, x.SourceWarehouseId, x.DestinationWarehouseId, x.ActorUserId, x.Quantity, x.Reference, x.OccurredAtUtc)).ToListAsync(token);
    public async Task<MovementSummary?> RecordMovementAsync(Guid actorId, RecordMovementCommand command, CancellationToken token)
    {
        var type = await inventoryDb.MovementTypes.SingleOrDefaultAsync(x => x.Id == command.MovementTypeId && x.IsActive, token);
        var itemOk = await inventoryDb.Items.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == command.ItemId && x.IsActive, token);
        var warehouseIds = new[] { command.SourceWarehouseId, command.DestinationWarehouseId }.Where(x => x.HasValue).Select(x => x!.Value).Distinct().ToArray();
        var warehousesOk = await inventoryDb.Warehouses.CountAsync(x => x.TenantId == tenantContext.TenantId && warehouseIds.Contains(x.Id) && x.IsActive, token) == warehouseIds.Length;
        if (type is null || !itemOk || !warehousesOk || type.RequiresSource != command.SourceWarehouseId.HasValue || type.RequiresDestination != command.DestinationWarehouseId.HasValue || command.Quantity <= 0 || string.IsNullOrWhiteSpace(command.Reference)) return null;
        var movement = StockMovement.Record(tenantContext.TenantId, command.ItemId, type.Id, command.SourceWarehouseId, command.DestinationWarehouseId, actorId, command.Quantity, command.Reference);
        inventoryDb.Movements.Add(movement); await inventoryDb.SaveChangesAsync(token); return new(movement.Id, movement.ItemId, movement.MovementTypeId, movement.SourceWarehouseId, movement.DestinationWarehouseId, actorId, movement.Quantity, movement.Reference, movement.OccurredAtUtc);
    }
    public async Task<IReadOnlyList<AllocationSummary>> GetAllocationsAsync(Guid electionId, CancellationToken token) => await inventoryDb.Allocations.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId).OrderByDescending(x => x.CreatedAtUtc).Select(x => new AllocationSummary(x.Id, x.ItemId, x.SourceWarehouseId, x.TeamId, x.PollingCenterId, x.RecipientUserId, x.StateId, x.Quantity, x.CreatedAtUtc, x.AcknowledgedAtUtc)).ToListAsync(token);
    public async Task<AllocationSummary?> CreateAllocationAsync(Guid electionId, CreateAllocationCommand command, CancellationToken token)
    {
        var valid = await ElectionExists(electionId, token) && await inventoryDb.Items.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == command.ItemId && x.IsActive, token) && await inventoryDb.Warehouses.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == command.SourceWarehouseId && x.IsActive, token) && await identityDb.Users.AnyAsync(x => x.Id == command.RecipientUserId && x.IsActive, token) && await inventoryDb.AllocationStates.AnyAsync(x => x.Id == command.StateId && x.IsActive, token);
        var targetCount = (command.TeamId.HasValue ? 1 : 0) + (command.PollingCenterId.HasValue ? 1 : 0);
        if (!valid || targetCount != 1 || command.Quantity <= 0 || (command.TeamId.HasValue && !await teamsDb.Teams.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == command.TeamId && x.IsActive, token)) || (command.PollingCenterId.HasValue && !await pollingDb.ElectionCenters.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == command.PollingCenterId, token))) return null;
        var allocation = StockAllocation.Create(tenantContext.TenantId, electionId, command.ItemId, command.SourceWarehouseId, command.TeamId, command.PollingCenterId, command.RecipientUserId, command.StateId, command.Quantity); inventoryDb.Allocations.Add(allocation); await inventoryDb.SaveChangesAsync(token); return ToSummary(allocation);
    }
    public async Task<AllocationSummary?> AcknowledgeAsync(Guid electionId, Guid allocationId, CancellationToken token)
    {
        var allocation = await inventoryDb.Allocations.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == allocationId, token); if (allocation is null || allocation.AcknowledgedAtUtc is not null) return null;
        var terminal = await inventoryDb.AllocationStates.Where(x => x.IsActive && x.IsTerminal).OrderBy(x => x.Id).FirstOrDefaultAsync(token); if (terminal is null) return null;
        allocation.Acknowledge(); allocation.MoveTo(terminal.Id); await inventoryDb.SaveChangesAsync(token); return ToSummary(allocation);
    }
    private Task<bool> ElectionExists(Guid electionId, CancellationToken token) => electionsDb.Elections.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token);
    private static AllocationSummary ToSummary(StockAllocation x) => new(x.Id, x.ItemId, x.SourceWarehouseId, x.TeamId, x.PollingCenterId, x.RecipientUserId, x.StateId, x.Quantity, x.CreatedAtUtc, x.AcknowledgedAtUtc);
}

public sealed record InventoryLookups(IReadOnlyList<AreaReference> Areas,IReadOnlyList<NamedReference> Teams,IReadOnlyList<NamedReference> Centers,IReadOnlyList<NamedReference> Users,IReadOnlyList<MovementTypeReference> MovementTypes,IReadOnlyList<AllocationStateReference> AllocationStates);
public sealed record AreaReference(long Id,string Name); public sealed record NamedReference(Guid Id,string Name); public sealed record MovementTypeReference(short Id,string Code,string Name,bool RequiresSource,bool RequiresDestination); public sealed record AllocationStateReference(short Id,string Code,string Name,bool IsTerminal);
public sealed record WarehouseSummary(Guid WarehouseId,long AreaId,string Name); public sealed record ItemSummary(Guid ItemId,string Sku,string Name,string Unit); public sealed record MovementSummary(Guid MovementId,Guid ItemId,short MovementTypeId,Guid? SourceWarehouseId,Guid? DestinationWarehouseId,Guid ActorUserId,decimal Quantity,string Reference,DateTimeOffset OccurredAtUtc); public sealed record AllocationSummary(Guid AllocationId,Guid ItemId,Guid SourceWarehouseId,Guid? TeamId,Guid? PollingCenterId,Guid RecipientUserId,short StateId,decimal Quantity,DateTimeOffset CreatedAtUtc,DateTimeOffset? AcknowledgedAtUtc);
public sealed record RecordMovementCommand(Guid ItemId,short MovementTypeId,Guid? SourceWarehouseId,Guid? DestinationWarehouseId,decimal Quantity,string Reference); public sealed record CreateAllocationCommand(Guid ItemId,Guid SourceWarehouseId,Guid? TeamId,Guid? PollingCenterId,Guid RecipientUserId,short StateId,decimal Quantity);
