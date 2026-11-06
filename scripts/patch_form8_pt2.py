import sys

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add signals in class
old_signals = "  readonly showQuickResultModal = signal(false);\n  readonly showAddOpponentModal = signal(false);"
new_signals = """  readonly showQuickResultModal = signal(false);
  readonly showAddOpponentModal = signal(false);
  readonly showForm8Modal = signal(false);
  readonly selectedCenterForForm8 = signal<CandidateCenterResultItem | null>(null);
  readonly form8Uploading = signal(false);
  readonly form8UploadData = signal<string>('');
  readonly form8FileName = signal<string>('');
  readonly form8PreviewUrl = signal<string>('');
  form8PresidingOfficer = '';
  form8Phone = '';
  form8CancelledVotes = 0;
  form8Note = '';
  form8Verified = true;
  readonly showWinnerCertificateModal = signal(false);"""

if old_signals in content:
    content = content.replace(old_signals, new_signals, 1)
    print("Signals added.")
else:
    print("Could not find old_signals")

# 2. Add methods in class before loadVoters
old_methods_anchor = "  // Voter Methods\n  loadVoters() {"
new_methods = """  // Form-8 Presiding Officer Methods
  openForm8Modal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8.set(center);
    this.form8UploadData.set('');
    this.form8FileName.set('');
    this.form8PreviewUrl.set(center.form8DocumentUrl || '');
    this.form8PresidingOfficer = center.presidingOfficerName || '';
    this.form8Phone = center.presidingOfficerPhone || '';
    this.form8CancelledVotes = center.cancelledVotes || 0;
    this.form8Note = center.verificationNote || '';
    this.form8Verified = true;
    this.showForm8Modal.set(true);
  }

  closeForm8Modal() {
    this.showForm8Modal.set(false);
    this.selectedCenterForForm8.set(null);
  }

  onForm8FileSelected(event: any) {
    const file = event.target?.files?.[0];
    if (!file) return;
    this.form8FileName.set(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      this.form8UploadData.set(result);
      this.form8PreviewUrl.set(result);
    };
    reader.readAsDataURL(file);
  }

  submitForm8() {
    const center = this.selectedCenterForForm8();
    if (!center) return;
    if (!this.form8UploadData() && !center.form8DocumentUrl) {
      alert('অনুগ্রহ করে প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ এর ছবি বা স্ক্যান কপি সিলেক্ট করুন।');
      return;
    }
    this.form8Uploading.set(true);
    const req: UploadAndVerifyForm8Request = {
      documentData: this.form8UploadData() || 'EXISTING',
      fileName: this.form8FileName() || 'form8_result_sheet.jpg',
      presidingOfficerName: this.form8PresidingOfficer,
      presidingOfficerPhone: this.form8Phone,
      cancelledVotes: Number(this.form8CancelledVotes) || 0,
      isVerified: this.form8Verified,
      verificationNote: this.form8Note
    };

    this.api.uploadForm8(this.electionId, center.electionCenterId, req).subscribe({
      next: () => {
        this.form8Uploading.set(false);
        this.closeForm8Modal();
        this.loadResultsSummary();
        alert('ফরম-৮ সফলভাবে আপলোড ও অফিসিয়াল ভেরিফিকেশন সম্পন্ন হয়েছে।');
      },
      error: err => {
        this.form8Uploading.set(false);
        const detail = err?.error?.message || err?.error?.error || err?.message || 'ফরম-৮ আপলোড করা সম্ভব হয়নি।';
        alert(`ত্রুটি: ${detail}`);
      }
    });
  }

  openWinnerCertificateModal() {
    this.showWinnerCertificateModal.set(true);
  }

  closeWinnerCertificateModal() {
    this.showWinnerCertificateModal.set(false);
  }

  printCertificate() {
    window.print();
  }

  // Voter Methods
  loadVoters() {"""

if old_methods_anchor in content:
    content = content.replace(old_methods_anchor, new_methods, 1)
    print("Methods added.")
else:
    print("Could not find old_methods_anchor")

# 3. Add Form-8 Modal and Winner Certificate Modal to template
old_modal_anchor = "    <!-- ===================================================================== -->\n    <!-- MODAL: ADD OPPONENT CANDIDATE -->"
new_modals = """    <!-- ===================================================================== -->
    <!-- MODAL: PRESIDING OFFICER FORM-8 UPLOAD & VERIFICATION -->
    <!-- ===================================================================== -->
    @if(showForm8Modal() && selectedCenterForForm8()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card form8-modal-card" style="width: min(840px, 95vw);">
          <div class="modal-header">
            <div>
              <span class="badge-eyebrow">নির্বাচন কমিশন ফরম-৮ (EC Form-8)</span>
              <h2>ভোটকেন্দ্রের ফলাফল শিট (ফরম-৮) আপলোড ও প্রত্যয়ন</h2>
              <p class="modal-subtitle">
                কেন্দ্র: <b>{{selectedCenterForForm8()!.centerName}} (কোড: {{selectedCenterForForm8()!.centerCode}})</b>
              </p>
            </div>
            <button class="close-btn" (click)="closeForm8Modal()">✕</button>
          </div>

          <form (ngSubmit)="submitForm8()">
            <div class="form8-content-grid">
              <!-- Left side: Upload & Preview -->
              <div class="form8-upload-panel">
                <label class="section-label">প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ শিটের ছবি/স্ক্যান *</label>
                <div class="file-dropzone" (click)="form8FileInput.click()">
                  @if(form8PreviewUrl()){
                    <div class="preview-container">
                      <img [src]="form8PreviewUrl()" alt="Form-8 Preview" class="form8-preview-img" />
                      <div class="change-overlay">
                        <span>🔄 নতুন ছবি নির্বাচন করুন</span>
                      </div>
                    </div>
                  } @else {
                    <div class="dropzone-placeholder">
                      <span class="drop-icon">📷</span>
                      <b>ফরম-৮ শিটের ছবি তুলুন বা আপলোড করুন</b>
                      <small>PNG, JPG বা PDF ফরম্যাট (সর্বোচ্চ ১০ মেগাবাইট)</small>
                    </div>
                  }
                </div>
                <input #form8FileInput type="file" accept="image/*,application/pdf" (change)="onForm8FileSelected($event)" style="display:none;" />

                @if(selectedCenterForForm8()!.form8DocumentUrl){
                  <div class="existing-doc-banner">
                    <span>✅ পূর্ববর্তী আপলোডকৃত অফিসিয়াল শিট সংরক্ষিত আছে</span>
                    <a [href]="selectedCenterForForm8()!.form8DocumentUrl" target="_blank" class="view-link">আসল ফাইল খুলুন ↗</a>
                  </div>
                }
              </div>

              <!-- Right side: Meta & Verification Details -->
              <div class="form8-meta-panel">
                <div class="form-field">
                  <label>প্রিজাইডিং অফিসারের নাম</label>
                  <input type="text" [(ngModel)]="form8PresidingOfficer" name="form8PresidingOfficer" placeholder="উদাঃ মোঃ রফিকুল ইসলাম" />
                </div>

                <div class="form-field">
                  <label>প্রিজাইডিং অফিসারের মোবাইল নম্বর</label>
                  <input type="tel" [(ngModel)]="form8Phone" name="form8Phone" placeholder="017XXXXXXXX" />
                </div>

                <div class="form-field">
                  <label>বাতিলকৃত ব্যালটের সংখ্যা (Cancelled/Invalid Votes)</label>
                  <input type="number" min="0" [(ngModel)]="form8CancelledVotes" name="form8CancelledVotes" placeholder="0" />
                </div>

                <div class="form-field">
                  <label>যাচাইকরণ নোট / সিলমোহরের বিবরণ</label>
                  <textarea rows="3" [(ngModel)]="form8Note" name="form8Note" placeholder="পোলিং এজেন্টের কপি ও প্রিজাইডিং অফিসারের স্বাক্ষরের সাথে শতভাগ মিলেছে..."></textarea>
                </div>

                <div class="verification-toggle-box">
                  <label class="checkbox-label">
                    <input type="checkbox" [(ngModel)]="form8Verified" name="form8Verified" />
                    <span><b>অফিসিয়াল যাচাই চূড়ান্ত (Mark as Verified)</b><br><small>ফলাফল শিটটি প্রিজাইডিং অফিসারের সিলযুক্ত মূল কপির সাথে যাচাইকৃত</small></span>
                  </label>
                </div>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn-cancel" (click)="closeForm8Modal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="form8Uploading() || (!form8UploadData() && !selectedCenterForForm8()!.form8DocumentUrl)">
                {{form8Uploading() ? 'আপলোড ও যাচাই হচ্ছে…' : '💾 ফরম-৮ সংরক্ষণ ও প্রত্যয়ন চূড়ান্ত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL: OFFICIAL WINNER CONSOLIDATION CERTIFICATE -->
    <!-- ===================================================================== -->
    @if(showWinnerCertificateModal()){
      <div class="modal-backdrop print-fullscreen">
        <div class="certificate-modal-wrapper">
          <div class="certificate-toolbar no-print">
            <div class="toolbar-left">
              <span class="cert-title">📋 ফরম-৮ ভিত্তিক ফলাফল সংহতকরণ বিবরণী ও বেসরকারি ফলাফল ঘোষণা প্রত্যয়নপত্র</span>
            </div>
            <div class="toolbar-actions">
              <button class="primary-button" (click)="printCertificate()">🖨️ প্রত্যয়নপত্র প্রিন্ট করুন</button>
              <button class="btn-cancel" (click)="closeWinnerCertificateModal()">✕ বন্ধ করুন</button>
            </div>
          </div>

          <div class="official-winner-cert-paper">
            <!-- EC Official Header -->
            <div class="cert-header">
              <div class="ec-emblem">⚖️</div>
              <h2>গণপ্রজাতন্ত্রী বাংলাদেশ নির্বাচন কমিশন</h2>
              <h3>উপজেলা / ইউনিয়ন পরিষদ সাধারণ নির্বাচন ২০২৬</h3>
              <p class="cert-election-title">
                নির্বাচনী এলাকা: <b>{{data()!.areaName}}</b> · আসন/ইউনিয়ন: <b>{{data()!.electionName}}</b>
              </p>
              <div class="cert-heading-divider">
                <span>বেসরকারি ফলাফল ঘোষণা ও সংহতকরণ প্রত্যয়নপত্র (CONSOLIDATION STATEMENT)</span>
              </div>
            </div>

            <!-- Certified Result Summary Card -->
            <div class="cert-summary-grid">
              <div class="cert-summary-box">
                <span class="box-label">সর্বমোট ভোটকেন্দ্র:</span>
                <b>{{resultsData()!.totalCenters}} টি</b>
              </div>
              <div class="cert-summary-box">
                <span class="box-label">ঘোষিত ফলাফল প্রাপ্ত কেন্দ্র:</span>
                <b>{{resultsData()!.countedCenters}} টি</b>
              </div>
              <div class="cert-summary-box highlight-box">
                <span class="box-label">বিজয়ী প্রার্থীর প্রাপ্ত ভোট:</span>
                <b>{{resultsData()!.candidateTotalVotes | number}} ভোট</b>
              </div>
              <div class="cert-summary-box">
                <span class="box-label">নিকটতম প্রতিদ্বন্দ্বীর ভোট:</span>
                <b>{{resultsData()!.runnerUpTotalVotes | number}} ভোট</b>
              </div>
              <div class="cert-summary-box victory-box">
                <span class="box-label">বিজয়ের মোট ব্যবধান (Lead Margin):</span>
                <b>+{{resultsData()!.leadMargin | number}} ভোট</b>
              </div>
            </div>

            <!-- Declaration Statement -->
            <div class="cert-declaration-block">
              <p>
                এতদ্বারা প্রত্যয়ন করা যাইতেছে যে, অদ্য অনুষ্ঠিত নির্বাচনে সংশ্লিষ্ট সকল ভোটকেন্দ্রের প্রিজাইডিং অফিসার কর্তৃক প্রস্তুতকৃত ও স্বাক্ষরিত ফরম-৮ (ফলাফল বিবরণী) সংহতকরণ শেষে প্রতিদ্বন্দ্বী প্রার্থী <b>{{resultsData()!.candidateName}}</b> (প্রতীক: <b>{{resultsData()!.candidateSymbolEmoji}} {{resultsData()!.candidateSymbol}}</b>) সর্বমোট <b>{{resultsData()!.candidateTotalVotes | number}}</b> ভোট পেয়ে বেসরকারিভাবে নির্বাচিত ঘোষিত হইলেন।
              </p>
            </div>

            <!-- Candidate Roster Breakdown -->
            <div class="cert-table-section">
              <h4>প্রতিদ্বন্দ্বী প্রার্থীদের সংহত ফলাফল বিবরণী (Summary of Results)</h4>
              <table class="cert-table">
                <thead>
                  <tr>
                    <th>ক্রমিক</th>
                    <th>প্রার্থীর নাম</th>
                    <th>রাজনৈতিক দল</th>
                    <th>প্রতীক</th>
                    <th style="text-align:right;">প্রাপ্ত মোট ভোট</th>
                    <th style="text-align:right;">ভোটের শতকরা হার</th>
                    <th style="text-align:center;">ফলাফল</th>
                  </tr>
                </thead>
                <tbody>
                  @for(t of resultsData()!.allCandidateTallies || []; track t.candidateId; let i = $index){
                    <tr [class.cert-winner-row]="t.isPrimary">
                      <td>{{i + 1}}</td>
                      <td><b>{{t.name}}</b></td>
                      <td>{{t.partyName}}</td>
                      <td>{{t.symbolEmoji}} {{t.symbolName}}</td>
                      <td style="text-align:right;"><b>{{t.totalVotes | number}}</b></td>
                      <td style="text-align:right;">{{t.votePercentage}}%</td>
                      <td style="text-align:center;">
                        @if(t.isPrimary && resultsData()!.isLeading){
                          <span class="cert-winner-stamp">★ বেসরকারি নির্বাচিত</span>
                        } @else {
                          <span>প্রতিদ্বন্দ্বী</span>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>

            <!-- Center by Center Certified Breakdown -->
            <div class="cert-table-section">
              <h4>কেন্দ্রভিত্তিক বিস্তারিত সংহত ফলাফল ছক (Center-by-Center Statement)</h4>
              <table class="cert-table cert-table-sm">
                <thead>
                  <tr>
                    <th>কোড</th>
                    <th>ভোটকেন্দ্রের নাম</th>
                    <th style="text-align:right;">আমাদের প্রার্থী</th>
                    <th style="text-align:right;">নিকটতম</th>
                    <th style="text-align:right;">ব্যবধান</th>
                    <th style="text-align:center;">ফরম-৮ প্রত্যয়ন স্ট্যাটাস</th>
                  </tr>
                </thead>
                <tbody>
                  @for(cr of resultsData()!.centerResults; track cr.electionCenterId){
                    <tr>
                      <td>{{cr.centerCode}}</td>
                      <td>{{cr.centerName}}</td>
                      <td style="text-align:right;"><b>{{cr.candidateVotes | number}}</b></td>
                      <td style="text-align:right;">{{cr.runnerUpVotes | number}}</td>
                      <td style="text-align:right;">
                        <span [class.green-text]="cr.margin > 0" [class.red-text]="cr.margin < 0">
                          {{cr.margin > 0 ? '+' : ''}}{{cr.margin | number}}
                        </span>
                      </td>
                      <td style="text-align:center;">
                        @if(cr.form8Verified){
                          <span class="cert-badge-check">✓ প্রিজাইডিং অফিসার ফরম-৮ যাচাইকৃত</span>
                        } @else if(cr.isCounted){
                          <span>দাখিলকৃত</span>
                        } @else {
                          <span>অপেক্ষমান</span>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>

            <!-- Signatures & Official Seals -->
            <div class="cert-sign-strip">
              <div class="sign-block">
                <div class="sign-line"></div>
                <p>প্রধান নির্বাচনী এজেন্ট</p>
                <small>{{data()!.candidate?.name}} সেল</small>
              </div>
              <div class="sign-block center-seal">
                <div class="seal-circle">
                  <span>নির্বাচন কমিশন<br>অফিসিয়াল সিল</span>
                </div>
                <small>তারিখ: {{data()!.electionDate | date:'dd/MM/yyyy'}}</small>
              </div>
              <div class="sign-block">
                <div class="sign-line"></div>
                <p>রিটার্নিং অফিসার / সহকারী রিটার্নিং অফিসার</p>
                <small>{{data()!.electionName}}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL: ADD OPPONENT CANDIDATE -->"""

if old_modal_anchor in content:
    content = content.replace(old_modal_anchor, new_modals, 1)
    print("Modals added.")
else:
    print("Could not find old_modal_anchor")

# 4. Add CSS styles
old_css_anchor = "    /* Official EC Form-20 Return Printable Stylesheet */"
new_css = """    /* Results Form-8 & Certificate UI */
    .results-top-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .print-cert-btn { background: #fff; border: 1.5px solid #2563eb; color: #1d4ed8; font-weight: 700; padding: 10px 18px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
    .print-cert-btn:hover { background: #eff6ff; }
    .row-actions-group { display: flex; gap: 6px; align-items: center; }
    .btn-form8 { background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; cursor: pointer; }
    .btn-form8:hover { background: #dbeafe; }
    .btn-form8.has-doc { background: #f0fdf4; border-color: #86efac; color: #15803d; }
    .form8-link { font-size: 0.75rem; color: #2563eb; text-decoration: underline; margin-left: 6px; font-weight: 700; }

    .form8-content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 16px 0; }
    .form8-upload-panel { display: flex; flex-direction: column; gap: 10px; }
    .file-dropzone { border: 2px dashed #93c5fd; border-radius: 12px; background: #f8fafc; min-height: 220px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; position: relative; }
    .file-dropzone:hover { border-color: #2563eb; background: #eff6ff; }
    .dropzone-placeholder { text-align: center; display: flex; flex-direction: column; gap: 6px; padding: 24px; color: #475569; }
    .drop-icon { font-size: 2.2rem; }
    .preview-container { width: 100%; height: 100%; position: relative; }
    .form8-preview-img { width: 100%; height: 260px; object-fit: contain; background: #000; border-radius: 10px; }
    .change-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.65); color: #fff; text-align: center; padding: 6px; font-size: 0.8rem; font-weight: 600; }
    .existing-doc-banner { display: flex; justify-content: space-between; align-items: center; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; color: #166534; }
    .existing-doc-banner .view-link { color: #15803d; font-weight: 700; text-decoration: underline; }
    .form8-meta-panel { display: flex; flex-direction: column; gap: 12px; }
    .verification-toggle-box { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 10px 14px; margin-top: 4px; }
    .verification-toggle-box .checkbox-label { display: flex; gap: 10px; align-items: flex-start; cursor: pointer; }

    /* Official Winner Certificate Styles */
    .certificate-modal-wrapper { width: min(880px, 98vw); max-height: 94vh; overflow-y: auto; background: #fff; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .certificate-toolbar { display: flex; justify-content: space-between; align-items: center; background: #0f172a; color: #fff; padding: 14px 24px; border-radius: 14px 14px 0 0; }
    .cert-title { font-size: 0.94rem; font-weight: 700; }
    .official-winner-cert-paper { padding: 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; color: #000; background: #fff; line-height: 1.6; }
    .cert-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }
    .ec-emblem { font-size: 2.2rem; margin-bottom: 4px; }
    .cert-header h2 { margin: 0 0 4px; font-size: 1.45rem; font-weight: 800; color: #000; }
    .cert-header h3 { margin: 0 0 6px; font-size: 1.15rem; font-weight: 700; color: #111; }
    .cert-election-title { margin: 4px 0 10px; font-size: 0.95rem; }
    .cert-heading-divider { background: #000; color: #fff; display: inline-block; padding: 4px 18px; border-radius: 4px; font-size: 0.88rem; font-weight: 700; letter-spacing: 0.04em; }

    .cert-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 18px 0; }
    .cert-summary-box { border: 1px solid #000; padding: 10px; text-align: center; background: #fafafa; border-radius: 4px; }
    .cert-summary-box .box-label { display: block; font-size: 0.76rem; color: #333; margin-bottom: 4px; }
    .cert-summary-box b { font-size: 1.15rem; font-weight: 800; }
    .cert-summary-box.highlight-box { background: #f0fdf4; border-color: #16a34a; }
    .cert-summary-box.highlight-box b { color: #15803d; }
    .cert-summary-box.victory-box { background: #eff6ff; border-color: #2563eb; }
    .cert-summary-box.victory-box b { color: #1d4ed8; }

    .cert-declaration-block { border: 1.5px solid #000; padding: 14px 18px; background: #fbfbfb; margin: 18px 0 24px; font-size: 0.96rem; text-align: justify; line-height: 1.7; border-left: 6px solid #000; }
    .cert-table-section { margin: 20px 0; }
    .cert-table-section h4 { margin: 0 0 8px; font-size: 0.96rem; font-weight: 700; border-bottom: 1px solid #000; padding-bottom: 4px; }
    .cert-table { width: 100%; border-collapse: collapse; font-size: 0.86rem; margin-bottom: 12px; }
    .cert-table th, .cert-table td { border: 1px solid #000; padding: 6px 10px; }
    .cert-table th { background: #f0f0f0; font-weight: 700; }
    .cert-table-sm { font-size: 0.82rem; }
    .cert-table-sm th, .cert-table-sm td { padding: 5px 8px; }
    .cert-winner-row { background: #f0fdf4; }
    .cert-winner-stamp { background: #15803d; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.74rem; font-weight: 700; }
    .cert-badge-check { color: #15803d; font-weight: 700; }
    .green-text { color: #15803d; font-weight: 700; }
    .red-text { color: #b91c1c; font-weight: 700; }

    .cert-sign-strip { display: grid; grid-template-columns: 1fr 140px 1fr; gap: 20px; align-items: flex-end; text-align: center; margin-top: 55px; }
    .center-seal { display: flex; flex-direction: column; align-items: center; gap: 6px; }
    .seal-circle { width: 90px; height: 90px; border: 2px dashed #000; border-radius: 50%; display: grid; place-items: center; font-size: 0.7rem; font-weight: 700; text-align: center; }

    /* Official EC Form-20 Return Printable Stylesheet */"""

if old_css_anchor in content:
    content = content.replace(old_css_anchor, new_css, 1)
    print("CSS added.")
else:
    print("Could not find old_css_anchor")

# 5. Update print styles
old_print = ".official-ec-return-paper, .official-ec-return-paper * {"
new_print = ".official-ec-return-paper, .official-ec-return-paper *,\n      .official-winner-cert-paper, .official-winner-cert-paper * {"
if old_print in content:
    content = content.replace(old_print, new_print, 1)

old_print_layout = ".official-form9-paper, .agent-badge-paper, .voter-slips-page, .official-complaint-paper, .official-ec-return-paper {"
new_print_layout = ".official-form9-paper, .agent-badge-paper, .voter-slips-page, .official-complaint-paper, .official-ec-return-paper, .official-winner-cert-paper {"
if old_print_layout in content:
    content = content.replace(old_print_layout, new_print_layout, 1)
    print("Print styles updated.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved part 2 successfully!")

