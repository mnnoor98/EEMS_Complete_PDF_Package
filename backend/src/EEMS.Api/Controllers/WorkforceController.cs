using System.ComponentModel.DataAnnotations;
using EEMS.Api.Authorization;
using EEMS.Api.Workforce;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/elections/{electionId:guid}/workforce")]
public sealed class WorkforceController(WorkforceOperationsService operations) : ControllerBase
{
    [HttpGet("lookups")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<WorkforceLookups>> GetLookups(Guid electionId, CancellationToken token) => Ok(await operations.GetLookupsAsync(electionId, token));

    [HttpGet("teams")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<TeamSummary>>> GetTeams(Guid electionId, CancellationToken token) => Ok(await operations.GetTeamsAsync(electionId, token));

    [HttpPost("teams")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TeamSummary>> CreateTeam(Guid electionId, CreateTeamRequest request, CancellationToken token)
    {
        var result = await operations.CreateTeamAsync(electionId, new CreateTeamCommand(request.AreaId, request.Name), token);
        return result is null ? BadRequest(new { error = "invalid_team_reference" }) : Ok(result);
    }

    [HttpPut("teams/{teamId:guid}/leader")][Authorize(Policy=PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TeamSummary>> AssignLeader(Guid electionId,Guid teamId,AssignTeamLeaderRequest request,CancellationToken token){var result=await operations.AssignTeamLeaderAsync(electionId,teamId,request.UserId,token);return result is null?BadRequest(new{error="invalid_team_leader"}):Ok(result);}

    [HttpGet("teams/{teamId:guid}/field-members")][Authorize(Policy=PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<FieldMemberSummary>>> GetFieldMembers(Guid electionId,Guid teamId,CancellationToken token)=>Ok(await operations.GetFieldMembersAsync(electionId,teamId,token));

    [HttpPost("teams/{teamId:guid}/field-members")][Authorize(Policy=PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<FieldMemberSummary>> CreateFieldMember(Guid electionId,Guid teamId,CreateFieldMemberRequest request,CancellationToken token){var result=await operations.CreateFieldMemberAsync(electionId,teamId,new(request.FullName,request.Phone,request.MemberType,request.AreaId,request.Address,request.EmergencyContact),token);return result is null?BadRequest(new{error="invalid_or_duplicate_field_member"}):Ok(result);}

    [HttpGet("teams/{teamId:guid}/member-work")][Authorize(Policy=PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<MemberWorkSummary>>> GetMemberWork(Guid electionId,Guid teamId,CancellationToken token)=>Ok(await operations.GetMemberWorkAsync(electionId,teamId,token));

    [HttpPost("teams/{teamId:guid}/member-work")][Authorize(Policy=PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<MemberWorkSummary>> AssignMemberWork(Guid electionId,Guid teamId,AssignMemberWorkRequest request,CancellationToken token){var result=await operations.AssignMemberWorkAsync(electionId,teamId,new(request.MemberId,request.StateId,request.PriorityId,request.Title,request.Instructions,request.DueAtUtc),token);return result is null?BadRequest(new{error="invalid_member_work"}):Ok(result);}

    [HttpPut("teams/{teamId:guid}/member-work/{assignmentId:guid}/state")][Authorize(Policy=PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<MemberWorkSummary>> MoveMemberWork(Guid electionId,Guid teamId,Guid assignmentId,MoveTeamTaskRequest request,CancellationToken token){var result=await operations.MoveMemberWorkAsync(electionId,teamId,assignmentId,request.StateId,request.ExpectedVersion,token);return result is null?Conflict(new{error="invalid_state_or_version"}):Ok(result);}

    [HttpGet("teams/{teamId:guid}/members")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<TeamMemberSummary>>> GetMembers(Guid electionId, Guid teamId, CancellationToken token) => Ok(await operations.GetTeamMembersAsync(electionId, teamId, token));

    [HttpPost("teams/{teamId:guid}/members")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TeamMemberSummary>> AddMember(Guid electionId, Guid teamId, AddTeamMemberRequest request, CancellationToken token)
    {
        var result = await operations.AddTeamMemberAsync(electionId, teamId, new AddTeamMemberCommand(request.UserId, request.Responsibility), token);
        return result is null ? BadRequest(new { error = "invalid_or_duplicate_team_member" }) : Ok(result);
    }

    [HttpGet("tasks")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<TeamTaskSummary>>> GetTasks(Guid electionId, CancellationToken token) => Ok(await operations.GetTasksAsync(electionId, token));

    [HttpPost("tasks")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TeamTaskSummary>> CreateTask(Guid electionId, CreateTeamTaskRequest request, CancellationToken token)
    {
        var result = await operations.CreateTaskAsync(electionId, new CreateTaskCommand(request.TeamId, request.AssigneeUserId, request.StateId, request.PriorityId, request.Title, request.DueAtUtc), token);
        return result is null ? BadRequest(new { error = "invalid_task_reference" }) : Ok(result);
    }

    [HttpPut("tasks/{taskId:guid}/state")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TeamTaskSummary>> MoveTask(Guid electionId, Guid taskId, MoveTeamTaskRequest request, CancellationToken token)
    {
        var result = await operations.MoveTaskAsync(electionId, taskId, request.StateId, request.ExpectedVersion, token);
        return result is null ? Conflict(new { error = "invalid_state_or_version" }) : Ok(result);
    }

    [HttpGet("trainings")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<TrainingSummary>>> GetTrainings(Guid electionId, CancellationToken token) => Ok(await operations.GetTrainingsAsync(electionId, token));

    [HttpPost("trainings")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<TrainingSummary>> CreateTraining(Guid electionId, CreateTrainingRequest request, CancellationToken token)
    {
        var result = await operations.CreateTrainingAsync(electionId, new CreateTrainingCommand(request.Title, request.StartsAtUtc, request.EndsAtUtc), token);
        return result is null ? BadRequest(new { error = "invalid_training_reference" }) : Ok(result);
    }

    [HttpGet("trainings/{trainingId:guid}/attendance")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<AttendanceSummary>>> GetAttendance(Guid electionId, Guid trainingId, CancellationToken token) => Ok(await operations.GetAttendanceAsync(electionId, trainingId, token));

    [HttpPost("trainings/{trainingId:guid}/attendance")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<AttendanceSummary>> RecordAttendance(Guid electionId, Guid trainingId, RecordAttendanceRequest request, CancellationToken token)
    {
        var result = await operations.RecordAttendanceAsync(electionId, trainingId, request.UserId, request.RecordedAtUtc, token);
        return result is null ? BadRequest(new { error = "invalid_or_duplicate_attendance" }) : Ok(result);
    }

    [HttpGet("agents")]
    [Authorize(Policy = PermissionCodes.WorkforceRead)]
    public async Task<ActionResult<IReadOnlyList<AgentAssignmentSummary>>> GetAgents(Guid electionId, CancellationToken token) => Ok(await operations.GetAgentAssignmentsAsync(electionId, token));

    [HttpPost("agents")]
    [Authorize(Policy = PermissionCodes.WorkforceManage)]
    public async Task<ActionResult<AgentAssignmentSummary>> AssignAgent(Guid electionId, AssignAgentRequest request, CancellationToken token)
    {
        var result = await operations.AssignAgentAsync(electionId, new AssignAgentCommand(request.ElectionCenterId, request.UserId, request.StartsAtUtc, request.EndsAtUtc), token);
        return result is null ? BadRequest(new { error = "invalid_agent_reference" }) : Ok(result);
    }
}

public sealed record CreateTeamRequest(long AreaId, [Required, MaxLength(160)] string Name);
public sealed record AssignTeamLeaderRequest(Guid UserId);
public sealed record CreateFieldMemberRequest([Required,MaxLength(200)]string FullName,[Required,MaxLength(30)]string Phone,[Required,MaxLength(80)]string MemberType,long? AreaId,[MaxLength(500)]string? Address,[MaxLength(120)]string? EmergencyContact);
public sealed record AssignMemberWorkRequest(Guid MemberId,short StateId,short PriorityId,[Required,MaxLength(200)]string Title,[MaxLength(1000)]string? Instructions,DateTimeOffset? DueAtUtc);
public sealed record AddTeamMemberRequest(Guid UserId, [Required, MaxLength(120)] string Responsibility);
public sealed record CreateTeamTaskRequest(Guid? TeamId, Guid? AssigneeUserId, short StateId, short PriorityId, [Required, MaxLength(200)] string Title, DateTimeOffset? DueAtUtc);
public sealed record MoveTeamTaskRequest(short StateId, int ExpectedVersion);
public sealed record CreateTrainingRequest([Required, MaxLength(200)] string Title, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc);
public sealed record RecordAttendanceRequest(Guid UserId, DateTimeOffset? RecordedAtUtc);
public sealed record AssignAgentRequest(Guid ElectionCenterId, Guid UserId, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc);
