# -*- coding: utf-8 -*-
with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add PartyName to candidates query in GetResultsSummary
old_cand_select = '''            select new
            {
                CandidateElectionId = ce.Id,
                CandidateId = c.Id,
                Name = c.Name,
                SymbolName = s != null ? s.NameBn : "প্রতীক",
                SymbolEmoji = s != null ? s.IconEmoji : "🗳️"
            }'''

new_cand_select = '''            select new
            {
                CandidateElectionId = ce.Id,
                CandidateId = c.Id,
                Name = c.Name,
                PartyName = ce.PartyName ?? c.PartyNameBn ?? c.PartyNameEn ?? "স্বতন্ত্র",
                SymbolName = s != null ? s.NameBn : "প্রতীক",
                SymbolEmoji = s != null ? s.IconEmoji : "🗳️"
            }'''

assert old_cand_select in text, 'old_cand_select not found'
text = text.replace(old_cand_select, new_cand_select, 1)
print('1. candidates query in GetResultsSummary updated!')

# 2. Fix return of CreateOpponentCandidate
old_hero_ret = '''        return Ok(new CandidateWarRoomHero(
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
            null));'''

new_hero_ret = '''        return Ok(new CandidateWarRoomHero(
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
            null));'''

assert old_hero_ret in text, 'old_hero_ret not found'
text = text.replace(old_hero_ret, new_hero_ret, 1)
print('2. CandidateWarRoomHero instantiation updated!')

with open('backend/src/EEMS.Api/Controllers/CandidatePortalController.cs', 'w', encoding='utf-8') as f:
    f.write(text)

print('All fixes applied!')

