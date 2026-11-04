using System.IdentityModel.Tokens.Jwt;
using EEMS.Api.Authorization;
using EEMS.Api.Inventory;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController, Route("api/v1/elections/{electionId:guid}/inventory")]
public sealed class InventoryController(InventoryOperationsService operations) : ControllerBase
{
    [HttpGet("lookups"), Authorize(Policy = PermissionCodes.InventoryRead)] public async Task<ActionResult<InventoryLookups>> GetLookups(Guid electionId,CancellationToken token){var x=await operations.GetLookupsAsync(electionId,token);return x is null?NotFound():Ok(x);}
    [HttpGet("warehouses"), Authorize(Policy = PermissionCodes.InventoryRead)] public async Task<ActionResult<IReadOnlyList<WarehouseSummary>>> GetWarehouses(Guid electionId,CancellationToken token)=>Ok(await operations.GetWarehousesAsync(token));
    [HttpPost("warehouses"), Authorize(Policy = PermissionCodes.InventoryManage)] public async Task<ActionResult<WarehouseSummary>> CreateWarehouse(Guid electionId,CreateWarehouseRequest request,CancellationToken token){var x=await operations.CreateWarehouseAsync(request.AreaId,request.Name,token);return x is null?BadRequest():Ok(x);}
    [HttpGet("items"), Authorize(Policy = PermissionCodes.InventoryRead)] public async Task<ActionResult<IReadOnlyList<ItemSummary>>> GetItems(Guid electionId,CancellationToken token)=>Ok(await operations.GetItemsAsync(token));
    [HttpPost("items"), Authorize(Policy = PermissionCodes.InventoryManage)] public async Task<ActionResult<ItemSummary>> CreateItem(Guid electionId,CreateItemRequest request,CancellationToken token){var x=await operations.CreateItemAsync(request.Sku,request.Name,request.Unit,token);return x is null?BadRequest():Ok(x);}
    [HttpGet("movements"), Authorize(Policy = PermissionCodes.InventoryRead)] public async Task<ActionResult<IReadOnlyList<MovementSummary>>> GetMovements(Guid electionId,CancellationToken token)=>Ok(await operations.GetMovementsAsync(token));
    [HttpPost("movements"), Authorize(Policy = PermissionCodes.InventoryManage)] public async Task<ActionResult<MovementSummary>> RecordMovement(Guid electionId,RecordMovementRequest request,CancellationToken token){if(!TryUserId(out var userId))return Unauthorized();var x=await operations.RecordMovementAsync(userId,new(request.ItemId,request.MovementTypeId,request.SourceWarehouseId,request.DestinationWarehouseId,request.Quantity,request.Reference),token);return x is null?BadRequest():Ok(x);}
    [HttpGet("allocations"), Authorize(Policy = PermissionCodes.InventoryRead)] public async Task<ActionResult<IReadOnlyList<AllocationSummary>>> GetAllocations(Guid electionId,CancellationToken token)=>Ok(await operations.GetAllocationsAsync(electionId,token));
    [HttpPost("allocations"), Authorize(Policy = PermissionCodes.InventoryManage)] public async Task<ActionResult<AllocationSummary>> CreateAllocation(Guid electionId,CreateAllocationRequest request,CancellationToken token){var x=await operations.CreateAllocationAsync(electionId,new(request.ItemId,request.SourceWarehouseId,request.TeamId,request.PollingCenterId,request.RecipientUserId,request.StateId,request.Quantity),token);return x is null?BadRequest():Ok(x);}
    [HttpPut("allocations/{allocationId:guid}/acknowledge"), Authorize(Policy = PermissionCodes.InventoryManage)] public async Task<ActionResult<AllocationSummary>> Acknowledge(Guid electionId,Guid allocationId,CancellationToken token){var x=await operations.AcknowledgeAsync(electionId,allocationId,token);return x is null?Conflict():Ok(x);}
    private bool TryUserId(out Guid userId)=>Guid.TryParse(User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value,out userId);
}
public sealed record CreateWarehouseRequest(long AreaId,string Name); public sealed record CreateItemRequest(string Sku,string Name,string Unit); public sealed record RecordMovementRequest(Guid ItemId,short MovementTypeId,Guid? SourceWarehouseId,Guid? DestinationWarehouseId,decimal Quantity,string Reference); public sealed record CreateAllocationRequest(Guid ItemId,Guid SourceWarehouseId,Guid? TeamId,Guid? PollingCenterId,Guid RecipientUserId,short StateId,decimal Quantity);
