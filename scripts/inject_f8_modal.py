file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "    <!-- ===================================================================== -->\n    <!-- MODAL: OFFICIAL WINNER CONSOLIDATION CERTIFICATE -->"

form8_modal = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: ELECTION COMMISSION FORM-8 STATEMENT SHEET -->
    <!-- ===================================================================== -->
    @if(selectedCenterForForm8Statement()){
      <div class="modal-backdrop print-modal-backdrop">
        <div class="card modal-card print-preview-card form8-modal-card">
          <div class="modal-header no-print">
            <div>
              <h2>বাংলাদেশ নির্বাচন কমিশন: ফরম - ৮</h2>
              <p class="subtitle">[বিধি ৩৬(১) দ্রষ্টব্য] — ভোট গণনার বিবরণী (Statement of the Count)</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ফরম-৮ প্রিন্ট করুন (A4)</button>
              <button class="close-btn" (click)="closeForm8StatementModal()">✕</button>
            </div>
          </div>

          <!-- Official Form-8 Government Statement Paper -->
          <div class="official-form8-sheet">
            <!-- Government Form Header -->
            <div class="f8-gov-head">
              <div class="f8-ec-title">বাংলাদেশ নির্বাচন কমিশন</div>
              <h2 class="f8-form-num">ফরম - ৮</h2>
              <div class="f8-rule-ref">[বিধি ৩৬(১) দ্রষ্টব্য]</div>
              <h3 class="f8-form-name">ভোট গণনার বিবরণী</h3>
            </div>

            <!-- Election & Center Metadata Grid -->
            <div class="f8-meta-table">
              <div class="f8-meta-row">
                <span class="f8-m-lbl">১. নির্বাচনী এলাকার নম্বর ও নাম:</span>
                <b class="f8-m-val">{{data()?.areaName || '৫ নং ইয়াকুবপুর ইউনিয়ন · দাগনভূঞা'}}</b>
              </div>
              <div class="f8-meta-row">
                <span class="f8-m-lbl">২. ভোটকেন্দ্রের ক্রমিক নম্বর ও নাম:</span>
                <b class="f8-m-val">{{selectedCenterForForm8Statement()!.centerCode}} — {{selectedCenterForForm8Statement()!.centerName}}</b>
              </div>
              <div class="f8-meta-row">
                <span class="f8-m-lbl">৩. গণনা সমাপ্তির তারিখ ও সময়:</span>
                <b class="f8-m-val">{{selectedCenterForForm8Statement()!.reportedAtUtc ? (selectedCenterForForm8Statement()!.reportedAtUtc | date:'dd/MM/yyyy, hh:mm a') : 'ভোটগ্রহণের দিন বিকেল ৫:০০'}}</b>
              </div>
            </div>

            <!-- Ballot Accounting Section -->
            <div class="f8-ballot-accounting">
              <div class="f8-sec-title">ব্যালট পেপারের সংবিধিবদ্ধ হিসাব:</div>
              <table class="f8-sub-table">
                <tbody>
                  <tr>
                    <td class="f8-item-lbl">(ক) ব্যালট বাক্সে প্রাপ্ত মোট ব্যালট পেপারের সংখ্যা:</td>
                    <td class="f8-item-val"><b>{{calcTotalCastVotes(selectedCenterForForm8Statement()) | number}}</b> টি</td>
                  </tr>
                  <tr>
                    <td class="f8-item-lbl">(খ) বাতিল বলিয়া গণ্য ব্যালট পেপারের সংখ্যা:</td>
                    <td class="f8-item-val"><b>{{selectedCenterForForm8Statement()!.cancelledVotes || 0 | number}}</b> টি</td>
                  </tr>
                  <tr>
                    <td class="f8-item-lbl">(গ) মোট প্রদত্ত বৈধ ব্যালট পেপারের সংখ্যা [ (ক) - (খ) ]:</td>
                    <td class="f8-item-val highlight-valid"><b>{{calcTotalValidVotes(selectedCenterForForm8Statement()) | number}}</b> টি</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Candidate Votes Table -->
            <div class="f8-candidates-section">
              <div class="f8-sec-title">প্রতিদ্বন্দ্বী প্রার্থীদের প্রাপ্ত বৈধ ভোটের সংখ্যা:</div>
              <table class="f8-votes-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">ক্রমিক</th>
                    <th>প্রতিদ্বন্দ্বী প্রার্থীর নাম</th>
                    <th style="width: 130px;">বরাদ্দকৃত প্রতীক</th>
                    <th>দলীয় পরিচয়</th>
                    <th style="width: 140px;">প্রাপ্ত বৈধ ভোট (অংকে)</th>
                    <th>প্রাপ্ত বৈধ ভোট (কথায়)</th>
                  </tr>
                </thead>
                <tbody>
                  @if(selectedCenterForForm8Statement()!.candidateVotesList && selectedCenterForForm8Statement()!.candidateVotesList!.length > 0){
                    @for(cv of selectedCenterForForm8Statement()!.candidateVotesList; track cv.candidateId; let i = $index){
                      <tr [class.highlight-our-row]="cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId())">
                        <td class="text-center">{{i + 1}}</td>
                        <td>
                          <b>{{cv.candidateName}}</b>
                          @if(cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId())){
                            <span class="f8-our-tag">★ বিজয়ী</span>
                          }
                        </td>
                        <td>
                          <span class="f8-sym-icon">{{cv.symbolEmoji}}</span> {{cv.symbolName || ''}}
                        </td>
                        <td>{{cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId()) ? (data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী') : 'প্রতিদ্বন্দ্বী দল / স্বতন্ত্র'}}</td>
                        <td class="text-right"><b>{{cv.votes | number}}</b></td>
                        <td class="text-left font-bangla">{{numberToBanglaWords(cv.votes)}}</td>
                      </tr>
                    }
                  } @else {
                    <tr class="highlight-our-row">
                      <td class="text-center">১</td>
                      <td><b>{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b></td>
                      <td>{{data()?.candidate?.symbolEmoji || '⚖️'}} {{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</td>
                      <td>{{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</td>
                      <td class="text-right"><b>{{selectedCenterForForm8Statement()!.candidateVotes | number}}</b></td>
                      <td class="text-left font-bangla">{{numberToBanglaWords(selectedCenterForForm8Statement()!.candidateVotes)}}</td>
                    </tr>
                    <tr>
                      <td class="text-center">২</td>
                      <td><b>শীর্ষ প্রতিদ্বন্দ্বী প্রার্থী</b></td>
                      <td>প্রতিদ্বন্দ্বী প্রতীক</td>
                      <td>অন্যান্য দল / স্বতন্ত্র</td>
                      <td class="text-right"><b>{{selectedCenterForForm8Statement()!.runnerUpVotes | number}}</b></td>
                      <td class="text-left font-bangla">{{numberToBanglaWords(selectedCenterForForm8Statement()!.runnerUpVotes)}}</td>
                    </tr>
                  }
                </tbody>
                <tfoot>
                  <tr>
                    <th colspan="4" class="text-right">মোট বৈধ ভোটের সংখ্যা:</th>
                    <th class="text-right"><b>{{calcTotalValidVotes(selectedCenterForForm8Statement()) | number}}</b></th>
                    <th class="text-left font-bangla"><b>{{numberToBanglaWords(calcTotalValidVotes(selectedCenterForForm8Statement()))}}</b></th>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Presiding Officer Certification & Signatures -->
            <div class="f8-cert-box">
              <p class="f8-cert-declaration">
                "আমি এই মর্মে প্রত্যয়ন করিতেছি যে, উপরোক্ত বিবরণী আমার উপস্থিতিতে ও তত্ত্বাবধানে সতর্কতার সহিত ভোট গণনা করিয়া সঠিকভাবে প্রস্তুত করা হইল এবং উপস্থিত প্রতিদ্বন্দ্বী প্রার্থী বা তাহাদের নির্বাচনী এজেন্ট / পোলিং এজেন্টদের উপস্থিতিতে ফলাফল ঘোষণা পূর্বক তাহাদের স্বাক্ষরিত অনুলিপি প্রদান করা হইল।"
              </p>
            </div>

            <!-- Signatures Section -->
            <div class="f8-signatures-grid">
              <div class="f8-po-sign-box">
                <div class="f8-sign-line"></div>
                <b>প্রিজাইডিং অফিসারের স্বাক্ষর ও সিলমোহর</b>
                <span class="f8-po-meta">নাম: {{selectedCenterForForm8Statement()!.presidingOfficerName || 'মোঃ শফিকুল ইসলাম'}}</span>
                <span class="f8-po-meta">মোবাইল: {{selectedCenterForForm8Statement()!.presidingOfficerPhone || '01819234567'}}</span>
                <span class="f8-po-meta">কেন্দ্র: {{selectedCenterForForm8Statement()!.centerName}} ({{selectedCenterForForm8Statement()!.centerCode}})</span>
              </div>

              <div class="f8-agents-signs-box">
                <div class="f8-agents-title">উপস্থিত পোলিং এজেন্টদের স্বাক্ষর:</div>
                <div class="f8-agent-slots">
                  <div class="f8-agent-slot">১. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">২. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">৩. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">৪. স্বাক্ষর: ................................... প্রতীক: .............</div>
                </div>
              </div>
            </div>

            <!-- Statutory Footer Note -->
            <div class="f8-statutory-footer">
              <span>* নির্বাচন পরিচালনা বিধিমালা অনুযায়ী এই বিবরণীর অনুলিপি সহকারী রিটার্নিং অফিসারের কার্যালয়ে তাৎক্ষণিক প্রেরণ করিতে হইবে।</span>
            </div>
          </div>
        </div>
      </div>
    }\n\n""" + target

if target in content:
    content = content.replace(target, form8_modal, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Form-8 Statement Modal injected successfully!")
else:
    print("Could not find target in content")

