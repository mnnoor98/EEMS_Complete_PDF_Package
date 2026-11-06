# -*- coding: utf-8 -*-
with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update CandidateElectionResultsSummary record to include AllCandidateTallies
old_summary_record = '''public sealed record CandidateElectionResultsSummary(
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
    IReadOnlyList<CandidateCenterResultItem> CenterResults);'''

new_summary_record = '''public sealed record CandidateElectionResultsSummary(
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
    string? Phone = null);'''

assert old_summary_record in text, 'old_summary_record not found'
text = text.replace(old_summary_record, new_summary_record, 1)
print('1. Records updated!')

# 2. Update GetResultsSummary to calculate allCandidateTallies and return them
old_return_summary = '''        var leadMargin = totalCandidateVotes - totalRunnerUpVotes;

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
            centerResults));'''

new_return_summary = '''        var leadMargin = totalCandidateVotes - totalRunnerUpVotes;

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
            allTallies));'''

assert old_return_summary in text, 'old_return_summary not found'
text = text.replace(old_return_summary, new_return_summary, 1)
print('2. GetResultsSummary updated with tallies!')

# 3. Add CreateOpponentCandidate and RemoveOpponentCandidate endpoints after SubmitQuickResult
target_quick_result_end = '''        resultsDb.Details.AddRange(details);
        await resultsDb.SaveChangesAsync(token);

        return Ok(new { success = true, submissionId = submission.Id, declaredVotes = totalVotes });
    }'''

opponent_endpoints = '''        resultsDb.Details.AddRange(details);
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
            candidate.Name,
            request.PartyName,
            sym?.NameBn ?? "প্রতীক",
            sym?.NameEn ?? "Symbol",
            sym?.IconEmoji ?? "🗳️",
            sym?.Category ?? "GENERAL",
            candidate.Slogan,
            candidate.Phone,
            null,
            null,
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
    }'''

assert target_quick_result_end in text, 'target_quick_result_end not found'
text = text.replace(target_quick_result_end, opponent_endpoints, 1)
print('3. Opponent endpoints added!')

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print('All patches written cleanly!')

