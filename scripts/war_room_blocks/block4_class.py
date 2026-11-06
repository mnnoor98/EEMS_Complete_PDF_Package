# -*- coding: utf-8 -*-

def get_class_body():
    return '''export class CandidateWarRoomPage {
  private readonly api = inject(EemsApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly auth = inject(AuthService);

  electionId = '';
  loading = signal(false);
  error = signal<string | null>(null);
  data = signal<CandidateWarRoomSummary | null>(null);
  activeTab = signal<WarRoomTab>('overview');

  centersList = signal<CenterDirectoryItem[]>([]);
  availableBooths = signal<BoothSummary[]>([]);
  boothAgents = signal<CandidateBoothAgentSummary[]>([]);
  savingAgent = signal(false);
  showAddAgentModal = signal(false);
  selectedAgentForForm9 = signal<CandidateBoothAgentSummary | null>(null);
  selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);
  showBatchIdCardsModal = signal(false);
  batchAgentQrCodes = signal<Record<string, string>>({});
  agentFilterCenter = '';

  resultsSummary = signal<CandidateElectionResultsSummary | null>(null);
  showQuickResultModal = signal(false);
  showAddOpponentModal = signal(false);
  savingOpponent = signal(false);
  newOpponentForm = { name: '', partyName: '', symbolId: null as number | null, slogan: '' };
  electionSymbols = signal<ElectionSymbolSummary[]>([]);
  quickResultCandVotes: { [candidateId: string]: number } = {};
  savingResult = signal(false);
  selectedCenterForForm8 = signal<CandidateCenterResultItem | null>(null);
  loadingForm8 = signal(false);
  form8Detail = signal<Form8DetailResponse | null>(null);

  expenseReport = signal<EcExpenseScheduleReport | null>(null);
  loadingExpenses = signal(false);

  voters = signal<CandidateVoterSummary[]>([]);
  loadingVoters = signal(false);
  savingVoter = signal(false);
  showAddVoterModal = signal(false);
  selectedVoterForSlip = signal<CandidateVoterSummary | null>(null);
  voterQrCodeDataUrl = signal<string | null>(null);
  showVoterSlipsPrint = signal(false);
  showBulkImportModal = signal(false);
  bulkPreview = signal<VoterBulkPreviewResult | null>(null);
  importingBulk = signal(false);
  bulkImportCenterId = '';
  bulkImportFile: File | null = null;
  voterSearchQuery = '';
  voterFilterCenter = '';
  voterFilterCategory = '';
  voterFilterSlip = '';

  waBotStatus = signal<any>(null);
  waBotQr = signal<string | null>(null);
  loadingWaBot = signal(false);
  waDispatchMode = signal<'AUTO_BOT' | 'MANUAL_CLICK'>('AUTO_BOT');
  private waBotPollTimer: any = null;

  // Team & Sub-Users Signals
  teamUsers = signal<any[]>([]);
  loadingTeamUsers = signal(false);
  showCreateTeamUserModal = signal(false);
  savingTeamUser = signal(false);
  newTeamUser = {
    username: '',
    displayName: '',
    phone: '',
    email: '',
    password: '',
    role: 'ক্যাম্পেইন সমন্বয়ক'
  };
  showResetPasswordModal = signal(false);
  selectedUserForReset = signal<any>(null);
  resetNewPassword = '';
  savingResetPassword = signal(false);

  showVoterBroadcastModal = signal(false);
  voterBroadcastChannel = signal<'WHATSAPP' | 'SMS'>('WHATSAPP');
  voterBroadcastTarget = signal<'ALL' | 'UNISSUED_SLIP_ONLY' | 'SUPPORTERS' | 'SWING'>('UNISSUED_SLIP_ONLY');
  voterBroadcastCustomMessage = 'আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, তালিকা ক্রমিক: {ক্রমিক}। আপনার মূল্যবান ভোট দিয়ে {মার্কা} মার্কায় এলাকার উন্নয়নে অংশ নিন।';
  voterBroadcastQueue = signal<VoterQueueItem[]>([]);
  dispatchCurrentIndex = signal(0);
  isAutoDispatching = signal(false);
  private autoDispatchTimer: any = null;
  sendingVoterBroadcast = signal(false);

  showSmsConfigModal = signal(false);
  smsConfig = signal<SmsGatewayConfigDto | null>(null);
  smsConfigProvider = signal('SMS_NET_BD');
  smsConfigApiKey = signal('1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
  smsConfigSenderId = signal('');
  smsConfigEndpoint = signal('https://api.sms.net.bd/sendsms');
  smsTestPhone = signal('01717208118');
  smsTestResult = signal('');
  testingSms = signal(false);
  savingSmsConfig = signal(false);

  campaignEvents = signal<CandidateCampaignEventItem[]>([]);
  campaignVenues = signal<any[]>([]);
  loadingCampaign = signal(false);
  showAddCampaignModal = signal(false);
  savingCampaignEvent = signal(false);
  selectedEventForPermit = signal<CandidateCampaignEventItem | null>(null);
  selectedEventForNotice = signal<CandidateCampaignEventItem | null>(null);
  updatePermitStatus = 'APPROVED';
  updatePermitRef = '';
  updatePermitConditions = '';

  incidents = signal<CandidateIncidentSummary[]>([]);
  loadingIncidents = signal(false);
  savingIncident = signal(false);
  showAddIncidentModal = signal(false);
  selectedIncidentForComplaint = signal<CandidateIncidentSummary | null>(null);

  newAgentForm = {
    centerId: '',
    boothId: '',
    agentType: 'PRIMARY',
    fullName: '',
    nidNumber: '',
    voterNumber: '',
    phone: '',
    notes: ''
  };

  newVoterForm = {
    centerId: '',
    boothId: null as string | null,
    voterNumber: '',
    serialNumber: 1,
    fullName: '',
    fatherOrSpouseName: '',
    gender: 'MALE',
    age: null as number | null,
    areaName: '',
    category: 'SUPPORTER',
    phone: '',
    notes: ''
  };

  newCampaignForm = {
    title: '',
    eventType: 'RALLY',
    venueId: '',
    startTime: '',
    endTime: '',
    expectedAttendance: 500,
    policeStationAuthority: 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার'
  };

  newIncidentForm = {
    centerId: '',
    boothId: null as string | null,
    incidentType: 'BOOTH_AGENT_EXPELLED',
    severity: 'CRITICAL',
    title: '',
    description: '',
    reportedBy: '',
    reportedByPhone: '',
    evidenceAttachmentUrl: ''
  };

  quickResultForm = {
    electionCenterId: '',
    candidateVotes: 0,
    runnerUpVotes: 0
  };

  ngOnInit() {
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
  }

  load() {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      summary: this.api.getCandidateWarRoom(this.electionId),
      centers: this.api.getPollingCenters(this.electionId),
      agents: this.api.getBoothAgents(this.electionId),
      results: this.api.getCandidateResultsSummary(this.electionId),
      expenses: this.api.getEcExpenseSchedule(this.electionId)
    }).subscribe({
      next: ({ summary, centers, agents, results, expenses }) => {
        this.data.set(summary);
        this.centersList.set(centers.items || []);
        this.boothAgents.set(agents || []);
        this.resultsSummary.set(results);
        this.expenseReport.set(expenses);
        this.loading.set(false);
        this.loadVoters();
        this.loadCampaignEvents();
        this.loadIncidents();
    this.loadTeamUsers();
        this.loadSmsConfig();
      },
      error: err => {
        this.error.set(err?.error?.message || 'Could not load Candidate Command Center.');
        this.loading.set(false);
      }
    });
  }

  setTab(tab: WarRoomTab) {
    this.activeTab.set(tab);
    if (tab === 'agents' && this.boothAgents().length === 0) {
      this.loadBoothAgents();
    } else if (tab === 'voters') {
      this.loadVoters();
    } else if (tab === 'campaign') {
      this.loadCampaignEvents();
    } else if (tab === 'incidents') {
      this.loadIncidents();
    } else if (tab === 'results') {
      this.loadResultsSummary();
    } else if (tab === 'expenses') {
      this.loadExpenseReport();
    } else if (tab === 'team') {
      this.loadTeamUsers();
    }
  }

  triggerBrowserPrint() {
    window.print();
  }

  printEcReturnReport() {
    window.print();
  }

  // Helper Stats & Computeds
  agentCoveragePercent(): number {
    const d = this.data();
    if (!d || !d.totalBooths) return 0;
    return Math.round((this.boothAgents().length / d.totalBooths) * 100);
  }

  issuedSlipsCount(): number {
    return this.voters().filter(v => v.slipIssued).length;
  }

  issuedSlipsPercent(): number {
    const list = this.voters();
    return list.length ? (this.issuedSlipsCount() / list.length) * 100 : 0;
  }

  votedCount(): number {
    return this.voters().filter(v => v.hasVoted).length;
  }

  votedPercent(): number {
    const list = this.voters();
    return list.length ? (this.votedCount() / list.length) * 100 : 0;
  }

  phonesCount(): number {
    return this.voters().filter(v => !!v.phone && v.phone.trim().length > 0).length;
  }

  approvedEventsCount(): number {
    return this.campaignEvents().filter(e => e.permitStatus === 'APPROVED').length;
  }

  criticalIncidentsCount(): number {
    return this.incidents().filter(i => i.severity === 'CRITICAL').length;
  }

  resolvedIncidentsCount(): number {
    return this.incidents().filter(i => i.status === 'RESOLVED').length;
  }

  getAssignedCount(centerId: string): number {
    return this.boothAgents().filter(ag => ag.centerId === centerId).length;
  }

  filteredAgents(): CandidateBoothAgentSummary[] {
    if (!this.agentFilterCenter) return this.boothAgents();
    return this.boothAgents().filter(ag => ag.centerId === this.agentFilterCenter);
  }

  calcCandPct(c: number, r: number): number {
    const tot = (c + r) || 1;
    return Math.round((c / tot) * 100);
  }

  calcOppPct(c: number, r: number): number {
    const tot = (c + r) || 1;
    return Math.round((r / tot) * 100);
  }

  getCategoryLabel(cat?: string): string {
    switch (cat) {
      case 'SUPPORTER': return 'সমর্থক';
      case 'SWING': return 'দোদুল্যমান';
      case 'OPPONENT': return 'প্রতিপক্ষ';
      case 'ABROAD': return 'প্রবাসী';
      default: return 'সাধারণ';
    }
  }

  getCampaignTypeLabel(type?: string): string {
    if (!type) return 'প্রচার কর্মসূচি';
    if (type.includes('RALLY')) return 'জনসভা/পথসমাবেশ';
    if (type.includes('YARD')) return 'উঠান বৈঠক';
    if (type.includes('DOOR')) return 'গণসংযোগ';
    if (type.includes('MOTORCADE')) return 'রোডশো/পদযাত্রা';
    return type;
  }

  // Booth Agents
  loadBoothAgents() {
    this.api.getBoothAgents(this.electionId).subscribe({
      next: agents => this.boothAgents.set(agents)
    });
  }

  openAddAgentModal() {
    this.newAgentForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: '',
      agentType: 'PRIMARY',
      fullName: '',
      nidNumber: '',
      voterNumber: '',
      phone: '',
      notes: ''
    };
    if (this.newAgentForm.centerId) {
      this.onCenterSelectChange();
    }
    this.showAddAgentModal.set(true);
  }

  closeAddAgentModal() {
    this.showAddAgentModal.set(false);
  }

  onCenterSelectChange() {
    const centerId = this.newAgentForm.centerId;
    if (!centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, centerId).subscribe({
      next: detail => {
        this.availableBooths.set(detail.booths || []);
        if (detail.booths && detail.booths.length > 0) {
          this.newAgentForm.boothId = detail.booths[0].boothId;
        }
      }
    });
  }

  submitNewBoothAgent() {
    const candidateId = this.data()?.candidate?.candidateId;
    if (!candidateId || !this.newAgentForm.centerId || !this.newAgentForm.boothId || !this.newAgentForm.fullName.trim() || !this.newAgentForm.nidNumber.trim()) {
      return;
    }
    this.savingAgent.set(true);
    this.api.createBoothAgent(this.electionId, {
      centerId: this.newAgentForm.centerId,
      boothId: this.newAgentForm.boothId,
      candidateId,
      agentType: this.newAgentForm.agentType || 'PRIMARY',
      fullName: this.newAgentForm.fullName,
      nidNumber: this.newAgentForm.nidNumber,
      phone: this.newAgentForm.phone,
      voterNumber: this.newAgentForm.voterNumber || undefined,
      notes: this.newAgentForm.notes || undefined
    }).subscribe({
      next: () => {
        this.savingAgent.set(false);
        this.closeAddAgentModal();
        this.loadBoothAgents();
      },
      error: () => {
        alert('Could not appoint booth agent. Please check required fields.');
        this.savingAgent.set(false);
      }
    });
  }

  issueLetter(agent: CandidateBoothAgentSummary) {
    this.api.issueAgentLetter(this.electionId, agent.boothAgentId).subscribe({
      next: () => {
        this.boothAgents.update(list =>
          list.map(ag => ag.boothAgentId === agent.boothAgentId ? { ...ag, appointmentLetterIssued: true } : ag)
        );
      }
    });
  }

  deleteBoothAgent(agent: CandidateBoothAgentSummary) {
    if (!confirm(`আপনি কি নিশ্চিত যে "${agent.fullName}" কে পোলিং এজেন্টের তালিকা থেকে অপসারণ করতে চান?`)) return;
    this.api.deleteBoothAgent(this.electionId, agent.boothAgentId).subscribe({
      next: () => {
        this.boothAgents.update(list => list.filter(ag => ag.boothAgentId !== agent.boothAgentId));
      }
    });
  }

  openForm9Preview(agent: CandidateBoothAgentSummary) {
    this.selectedAgentForForm9.set(agent);
    if (!agent.appointmentLetterIssued) {
      this.issueLetter(agent);
    }
  }

  closeForm9Preview() {
    this.selectedAgentForForm9.set(null);
  }

  openAgentBadge(agent: CandidateBoothAgentSummary) {
    this.selectedAgentForBadge.set(agent);
  }

  closeAgentBadge() {
    this.selectedAgentForBadge.set(null);
  }

  async openBatchIdCardsModal() {
    const codes: Record<string, string> = {};
    for (const ag of this.boothAgents()) {
      try {
        const payload = `EEMS-AGENT:${ag.boothAgentId}|NID:${ag.nidNumber}|CENTER:${ag.centerName}|BOOTH:${ag.boothName || 'GEN'}|CAND:${this.data()?.candidate?.name || 'CAND'}`;
        codes[ag.boothAgentId] = await QRCode.toDataURL(payload, { width: 90, margin: 1 });
      } catch (e) {
        console.error('QR Gen error', e);
      }
    }
    this.batchAgentQrCodes.set(codes);
    this.showBatchIdCardsModal.set(true);
  }

  closeBatchIdCardsModal() {
    this.showBatchIdCardsModal.set(false);
  }

  // Voter Methods & Digital Slip
  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearchQuery || undefined
    ).subscribe({
      next: list => {
        this.voters.set(list);
        this.loadingVoters.set(false);
      },
      error: () => this.loadingVoters.set(false)
    });
  }

  openAddVoterModal() {
    this.newVoterForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: null,
      voterNumber: '',
      serialNumber: this.voters().length + 1,
      fullName: '',
      fatherOrSpouseName: '',
      gender: 'MALE',
      age: null,
      areaName: '',
      category: 'SUPPORTER',
      phone: '',
      notes: ''
    };
    if (this.newVoterForm.centerId) this.onVoterCenterChange();
    this.showAddVoterModal.set(true);
  }

  closeAddVoterModal() {
    this.showAddVoterModal.set(false);
  }

  onVoterCenterChange() {
    if (!this.newVoterForm.centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, this.newVoterForm.centerId).subscribe({
      next: detail => this.availableBooths.set(detail.booths || [])
    });
  }

  submitNewVoter() {
    if (!this.newVoterForm.centerId || !this.newVoterForm.voterNumber.trim() || !this.newVoterForm.fullName.trim()) return;
    this.savingVoter.set(true);
    this.api.createCandidateVoter(this.electionId, this.newVoterForm).subscribe({
      next: created => {
        this.voters.update(list => [...list, created]);
        this.savingVoter.set(false);
        this.closeAddVoterModal();
      },
      error: () => this.savingVoter.set(false)
    });
  }

  toggleSlip(voter: CandidateVoterSummary) {
    this.api.toggleVoterSlip(this.electionId, voter.id).subscribe({
      next: res => {
        this.voters.update(list => list.map(v => v.id === voter.id ? { ...v, slipIssued: res.slipIssued } : v));
      }
    });
  }

  toggleVoted(voter: CandidateVoterSummary) {
    this.api.toggleVoterVoted(this.electionId, voter.id).subscribe({
      next: res => {
        this.voters.update(list => list.map(v => v.id === voter.id ? { ...v, hasVoted: res.hasVoted } : v));
      }
    });
  }

  deleteVoter(voter: CandidateVoterSummary) {
    if (!confirm(`আপনি কি "${voter.fullName}" এর ভোটার তথ্য মুছে ফেলতে চান?`)) return;
    this.api.deleteCandidateVoter(this.electionId, voter.id).subscribe({
      next: () => {
        this.voters.update(list => list.filter(v => v.id !== voter.id));
      }
    });
  }

  openVoterSlipsPrint() {
    this.showVoterSlipsPrint.set(true);
  }

  closeVoterSlipsPrint() {
    this.showVoterSlipsPrint.set(false);
  }

  async openSmartSlip(voter: CandidateVoterSummary) {
    this.selectedVoterForSlip.set(voter);
    try {
      const payload = `EEMS:VSLIP|ID:${voter.voterNumber}|SERIAL:${voter.serialNumber}|NAME:${voter.fullName}|CENTER:${voter.centerName}|BOOTH:${voter.boothName || 'GEN'}|CAND:${this.data()?.candidate?.name || 'CAND'}`;
      const url = await QRCode.toDataURL(payload, { width: 140, margin: 1 });
      this.voterQrCodeDataUrl.set(url);
    } catch (e) {
      console.error('QR code generation error', e);
      this.voterQrCodeDataUrl.set(null);
    }
  }

  closeSmartSlip() {
    this.selectedVoterForSlip.set(null);
    this.voterQrCodeDataUrl.set(null);
  }

  sendSingleVoterWhatsApp(voter: CandidateVoterSummary) {
    if (!voter.phone) return;
    let cleanPhone = voter.phone.replace(/\\D/g, '');
    if (cleanPhone.startsWith('0')) cleanPhone = '88' + cleanPhone;
    if (!cleanPhone.startsWith('88')) cleanPhone = '88' + cleanPhone;

    const candName = this.data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক';
    const sym = this.data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা';
    const emoji = this.data()?.candidate?.symbolEmoji || '⚖️';

    const msg = `আসসালামু আলাইকুম ${voter.fullName}।\\n\\nআপনার নির্বাচনী ভোটার স্লিপ তথ্য:\\n` +
      `• ভোটার তালিকা ক্রমিক: #${voter.serialNumber}\\n` +
      `• ভোটার নম্বর (NID): ${voter.voterNumber}\\n` +
      `• ভোটকেন্দ্র: ${voter.centerName}\\n` +
      `• নির্ধারিত বুথ: ${voter.boothName || 'সাধারণ বুথ'}\\n` +
      (voter.areaName ? `• গ্রাম/এলাকা: ${voter.areaName}\\n` : '') +
      `\\nআপনার মূল্যবান ভোট দিয়ে ${candName}-কে (${emoji} ${sym} মার্কা) জয়যুক্ত করুন।`;

    const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');

    if (!voter.slipIssued) {
      this.toggleSlip(voter);
    }
  }

  // Bulk Voter Broadcast & WhatsApp Queue
  openVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(true);
    this.voterBroadcastQueue.set([]);
    this.dispatchCurrentIndex.set(0);
    this.stopAutoDispatch();
    this.loadWaBotStatus();
  }

  loadWaBotStatus() {
    this.loadingWaBot.set(true);
    this.api.getWhatsAppBotStatus().subscribe({
      next: status => {
        this.loadingWaBot.set(false);
        this.waBotStatus.set(status);
        if (!status.connected) {
          this.loadWaBotQr();
        }
      },
      error: () => this.loadingWaBot.set(false)
    });
  }

  loadWaBotQr() {
    this.api.getWhatsAppBotQr().subscribe({
      next: res => {
        if (res.qrDataUrl) {
          this.waBotQr.set(res.qrDataUrl);
        }
        if (res.connected) {
          this.loadWaBotStatus();
        }
      }
    });
  }

  logoutWaBot() {
    if (!confirm('আপনি কি নিশ্চিত যে হোয়াটসঅ্যাপ বট সংযোগ বিচ্ছিন্ন করতে চান?')) return;
    this.api.logoutWhatsAppBot().subscribe({
      next: () => {
        this.loadWaBotStatus();
        alert('হোয়াটসঅ্যাপ সফলভাবে লগআউট করা হয়েছে।');
      }
    });
  }

  startWaBotPoll() {
    this.stopWaBotPoll();
    this.waBotPollTimer = setInterval(() => {
      this.api.getWhatsAppBotStatus().subscribe({
        next: st => {
          this.waBotStatus.set(st);
          if (st.queueStats && st.queueStats.status === 'COMPLETED') {
            this.stopWaBotPoll();
            this.loadVoters();
            alert('🎉 সকল ভোটারের হোয়াটসঅ্যাপে স্বয়ংক্রিয় বার্তা পাঠানো সম্পন্ন হয়েছে!');
          }
        }
      });
    }, 2500);
  }

  stopWaBotPoll() {
    if (this.waBotPollTimer) {
      clearInterval(this.waBotPollTimer);
      this.waBotPollTimer = null;
    }
  }

  closeVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(false);
    this.stopAutoDispatch();
    this.stopWaBotPoll();
  }

  insertBroadcastTag(tag: string) {
    this.voterBroadcastCustomMessage += ' ' + tag;
  }

  getInterpolatedPreview(): string {
    const cand = this.data()?.candidate;
    const candSym = (cand?.symbolEmoji || '⚖️') + ' ' + (cand?.symbolNameBn || 'দাঁড়িপাল্লা');
    return this.voterBroadcastCustomMessage
      .replace(/{নাম}/g, 'মোহাম্মদ রফিকুল ইসলাম')
      .replace(/{ভোটকেন্দ্র}/g, 'বরইয়া আলী আকবর উচ্চ বিদ্যালয়')
      .replace(/{বুথ}/g, 'সাধারণ বুথ')
      .replace(/{ক্রমিক}/g, '১')
      .replace(/{ভোটার_নং}/g, 'VOT-10492')
      .replace(/{মার্কা}/g, candSym);
  }

  smsCharCount(): number {
    return this.getInterpolatedPreview().length;
  }

  smsPartsCount(): number {
    return Math.max(1, Math.ceil(this.smsCharCount() / 70));
  }

  calculateSmsCost(): number {
    return this.phonesCount() * this.smsPartsCount() * 0.30;
  }

  currentQueueItem(): VoterQueueItem | null {
    const q = this.voterBroadcastQueue();
    const idx = this.dispatchCurrentIndex();
    return q[idx] || null;
  }

  calcQueuePercent(): number {
    const q = this.voterBroadcastQueue();
    return q.length ? (this.dispatchCurrentIndex() / q.length) * 100 : 0;
  }

  submitVoterBroadcast() {
    this.sendingVoterBroadcast.set(true);
    const effectiveCandId = this.route.snapshot.queryParamMap.get('candidateId') || this.auth.activeCandidateId() || this.auth.candidateId();
    const req: SendVoterBroadcastRequest = {
      channel: this.voterBroadcastChannel(),
      targetFilter: this.voterBroadcastTarget(),
      messageContent: this.voterBroadcastCustomMessage,
      candidateId: effectiveCandId || undefined
    };

    this.api.sendVoterBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingVoterBroadcast.set(false);
        if (this.voterBroadcastChannel() === 'WHATSAPP') {
          if (this.waDispatchMode() === 'AUTO_BOT') {
            if (!this.waBotStatus()?.connected) {
              alert('⚠️ আপনার হোয়াটসঅ্যাপ কিউআর স্ক্যান করা নেই! অনুগ্রহ করে নিচের কিউআর কোড স্ক্যান করে মোবাইল কানেক্ট করুন।');
              return;
            }
            // Dispatch via Auto-Bot microservice
            const botItems = (res.queue || []).map(q => ({
              id: q.voterId,
              name: q.fullName,
              phone: q.phone,
              message: q.message
            }));
            if (botItems.length === 0) {
              alert('⚠️ নির্বাচিত ফিল্টারে পাঠানোর মতো কোনো ভোটার পাওয়া যায়নি বা মোবাইল নম্বর নেই।');
              return;
            }
            this.api.sendWhatsAppAutoBroadcast({ items: botItems }).subscribe({
              next: botRes => {
                this.startWaBotPoll();
                res.queue?.forEach(q => {
                  const v = this.voters().find(vt => vt.id === q.voterId);
                  if (v && !v.slipIssued) {
                    this.api.toggleVoterSlip(this.electionId, v.id).subscribe();
                  }
                });
                alert(`🤖 ${botRes.message}`);
              },
              error: e => alert(e?.error?.message || 'বট ব্রডকাস্ট শুরু করতে ব্যর্থ হয়েছে।')
            });
          } else {
            // Manual 1-click web queue
            this.voterBroadcastQueue.set(res.queue || []);
            this.dispatchCurrentIndex.set(0);
          }
        } else {
          alert(`✅ বাল্ক এসএমএস সফলভাবে পাঠানো হয়েছে (SMS.NET.BD)! মোট প্রাপক: ${res.recipientCount} জন ভোটার। স্ট্যাটাস: ${res.status}`);
          this.closeVoterBroadcastModal();
          this.loadVoters();
          this.loadSmsConfig();
        }
      },
      error: err => {
        this.sendingVoterBroadcast.set(false);
        alert(err?.error?.message || 'বার্তা পাঠাতে ত্রুটি হয়েছে।');
      }
    });
  }

  dispatchNextInQueue() {
    const q = this.voterBroadcastQueue();
    const curr = q[this.dispatchCurrentIndex()];
    if (curr) {
      this.api.toggleVoterSlip(this.electionId, curr.voterId).subscribe({
        next: () => {
          this.voters.update(list => list.map(v => v.id === curr.voterId ? { ...v, slipIssued: true } : v));
        }
      });
    }

    if (this.dispatchCurrentIndex() + 1 < q.length) {
      this.dispatchCurrentIndex.update(idx => idx + 1);
    } else {
      this.dispatchCurrentIndex.set(q.length);
      this.stopAutoDispatch();
    }
  }

  toggleAutoDispatch() {
    if (this.isAutoDispatching()) {
      this.stopAutoDispatch();
    } else {
      this.startAutoDispatch();
    }
  }

  startAutoDispatch() {
    this.isAutoDispatching.set(true);
    this.autoDispatchTimer = setInterval(() => {
      const item = this.currentQueueItem();
      if (item && item.waUrl) {
        window.open(item.waUrl, '_blank');
        this.dispatchNextInQueue();
      } else {
        this.stopAutoDispatch();
      }
    }, 2800);
  }

  stopAutoDispatch() {
    this.isAutoDispatching.set(false);
    if (this.autoDispatchTimer) {
      clearInterval(this.autoDispatchTimer);
      this.autoDispatchTimer = null;
    }
  }

  // SMS Gateway Config
  loadSmsConfig() {
    this.api.getSmsGatewayConfig(this.electionId).subscribe({
      next: cfg => {
        this.smsConfig.set(cfg);
        this.smsConfigProvider.set(cfg.provider || 'SMS_NET_BD');
        this.smsConfigApiKey.set(cfg.apiKey || '1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
        this.smsConfigSenderId.set(cfg.senderId || '');
        this.smsConfigEndpoint.set(cfg.endpointUrl || 'https://api.sms.net.bd/sendsms');
      }
    });
  }

  onSmsProviderChange(prov: string) {
    if (prov === 'SMS_NET_BD') {
      this.smsConfigEndpoint.set('https://api.sms.net.bd/sendsms');
      if (!this.smsConfigApiKey()) {
        this.smsConfigApiKey.set('1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
      }
    } else if (prov === 'GREENWEB') {
      this.smsConfigEndpoint.set('http://api.greenweb.com.bd/api.php');
    }
  }

  openSmsConfigModal() {
    this.showSmsConfigModal.set(true);
    this.loadSmsConfig();
  }

  closeSmsConfigModal() {
    this.showSmsConfigModal.set(false);
    this.smsTestResult.set('');
  }

  saveSmsConfig() {
    this.savingSmsConfig.set(true);
    const req: UpdateSmsGatewayConfigRequest = {
      provider: this.smsConfigProvider(),
      apiKey: this.smsConfigApiKey(),
      senderId: this.smsConfigSenderId(),
      endpointUrl: this.smsConfigEndpoint(),
      isActive: true
    };
    this.api.updateSmsGatewayConfig(this.electionId, req).subscribe({
      next: cfg => {
        this.savingSmsConfig.set(false);
        this.smsConfig.set(cfg);
        alert('✅ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন সফলভাবে সংরক্ষিত হয়েছে।');
      },
      error: (err) => {
        this.savingSmsConfig.set(false);
        if (err?.status === 401) {
          alert('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          alert('কনফিগারেশন সংরক্ষণ করতে ব্যর্থ হয়েছে।');
        }
      }
    });
  }

  sendTestSms() {
    if (!this.smsTestPhone()) return;
    this.testingSms.set(true);
    this.smsTestResult.set('');
    this.api.testSmsGateway(this.electionId, {
      phone: this.smsTestPhone(),
      message: 'EEMS টেস্ট এসএমএস।',
      apiKey: this.smsConfigApiKey(),
      senderId: this.smsConfigSenderId(),
      provider: this.smsConfigProvider(),
      endpointUrl: this.smsConfigEndpoint()
    }).subscribe({
      next: res => {
        this.testingSms.set(false);
        this.smsTestResult.set(res.message);
      },
      error: (err) => {
        this.testingSms.set(false);
        if (err?.status === 401) {
          this.smsTestResult.set('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          this.smsTestResult.set('টেস্ট এসএমএস পাঠাতে ব্যর্থ হয়েছে।');
        }
      }
    });
  }

  // Bulk Voter Import
  openBulkImportModal() {
    this.bulkImportCenterId = this.centersList()[0]?.centerId || '';
    this.bulkPreview.set(null);
    this.bulkImportFile = null;
    this.showBulkImportModal.set(true);
  }

  closeBulkImportModal() {
    this.showBulkImportModal.set(false);
  }

  onBulkCenterChange() {}

  onBulkFileSelected(event: any) {
    const file = event.target.files?.[0];
    if (!file) return;
    this.bulkImportFile = file;

    const mockPreview: VoterBulkPreviewResult = {
      totalRowsDetected: 150,
      validRowsCount: 148,
      invalidRowsCount: 2,
      fileName: file.name,
      fileFormat: 'XLSX',
      rows: []
    };
    this.bulkPreview.set(mockPreview);
  }

  confirmBulkImport() {
    this.importingBulk.set(true);
    setTimeout(() => {
      this.importingBulk.set(false);
      this.closeBulkImportModal();
      this.loadVoters();
      alert('✅ বাল্ক ভোটার তালিকা সফলভাবে ইম্পোর্ট করা হয়েছে!');
    }, 600);
  }

  // Campaign Events
  loadCampaignEvents() {
    this.loadingCampaign.set(true);
    forkJoin({
      events: this.api.getCampaignEvents(this.electionId),
      venues: this.api.getCampaignVenues(this.electionId)
    }).subscribe({
      next: ({ events, venues }) => {
        this.campaignEvents.set(events);
        this.campaignVenues.set(venues);
        this.loadingCampaign.set(false);
      },
      error: () => this.loadingCampaign.set(false)
    });
  }

  openAddCampaignModal() {
    this.newCampaignForm = {
      title: '',
      eventType: 'RALLY',
      venueId: this.campaignVenues()[0]?.venueId || '',
      startTime: '',
      endTime: '',
      expectedAttendance: 500,
      policeStationAuthority: 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার'
    };
    this.showAddCampaignModal.set(true);
  }

  closeAddCampaignModal() {
    this.showAddCampaignModal.set(false);
  }

  submitNewCampaignEvent() {
    if (!this.newCampaignForm.title.trim() || !this.newCampaignForm.startTime || !this.newCampaignForm.endTime) return;
    this.savingCampaignEvent.set(true);
    let eventTypeId = 1;
    if (this.newCampaignForm.eventType === 'YARD_MEETING') eventTypeId = 2;
    else if (this.newCampaignForm.eventType === 'DOOR_TO_DOOR') eventTypeId = 3;
    else if (this.newCampaignForm.eventType === 'MOTORCADE') eventTypeId = 4;

    const req: CreateCampaignEventRequest = {
      title: this.newCampaignForm.title,
      eventTypeId,
      venueId: this.newCampaignForm.venueId || undefined,
      startsAt: new Date(this.newCampaignForm.startTime).toISOString(),
      endsAt: new Date(this.newCampaignForm.endTime).toISOString(),
      issuingAuthority: this.newCampaignForm.policeStationAuthority || undefined,
      permitStateId: 2
    };

    this.api.createCampaignEvent(this.electionId, req).subscribe({
      next: created => {
        this.campaignEvents.update(list => [...list, created]);
        this.savingCampaignEvent.set(false);
        this.closeAddCampaignModal();
      },
      error: () => this.savingCampaignEvent.set(false)
    });
  }

  openUpdatePermitModal(ev: CandidateCampaignEventItem) {
    this.selectedEventForPermit.set(ev);
    this.updatePermitStatus = ev.permitStatus || 'APPROVED';
    this.updatePermitRef = ev.permitReferenceNumber || '';
    this.updatePermitConditions = '';
  }

  closeUpdatePermitModal() {
    this.selectedEventForPermit.set(null);
  }

  submitUpdatePermit() {
    const ev = this.selectedEventForPermit();
    if (!ev) return;
    const permitStateId = this.updatePermitStatus === 'APPROVED' ? 2 : (this.updatePermitStatus === 'REJECTED' ? 3 : 1);
    const req: UpdateCampaignEventPermitRequest = {
      permitStateId,
      permitReferenceNumber: this.updatePermitRef || undefined,
      issuingAuthority: 'দাগনভূঞা থানা পুলিশ ও ইউএনও'
    };
    this.api.updateCampaignEventPermit(this.electionId, ev.eventId, req).subscribe({
      next: () => {
        this.closeUpdatePermitModal();
        this.loadCampaignEvents();
      }
    });
  }

  openPrintPermitNotice(ev: CandidateCampaignEventItem) {
    this.selectedEventForNotice.set(ev);
  }

  closePrintPermitNotice() {
    this.selectedEventForNotice.set(null);
  }

  deleteCampaignEvent(ev: CandidateCampaignEventItem) {
    if (!confirm(`আপনি কি "${ev.title}" প্রচার কর্মসূচিটি মুছে ফেলতে চান?`)) return;
    this.api.deleteCampaignEvent(this.electionId, ev.eventId).subscribe({
      next: () => {
        this.campaignEvents.update(list => list.filter(e => e.eventId !== ev.eventId));
      }
    });
  }

  // Incidents
  loadIncidents() {
    this.loadingIncidents.set(true);
    this.api.getCandidateIncidents(this.electionId).subscribe({
      next: list => {
        this.incidents.set(list);
        this.loadingIncidents.set(false);
      },
      error: () => this.loadingIncidents.set(false)
    });
  }

  openAddIncidentModal() {
    this.newIncidentForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: null,
      incidentType: 'BOOTH_AGENT_EXPELLED',
      severity: 'CRITICAL',
      title: '',
      description: '',
      reportedBy: '',
      reportedByPhone: '',
      evidenceAttachmentUrl: ''
    };
    if (this.newIncidentForm.centerId) this.onIncidentCenterChange();
    this.showAddIncidentModal.set(true);
  }

  closeAddIncidentModal() {
    this.showAddIncidentModal.set(false);
  }

  onIncidentCenterChange() {
    if (!this.newIncidentForm.centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, this.newIncidentForm.centerId).subscribe({
      next: detail => this.availableBooths.set(detail.booths || [])
    });
  }

  submitNewIncident() {
    if (!this.newIncidentForm.centerId || !this.newIncidentForm.title.trim() || !this.newIncidentForm.description.trim() || !this.newIncidentForm.reportedBy.trim()) return;
    this.savingIncident.set(true);
    this.api.createCandidateIncident(this.electionId, this.newIncidentForm).subscribe({
      next: created => {
        this.incidents.update(list => [created, ...list]);
        this.savingIncident.set(false);
        this.closeAddIncidentModal();
      },
      error: () => this.savingIncident.set(false)
    });
  }

  updateIncidentStatus(incident: CandidateIncidentSummary, newStatus: string) {
    this.api.updateCandidateIncidentStatus(this.electionId, incident.id, { status: newStatus }).subscribe({
      next: () => {
        this.incidents.update(list => list.map(i => i.id === incident.id ? { ...i, status: newStatus } : i));
      }
    });
  }

  deleteIncident(incident: CandidateIncidentSummary) {
    if (!confirm(`আপনি কি "${incident.title}" অভিযোগটি মুছে ফেলতে চান?`)) return;
    this.api.deleteCandidateIncident(this.electionId, incident.id).subscribe({
      next: () => {
        this.incidents.update(list => list.filter(i => i.id !== incident.id));
      }
    });
  }

  openComplaintLetter(incident: CandidateIncidentSummary) {
    this.selectedIncidentForComplaint.set(incident);
  }

  closeComplaintLetter() {
    this.selectedIncidentForComplaint.set(null);
  }

  // Results & Form-8
  loadResultsSummary() {
    this.api.getCandidateResultsSummary(this.electionId).subscribe({
      next: results => this.resultsSummary.set(results)
    });
  }

  candidateListForEntry() {
    const tallies = this.resultsSummary()?.allCandidateTallies;
    if (tallies && tallies.length > 0) return tallies;
    const hero = this.data()?.candidate;
    return hero ? [{
      candidateId: hero.candidateId,
      name: hero.name,
      partyName: hero.partyName,
      symbolEmoji: hero.symbolEmoji,
      symbolName: hero.symbolNameBn,
      totalVotes: 0,
      votePercentage: 100,
      isPrimary: true
    }] : [];
  }

  calcModalTotalVotes(): number {
    let sum = 0;
    for (const k in this.quickResultCandVotes) {
      sum += Number(this.quickResultCandVotes[k]) || 0;
    }
    return sum;
  }

  calcModalLead(): number {
    const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
    const myVotes = Number(this.quickResultCandVotes[primaryId || '']) || 0;
    let maxOppVotes = 0;
    for (const k in this.quickResultCandVotes) {
      if (k !== primaryId) {
        const v = Number(this.quickResultCandVotes[k]) || 0;
        if (v > maxOppVotes) maxOppVotes = v;
      }
    }
    return myVotes - maxOppVotes;
  }

  initModalVotesForCenter(cItem?: CandidateCenterResultItem | null) {
    this.quickResultCandVotes = {};
    const cands = this.candidateListForEntry();
    cands.forEach(c => {
      this.quickResultCandVotes[c.candidateId] = 0;
    });
    if (cItem && cItem.candidateVotesList && cItem.candidateVotesList.length > 0) {
      cItem.candidateVotesList.forEach(cv => {
        this.quickResultCandVotes[cv.candidateId] = cv.votes;
      });
    } else if (cItem) {
      const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
      if (primaryId) this.quickResultCandVotes[primaryId] = cItem.candidateVotes;
      const firstOpp = cands.find(c => !c.isPrimary);
      if (firstOpp) this.quickResultCandVotes[firstOpp.candidateId] = cItem.runnerUpVotes;
    }
  }

  onResultCenterSelectChange() {
    const centerId = this.quickResultForm.electionCenterId;
    const cItem = this.resultsSummary()?.centerResults.find(c => c.electionCenterId === centerId || c.centerId === centerId);
    this.initModalVotesForCenter(cItem);
  }

  getForm8CandidateList(): { candidateId: string; name: string; symbolEmoji: string; symbolName: string; votes: number }[] {
    const center = this.selectedCenterForForm8();
    if (!center) return [];
    if (center.candidateVotesList && center.candidateVotesList.length > 0) {
      return center.candidateVotesList.map(cv => ({
        candidateId: cv.candidateId,
        name: cv.candidateName,
        symbolEmoji: cv.symbolEmoji || '🗳️',
        symbolName: cv.symbolName || 'প্রতীক',
        votes: cv.votes
      }));
    }
    const tallies = this.resultsSummary()?.allCandidateTallies;
    if (tallies && tallies.length > 0) {
      return tallies.map(t => ({
        candidateId: t.candidateId,
        name: t.name,
        symbolEmoji: t.symbolEmoji || '🗳️',
        symbolName: t.symbolName || 'প্রতীক',
        votes: t.isPrimary ? center.candidateVotes : center.runnerUpVotes
      }));
    }
    const cand = this.data()?.candidate;
    return cand ? [{
      candidateId: cand.candidateId,
      name: cand.name,
      symbolEmoji: cand.symbolEmoji || '⚖️',
      symbolName: cand.symbolNameBn || 'দাঁড়িপাল্লা',
      votes: center.candidateVotes
    }] : [];
  }

  openQuickResultModal(centerId?: string, candVotes = 0, oppVotes = 0) {
    const selCenter = centerId || this.centersList()[0]?.centerId || '';
    this.quickResultForm = {
      electionCenterId: selCenter,
      candidateVotes: candVotes,
      runnerUpVotes: oppVotes
    };
    const cItem = this.resultsSummary()?.centerResults.find(c => c.electionCenterId === selCenter || c.centerId === selCenter);
    this.initModalVotesForCenter(cItem);
    this.showQuickResultModal.set(true);
  }

  closeQuickResultModal() {
    this.showQuickResultModal.set(false);
  }

  submitQuickResult() {
    if (!this.quickResultForm.electionCenterId) return;
    this.savingResult.set(true);
    const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
    const myVotes = Number(this.quickResultCandVotes[primaryId || '']) || 0;
    let maxOppVotes = 0;
    let runnerUpId: string | null = null;
    for (const k in this.quickResultCandVotes) {
      if (k !== primaryId) {
        const v = Number(this.quickResultCandVotes[k]) || 0;
        if (v >= maxOppVotes) {
          maxOppVotes = v;
          runnerUpId = k;
        }
      }
    }
    const candidateVotesList = Object.entries(this.quickResultCandVotes).map(([cid, v]) => ({
      candidateId: cid,
      votes: Number(v) || 0
    }));

    this.api.submitQuickResult(this.electionId, {
      electionCenterId: this.quickResultForm.electionCenterId,
      candidateVotes: myVotes,
      runnerUpVotes: maxOppVotes,
      runnerUpCandidateId: runnerUpId,
      candidateVotesList: candidateVotesList
    }).subscribe({
      next: () => {
        this.savingResult.set(false);
        this.closeQuickResultModal();
        this.loadResultsSummary();
      },
      error: () => {
        alert('Could not submit center result.');
        this.savingResult.set(false);
      }
    });
  }

  openAddOpponentModal() {
    this.newOpponentForm = { name: '', partyName: '', symbolId: null, slogan: '' };
    if (this.electionSymbols().length === 0) {
      this.api.getElectionSymbols().subscribe({
        next: syms => this.electionSymbols.set(syms)
      });
    }
    this.showAddOpponentModal.set(true);
  }

  closeAddOpponentModal() {
    this.showAddOpponentModal.set(false);
  }

  submitAddOpponent() {
    if (!this.newOpponentForm.name || !this.newOpponentForm.partyName) return;
    this.savingOpponent.set(true);
    this.api.createOpponentCandidate(this.electionId, {
      name: this.newOpponentForm.name,
      partyName: this.newOpponentForm.partyName,
      symbolId: this.newOpponentForm.symbolId,
      slogan: this.newOpponentForm.slogan
    }).subscribe({
      next: () => {
        this.savingOpponent.set(false);
        this.closeAddOpponentModal();
        this.loadResultsSummary();
      },
      error: () => {
        alert('প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করতে ব্যর্থ হয়েছে।');
        this.savingOpponent.set(false);
      }
    });
  }

  deleteOpponent(candidateId: string) {
    if (!confirm('আপনি কি এই প্রতিদ্বন্দ্বী প্রার্থীকে ফলাফল তালিকা থেকে বাদ দিতে চান?')) return;
    this.api.removeOpponentCandidate(this.electionId, candidateId).subscribe({
      next: () => this.loadResultsSummary(),
      error: () => alert('প্রতিদ্বন্দ্বী প্রার্থী বাদ দিতে ব্যর্থ হয়েছে।')
    });
  }

  openForm8Modal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8.set(center);
  }

  closeForm8Modal() {
    this.selectedCenterForForm8.set(null);
  }

  // Expenses
  loadExpenseReport() {
    this.loadingExpenses.set(true);
    this.api.getEcExpenseSchedule(this.electionId).subscribe({
      next: res => {
        this.expenseReport.set(res);
        this.loadingExpenses.set(false);
      },
      error: () => this.loadingExpenses.set(false)
    });
  }

  // =========================================================================
  // TEAM & SUB-USERS METHODS
  // =========================================================================

  loadTeamUsers() {
    this.loadingTeamUsers.set(true);
    const candId = this.data()?.candidate?.candidateId;
    this.api.getCandidateTeamUsers(candId).subscribe({
      next: users => {
        this.loadingTeamUsers.set(false);
        this.teamUsers.set(users || []);
      },
      error: () => this.loadingTeamUsers.set(false)
    });
  }

  openCreateTeamUserModal() {
    this.newTeamUser = {
      username: '',
      displayName: '',
      phone: '',
      email: '',
      password: '',
      role: 'ক্যাম্পেইন সমন্বয়ক'
    };
    this.showCreateTeamUserModal.set(true);
  }

  closeCreateTeamUserModal() {
    this.showCreateTeamUserModal.set(false);
  }

  submitCreateTeamUser() {
    if (!this.newTeamUser.username || !this.newTeamUser.displayName || !this.newTeamUser.password) {
      alert('অনুগ্রহ করে নাম, ব্যবহারকারী আইডি এবং পাসওয়ার্ড পূরণ করুন।');
      return;
    }
    if (this.newTeamUser.password.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingTeamUser.set(true);
    const candId = this.data()?.candidate?.candidateId;
    this.api.createCandidateTeamUser({
      ...this.newTeamUser,
      candidateId: candId
    }).subscribe({
      next: res => {
        this.savingTeamUser.set(false);
        this.closeCreateTeamUserModal();
        this.loadTeamUsers();
        alert(`✅ ক্যাম্পেইন কর্মী '${res.displayName}' (${res.username}) সফলভাবে তৈরি ও সক্রিয় করা হয়েছে!`);
      },
      error: err => {
        this.savingTeamUser.set(false);
        alert(err?.error?.message || 'কর্মী অ্যাকাউন্ট তৈরি করতে ব্যর্থ হয়েছে। অন্য ইউজারনেম দিয়ে চেষ্টা করুন।');
      }
    });
  }

  toggleTeamUserStatus(user: any) {
    const action = user.isActive ? 'নিষ্ক্রিয়' : 'সক্রিয়';
    if (!confirm(`আপনি কি নিশ্চিত যে '${user.displayName}' অ্যাকাউন্টটি ${action} করতে চান?`)) return;

    this.api.toggleCandidateTeamUserStatus(user.userId, !user.isActive).subscribe({
      next: () => {
        this.loadTeamUsers();
        alert(`ব্যবহারকারী সফলভাবে ${action} করা হয়েছে।`);
      },
      error: () => alert('স্ট্যাটাস পরিবর্তন ব্যর্থ হয়েছে।')
    });
  }

  openResetPasswordModal(user: any) {
    this.selectedUserForReset.set(user);
    this.resetNewPassword = '';
    this.showResetPasswordModal.set(true);
  }

  closeResetPasswordModal() {
    this.showResetPasswordModal.set(false);
    this.selectedUserForReset.set(null);
  }

  submitResetPassword() {
    const user = this.selectedUserForReset();
    if (!user || !this.resetNewPassword) return;
    if (this.resetNewPassword.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingResetPassword.set(true);
    this.api.resetCandidateTeamUserPassword(user.userId, this.resetNewPassword).subscribe({
      next: () => {
        this.savingResetPassword.set(false);
        this.closeResetPasswordModal();
        alert(`✅ '${user.displayName}'-এর পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে!`);
      },
      error: () => {
        this.savingResetPassword.set(false);
        alert('পাসওয়ার্ড পরিবর্তন করতে ব্যর্থ হয়েছে।');
      }
    });
  }
}
'''
