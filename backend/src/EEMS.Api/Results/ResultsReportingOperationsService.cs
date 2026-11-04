using System.Text.Json;
using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Reporting.Domain;
using EEMS.Modules.Reporting.Infrastructure;
using EEMS.Modules.Results.Domain;
using EEMS.Modules.Results.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Results;

public sealed class ResultsReportingOperationsService(ResultsDbContext resultsDb, ReportingDbContext reportingDb, ElectionsDbContext electionsDb, CandidatesDbContext candidatesDb, PollingDbContext pollingDb, ITenantContext tenantContext)
{
    public async Task<ResultLookups> GetLookupsAsync(Guid electionId, CancellationToken token)
    {
        var electionTypeId = await electionsDb.Elections.Where(x => x.TenantId == tenantContext.TenantId && x.Id == electionId).Select(x => (short?)x.ElectionTypeId).SingleOrDefaultAsync(token);
        var centers = await (from link in pollingDb.ElectionCenters join center in pollingDb.Centers on link.CenterId equals center.Id where link.TenantId == tenantContext.TenantId && link.ElectionId == electionId orderby center.Name select new ResultCenterReference(link.Id, center.Code, center.Name)).ToListAsync(token);
        var candidates = await (from assignment in candidatesDb.CandidateElections join candidate in candidatesDb.Candidates on assignment.CandidateId equals candidate.Id where assignment.TenantId == tenantContext.TenantId && assignment.ElectionId == electionId && assignment.IsActive orderby candidate.Name select new ResultCandidateReference(assignment.Id, assignment.PositionId, candidate.Name)).ToListAsync(token);
        return new(
            await resultsDb.States.Where(x => x.IsActive).OrderBy(x => x.Id).Select(x => new ResultStateReference(x.Id, x.Code, x.Name, x.IsVerified)).ToListAsync(token),
            electionTypeId is null ? [] : await electionsDb.Positions.Where(x => x.ElectionTypeId == electionTypeId && x.IsActive).OrderBy(x => x.Name).Select(x => new ResultPositionReference(x.Id, x.Code, x.Name)).ToListAsync(token),
            centers, candidates,
            await reportingDb.ExportStates.Where(x => x.IsActive).OrderBy(x => x.Id).Select(x => new ExportStateReference(x.Id, x.Code, x.Name, x.IsTerminal)).ToListAsync(token));
    }

    public async Task<IReadOnlyList<ResultSubmissionSummary>> GetSubmissionsAsync(Guid electionId, CancellationToken token)
    {
        var submissions = await resultsDb.Submissions.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId).OrderByDescending(x => x.CreatedAtUtc).ToListAsync(token);
        var ids = submissions.Select(x => x.Id).ToArray();
        var details = await resultsDb.Details.Where(x => x.TenantId == tenantContext.TenantId && ids.Contains(x.SubmissionId)).ToListAsync(token);
        var verifications = await resultsDb.Verifications.Where(x => x.TenantId == tenantContext.TenantId && ids.Contains(x.SubmissionId)).OrderByDescending(x => x.VerifiedAtUtc).ToListAsync(token);
        return submissions.Select(x => ToSummary(x, details.Where(d => d.SubmissionId == x.Id), verifications.FirstOrDefault(v => v.SubmissionId == x.Id))).ToArray();
    }

    public async Task<ResultSubmissionSummary?> SubmitAsync(Guid electionId, Guid userId, CreateResultSubmissionCommand command, CancellationToken token)
    {
        var existing = await resultsDb.Submissions.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.IdempotencyKey == command.IdempotencyKey, token);
        if (existing is not null) return (await GetSubmissionsAsync(electionId, token)).FirstOrDefault(x => x.SubmissionId == existing.Id);
        var firstState = await resultsDb.States.Where(x => x.IsActive).OrderBy(x => x.Id).FirstOrDefaultAsync(token);
        var validCenter = await pollingDb.ElectionCenters.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == command.ElectionCenterId, token);
        var validPosition = await electionsDb.Positions.AnyAsync(x => x.Id == command.PositionId && x.IsActive, token);
        var candidateIds = command.Details.Select(x => x.CandidateElectionId).Distinct().ToArray();
        var validCandidates = await candidatesDb.CandidateElections.CountAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.PositionId == command.PositionId && candidateIds.Contains(x.Id) && x.IsActive, token) == candidateIds.Length;
        if (firstState is null || !validCenter || !validPosition || command.Details.Count == 0 || candidateIds.Length != command.Details.Count || !validCandidates || command.Details.Any(x => x.Votes < 0) || command.Details.Sum(x => x.Votes) != command.DeclaredTotalVotes) return null;
        var submission = ResultSubmission.Create(tenantContext.TenantId, electionId, command.ElectionCenterId, command.PositionId, userId, firstState.Id, command.IdempotencyKey, command.DeclaredTotalVotes);
        var details = command.Details.Select(x => ResultDetail.Create(tenantContext.TenantId, submission.Id, x.CandidateElectionId, x.Votes)).ToArray();
        resultsDb.Submissions.Add(submission); resultsDb.Details.AddRange(details); await resultsDb.SaveChangesAsync(token);
        reportingDb.AuditLogs.Add(AuditLog.Record(tenantContext.TenantId, userId, "result.submitted", "ResultSubmission", submission.Id.ToString(), command.IdempotencyKey, JsonSerializer.Serialize(new { electionId, command.ElectionCenterId, command.PositionId, command.DeclaredTotalVotes })));
        await reportingDb.SaveChangesAsync(token);
        return ToSummary(submission, details, null);
    }

    public async Task<ResultSubmissionSummary?> VerifyAsync(Guid electionId, Guid submissionId, Guid verifierId, VerifyResultCommand command, CancellationToken token)
    {
        var submission = await resultsDb.Submissions.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == submissionId, token);
        var state = await resultsDb.States.SingleOrDefaultAsync(x => x.Id == command.ResultingStateId && x.IsActive, token);
        if (submission is null || state is null || submission.Version != command.ExpectedVersion || submission.SubmittedByUserId == verifierId) return null;
        var verification = ResultVerification.Record(tenantContext.TenantId, submission.Id, submission.SubmittedByUserId, verifierId, state.Id, command.Note);
        resultsDb.Verifications.Add(verification); submission.MoveTo(state.Id); await resultsDb.SaveChangesAsync(token);
        reportingDb.AuditLogs.Add(AuditLog.Record(tenantContext.TenantId, verifierId, "result.verified", "ResultSubmission", submission.Id.ToString(), Guid.NewGuid().ToString("N"), JsonSerializer.Serialize(new { state.Code, command.Note })));
        await reportingDb.SaveChangesAsync(token);
        var details = await resultsDb.Details.Where(x => x.TenantId == tenantContext.TenantId && x.SubmissionId == submission.Id).ToListAsync(token);
        return ToSummary(submission, details, verification);
    }

    public async Task<IReadOnlyList<ExportSummary>> GetExportsAsync(Guid electionId, CancellationToken token) => await reportingDb.ExportLogs.Where(x => x.TenantId == tenantContext.TenantId && x.FiltersJson.Contains(electionId.ToString())).OrderByDescending(x => x.RequestedAtUtc).Select(x => new ExportSummary(x.Id, x.StateId, x.ReportType, x.Format, x.RequestedAtUtc, x.CompletedAtUtc, x.StorageKey)).ToListAsync(token);

    public async Task<ExportSummary?> RequestExportAsync(Guid electionId, Guid userId, RequestExportCommand command, CancellationToken token)
    {
        var state = await reportingDb.ExportStates.Where(x => x.IsActive).OrderBy(x => x.Id).FirstOrDefaultAsync(token); if (state is null) return null;
        var correlation = Guid.NewGuid().ToString("N"); var filters = JsonSerializer.Serialize(new { electionId });
        var export = ExportLog.Request(tenantContext.TenantId, userId, state.Id, command.ReportType, command.Format, filters, correlation); reportingDb.ExportLogs.Add(export);
        reportingDb.AuditLogs.Add(AuditLog.Record(tenantContext.TenantId, userId, "report.export_requested", "ExportLog", export.Id.ToString(), correlation, filters)); await reportingDb.SaveChangesAsync(token);
        return new(export.Id, export.StateId, export.ReportType, export.Format, export.RequestedAtUtc, null, null);
    }

    private static ResultSubmissionSummary ToSummary(ResultSubmission submission, IEnumerable<ResultDetail> details, ResultVerification? verification) => new(submission.Id, submission.ElectionCenterId, submission.PositionId, submission.SubmittedByUserId, submission.StateId, submission.IdempotencyKey, submission.DeclaredTotalVotes, submission.CreatedAtUtc, submission.Version, details.Select(x => new ResultDetailSummary(x.CandidateElectionId, x.Votes)).ToArray(), verification is null ? null : new ResultVerificationSummary(verification.VerifierUserId, verification.ResultingStateId, verification.Note, verification.VerifiedAtUtc));
}

public sealed record ResultLookups(IReadOnlyList<ResultStateReference> States, IReadOnlyList<ResultPositionReference> Positions, IReadOnlyList<ResultCenterReference> Centers, IReadOnlyList<ResultCandidateReference> Candidates, IReadOnlyList<ExportStateReference> ExportStates);
public sealed record ResultStateReference(short Id,string Code,string Name,bool IsVerified); public sealed record ResultPositionReference(long Id,string Code,string Name); public sealed record ResultCenterReference(Guid ElectionCenterId,string Code,string Name); public sealed record ResultCandidateReference(Guid CandidateElectionId,long PositionId,string Name); public sealed record ExportStateReference(short Id,string Code,string Name,bool IsTerminal);
public sealed record ResultDetailSummary(Guid CandidateElectionId,int Votes); public sealed record ResultVerificationSummary(Guid VerifierUserId,short ResultingStateId,string Note,DateTimeOffset VerifiedAtUtc);
public sealed record ResultSubmissionSummary(Guid SubmissionId,Guid ElectionCenterId,long PositionId,Guid SubmittedByUserId,short StateId,string IdempotencyKey,int DeclaredTotalVotes,DateTimeOffset CreatedAtUtc,int Version,IReadOnlyList<ResultDetailSummary> Details,ResultVerificationSummary? Verification);
public sealed record CreateResultDetailCommand(Guid CandidateElectionId,int Votes); public sealed record CreateResultSubmissionCommand(Guid ElectionCenterId,long PositionId,string IdempotencyKey,int DeclaredTotalVotes,IReadOnlyList<CreateResultDetailCommand> Details); public sealed record VerifyResultCommand(short ResultingStateId,int ExpectedVersion,string Note);
public sealed record ExportSummary(Guid ExportId,short StateId,string ReportType,string Format,DateTimeOffset RequestedAtUtc,DateTimeOffset? CompletedAtUtc,string? StorageKey); public sealed record RequestExportCommand(string ReportType,string Format);
