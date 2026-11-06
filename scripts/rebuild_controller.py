# -*- coding: utf-8 -*-
"""
Rebuilds CandidatePortalController.cs cleanly with all endpoints:
1. Base candidate & election operations
2. Polling booth agents & appointment letters
3. Form-8 center results & opponent candidates
4. EC expense vouchers & ceiling
5. Voters management, QR/Excel/PDF import & slips
6. Incidents & magistrate complaints
7. Broadcast outbox logs
8. SMS Gateway Config, Test & Live Balance Sync (SMS.NET.BD with real key)
9. Bulk voter broadcast (SMS + WhatsApp with case-insensitive target filters)
10. WhatsApp QR Auto-Bot integration (camelCase JSON payload)
11. Candidate Team & Sub-Users (iam.users + iam.tenant_users with candidate_id)
12. Super Admin Master Candidate Overview Hub (/api/v1/candidate/master-overview)
"""
import os

controller_path = 'backend/src/EEMS.Api/Controllers/CandidatePortalController.cs'

code = '''using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using System.Text.Json;
using EEMS.Api.Authorization;
using EEMS.Modules.Candidates.Domain;
using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Events.Infrastructure;
using EEMS.Modules.Finance.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Identity.Security;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Results.Domain;
using EEMS.Modules.Results.Infrastructure;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
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
    IPasswordHasher<EEMS.Modules.Identity.Domain.User> passwordHasher) : ControllerBase
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

    [HttpGet("candidates")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateWarRoomHero>>> GetAllCandidates(CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var assignments = await candidatesDb.CandidateElections
            .Where(x => x.TenantId == tenantId)
            .ToListAsync(token);

        var candidateIds = assignments.Select(x => x.CandidateId).Distinct().ToList();
        var candidates = await candidatesDb.Candidates
            .Where(x => x.TenantId == tenantId && candidateIds.Contains(x.Id))
            .ToDictionaryAsync(x => x.Id, token);

        var symbolIds = assignments.Where(x => x.SymbolId.HasValue).Select(x => x.SymbolId!.Value).Distinct().ToList();
        var symbols = await candidatesDb.Symbols
            .Where(s => symbolIds.Contains(s.Id))
            .ToDictionaryAsync(s => s.Id, token);

        var list = new List<CandidateWarRoomHero>();
        foreach (var a in assignments)
        {
            if (!candidates.TryGetValue(a.CandidateId, out var c)) continue;
            symbols.TryGetValue(a.SymbolId ?? -1, out var sym);

            list.Add(new CandidateWarRoomHero(
                c.Id,
                a.Id,
                c.Name,
                c.PositionName,
                a.SymbolId,
                sym?.NameBn,
                sym?.NameEn,
                sym?.IconEmoji ?? "🗳️",
                a.PartyName ?? "স্বতন্ত্র",
                a.Slogan ?? string.Empty,
                c.Phone,
                c.CampaignOffice
            ));
        }

        return Ok(list);
    }

    [HttpGet("elections/{electionId:guid}/war-room")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<CandidateWarRoomSummary>> GetWarRoom(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == electionId, token);
        if (election is null) return NotFound(new { error = "election_not_found" });

        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        CandidateElection? assignment = null;

        if (userCandidateId.HasValue)
        {
            assignment = await candidatesDb.CandidateElections
                .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == userCandidateId.Value, token);
        }

        if (assignment is null)
        {
            assignment = await candidatesDb.CandidateElections
                .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
                .OrderBy(x => x.CreatedAtUtc)
                .FirstOrDefaultAsync(token);
        }

        CandidateWarRoomHero? hero = null;
        if (assignment is not null)
        {
            var candidate = await candidatesDb.Candidates
                .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == assignment.CandidateId, token);

            if (candidate is not null)
            {
                ElectionSymbol? symbol = null;
                if (assignment.SymbolId.HasValue)
                {
                    symbol = await candidatesDb.Symbols.SingleOrDefaultAsync(s => s.Id == assignment.SymbolId.Value, token);
                }

                hero = new CandidateWarRoomHero(
                    candidate.Id,
                    assignment.Id,
                    candidate.Name,
                    candidate.PositionName,
                    assignment.SymbolId,
                    symbol?.NameBn,
                    symbol?.NameEn,
                    symbol?.IconEmoji ?? "🗳️",
                    assignment.PartyName ?? "স্বতন্ত্র",
                    assignment.Slogan ?? string.Empty,
                    candidate.Phone,
                    candidate.CampaignOffice);
            }
        }

        var totalCenters = await pollingDb.Centers.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId, token);
        var verifiedCenters = await pollingDb.Centers.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.Status == "VERIFIED", token);
        var totalBooths = await pollingDb.Booths.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId, token);

        var targetCandidateId = assignment?.CandidateId ?? userCandidateId;
        var assignedAgents = 0;
        if (targetCandidateId.HasValue)
        {
            assignedAgents = await pollingDb.BoothAgents.CountAsync(
                x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == targetCandidateId.Value, token);
        }

        var totalTeams = await teamsDb.Teams.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId, token);
        var totalFieldMembers = await teamsDb.Members.CountAsync(x => x.TenantId == tenantId, token);
        var openTasks = await teamsDb.Tasks.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.Status != "COMPLETED", token);
        var totalEvents = await eventsDb.Events.CountAsync(x => x.TenantId == tenantId && x.ElectionId == electionId, token);

        decimal ecCeiling = 2500000m;
        var totalCommittedExpenses = await financeDb.Vouchers
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId && x.Status != "REJECTED")
            .SumAsync(x => (decimal?)x.Amount, token) ?? 0m;
        var remainingBudget = Math.Max(0m, ecCeiling - totalCommittedExpenses);

        return Ok(new CandidateWarRoomSummary(
            election.Id,
            election.Name,
            election.ElectionDate,
            "দাগনভূঞা, ফেনী",
            hero,
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
            remainingBudget));
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
        var assignment = await candidatesDb.CandidateElections
            .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == candidateId, token);
        if (assignment is null) return NotFound(new { error = "candidate_election_not_found" });

        var candidate = await candidatesDb.Candidates
            .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == candidateId, token);
        if (candidate is null) return NotFound(new { error = "candidate_not_found" });

        assignment.UpdateCampaignDetails(request.SymbolId, request.PartyName, request.Slogan);
        candidate.UpdateContactDetails(request.Phone, request.CampaignOffice);

        await candidatesDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 2. POLLING AGENTS
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/booth-agents")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBoothAgentSummary>>> GetBoothAgents(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] Guid? boothId,
        [FromQuery] Guid? candidateId,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var targetCandidateId = userCandidateId ?? candidateId;

        var query = pollingDb.BoothAgents
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (targetCandidateId.HasValue)
        {
            query = query.Where(x => x.CandidateId == targetCandidateId.Value);
        }

        if (centerId.HasValue) query = query.Where(x => x.CenterId == centerId.Value);
        if (boothId.HasValue) query = query.Where(x => x.BoothId == boothId.Value);

        var agents = await query.OrderBy(x => x.CreatedAtUtc).ToListAsync(token);
        if (agents.Count == 0) return Ok(Array.Empty<CandidateBoothAgentSummary>());

        var centerIds = agents.Select(x => x.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers
            .Where(x => x.TenantId == tenantId && centerIds.Contains(x.Id))
            .ToDictionaryAsync(x => x.Id, token);

        var boothIds = agents.Select(x => x.BoothId).Distinct().ToList();
        var booths = await pollingDb.Booths
            .Where(x => x.TenantId == tenantId && boothIds.Contains(x.Id))
            .ToDictionaryAsync(x => x.Id, token);

        var candIds = agents.Select(x => x.CandidateId).Distinct().ToList();
        var candidates = await candidatesDb.Candidates
            .Where(x => x.TenantId == tenantId && candIds.Contains(x.Id))
            .ToDictionaryAsync(x => x.Id, token);

        var list = agents.Select(a =>
        {
            centers.TryGetValue(a.CenterId, out var c);
            booths.TryGetValue(a.BoothId, out var b);
            candidates.TryGetValue(a.CandidateId, out var cand);

            return new CandidateBoothAgentSummary(
                a.Id,
                a.CenterId,
                c?.Name ?? string.Empty,
                c?.Code ?? string.Empty,
                a.BoothId,
                b?.Code ?? string.Empty,
                b?.Name ?? string.Empty,
                a.CandidateId,
                cand?.Name ?? string.Empty,
                a.AgentType,
                a.FullName,
                a.NidNumber,
                a.Phone,
                a.VoterNumber,
                a.PhotoUrl,
                a.AppointmentLetterIssued,
                a.CheckedInAtBooth,
                a.Status,
                a.Notes,
                a.CreatedAtUtc);
        }).ToList();

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
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var effectiveCandidateId = userCandidateId ?? request.CandidateId;

        var center = await pollingDb.Centers.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == request.CenterId, token);
        if (center is null) return NotFound(new { error = "center_not_found" });

        var booth = await pollingDb.Booths.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == request.BoothId, token);
        if (booth is null) return NotFound(new { error = "booth_not_found" });

        var candidate = await candidatesDb.Candidates.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.Id == effectiveCandidateId, token);
        if (candidate is null) return NotFound(new { error = "candidate_not_found" });

        var existingInBooth = await pollingDb.BoothAgents.AnyAsync(
            x => x.TenantId == tenantId &&
                 x.ElectionId == electionId &&
                 x.BoothId == request.BoothId &&
                 x.CandidateId == effectiveCandidateId &&
                 x.AgentType == request.AgentType &&
                 x.Status == "ACTIVE",
            token);

        if (existingInBooth)
        {
            return Conflict(new { error = "agent_slot_already_filled", message = "এই বুথে উক্ত প্রার্থীর এই পদের সক্রিয় এজেন্ট ইতিমধ্যেই নিয়োগপ্রাপ্ত আছেন।" });
        }

        var agent = BoothAgent.Create(
            tenantId,
            electionId,
            request.CenterId,
            request.BoothId,
            effectiveCandidateId,
            request.AgentType,
            request.FullName,
            request.NidNumber,
            request.Phone,
            request.VoterNumber,
            request.Notes);

        pollingDb.BoothAgents.Add(agent);
        await pollingDb.SaveChangesAsync(token);

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

    [HttpPost("elections/{electionId:guid}/booth-agents/{agentId:guid}/issue-letter")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> IssueAppointmentLetter(Guid electionId, Guid agentId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var agent = await pollingDb.BoothAgents.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == agentId, token);
        if (agent is null) return NotFound(new { error = "agent_not_found" });

        agent.IssueAppointmentLetter();
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpDelete("elections/{electionId:guid}/booth-agents/{agentId:guid}")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> DeleteBoothAgent(Guid electionId, Guid agentId, CancellationToken token)
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
    // 3. RESULTS & FORM-8 TALLIES
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
        var targetCandidateId = userCandidateId ?? candidateId;

        CandidateElection? mainAssignment = null;
        if (targetCandidateId.HasValue)
        {
            mainAssignment = await candidatesDb.CandidateElections
                .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.CandidateId == targetCandidateId.Value, token);
        }

        if (mainAssignment is null)
        {
            mainAssignment = await candidatesDb.CandidateElections
                .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
                .OrderBy(x => x.CreatedAtUtc)
                .FirstOrDefaultAsync(token);
        }

        if (mainAssignment is null)
        {
            return NotFound(new { error = "no_candidate_for_election" });
        }

        var mainCandidate = await candidatesDb.Candidates.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == mainAssignment.CandidateId, token);
        var mainSymbol = mainAssignment.SymbolId.HasValue ? await candidatesDb.Symbols.SingleOrDefaultAsync(s => s.Id == mainAssignment.SymbolId.Value, token) : null;

        var allCenters = await pollingDb.Centers
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
            .OrderBy(x => x.Code)
            .ToListAsync(token);

        var electionCenters = await resultsDb.ElectionCenters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId)
            .ToDictionaryAsync(x => x.CenterId, token);

        var details = await resultsDb.Details
            .Where(x => x.TenantId == tenantId)
            .ToListAsync(token);

        var centerResults = new List<CandidateCenterResultItem>();
        int candidateTotal = 0;
        int runnerUpTotal = 0;
        int countedCenters = 0;

        foreach (var c in allCenters)
        {
            electionCenters.TryGetValue(c.Id, out var ec);
            var ecId = ec?.Id ?? Guid.Empty;

            var candVotes = details.Where(d => d.CandidateElectionId == mainAssignment.Id && (ec == null || d.ElectionCenterId == ec.Id)).Sum(d => d.Votes);
            var otherVotes = details.Where(d => d.CandidateElectionId != mainAssignment.Id && (ec == null || d.ElectionCenterId == ec.Id))
                .GroupBy(d => d.CandidateElectionId)
                .Select(g => g.Sum(x => x.Votes))
                .DefaultIfEmpty(0)
                .Max();

            candidateTotal += candVotes;
            runnerUpTotal += otherVotes;
            if (candVotes > 0 || otherVotes > 0) countedCenters++;

            centerResults.Add(new CandidateCenterResultItem(
                ecId,
                c.Id,
                c.Code,
                c.Name,
                candVotes,
                otherVotes,
                candVotes - otherVotes,
                candVotes > 0 || otherVotes > 0,
                ec?.Form8Verified ?? false,
                ec?.ReportedAtUtc
            ));
        }

        int margin = candidateTotal - runnerUpTotal;
        return Ok(new CandidateElectionResultsSummary(
            mainCandidate?.Id ?? Guid.Empty,
            mainCandidate?.Name ?? "প্রার্থী",
            mainSymbol?.NameBn ?? "মার্কা",
            mainSymbol?.IconEmoji ?? "⚖️",
            "নিকটতম প্রতিদ্বন্দ্বী",
            "লাঙ্গল",
            "🚜",
            allCenters.Count,
            countedCenters,
            Math.Max(0, allCenters.Count - countedCenters),
            candidateTotal,
            runnerUpTotal,
            margin,
            margin >= 0,
            centerResults
        ));
    }

    [HttpPost("elections/{electionId:guid}/quick-result")]
    [Authorize(Policy = PermissionCodes.ResultsManage)]
    public async Task<IActionResult> SubmitQuickResult(
        Guid electionId,
        [FromBody] QuickResultSubmissionRequest request,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var ec = await resultsDb.ElectionCenters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == request.ElectionCenterId, token);
        if (ec is null) return NotFound(new { error = "election_center_not_found" });

        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
        var mainAssignment = await candidatesDb.CandidateElections
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId && (userCandidateId == null || x.CandidateId == userCandidateId.Value))
            .FirstOrDefaultAsync(token);
        if (mainAssignment is null) return BadRequest(new { error = "candidate_assignment_not_found" });

        var detail = await resultsDb.Details.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionCenterId == ec.Id && x.CandidateElectionId == mainAssignment.Id, token);

        if (detail is null)
        {
            detail = ResultDetail.Create(tenantId, ec.Id, mainAssignment.Id, request.CandidateVotes);
            resultsDb.Details.Add(detail);
        }
        else
        {
            detail.UpdateVotes(request.CandidateVotes);
        }

        ec.MarkReported();
        await resultsDb.SaveChangesAsync(token);
        return NoContent();
    }

    // =========================================================================
    // 4. EC EXPENSES & CEILING
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/expenses/ec-schedule")]
    [Authorize(Policy = PermissionCodes.FinanceRead)]
    public async Task<ActionResult<EcExpenseScheduleReport>> GetEcExpenseSchedule(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        decimal ceiling = 2500000m;

        var vouchers = await financeDb.Vouchers
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId && x.Status != "REJECTED")
            .ToListAsync(token);

        decimal totalCommitted = vouchers.Sum(x => x.Amount);
        decimal remaining = Math.Max(0m, ceiling - totalCommitted);
        double utilization = ceiling > 0 ? (double)(totalCommitted / ceiling) * 100 : 0.0;

        var cats = new List<EcCategoryScheduleItem>
        {
            new("জনসভা ও পথসমাবেশ মঞ্চ নির্মাণ", "Public Meetings & Stages", 500000m, vouchers.Where(v => v.ReferenceNumber?.Contains("MEET") == true).Sum(v => v.Amount), 500000m, vouchers.Count),
            new("মুদ্রণ সামগ্রী (পোস্টার, লিফলেট, স্লিপ)", "Printing & Materials", 800000m, vouchers.Where(v => v.ReferenceNumber?.Contains("PRINT") == true).Sum(v => v.Amount), 800000m, vouchers.Count),
            new("মাইকিং ও ডিজিটাল প্রচারণা", "Miking & Digital Ads", 400000m, vouchers.Where(v => v.ReferenceNumber?.Contains("MIKE") == true).Sum(v => v.Amount), 400000m, vouchers.Count),
            new("পোলিং এজেন্ট প্রশিক্ষণ ও আপ্যায়ন", "Agent Training & Food", 500000m, vouchers.Where(v => v.ReferenceNumber?.Contains("FOOD") == true).Sum(v => v.Amount), 500000m, vouchers.Count),
            new("নির্বাচনী ক্যাম্প অফিস ও পরিবহন", "Camp Office & Transport", 300000m, vouchers.Where(v => v.ReferenceNumber?.Contains("OFFICE") == true).Sum(v => v.Amount), 300000m, vouchers.Count)
        };

        return Ok(new EcExpenseScheduleReport(
            ceiling,
            totalCommitted,
            remaining,
            utilization,
            totalCommitted <= ceiling,
            cats
        ));
    }

    // =========================================================================
    // 5. VOTERS & SMART VOTER SLIP ISSUANCE
    // =========================================================================

    [HttpGet("elections/{electionId:guid}/voters")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateVoterSummary>>> GetVoters(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] Guid? boothId,
        [FromQuery] bool? slipIssued,
        [FromQuery] bool? hasVoted,
        [FromQuery] string? search,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();

        var query = pollingDb.Voters.Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (userCandidateId.HasValue)
        {
            query = query.Where(x => x.CandidateId == null || x.CandidateId == userCandidateId.Value);
        }

        if (centerId.HasValue) query = query.Where(x => x.CenterId == centerId.Value);
        if (boothId.HasValue) query = query.Where(x => x.BoothId == boothId.Value);
        if (slipIssued.HasValue) query = query.Where(x => x.SlipIssued == slipIssued.Value);
        if (hasVoted.HasValue) query = query.Where(x => x.HasVoted == hasVoted.Value);

        if (!string.IsNullOrWhiteSpace(search))
        {
            var s = search.Trim().ToLowerInvariant();
            query = query.Where(x =>
                x.FullName.ToLower().Contains(s) ||
                x.VoterNumber.ToLower().Contains(s) ||
                (x.Phone != null && x.Phone.Contains(s)) ||
                (x.AreaName != null && x.AreaName.ToLower().Contains(s)));
        }

        var voters = await query.OrderBy(x => x.SerialNumber).ToListAsync(token);
        if (voters.Count == 0) return Ok(Array.Empty<CandidateVoterSummary>());

        var centerIds = voters.Select(x => x.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(x => centerIds.Contains(x.Id)).ToDictionaryAsync(x => x.Id, token);
        var boothIds = voters.Where(x => x.BoothId.HasValue).Select(x => x.BoothId!.Value).Distinct().ToList();
        var booths = await pollingDb.Booths.Where(x => boothIds.Contains(x.Id)).ToDictionaryAsync(x => x.Id, token);

        var list = voters.Select(v =>
        {
            centers.TryGetValue(v.CenterId, out var c);
            booths.TryGetValue(v.BoothId ?? Guid.Empty, out var b);

            return new CandidateVoterSummary(
                v.Id,
                v.CenterId,
                c?.Name ?? string.Empty,
                c?.Code ?? string.Empty,
                v.BoothId,
                b?.Code,
                b?.Name,
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
                v.CreatedAtUtc
            );
        }).ToList();

        return Ok(list);
    }

    [HttpPost("elections/{electionId:guid}/voters")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<CandidateVoterSummary>> CreateVoter(
        Guid electionId,
        [FromBody] CreateVoterRequest request,
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
            request.Gender?.Trim() ?? "M",
            request.Age,
            request.AreaName?.Trim(),
            request.Category?.Trim() ?? "GENERAL",
            request.Phone?.Trim(),
            request.Notes?.Trim(),
            userCandidateId);

        pollingDb.Voters.Add(voter);
        await pollingDb.SaveChangesAsync(token);

        var center = await pollingDb.Centers.SingleOrDefaultAsync(x => x.Id == request.CenterId, token);
        return Ok(new CandidateVoterSummary(
            voter.Id,
            voter.CenterId,
            center?.Name ?? "",
            center?.Code ?? "",
            voter.BoothId,
            null,
            null,
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
            voter.CreatedAtUtc
        ));
    }

    [HttpPost("elections/{electionId:guid}/voters/{voterId:guid}/toggle-slip")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> ToggleSlip(Guid electionId, Guid voterId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        voter.ToggleSlipIssued();
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/voters/{voterId:guid}/toggle-voted")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> ToggleVoted(Guid electionId, Guid voterId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var voter = await pollingDb.Voters.SingleOrDefaultAsync(
            x => x.TenantId == tenantId && x.ElectionId == electionId && x.Id == voterId, token);
        if (voter is null) return NotFound(new { error = "voter_not_found" });

        voter.ToggleHasVoted();
        await pollingDb.SaveChangesAsync(token);
        return NoContent();
    }

    [HttpPost("elections/{electionId:guid}/voters/batch-mark-slips")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<IActionResult> BatchMarkSlips(
        Guid electionId,
        [FromBody] BatchMarkSlipsRequest request,
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
        return NoContent();
    }

    // =========================================================================
    // 6. INCIDENTS & MAGISTRATE COMPLAINTS
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

        if (incidents.Count == 0) return Ok(Array.Empty<CandidateIncidentSummary>());

        var centerIds = incidents.Select(x => x.CenterId).Distinct().ToList();
        var centers = await pollingDb.Centers.Where(x => centerIds.Contains(x.Id)).ToDictionaryAsync(x => x.Id, token);

        return Ok(incidents.Select(i =>
        {
            centers.TryGetValue(i.CenterId, out var c);
            return new CandidateIncidentSummary(
                i.Id,
                i.CenterId,
                c?.Name ?? "ভোটকেন্দ্র",
                c?.Code ?? "",
                i.BoothId,
                null,
                null,
                i.IncidentType,
                i.Severity,
                i.Title,
                i.Description,
                i.ReportedBy,
                i.ReportedByPhone,
                i.ReportedAt,
                i.Status,
                i.EvidenceAttachmentUrl,
                i.MagistrateName,
                i.ActionTaken,
                i.OfficialComplaintGenerated,
                i.CreatedAtUtc
            );
        }).ToList());
    }

    [HttpPost("elections/{electionId:guid}/incidents")]
    [Authorize(Policy = PermissionCodes.PollingManage)]
    public async Task<ActionResult<CandidateIncidentSummary>> CreateIncident(
        Guid electionId,
        [FromBody] CreateIncidentRequest request,
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
        return Ok(new CandidateIncidentSummary(
            incident.Id,
            incident.CenterId,
            center?.Name ?? "ভোটকেন্দ্র",
            center?.Code ?? "",
            incident.BoothId,
            null,
            null,
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
            incident.CreatedAtUtc
        ));
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
            if (!string.IsNullOrWhiteSpace(apiKey) && (provider == "SMS_NET_BD" || endpointUrl?.Contains("sms.net.bd") == true))
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
                            if (decimal.TryParse(balStr, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var liveBal))
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
                if (string.IsNullOrWhiteSpace(provider) || provider == "SMS_NET_BD") provider = reader.GetString(0);
                if (string.IsNullOrWhiteSpace(endpointUrl) || endpointUrl == "https://api.sms.net.bd/sendsms") endpointUrl = reader.IsDBNull(3) ? "https://api.sms.net.bd/sendsms" : reader.GetString(3);
            }
        }

        // Auto-persist latest test configuration
        await using (var updCmd = conn.CreateCommand())
        {
            updCmd.CommandText = @"
                UPDATE campaign.sms_gateway_configs
                SET api_key = @key, sender_id = @sid, provider = @prov, endpoint_url = @ep, last_tested_at = NOW()
                WHERE tenant_id = @t AND election_id = @e;";
            var pT = updCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; updCmd.Parameters.Add(pT);
            var pE = updCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; updCmd.Parameters.Add(pE);
            var pK = updCmd.CreateParameter(); pK.ParameterName = "@key"; pK.Value = apiKey; updCmd.Parameters.Add(pK);
            var pS = updCmd.CreateParameter(); pS.ParameterName = "@sid"; pS.Value = senderId; updCmd.Parameters.Add(pS);
            var pP = updCmd.CreateParameter(); pP.ParameterName = "@prov"; pP.Value = provider; updCmd.Parameters.Add(pP);
            var pEp = updCmd.CreateParameter(); pEp.ParameterName = "@ep"; pEp.Value = endpointUrl; updCmd.Parameters.Add(pEp);
            await updCmd.ExecuteNonQueryAsync(token);
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
        var channel = (request.Channel ?? "WHATSAPP").Trim().ToUpperInvariant();
        var targetFilter = (request.TargetFilter ?? "ALL").Trim().ToUpperInvariant();

        // 1. Query voters matching scope
        var voterQuery = pollingDb.Voters
            .Where(x => x.TenantId == tenantId && x.ElectionId == electionId);

        if (userCandidateId.HasValue)
        {
            voterQuery = voterQuery.Where(x => x.CandidateId == null || x.CandidateId == userCandidateId.Value);
        }

        if (request.TargetCenterId.HasValue && request.TargetCenterId.Value != Guid.Empty)
        {
            voterQuery = voterQuery.Where(x => x.CenterId == request.TargetCenterId.Value);
        }

        if (targetFilter == "SUPPORTER" || targetFilter == "SUPPORTERS")
        {
            voterQuery = voterQuery.Where(x => x.Category == "SUPPORTER");
        }
        else if (targetFilter == "UNISSUED_SLIP" || targetFilter == "UNISSUED_SLIP_ONLY")
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
            .SingleOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && (userCandidateId == null || x.CandidateId == userCandidateId.Value), token);
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
                .Replace("{নাম}", v.FullName)
                .Replace("{ভোটারের নাম}", v.FullName)
                .Replace("{ভোটকেন্দ্র}", centerName)
                .Replace("{বুথ}", boothName)
                .Replace("{ক্রমিক}", v.SerialNumber.ToString(System.Globalization.CultureInfo.InvariantCulture))
                .Replace("{ভোটার নং}", v.VoterNumber)
                .Replace("{প্রার্থী}", candName)
                .Replace("{মার্কা}", candSymbol);

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
            if (gwProvider == "SMS_NET_BD" || gwEndpoint.Contains("sms.net.bd"))
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
                INSERT INTO campaign.broadcast_logs (broadcast_id, tenant_id, election_id, channel, template_type, recipient_count, status, sent_at)
                VALUES (@id, @t, @e, @ch, @tpl, @rc, @st, NOW());";
            var pId = insCmd.CreateParameter(); pId.ParameterName = "@id"; pId.Value = broadcastId; insCmd.Parameters.Add(pId);
            var pT = insCmd.CreateParameter(); pT.ParameterName = "@t"; pT.Value = tenantId; insCmd.Parameters.Add(pT);
            var pE = insCmd.CreateParameter(); pE.ParameterName = "@e"; pE.Value = electionId; insCmd.Parameters.Add(pE);
            var pCh = insCmd.CreateParameter(); pCh.ParameterName = "@ch"; pCh.Value = channel; insCmd.Parameters.Add(pCh);
            var pTpl = insCmd.CreateParameter(); pTpl.ParameterName = "@tpl"; pTpl.Value = templateType; insCmd.Parameters.Add(pTpl);
            var pRc = insCmd.CreateParameter(); pRc.ParameterName = "@rc"; pRc.Value = voters.Count; insCmd.Parameters.Add(pRc);
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
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
            var json = JsonSerializer.Serialize(request, CamelCaseJsonOptions);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            var response = await client.PostAsync("http://localhost:5140/api/whatsapp/broadcast", content, token);
            var resultStr = await response.Content.ReadAsStringAsync(token);
            return Content(resultStr, "application/json");
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

        var normalizedUsername = request.Username.Trim().ToLowerInvariant();
        if (await identityDb.Users.AnyAsync(u => u.ExternalSubject.ToLower() == normalizedUsername, token))
        {
            return Conflict(new { error = "username_exists", message = "এই ব্যবহারকারী আইডি (Username) ইতিমধ্যে ব্যবহৃত হচ্ছে। অন্য আইডি দিন।" });
        }

        var user = EEMS.Modules.Identity.Domain.User.Create(normalizedUsername, request.DisplayName.Trim(), request.Email?.Trim());
        identityDb.Users.Add(user);

        var tenantUser = TenantUser.Create(tenantId, user.Id, targetCandidateId.Value);
        identityDb.TenantUsers.Add(tenantUser);

        var hash = passwordHasher.HashPassword(user, request.Password.Trim());
        identityDb.PasswordCredentials.Add(PasswordCredential.Create(user.Id, hash, false));

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
            cred.UpdatePassword(newHash, false);
        }
        else
        {
            identityDb.PasswordCredentials.Add(PasswordCredential.Create(user.Id, newHash, false));
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
                if (res != null) teamCount = Convert.ToInt32(res);
            }

            // 3. Booth agents count
            int agentCount = 0;
            await using (var aCmd = conn.CreateCommand())
            {
                aCmd.CommandText = "SELECT COUNT(*) FROM polling.booth_agents WHERE candidate_id = @cid;";
                var p = aCmd.CreateParameter(); p.ParameterName = "@cid"; p.Value = c.CandId; aCmd.Parameters.Add(p);
                var res = await aCmd.ExecuteScalarAsync(token);
                if (res != null) agentCount = Convert.ToInt32(res);
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
                if (res != null) totalVotes = Convert.ToInt32(res);
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
    IReadOnlyList<CandidateCenterResultItem> CenterResults);

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
    DateTimeOffset CreatedAtUtc);

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
    [Required] string MessageContent);

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
'''

with open(controller_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"CandidatePortalController.cs successfully written ({len(code.splitlines())} lines)!")

