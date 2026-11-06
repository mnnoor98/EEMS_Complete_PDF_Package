file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if '<!-- PRINTABLE VIEW: OFFICIAL MAGISTRATE & RETURNING OFFICER COMPLAINT -->' in line:
        start_idx = i - 1  # include the separator comment
        break

for i in range(start_idx, len(lines)):
    if '<!-- MODAL: ADD EXPENSE VOUCHER -->' in lines[i]:
        end_idx = i - 1
        break

print(f"Replacing lines {start_idx} to {end_idx}")

replacement_lines = """    <!-- ===================================================================== -->
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
              <b>বিষয়: {{selectedIncidentForComplaint()!.centerName}}-এ {{getStatutoryViolationClauses(selectedIncidentForComplaint()!.incidentType).title}} প্রসঙ্গে জরুরি ম্যাজিস্ট্রেট হস্তক্ষেপ ও আইনানুগ কঠোর ব্যবস্থা গ্রহণ।</b>
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
    }\n\n"""

new_lines = lines[:start_idx] + [replacement_lines] + lines[end_idx:]
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Complaint modal successfully replaced!")

