import os

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add QRCode import if not present
if 'import * as QRCode from \'qrcode\';' not in content:
    target = "import { forkJoin } from 'rxjs';"
    replacement = "import { forkJoin } from 'rxjs';\nimport * as QRCode from 'qrcode';"
    if target in content:
        content = content.replace(target, replacement, 1)
        print("QRCode import added.")
    else:
        print("ERROR: could not find target for QRCode import")

# 2. Add Toolbar button for Batch ID Cards in Agent Tab
target_toolbar = """                <button class="primary-button" (click)="openAddAgentModal()">
                  ➕ নতুন এজেন্ট নিয়োগ করুন
                </button>"""

batch_btn = """                <button class="outline-sm-btn" (click)="openBatchIdCardsModal()" style="font-weight: 700; border-color: #082136; color: #082136; background: #f0f7ff;">
                  🪪 ব্যাচ আইডি কার্ড প্রিন্ট
                </button>
                <button class="primary-button" (click)="openAddAgentModal()">
                  ➕ নতুন এজেন্ট নিয়োগ করুন
                </button>"""

if target_toolbar in content:
    content = content.replace(target_toolbar, batch_btn, 1)
    print("Batch ID Card toolbar button added.")
else:
    print("ERROR: could not find target_toolbar")

# 3. Add batchIdCards signals & state
target_signals = "  readonly selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);"
replacement_signals = """  readonly selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);
  readonly showBatchIdCardsModal = signal(false);
  readonly agentQrCodes = signal<Record<string, string>>({});
  batchIdCardCenterFilter = '';
  batchIdCardTypeFilter = '';

  readonly batchFilteredAgents = computed(() => {
    let list = this.boothAgents();
    const cFilter = this.batchIdCardCenterFilter;
    const tFilter = this.batchIdCardTypeFilter;
    if (cFilter) {
      list = list.filter(a => a.centerId === cFilter);
    }
    if (tFilter) {
      list = list.filter(a => a.agentType === tFilter);
    }
    return list;
  });"""

if target_signals in content:
    content = content.replace(target_signals, replacement_signals, 1)
    print("Signals and computed added.")
else:
    print("ERROR: could not find target_signals")

# 4. Add methods: generateAgentQr, ensureAgentQrs, openBatchIdCardsModal, closeBatchIdCardsModal, updated openAgentBadge
target_methods = """  openAgentBadge(ag: CandidateBoothAgentSummary) {
    this.selectedAgentForBadge.set(ag);
  }

  closeAgentBadge() {
    this.selectedAgentForBadge.set(null);
  }"""

replacement_methods = """  async generateAgentQr(ag: CandidateBoothAgentSummary): Promise<string> {
    const cand = this.data()?.candidate;
    const payload = `EEMS-POLLING-AGENT-ID\\nELECTION: ${this.data()?.areaName || 'নির্বাচনী আসন'}\\nCANDIDATE: ${cand?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}\\nSYMBOL: ${cand?.symbolEmoji || '⚖️'} ${cand?.symbolNameBn || 'দাঁড়িপাল্লা'}\\nPARTY: ${cand?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}\\nCENTER: ${ag.centerName} (${ag.centerCode})\\nBOOTH: ${ag.boothName}\\nAGENT: ${ag.fullName}\\nNID: ${ag.nidNumber}\\nPHONE: ${ag.phone}\\nTYPE: ${ag.agentType === 'PRIMARY' ? 'মূল এজেন্ট' : 'বিকল্প এজেন্ট'}\\nVERIFIED: বাংলাদেশ নির্বাচন কমিশন ২০২৬`;
    try {
      return await QRCode.toDataURL(payload, {
        width: 180,
        margin: 1,
        errorCorrectionLevel: 'M',
        color: { dark: '#082136', light: '#ffffff' }
      });
    } catch (err) {
      console.error('Error generating QR for agent', err);
      return '';
    }
  }

  async ensureAgentQrs(agents: CandidateBoothAgentSummary[]) {
    const current = { ...this.agentQrCodes() };
    let changed = false;
    for (const ag of agents) {
      if (!current[ag.boothAgentId]) {
        current[ag.boothAgentId] = await this.generateAgentQr(ag);
        changed = true;
      }
    }
    if (changed) {
      this.agentQrCodes.set(current);
    }
  }

  async openBatchIdCardsModal() {
    this.showBatchIdCardsModal.set(true);
    await this.ensureAgentQrs(this.boothAgents());
  }

  closeBatchIdCardsModal() {
    this.showBatchIdCardsModal.set(false);
  }

  async openAgentBadge(ag: CandidateBoothAgentSummary) {
    this.selectedAgentForBadge.set(ag);
    if (!this.agentQrCodes()[ag.boothAgentId]) {
      const qr = await this.generateAgentQr(ag);
      this.agentQrCodes.update(curr => ({ ...curr, [ag.boothAgentId]: qr }));
    }
  }

  closeAgentBadge() {
    this.selectedAgentForBadge.set(null);
  }"""

if target_methods in content:
    content = content.replace(target_methods, replacement_methods, 1)
    print("Methods added successfully.")
else:
    print("ERROR: could not find target_methods")

# 5. Replace single badge modal with modern ID Card layout + Add Batch ID Cards Modal
target_badge_modal = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: AGENT ID BADGE -->
    <!-- ===================================================================== -->
    @if(selectedAgentForBadge()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>পোলিং এজেন্ট পরিচয়পত্র (Badge Preview)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeAgentBadge()">✕</button>
            </div>
          </div>

          <div class="agent-badge-paper">
            <div class="badge-head">
              <span class="badge-org">জাতীয় নির্বাচন কমান্ড সেন্টার</span>
              <h3 class="badge-title">পোলিং এজেন্ট পরিচয়পত্র</h3>
              <span class="badge-seat">{{data()?.areaName}}</span>
            </div>

            <div class="badge-symbol-circle">
              <span class="badge-sym-icon">{{data()?.candidate?.symbolEmoji}}</span>
              <span class="badge-sym-name">{{data()?.candidate?.symbolNameBn}}</span>
            </div>

            <div class="badge-candidate-tag">
              প্রার্থী: <b>{{data()?.candidate?.name}}</b>
            </div>

            <div class="badge-info-list">
              <div class="b-row">
                <span>নাম:</span>
                <b>{{selectedAgentForBadge()!.fullName}}</b>
              </div>
              <div class="b-row">
                <span>কেন্দ্র:</span>
                <b>{{selectedAgentForBadge()!.centerName}}</b>
              </div>
              <div class="b-row">
                <span>বুথ নং:</span>
                <b>{{selectedAgentForBadge()!.boothName}}</b>
              </div>
              <div class="b-row">
                <span>মোবাইল:</span>
                <b>{{selectedAgentForBadge()!.phone}}</b>
              </div>
              <div class="b-row">
                <span>ধরন:</span>
                <b>{{selectedAgentForBadge()!.agentType === 'PRIMARY' ? 'মূল এজেন্ট' : 'বিকল্প এজেন্ট'}}</b>
              </div>
            </div>

            <div class="badge-footer">
              <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
            </div>
          </div>
        </div>
      </div>
    }"""

replacement_badge_and_batch = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: SINGLE AGENT ID CARD -->
    <!-- ===================================================================== -->
    @if(selectedAgentForBadge()){
      <div class="modal-backdrop batch-cards-backdrop">
        <div class="card modal-card print-preview-card single-badge-modal-card">
          <div class="modal-header no-print">
            <div>
              <h2>পোলিং এজেন্ট অফিশিয়াল ফটো আইডি কার্ড</h2>
              <p class="subtitle">নির্বাচন কমিশন ও প্রার্থীর প্রতীকযুক্ত ভেরিফায়েড পরিচয়পত্র</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeAgentBadge()">✕</button>
            </div>
          </div>

          <div class="single-id-card-wrap">
            <div class="official-agent-id-card printable-card-target">
              <div class="cut-corner top-left">✂️</div>
              <div class="cut-corner top-right">✂️</div>

              <!-- Top Ribbon -->
              <div class="card-ribbon-head">
                <div class="ribbon-gov">গণপ্রজাতন্ত্রী বাংলাদেশ · নির্বাচন ২০২৬</div>
                <div class="ribbon-title">পোলিং এজেন্ট পরিচয়পত্র (POLLING AGENT ID)</div>
                <div class="ribbon-seat">{{data()?.areaName || '৫ নং ইয়াকুবপুর ইউনিয়ন · দাগনভূঞা'}}</div>
              </div>

              <!-- Candidate Identity Strip -->
              <div class="card-cand-strip">
                <div class="cand-sym-box">
                  <span class="cand-sym-icon">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                  <span class="cand-sym-name">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</span>
                </div>
                <div class="cand-info-box">
                  <div class="cand-meta">মনোনীত প্রার্থী: <b class="cand-name-txt">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b></div>
                  <div class="cand-party-txt">{{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</div>
                </div>
              </div>

              <!-- Agent Details & QR Section -->
              <div class="card-agent-body">
                <!-- Agent Photo -->
                <div class="agent-photo-col">
                  <div class="agent-photo-frame">
                    @if(selectedAgentForBadge()!.photoUrl){
                      <img [src]="selectedAgentForBadge()!.photoUrl" alt="{{selectedAgentForBadge()!.fullName}}" class="agent-img" />
                    } @else {
                      <div class="agent-avatar-placeholder">
                        <span>👤</span>
                      </div>
                    }
                  </div>
                  <span class="agent-type-tag" [class.reserve]="selectedAgentForBadge()!.agentType === 'RESERVE'">
                    {{selectedAgentForBadge()!.agentType === 'PRIMARY' ? 'মূল এজেন্ট' : 'বিকল্প এজেন্ট'}}
                  </span>
                </div>

                <!-- Agent Info -->
                <div class="agent-data-col">
                  <div class="card-field-row name-row">
                    <span class="f-lbl">নাম:</span>
                    <b class="f-val-name">{{selectedAgentForBadge()!.fullName}}</b>
                  </div>
                  <div class="card-field-row">
                    <span class="f-lbl">NID:</span>
                    <span class="f-val">{{selectedAgentForBadge()!.nidNumber}}</span>
                  </div>
                  <div class="card-field-row">
                    <span class="f-lbl">ভোটার নং:</span>
                    <span class="f-val">{{selectedAgentForBadge()!.voterNumber || '—'}}</span>
                  </div>
                  <div class="card-field-row">
                    <span class="f-lbl">মোবাইল:</span>
                    <span class="f-val">📞 {{selectedAgentForBadge()!.phone}}</span>
                  </div>
                  <div class="card-field-row center-row">
                    <span class="f-lbl">ভোটকেন্দ্র:</span>
                    <span class="f-val-center">{{selectedAgentForBadge()!.centerName}} ({{selectedAgentForBadge()!.centerCode}})</span>
                  </div>
                  <div class="card-field-row booth-row">
                    <span class="f-lbl">ভোটকক্ষ:</span>
                    <b class="f-val-booth">{{selectedAgentForBadge()!.boothName}}</b>
                  </div>
                </div>

                <!-- QR Verification -->
                <div class="agent-qr-col">
                  <div class="qr-box">
                    @if(agentQrCodes()[selectedAgentForBadge()!.boothAgentId]){
                      <img [src]="agentQrCodes()[selectedAgentForBadge()!.boothAgentId]" alt="QR Verification" class="qr-code-img" />
                    } @else {
                      <div class="qr-loading">QR...</div>
                    }
                    <span class="qr-caption">স্মার্ট ভেরিফিকেশন</span>
                  </div>
                </div>
              </div>

              <!-- Card Footer & Official Signatures -->
              <div class="card-foot-strip">
                <div class="validity-txt">
                  <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
                </div>
                <div class="seal-sign-box">
                  <div class="sign-holder">
                    <div class="sign-line-bar"></div>
                    <span class="sign-label">প্রার্থী / প্রধান এজেন্টের স্বাক্ষর ও সিল</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: BATCH AGENT ID CARDS (A4 MULTI-CARD SHEET) -->
    <!-- ===================================================================== -->
    @if(showBatchIdCardsModal()){
      <div class="modal-backdrop batch-cards-backdrop">
        <div class="card modal-card batch-cards-modal-card">
          <!-- Top Control Header (Hidden in Print) -->
          <div class="modal-header batch-modal-header no-print">
            <div class="header-titles">
              <h2>🪪 পোলিং এজেন্টদের অফিশিয়াল ফটো আইডি কার্ড ব্যাচ প্রিন্ট</h2>
              <p class="subtitle">প্রার্থীর নির্বাচনী প্রতীক, নাম, কিউআর কোড এবং বুথ নম্বরসহ এক ক্লিকে সকল পোলিং এজেন্টের আইডি কার্ড প্রিন্ট করুন।</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button print-action-btn" (click)="triggerBrowserPrint()">
                🖨️ ব্যাচ প্রিন্ট করুন (A4 পেপার)
              </button>
              <button class="close-btn" (click)="closeBatchIdCardsModal()">✕</button>
            </div>
          </div>

          <!-- Batch Filter Strip (Hidden in Print) -->
          <div class="batch-filter-strip no-print">
            <div class="filter-item">
              <label>ভোটকেন্দ্র ফিল্টার:</label>
              <select [(ngModel)]="batchIdCardCenterFilter">
                <option value="">সকল ভোটকেন্দ্র ({{boothAgents().length}})</option>
                @for(c of centersList(); track c.centerId){
                  <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                }
              </select>
            </div>
            <div class="filter-item">
              <label>এজেন্টের ধরন:</label>
              <select [(ngModel)]="batchIdCardTypeFilter">
                <option value="">সকল ধরন</option>
                <option value="PRIMARY">মূল এজেন্ট (Primary)</option>
                <option value="RESERVE">বিকল্প এজেন্ট (Reserve)</option>
              </select>
            </div>
            <div class="filter-item card-counter-pill">
              <span>প্রিন্টের জন্য প্রস্তুত: <b>{{batchFilteredAgents().length}}</b> টি আইডি কার্ড</span>
            </div>
          </div>

          <!-- Batch ID Cards Printable Sheet (A4 Multi-Card Layout) -->
          <div class="batch-id-cards-sheet">
            @if(batchFilteredAgents().length === 0){
              <div class="empty no-print">কোনো পোলিং এজেন্ট পাওয়া যায়নি। ফিল্টার পরিবর্তন করুন অথবা নতুন এজেন্ট নিয়োগ করুন।</div>
            } @else {
              <div class="cards-grid-layout printable-card-target">
                @for(ag of batchFilteredAgents(); track ag.boothAgentId){
                  <div class="official-agent-id-card">
                    <!-- Cut Line Border Markers -->
                    <div class="cut-corner top-left">✂️</div>
                    <div class="cut-corner top-right">✂️</div>

                    <!-- Top Ribbon -->
                    <div class="card-ribbon-head">
                      <div class="ribbon-gov">গণপ্রজাতন্ত্রী বাংলাদেশ · নির্বাচন ২০২৬</div>
                      <div class="ribbon-title">পোলিং এজেন্ট পরিচয়পত্র (POLLING AGENT ID)</div>
                      <div class="ribbon-seat">{{data()?.areaName || '৫ নং ইয়াকুবপুর ইউনিয়ন · দাগনভূঞা'}}</div>
                    </div>

                    <!-- Candidate Identity Strip -->
                    <div class="card-cand-strip">
                      <div class="cand-sym-box">
                        <span class="cand-sym-icon">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                        <span class="cand-sym-name">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</span>
                      </div>
                      <div class="cand-info-box">
                        <div class="cand-meta">মনোনীত প্রার্থী: <b class="cand-name-txt">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b></div>
                        <div class="cand-party-txt">{{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</div>
                      </div>
                    </div>

                    <!-- Agent Details & QR Section -->
                    <div class="card-agent-body">
                      <!-- Agent Photo & Badge Type -->
                      <div class="agent-photo-col">
                        <div class="agent-photo-frame">
                          @if(ag.photoUrl){
                            <img [src]="ag.photoUrl" alt="{{ag.fullName}}" class="agent-img" />
                          } @else {
                            <div class="agent-avatar-placeholder">
                              <span>👤</span>
                            </div>
                          }
                        </div>
                        <span class="agent-type-tag" [class.reserve]="ag.agentType === 'RESERVE'">
                          {{ag.agentType === 'PRIMARY' ? 'মূল এজেন্ট' : 'বিকল্প এজেন্ট'}}
                        </span>
                      </div>

                      <!-- Agent Core Data -->
                      <div class="agent-data-col">
                        <div class="card-field-row name-row">
                          <span class="f-lbl">নাম:</span>
                          <b class="f-val-name">{{ag.fullName}}</b>
                        </div>
                        <div class="card-field-row">
                          <span class="f-lbl">NID:</span>
                          <span class="f-val">{{ag.nidNumber}}</span>
                        </div>
                        <div class="card-field-row">
                          <span class="f-lbl">ভোটার নং:</span>
                          <span class="f-val">{{ag.voterNumber || '—'}}</span>
                        </div>
                        <div class="card-field-row">
                          <span class="f-lbl">মোবাইল:</span>
                          <span class="f-val">📞 {{ag.phone}}</span>
                        </div>
                        <div class="card-field-row center-row">
                          <span class="f-lbl">ভোটকেন্দ্র:</span>
                          <span class="f-val-center">{{ag.centerName}} ({{ag.centerCode}})</span>
                        </div>
                        <div class="card-field-row booth-row">
                          <span class="f-lbl">ভোটকক্ষ:</span>
                          <b class="f-val-booth">{{ag.boothName}}</b>
                        </div>
                      </div>

                      <!-- QR Code Verification -->
                      <div class="agent-qr-col">
                        <div class="qr-box">
                          @if(agentQrCodes()[ag.boothAgentId]){
                            <img [src]="agentQrCodes()[ag.boothAgentId]" alt="QR Verification" class="qr-code-img" />
                          } @else {
                            <div class="qr-loading">QR...</div>
                          }
                          <span class="qr-caption">স্মার্ট ভেরিফিকেশন</span>
                        </div>
                      </div>
                    </div>

                    <!-- Card Footer & Official Signatures -->
                    <div class="card-foot-strip">
                      <div class="validity-txt">
                        <span>কার্যকারিতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
                      </div>
                      <div class="seal-sign-box">
                        <div class="sign-holder">
                          <div class="sign-line-bar"></div>
                          <span class="sign-label">প্রার্থী / প্রধান এজেন্টের স্বাক্ষর ও সিল</span>
                        </div>
                      </div>
                    </div>
                  </div>
                }
              </div>
            }
          </div>
        </div>
      </div>
    }"""

if target_badge_modal in content:
    content = content.replace(target_badge_modal, replacement_badge_and_batch, 1)
    print("Modals replaced successfully.")
else:
    print("ERROR: could not find target_badge_modal")

# 6. Add CSS Styles
old_css_anchor = "    /* Agent Badge */"
new_css = """    /* Official Polling Agent ID Card & Batch Printing Styles */
    .batch-cards-backdrop { position: fixed; inset: 0; background: rgba(8, 33, 54, 0.75); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: flex-start; z-index: 1000; overflow-y: auto; padding: 24px 16px; }
    .batch-cards-modal-card { width: min(1080px, 98vw); background: #f8fafc; border-radius: 14px; box-shadow: 0 12px 32px rgba(0,0,0,0.25); border: 1px solid #cbd5e1; padding: 24px; margin-bottom: 40px; }
    .single-badge-modal-card { width: min(540px, 96vw); }
    .batch-modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 14px; }
    .header-titles h2 { margin: 0 0 4px 0; color: #082136; font-size: 1.3rem; font-weight: 800; }
    .header-titles .subtitle { margin: 0; font-size: 0.8rem; color: #64748b; }
    .modal-header-actions { display: flex; align-items: center; gap: 12px; }
    .print-action-btn { background: #082136; color: #fff; font-weight: 700; border: none; padding: 9px 18px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 0.88rem; box-shadow: 0 2px 6px rgba(8,33,54,0.3); }
    .print-action-btn:hover { background: #13395c; }
    
    .batch-filter-strip { display: flex; align-items: center; gap: 16px; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 16px; margin-bottom: 20px; flex-wrap: wrap; }
    .filter-item { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; }
    .filter-item label { font-weight: 700; color: #334155; }
    .filter-item select { border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; font-size: 0.82rem; background: #f8fafc; color: #0f172a; outline: none; }
    .card-counter-pill { margin-left: auto; background: #e0f2fe; color: #0369a1; padding: 6px 14px; border-radius: 20px; font-weight: 600; border: 1px solid #bae6fd; }

    /* Single ID Card Wrap */
    .single-id-card-wrap { display: flex; justify-content: center; padding: 16px 0; }

    /* Cards Grid Layout (2 Columns for A4 print) */
    .cards-grid-layout { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }

    /* Official Agent ID Card Component */
    .official-agent-id-card {
      position: relative;
      background: #ffffff;
      border: 2px solid #082136;
      border-radius: 10px;
      padding: 0;
      box-shadow: 0 4px 12px rgba(8, 33, 54, 0.08);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Hind Siliguri", sans-serif;
      box-sizing: border-box;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      page-break-inside: avoid;
      break-inside: avoid;
    }
    
    /* Cut Marks */
    .cut-corner { position: absolute; font-size: 10px; color: #94a3b8; pointer-events: none; z-index: 5; }
    .cut-corner.top-left { top: 2px; left: 4px; }
    .cut-corner.top-right { top: 2px; right: 4px; }

    /* Ribbon Header */
    .card-ribbon-head {
      background: #082136;
      color: #ffffff;
      padding: 8px 12px;
      text-align: center;
      border-bottom: 2px solid #d97706;
    }
    .ribbon-gov { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.05em; color: #cbd5e1; }
    .ribbon-title { font-size: 0.95rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.02em; margin: 1px 0; }
    .ribbon-seat { font-size: 0.72rem; color: #fde68a; font-weight: 700; }

    /* Candidate Identity Strip */
    .card-cand-strip {
      background: #f0fdf4;
      border-bottom: 1.5px solid #bbf7d0;
      display: flex;
      align-items: center;
      padding: 6px 12px;
      gap: 12px;
    }
    .cand-sym-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      background: #ffffff;
      border: 1.5px solid #16a34a;
      border-radius: 8px;
      padding: 3px 8px;
      min-width: 52px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .cand-sym-icon { font-size: 1.5rem; line-height: 1.1; }
    .cand-sym-name { font-size: 0.65rem; font-weight: 800; color: #166534; }
    .cand-info-box { display: flex; flex-direction: column; gap: 1px; font-size: 0.76rem; }
    .cand-meta { color: #1e293b; }
    .cand-name-txt { color: #082136; font-size: 0.88rem; font-weight: 800; }
    .cand-party-txt { font-size: 0.7rem; color: #166534; font-weight: 700; }

    /* Agent Details Body (Photo + Info + QR) */
    .card-agent-body {
      display: flex;
      padding: 10px 12px;
      gap: 12px;
      align-items: center;
      background: #ffffff;
      flex: 1;
    }

    /* Photo Column */
    .agent-photo-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      width: 76px;
      flex-shrink: 0;
    }
    .agent-photo-frame {
      width: 70px;
      height: 82px;
      border: 1.5px solid #082136;
      border-radius: 6px;
      overflow: hidden;
      background: #f1f5f9;
      display: grid;
      place-items: center;
    }
    .agent-img { width: 100%; height: 100%; object-fit: cover; }
    .agent-avatar-placeholder { font-size: 2.2rem; color: #94a3b8; }
    .agent-type-tag {
      font-size: 0.62rem;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      background: #166534;
      color: #ffffff;
      text-align: center;
      white-space: nowrap;
    }
    .agent-type-tag.reserve { background: #d97706; }

    /* Core Info Column */
    .agent-data-col {
      display: flex;
      flex-direction: column;
      gap: 3px;
      flex: 1;
      font-size: 0.76rem;
      min-width: 0;
    }
    .card-field-row { display: flex; gap: 4px; align-items: baseline; }
    .f-lbl { color: #64748b; font-weight: 700; width: 56px; flex-shrink: 0; font-size: 0.7rem; }
    .f-val { color: #0f172a; font-weight: 600; word-break: break-all; }
    .f-val-name { color: #082136; font-size: 0.84rem; font-weight: 800; }
    .f-val-center { color: #1e293b; font-weight: 700; font-size: 0.75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px; }
    .booth-row { margin-top: 2px; }
    .f-val-booth {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      color: #92400e;
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 800;
      font-size: 0.78rem;
    }

    /* QR Code Column */
    .agent-qr-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 78px;
      flex-shrink: 0;
    }
    .qr-box {
      border: 1px solid #cbd5e1;
      background: #f8fafc;
      padding: 3px;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
    .qr-code-img { width: 68px; height: 68px; display: block; }
    .qr-loading { width: 68px; height: 68px; display: grid; place-items: center; font-size: 0.65rem; color: #94a3b8; }
    .qr-caption { font-size: 0.55rem; color: #64748b; font-weight: 700; margin-top: 2px; }

    /* Card Footer Strip */
    .card-foot-strip {
      border-top: 1px solid #e2e8f0;
      background: #f8fafc;
      padding: 4px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .validity-txt { font-size: 0.6rem; color: #64748b; font-weight: 600; flex: 1; }
    .seal-sign-box { text-align: right; flex-shrink: 0; }
    .sign-holder { display: flex; flex-direction: column; align-items: flex-end; }
    .sign-line-bar { width: 130px; border-bottom: 1px dashed #64748b; margin-bottom: 2px; }
    .sign-label { font-size: 0.58rem; color: #475569; font-weight: 700; }

    /* Agent Badge legacy */"""

if old_css_anchor in content:
    content = content.replace(old_css_anchor, new_css, 1)
    print("CSS rules added.")
else:
    print("ERROR: could not find old_css_anchor")

# 7. Update @media print
old_print_anchor = "      .official-form9-paper, .agent-badge-paper, .voter-slips-page, .official-complaint-paper, .official-ec-return-paper, .official-winner-cert-paper {"
new_print = """      .official-form9-paper, .official-form9-paper *,
      .batch-id-cards-sheet, .batch-id-cards-sheet *,
      .official-agent-id-card, .official-agent-id-card *,
      .single-id-card-wrap, .single-id-card-wrap *,"""

if old_print_anchor in content:
    content = content.replace(
        ".official-form9-paper, .official-form9-paper *,",
        new_print,
        1
    )
    # also add print specific layout for batch-id-cards
    print_override = """      .batch-cards-backdrop { position: static !important; background: transparent !important; padding: 0 !important; display: block !important; }
      .batch-cards-modal-card { width: 100% !important; max-width: 100% !important; box-shadow: none !important; border: none !important; padding: 0 !important; background: transparent !important; }
      .cards-grid-layout { display: grid !important; grid-template-columns: repeat(2, 1fr) !important; gap: 12px !important; page-break-inside: auto !important; }
      .official-agent-id-card { page-break-inside: avoid !important; break-inside: avoid !important; border: 1.5px solid #082136 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-shadow: none !important; }
"""
    content = content.replace("      .no-print { display: none !important; }", print_override + "      .no-print { display: none !important; }", 1)
    print("@media print updated.")
else:
    print("ERROR: could not find old_print_anchor")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching completed successfully!")

