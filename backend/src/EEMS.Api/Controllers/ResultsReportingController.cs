using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using EEMS.Api.Authorization;
using EEMS.Api.Results;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController,Authorize,Route("api/v1/elections/{electionId:guid}/results")]
public sealed class ResultsReportingController(ResultsReportingOperationsService operations):ControllerBase
{
    [HttpGet("lookups"),Authorize(Policy=PermissionCodes.ResultsRead)] public async Task<ActionResult<ResultLookups>> GetLookups(Guid electionId,CancellationToken token)=>Ok(await operations.GetLookupsAsync(electionId,token));
    [HttpGet,Authorize(Policy=PermissionCodes.ResultsRead)] public async Task<ActionResult<IReadOnlyList<ResultSubmissionSummary>>> GetSubmissions(Guid electionId,CancellationToken token)=>Ok(await operations.GetSubmissionsAsync(electionId,token));
    [HttpPost,Authorize(Policy=PermissionCodes.ResultsManage)] public async Task<ActionResult<ResultSubmissionSummary>> Submit(Guid electionId,CreateResultSubmissionRequest request,CancellationToken token){if(!TryUserId(out var userId))return Unauthorized();var item=await operations.SubmitAsync(electionId,userId,new(request.ElectionCenterId,request.PositionId,request.IdempotencyKey,request.DeclaredTotalVotes,request.Details.Select(x=>new CreateResultDetailCommand(x.CandidateElectionId,x.Votes)).ToArray()),token);return item is null?BadRequest(new{error="invalid_result_submission"}):Ok(item);}
    [HttpPost("{submissionId:guid}/verify"),Authorize(Policy=PermissionCodes.ResultsManage)] public async Task<ActionResult<ResultSubmissionSummary>> Verify(Guid electionId,Guid submissionId,VerifyResultRequest request,CancellationToken token){if(!TryUserId(out var userId))return Unauthorized();var item=await operations.VerifyAsync(electionId,submissionId,userId,new(request.ResultingStateId,request.ExpectedVersion,request.Note),token);return item is null?Conflict(new{error="invalid_verification_or_version"}):Ok(item);}
    [HttpGet("exports"),Authorize(Policy=PermissionCodes.ReportingRead)] public async Task<ActionResult<IReadOnlyList<ExportSummary>>> GetExports(Guid electionId,CancellationToken token)=>Ok(await operations.GetExportsAsync(electionId,token));
    [HttpPost("exports"),Authorize(Policy=PermissionCodes.ReportingManage)] public async Task<ActionResult<ExportSummary>> RequestExport(Guid electionId,RequestExportRequest request,CancellationToken token){if(!TryUserId(out var userId))return Unauthorized();var item=await operations.RequestExportAsync(electionId,userId,new(request.ReportType,request.Format),token);return item is null?BadRequest():Ok(item);}
    private bool TryUserId(out Guid userId)=>Guid.TryParse(User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value,out userId);
}
public sealed record CreateResultDetailRequest(Guid CandidateElectionId,int Votes); public sealed record CreateResultSubmissionRequest(Guid ElectionCenterId,long PositionId,[Required,MaxLength(100)]string IdempotencyKey,int DeclaredTotalVotes,[MinLength(1)]IReadOnlyList<CreateResultDetailRequest> Details); public sealed record VerifyResultRequest(short ResultingStateId,int ExpectedVersion,[Required,MaxLength(2000)]string Note); public sealed record RequestExportRequest([Required,MaxLength(100)]string ReportType,[Required,MaxLength(20)]string Format);
