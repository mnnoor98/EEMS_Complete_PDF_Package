using EEMS.Modules.Candidates.Domain;
using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Elections.Domain;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Elections;

public sealed class ElectionOperationsService(
    ElectionsDbContext electionsDb,
    CandidatesDbContext candidatesDb,
    PollingDbContext pollingDb,
    GeographyDbContext geographyDb,
    ITenantContext tenantContext)
{
    public async Task<ElectionLookups> GetLookupsAsync(CancellationToken token) => new(
        await electionsDb.ElectionTypes.Where(x => x.IsActive).OrderBy(x => x.Name).Select(x => new ReferenceItem<short>(x.Id, x.Code, x.Name)).ToListAsync(token),
        await electionsDb.LifecycleStates.Where(x => x.IsActive).OrderBy(x => x.Id).Select(x => new LifecycleReference(x.Id, x.Code, x.Name, x.IsTerminal)).ToListAsync(token),
        await electionsDb.Positions.Where(x => x.IsActive).OrderBy(x => x.Name).Select(x => new PositionReference(x.Id, x.ElectionTypeId, x.Code, x.Name)).ToListAsync(token),
        await geographyDb.Areas.Where(x => x.IsActive).OrderBy(x => x.NameBn).Select(x => new AreaReference(x.Id, x.ParentAreaId, x.AreaTypeId, x.Code, x.NameBn, x.NameEn)).ToListAsync(token));

    public async Task<IReadOnlyList<ElectionSummary>> GetElectionsAsync(CancellationToken token) =>
        await electionsDb.Elections.Where(x => x.TenantId == tenantContext.TenantId).OrderByDescending(x => x.ElectionDate)
            .Select(x => new ElectionSummary(x.Id, x.Name, x.ElectionTypeId, x.AreaId, x.LifecycleStateId, x.ElectionDate, x.Version)).ToListAsync(token);

    public async Task<ElectionSummary?> CreateElectionAsync(CreateElectionCommand command, CancellationToken token)
    {
        var valid = await electionsDb.ElectionTypes.AnyAsync(x => x.Id == command.ElectionTypeId && x.IsActive, token) &&
                    await electionsDb.LifecycleStates.AnyAsync(x => x.Id == command.LifecycleStateId && x.IsActive, token) &&
                    await geographyDb.Areas.AnyAsync(x => x.Id == command.AreaId && x.IsActive, token);
        if (!valid) return null;
        var election = Election.Create(tenantContext.TenantId, command.ElectionTypeId, command.AreaId, command.LifecycleStateId, command.Name, command.ElectionDate);
        electionsDb.Elections.Add(election);
        await electionsDb.SaveChangesAsync(token);
        return new ElectionSummary(election.Id, election.Name, election.ElectionTypeId, election.AreaId, election.LifecycleStateId, election.ElectionDate, election.Version);
    }

    public async Task<bool> MoveElectionAsync(Guid electionId, short stateId, int expectedVersion, CancellationToken token)
    {
        var stateExists = await electionsDb.LifecycleStates.AnyAsync(x => x.Id == stateId && x.IsActive, token);
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token);
        if (!stateExists || election is null || election.Version != expectedVersion) return false;
        election.MoveTo(stateId);
        await electionsDb.SaveChangesAsync(token);
        return true;
    }

    public async Task<ElectionUpdateResult> UpdateElectionAsync(Guid electionId, UpdateElectionCommand command, CancellationToken token)
    {
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token);
        if (election is null) return new(ElectionUpdateStatus.NotFound, null);
        if (election.Version != command.ExpectedVersion) return new(ElectionUpdateStatus.VersionConflict, null);
        var valid = await electionsDb.ElectionTypes.AnyAsync(x => x.Id == command.ElectionTypeId && x.IsActive, token) &&
                    await geographyDb.Areas.AnyAsync(x => x.Id == command.AreaId && x.IsActive, token);
        if (!valid) return new(ElectionUpdateStatus.InvalidReference, null);
        election.UpdateDetails(command.ElectionTypeId, command.AreaId, command.Name, command.ElectionDate);
        await electionsDb.SaveChangesAsync(token);
        return new(ElectionUpdateStatus.Updated, new ElectionSummary(election.Id, election.Name, election.ElectionTypeId, election.AreaId, election.LifecycleStateId, election.ElectionDate, election.Version));
    }

    public async Task<IReadOnlyList<CandidateSummary>> GetCandidatesAsync(Guid electionId, CancellationToken token) =>
        await (from assignment in candidatesDb.CandidateElections
               join candidate in candidatesDb.Candidates on assignment.CandidateId equals candidate.Id
               where assignment.TenantId == tenantContext.TenantId && assignment.ElectionId == electionId
               orderby candidate.Name
               select new CandidateSummary(candidate.Id, assignment.Id, candidate.Name, candidate.ExternalReference, assignment.PositionId, assignment.AreaId, assignment.NominationReference, assignment.IsActive)).ToListAsync(token);

    public async Task<CandidateSummary?> AddCandidateAsync(Guid electionId, AddCandidateCommand command, CancellationToken token)
    {
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token);
        var positionExists = election is not null && await electionsDb.Positions.AnyAsync(x => x.Id == command.PositionId && x.ElectionTypeId == election.ElectionTypeId && x.IsActive, token);
        var areaExists = await geographyDb.Areas.AnyAsync(x => x.Id == command.AreaId && x.IsActive, token);
        if (election is null || !positionExists || !areaExists) return null;
        var candidate = Candidate.Create(tenantContext.TenantId, command.Name, command.ExternalReference);
        candidatesDb.Candidates.Add(candidate);
        await candidatesDb.SaveChangesAsync(token);
        var assignment = CandidateElection.Create(tenantContext.TenantId, electionId, candidate.Id, command.PositionId, command.AreaId, command.NominationReference);
        candidatesDb.CandidateElections.Add(assignment);
        await candidatesDb.SaveChangesAsync(token);
        return new CandidateSummary(candidate.Id, assignment.Id, candidate.Name, candidate.ExternalReference, assignment.PositionId, assignment.AreaId, assignment.NominationReference, true);
    }

    public async Task<IReadOnlyList<ElectionCenterSummary>> GetElectionCentersAsync(Guid electionId, CancellationToken token) =>
        await (from link in pollingDb.ElectionCenters
               join center in pollingDb.Centers on link.CenterId equals center.Id
               where link.TenantId == tenantContext.TenantId && link.ElectionId == electionId
               orderby center.Name
               select new ElectionCenterSummary(link.Id, center.Id, center.AreaId, center.Code, center.Name, center.Address, link.IsVerified)).ToListAsync(token);

    public async Task<ElectionCenterSummary?> AddElectionCenterAsync(Guid electionId, AddElectionCenterCommand command, CancellationToken token)
    {
        var valid = await electionsDb.Elections.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token) &&
                    await geographyDb.Areas.AnyAsync(x => x.Id == command.AreaId && x.IsActive, token);
        if (!valid) return null;
        var code = command.Code.Trim().ToUpperInvariant();
        var center = await pollingDb.Centers.SingleOrDefaultAsync(x => x.AreaId == command.AreaId && x.Code == code, token);
        if (center is null)
        {
            center = PollingCenter.Create(command.AreaId, code, command.Name, command.Address);
            pollingDb.Centers.Add(center);
            await pollingDb.SaveChangesAsync(token);
        }
        if (await pollingDb.ElectionCenters.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.CenterId == center.Id, token)) return null;
        var link = ElectionCenter.Create(tenantContext.TenantId, electionId, center.Id);
        pollingDb.ElectionCenters.Add(link);
        await pollingDb.SaveChangesAsync(token);
        return new ElectionCenterSummary(link.Id, center.Id, center.AreaId, center.Code, center.Name, center.Address, false);
    }

    public async Task<bool> VerifyElectionCenterAsync(Guid electionId, Guid electionCenterId, CancellationToken token)
    {
        var center = await pollingDb.ElectionCenters.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == electionCenterId, token);
        if (center is null) return false;
        center.Verify();
        await pollingDb.SaveChangesAsync(token);
        return true;
    }
}

public sealed record ReferenceItem<T>(T Id, string Code, string Name);
public sealed record LifecycleReference(short Id, string Code, string Name, bool IsTerminal);
public sealed record PositionReference(long Id, short ElectionTypeId, string Code, string Name);
public sealed record AreaReference(long Id, long? ParentAreaId, short AreaTypeId, string Code, string NameBn, string? NameEn);
public sealed record ElectionLookups(IReadOnlyList<ReferenceItem<short>> ElectionTypes, IReadOnlyList<LifecycleReference> LifecycleStates, IReadOnlyList<PositionReference> Positions, IReadOnlyList<AreaReference> Areas);
public sealed record ElectionSummary(Guid ElectionId, string Name, short ElectionTypeId, long AreaId, short LifecycleStateId, DateOnly ElectionDate, int Version);
public sealed record CreateElectionCommand(short ElectionTypeId, long AreaId, short LifecycleStateId, string Name, DateOnly ElectionDate);
public sealed record UpdateElectionCommand(short ElectionTypeId, long AreaId, string Name, DateOnly ElectionDate, int ExpectedVersion);
public enum ElectionUpdateStatus { Updated, NotFound, InvalidReference, VersionConflict }
public sealed record ElectionUpdateResult(ElectionUpdateStatus Status, ElectionSummary? Election);
public sealed record AddCandidateCommand(string Name, string? ExternalReference, long PositionId, long AreaId, string? NominationReference);
public sealed record CandidateSummary(Guid CandidateId, Guid AssignmentId, string Name, string? ExternalReference, long PositionId, long AreaId, string? NominationReference, bool IsActive);
public sealed record AddElectionCenterCommand(long AreaId, string Code, string Name, string? Address);
public sealed record ElectionCenterSummary(Guid ElectionCenterId, Guid CenterId, long AreaId, string Code, string Name, string? Address, bool IsVerified);
