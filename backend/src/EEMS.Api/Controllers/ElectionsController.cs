using System.ComponentModel.DataAnnotations;
using EEMS.Api.Authorization;
using EEMS.Api.Elections;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/elections")]
public sealed class ElectionsController(ElectionOperationsService operations) : ControllerBase
{
    [HttpGet("lookups")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<ElectionLookups>> GetLookups(CancellationToken token) => Ok(await operations.GetLookupsAsync(token));

    [HttpGet]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<ElectionSummary>>> GetElections(CancellationToken token) => Ok(await operations.GetElectionsAsync(token));

    [HttpPost]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<ActionResult<ElectionSummary>> CreateElection(CreateElectionRequest request, CancellationToken token)
    {
        var created = await operations.CreateElectionAsync(new CreateElectionCommand(request.ElectionTypeId, request.AreaId, request.LifecycleStateId, request.Name, request.ElectionDate), token);
        return created is null ? BadRequest(new { error = "invalid_election_reference" }) : CreatedAtAction(nameof(GetElections), created);
    }

    [HttpPut("{electionId:guid}")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<ActionResult<ElectionSummary>> UpdateElection(Guid electionId, UpdateElectionRequest request, CancellationToken token)
    {
        var result = await operations.UpdateElectionAsync(electionId, new UpdateElectionCommand(request.ElectionTypeId, request.AreaId, request.Name, request.ElectionDate, request.ExpectedVersion), token);
        return result.Status switch
        {
            ElectionUpdateStatus.Updated => Ok(result.Election),
            ElectionUpdateStatus.NotFound => NotFound(),
            ElectionUpdateStatus.InvalidReference => BadRequest(new { error = "invalid_election_reference" }),
            _ => Conflict(new { error = "invalid_version" })
        };
    }

    [HttpPut("{electionId:guid}/lifecycle")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<IActionResult> MoveElection(Guid electionId, MoveElectionRequest request, CancellationToken token) =>
        await operations.MoveElectionAsync(electionId, request.LifecycleStateId, request.ExpectedVersion, token) ? NoContent() : Conflict(new { error = "invalid_state_or_version" });

    [HttpGet("{electionId:guid}/candidates")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateSummary>>> GetCandidates(Guid electionId, CancellationToken token) => Ok(await operations.GetCandidatesAsync(electionId, token));

    [HttpPost("{electionId:guid}/candidates")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<ActionResult<CandidateSummary>> AddCandidate(Guid electionId, AddCandidateRequest request, CancellationToken token)
    {
        var created = await operations.AddCandidateAsync(electionId, new AddCandidateCommand(request.Name, request.ExternalReference, request.PositionId, request.AreaId, request.NominationReference), token);
        return created is null ? BadRequest(new { error = "invalid_candidate_reference" }) : Ok(created);
    }

    [HttpGet("{electionId:guid}/centers")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<ElectionCenterSummary>>> GetCenters(Guid electionId, CancellationToken token) => Ok(await operations.GetElectionCentersAsync(electionId, token));

    [HttpPost("{electionId:guid}/centers")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<ActionResult<ElectionCenterSummary>> AddCenter(Guid electionId, AddElectionCenterRequest request, CancellationToken token)
    {
        var created = await operations.AddElectionCenterAsync(electionId, new AddElectionCenterCommand(request.AreaId, request.Code, request.Name, request.Address), token);
        return created is null ? BadRequest(new { error = "invalid_center_reference" }) : Ok(created);
    }

    [HttpPost("{electionId:guid}/centers/{electionCenterId:guid}/verify")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<IActionResult> VerifyCenter(Guid electionId, Guid electionCenterId, CancellationToken token) =>
        await operations.VerifyElectionCenterAsync(electionId, electionCenterId, token) ? NoContent() : NotFound();
}

public sealed record CreateElectionRequest(short ElectionTypeId, long AreaId, short LifecycleStateId, [Required, MaxLength(200)] string Name, DateOnly ElectionDate);
public sealed record UpdateElectionRequest(short ElectionTypeId, long AreaId, [Required, MaxLength(200)] string Name, DateOnly ElectionDate, int ExpectedVersion);
public sealed record MoveElectionRequest(short LifecycleStateId, int ExpectedVersion);
public sealed record AddCandidateRequest([Required, MaxLength(200)] string Name, [MaxLength(100)] string? ExternalReference, long PositionId, long AreaId, [MaxLength(120)] string? NominationReference);
public sealed record AddElectionCenterRequest(long AreaId, [Required, MaxLength(50)] string Code, [Required, MaxLength(250)] string Name, [MaxLength(500)] string? Address);
