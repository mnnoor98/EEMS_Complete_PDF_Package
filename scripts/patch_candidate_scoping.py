# -*- coding: utf-8 -*-
import re

file_path = 'backend/src/EEMS.Api/Controllers/CandidatePortalController.cs'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update GetWarRoom signature and scoping
old_war_room = '''    [HttpGet("elections/{electionId:guid}/war-room")]
    [Authorize(Policy = PermissionCodes.ElectionsRead)]
    public async Task<ActionResult<CandidateWarRoomSummary>> GetWarRoom(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var election = await electionsDb.Elections.SingleOrDefaultAsync(x => x.TenantId == tenantId && x.Id == electionId, token);
        if (election is null) return NotFound(new { error = "election_not_found" });

        var area = await geographyDb.Areas.SingleOrDefaultAsync(x => x.Id == election.AreaId, token);
        var areaName = area != null ? (area.NameEn ?? area.NameBn) : $"Area {election.AreaId}";

        // Get candidate assignment
        var assignment = await candidatesDb.CandidateElections
            .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.ElectionId == electionId && x.IsActive, token);'''

new_war_room = '''    [HttpGet("elections/{electionId:guid}/war-room")]
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
        }'''

assert old_war_room in text, "old_war_room not found"
text = text.replace(old_war_room, new_war_room, 1)
print("1. GetWarRoom patched successfully!")

# 2. Update GetResultsSummary signature and scoping
old_results = '''    [HttpGet("elections/{electionId:guid}/results-summary")]
    [Authorize(Policy = PermissionCodes.ResultsRead)]
    public async Task<ActionResult<CandidateElectionResultsSummary>> GetResultsSummary(Guid electionId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;

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
                SymbolName = s != null ? s.NameBn : "প্রতীক",
                SymbolEmoji = s != null ? s.IconEmoji : "🗳️"
            }
        ).ToListAsync(token);

        if (candidates.Count == 0) return NotFound(new { error = "no_candidates_for_election" });

        var primaryCandidate = candidates[0];
        var runnerUpCandidate = candidates.Count > 1 ? candidates[1] : null;'''

new_results = '''    [HttpGet("elections/{electionId:guid}/results-summary")]
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
                SymbolName = s != null ? s.NameBn : "প্রতীক",
                SymbolEmoji = s != null ? s.IconEmoji : "🗳️"
            }
        ).ToListAsync(token);

        if (candidates.Count == 0) return NotFound(new { error = "no_candidates_for_election" });

        var primaryCandidate = (targetCandidateId.HasValue 
            ? candidates.FirstOrDefault(c => c.CandidateId == targetCandidateId.Value) 
            : null) ?? candidates[0];

        var runnerUpCandidate = candidates.FirstOrDefault(c => c.CandidateElectionId != primaryCandidate.CandidateElectionId);'''

assert old_results in text, "old_results not found"
text = text.replace(old_results, new_results, 1)
print("2. GetResultsSummary patched successfully!")

# 3. Update GetBoothAgents signature and scoping
old_agents = '''    [HttpGet("elections/{electionId:guid}/booth-agents")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateBoothAgentSummary>>> GetBoothAgents(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] string? status,
        [FromQuery] string? agentType,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var query = from agent in pollingDb.BoothAgents
                    join center in pollingDb.Centers on agent.CenterId equals center.Id
                    join booth in pollingDb.Booths on agent.BoothId equals booth.Id
                    where agent.TenantId == tenantId && agent.ElectionId == electionId
                    select new { agent, center, booth };'''

new_agents = '''    [HttpGet("elections/{electionId:guid}/booth-agents")]
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
        }'''

assert old_agents in text, "old_agents not found"
text = text.replace(old_agents, new_agents, 1)
print("3. GetBoothAgents patched successfully!")

# 4. Update GetVoters signature and scoping
old_voters = '''    [HttpGet("elections/{electionId:guid}/voters")]
    [Authorize(Policy = PermissionCodes.PollingRead)]
    public async Task<ActionResult<IReadOnlyList<CandidateVoterSummary>>> GetVoters(
        Guid electionId,
        [FromQuery] Guid? centerId,
        [FromQuery] string? category,
        [FromQuery] bool? slipIssued,
        [FromQuery] string? search,
        CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        var query = pollingDb.Voters.Where(x => x.TenantId == tenantId && x.ElectionId == electionId);'''

new_voters = '''    [HttpGet("elections/{electionId:guid}/voters")]
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
        }'''

assert old_voters in text, "old_voters not found"
text = text.replace(old_voters, new_voters, 1)
print("4. GetVoters patched successfully!")

# 5. Update CreateVoter to pass candidateId
old_create_voter = '''        var voter = Voter.Create(
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
            request.Notes?.Trim());'''

new_create_voter = '''        var (userCandidateId, isSuperAdmin) = GetUserCandidateScope();
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
            userCandidateId);'''

if old_create_voter in text:
    text = text.replace(old_create_voter, new_create_voter, 1)
    print("5. CreateVoter patched successfully!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("All backend candidate scoping updates saved successfully!")

