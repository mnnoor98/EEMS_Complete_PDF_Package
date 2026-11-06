using System.Globalization;
using System.Text.Json;
using EEMS.Modules.Identity.Security;
using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using EEMS.Api.Authorization;
using EEMS.Modules.Candidates.Domain;
using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Events.Infrastructure;
using EEMS.Modules.Finance.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Results.Domain;
using EEMS.Modules.Results.Infrastructure;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/candidate")]
public sealed class CandidatePortalController(
    CandidatesDbContext candidatesDb,
    ElectionsDbContext electionsDb,
    GeographyDbContext geographyDb,
    PollingDbContext pollingDb,
    TeamsDbContext teamsDb,
    FinanceDbContext financeDb,
    EventsDbContext eventsDb,
    ResultsDbContext resultsDb,
    IdentityDbContext identityDb,
    ITenantContext tenantContext,
    Microsoft.AspNetCore.Identity.IPasswordHasher<EEMS.Modules.Identity.Domain.User> passwordHasher) : ControllerBase
{

    private static readonly JsonSerializerOptions CamelCaseJsonOptions = new(JsonSerializerDefaults.Web);

    private (Guid? CandidateId, bool IsSuperAdmin) GetUserCandidateScope()
    {
        var isSuperAdminClaim = User.FindFirst("is_super_admin")?.Value;
        bool isSuperAdmin = string.Equals(isSuperAdminClaim, "true", StringComparison.OrdinalIgnoreCase);

        var candClaim = User.FindFirst(IdentityClaimTypes.CandidateId)?.Value;
        if (Guid.TryParse(candClaim, out var cid))
        {
            return (cid, isSuperAdmin);
        }

        return (null, isSuperAdmin);
    }
    // =========================================================================
    // 1. SYMBOLS & CAMPAIGN PROFILE
    // =========================================================================

    [HttpGet("symbols")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<ElectionSymbolSummary>>> GetSymbols(CancellationToken token)
    {
        var items = await candidatesDb.Symbols
            .Where(s => s.IsActive)
            .OrderBy(s => s.Id)
            .Select(s => new ElectionSymbolSummary(s.Id, s.Code, s.NameBn, s.NameEn, s.Category, s.IconEmoji))
            .ToListAsync(token);
        return Ok(items);
    }

    [HttpGet("elections/{electionId:guid}/war-room")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<CandidateWarRoomSummary>> GetWarRoom(
        Guid electionId,
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == electionId, token);
        if (election is null) return NotFound(new { error = "election_not_found" });

        var area = await geographyDb.Areas.SingleOrDefaultAsync(x => x.Id == election.AreaId, token);
        var areaName = area != null ? (area.NameEn ?? area.NameBn) : $"Area {election.AreaId}";

        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = candidateId ?? userCandidateId;

        // Get candidate assignment
        CandidateElection? assignment = null;
        if (targetCandidateId.HasValue)
        {
            assignment = await candidatesDb.CandidateElections
                .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == targetCandidateId.Value && x.IsActive, token);
        }

        if (assignment is null)
        {
            assignment = await candidatesDb.CandidateElections
                .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive, token);
        }

        CandidateWarRoomHero? candidateData = null;
        if (assignment is not null)
        {
            var candidate = await candidatesDb.Candidates
                .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.Id == assignment.CandidateId, token);

            var position = await electionsDb.Positions
                .FirstOrDefaultAsync(x => x.Id == assignment.PositionId, token);

            var symId = assignment.SymbolId ?? candidate?.SymbolId;
            var symbol = symId.HasValue
                ? await candidatesDb.Symbols.FirstOrDefaultAsync(x => x.Id == symId.Value, token)
                : null;

            if (candidate is not null)
            {
                candidateData = new CandidateWarRoomHero(
                    candidate.Id,
                    assignment.Id,
                    candidate.Name,
                    position?.Name ?? "Contesting Candidate",
                    symId,
                    symbol?.NameBn,
                    symbol?.NameEn,
                    symbol?.IconEmoji ?? "🗳️",
                    assignment.PartyName ?? candidate.PartyNameBn ?? "স্বতন্ত্র (Independent)",
                    assignment.Slogan ?? candidate.Slogan ?? "উন্নয়ন ও জনকল্যাণের অঙ্গীকার",
                    candidate.Phone,
                    candidate.CampaignOffice);
            }
        }

        // Polling center stats
        var totalCenters = await pollingDb.ElectionCenters.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId, token);
        var verifiedCenters = await pollingDb.ElectionCenters.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsVerified, token);
        
        var electionCenterIds = await pollingDb.ElectionCenters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
            .Select(x => x.CenterId)
            .ToListAsync(token);

        var totalBooths = await pollingDb.Booths.CountAsync(b => electionCenterIds.Contains(b.CenterId) && b.IsActive, token);

        // Dedicated booth agents count
        var assignedAgents = await pollingDb.BoothAgents
            .CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.Status != "ABSENT", token);

        if (assignedAgents == 0)
        {
            // Fallback to general agent assignments if none in booth_agents
            assignedAgents = await (
                from link in pollingDb.ElectionCenters
                join agent in pollingDb.AgentAssignments on link.Id equals agent.ElectionCenterId
                where link.TenantId == tenantId && link.ElectionId == electionId && agent.IsActive
                select agent.Id
            ).CountAsync(token);
        }

        // Workforce stats
        var totalTeams = await teamsDb.Teams.CountAsync(x => x.TenantId == tenantId && x.IsActive, token);
        var totalFieldMembers = await teamsDb.FieldMembers.CountAsync(x => x.TenantId == tenantId && x.IsActive, token);
        var openTasks = await teamsDb.Tasks.CountAsync(x => x.TenantId == tenantId, token);

        // Campaign Events stats
        var totalEvents = await eventsDb.Events.CountAsync(x => x.TenantId == tenantId, token);

        // Finance / EC Ceiling stats
        var totalCommittedExpenses = await financeDb.Expenses
            .Where(x => x.TenantId == tenantId)
            .SumAsync(x => (decimal?)x.Amount, token) ?? 0m;

        const decimal ecCeiling = 2500000.00m; // 25 Lakh BDT (EC standard)

        return Ok(new CandidateWarRoomSummary(
            election.Id,
            election.Name,
            election.ElectionDate,
            areaName,
            candidateData,
            totalCenters,
            verifiedCenters,
            totalBooths,
            assignedAgents,
            totalTeams,
            totalFieldMembers,
            openTasks,
            totalEvents,
            ecCeiling,
            totalCommittedExpenses,
            Math.Max(0m, ecCeiling - totalCommittedExpenses)));
    }

    [HttpPut("elections/{electionId:guid}/candidates/{candidateId:guid}/campaign")]
    [Authorize(Policy = PermissionCodes.ElectionsManage)]
    public async Task<IActionResult> UpdateCampaignDetails(
        Guid electionId,
        Guid candidateId,
        UpdateCampaignDetailsRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var candidate = await candidatesDb.Candidates.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.Id == candidateId, token);
        if (candidate is null) return NotFound(new { error = "candidate_not_found" });

        var assignment = await candidatesDb.CandidateElections.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == candidateId, token);
        if (assignment is null) return NotFound(new { error = "candidate_assignment_not_found" });

        candidate.UpdateProfile(
            candidate.Name,
            request.SymbolId,
            request.PartyName,
            request.PartyName,
            request.Slogan,
            request.Phone,
            candidate.PhotoUrl,
            request.CampaignOffice);

        assignment.UpdateCampaignDetails(request.SymbolId, request.PartyName, request.Slogan);

        await candidatesDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 2. POLLING BOOTH AGENTS & FORM-9
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/booth-agents")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBoothAgentSummary>>> GetBoothAgents(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] string? status,
        [FromQuery] string? agentType,
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = candidateId ?? userCandidateId;

        var query = from agent in pollingDb.BoothAgents
                    join center in pollingDb.Centers on agent.CenterId equals center.Id
                    join booth in pollingDb.Booths on agent.BoothId equals booth.Id
                    where agent.TenantId == tenantId && agent.ElectionId == electionId
                    select new { agent, center, booth };

        if (targetCandidateId.HasValue)
        {
            query = query.Where(x => x.agent.CandidateId == targetCandidateId.Value);
        }

        if (centerId.HasValue) query = query.Where(x => x.agent.CenterId == centerId.Value);
        if (!string.IsNullOrWhiteSpace(status))
        {
            var normStatus = status.Trim().ToUpperInvariant();
            query = query.Where(x => x.agent.Status == normStatus);
        }
        if (!string.IsNullOrWhiteSpace(agentType))
        {
            var normType = agentType.Trim().ToUpperInvariant();
            query = query.Where(x => x.agent.AgentType == normType);
        }

        var agentRows = await query
            .OrderBy(x => x.center.Name)
            .ThenBy(x => x.booth.Code)
            .ThenBy(x => x.agent.AgentType)
            .ToListAsync(token);

        var candidateIds = agentRows.Select(x => x.agent.CandidateId).Distinct().ToList();
        var candidates = await candidatesDb.Candidates
            .Where(c => c.TenantId == tenantId && candidateIds.Contains(c.Id))
            .ToDictionaryAsync(c => c.Id, c => c.Name, token);

        var list = agentRows.Select(x => new CandidateBoothAgentSummary(
            x.agent.Id,
            x.agent.CenterId,
            x.center.Name,
            x.center.Code,
            x.agent.BoothId,
            x.booth.Code,
            x.booth.Name,
            x.agent.CandidateId,
            candidates.GetValueOrDefault(x.agent.CandidateId, "Candidate"),
            x.agent.AgentType,
            x.agent.FullName,
            x.agent.NidNumber,
            x.agent.Phone,
            x.agent.VoterNumber,
            x.agent.PhotoUrl,
            x.agent.AppointmentLetterIssued,
            x.agent.CheckedInAtBooth,
            x.agent.Status,
            x.agent.Notes,
            x.agent.CreatedAtUtc)).ToList();

        return Ok(list);
    }

    [HttpPost("elections/{electionId:guid}/booth-agents")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<CandidateBoothAgentSummary>> CreateBoothAgent(
        Guid electionId,
        CreateBoothAgentRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;

        var centerExists = await pollingDb.ElectionCenters.AnyAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.CenterId == request.CenterId, token);
        if (!centerExists) return BadRequest(new { error = "invalid_election_center" });

        var booth = await pollingDb.Booths.SingleOrDefaultAsync(
            x => x.CenterId == request.CenterId && x.Id == request.BoothId && x.IsActive, token);
        if (booth is null) return BadRequest(new { error = "invalid_booth" });

        var candidate = await candidatesDb.Candidates.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.Id == request.CandidateId, token);
        if (candidate is null) return BadRequest(new { error = "invalid_candidate" });

        var agentType = string.Equals(request.AgentType, "RESERVE", StringComparison.OrdinalIgnoreCase) ? "RESERVE" : "PRIMARY";

        var agent = BoothAgent.Create(
            tenantId,
            electionId,
            request.CenterId,
            request.BoothId,
            request.CandidateId,
            agentType,
            request.FullName.Trim(),
            request.NidNumber.Trim(),
            request.Phone.Trim(),
            request.VoterNumber?.Trim(),
            request.Notes?.Trim());

        pollingDb.BoothAgents.Add(agent);
        await pollingDb.SaveChangesAsync(token);

        var center = await pollingDb.Centers.SingleAsync(x => x.Id == request.CenterId, token);

        return Ok(new CandidateBoothAgentSummary(
            agent.Id,
            agent.CenterId,
            center.Name,
            center.Code,
            agent.BoothId,
            booth.Code,
            booth.Name,
            agent.CandidateId,
            candidate.Name,
            agent.AgentType,
            agent.FullName,
            agent.NidNumber,
            agent.Phone,
            agent.VoterNumber,
            agent.PhotoUrl,
            agent.AppointmentLetterIssued,
            agent.CheckedInAtBooth,
            agent.Status,
            agent.Notes,
            agent.CreatedAtUtc));
    }

    [HttpPut("elections/{electionId:guid}/booth-agents/{agentId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> UpdateBoothAgent(
        Guid electionId,
        Guid agentId,
        UpdateBoothAgentRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var agent = await pollingDb.BoothAgents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == agentId, token);
        if (agent is null) return NotFound(new { error = "agent_not_found" });

        agent.UpdateDetails(
            request.FullName.Trim(),
            request.NidNumber.Trim(),
            request.Phone.Trim(),
            request.VoterNumber?.Trim(),
            string.Equals(request.AgentType, "RESERVE", StringComparison.OrdinalIgnoreCase) ? "RESERVE" : "PRIMARY",
            request.Notes?.Trim());

        agent.UpdateStatus(request.Status.Trim().ToUpperInvariant(), request.AppointmentLetterIssued);

        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/booth-agents/{agentId:guid}/issue-letter")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> IssueAppointmentLetter(
        Guid electionId,
        Guid agentId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var agent = await pollingDb.BoothAgents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == agentId, token);
        if (agent is null) return NotFound(new { error = "agent_not_found" });

        agent.UpdateStatus(agent.Status, true);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpDelete("elections/{electionId:guid}/booth-agents/{agentId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> DeleteBoothAgent(
        Guid electionId,
        Guid agentId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var agent = await pollingDb.BoothAgents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == agentId, token);
        if (agent is null) return NotFound(new { error = "agent_not_found" });

        pollingDb.BoothAgents.Remove(agent);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 3. LIVE RESULTS TALLY & LEAD MARGIN
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/results-summary")]
    [Authorize(Policy = PermissionCodes.ResultsRead)]
    public async Task<ActionResult<CandidateElectionResultsSummary>> GetResultsSummary(
        Guid electionId,
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = candidateId ?? userCandidateId;

        // Get our candidate and opponent candidates
        var candidates = await (
            from ce in candidatesDb.CandidateElections
            join c in candidatesDb.Candidates on ce.CandidateId equals c.Id
            join sym in candidatesDb.Symbols on ce.SymbolId ?? c.SymbolId equals (int?)sym.Id into symG
            from s in symG.DefaultIfEmpty()
            where ce.TenantId == tenantId && ce.ElectionId == electionId && ce.IsActive
            select new
            {
                CandidateElectionId = ce.Id,
                CandidateId = c.Id,
                Name = c.Name,
                PartyName = ce.PartyName ?? c.PartyNameBn ?? c.PartyNameEn ?? "স্বতন্ত্র",
                SymbolName = s != null ? s.NameBn : "প্রতীক",
                SymbolEmoji = s != null ? s.IconEmoji : "🗳️"
            }
        ).ToListAsync(token);

        if (candidates.Count == 0) return NotFound(new { error = "no_candidates_for_election" });

        var primaryCandidate = (targetCandidateId.HasValue 
            ? candidates.FirstOrDefault(c => c.CandidateId == targetCandidateId.Value) 
            : null) ?? candidates[0];

        var runnerUpCandidate = candidates.FirstOrDefault(c => c.CandidateElectionId != primaryCandidate.CandidateElectionId);

        // Fetch centers for this election
        var centers = await (
            from link in pollingDb.ElectionCenters
            join c in pollingDb.Centers on link.CenterId equals c.Id
            where link.TenantId == tenantId && link.ElectionId == electionId
            select new { link.Id, link.CenterId, c.Code, c.Name }
        ).ToListAsync(token);

        // Fetch result submissions
        var submissions = await resultsDb.Submissions
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
            .ToListAsync(token);

        var submissionIds = submissions.Select(s => s.Id).ToList();

        var details = await resultsDb.Details
            .Where(d => d.TenantId == tenantId && submissionIds.Contains(d.SubmissionId))
            .ToListAsync(token);

        var verifications = await resultsDb.Verifications
            .Where(v => v.TenantId == tenantId && submissionIds.Contains(v.SubmissionId))
            .ToListAsync(token);

        var centerResults = new List<CandidateCenterResultItem>();
        int totalCandidateVotes = 0;
        int totalRunnerUpVotes = 0;
        int countedCount = 0;

        foreach (var c in centers)
        {
            var sub = submissions.FirstOrDefault(s => s.ElectionCenterId == c.Id);
            bool isCounted = sub != null;
            int candVotes = 0;
            int oppVotes = 0;
            bool form8Verified = false;
            DateTimeOffset? reportedAt = sub?.CreatedAtUtc;

            if (sub != null)
            {
                countedCount++;
                var subDetails = details.Where(d => d.SubmissionId == sub.Id).ToList();
                candVotes = subDetails.FirstOrDefault(d => d.CandidateElectionId == primaryCandidate.CandidateElectionId)?.Votes ?? 0;
                
                if (runnerUpCandidate != null)
                {
                    oppVotes = subDetails.FirstOrDefault(d => d.CandidateElectionId == runnerUpCandidate.CandidateElectionId)?.Votes ?? 0;
                }
                else
                {
                    var otherDetail = subDetails.Where(d => d.CandidateElectionId != primaryCandidate.CandidateElectionId)
                        .OrderByDescending(d => d.Votes)
                        .FirstOrDefault();
                    oppVotes = otherDetail?.Votes ?? 0;
                }

                form8Verified = verifications.Any(v => v.SubmissionId == sub.Id);
                totalCandidateVotes += candVotes;
                totalRunnerUpVotes += oppVotes;
            }

            centerResults.Add(new CandidateCenterResultItem(
                c.Id,
                c.CenterId,
                c.Code,
                c.Name,
                candVotes,
                oppVotes,
                candVotes - oppVotes,
                isCounted,
                form8Verified,
                reportedAt));
        }

        var leadMargin = totalCandidateVotes - totalRunnerUpVotes;

        var allTallies = new List<CandidateTallyItemDto>();
        int grandTotalVotes = 0;
        var candidateVotesMap = new Dictionary<Guid, int>();

        foreach (var cand in candidates)
        {
            int candVotes = details.Where(d => d.CandidateElectionId == cand.CandidateElectionId).Sum(d => d.Votes);
            candidateVotesMap[cand.CandidateId] = candVotes;
            grandTotalVotes += candVotes;
        }

        foreach (var cand in candidates.OrderByDescending(c => candidateVotesMap.GetValueOrDefault(c.CandidateId, 0)))
        {
            int votes = candidateVotesMap.GetValueOrDefault(cand.CandidateId, 0);
            decimal pct = grandTotalVotes > 0 ? Math.Round((decimal)votes * 100m / grandTotalVotes, 1) : 0m;
            bool isPrim = cand.CandidateElectionId == primaryCandidate.CandidateElectionId;
            allTallies.Add(new CandidateTallyItemDto(
                cand.CandidateId,
                cand.Name,
                cand.PartyName,
                cand.SymbolEmoji,
                cand.SymbolName,
                votes,
                pct,
                isPrim
            ));
        }

        return Ok(new CandidateElectionResultsSummary(
            primaryCandidate.CandidateId,
            primaryCandidate.Name,
            primaryCandidate.SymbolName,
            primaryCandidate.SymbolEmoji,
            runnerUpCandidate?.Name ?? "নিকটতম প্রতিদ্বন্দ্বী",
            runnerUpCandidate?.SymbolName ?? "প্রতীক",
            runnerUpCandidate?.SymbolEmoji ?? "🗳️",
            centers.Count,
            countedCount,
            centers.Count - countedCount,
            totalCandidateVotes,
            totalRunnerUpVotes,
            leadMargin,
            leadMargin >= 0,
            centerResults,
            allTallies));
    }

    [HttpPost("elections/{electionId:guid}/quick-result")]
    [Authorize(Policy = PermissionCodes.ResultsManage)]
    public async Task<IActionResult> SubmitQuickResult(
        Guid electionId,
        QuickResultSubmissionRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var centerLink = await pollingDb.ElectionCenters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == request.ElectionCenterId, token);
        if (centerLink is null) return BadRequest(new { error = "invalid_election_center" });

        var candidates = await candidatesDb.CandidateElections
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive)
            .OrderBy(x => x.Id)
            .ToListAsync(token);
        if (candidates.Count == 0) return BadRequest(new { error = "no_candidates_registered" });

        var primaryCe = candidates[0];
        var runnerUpCe = candidates.Count > 1 ? candidates[1] : null;

        if (runnerUpCe == null && request.RunnerUpVotes > 0)
        {
            var opponent = Candidate.Create(tenantId, "নিকটতম প্রতিদ্বন্দ্বী (স্বতন্ত্র)", null, null, null, null, null, null);
            candidatesDb.Candidates.Add(opponent);
            await candidatesDb.SaveChangesAsync(token);

            runnerUpCe = CandidateElection.Create(tenantId, electionId, opponent.Id, primaryCe.PositionId, primaryCe.AreaId, "OPP-02");
            runnerUpCe.UpdateCampaignDetails(3, "লাঙ্গল", "শান্তি ও প্রগতির অঙ্গীকার"); // Plow
            candidatesDb.CandidateElections.Add(runnerUpCe);
            await candidatesDb.SaveChangesAsync(token);
        }

        var subClaim = User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
        if (!Guid.TryParse(subClaim, out var userId) || userId == Guid.Empty)
        {
            userId = await identityDb.Users
                .Where(u => u.IsActive)
                .Select(u => u.Id)
                .FirstOrDefaultAsync(token);

            if (userId == Guid.Empty)
            {
                var anyUser = await identityDb.Users.Select(u => u.Id).FirstOrDefaultAsync(token);
                userId = anyUser != Guid.Empty ? anyUser : Guid.NewGuid();
            }
        }

        var firstState = await resultsDb.States.Where(x => x.IsActive).OrderBy(x => x.Id).FirstOrDefaultAsync(token);
        var stateId = firstState?.Id ?? 1;

        var idempotencyKey = $"QUICK-{request.ElectionCenterId}-{DateTime.UtcNow:yyyyMMddHHmmss}";
        var totalVotes = request.CandidateVotes + request.RunnerUpVotes;

        var existingSub = await resultsDb.Submissions.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.ElectionCenterId == request.ElectionCenterId, token);

        if (existingSub != null)
        {
            var oldDetails = await resultsDb.Details.Where(x => x.TenantId == tenantId && x.SubmissionId == existingSub.Id).ToListAsync(token);
            resultsDb.Details.RemoveRange(oldDetails);
            resultsDb.Submissions.Remove(existingSub);
            await resultsDb.SaveChangesAsync(token);
        }

        var submission = ResultSubmission.Create(
            tenantId,
            electionId,
            request.ElectionCenterId,
            primaryCe.PositionId,
            userId,
            stateId,
            idempotencyKey,
            totalVotes);

        var details = new List<ResultDetail>
        {
            ResultDetail.Create(tenantId, submission.Id, primaryCe.Id, request.CandidateVotes)
        };

        if (runnerUpCe != null)
        {
            details.Add(ResultDetail.Create(tenantId, submission.Id, runnerUpCe.Id, request.RunnerUpVotes));
        }

        resultsDb.Submissions.Add(submission);
        await resultsDb.SaveChangesAsync(token);

        resultsDb.Details.AddRange(details);
        await resultsDb.SaveChangesAsync(token);

        return Ok(new { success = true, submissionId = submission.Id, declaredVotes = totalVotes });
    }

    [HttpPost("elections/{electionId:guid}/opponents")]
    [Authorize(Policy = PermissionCodes.ResultsManage)]
    public async Task<ActionResult<CandidateWarRoomHero>> CreateOpponentCandidate(
        Guid electionId,
        [FromBody] CreateOpponentCandidateRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var election = await electionsDb.Elections.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.Id == electionId, token);
        if (election is null) return NotFound(new { error = "election_not_found" });

        var primaryCe = await candidatesDb.CandidateElections
            .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive, token);
        long positionId = primaryCe?.PositionId ?? 1;
        long areaId = primaryCe?.AreaId ?? election.AreaId;

        var candidate = Candidate.Create(
            tenantId,
            request.Name.Trim(),
            null,
            request.SymbolId,
            request.PartyName.Trim(),
            request.PartyName.Trim(),
            request.Slogan?.Trim(),
            request.Phone?.Trim());
        candidatesDb.Candidates.Add(candidate);
        await candidatesDb.SaveChangesAsync(token);

        var candidateElection = CandidateElection.Create(
            tenantId,
            electionId,
            candidate.Id,
            positionId,
            areaId,
            $"OPP-{DateTime.UtcNow.Ticks % 100000:D5}",
            request.SymbolId,
            request.PartyName.Trim(),
            request.Slogan?.Trim());
        candidatesDb.CandidateElections.Add(candidateElection);
        await candidatesDb.SaveChangesAsync(token);

        var sym = request.SymbolId.HasValue 
            ? await candidatesDb.Symbols.SingleOrDefaultAsync(s => s.Id == request.SymbolId.Value, token)
            : null;

        return Ok(new CandidateWarRoomHero(
            candidate.Id,
            candidateElection.Id,
            candidate.Name,
            "প্রতিদ্বন্দ্বী প্রার্থী",
            request.SymbolId,
            sym?.NameBn ?? "প্রতীক",
            sym?.NameEn ?? "Symbol",
            sym?.IconEmoji ?? "🗳️",
            request.PartyName,
            candidate.Slogan ?? "",
            candidate.Phone,
            null));
    }

    [HttpDelete("elections/{electionId:guid}/opponents/{candidateId:guid}")]
    [Authorize(Policy = PermissionCodes.ResultsManage)]
    public async Task<IActionResult> RemoveOpponentCandidate(
        Guid electionId,
        Guid candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        
        if (userCandidateId.HasValue && userCandidateId.Value == candidateId)
        {
            return BadRequest(new { error = "cannot_delete_primary", message = "নিজস্ব প্রার্থীকে প্রতিদ্বন্দ্বী তালিকা থেকে বাদ দেওয়া যাবে না।" });
        }

        var ce = await candidatesDb.CandidateElections
            .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == candidateId, token);
        if (ce != null)
        {
            candidatesDb.CandidateElections.Remove(ce);
            await candidatesDb.SaveChangesAsync(token);
        }

        return NoContent();
    }

    // =========================================================================
    // 4. EC EXPENSE COMPLIANCE SCHEDULE
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/expenses/ec-schedule")]
    [Authorize(Policy = PermissionCodes.FinanceRead)]
    public async Task<ActionResult<EcExpenseScheduleReport>> GetEcExpenseSchedule(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        const decimal ecCeiling = 2500000.00m; // 25 Lakh BDT statutory limit

        var expenses = await (
            from e in financeDb.Expenses
            join bl in financeDb.BudgetLines on e.BudgetLineId equals bl.Id into blGroup
            from bLine in blGroup.DefaultIfEmpty()
            join v in financeDb.Vendors on e.VendorId equals v.Id into vGroup
            from vendor in vGroup.DefaultIfEmpty()
            where e.TenantId == tenantId
            select new
            {
                e.Id,
                e.Amount,
                e.ExpenseDate,
                e.InvoiceNumber,
                Category = bLine != null ? bLine.Category : "সাধারণ প্রচারণা",
                VendorName = vendor != null ? vendor.Name : "স্থানীয় ভেন্ডর"
            }
        ).ToListAsync(token);

        var totalCommitted = expenses.Sum(x => x.Amount);

        var statutoryCategories = new (string NameBn, string NameEn, decimal Allocation, string[] Keywords)[]
        {
            ("প্রচারপত্র, পোস্টার, ব্যানার ও লিফলেট", "Posters, Banners & Leaflets", 600000.00m, new[] { "poster", "banner", "leaflet", "পোস্টার", "ব্যানার", "প্রচারপত্র" }),
            ("পথসভা, জনসভা, মাইকিং ও সাউন্ড", "Public Meetings & Sound Systems", 500000.00m, new[] { "sound", "mike", "rally", "meeting", "পথসভা", "মাইকিং", "সাউন্ড" }),
            ("নির্বাচনী ক্যাম্প ও কেন্দ্রীয় কার্যালয়", "Campaign Offices & Booths", 400000.00m, new[] { "office", "camp", "rent", "ক্যাম্প", "অফিস", "কার্যালয়" }),
            ("কর্মী ও পোলিং এজেন্ট ভাতা/আপ্যায়ন", "Polling Agent & Volunteer Refreshments", 450000.00m, new[] { "agent", "volunteer", "food", "refreshment", "কর্মী", "এজেন্ট", "আপ্যায়ন", "ভাতা" }),
            ("ডিজিটাল ও সোশ্যাল মিডিয়া প্রচারণা", "Digital & Social Media Ads", 250000.00m, new[] { "digital", "social", "facebook", "ডিজিটাল", "মিডিয়া" }),
            ("যাতায়াত ও যানবাহন ভাড়া", "Transport & Vehicle Hire", 200000.00m, new[] { "transport", "vehicle", "fuel", "গাড়ি", "যাতায়াত", "জ্বালানি" }),
            ("বিবিধ ও আনুষঙ্গিক খরচ", "Miscellaneous Expenses", 100000.00m, new[] { "misc", "other", "বিবিধ", "সাধারণ" })
        };

        var categoryReports = new List<EcCategoryScheduleItem>();

        foreach (var cat in statutoryCategories)
        {
            var matchedExpenses = expenses.Where(e =>
                cat.Keywords.Any(k => e.Category.Contains(k, StringComparison.OrdinalIgnoreCase))
            ).ToList();

            var spent = matchedExpenses.Sum(x => x.Amount);
            if (cat.NameEn == "Miscellaneous Expenses" && spent == 0 && totalCommitted > 0)
            {
                spent = Math.Max(0m, totalCommitted - categoryReports.Sum(x => x.SpentAmount));
            }

            categoryReports.Add(new EcCategoryScheduleItem(
                cat.NameBn,
                cat.NameEn,
                cat.Allocation,
                spent,
                Math.Max(0m, cat.Allocation - spent),
                matchedExpenses.Count));
        }

        var utilization = ecCeiling > 0 ? (double)(totalCommitted / ecCeiling) * 100.0 : 0.0;

        return Ok(new EcExpenseScheduleReport(
            ecCeiling,
            totalCommitted,
            Math.Max(0m, ecCeiling - totalCommitted),
            Math.Round(utilization, 1),
            totalCommitted <= ecCeiling,
            categoryReports));
    }

    // =========================================================================
    // 5. VOTER ROLL & CANDIDATE VOTER SLIPS
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/voters")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateVoterSummary>>> GetVoters(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] string? category,
        [FromQuery] bool? slipIssued,
        [FromQuery] string? search,
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = candidateId ?? userCandidateId;

        var query = pollingDb.Voters.Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (targetCandidateId.HasValue)
        {
            query = query.Where(x => x.CandidateId == null || x.CandidateId == targetCandidateId.Value);
        }

        if (centerId.HasValue && centerId.Value != Guid.Empty)
            query = query.Where(x => x.CenterId == centerId.Value);

        if (!string.IsNullOrWhiteSpace(category))
            query = query.Where(x => x.Category == category);

        if (slipIssued.HasValue)
            query = query.Where(x => x.SlipIssued == slipIssued.Value);

        if (!string.IsNullOrWhiteSpace(search))
        {
            var s = search.Trim();
            query = query.Where(x => x.FullName.Contains(s) || x.VoterNumber.Contains(s) || (x.Phone != null && x.Phone.Contains(s)));
        }

        var voters = await query.OrderBy(x => x.SerialNumber).ToListAsync(token);

        var centerIds = voters.Select(x => x.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(c => centerIds.Contains(c.Id)).ToDictionaryAsync(c => c.Id, token);

        var boothIds = voters.Where(x => x.BoothId.HasValue).Select(x => x.BoothId!.Value).Distinct().ToList();
        var booths = await pollingDb.Booths.Where(b => boothIds.Contains(b.Id)).ToDictionaryAsync(b => b.Id, token);

        var list = voters.Select(v => new CandidateVoterSummary(
            v.Id,
            v.CenterId,
            centers.TryGetValue(v.CenterId, out var c) ? c.Name : "ভোটকেন্দ্র",
            centers.TryGetValue(v.CenterId, out var c2) ? c2.Code : string.Empty,
            v.BoothId,
            v.BoothId.HasValue && booths.TryGetValue(v.BoothId.Value, out var b) ? b.Code : null,
            v.BoothId.HasValue && booths.TryGetValue(v.BoothId.Value, out var b2) ? b2.Name : null,
            v.VoterNumber,
            v.SerialNumber,
            v.FullName,
            v.FatherOrSpouseName,
            v.Gender,
            v.Age,
            v.AreaName,
            v.Category,
            v.SlipIssued,
            v.HasVoted,
            v.Phone,
            v.Notes,
            v.CreatedAtUtc)).ToList();

        return Ok(list);
    }

    [HttpPost("elections/{electionId:guid}/voters")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<CandidateVoterSummary>> CreateVoter(
        Guid electionId,
        CreateVoterRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var voter = Voter.Create(
            tenantId,
            electionId,
            request.CenterId,
            request.BoothId,
            request.VoterNumber.Trim(),
            request.SerialNumber,
            request.FullName.Trim(),
            request.FatherOrSpouseName?.Trim(),
            string.Equals(request.Gender, "FEMALE", StringComparison.OrdinalIgnoreCase) ? "FEMALE" : "MALE",
            request.Age,
            request.AreaName?.Trim(),
            string.IsNullOrWhiteSpace(request.Category) ? "SUPPORTER" : request.Category.Trim().ToUpperInvariant(),
            request.Phone?.Trim(),
            request.Notes?.Trim(),
            userCandidateId);

        pollingDb.Voters.Add(voter);
        await pollingDb.SaveChangesAsync(token);

        var center = await pollingDb.Centers.SingleOrDefaultAsync(x => x.Id == request.CenterId, token);
        Booth? booth = null;
        if (request.BoothId.HasValue)
            booth = await pollingDb.Booths.SingleOrDefaultAsync(x => x.Id == request.BoothId.Value, token);

        return Ok(new CandidateVoterSummary(
            voter.Id,
            voter.CenterId,
            center?.Name ?? "ভোটকেন্দ্র",
            center?.Code ?? string.Empty,
            voter.BoothId,
            booth?.Code,
            booth?.Name,
            voter.VoterNumber,
            voter.SerialNumber,
            voter.FullName,
            voter.FatherOrSpouseName,
            voter.Gender,
            voter.Age,
            voter.AreaName,
            voter.Category,
            voter.SlipIssued,
            voter.HasVoted,
            voter.Phone,
            voter.Notes,
            voter.CreatedAtUtc));
    }

    [HttpPut("elections/{electionId:guid}/voters/{voterId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> UpdateVoter(
        Guid electionId,
        Guid voterId,
        UpdateVoterRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        voter.UpdateDetails(
            request.CenterId,
            request.BoothId,
            request.VoterNumber.Trim(),
            request.SerialNumber,
            request.FullName.Trim(),
            request.FatherOrSpouseName?.Trim(),
            string.Equals(request.Gender, "FEMALE", StringComparison.OrdinalIgnoreCase) ? "FEMALE" : "MALE",
            request.Age,
            request.AreaName?.Trim(),
            string.IsNullOrWhiteSpace(request.Category) ? "SUPPORTER" : request.Category.Trim().ToUpperInvariant(),
            request.Phone?.Trim(),
            request.Notes?.Trim());

        voter.MarkSlipIssued(request.SlipIssued);
        voter.MarkVoted(request.HasVoted);

        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/voters/{voterId:guid}/toggle-slip")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> ToggleSlip(Guid electionId, Guid voterId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        voter.MarkSlipIssued(!voter.SlipIssued);
        await pollingDb.SaveChangesAsync(token);
        return Ok(new { slipIssued = voter.SlipIssued });
    }

    [HttpPost("elections/{electionId:guid}/voters/{voterId:guid}/toggle-voted")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> ToggleVoted(Guid electionId, Guid voterId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        voter.MarkVoted(!voter.HasVoted);
        await pollingDb.SaveChangesAsync(token);
        return Ok(new { hasVoted = voter.HasVoted });
    }

    [HttpPost("elections/{electionId:guid}/voters/batch-mark-slips")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> BatchMarkSlips(
        Guid electionId,
        BatchMarkSlipsRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voters = await pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId && request.VoterIds.Contains(x.Id))
            .ToListAsync(token);

        foreach (var v in voters)
        {
            v.MarkSlipIssued(request.SlipIssued);
        }

        await pollingDb.SaveChangesAsync(token);
        return Ok(new { updatedCount = voters.Count, slipIssued = request.SlipIssued });
    }

    [HttpDelete("elections/{electionId:guid}/voters/{voterId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> DeleteVoter(Guid electionId, Guid voterId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        pollingDb.Voters.Remove(voter);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 6. ELECTION-DAY INCIDENTS & MAGISTRATE COMPLAINT
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/incidents")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateIncidentSummary>>> GetIncidents(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var incidents = await pollingDb.Incidents
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
            .OrderByDescending(x => x.ReportedAt)
            .ToListAsync(token);

        var centerIds = incidents.Select(x => x.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(c => centerIds.Contains(c.Id)).ToDictionaryAsync(c => c.Id, token);

        var boothIds = incidents.Where(x => x.BoothId.HasValue).Select(x => x.BoothId!.Value).Distinct().ToList();
        var booths = await pollingDb.Booths.Where(b => boothIds.Contains(b.Id)).ToDictionaryAsync(b => b.Id, token);

        var list = incidents.Select(inc => new CandidateIncidentSummary(
            inc.Id,
            inc.CenterId,
            centers.TryGetValue(inc.CenterId, out var c) ? c.Name : "ভোটকেন্দ্র",
            centers.TryGetValue(inc.CenterId, out var c2) ? c2.Code : string.Empty,
            inc.BoothId,
            inc.BoothId.HasValue && booths.TryGetValue(inc.BoothId.Value, out var b) ? b.Code : null,
            inc.BoothId.HasValue && booths.TryGetValue(inc.BoothId.Value, out var b2) ? b2.Name : null,
            inc.IncidentType,
            inc.Severity,
            inc.Title,
            inc.Description,
            inc.ReportedBy,
            inc.ReportedByPhone,
            inc.ReportedAt,
            inc.Status,
            inc.EvidenceAttachmentUrl,
            inc.MagistrateName,
            inc.ActionTaken,
            inc.OfficialComplaintGenerated,
            inc.CreatedAtUtc)).ToList();

        return Ok(list);
    }

    [HttpPost("elections/{electionId:guid}/incidents")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<CandidateIncidentSummary>> CreateIncident(
        Guid electionId,
        CreateIncidentRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var incident = Incident.Create(
            tenantId,
            electionId,
            request.CenterId,
            request.BoothId,
            request.IncidentType.Trim().ToUpperInvariant(),
            request.Severity.Trim().ToUpperInvariant(),
            request.Title.Trim(),
            request.Description.Trim(),
            request.ReportedBy.Trim(),
            request.ReportedByPhone?.Trim(),
            request.EvidenceAttachmentUrl?.Trim());

        pollingDb.Incidents.Add(incident);
        await pollingDb.SaveChangesAsync(token);

        var center = await pollingDb.Centers.SingleOrDefaultAsync(x => x.Id == request.CenterId, token);
        Booth? booth = null;
        if (request.BoothId.HasValue)
            booth = await pollingDb.Booths.SingleOrDefaultAsync(x => x.Id == request.BoothId.Value, token);

        return Ok(new CandidateIncidentSummary(
            incident.Id,
            incident.CenterId,
            center?.Name ?? "ভোটকেন্দ্র",
            center?.Code ?? string.Empty,
            incident.BoothId,
            booth?.Code,
            booth?.Name,
            incident.IncidentType,
            incident.Severity,
            incident.Title,
            incident.Description,
            incident.ReportedBy,
            incident.ReportedByPhone,
            incident.ReportedAt,
            incident.Status,
            incident.EvidenceAttachmentUrl,
            incident.MagistrateName,
            incident.ActionTaken,
            incident.OfficialComplaintGenerated,
            incident.CreatedAtUtc));
    }

    [HttpPut("elections/{electionId:guid}/incidents/{incidentId:guid}/status")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> UpdateIncidentStatus(
        Guid electionId,
        Guid incidentId,
        UpdateIncidentStatusRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var incident = await pollingDb.Incidents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == incidentId, token);
        if (incident is null) return NotFound(new { error = "incident_not_found" });

        incident.UpdateStatus(
            request.Status.Trim().ToUpperInvariant(),
            request.ActionTaken?.Trim(),
            request.MagistrateName?.Trim(),
            request.OfficialComplaintGenerated);

        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpDelete("elections/{electionId:guid}/incidents/{incidentId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> DeleteIncident(Guid electionId, Guid incidentId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var incident = await pollingDb.Incidents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == incidentId, token);
        if (incident is null) return NotFound(new { error = "incident_not_found" });

        pollingDb.Incidents.Remove(incident);
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 10A. BROADCAST OUTBOX LOGS
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBroadcastLogItem>>> GetBroadcastLogs(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT broadcast_id, channel, template_type, recipient_count, status, sent_at
            FROM campaign.broadcast_logs
            WHERE tenant_id = @t AND election_id = @e
            ORDER BY sent_at DESC
            LIMIT 50;";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);

        var list = new List<CandidateBroadcastLogItem>();
        await using var reader = await cmd.ExecuteReaderAsync(token);
        while (await reader.ReadAsync(token))
        {
            list.Add(new CandidateBroadcastLogItem(
                reader.GetGuid(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.GetInt32(3),
                reader.GetString(4),
                new DateTimeOffset(reader.GetDateTime(5), TimeSpan.Zero)
            ));
        }

        return Ok(list);
    }

    // =========================================================================
    // 10B. SMS GATEWAY CONFIGURATION & LIVE BALANCE
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/sms-config")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<SmsGatewayConfigDto>> GetSmsGatewayConfig(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT config_id, provider, api_key, api_secret, sender_id, endpoint_url, is_active, balance, last_tested_at, updated_at
            FROM campaign.sms_gateway_configs
            WHERE tenant_id = @t AND election_id = @e
            LIMIT 1;";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);

        await using var reader = await cmd.ExecuteReaderAsync(token);
        if (await reader.ReadAsync(token))
        {
            var configId = reader.GetGuid(0);
            var provider = reader.GetString(1);
            var apiKey = reader.GetString(2);
            var apiSecret = reader.IsDBNull(3) ? null : reader.GetString(3);
            var senderId = reader.GetString(4);
            var endpointUrl = reader.IsDBNull(5) ? null : reader.GetString(5);
            var isActive = reader.GetBoolean(6);
            var balance = reader.GetDecimal(7);
            var lastTestedAt = reader.IsDBNull(8) ? null : reader.GetFieldValue<DateTimeOffset?>(8);
            var updatedAt = reader.GetFieldValue<DateTimeOffset>(9);

            // Live balance sync for sms.net.bd
            if (!string.IsNullOrWhiteSpace(apiKey) && (provider == "SMS_NET_BD" || endpointUrl?.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase) == true))
            {
                try
                {
                    using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
                    var balUrl = $"https://api.sms.net.bd/user/balance/?api_key={apiKey.Trim()}";
                    var resp = await http.GetAsync(balUrl, token);
                    if (resp.IsSuccessStatusCode)
                    {
                        var content = await resp.Content.ReadAsStringAsync(token);
                        using var doc = JsonDocument.Parse(content);
                        if (doc.RootElement.TryGetProperty("data", out var dataEl) &&
                            dataEl.TryGetProperty("balance", out var balEl))
                        {
                            var balStr = balEl.GetString() ?? balEl.GetRawText();
                            if (decimal.TryParse(balStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var liveBal))
                            {
                                balance = liveBal;
                            }
                        }
                    }
                }
                catch { }
            }

            return Ok(new SmsGatewayConfigDto(configId, provider, apiKey, apiSecret, senderId, endpointUrl, isActive, balance, lastTestedAt, updatedAt));
        }

        return Ok(new SmsGatewayConfigDto(Guid.Empty, "SMS_NET_BD", "1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN", null, "", "https://api.sms.net.bd/sendsms", true, 0.90m, null, DateTimeOffset.UtcNow));
    }

    [HttpPut("elections/{electionId:guid}/sms-config")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> UpdateSmsGatewayConfig(Guid electionId, [FromBody] UpdateSmsGatewayConfigRequest request, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            INSERT INTO campaign.sms_gateway_configs (config_id, tenant_id, election_id, provider, api_key, api_secret, sender_id, endpoint_url, is_active, balance, updated_at)
            VALUES (gen_random_uuid(), @t, @e, @prov, @key, @sec, @sid, @ep, @act, 0.90, NOW())
            ON CONFLICT (tenant_id, election_id) DO UPDATE
            SET provider = EXCLUDED.provider,
                api_key = EXCLUDED.api_key,
                api_secret = EXCLUDED.api_secret,
                sender_id = EXCLUDED.sender_id,
                endpoint_url = EXCLUDED.endpoint_url,
                is_active = EXCLUDED.is_active,
                updated_at = NOW();";

        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);
        var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; cmd.Parameters.Add(pE);
        var pProv = cmd.CreateParameter(); pProv.ParameterName = "@prov"; pProv.Value = request.Provider.Trim().ToUpperInvariant(); cmd.Parameters.Add(pProv);
        var pKey = cmd.CreateParameter(); pKey.ParameterName = "@key"; pKey.Value = request.ApiKey.Trim(); cmd.Parameters.Add(pKey);
        var pSec = cmd.CreateParameter(); pSec.ParameterName = "@sec"; pSec.Value = (object?)request.ApiSecret?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pSec);
        var pSid = cmd.CreateParameter(); pSid.ParameterName = "@sid"; pSid.Value = (object?)request.SenderId?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pSid);
        var pEp = cmd.CreateParameter(); pEp.ParameterName = "@ep"; pEp.Value = (object?)request.EndpointUrl?.Trim() ?? DBNull.Value; cmd.Parameters.Add(pEp);
        var pAct = cmd.CreateParameter(); pAct.ParameterName = "@act"; pAct.Value = request.IsActive; cmd.Parameters.Add(pAct);

        await cmd.ExecuteNonQueryAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/sms-test")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> TestSmsGateway(
        Guid electionId,
        [FromBody] TestSmsRequest request,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(request.Phone))
        {
            return BadRequest(new { error = "phone_required", message = "টেস্ট মোবাইল নম্বর প্রদান করুন।" });
        }

        var tenantId = tenantContext.TenantId;
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        string provider = !string.IsNullOrWhiteSpace(request.Provider) ? request.Provider.Trim() : "SMS_NET_BD";
        string apiKey = !string.IsNullOrWhiteSpace(request.ApiKey) ? request.ApiKey.Trim() : "";
        string senderId = request.SenderId != null ? request.SenderId.Trim() : "";
        string endpointUrl = !string.IsNullOrWhiteSpace(request.EndpointUrl) ? request.EndpointUrl.Trim() : "https://api.sms.net.bd/sendsms";

        await using (var getCmd = conn.CreateCommand())
        {
            getCmd.CommandText = @"
                SELECT provider, api_key, sender_id, endpoint_url
                FROM campaign.sms_gateway_configs
                WHERE tenant_id = @t AND election_id = @e
                LIMIT 1;";
            var pT = getCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; getCmd.Parameters.Add(pT);
            var pE = getCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; getCmd.Parameters.Add(pE);
            await using var reader = await getCmd.ExecuteReaderAsync(token);
            if (await reader.ReadAsync(token))
            {
                if (string.IsNullOrWhiteSpace(apiKey)) apiKey = reader.GetString(1);
                if (string.IsNullOrWhiteSpace(senderId)) senderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                if (string.IsNullOrWhiteSpace(provider) || string.Equals(provider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase)) provider = reader.GetString(0);
                if (string.IsNullOrWhiteSpace(endpointUrl) || string.Equals(endpointUrl, "https://api.sms.net.bd/sendsms", StringComparison.OrdinalIgnoreCase)) endpointUrl = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
            }
        }

        // Live Gateway Integration for SMS.NET.BD
        if (string.Equals(provider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase) || endpointUrl.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase))
        {
            try
            {
                using var httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
                var formParams = new Dictionary<string, string>
                {
                    ["api_key"] = apiKey,
                    ["msg"] = string.IsNullOrWhiteSpace(request.Message) ? "টেস্ট বার্তা: EEMS নির্বাচনী ওয়ার রুম থেকে পরীক্ষামূলক এসএমএস।" : request.Message,
                    ["to"] = request.Phone.Trim()
                };
                if (!string.IsNullOrWhiteSpace(senderId))
                {
                    formParams["sender_id"] = senderId.Trim();
                }

                var response = await httpClient.PostAsync(endpointUrl, new FormUrlEncodedContent(formParams), token);
                var rawBody = await response.Content.ReadAsStringAsync(token);

                bool isSuccess = false;
                string statusMsg = "";
                try
                {
                    using var doc = JsonDocument.Parse(rawBody);
                    var root = doc.RootElement;
                    int errCode = root.TryGetProperty("error", out var errProp) ? errProp.GetInt32() : -1;
                    string gwMsg = root.TryGetProperty("msg", out var msgProp) ? msgProp.GetString() ?? "" : "";

                    if (errCode == 0)
                    {
                        isSuccess = true;
                        statusMsg = "এসএমএস.নেট.বিডি (SMS.NET.BD) গেটওয়ে দিয়ে টেস্ট বার্তা সফলভাবে পাঠানো হয়েছে।";
                    }
                    else if (errCode == 405)
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: এপিআই টোকেন অনুমোদিত নয় বা ভুল (Error 405)। আপনার sms.net.bd ড্যাশবোর্ড থেকে সঠিক API Key কপি করে সংরক্ষণ করুন।";
                    }
                    else if (errCode == 413)
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: অননুমোদিত সেন্ডার আইডি '{senderId}' (Error 413)। নন-মাস্কিং এসএমএস পাঠাতে 'সেন্ডার আইডি' ঘরটি খালি রাখুন।";
                    }
                    else
                    {
                        isSuccess = false;
                        statusMsg = $"এসএমএস গেটওয়ে রেসপন্স: {gwMsg} (Error code: {errCode})।";
                    }
                }
                catch
                {
                    statusMsg = rawBody;
                }

                return Ok(new {
                    success = isSuccess,
                    provider = "SMS_NET_BD",
                    phone = request.Phone,
                    message = statusMsg,
                    raw = rawBody
                });
            }
            catch (Exception ex)
            {
                return Ok(new {
                    success = false,
                    provider = "SMS_NET_BD",
                    phone = request.Phone,
                    message = $"গেটওয়ে কানেকশন ত্রুটি: {ex.Message}"
                });
            }
        }

        return Ok(new {
            success = true,
            provider,
            phone = request.Phone,
            message = "টেস্ট বার্তা সফলভাবে প্রক্রিয়াকরণ সম্পন্ন হয়েছে।"
        });
    }

    // =========================================================================
    // 10C. VOTER BROADCAST DISPATCHER (SMS & WHATSAPP)
    // =========================================================================

    [HttpPost("elections/{electionId:guid}/voter-broadcasts")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<SendVoterBroadcastResponse>> SendVoterBroadcast(
        Guid electionId,
        [FromBody] SendVoterBroadcastRequest request,
        CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(request.MessageContent))
        {
            return BadRequest(new { error = "message_empty", message = "মেসেজের বিষয়বস্তু প্রদান করা আবশ্যক।" });
        }

        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = request.CandidateId ?? userCandidateId;
        var channel = (request.Channel ?? "WHATSAPP").Trim().ToUpperInvariant();
        var targetFilter = (request.TargetFilter ?? "ALL").Trim().ToUpperInvariant();

        // 1. Query voters matching scope
        var voterQuery = pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (targetCandidateId.HasValue)
        {
            voterQuery = voterQuery.Where(x => x.CandidateId == null || x.CandidateId == targetCandidateId.Value);
        }

        if (request.TargetCenterId.HasValue && request.TargetCenterId.Value != Guid.Empty)
        {
            voterQuery = voterQuery.Where(x => x.CenterId == request.TargetCenterId.Value);
        }

        if (string.Equals(targetFilter, "SUPPORTER", StringComparison.OrdinalIgnoreCase) || string.Equals(targetFilter, "SUPPORTERS", StringComparison.OrdinalIgnoreCase))
        {
            voterQuery = voterQuery.Where(x => x.Category == "SUPPORTER");
        }
        else if (string.Equals(targetFilter, "UNISSUED_SLIP", StringComparison.OrdinalIgnoreCase) || string.Equals(targetFilter, "UNISSUED_SLIP_ONLY", StringComparison.OrdinalIgnoreCase))
        {
            voterQuery = voterQuery.Where(x => !x.SlipIssued);
        }

        var voters = await voterQuery
            .Where(x => !string.IsNullOrEmpty(x.Phone))
            .OrderBy(x => x.SerialNumber)
            .ToListAsync(token);

        if (voters.Count == 0)
        {
            return BadRequest(new { error = "no_recipients", message = "নির্বাচিত ফিল্টারে মোবাইল নম্বরযুক্ত কোনো ভোটার পাওয়া যায়নি।" });
        }

        // 2. Fetch center and booth names for placeholder interpolation
        var centerIds = voters.Select(v => v.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(c => centerIds.Contains(c.Id)).ToDictionaryAsync(c => c.Id, token);
        var boothIds = voters.Where(v => v.BoothId.HasValue).Select(v => v.BoothId!.Value).Distinct().ToList();
        var booths = await pollingDb.Booths.Where(b => boothIds.Contains(b.Id)).ToDictionaryAsync(b => b.Id, token);

        // Fetch candidate details for placeholders
        string candName = "প্রার্থী";
        string candSymbol = "মার্কা";
        var candAssignment = await candidatesDb.CandidateElections
            .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && (targetCandidateId == null || x.CandidateId == targetCandidateId.Value), token);
        if (candAssignment == null)
        {
            candAssignment = await candidatesDb.CandidateElections
                .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive, token);
        }
        if (candAssignment != null)
        {
            var candProfile = await candidatesDb.Candidates.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == candAssignment.CandidateId, token);
            if (candProfile != null) candName = candProfile.Name;
            if (candAssignment.SymbolId.HasValue)
            {
                var sym = await candidatesDb.Symbols.SingleOrDefaultAsync(s => s.Id == candAssignment.SymbolId.Value, token);
                if (sym != null) candSymbol = sym.NameBn ?? sym.NameEn ?? "মার্কা";
            }
        }

        // 3. Build queue items with personalized message
        var queue = new List<VoterQueueItem>();
        foreach (var v in voters)
        {
            var centerName = centers.TryGetValue(v.CenterId, out var c) ? c.Name : "ভোটকেন্দ্র";
            string? boothName = v.BoothId.HasValue && booths.TryGetValue(v.BoothId.Value, out var b) ? b.Name : "সাধারণ বুথ";

            var msg = request.MessageContent
                .Replace("{নাম}", v.FullName, StringComparison.Ordinal)
                .Replace("{ভোটারের নাম}", v.FullName, StringComparison.Ordinal)
                .Replace("{ভোটকেন্দ্র}", centerName, StringComparison.Ordinal)
                .Replace("{বুথ}", boothName, StringComparison.Ordinal)
                .Replace("{ক্রমিক}", v.SerialNumber.ToString(CultureInfo.InvariantCulture), StringComparison.Ordinal)
                .Replace("{ভোটার নং}", v.VoterNumber, StringComparison.Ordinal)
                .Replace("{প্রার্থী}", candName, StringComparison.Ordinal)
                .Replace("{মার্কা}", candSymbol, StringComparison.Ordinal);

            var cleanPhone = System.Text.RegularExpressions.Regex.Replace(v.Phone ?? string.Empty, @"\D", "");
            if (cleanPhone.StartsWith("880", StringComparison.Ordinal)) cleanPhone = cleanPhone.Substring(2);

            var waUrl = $"https://wa.me/88{cleanPhone}?text={Uri.EscapeDataString(msg)}";

            queue.Add(new VoterQueueItem(
                v.Id,
                v.FullName,
                v.Phone ?? string.Empty,
                v.SerialNumber,
                v.VoterNumber,
                centerName,
                boothName,
                msg,
                waUrl
            ));
        }

        // 4. Update database
        var broadcastId = Guid.NewGuid();
        var templateType = string.IsNullOrWhiteSpace(request.TemplateType) ? "SLIP_NOTICE" : request.TemplateType.Trim();
        var conn = pollingDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        string responseMsg;
        if (channel == "SMS")
        {
            foreach (var v in voters)
            {
                v.MarkSlipIssued(true);
            }
            await pollingDb.SaveChangesAsync(token);

            // Fetch gateway config
            string gwProvider = "SMS_NET_BD";
            string gwApiKey = "";
            string gwSenderId = "";
            string gwEndpoint = "https://api.sms.net.bd/sendsms";

            await using (var getCmd = conn.CreateCommand())
            {
                getCmd.CommandText = @"
                    SELECT provider, api_key, sender_id, endpoint_url
                    FROM campaign.sms_gateway_configs
                    WHERE tenant_id = @t AND election_id = @e
                    LIMIT 1;";
                var pT = getCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; getCmd.Parameters.Add(pT);
                var pE = getCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; getCmd.Parameters.Add(pE);
                await using var reader = await getCmd.ExecuteReaderAsync(token);
                if (await reader.ReadAsync(token))
                {
                    gwProvider = reader.GetString(0);
                    gwApiKey = reader.GetString(1);
                    gwSenderId = reader.IsDBNull(2) ? "" : reader.GetString(2);
                    gwEndpoint = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
                }
            }

            int successCount = 0;
            if (string.Equals(gwProvider, "SMS_NET_BD", StringComparison.OrdinalIgnoreCase) || gwEndpoint.Contains("sms.net.bd", StringComparison.OrdinalIgnoreCase))
            {
                using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
                foreach (var q in queue)
                {
                    try
                    {
                        var formParams = new Dictionary<string, string>
                        {
                            ["api_key"] = gwApiKey,
                            ["msg"] = q.Message,
                            ["to"] = q.Phone
                        };
                        if (!string.IsNullOrWhiteSpace(gwSenderId)) formParams["sender_id"] = gwSenderId;

                        var resp = await http.PostAsync(gwEndpoint, new FormUrlEncodedContent(formParams), token);
                        if (resp.IsSuccessStatusCode) successCount++;
                    }
                    catch { }
                }
            }

            responseMsg = $"বাল্ক এসএমএস পাঠানো হয়েছে। সফল: {successCount}/{queue.Count} জন ভোটার।";
        }
        else
        {
            responseMsg = $"{queue.Count} জন ভোটারের ডিজিটাল স্লিপ বার্তা তৈরি হয়েছে।";
        }

        // Log outbox
        await using (var insCmd = conn.CreateCommand())
        {
            insCmd.CommandText = @"
                INSERT INTO campaign.broadcast_logs (broadcast_id, tenant_id, election_id, channel, recipient_group, recipient_count, message_content, template_type, status, sent_at)
                VALUES (@id, @t, @e, @ch, 'VOTERS', @rc, @msg, @tpl, @st, NOW());";
            var pId = insCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = broadcastId; insCmd.Parameters.Add(pId);
            var pT = insCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; insCmd.Parameters.Add(pT);
            var pE = insCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; insCmd.Parameters.Add(pE);
            var pCh = insCmd.CreateParameter(); pCh.ParameterName = "@ch"; pCh.Value = channel; insCmd.Parameters.Add(pCh);
            var pRc = insCmd.CreateParameter(); pRc.ParameterName = "@rc"; pRc.Value = voters.Count; insCmd.Parameters.Add(pRc);
            var pMsg = insCmd.CreateParameter(); pMsg.ParameterName = "@msg"; pMsg.Value = request.MessageContent; insCmd.Parameters.Add(pMsg);
            var pTpl = insCmd.CreateParameter(); pTpl.ParameterName = "@tpl"; pTpl.Value = (object?)templateType ?? DBNull.Value; insCmd.Parameters.Add(pTpl);
            var pSt = insCmd.CreateParameter(); pSt.ParameterName = "@st"; pSt.Value = channel == "SMS" ? "DELIVERED" : "QUEUED"; insCmd.Parameters.Add(pSt);
            await insCmd.ExecuteNonQueryAsync(token);
        }

        return Ok(new SendVoterBroadcastResponse(
            true,
            broadcastId,
            voters.Count,
            channel,
            channel == "SMS" ? "DELIVERED" : "QUEUED_FOR_DISPATCH",
            responseMsg,
            queue
        ));
    }

    // =========================================================================
    // 10D. WHATSAPP QR AUTO-BOT DISPATCHER
    // =========================================================================

    [HttpGet("whatsapp/status")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<IActionResult> GetWhatsAppBotStatus(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var response = await client.GetAsync("http://localhost:5140/api/whatsapp/status", token);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync(token);
                return Content(content, "application/json");
            }
        }
        catch { }

        return Ok(new {
            connected = false,
            phone = (string?)null,
            isConnecting = false,
            hasQR = false,
            serviceRunning = false,
            message = "হোয়াটসঅ্যাপ অটো-বট সার্ভিস বর্তমানে অফলাইনে আছে।"
        });
    }

    [HttpGet("whatsapp/qr")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<IActionResult> GetWhatsAppBotQr(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var response = await client.GetAsync("http://localhost:5140/api/whatsapp/qr", token);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync(token);
                return Content(content, "application/json");
            }
        }
        catch { }

        return Ok(new {
            connected = false,
            phone = (string?)null,
            qrDataUrl = (string?)null,
            message = "কিউআর কোড পাওয়া যায়নি।"
        });
    }

    [HttpPost("whatsapp/auto-broadcast")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> SendWhatsAppAutoBroadcast(
        [FromBody] WhatsAppAutoBroadcastRequest request,
        CancellationToken token)
    {
        try
        {
            if (request == null || request.Items == null || request.Items.Count == 0)
            {
                return BadRequest(new { error = "empty_items", message = "কোনো প্রাপক ভোটার তালিকা প্রদান করা হয়নি।" });
            }

            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            var json = JsonSerializer.Serialize(request, CamelCaseJsonOptions);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/broadcast", content, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return new ContentResult
            {
                StatusCode = (int)response.StatusCode,
                Content = resultStr,
                ContentType = "application/json"
            };
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = ex.Message });
        }
    }

    [HttpPost("whatsapp/logout")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> LogoutWhatsAppBot(CancellationToken token)
    {
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/logout", null, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return Content(resultStr, "application/json");
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = "bot_error", message = ex.Message });
        }
    }

    // =========================================================================
    // 10E. CANDIDATE TEAM & SUB-USERS (মাস্টার প্রার্থীর সাব-ইউজার ও কর্মী ব্যবস্থাপনা)
    // =========================================================================

    [HttpGet("team-users")]
    [Authorize(Policy = PermissionCodes.UsersRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateTeamUserItem>>> GetCandidateTeamUsers(
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = userCandidateId ?? candidateId;

        if (!targetCandidateId.HasValue && !isSuperAdmin)
        {
            return Ok(Array.Empty<CandidateTeamUserItem>());
        }

        var conn = identityDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        await using var cmd = conn.CreateCommand();
        if (targetCandidateId.HasValue)
        {
            cmd.CommandText = @"
                SELECT u.user_id, u.external_subject, u.display_name, u.email, tu.candidate_id, tu.is_active, u.created_at
                FROM iam.tenant_users tu
                JOIN iam.users u ON tu.user_id = u.user_id
                WHERE tu.tenant_id = @t AND tu.candidate_id = @c
                ORDER BY u.created_at DESC;";
            var pC = cmd.CreateParameter(); pC.ParameterName = "@c"; pC.Value = targetCandidateId.Value; cmd.Parameters.Add(pC);
        }
        else
        {
            cmd.CommandText = @"
                SELECT u.user_id, u.external_subject, u.display_name, u.email, tu.candidate_id, tu.is_active, u.created_at
                FROM iam.tenant_users tu
                JOIN iam.users u ON tu.user_id = u.user_id
                WHERE tu.tenant_id = @t AND tu.candidate_id IS NOT NULL
                ORDER BY u.created_at DESC;";
        }
        var pT = cmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; cmd.Parameters.Add(pT);

        var list = new List<CandidateTeamUserItem>();
        await using var reader = await cmd.ExecuteReaderAsync(token);
        while (await reader.ReadAsync(token))
        {
            list.Add(new CandidateTeamUserItem(
                reader.GetGuid(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.IsDBNull(3) ? null : reader.GetString(3),
                null,
                "ক্যাম্পেইন টিম সদস্য",
                reader.GetBoolean(5),
                new DateTimeOffset(reader.GetDateTime(6), TimeSpan.Zero)
            ));
        }

        return Ok(list);
    }

    [HttpPost("team-users")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<ActionResult<CandidateTeamUserItem>> CreateCandidateTeamUser(
        [FromBody] CreateCandidateTeamUserRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = userCandidateId ?? request.CandidateId;

        if (!targetCandidateId.HasValue)
        {
            return BadRequest(new { error = "candidate_required", message = "প্রার্থী নির্ধারণ করা হয়নি।" });
        }

        var normalizedUsername = request.Username.Trim();
        if (await identityDb.Users.AnyAsync(u => u.ExternalSubject == normalizedUsername, token))
        {
            return Conflict(new { error = "username_exists", message = "এই ব্যবহারকারী আইডি (Username) ইতিমধ্যে ব্যবহৃত হচ্ছে। অন্য আইডি দিন।" });
        }

        var user = EEMS.Modules.Identity.Domain.User.Create(request.Username.Trim(), request.DisplayName.Trim(), request.Email?.Trim());
        identityDb.Users.Add(user);

        var tenantUser = EEMS.Modules.Identity.Domain.TenantUser.Create(tenantId, user.Id, targetCandidateId.Value);
        identityDb.TenantUsers.Add(tenantUser);

        var hash = passwordHasher.HashPassword(user, request.Password.Trim());
        identityDb.PasswordCredentials.Add(EEMS.Modules.Identity.Domain.PasswordCredential.Create(user.Id, hash, false));

        await identityDb.SaveChangesAsync(token);

        return Ok(new CandidateTeamUserItem(
            user.Id,
            user.ExternalSubject,
            user.DisplayName,
            user.Email,
            request.Phone?.Trim(),
            request.Role?.Trim() ?? "ক্যাম্পেইন টিম সদস্য",
            true,
            user.CreatedAtUtc
        ));
    }

    [HttpPut("team-users/{userId:guid}/status")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<IActionResult> ToggleTeamUserStatus(
        Guid userId,
        [FromBody] ToggleUserStatusRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();

        var tu = await identityDb.TenantUsers.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.UserId == userId, token);

        if (tu == null) return NotFound(new { error = "user_not_found" });

        if (userCandidateId.HasValue && tu.CandidateId != userCandidateId.Value)
        {
            return Forbid();
        }

        if (request.IsActive) tu.Enable(); else tu.Disable();
        await identityDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("team-users/{userId:guid}/reset-password")]
    [Authorize(Policy = PermissionCodes.UsersManage)]
    public async Task<IActionResult> ResetTeamUserPassword(
        Guid userId,
        [FromBody] ResetPasswordRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();

        var tu = await identityDb.TenantUsers.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.UserId == userId, token);

        if (tu == null) return NotFound(new { error = "user_not_found" });

        if (userCandidateId.HasValue && tu.CandidateId != userCandidateId.Value)
        {
            return Forbid();
        }

        var user = await identityDb.Users.SingleOrDefaultAsync(u => u.Id == userId, token);
        if (user == null) return NotFound();

        var cred = await identityDb.PasswordCredentials.SingleOrDefaultAsync(p => p.UserId == userId, token);
        var newHash = passwordHasher.HashPassword(user, request.NewPassword.Trim());
        if (cred != null)
        {
            cred.ChangePassword(newHash);
        }
        else
        {
            identityDb.PasswordCredentials.Add(EEMS.Modules.Identity.Domain.PasswordCredential.Create(user.Id, newHash, false));
        }

        await identityDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 10F. SUPER ADMIN MASTER CANDIDATES OVERVIEW HUB (মাস্টার প্রার্থীভিত্তিক তদারকি)
    // =========================================================================

    [HttpGet("master-overview")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<MasterCandidateOverviewItem>>> GetMasterCandidateOverview(
        [FromQuery] Guid? electionId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var conn = candidatesDb.Database.GetDbConnection();
        if (conn.State != System.Data.ConnectionState.Open) await conn.OpenAsync(token);

        // Fetch all master candidates (filtered by election if provided)
        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT c.candidate_id, c.name, ce.election_id, s.name_bn, s.name_en, s.icon_emoji, 
                   ce.party_name, ce.slogan, c.phone, c.campaign_office, el.name as election_name
            FROM election.candidates c
            JOIN election.candidate_elections ce ON c.candidate_id = ce.candidate_id
            LEFT JOIN election.symbols s ON ce.symbol_id = s.symbol_id
            LEFT JOIN election.elections el ON ce.election_id = el.election_id
            WHERE c.is_active = TRUE " + (electionId.HasValue ? " AND ce.election_id = @e" : "") + @"
            ORDER BY ce.created_at;";

        if (electionId.HasValue)
        {
            var pE = cmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId.Value; cmd.Parameters.Add(pE);
        }

        var candidateList = new List<MasterCandidateOverviewItem>();
        var candRaw = new List<(Guid CandId, string Name, Guid ElecId, string? SymBn, string? SymEn, string? Emoji, string? Party, string? Slogan, string? Phone, string? Office, string? ElecName)>();

        await using (var reader = await cmd.ExecuteReaderAsync(token))
        {
            while (await reader.ReadAsync(token))
            {
                candRaw.Add((
                    reader.GetGuid(0),
                    reader.GetString(1),
                    reader.GetGuid(2),
                    reader.IsDBNull(3) ? null : reader.GetString(3),
                    reader.IsDBNull(4) ? null : reader.GetString(4),
                    reader.IsDBNull(5) ? "🗳️" : reader.GetString(5),
                    reader.IsDBNull(6) ? "স্বতন্ত্র" : reader.GetString(6),
                    reader.IsDBNull(7) ? "" : reader.GetString(7),
                    reader.IsDBNull(8) ? null : reader.GetString(8),
                    reader.IsDBNull(9) ? null : reader.GetString(9),
                    reader.IsDBNull(10) ? "" : reader.GetString(10)
                ));
            }
        }

        foreach (var c in candRaw)
        {
            // 1. Primary user
            string? primaryUsername = null;
            string? primaryDisplayName = null;
            await using (var uCmd = conn.CreateCommand())
            {
                uCmd.CommandText = @"
                    SELECT u.external_subject, u.display_name
                    FROM iam.tenant_users tu
                    JOIN iam.users u ON tu.user_id = u.user_id
                    WHERE tu.candidate_id = @cid
                    ORDER BY tu.joined_at
                    LIMIT 1;";
                var p = uCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; uCmd.Parameters.Add(p);
                await using var uReader = await uCmd.ExecuteReaderAsync(token);
                if (await uReader.ReadAsync(token))
                {
                    primaryUsername = uReader.GetString(0);
                    primaryDisplayName = uReader.GetString(1);
                }
            }

            // 2. Team sub-users count
            int teamCount = 0;
            await using (var tCmd = conn.CreateCommand())
            {
                tCmd.CommandText = "SELECT COUNT(*) FROM iam.tenant_users WHERE candidate_id = @cid;";
                var p = tCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; tCmd.Parameters.Add(p);
                var res = await tCmd.ExecuteScalarAsync(token);
                if (res != null) teamCount = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            // 3. Booth agents count
            int agentCount = 0;
            await using (var aCmd = conn.CreateCommand())
            {
                aCmd.CommandText = "SELECT COUNT(*) FROM polling.booth_agents WHERE candidate_id = @cid;";
                var p = aCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; aCmd.Parameters.Add(p);
                var res = await aCmd.ExecuteScalarAsync(token);
                if (res != null) agentCount = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            // 4. Voters in scope & slips count
            int voterCount = 0;
            int slipsIssuedCount = 0;
            await using (var vCmd = conn.CreateCommand())
            {
                vCmd.CommandText = "SELECT COUNT(*), COUNT(*) FILTER (WHERE slip_issued = TRUE) FROM polling.voters WHERE candidate_id = @cid;";
                var p = vCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; vCmd.Parameters.Add(p);
                await using var vReader = await vCmd.ExecuteReaderAsync(token);
                if (await vReader.ReadAsync(token))
                {
                    voterCount = vReader.GetInt32(0);
                    slipsIssuedCount = vReader.GetInt32(1);
                }
            }

            // 5. Total Form-8 center votes
            int totalVotes = 0;
            await using (var rCmd = conn.CreateCommand())
            {
                rCmd.CommandText = @"
                    SELECT COALESCE(SUM(d.votes), 0)
                    FROM results.details d
                    JOIN election.candidate_elections ce ON d.candidate_election_id = ce.candidate_election_id
                    WHERE ce.candidate_id = @cid;";
                var p = rCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; rCmd.Parameters.Add(p);
                var res = await rCmd.ExecuteScalarAsync(token);
                if (res != null) totalVotes = Convert.ToInt32(res, CultureInfo.InvariantCulture);
            }

            candidateList.Add(new MasterCandidateOverviewItem(
                c.CandId,
                c.ElecId,
                c.ElecName ?? "",
                c.Name,
                c.SymBn ?? c.SymEn ?? "",
                c.Emoji ?? "🗳️",
                c.Party ?? "স্বতন্ত্র",
                c.Slogan ?? "",
                c.Phone,
                c.Office,
                primaryUsername,
                primaryDisplayName,
                teamCount,
                agentCount,
                voterCount,
                slipsIssuedCount,
                voterCount > 0 ? (int)Math.Round((double)slipsIssuedCount * 100 / voterCount) : 0,
                totalVotes
            ));
        }

        return Ok(candidateList);
    }
}

// =========================================================================
// DATA TRANSFER RECORDS
// =========================================================================

public sealed record ElectionSymbolSummary(int Id, string Code, string NameBn, string NameEn, string Category, string IconEmoji);

public sealed record CandidateWarRoomHero(
    Guid CandidateId,
    Guid AssignmentId,
    string Name,
    string PositionName,
    int? SymbolId,
    string? SymbolNameBn,
    string? SymbolNameEn,
    string SymbolEmoji,
    string PartyName,
    string Slogan,
    string? Phone,
    string? CampaignOffice);

public sealed record CandidateWarRoomSummary(
    Guid ElectionId,
    string ElectionName,
    DateOnly ElectionDate,
    string AreaName,
    CandidateWarRoomHero? Candidate,
    int TotalCenters,
    int VerifiedCenters,
    int TotalBooths,
    int AssignedAgents,
    int TotalTeams,
    int TotalFieldMembers,
    int OpenTasks,
    int TotalEvents,
    decimal EcCeiling,
    decimal TotalCommittedExpenses,
    decimal RemainingBudget);

public sealed record UpdateCampaignDetailsRequest(
    int? SymbolId,
    [MaxLength(150)] string? PartyName,
    [MaxLength(300)] string? Slogan,
    [MaxLength(30)] string? Phone,
    [MaxLength(300)] string? CampaignOffice);

public sealed record CandidateBoothAgentSummary(
    Guid BoothAgentId,
    Guid CenterId,
    string CenterName,
    string CenterCode,
    Guid BoothId,
    string BoothCode,
    string BoothName,
    Guid CandidateId,
    string CandidateName,
    string AgentType,
    string FullName,
    string NidNumber,
    string Phone,
    string? VoterNumber,
    string? PhotoUrl,
    bool AppointmentLetterIssued,
    DateTimeOffset? CheckedInAtBooth,
    string Status,
    string? Notes,
    DateTimeOffset CreatedAtUtc);

public sealed record CreateBoothAgentRequest(
    Guid CenterId,
    Guid BoothId,
    Guid CandidateId,
    string AgentType,
    [Required, MaxLength(150)] string FullName,
    [Required, MaxLength(30)] string NidNumber,
    [Required, MaxLength(20)] string Phone,
    [MaxLength(50)] string? VoterNumber,
    [MaxLength(500)] string? Notes);

public sealed record UpdateBoothAgentRequest(
    [Required, MaxLength(150)] string FullName,
    [Required, MaxLength(30)] string NidNumber,
    [Required, MaxLength(20)] string Phone,
    [MaxLength(50)] string? VoterNumber,
    string AgentType,
    string Status,
    bool AppointmentLetterIssued,
    [MaxLength(500)] string? Notes);

public sealed record CandidateCenterResultItem(
    Guid ElectionCenterId,
    Guid CenterId,
    string CenterCode,
    string CenterName,
    int CandidateVotes,
    int RunnerUpVotes,
    int Margin,
    bool IsCounted,
    bool Form8Verified,
    DateTimeOffset? ReportedAtUtc);

public sealed record CandidateElectionResultsSummary(
    Guid CandidateId,
    string CandidateName,
    string CandidateSymbol,
    string CandidateSymbolEmoji,
    string RunnerUpName,
    string RunnerUpSymbol,
    string RunnerUpSymbolEmoji,
    int TotalCenters,
    int CountedCenters,
    int RemainingCenters,
    int CandidateTotalVotes,
    int RunnerUpTotalVotes,
    int LeadMargin,
    bool IsLeading,
    IReadOnlyList<CandidateCenterResultItem> CenterResults,
    IReadOnlyList<CandidateTallyItemDto>? AllCandidateTallies = null);

public sealed record CandidateTallyItemDto(
    Guid CandidateId,
    string Name,
    string PartyName,
    string SymbolEmoji,
    string SymbolName,
    int TotalVotes,
    decimal VotePercentage,
    bool IsPrimary);

public sealed record CreateOpponentCandidateRequest(
    [Required, MaxLength(200)] string Name,
    [Required, MaxLength(150)] string PartyName,
    int? SymbolId = null,
    string? Slogan = null,
    string? Phone = null);

public sealed record QuickResultSubmissionRequest(
    Guid ElectionCenterId,
    int CandidateVotes,
    int RunnerUpVotes,
    string? Notes);

public sealed record EcCategoryScheduleItem(
    string NameBn,
    string NameEn,
    decimal AllocatedAmount,
    decimal SpentAmount,
    decimal RemainingAmount,
    int VoucherCount);

public sealed record EcExpenseScheduleReport(
    decimal EcCeiling,
    decimal TotalCommitted,
    decimal RemainingBudget,
    double UtilizationPercentage,
    bool IsWithinCeiling,
    IReadOnlyList<EcCategoryScheduleItem> Categories);

public sealed record CandidateVoterSummary(
    Guid Id,
    Guid CenterId,
    string CenterName,
    string CenterCode,
    Guid? BoothId,
    string? BoothCode,
    string? BoothName,
    string VoterNumber,
    int SerialNumber,
    string FullName,
    string? FatherOrSpouseName,
    string Gender,
    int? Age,
    string? AreaName,
    string Category,
    bool SlipIssued,
    bool HasVoted,
    string? Phone,
    string? Notes,
    DateTimeOffset CreatedAtUtc,
    Guid? CandidateId = null);

public sealed record CreateVoterRequest(
    Guid CenterId,
    Guid? BoothId,
    [Required, MaxLength(50)] string VoterNumber,
    int SerialNumber,
    [Required, MaxLength(150)] string FullName,
    [MaxLength(150)] string? FatherOrSpouseName,
    string? Gender,
    int? Age,
    [MaxLength(150)] string? AreaName,
    string? Category,
    [MaxLength(20)] string? Phone,
    [MaxLength(500)] string? Notes);

public sealed record UpdateVoterRequest(
    Guid CenterId,
    Guid? BoothId,
    [Required, MaxLength(50)] string VoterNumber,
    int SerialNumber,
    [Required, MaxLength(150)] string FullName,
    [MaxLength(150)] string? FatherOrSpouseName,
    string? Gender,
    int? Age,
    [MaxLength(150)] string? AreaName,
    string? Category,
    [MaxLength(20)] string? Phone,
    [MaxLength(500)] string? Notes,
    bool SlipIssued,
    bool HasVoted);

public sealed record BatchMarkSlipsRequest(
    List<Guid> VoterIds,
    bool SlipIssued);

public sealed record CandidateIncidentSummary(
    Guid Id,
    Guid CenterId,
    string CenterName,
    string CenterCode,
    Guid? BoothId,
    string? BoothCode,
    string? BoothName,
    string IncidentType,
    string Severity,
    string Title,
    string Description,
    string ReportedBy,
    string? ReportedByPhone,
    DateTimeOffset ReportedAt,
    string Status,
    string? EvidenceAttachmentUrl,
    string? MagistrateName,
    string? ActionTaken,
    bool OfficialComplaintGenerated,
    DateTimeOffset CreatedAtUtc);

public sealed record CreateIncidentRequest(
    Guid CenterId,
    Guid? BoothId,
    [Required, MaxLength(50)] string IncidentType,
    [Required, MaxLength(20)] string Severity,
    [Required, MaxLength(200)] string Title,
    [Required] string Description,
    [Required, MaxLength(150)] string ReportedBy,
    [MaxLength(30)] string? ReportedByPhone,
    [MaxLength(500)] string? EvidenceAttachmentUrl);

public sealed record UpdateIncidentStatusRequest(
    [Required, MaxLength(30)] string Status,
    string? ActionTaken,
    string? MagistrateName,
    bool? OfficialComplaintGenerated);

public sealed record CandidateBroadcastLogItem(
    Guid BroadcastId,
    string Channel,
    string TemplateType,
    int RecipientCount,
    string Status,
    DateTimeOffset SentAt);

public sealed record SmsGatewayConfigDto(
    Guid ConfigId,
    string Provider,
    string ApiKey,
    string? ApiSecret,
    string SenderId,
    string? EndpointUrl,
    bool IsActive,
    decimal Balance,
    DateTimeOffset? LastTestedAt,
    DateTimeOffset UpdatedAt);

public sealed record UpdateSmsGatewayConfigRequest(
    [Required] string Provider,
    [Required] string ApiKey,
    string? ApiSecret,
    string? SenderId,
    string? EndpointUrl,
    bool IsActive);

public sealed record TestSmsRequest(
    [Required] string Phone,
    string? Message,
    string? ApiKey = null,
    string? SenderId = null,
    string? Provider = null,
    string? EndpointUrl = null);

public sealed record SendVoterBroadcastRequest(
    [Required] string Channel,
    string? TargetFilter,
    Guid? TargetCenterId,
    string? TemplateType,
    [Required] string MessageContent,
    Guid? CandidateId = null);

public sealed record VoterQueueItem(
    Guid VoterId,
    string FullName,
    string Phone,
    int SerialNumber,
    string VoterNumber,
    string CenterName,
    string BoothName,
    string Message,
    string WhatsAppWebUrl);

public sealed record SendVoterBroadcastResponse(
    bool Success,
    Guid BroadcastId,
    int RecipientCount,
    string Channel,
    string Status,
    string Message,
    IReadOnlyList<VoterQueueItem> Queue);

public sealed record WhatsAppAutoBroadcastRequest(
    IReadOnlyList<WhatsAppQueueItemDto> Items);

public sealed record WhatsAppQueueItemDto(
    Guid? Id,
    string? Name,
    string Phone,
    string Message);

public sealed record CandidateTeamUserItem(
    Guid UserId,
    string Username,
    string DisplayName,
    string? Email,
    string? Phone,
    string Role,
    bool IsActive,
    DateTimeOffset CreatedAtUtc);

public sealed record CreateCandidateTeamUserRequest(
    [Required, MaxLength(100)] string Username,
    [Required, MaxLength(150)] string DisplayName,
    [MaxLength(150)] string? Email,
    [MaxLength(20)] string? Phone,
    [Required, MinLength(6)] string Password,
    [MaxLength(50)] string? Role,
    Guid? CandidateId);

public sealed record ToggleUserStatusRequest(bool IsActive);

public sealed record ResetPasswordRequest([Required, MinLength(6)] string NewPassword);

public sealed record MasterCandidateOverviewItem(
    Guid CandidateId,
    Guid ElectionId,
    string ElectionName,
    string CandidateName,
    string SymbolName,
    string SymbolEmoji,
    string PartyName,
    string Slogan,
    string? Phone,
    string? CampaignOffice,
    string? PrimaryUsername,
    string? PrimaryDisplayName,
    int TeamCount,
    int AgentCount,
    int VoterCount,
    int SlipsIssuedCount,
    int SlipPercentage,
    int TotalVotes);
