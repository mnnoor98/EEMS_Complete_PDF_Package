# -*- coding: utf-8 -*-
file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix template closing backtick
target_premature_close = "    }\n\n  `,\n\n    <!-- ===================================================================== -->\n    <!-- MODAL: ADD CAMPAIGN EVENT -->"
replacement_fix = "    }\n\n    <!-- ===================================================================== -->\n    <!-- MODAL: ADD CAMPAIGN EVENT -->"

if target_premature_close in content:
    content = content.replace(target_premature_close, replacement_fix, 1)
    print("Premature template backtick removed.")
else:
    print("WARN: target_premature_close not found.")

# Put the closing backtick right before `styles: [`
target_styles = "\n    styles: [`"
replacement_styles = "\n  `,\n  styles: [`"
if "\n  `,\n  styles: [`" not in content and target_styles in content:
    content = content.replace(target_styles, replacement_styles, 1)
    print("Template closing backtick added before styles.")
else:
    print("WARN: target_styles not found or already correct.")

# 2. Append all missing methods to CandidateWarRoomPage
methods = """
  // =========================================================================
  // VOTERS MANAGEMENT METHODS
  // =========================================================================
  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    const effectiveCandId = this.auth.effectiveCandidateId();
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearch || undefined,
      effectiveCandId
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
    if (!confirm('আপনি কি এই ভোটারের তথ্য মুছে ফেলতে চান?')) return;
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

  // =========================================================================
  // BULK VOTER IMPORT METHODS (CSV / EXCEL / PDF)
  // =========================================================================
  openBulkImportModal() {
    this.bulkImportCenterId = this.voterFilterCenter || this.centersList()[0]?.centerId || '';
    this.bulkImportBoothId = '';
    this.selectedBulkFileName.set('');
    this.selectedBulkFile = null;
    this.bulkPreviewData.set(null);
    this.bulkImportError.set('');
    this.bulkImportSuccessMessage.set('');
    if (this.bulkImportCenterId) this.onBulkCenterChange();
    this.showBulkImportModal.set(true);
  }

  closeBulkImportModal() {
    this.showBulkImportModal.set(false);
  }

  onBulkCenterChange() {
    if (!this.bulkImportCenterId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, this.bulkImportCenterId).subscribe({
      next: detail => this.availableBooths.set(detail.booths || [])
    });
  }

  onBulkFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    this.selectedBulkFile = file;
    this.selectedBulkFileName.set(file.name);
    this.bulkImportError.set('');
    this.bulkImportSuccessMessage.set('');
    this.bulkPreviewData.set(null);

    if (!this.bulkImportCenterId) {
      this.bulkImportError.set('অনুগ্রহ করে প্রথমে একটি ডিফল্ট ভোটকেন্দ্র নির্বাচন করুন।');
      return;
    }

    this.loadingBulkPreview.set(true);
    this.api.previewVoterBulk(this.electionId, this.bulkImportCenterId, this.bulkImportBoothId || undefined, file).subscribe({
      next: res => {
        this.bulkPreviewData.set(res);
        this.loadingBulkPreview.set(false);
      },
      error: (err) => {
        const msg = err?.error?.error || err?.message || 'ফাইলটি প্রসেস করা যায়নি। ফরম্যাট যাচাই করুন।';
        this.bulkImportError.set(msg);
        this.loadingBulkPreview.set(false);
      }
    });
  }

  confirmBulkImport() {
    const preview = this.bulkPreviewData();
    if (!preview || preview.validRowsCount === 0 || !this.bulkImportCenterId) return;

    this.importingBulkVoters.set(true);
    this.bulkImportError.set('');
    const candId = this.data()?.candidate?.candidateId || this.auth.effectiveCandidateId();

    this.api.confirmVoterBulkImport(this.electionId, {
      centerId: this.bulkImportCenterId,
      boothId: this.bulkImportBoothId || undefined,
      candidateId: candId,
      rows: preview.rows.filter(r => r.isValid)
    }).subscribe({
      next: res => {
        this.importingBulkVoters.set(false);
        this.bulkImportSuccessMessage.set(res.message);
        this.loadVoters();
        setTimeout(() => {
          this.closeBulkImportModal();
        }, 2200);
      },
      error: (err) => {
        this.importingBulkVoters.set(false);
        const msg = err?.error?.error || err?.message || 'ভোটার ডাটা সংরক্ষণ করা যায়নি।';
        this.bulkImportError.set(msg);
      }
    });
  }

  // =========================================================================
  // INCIDENT MANAGEMENT & LEGAL NOTICE METHODS
  // =========================================================================
  loadIncidents() {
    this.loadingIncidents.set(true);
    const effectiveCandId = this.auth.effectiveCandidateId();
    this.api.getCandidateIncidents(this.electionId, undefined, effectiveCandId).subscribe({
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
    if (!confirm('আপনি কি এই অভিযোগটি মুছে ফেলতে চান?')) return;
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

  getRecipientDesignation(): string {
    switch (this.complaintRecipientType) {
      case 'ARO':
        return 'সহকারী রিটার্নিং অফিসার ও উপজেলা নির্বাহী অফিসার (ইউএনও)';
      case 'MAGISTRATE':
        return 'বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট / জুডিশিয়াল ম্যাজিস্ট্রেট (ভ্রাম্যমাণ আদালত)';
      case 'RO':
        return 'মাননীয় রিটার্নিং অফিসার ও জেলা ম্যাজিস্ট্রেট / জেলা প্রশাসক';
      default:
        return 'সহকারী রিটার্নিং অফিসার এবং বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট (যৌথভাবে)';
    }
  }

  getStatutoryViolationClauses(type?: string): { title: string; clauses: string; remedies: string[] } {
    switch (type) {
      case 'BOOTH_AGENT_EXPELLED':
        return {
          title: 'পোলিং এজেন্টকে বলপ্রয়োগে ভোটকক্ষ হইতে বহিষ্কার ও ভয়ভীতি প্রদর্শন',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৩(২)(খ), ৭৪(১) এবং নির্বাচন আচরণ বিধিমালা, ২০০৮ এর বিধি ১৬',
          remedies: [
            'অনতিবিলম্বে ভোটকেন্দ্রে অতিরিক্ত স্ট্রাইকিং ফোর্স ও বিজ্ঞ ম্যাজিস্ট্রেট প্রেরণপূর্বক জোরপূর্বক বহিষ্কৃত পোলিং এজেন্টদের সসম্মানে ও পূর্ণ নিরাপত্তায় ভোটকক্ষে পুনর্বহাল করা।',
            'বহিষ্কারের ঘটনায় জড়িত দুষ্কৃতকারী ও পক্ষপাতদুষ্ট কর্মকর্তাদের তাৎক্ষণিক গ্রেপ্তারপূর্বক ভ্রাম্যমাণ আদালতে সাজা প্রদান।',
            'এজেন্টদের অনুপস্থিতিতে কোনো ভোটগ্রহণ বা ব্যালট পেপার বিতরণ সম্পূর্ণ স্থগিত রাখা।'
          ]
        };
      case 'FAKE_VOTING':
        return {
          title: 'জাল ভোট প্রদান, প্রক্সি ভোটিং ও বহিরাগতদের অনুপ্রবেশ',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৩(১), ৭৭ এবং দণ্ডবিধি, ১৮৬০ এর ধারা ১৭১(ঘ)',
          remedies: [
            'অবিলম্বে ভোটকেন্দ্রে ভোটারদের আঙ্গুলের অমোচনীয় কালি ও এনআইডি যাচাই জোরদার করা।',
            'জাল ভোট প্রদানে জড়িতদের আটক করিয়া সংক্ষিপ্ত বিচার আইনে তাৎক্ষণিক দণ্ড প্রদান।'
          ]
        };
      case 'VOTER_OBSTRUCTION':
        return {
          title: 'ভোটারদের ভোটকেন্দ্রে আসিতে বাধা প্রদান ও রাস্তায় ভয়ভীতি প্রদর্শন',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৪, ৭৭ এবং আচরণবিধি ২০০৮ এর বিধি ১৮',
          remedies: [
            'কেন্দ্রে প্রবেশের সকল সংযোগ সড়কে বিজিবি/পুলিশের তল্লাশি চৌকি ও নিয়মিত টহল স্থাপন।',
            'ভোটারদের নির্ভয়ে কেন্দ্রে পৌঁছানোর সার্বিক নিরাপত্তা নিশ্চিত করা।'
          ]
        };
      case 'CENTER_CAPTURE':
        return {
          title: 'ভোটকেন্দ্র দখল, ব্যালট পেপার ছিনতাই ও বলপ্রয়োগ',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৮০, ৮১ ও ৮২',
          remedies: [
            'নির্বাচন কমিশনের আরপিও অনুচ্ছেদ ৮০ অনুযায়ী কেন্দ্রের ভোটগ্রহণ তাৎক্ষণিক স্থগিত ঘোষণা করা।',
            'ছিনতাইকৃত ও অবৈধভাবে সীলযুক্ত ব্যালট পেপার বাতিল গণ্য করা।'
          ]
        };
      case 'PRESIDING_BIAS':
        return {
          title: 'প্রিজাইডিং বা পোলিং কর্মকর্তার প্রকাশ্য পক্ষপাতিত্ব ও নিয়ম লঙ্ঘন',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৯ ও ৮১',
          remedies: [
            'পক্ষপাতদুষ্ট প্রিজাইডিং বা পোলিং অফিসারকে অনতিবিলম্বে দায়িত্ব হইতে প্রত্যাহার ও তদন্তপূর্বক ব্যবস্থা গ্রহণ।'
          ]
        };
      default:
        return {
          title: 'নির্বাচনী আইন ও আচরণবিধির মারাত্মক লঙ্ঘন ও গোলযোগ',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এবং নির্বাচন আচরণ বিধিমালা, ২০০৮',
          remedies: [
            'বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট ও পর্যাপ্ত নিরাপত্তা বাহিনী মোতায়েনপূর্বক তাৎক্ষণিক আইনানুগ ব্যবস্থা গ্রহণ।'
          ]
        };
    }
  }

  markComplaintSubmitted() {
    const inc = this.selectedIncidentForComplaint();
    if (!inc) return;
    this.api.updateCandidateIncidentStatus(this.electionId, inc.id, {
      status: 'SUBMITTED_TO_EC',
      officialComplaintGenerated: true
    }).subscribe({
      next: () => {
        this.incidents.update(list => list.map(i => i.id === inc.id ? { ...i, status: 'SUBMITTED_TO_EC', officialComplaintGenerated: true } : i));
        alert('লিখিত অভিযোগটি সহকারী রিটার্নিং অফিসার ও বিজ্ঞ ম্যাজিস্ট্রেটের কার্যালয়ে দাখিল হিসেবে চিহ্নিত করা হয়েছে।');
      }
    });
  }

  // =========================================================================
  // CAMPAIGN EVENTS, RALLIES & ROUTE PERMIT METHODS (বিকল্প ৩)
  // =========================================================================
  loadCampaignEvents() {
    this.loadingCampaign.set(true);
    forkJoin({
      events: this.api.getCampaignEvents(this.electionId),
      venues: this.api.getCampaignVenues(this.electionId)
    }).subscribe({
      next: res => {
        this.campaignEvents.set(res.events);
        this.campaignVenues.set(res.venues);
        this.loadingCampaign.set(false);
      },
      error: () => this.loadingCampaign.set(false)
    });
  }

  openAddCampaignModal() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const yyyy = tomorrow.getFullYear();
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const dd = String(tomorrow.getDate()).padStart(2, '0');

    this.newCampaignForm = {
      title: '',
      eventTypeId: 1,
      venueId: this.campaignVenues()[0]?.venueId || '',
      newVenueName: '',
      newVenueAddress: '',
      newVenueCapacity: null,
      startsAt: `${yyyy}-${mm}-${dd}T15:00`,
      endsAt: `${yyyy}-${mm}-${dd}T18:00`,
      issuingAuthority: 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার',
      permitReferenceNumber: `আবেদন-${yyyy}${mm}${dd}`,
      permitStateId: 1,
      description: ''
    };
    this.showAddCampaignModal.set(true);
  }

  closeAddCampaignModal() {
    this.showAddCampaignModal.set(false);
  }

  isNewEventMikingCompliant(): boolean {
    if (!this.newCampaignForm.startsAt || !this.newCampaignForm.endsAt) return true;
    try {
      const s = new Date(this.newCampaignForm.startsAt);
      const e = new Date(this.newCampaignForm.endsAt);
      const sHour = s.getHours();
      const eHour = e.getHours();
      const eMin = e.getMinutes();
      return sHour >= 14 && (eHour < 20 || (eHour === 20 && eMin === 0));
    } catch {
      return true;
    }
  }

  submitNewCampaignEvent() {
    if (!this.newCampaignForm.title.trim() || !this.newCampaignForm.startsAt || !this.newCampaignForm.endsAt) {
      alert('অনুগ্রহ করে কর্মসূচির শিরোনাম, শুরুর ও সমাপ্তির সময় দিন।');
      return;
    }
    const sDate = new Date(this.newCampaignForm.startsAt);
    const eDate = new Date(this.newCampaignForm.endsAt);
    if (eDate <= sDate) {
      alert('সমাপ্তির সময় অবশ্যই শুরুর সময়ের পরবর্তী হতে হবে।');
      return;
    }

    this.savingCampaignEvent.set(true);
    const req: CreateCampaignEventRequest = {
      title: this.newCampaignForm.title.trim(),
      eventTypeId: Number(this.newCampaignForm.eventTypeId) || 1,
      venueId: this.newCampaignForm.venueId || undefined,
      newVenueName: this.newCampaignForm.venueId ? undefined : this.newCampaignForm.newVenueName,
      newVenueAddress: this.newCampaignForm.venueId ? undefined : this.newCampaignForm.newVenueAddress,
      newVenueCapacity: this.newCampaignForm.venueId ? undefined : (this.newCampaignForm.newVenueCapacity || undefined),
      startsAt: sDate.toISOString(),
      endsAt: eDate.toISOString(),
      issuingAuthority: this.newCampaignForm.issuingAuthority,
      permitReferenceNumber: this.newCampaignForm.permitReferenceNumber,
      permitStateId: Number(this.newCampaignForm.permitStateId) || 1,
      description: this.newCampaignForm.description
    };

    this.api.createCampaignEvent(this.electionId, req).subscribe({
      next: created => {
        this.campaignEvents.update(list => [...list, created]);
        this.savingCampaignEvent.set(false);
        this.closeAddCampaignModal();
        this.loadCampaignEvents();
      },
      error: err => {
        alert(err?.error || 'কর্মসূচি সংরক্ষণ করা যায়নি।');
        this.savingCampaignEvent.set(false);
      }
    });
  }

  openUpdatePermitModal(ev: CandidateCampaignEventItem) {
    this.selectedEventForPermit.set(ev);
    this.updatePermitForm = {
      permitStateId: ev.permitStateId || 2,
      issuingAuthority: ev.issuingAuthority || 'দাগনভূঞা থানা পুলিশ ও উপজেলা প্রশাসন',
      permitReferenceNumber: ev.permitReferenceNumber || '',
      expiresOn: ev.permitExpiresOn || ''
    };
    this.showUpdatePermitModal.set(true);
  }

  closeUpdatePermitModal() {
    this.showUpdatePermitModal.set(false);
    this.selectedEventForPermit.set(null);
  }

  submitUpdatePermit() {
    const ev = this.selectedEventForPermit();
    if (!ev) return;
    this.savingCampaignPermit.set(true);
    const req: UpdateCampaignEventPermitRequest = {
      permitStateId: Number(this.updatePermitForm.permitStateId),
      issuingAuthority: this.updatePermitForm.issuingAuthority,
      permitReferenceNumber: this.updatePermitForm.permitReferenceNumber,
      permitExpiresOn: this.updatePermitForm.expiresOn || undefined
    };

    this.api.updateCampaignEventPermit(this.electionId, ev.eventId, req).subscribe({
      next: () => {
        this.savingCampaignPermit.set(false);
        this.closeUpdatePermitModal();
        this.loadCampaignEvents();
      },
      error: () => this.savingCampaignPermit.set(false)
    });
  }

  openPrintPermitNotice(ev: CandidateCampaignEventItem) {
    this.selectedEventForNotice.set(ev);
    this.showPrintPermitNoticeModal.set(true);
  }

  closePrintPermitNotice() {
    this.showPrintPermitNoticeModal.set(false);
    this.selectedEventForNotice.set(null);
  }

  deleteCampaignEvent(ev: CandidateCampaignEventItem) {
    if (!confirm(`আপনি কি "${ev.title}" কর্মসূচিটি বাতিল ও মুছে ফেলতে চান?`)) return;
    this.api.deleteCampaignEvent(this.electionId, ev.eventId).subscribe({
      next: () => {
        this.campaignEvents.update(list => list.filter(e => e.eventId !== ev.eventId));
      }
    });
  }
"""

if "submitNewCampaignEvent() {" not in content:
    idx_last_brace = content.rfind("}")
    if idx_last_brace != -1:
        content = content[:idx_last_brace] + methods + "\n}\n"
        print("Methods appended successfully.")
    else:
        print("ERROR: closing brace not found.")
else:
    print("Methods already present.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("fix_war_room_structure.py complete.")
