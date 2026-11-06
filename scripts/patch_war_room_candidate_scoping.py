# -*- coding: utf-8 -*-
with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update ngOnInit to listen to queryParamMap
old_ng_on_init = '''  ngOnInit() {
    this.electionId = this.route.snapshot.paramMap.get('electionId') || '';
    if (this.electionId) {
      this.load();
    }

    // Listen to sidebar menu navigation fragments
    this.route.fragment.subscribe(frag => {
      if (frag && ['overview', 'agents', 'voters', 'campaign', 'incidents', 'results', 'expenses'].includes(frag)) {
        this.setTab(frag as WarRoomTab);
      }
    });
  }'''

new_ng_on_init = '''  ngOnInit() {
    this.electionId = this.route.snapshot.paramMap.get('electionId') || '';
    if (this.electionId) {
      this.load();
    }

    this.route.queryParamMap.subscribe(() => {
      if (this.electionId) {
        this.load();
      }
    });

    // Listen to sidebar menu navigation fragments
    this.route.fragment.subscribe(frag => {
      if (frag && ['overview', 'agents', 'voters', 'campaign', 'incidents', 'results', 'expenses', 'team'].includes(frag)) {
        this.setTab(frag as WarRoomTab);
      }
    });
  }'''

assert old_ng_on_init in text, "old_ng_on_init not found"
text = text.replace(old_ng_on_init, new_ng_on_init, 1)
print("1. ngOnInit updated!")

# 2. Update load() to pass effectiveCandId to forkJoin APIs
old_load = '''  load() {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      summary: this.api.getCandidateWarRoom(this.electionId),
      centers: this.api.getPollingCenters(this.electionId),
      agents: this.api.getBoothAgents(this.electionId),
      results: this.api.getCandidateResultsSummary(this.electionId),
      expenses: this.api.getEcExpenseSchedule(this.electionId)
    }).subscribe({'''

new_load = '''  load() {
    this.loading.set(true);
    this.error.set(null);

    const effectiveCandId = this.route.snapshot.queryParamMap.get('candidateId') || this.auth.activeCandidateId() || this.auth.candidateId();

    forkJoin({
      summary: this.api.getCandidateWarRoom(this.electionId, effectiveCandId),
      centers: this.api.getPollingCenters(this.electionId),
      agents: this.api.getBoothAgents(this.electionId, undefined, undefined, undefined, effectiveCandId),
      results: this.api.getCandidateResultsSummary(this.electionId, effectiveCandId),
      expenses: this.api.getEcExpenseSchedule(this.electionId)
    }).subscribe({'''

assert old_load in text, "old_load not found"
text = text.replace(old_load, new_load, 1)
print("2. load() updated!")

# 3. Update loadVoters() to pass effectiveCandId
old_load_voters = '''  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearchQuery || undefined
    ).subscribe({'''

new_load_voters = '''  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    const effectiveCandId = this.route.snapshot.queryParamMap.get('candidateId') || this.auth.activeCandidateId() || this.auth.candidateId();
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearchQuery || undefined,
      effectiveCandId
    ).subscribe({'''

assert old_load_voters in text, "old_load_voters not found"
text = text.replace(old_load_voters, new_load_voters, 1)
print("3. loadVoters() updated!")

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("block4_class.py updated successfully!")

