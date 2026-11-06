import os

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state variable for complaint recipient
target_signal = "  readonly selectedIncidentForComplaint = signal<CandidateIncidentSummary | null>(null);"
replacement_signal = """  readonly selectedIncidentForComplaint = signal<CandidateIncidentSummary | null>(null);
  complaintRecipientType = 'ARO_AND_MAGISTRATE';"""

if target_signal in content:
    content = content.replace(target_signal, replacement_signal, 1)
    print("Recipient state added.")
else:
    print("ERROR: could not find target_signal")

# 2. Add methods: getStatutoryViolationClauses, markComplaintSubmitted, getRecipientDesignation
target_methods = """  openComplaintLetter(incident: CandidateIncidentSummary) {
    this.selectedIncidentForComplaint.set(incident);
  }

  closeComplaintLetter() {
    this.selectedIncidentForComplaint.set(null);
  }"""

replacement_methods = """  openComplaintLetter(incident: CandidateIncidentSummary) {
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
            'বহিষ্কারের সাথে জড়িত প্রিজাইডিং অফিসার / সহকারী প্রিজাইডিং অফিসার ও সন্ত্রাসীদের বিরুদ্ধে আরপিও-র অনুচ্ছেদ ৮০ অনুযায়ী তাৎক্ষণিক আইনি ব্যবস্থা গ্রহণ করা।',
            'এজেন্টের অনুপস্থিতিতে জোরপূর্বক প্রদত্ত বা সিলমারা ব্যালট পেপার তাৎক্ষণিক পরীক্ষা করে বাতিল ও জব্দ করা।'
          ]
        };
      case 'FAKE_VOTING':
        return {
          title: 'জাল ভোট প্রদান, ব্যালট পেপার ছিনতাই ও ভুয়া ভোটাধিকার প্রয়োগ',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৩(১), ৭৪(১) এবং দণ্ডবিধি, ১৮৬০ এর সংশ্লিষ্ট ধারা',
          remedies: [
            'জাল ভোট প্রদানকারী ও ব্যালট ছিনতাইকারী চক্রকে হাতেনাতে গ্রেফতার ও মোবাইল কোর্টে তাৎক্ষণিক দণ্ড প্রদান।',
            'উক্ত বুথের ব্যবহৃত ব্যালট পেপারের কাউন্টারফয়েল এবং ভোটার তালিকা তাৎক্ষণিক বিজ্ঞ ম্যাজিস্ট্রেটের উপস্থিতিতে জব্দ ও নিরীক্ষা করা।',
            'প্রয়োজনে গণপ্রতিনিধিত্ব আদেশ, ১৯৭২ এর অনুচ্ছেদ ৩১ অনুযায়ী উক্ত কেন্দ্রের ভোটগ্রহণ সাময়িক স্থগিত ঘোষণা করা।'
          ]
        };
      case 'VOTER_OBSTRUCTION':
        return {
          title: 'ভোটকেন্দ্রে প্রবেশের রাস্তায় প্রতিবন্ধকতা সৃষ্টি, ভোটারদের মারধর ও ভয়ভীতি প্রদর্শন',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৩(২)(ক), ৭৪(১) ও আচরণ বিধিমালা বিধি ১১',
          remedies: [
            'ভোটকেন্দ্রের চতুর্দিকে ১০০০ গজ সীমানায় বিজিবি, র্যাব ও পুলিশের সার্বক্ষণিক স্ট্রাইকিং মোবাইল পেট্রোলিং জোরদার করা।',
            'ভোটারদের নির্বিঘ্নে কেন্দ্রে আগমন ও ভোটাধিকার প্রয়োগের অনুকূল নিরাপত্তা বলয় তৈরি করা।',
            'ত্রাস সৃষ্টিকারী সশস্ত্র সন্ত্রাসীদের চিহ্নিত করে অনতিবিলম্বে গ্রেফতার করা।'
          ]
        };
      case 'CENTER_CAPTURE':
        return {
          title: 'ভোটকেন্দ্র দখল, অস্ত্র প্রদর্শন এবং ব্যালট বাক্স ছিনতাইয়ের অপচেষ্টা',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৭৩, ৭৪, ৭৭ এবং অস্ত্র আইন, ১৮৭৮',
          remedies: [
            'কেন্দ্রে অবিলম্বে অতিরিক্ত স্ট্রাইকিং ফোর্স (BGB/RAB) মোতায়েন করে কেন্দ্র সম্পূর্ণ দখলমুক্ত ও নিরাপদ করা।',
            'আরপিও-র অনুচ্ছেদ ৩১ অনুযায়ী ভোটগ্রহণ অবিলম্বে সাময়িক স্থগিত ঘোষণা করে ম্যাজিস্ট্রেট কর্তৃক পরিস্থিতির পূর্ণ নিয়ন্ত্রণ গ্রহণ করা।',
            'সন্ত্রাসী ও অস্ত্রধারীদের বিরুদ্ধে নিয়মিত ফৌজদারি মামলা দায়ের পূর্বক গ্রেফতার নিশ্চিত করা।'
          ]
        };
      case 'PRESIDING_BIAS':
        return {
          title: 'নির্বাচনী কর্মকর্তা কর্তৃক পক্ষপাতমূলক আচরণ ও অনিয়মে সহায়তা',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এর অনুচ্ছেদ ৮০ (Breach of Official Duty)',
          remedies: [
            'পক্ষপাতদুষ্ট প্রিজাইডিং অফিসার / সহকারী প্রিজাইডিং অফিসারকে নির্বাচনী দায়িত্ব থেকে তাৎক্ষণিক প্রত্যাহার করা।',
            'নিরপেক্ষ বিকল্প কর্মকর্তা নিয়োগ করে ভোটগ্রহণের স্বচ্ছতা ও নিরপেক্ষতা নিশ্চিত করা।',
            'নির্বাচনী দায়িত্বে অবহেলা ও পক্ষপাতিত্বের দায়ে সংশ্লিষ্ট কর্মকর্তার বিরুদ্ধে আইনি ব্যবস্থা গ্রহণ করা।'
          ]
        };
      default:
        return {
          title: 'নির্বাচনী আচরণবিধি লঙ্ঘন, অনিয়ম ও নিরপেক্ষ পরিবেশ বিনষ্টকরণ',
          clauses: 'গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এবং নির্বাচন আচরণ বিধিমালা, ২০০৮',
          remedies: [
            'বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট কর্তৃক ঘটনাস্থলে সরেজমিনে তদন্তপূর্বক তাৎক্ষণিক ভ্রাম্যমাণ আদালত পরিচালনা।',
            'কেন্দ্রের সার্বিক আইনশৃঙ্খলা পুনঃপ্রতিষ্ঠা এবং ভোটার ও পোলিং এজেন্টদের পূর্ণ নিরাপত্তা বিধান করা।'
          ]
        };
    }
  }

  markComplaintSubmitted() {
    const inc = this.selectedIncidentForComplaint();
    if (!inc) return;
    this.updateIncidentStatus(inc, 'SUBMITTED_TO_EC');
    alert('অভিযোগটি সহকারী রিটার্নিং অফিসার ও ম্যাজিস্ট্রেট বরাবরে আনুষ্ঠানিকভাবে দাখিল হিসেবে সিস্টেমে নথিভুক্ত করা হয়েছে।');
  }"""

if target_methods in content:
    content = content.replace(target_methods, replacement_methods, 1)
    print("Methods updated successfully.")
else:
    print("ERROR: could not find target_methods")

# 3. Replace the complaint modal template
target_modal = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: OFFICIAL MAGISTRATE & RETURNING OFFICER COMPLAINT -->
    <!-- ===================================================================== -->
    @if(selectedIncidentForComplaint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>ম্যাজিস্ট্রেট ও রিটার্নিং অফিসার অভিযোগপত্র (Legal Complaint)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeComplaintLetter()">✕</button>
            </div>
          </div>

          <div class="official-complaint-paper">
            <div class="complaint-head">
              <div class="gov-seal">🇧🇩</div>
              <h3>নির্বাচনী আচরণবিধি লঙ্ঘন ও অনিয়ম প্রতিকারের আবেদন</h3>
              <p class="complaint-sub">জাতীয় সংসদ নির্বাচন / স্থানীয় সরকার নির্বাচন ২০২৬</p>
            </div>

            <div class="complaint-date-ref">
              <span>তারিখ: {{selectedIncidentForComplaint()!.reportedAt | date:'dd MMMM yyyy, hh:mm a'}}</span>
              <span>স্মারক নং: EEMS-COMPLAINT/{{selectedIncidentForComplaint()!.id.slice(0,8).toUpperCase()}}</span>
            </div>

            <div class="complaint-recipient">
              <p><b>বরাবর,</b><br/>
              সহকারী রিটার্নিং অফিসার / বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট,<br/>
              {{data()!.areaName || 'নির্বাচনী আসন'}}।</p>
            </div>

            <div class="complaint-subject">
              <b>বিষয়: {{selectedIncidentForComplaint()!.centerName}}-এ নির্বাচনী অনিয়ম/আইনশৃঙ্খলা বিঘ্ন প্রসঙ্গে জরুরি হস্তক্ষেপ ও আইনানুগ ব্যবস্থা গ্রহণ।</b>
            </div>

            <div class="complaint-body-text">
              <p>মহোদয়,</p>
              <p> যথাবিহিত সম্মান প্রদর্শনপূর্বক বিনীত নিবেদন এই যে, অদ্য অনুষ্ঠিত নির্বাচনে আমি অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b> (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</b>)-এর পক্ষে দায়িত্ব পালন করছি।</p>
              
              <p>অত্যন্ত উদ্বেগের সাথে জানাচ্ছি যে, অদ্য আনুমানিক <b>{{selectedIncidentForComplaint()!.reportedAt | date:'hh:mm a'}}</b> ঘটিকায় <b>{{selectedIncidentForComplaint()!.centerName}}</b>-এর <b>{{selectedIncidentForComplaint()!.boothName || 'ভোটকেন্দ্রে'}}</b> নিম্নলিখিত ঘটনাটি সংঘটিত হয়েছে:</p>

              <div class="incident-statement-box">
                <b>ঘটনার বিবরণ:</b>
                <p>{{selectedIncidentForComplaint()!.description}}</p>
                <p><b>ঘটনার তীব্রতা:</b> {{selectedIncidentForComplaint()!.severity}} | <b>ঘটনার ধরন:</b> {{selectedIncidentForComplaint()!.incidentType}}</p>
                <p><b>ঘটনাস্থলে উপস্থিত প্রত্যক্ষদর্শী/প্রতিবেদনকারী:</b> {{selectedIncidentForComplaint()!.reportedBy}} (মোবাইল: {{selectedIncidentForComplaint()!.reportedByPhone || 'উপলব্ধ নয়'}})</p>
              </div>

              <p>উল্লিখিত ঘটনার ফলে উক্ত ভোটকেন্দ্রে সুষ্ঠু ও নিরপেক্ষ ভোটগ্রহণ মারাত্মকভাবে ব্যাহত হচ্ছে এবং আমাদের ভোটার ও পোলিং এজেন্টরা চরম নিরাপত্তাহীনতায় ভুগছেন।</p>

              <p><b>অতএব প্রার্থনা:</b> মহোদয় অবিলম্বে সরেজমিনে উক্ত ভোটকেন্দ্রে প্রয়োজনীয় স্ট্রাইকিং ফোর্স ও জুডিশিয়াল ম্যাজিস্ট্রেট প্রেরণপূর্বক দোষীদের বিরুদ্ধে কঠোর আইনানুগ ব্যবস্থা গ্রহণ এবং কেন্দ্রে ভোটার ও এজেন্টদের পূর্ণ নিরাপত্তা নিশ্চিত করতে আপনার সদয় মর্জি হয়।</p>
            </div>

            <div class="complaint-sig-row">
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{selectedIncidentForComplaint()!.reportedBy}}</b><br/>
                <span>ঘটনাস্থলে উপস্থিত এজেন্ট / প্রত্যক্ষদর্শী</span>
              </div>
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b><br/>
                <span>প্রতিদ্বন্দ্বী প্রার্থী / প্রধান নির্বাচনী এজেন্ট</span><br/>
                <span>প্রতীক: {{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    }"""

replacement_modal = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: OFFICIAL MAGISTRATE & ARO LEGAL COMPLAINT -->
    <!-- ===================================================================== -->
    @if(selectedIncidentForComplaint()){
      <div class="modal-backdrop print-modal-backdrop">
        <div class="card modal-card print-preview-card complaint-modal-card">
          <!-- Control Toolbar (Hidden in Print) -->
          <div class="modal-header complaint-toolbar no-print">
            <div class="complaint-titles">
              <h2>⚖️ ম্যাজিস্ট্রেট ও সহকারী রিটার্নিং অফিসার (ARO) অভিযোগপত্র</h2>
              <p class="subtitle">নির্বাচনী অনিয়ম, গোলযোগ ও আচরণবিধি লঙ্ঘনের বিরুদ্ধে তাৎক্ষণিক আইনগত প্রতিকার আবেদন</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button-sm outline-btn" (click)="markComplaintSubmitted()" title="প্রশাসনে দাখিল সম্পন্ন হিসেবে মার্ক করুন">
                📤 প্রশাসনে দাখিল সম্পন্ন
              </button>
              <button class="primary-button" (click)="triggerBrowserPrint()">
                🖨️ আইনি অভিযোগপত্র প্রিন্ট (A4)
              </button>
              <button class="close-btn" (click)="closeComplaintLetter()">✕</button>
            </div>
          </div>

          <!-- Recipient Selector Toolbar (Hidden in Print) -->
          <div class="complaint-control-bar no-print">
            <div class="control-grp">
              <label>অভিযোগের প্রাপক পদবি:</label>
              <select [(ngModel)]="complaintRecipientType">
                <option value="ARO_AND_MAGISTRATE">সহকারী রিটার্নিং অফিসার এবং বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট (যৌথভাবে)</option>
                <option value="ARO">সহকারী রিটার্নিং অফিসার ও উপজেলা নির্বাহী অফিসার (ইউএনও)</option>
                <option value="MAGISTRATE">বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট / জুডিশিয়াল ম্যাজিস্ট্রেট (ভ্রাম্যমাণ আদালত)</option>
                <option value="RO">মাননীয় রিটার্নিং অফিসার ও জেলা ম্যাজিস্ট্রেট / জেলা প্রশাসক</option>
              </select>
            </div>
            <div class="control-status">
              <span>বর্তমান স্ট্যাটাস: <b>{{selectedIncidentForComplaint()!.status}}</b></span>
            </div>
          </div>

          <!-- Official Complaint Paper (A4 Printable Document) -->
          <div class="official-complaint-paper">
            <!-- Header Pad -->
            <div class="complaint-head">
              <div class="gov-seal">🇧🇩</div>
              <div class="c-org-title">গণপ্রজাতন্ত্রী বাংলাদেশ · নির্বাচন ২০২৬</div>
              <div class="c-candidate-office">প্রার্থীর কেন্দ্রীয় নির্বাচন পরিচালনা কার্যালয়</div>
              <h3>নির্বাচনী অপরাধ, অনিয়ম ও আচরণবিধি লঙ্ঘন প্রতিকারের আবেদন</h3>
              <p class="complaint-sub">[গণপ্রতিনিধিত্ব আদেশ (RPO), ১৯৭২ এবং সংসদ নির্বাচন আচরণ বিধিমালা অনুযায়ী প্রস্তুতকৃত]</p>
            </div>

            <!-- Date & Memo Row -->
            <div class="complaint-date-ref">
              <span><b>স্মারক নং:</b> EEMS/COMPLAINT/2026/{{selectedIncidentForComplaint()!.id.slice(0,8).toUpperCase()}}</span>
              <span><b>তারিখ ও সময়:</b> {{selectedIncidentForComplaint()!.reportedAt | date:'dd MMMM yyyy, hh:mm a'}}</span>
            </div>

            <!-- Recipient Box -->
            <div class="complaint-recipient">
              <p><b>বরাবর,</b><br/>
              <b>{{getRecipientDesignation()}},</b><br/>
              উপজেলা প্রশাসন ও নির্বাচনী কার্যালয়,<br/>
              {{data()?.areaName || '৫ নং ইয়াকুবপুর ইউনিয়ন · দাগনভূঞা, ফেনী'}}।</p>
            </div>

            <!-- Subject -->
            <div class="complaint-subject">
              <b>বিষয়: {{selectedIncidentForComplaint()!.centerName}}-এ {{getStatutoryViolationClauses(selectedIncidentForComplaint()!.incidentType).title}} প্রসঙ্গে জরুরি হস্তক্ষেপ ও আইনানুগ কঠোর ব্যবস্থা গ্রহণ।</b>
            </div>

            <!-- Body Text -->
            <div class="complaint-body-text">
              <p>মহোদয়,</p>
              <p>যথাবিহিত সম্মান প্রদর্শনপূর্বক বিনীত নিবেদন এই যে, অদ্য অনুষ্ঠিত নির্বাচনে আমি অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b> (বরাদ্দকৃত প্রতীক: <b>{{data()?.candidate?.symbolEmoji || '⚖️'}} {{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</b>, দল: <b>{{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</b>)-এর প্রধান নির্বাচনী এজেন্ট হিসেবে দায়িত্ব পালন করছি।</p>
              
              <p>অত্যন্ত উদ্বেগের সাথে আপনাকে জানাচ্ছি যে, অদ্য আনুমানিক <b>{{selectedIncidentForComplaint()!.reportedAt | date:'hh:mm a'}}</b> ঘটিকায় <b>{{selectedIncidentForComplaint()!.centerName}} (কেন্দ্র কোড: {{selectedIncidentForComplaint()!.centerCode || 'C-101'}})</b>-এর <b>{{selectedIncidentForComplaint()!.boothName || 'সকল ভোটকক্ষে'}}</b> নিম্নলিখিত মারাত্মক আইনবিরোধী ঘটনাটি সংঘটিত হয়েছে:</p>

              <!-- Incident Fact Box -->
              <div class="incident-statement-box">
                <div class="fact-row"><b>১. ঘটনার বিবরণ:</b> <span class="fact-text">{{selectedIncidentForComplaint()!.description}}</span></div>
                <div class="fact-row"><b>২. অপরাধের ধরন ও তীব্রতা:</b> <span>{{selectedIncidentForComplaint()!.incidentType}} | {{selectedIncidentForComplaint()!.severity === 'CRITICAL' ? 'মারাত্মক জরুরি (CRITICAL)' : 'গুরুতর (HIGH)'}}</span></div>
                <div class="fact-row"><b>৩. লঙ্ঘনকৃত সংবিধিবদ্ধ আইন:</b> <span class="legal-clause-tag">{{getStatutoryViolationClauses(selectedIncidentForComplaint()!.incidentType).clauses}}</span></div>
                <div class="fact-row"><b>৪. ঘটনাস্থলে উপস্থিত প্রত্যক্ষদর্শী/প্রতিবেদনকারী:</b> <span>{{selectedIncidentForComplaint()!.reportedBy}} (মোবাইল: {{selectedIncidentForComplaint()!.reportedByPhone || 'উপলব্ধ নয়'}})</span></div>
              </div>

              <p>উল্লিখিত সন্ত্রাসী কার্যকলাপ ও আইনবিরোধী আচরণের ফলে অত্র ভোটকেন্দ্রে ভোটারদের উপস্থিতি মারাত্মকভাবে বাধাগ্রস্ত হচ্ছে, আমাদের পোলিং এজেন্টদের ভয়ভীতি প্রদর্শন করে কেন্দ্র ছাড়া করা হয়েছে এবং ভোটগ্রহণের সুষ্ঠু ও নিরপেক্ষ পরিবেশ সম্পূর্ণরূপে বিনষ্ট হচ্ছে।</p>

              <!-- Prayers / Remedies Requested -->
              <div class="complaint-prayers-box">
                <b>অতএব, মহোদয়ের সমীপে বিনীত প্রার্থনা:</b>
                <ol class="prayers-list">
                  @for(rem of getStatutoryViolationClauses(selectedIncidentForComplaint()!.incidentType).remedies; track rem){
                    <li>{{rem}}</li>
                  }
                </ol>
                <p class="prayer-conclusion">উক্ত ভোটকেন্দ্রে অবাধ, সুষ্ঠু ও নিরপেক্ষ নির্বাচন নিশ্চিতকল্পে আপনার দ্রুত ও দৃষ্টান্তমূলক আইনি হস্তক্ষেপ একান্তভাবে কামনা করছি।</p>
              </div>
            </div>

            <!-- Signatures Row -->
            <div class="complaint-sig-row">
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{selectedIncidentForComplaint()!.reportedBy}}</b><br/>
                <span>ঘটনাস্থলে উপস্থিত প্রত্যক্ষদর্শী / পোলিং এজেন্ট</span><br/>
                <span>মোবাইল: {{selectedIncidentForComplaint()!.reportedByPhone || '—'}}</span>
              </div>
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b><br/>
                <span>প্রতিদ্বন্দ্বী প্রার্থী / প্রধান নির্বাচনী এজেন্ট</span><br/>
                <span>প্রতীক: {{data()?.candidate?.symbolEmoji || '⚖️'}} {{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</span><br/>
                <span class="office-seal-text">(প্রার্থীর সিল ও স্বাক্ষর)</span>
              </div>
            </div>

            <!-- Carbon Copies (অনুলিপি) -->
            <div class="complaint-copies-section">
              <div class="copies-title">অনুলিপি সদয় অবগতি ও তাৎক্ষণিক প্রয়োজনীয় ব্যবস্থা গ্রহণের জন্য প্রেরিত হইল:</div>
              <ol class="copies-list">
                <li>মাননীয় রিটার্নিং অফিসার ও জেলা ম্যাজিস্ট্রেট / জেলা প্রশাসক, ফেনী জেলা।</li>
                <li>পুলিশ সুপার (SP), ফেনী জেলা ও সংশ্লিষ্ট সার্কেল এএসপি।</li>
                <li>ক্যাম্প কমান্ডার, বিজিবি ও র্যাব স্ট্রাইকিং ফোর্স (দাগনভূঞা নির্বাচনী এরিয়া)।</li>
                <li>ভারপ্রাপ্ত কর্মকর্তা (ওসি), দাগনভূঞা থানা।</li>
                <li>আইন ও নির্বাচন পরিচালনা অনুবিভাগ, বাংলাদেশ নির্বাচন কমিশন সচিবালয়, আগারগাঁও, ঢাকা।</li>
                <li>অফিস নথি / নির্বাচনী মিডিয়া সেল।</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    }"""

if target_modal in content:
    content = content.replace(target_modal, replacement_modal, 1)
    print("Complaint Modal template replaced successfully.")
else:
    print("ERROR: could not find target_modal")

# 4. Enhance CSS for complaint paper
old_css_complaint = """    /* Complaint Legal Paper */
    .official-complaint-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 750px; margin: 0 auto; }"""

new_css_complaint = """    /* Complaint Legal Paper */
    .complaint-modal-card { width: min(860px, 98vw); max-height: 94vh; overflow-y: auto; background: #f1f5f9; padding: 24px; }
    .complaint-toolbar { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px; }
    .complaint-titles h2 { margin: 0 0 4px 0; color: #082136; font-size: 1.25rem; font-weight: 800; }
    .complaint-titles .subtitle { margin: 0; font-size: 0.8rem; color: #64748b; }
    .complaint-control-bar { display: flex; justify-content: space-between; align-items: center; background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px 16px; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
    .control-grp { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; }
    .control-grp label { font-weight: 700; color: #1e293b; }
    .control-grp select { border: 1px solid #94a3b8; border-radius: 6px; padding: 6px 10px; font-size: 0.82rem; background: #f8fafc; color: #0f172a; outline: none; }
    .control-status span { font-size: 0.82rem; color: #475569; }
    .outline-btn { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-weight: 700; padding: 7px 12px; border-radius: 6px; cursor: pointer; }
    .outline-btn:hover { background: #dbeafe; }

    .official-complaint-paper { background: #fff; padding: 40px 48px; font-family: "Hind Siliguri", "Segoe UI", sans-serif; line-height: 1.6; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 800px; margin: 0 auto; box-sizing: border-box; }
    .c-org-title { font-size: 0.76rem; font-weight: 700; color: #475569; letter-spacing: 0.04em; }
    .c-candidate-office { font-size: 0.88rem; font-weight: 800; color: #082136; margin: 2px 0 4px 0; }
    .incident-statement-box { background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 14px 16px; margin: 16px 0; font-size: 0.88rem; display: flex; flex-direction: column; gap: 6px; }
    .fact-row { display: flex; gap: 8px; }
    .fact-row b { width: 170px; flex-shrink: 0; color: #1e293b; }
    .fact-text { font-style: italic; color: #0f172a; }
    .legal-clause-tag { color: #b91c1c; font-weight: 700; }
    .complaint-prayers-box { margin-top: 16px; font-size: 0.9rem; }
    .prayers-list { margin: 8px 0 12px 24px; padding: 0; display: flex; flex-direction: column; gap: 4px; font-size: 0.88rem; line-height: 1.5; }
    .prayer-conclusion { font-style: italic; margin-top: 8px; font-size: 0.85rem; }
    .office-seal-text { font-size: 0.72rem; color: #64748b; font-style: italic; }
    .complaint-copies-section { margin-top: 36px; border-top: 1px solid #94a3b8; padding-top: 10px; font-size: 0.75rem; color: #334155; }
    .copies-title { font-weight: 800; margin-bottom: 4px; }
    .copies-list { margin: 0 0 0 20px; padding: 0; line-height: 1.5; }"""

if old_css_complaint in content:
    content = content.replace(old_css_complaint, new_css_complaint, 1)
    print("Complaint CSS updated.")
else:
    print("ERROR: could not find old_css_complaint")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Magistrate Complaint patch applied successfully!")

