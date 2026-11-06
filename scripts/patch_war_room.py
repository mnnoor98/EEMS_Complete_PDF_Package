# -*- coding: utf-8 -*-
import sys

file_path = r'frontend/src/app/features/candidates/candidate-war-room.page.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modals to insert before closing template `\n  `,\n  styles:`
modals_html = """
    <!-- ===================================================================== -->
    <!-- MODAL: ADD NEW VOTER -->
    <!-- ===================================================================== -->
    @if(showAddVoterModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন ভোটার তথ্য এন্ট্রি</h2>
            <button class="close-btn" (click)="closeAddVoterModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewVoter()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র *</label>
                <select [(ngModel)]="newVoterForm.centerId" name="vCenter" required (change)="onVoterCenterChange()">
                  <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>নির্ধারিত বুথ (ঐচ্ছিক)</label>
                <select [(ngModel)]="newVoterForm.boothId" name="vBooth">
                  <option [ngValue]="null">সাধারণ / অনির্ধারিত বুথ</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>ভোটার তালিকা ক্রমিক নং *</label>
                <input type="number" [(ngModel)]="newVoterForm.serialNumber" name="vSerial" min="1" required>
              </div>

              <div class="form-field">
                <label>ভোটার নম্বর (Voter ID) *</label>
                <input [(ngModel)]="newVoterForm.voterNumber" name="vNumber" required placeholder="ভোটার নম্বর">
              </div>

              <div class="form-field">
                <label>ভোটারের নাম *</label>
                <input [(ngModel)]="newVoterForm.fullName" name="vName" required placeholder="ভোটারের পূর্ণ নাম">
              </div>

              <div class="form-field">
                <label>পিতা / স্বামীর নাম</label>
                <input [(ngModel)]="newVoterForm.fatherOrSpouseName" name="vFather" placeholder="পিতা বা স্বামীর নাম">
              </div>

              <div class="form-field">
                <label>লিঙ্গ</label>
                <select [(ngModel)]="newVoterForm.gender" name="vGender">
                  <option value="MALE">পুরুষ (Male)</option>
                  <option value="FEMALE">নারী (Female)</option>
                </select>
              </div>

              <div class="form-field">
                <label>বয়স</label>
                <input type="number" [(ngModel)]="newVoterForm.age" name="vAge" min="18" max="120" placeholder="বয়স">
              </div>

              <div class="form-field">
                <label>গ্রাম / পাড়া / এলাকা</label>
                <input [(ngModel)]="newVoterForm.areaName" name="vArea" placeholder="গ্রাম বা পাড়ার নাম">
              </div>

              <div class="form-field">
                <label>ক্যাটাগরি</label>
                <select [(ngModel)]="newVoterForm.category" name="vCat">
                  <option value="SUPPORTER">বিশ্বস্ত সমর্থক (SUPPORTER)</option>
                  <option value="SWING">নিরপেক্ষ / দোদুল্যমান (SWING)</option>
                  <option value="OPPONENT">প্রতিপক্ষ সমর্থক (OPPONENT)</option>
                  <option value="ABROAD">প্রবাসী / অনুপস্থিত (ABROAD)</option>
                </select>
              </div>

              <div class="form-field">
                <label>মোবাইল নম্বর</label>
                <input [(ngModel)]="newVoterForm.phone" name="vPhone" placeholder="017xxxxxxxx">
              </div>

              <div class="form-field wide">
                <label>মন্তব্য</label>
                <input [(ngModel)]="newVoterForm.notes" name="vNotes" placeholder="বিশেষ কোনো তথ্য থাকলে লিখুন">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddVoterModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingVoter()">
                {{savingVoter() ? 'সংরক্ষণ হচ্ছে…' : 'ভোটার যুক্ত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL: ADD NEW INCIDENT -->
    <!-- ===================================================================== -->
    @if(showAddIncidentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>🚨 নির্বাচনী অনিয়ম / গোলযোগ রেকর্ড</h2>
            <button class="close-btn" (click)="closeAddIncidentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewIncident()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র *</label>
                <select [(ngModel)]="newIncidentForm.centerId" name="iCenter" required (change)="onIncidentCenterChange()">
                  <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>বুথ (ঐচ্ছিক)</label>
                <select [(ngModel)]="newIncidentForm.boothId" name="iBooth">
                  <option [ngValue]="null">সকল বুথ / কেন্দ্র চত্বর</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>অনিয়মের ধরন *</label>
                <select [(ngModel)]="newIncidentForm.incidentType" name="iType" required>
                  <option value="BOOTH_AGENT_EXPELLED">পোলিং এজেন্টকে ঢুকতে বাধা / বের করে দেওয়া</option>
                  <option value="VOTER_INTIMIDATION">ভোটারদের ভয়ভীতি প্রদর্শন / বাধা</option>
                  <option value="BALLOT_STUFFING">জাল ভোট প্রদান / ব্যালট ছিনতাই</option>
                  <option value="VIOLENCE">কেন্দ্রে মারামারি / বিশৃঙ্খলা</option>
                  <option value="EQUIPMENT_FAILURE">ভোটগ্রহণ সরঞ্জাম / সিল সমস্যা</option>
                  <option value="OTHER">অন্যান্য অনিয়ম</option>
                </select>
              </div>

              <div class="form-field">
                <label>তীব্রতা (Severity) *</label>
                <select [(ngModel)]="newIncidentForm.severity" name="iSev" required>
                  <option value="CRITICAL">জরুরি হস্তক্ষেপ প্রয়োজন (CRITICAL)</option>
                  <option value="HIGH">উচ্চ গুরুতর (HIGH)</option>
                  <option value="MEDIUM">মাঝারি (MEDIUM)</option>
                  <option value="LOW">সাধারণ (LOW)</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>অভিযোগের শিরোনাম *</label>
                <input [(ngModel)]="newIncidentForm.title" name="iTitle" required placeholder="সংক্ষেপে মূল ঘটনা">
              </div>

              <div class="form-field wide">
                <label>বিস্তারিত বিবরণ *</label>
                <textarea [(ngModel)]="newIncidentForm.description" name="iDesc" required rows="4" placeholder="ঘটনা কখন, কারা এবং কীভাবে ঘটিয়েছে তা স্পষ্টভাবে লিখুন"></textarea>
              </div>

              <div class="form-field">
                <label>সংবাদদাতা / এজেন্টের নাম *</label>
                <input [(ngModel)]="newIncidentForm.reportedBy" name="iRep" required placeholder="নাম">
              </div>

              <div class="form-field">
                <label>সংবাদদাতার মোবাইল নম্বর</label>
                <input [(ngModel)]="newIncidentForm.reportedByPhone" name="iRepPhone" placeholder="017xxxxxxxx">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddIncidentModal()">বাতিল</button>
              <button class="primary-button alert-btn" [disabled]="savingIncident()">
                {{savingIncident() ? 'সংরক্ষণ হচ্ছে…' : 'অভিযোগ দাখিল করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: BATCH VOTER SLIPS (ভোটার স্লিপ) -->
    <!-- ===================================================================== -->
    @if(showVoterSlipsPrint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card wide-slip-modal">
          <div class="modal-header no-print">
            <h2>ভোটার স্লিপ প্রিন্ট প্রিভিউ (প্রার্থীর মার্কা ও ভোটার তথ্য)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeVoterSlipsPrint()">✕</button>
            </div>
          </div>

          <div class="voter-slips-page">
            <div class="voter-slips-grid">
              @for(v of voters(); track v.id){
                <div class="voter-slip-card">
                  <div class="slip-header">
                    <span class="slip-symbol-emoji">{{data()!.candidate?.symbolEmoji || '🗳️'}}</span>
                    <div class="slip-cand-info">
                      <b class="slip-cand-name">{{data()!.candidate?.name || 'প্রার্থীর নাম'}}</b>
                      <span class="slip-symbol-name">{{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn || 'মার্কা'}} মার্কা</span>
                    </div>
                  </div>
                  @if(data()!.candidate?.slogan){
                    <div class="slip-slogan">"{{data()!.candidate?.slogan}}"</div>
                  }
                  <div class="slip-body">
                    <div class="slip-serial-row">
                      <span>তালিকা ক্রমিক:</span>
                      <b class="slip-serial-num">{{v.serialNumber}}</b>
                    </div>
                    <div class="slip-row">
                      <span>ভোটারের নাম:</span>
                      <b>{{v.fullName}}</b>
                    </div>
                    <div class="slip-row">
                      <span>ভোটার নম্বর:</span>
                      <span>{{v.voterNumber}}</span>
                    </div>
                    <div class="slip-row">
                      <span>ভোটকেন্দ্র:</span>
                      <span>{{v.centerName}}</span>
                    </div>
                    @if(v.boothName){
                      <div class="slip-row">
                        <span>নির্ধারিত বুথ:</span>
                        <b>{{v.boothName}}</b>
                      </div>
                    }
                    @if(v.areaName){
                      <div class="slip-row">
                        <span>গ্রাম / এলাকা:</span>
                        <span>{{v.areaName}}</span>
                      </div>
                    }
                  </div>
                  <div class="slip-footer">
                    <span>আপনার মূল্যবান ভোট দিয়ে এলাকার উন্নয়নে অংশ নিন।</span>
                  </div>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
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
              <p>যথাবিহিত সম্মান প্রদর্শনপূর্বক বিনীত নিবেদন এই যে, অদ্য অনুষ্ঠিত নির্বাচনে আমি অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b> (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</b>)-এর পক্ষে দায়িত্ব পালন করছি।</p>
              
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
    }
"""

target_end_template = '            <div class="badge-footer">\n              <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>\n            </div>\n          </div>\n        </div>\n      </div>\n    }'
if target_end_template not in content:
    print('Error: target_end_template not found!')
    sys.exit(1)

content = content.replace(target_end_template, target_end_template + modals_html)

# 2. Add styles
extra_styles = """
    /* Voters Workspace */
    .voters-workspace, .incidents-workspace { padding: 22px; }
    .search-grp { display: flex; align-items: flex-end; gap: 6px; }
    .search-grp input { padding: 9px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 0.88rem; width: 220px; }
    .search-btn { background: var(--navy); color: #fff; border: none; border-radius: 8px; padding: 9px 12px; cursor: pointer; }
    .serial-pill { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 99px; font-size: 0.82rem; }
    .category-chip { padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .category-chip[data-cat="SUPPORTER"] { background: #dcfce7; color: #15803d; }
    .category-chip[data-cat="SWING"] { background: #fef9c3; color: #a16207; }
    .category-chip[data-cat="OPPONENT"] { background: #fee2e2; color: #b91c1c; }
    .category-chip[data-cat="ABROAD"] { background: #f1f5f9; color: #64748b; }
    .toggle-pill { border: 1px solid var(--line); background: #f8fafc; border-radius: 99px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
    .toggle-pill.done { background: #dcfce7; border-color: #86efac; color: #166534; }
    .vote-status-btn { border: 1px solid var(--line); background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; cursor: pointer; }
    .vote-status-btn.voted { background: var(--teal); border-color: var(--teal); color: #fff; }

    /* Incidents Workspace */
    .alert-btn { background: #dc2626 !important; }
    .alert-btn:hover { background: #b91c1c !important; }
    .incidents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; margin-top: 18px; }
    .incident-card { border: 1px solid var(--line); border-radius: 12px; padding: 18px; background: #fff; display: flex; flex-direction: column; gap: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-left: 5px solid #64748b; }
    .incident-card[data-severity="CRITICAL"] { border-left-color: #dc2626; background: #fffafa; }
    .incident-card[data-severity="HIGH"] { border-left-color: #ea580c; }
    .incident-card[data-severity="MEDIUM"] { border-left-color: #eab308; }
    .inc-head { display: flex; justify-content: space-between; align-items: center; }
    .severity-badge { font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; background: #fef08a; color: #854d0e; text-transform: uppercase; }
    .severity-badge.crit { background: #fee2e2; color: #991b1b; }
    .inc-time { font-size: 0.75rem; color: #64748b; }
    .inc-title { margin: 0; font-size: 1.05rem; color: var(--navy); }
    .inc-desc { margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.45; }
    .inc-meta-row { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 8px 12px; border-radius: 6px; }
    .action-taken-box { background: #ecfdf5; border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 0 6px 6px 0; font-size: 0.82rem; }
    .action-taken-box b { color: #065f46; display: block; margin-bottom: 2px; }
    .action-taken-box p { margin: 0 0 4px; color: #047857; }
    .action-taken-box small { color: #059669; font-weight: 600; }
    .inc-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; border-top: 1px solid #f1f5f9; padding-top: 12px; flex-wrap: wrap; gap: 8px; }
    .status-change-grp { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; }
    .status-change-grp select { padding: 4px 8px; border-radius: 6px; border: 1px solid var(--line); font-size: 0.78rem; }
    .inc-actions { display: flex; gap: 6px; }
    .print-complaint-btn { background: #f8fafc; border: 1px solid #cbd5e1; font-size: 0.75rem; padding: 5px 10px; }

    /* Voter Slips Print Paper */
    .wide-slip-modal { width: min(850px, 100%) !important; }
    .voter-slips-page { background: #fff; padding: 10px; }
    .voter-slips-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .voter-slip-card { border: 2px dashed #0e2942; border-radius: 10px; padding: 14px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; page-break-inside: avoid; }
    .slip-header { display: flex; align-items: center; gap: 10px; border-bottom: 1.5px solid #0e2942; padding-bottom: 6px; margin-bottom: 6px; }
    .slip-symbol-emoji { font-size: 2rem; line-height: 1; }
    .slip-cand-info { display: flex; flex-direction: column; }
    .slip-cand-name { font-size: 1rem; color: #0e2942; }
    .slip-symbol-name { font-size: 0.78rem; color: var(--teal); font-weight: 800; }
    .slip-slogan { font-size: 0.75rem; font-style: italic; color: #475569; margin-bottom: 8px; text-align: center; border-bottom: 1px dotted #cbd5e1; padding-bottom: 4px; }
    .slip-body { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; }
    .slip-serial-row { display: flex; justify-content: space-between; align-items: center; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; }
    .slip-serial-num { font-size: 1.25rem; color: #0e2942; }
    .slip-row { display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 1px solid #f8fafc; }
    .slip-row span { color: #64748b; }
    .slip-footer { font-size: 0.65rem; color: #475569; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 6px; margin-top: 8px; font-weight: 600; }

    /* Complaint Legal Paper */
    .official-complaint-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 750px; margin: 0 auto; }
    .complaint-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 18px; }
    .gov-seal { font-size: 2rem; }
    .complaint-head h3 { margin: 4px 0 2px; font-size: 1.3rem; }
    .complaint-sub { margin: 0; font-size: 0.88rem; color: #333; }
    .complaint-date-ref { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 16px; border-bottom: 1px dashed #999; padding-bottom: 6px; }
    .complaint-recipient { margin-bottom: 14px; font-size: 0.92rem; }
    .complaint-subject { margin-bottom: 16px; font-size: 0.95rem; border-left: 4px solid #000; padding-left: 10px; }
    .complaint-body-text { font-size: 0.92rem; text-align: justify; }
    .incident-statement-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; margin: 12px 0; font-size: 0.88rem; }
    .complaint-sig-row { display: flex; justify-content: space-between; margin-top: 50px; text-align: center; }
    .c-sig-block { width: 44%; }
    .c-sig-line { border-top: 1px solid #000; margin-bottom: 6px; }
"""

# Insert print media styles
media_print_target = '      .official-form9-paper, .official-form9-paper *,\n      .agent-badge-paper, .agent-badge-paper * {'
media_print_replacement = '      .official-form9-paper, .official-form9-paper *,\n      .agent-badge-paper, .agent-badge-paper *,\n      .voter-slips-page, .voter-slips-page *,\n      .official-complaint-paper, .official-complaint-paper * {'
content = content.replace(media_print_target, media_print_replacement)

media_print_target2 = '      .official-form9-paper, .agent-badge-paper {'
media_print_replacement2 = '      .official-form9-paper, .agent-badge-paper, .voter-slips-page, .official-complaint-paper {'
content = content.replace(media_print_target2, media_print_replacement2)

# Insert extra_styles before `@media print`
content = content.replace('    /* Media Print */', extra_styles + '\n    /* Media Print */')

# 3. Add Component signals and methods
signals_target = '  readonly selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);'
new_signals = """  readonly selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);

  readonly voters = signal<CandidateVoterSummary[]>([]);
  readonly incidents = signal<CandidateIncidentSummary[]>([]);
  readonly loadingVoters = signal(false);
  readonly loadingIncidents = signal(false);
  readonly savingVoter = signal(false);
  readonly savingIncident = signal(false);

  readonly showAddVoterModal = signal(false);
  readonly showAddIncidentModal = signal(false);
  readonly showVoterSlipsPrint = signal(false);
  readonly selectedIncidentForComplaint = signal<CandidateIncidentSummary | null>(null);

  voterSearch = '';
  voterFilterCenter = '';
  voterFilterCategory = '';
  voterFilterSlip = '';

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

  newIncidentForm = {
    centerId: '',
    boothId: null as string | null,
    incidentType: 'BOOTH_AGENT_EXPELLED',
    severity: 'HIGH',
    title: '',
    description: '',
    reportedBy: '',
    reportedByPhone: '',
    evidenceAttachmentUrl: ''
  };"""
content = content.replace(signals_target, new_signals)

# Update load() to load voters and incidents
load_target = """    forkJoin({
      warRoom: this.api.getCandidateWarRoom(this.electionId),
      symbols: this.api.getElectionSymbols(),
      agents: this.api.getBoothAgents(this.electionId),
      centers: this.api.getPollingCenters(this.electionId)
    }).subscribe({
      next: res => {
        this.data.set(res.warRoom);
        this.symbols.set(res.symbols);
        this.boothAgents.set(res.agents);
        this.centersList.set(res.centers.items);
        this.loading.set(false);
      },"""

load_replacement = """    forkJoin({
      warRoom: this.api.getCandidateWarRoom(this.electionId),
      symbols: this.api.getElectionSymbols(),
      agents: this.api.getBoothAgents(this.electionId),
      centers: this.api.getPollingCenters(this.electionId),
      voters: this.api.getCandidateVoters(this.electionId),
      incidents: this.api.getCandidateIncidents(this.electionId)
    }).subscribe({
      next: res => {
        this.data.set(res.warRoom);
        this.symbols.set(res.symbols);
        this.boothAgents.set(res.agents);
        this.centersList.set(res.centers.items);
        this.voters.set(res.voters);
        this.incidents.set(res.incidents);
        this.loading.set(false);
      },"""
content = content.replace(load_target, load_replacement)

# Add setTab logic
tab_switch_target = "    if (tab === 'agents' && this.boothAgents().length === 0) {\n      this.loadBoothAgents();\n    }"
tab_switch_replacement = """    if (tab === 'agents' && this.boothAgents().length === 0) {
      this.loadBoothAgents();
    } else if (tab === 'voters') {
      this.loadVoters();
    } else if (tab === 'incidents') {
      this.loadIncidents();
    }"""
content = content.replace(tab_switch_target, tab_switch_replacement)

# Add methods at the bottom of CandidateWarRoomPage
methods_target = "  triggerBrowserPrint() {\n    window.print();\n  }\n}"
new_methods = """  triggerBrowserPrint() {
    window.print();
  }

  // Voter Methods
  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearch || undefined
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

  // Incident Methods
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
}"""
content = content.replace(methods_target, new_methods)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied successfully!')

