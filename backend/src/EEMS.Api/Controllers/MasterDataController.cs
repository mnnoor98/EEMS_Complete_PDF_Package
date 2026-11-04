using System.ComponentModel.DataAnnotations;
using EEMS.Api.Authorization;
using EEMS.Api.MasterData;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController,Authorize,Route("api/v1/master-data")]
public sealed class MasterDataController(MasterDataService service):ControllerBase
{
 [HttpGet,Authorize(Policy=PermissionCodes.ElectionsRead)]public async Task<ActionResult<MasterDataWorkspace>> Get(CancellationToken ct)=>Ok(await service.Get(ct));
 [HttpPost("areas"),Authorize(Policy=PermissionCodes.ElectionsManage)]public async Task<ActionResult<AreaItem>> AddArea(CreateAreaRequest r,CancellationToken ct){var x=await service.AddArea(new(r.Id,r.ParentAreaId,r.AreaTypeId,r.Code,r.NameBn,r.NameEn),ct);return x is null?BadRequest(new{error="duplicate_or_invalid_area_reference"}):Ok(x);}
 [HttpPost("election-types"),Authorize(Policy=PermissionCodes.ElectionsManage)]public async Task<ActionResult<ElectionTypeItem>> AddElectionType(CreateElectionTypeRequest r,CancellationToken ct){var x=await service.AddElectionType(new(r.Id,r.Code,r.Name),ct);return x is null?BadRequest(new{error="duplicate_election_type"}):Ok(x);}
 [HttpPost("positions"),Authorize(Policy=PermissionCodes.ElectionsManage)]public async Task<ActionResult<PositionItem>> AddPosition(CreatePositionRequest r,CancellationToken ct){var x=await service.AddPosition(new(r.Id,r.ElectionTypeId,r.Code,r.Name),ct);return x is null?BadRequest(new{error="duplicate_or_invalid_position"}):Ok(x);}
 [HttpPost("task-states"),Authorize(Policy=PermissionCodes.ElectionsManage)]public async Task<ActionResult<TaskStateItem>> AddTaskState(CreateTaskStateRequest r,CancellationToken ct){var x=await service.AddTaskState(new(r.Id,r.Code,r.Name,r.IsTerminal),ct);return x is null?BadRequest(new{error="duplicate_task_state"}):Ok(x);}
 [HttpPost("task-priorities"),Authorize(Policy=PermissionCodes.ElectionsManage)]public async Task<ActionResult<TaskPriorityItem>> AddTaskPriority(CreateTaskPriorityRequest r,CancellationToken ct){var x=await service.AddTaskPriority(new(r.Id,r.Code,r.Name,r.Rank),ct);return x is null?BadRequest(new{error="duplicate_task_priority_or_rank"}):Ok(x);}
}
public sealed record CreateAreaRequest([Range(1,long.MaxValue)]long Id,long? ParentAreaId,[Range(1,short.MaxValue)]short AreaTypeId,[Required,MaxLength(40)]string Code,[Required,MaxLength(200)]string NameBn,[MaxLength(200)]string? NameEn);public sealed record CreateElectionTypeRequest([Range(1,short.MaxValue)]short Id,[Required,MaxLength(40)]string Code,[Required,MaxLength(120)]string Name);public sealed record CreatePositionRequest([Range(1,long.MaxValue)]long Id,[Range(1,short.MaxValue)]short ElectionTypeId,[Required,MaxLength(60)]string Code,[Required,MaxLength(120)]string Name);public sealed record CreateTaskStateRequest([Range(1,short.MaxValue)]short Id,[Required,MaxLength(40)]string Code,[Required,MaxLength(100)]string Name,bool IsTerminal);public sealed record CreateTaskPriorityRequest([Range(1,short.MaxValue)]short Id,[Required,MaxLength(40)]string Code,[Required,MaxLength(100)]string Name,[Range(1,short.MaxValue)]short Rank);
