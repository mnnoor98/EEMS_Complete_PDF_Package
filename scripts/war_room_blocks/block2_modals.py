# -*- coding: utf-8 -*-

def get_template_modals():
    return '''
    <!-- ===================================================================== -->
    <!-- MODAL 1: ADD / APPOINT BOOTH AGENT -->
    <!-- ===================================================================== -->
    @if(showAddAgentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন পোলিং এজেন্ট নিয়োগ ফর্ম</h2>
            <button class="close-btn" (click)="closeAddAgentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewBoothAgent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র নির্বাচন করুন *</label>
                <select [(ngModel)]="newAgentForm.centerId" name="centerId" (change)="onResultCenterSelectChange()" required>
                  <option value="" disabled>ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>ভোটকক্ষ / বুথ নম্বর *</label>
                <select [(ngModel)]="newAgentForm.boothId" name="boothId" required>
                  <option value="" disabled>বুথ পছন্দ করুন</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>এজেন্টের ধরন *</label>
                <select [(ngModel)]="newAgentForm.agentType" name="agentType" required>
                  <option value="PRIMARY">মূল এজেন্ট (Primary)</option>
                  <option value="RESERVE">বিকল্প এজেন্ট (Reserve)</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>এজেন্টের পূর্ণ নাম *</label>
                <input [(ngModel)]="newAgentForm.fullName" name="fullName" required placeholder="যেমন: মো: কামরুল ইসলাম">
              </div>

              <div class="form-field">
                <label>জাতীয় পরিচয়পত্র নম্বর (NID) *</label>
                <input [(ngModel)]="newAgentForm.nidNumber" name="nidNumber" required placeholder="১০ বা ১৭ ডিজিটের NID">
              </div>

              <div class="form-field">
                <label>ভোটার নম্বর</label>
                <input [(ngModel)]="newAgentForm.voterNumber" name="voterNumber" placeholder="যেমন: VOT-10492">
              </div>

              <div class="form-field">
                <label>মোবাইল ফোন নম্বর *</label>
                <input [(ngModel)]="newAgentForm.phone" name="phone" required placeholder="যেমন: 01711223344">
              </div>

              <div class="form-field wide">
                <label>মন্তব্য / দায়িত্ব পালনের নোট</label>
                <input [(ngModel)]="newAgentForm.notes" name="notes" placeholder="যেমন: সকাল ৭টায় উপস্থিতি ও ব্যালট বাক্স পরীক্ষা">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddAgentModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingAgent()">
                {{savingAgent() ? 'সংরক্ষণ হচ্ছে…' : 'পোলিং এজেন্ট নিয়োগ নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 2: PRINTABLE BANGLADESH ELECTION COMMISSION FORM-9 -->
    <!-- ===================================================================== -->
    @if(selectedAgentForForm9()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>ফরম-৯ প্রিন্ট প্রিভিউ (পোলিং এজেন্ট নিয়োগপত্র)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeForm9Preview()">✕</button>
            </div>
          </div>

          <div class="official-form9-paper">
            <div class="form9-header">
              <div class="gov-seal">🇧🇩</div>
              <h2 class="form9-title">ফরম - ৯</h2>
              <p class="form9-sub">[বিধি ২৪ (১) দ্রষ্টব্য]</p>
              <h3 class="form9-main-title">পোলিং এজেন্ট নিয়োগপত্র</h3>
            </div>

            <div class="form9-body">
              <p>বরাবর,</p>
              <p class="recipient-line">
                প্রিজাইডিং অফিসার,<br/>
                <b>{{selectedAgentForForm9()!.centerName}}</b> ভোটকেন্দ্র।
              </p>

              <p class="paragraph-text">
                আমি <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b>, নির্বাচনী এলাকা: <b>{{data()!.areaName || 'নির্বাচনী এলাকা'}}</b>
                (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn}}</b>)-এর
                প্রতিদ্বন্দ্বী প্রার্থী হিসেবে এতদ্বারা নিম্নবর্ণিত ব্যক্তিকে অত্র ভোটকেন্দ্রে
                <b>{{selectedAgentForForm9()!.boothName || 'সকল বুথে'}}</b> আমার পোলিং এজেন্ট হিসেবে দায়িত্ব পালনের জন্য নিয়োগ প্রদান করিলাম।
              </p>

              <div class="agent-spec-table">
                <table>
                  <tr>
                    <td class="lbl">পোলিং এজেন্টের নাম:</td>
                    <td class="val"><b>{{selectedAgentForForm9()!.fullName}}</b></td>
                  </tr>
                  <tr>
                    <td class="lbl">জাতীয় পরিচয়পত্র নম্বর (NID):</td>
                    <td class="val"><b>{{selectedAgentForForm9()!.nidNumber}}</b></td>
                  </tr>
                  <tr>
                    <td class="lbl">ভোটার তালিকা নম্বর:</td>
                    <td class="val">{{selectedAgentForForm9()!.voterNumber || 'প্রযোজ্য'}}</td>
                  </tr>
                  <tr>
                    <td class="lbl">যোগাযোগের মোবাইল নম্বর:</td>
                    <td class="val">{{selectedAgentForForm9()!.phone}}</td>
                  </tr>
                  <tr>
                    <td class="lbl">দায়িত্বের ধরন:</td>
                    <td class="val">{{selectedAgentForForm9()!.agentType === 'PRIMARY' ? 'মূল পোলিং এজেন্ট' : 'বিকল্প এজেন্ট'}}</td>
                  </tr>
                </table>
              </div>

              <div class="declaration-block">
                <p><b>এজেন্টের সম্মতি ও অঙ্গীকার:</b></p>
                <p class="declaration-text">
                  আমি অত্র ভোটকেন্দ্রে প্রতিদ্বন্দ্বী প্রার্থীর পোলিং এজেন্ট হিসেবে দায়িত্ব পালনে সম্মত আছি
                  এবং ভোটগ্রহণের গোপনীয়তা ও নির্বাচন কমিশনের সকল আইন ও আচরণবিধি যথাযথভাবে মানিয়া চলিব।
                </p>
              </div>

              <div class="signatures-row">
                <div class="sig-col">
                  <div class="sig-line"></div>
                  <b>{{selectedAgentForForm9()!.fullName}}</b>
                  <p class="sig-caption">নিযুক্ত পোলিং এজেন্টের স্বাক্ষর ও তারিখ</p>
                </div>
                <div class="sig-col">
                  <div class="sig-line"></div>
                  <b>{{data()!.candidate?.name || 'প্রার্থীর স্বাক্ষর'}}</b>
                  <p class="sig-caption">প্রতিদ্বন্দ্বী প্রার্থী / প্রধান নির্বাচনী এজেন্টের স্বাক্ষর</p>
                  <p class="sig-symbol">প্রতীক: {{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 3: SINGLE AGENT ID BADGE -->
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
              <span class="badge-emblem">🇧🇩</span>
              <div class="badge-title-block">
                <p class="badge-org">বাংলাদেশ নির্বাচন কমিশন</p>
                <h4 class="badge-type">পোলিং এজেন্ট পরিচয়পত্র</h4>
              </div>
            </div>

            <div class="badge-symbol-hero">
              <span class="badge-symbol-emoji">{{data()!.candidate?.symbolEmoji || '🗳️'}}</span>
              <div class="badge-cand-details">
                <span class="badge-cand-name">{{data()!.candidate?.name}}</span>
                <span class="badge-symbol-txt">{{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn}} মার্কা</span>
              </div>
            </div>

            <div class="badge-photo-id-row">
              <div class="badge-photo-box">
                @if(selectedAgentForBadge()!.photoUrl){
                  <img [src]="selectedAgentForBadge()!.photoUrl" alt="agent" class="badge-img">
                } @else {
                  <div class="badge-placeholder">ছবির স্থান</div>
                }
              </div>
              <div class="badge-bio">
                <div class="badge-field">
                  <span class="lbl">নাম:</span>
                  <b class="val">{{selectedAgentForBadge()!.fullName}}</b>
                </div>
                <div class="badge-field">
                  <span class="lbl">কেন্দ্র:</span>
                  <span class="val">{{selectedAgentForBadge()!.centerName}}</span>
                </div>
                <div class="badge-field">
                  <span class="lbl">বুথ নং:</span>
                  <b class="val">{{selectedAgentForBadge()!.boothName || 'সকল বুথ'}}</b>
                </div>
                <div class="badge-field">
                  <span class="lbl">NID:</span>
                  <span class="val mono">{{selectedAgentForBadge()!.nidNumber}}</span>
                </div>
                <div class="badge-field">
                  <span class="lbl">মোবাইল:</span>
                  <span class="val">{{selectedAgentForBadge()!.phone}}</span>
                </div>
              </div>
            </div>

            <div class="badge-footer">
              <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 4: BATCH ID CARDS (Photo ID Card Generator - 4 per page with QR) -->
    <!-- ===================================================================== -->
    @if(showBatchIdCardsModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(920px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <div>
              <h2>🪪 পোলিং এজেন্টদের অফিশিয়াল ব্যাচ আইডি কার্ড (Batch Print)</h2>
              <span style="font-size: 0.85rem; color: #64748b;">প্রতিটি কেন্দ্রের বুথ এজেন্টদের জন্য প্রার্থীর প্রতীক, নাম, কিউআর কোড এবং বুথ নম্বরসহ আইডি কার্ড (৪টি প্রতি পেইজ)</span>
            </div>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ব্যাচ প্রিন্ট করুন (A4)</button>
              <button class="close-btn" (click)="closeBatchIdCardsModal()">✕</button>
            </div>
          </div>

          <div class="batch-id-cards-page">
            <div class="batch-cards-grid">
              @for(ag of boothAgents(); track ag.boothAgentId){
                <div class="official-agent-card">
                  <!-- Header -->
                  <div class="card-ec-header">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span style="font-size: 1.4rem;">🇧🇩</span>
                      <div>
                        <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: #1e293b;">বাংলাদেশ নির্বাচন ২০২৬</div>
                        <div style="font-size: 0.82rem; font-weight: 800; color: #047857;">অফিসিয়াল পোলিং এজেন্ট কার্ড</div>
                      </div>
                    </div>
                    <span style="font-size: 0.7rem; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: 700;">FORM-9 ISSUED</span>
                  </div>

                  <!-- Candidate & Symbol Row -->
                  <div class="card-candidate-banner">
                    <span class="card-symbol-badge">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                    <div style="flex: 1; min-width: 0;">
                      <b style="font-size: 0.95rem; color: #064e3b; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{data()?.candidate?.name || 'প্রার্থী'}}</b>
                      <span style="font-size: 0.78rem; color: #047857; font-weight: 700;">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}} মার্কা · {{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</span>
                    </div>
                  </div>

                  <!-- Agent Details & QR Code Row -->
                  <div class="card-details-grid">
                    <div class="card-photo-box">
                      @if(ag.photoUrl){
                        <img [src]="ag.photoUrl" alt="agent" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px;">
                      } @else {
                        <div class="photo-placeholder-box">
                          <span>👤</span>
                          <small>ছবি</small>
                        </div>
                      }
                    </div>

                    <div class="card-info-col">
                      <div class="info-row">
                        <span class="info-k">এজেন্টের নাম:</span>
                        <b class="info-v">{{ag.fullName}}</b>
                      </div>
                      <div class="info-row">
                        <span class="info-k">ভোটকেন্দ্র:</span>
                        <span class="info-v" style="font-weight: 700;">{{ag.centerName}}</span>
                      </div>
                      <div class="info-row highlight-booth">
                        <span class="info-k">নির্ধারিত বুথ:</span>
                        <b class="info-v" style="color: #047857; font-size: 0.9rem;">{{ag.boothName || 'সকল বুথ / সাধারণ'}}</b>
                      </div>
                      <div class="info-row">
                        <span class="info-k">NID নং:</span>
                        <span class="info-v mono">{{ag.nidNumber}}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-k">মোবাইল:</span>
                        <span class="info-v mono">{{ag.phone}}</span>
                      </div>
                    </div>

                    <!-- Dynamic QR Code -->
                    <div class="card-qr-box">
                      @if(batchAgentQrCodes()[ag.boothAgentId]){
                        <img [src]="batchAgentQrCodes()[ag.boothAgentId]" alt="Agent QR" style="width: 72px; height: 72px; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px; background: #fff;">
                      } @else {
                        <div style="width: 72px; height: 72px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; color: #64748b; text-align: center;">QR Code</div>
                      }
                      <small style="font-size: 0.6rem; color: #64748b; margin-top: 2px;">বৈধতা যাচাই</small>
                    </div>
                  </div>

                  <!-- Footer -->
                  <div class="card-ec-footer">
                    <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
                    <span>স্মারক: FORM9/{{ag.boothAgentId.slice(0,6).toUpperCase()}}</span>
                  </div>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 5: ADD NEW VOTER -->
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
                <input [(ngModel)]="newVoterForm.voterNumber" name="vNumber" required placeholder="যেমন: VOT-10492">
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
    <!-- MODAL 6: BULK VOTER IMPORT (Excel / CSV / PDF) -->
    <!-- ===================================================================== -->
    @if(showBulkImportModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(720px, 95vw);">
          <div class="modal-header">
            <h2>📥 বাল্ক ভোটার তালিকা ইম্পোর্ট (Excel / CSV / PDF)</h2>
            <button class="close-btn" (click)="closeBulkImportModal()">✕</button>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <p style="font-size: 0.88rem; color: #475569; margin: 0;">
              নির্বাচন কমিশনের ভোটার তালিকার Excel (.xlsx) বা CSV ফাইল আপলোড করে এক ক্লিকে সকল ভোটারের তথ্য যুক্ত করুন।
            </p>

            <div class="form-field">
              <label>ডিফল্ট ভোটকেন্দ্র নির্বাচন করুন *</label>
              <select [(ngModel)]="bulkImportCenterId" (change)="onBulkCenterChange()">
                <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                @for(c of centersList(); track c.centerId){
                  <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                }
              </select>
            </div>

            <div style="border: 2px dashed var(--line); border-radius: 12px; padding: 24px; text-align: center; background: #f8fafc;">
              <input type="file" (change)="onBulkFileSelected($event)" accept=".xlsx,.csv,.pdf,.txt" style="display: none;" #bulkFileInput>
              <span style="font-size: 2.2rem; display: block; margin-bottom: 8px;">📑</span>
              <button type="button" class="primary-button" (click)="bulkFileInput.click()">ফাইল বাছাই করুন (.xlsx / .csv)</button>
              <span style="display: block; font-size: 0.78rem; color: #64748b; margin-top: 8px;">বা ড্র্যাগ করে এখানে ফেলুন</span>
            </div>

            @if(bulkPreview()){
              <div style="background: #f1f5f9; padding: 12px; border-radius: 8px; font-size: 0.85rem;">
                <b>প্রিভিউ:</b> মোট {{bulkPreview()!.totalRowsDetected}}টি রেকর্ড পাওয়া গেছে (বৈধ: {{bulkPreview()!.validRowsCount}}, ত্রুটি: {{bulkPreview()!.invalidRowsCount}})।
              </div>
            }

            <div class="modal-actions" style="margin-top: 10px;">
              <button type="button" class="text-button" (click)="closeBulkImportModal()">বাতিল</button>
              <button class="primary-button" [disabled]="importingBulk() || !bulkPreview()" (click)="confirmBulkImport()">
                {{importingBulk() ? 'ইম্পোর্ট হচ্ছে…' : 'ইম্পোর্ট নিশ্চিত করুন'}}
              </button>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 7: BATCH VOTER SLIPS PRINT PREVIEW -->
    <!-- ===================================================================== -->
    @if(showVoterSlipsPrint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card wide-slip-modal" style="width: min(850px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <h2>ভোটার স্লিপ প্রিন্ট প্রিভিউ (প্রার্থীর মার্কা ও ভোটার তথ্য)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন (A4)</button>
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
                      <b class="slip-serial-num">#{{v.serialNumber}}</b>
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
    <!-- MODAL 8: SMART DIGITAL VOTER SLIP CARD WITH QR CODE (Digital Pass) -->
    <!-- ===================================================================== -->
    @if(selectedVoterForSlip()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card smart-slip-modal-card" style="width: min(540px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h2>🎫 স্মার্ট ডিজিটাল ভোটার স্লিপ (Digital Pass)</h2>
            <button class="close-btn" (click)="closeSmartSlip()">✕</button>
          </div>

          <!-- Digital Card View -->
          <div class="digital-slip-card" style="background: linear-gradient(135deg, #064e3b, #047857); color: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px rgba(4,120,87,0.3); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 12px; margin-bottom: 14px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.8rem; background: rgba(255,255,255,0.15); border-radius: 12px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                <div>
                  <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #fff;">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</h3>
                  <p style="margin: 2px 0 0; font-size: 0.85rem; color: #a7f3d0; font-weight: 600;">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}} মার্কা · {{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</p>
                </div>
              </div>
              <div style="text-align: right;">
                <span style="display: block; font-size: 0.75rem; text-transform: uppercase; color: #6ee7b7; font-weight: 700;">তালিকা ক্রমিক</span>
                <b style="font-size: 1.8rem; line-height: 1; color: #fef08a;">#{{selectedVoterForSlip()!.serialNumber}}</b>
              </div>
            </div>

            <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 14px; margin-bottom: 14px;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">ভোটারের নাম:</span>
                  <b style="font-size: 1rem; color: #fff;">{{selectedVoterForSlip()!.fullName}}</b>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">পিতা/স্বামীর নাম:</span>
                  <span style="color: #f3f4f6;">{{selectedVoterForSlip()!.fatherOrSpouseName || '—'}}</span>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">জাতীয় পরিচয়পত্র (NID):</span>
                  <b style="letter-spacing: 0.5px; color: #fef08a;">{{selectedVoterForSlip()!.voterNumber}}</b>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">বয়স ও লিঙ্গ:</span>
                  <span>{{selectedVoterForSlip()!.age || '—'}} বছর ({{selectedVoterForSlip()!.gender === 'FEMALE' ? 'নারী' : 'পুরুষ'}})</span>
                </div>
              </div>
            </div>

            <!-- Polling Center Highlight -->
            <div style="background: #ffffff; color: #0f172a; border-radius: 12px; padding: 14px; display: flex; justify-content: space-between; align-items: center; gap: 14px;">
              <div style="flex: 1;">
                <span style="display: block; font-size: 0.72rem; text-transform: uppercase; color: #047857; font-weight: 800; letter-spacing: 0.5px;">নির্ধারিত ভোটকেন্দ্র</span>
                <b style="font-size: 1.05rem; color: #064e3b; display: block; margin: 2px 0;">{{selectedVoterForSlip()!.centerName}}</b>
                <span style="font-size: 0.85rem; color: #475569; display: flex; align-items: center; gap: 6px;">
                  <span>বুথ: <b style="color: #047857;">{{selectedVoterForSlip()!.boothName || 'সাধারণ বুথ'}}</b></span>
                  @if(selectedVoterForSlip()!.areaName){
                    <span>· এলাকা: {{selectedVoterForSlip()!.areaName}}</span>
                  }
                </span>
              </div>

              <!-- Dynamic QR Code Container -->
              <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px; text-align: center;">
                @if(voterQrCodeDataUrl()){
                  <img [src]="voterQrCodeDataUrl()" alt="Voter QR" style="width: 84px; height: 84px; display: block;">
                } @else {
                  <div style="width: 84px; height: 84px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #94a3b8;">QR কোড</div>
                }
                <span style="display: block; font-size: 0.65rem; color: #64748b; font-weight: 600; margin-top: 2px;">ডিজিটাল ভেরিফিকেশন</span>
              </div>
            </div>

            <div style="margin-top: 14px; text-align: center; font-size: 0.8rem; color: #a7f3d0; border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 10px;">
              ভোটগ্রহণের দিন এই ডিজিটাল কার্ড বা প্রিন্ট কপি সাথে নিয়ে কেন্দ্রে উপস্থিত হোন।
            </div>
          </div>

          <!-- Actions: WhatsApp 1-Click + Print -->
          <div style="display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap;">
            <button class="primary-button" style="background: #25d366; color: #fff; border: none; display: flex; align-items: center; gap: 8px;" (click)="sendSingleVoterWhatsApp(selectedVoterForSlip()!)" [disabled]="!selectedVoterForSlip()!.phone">
              <span>💬</span> হোয়াটসঅ্যাপে ডিজিটাল স্লিপ পাঠান (1-Click)
            </button>
            <button class="btn-sm" style="background: #0369a1; color: #fff;" (click)="triggerBrowserPrint()">
              🖨️ স্লিপ প্রিন্ট করুন
            </button>
            <button class="text-button" (click)="closeSmartSlip()">বন্ধ করুন</button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 9: CANDIDATE BULK VOTER BROADCAST (SMS & Free WhatsApp Dispatcher) -->
    <!-- ===================================================================== -->
    @if(showVoterBroadcastModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(680px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <div>
              <h2 style="margin: 0;">📱 ভোটার বাল্ক ম্যাসেজিং ও ডিজিটাল স্লিপ ডিসপ্যাচ</h2>
              <span style="font-size: 0.85rem; color: #64748b;">সকল ভোটারকে এক ক্লিকে কেন্দ্র, বুথ, ক্রমিক নম্বর ও মার্কার তথ্যসহ স্মার্ট স্লিপ পাঠান</span>
            </div>
            <button class="close-btn" (click)="closeVoterBroadcastModal()">✕</button>
          </div>

          <!-- Channel Selection Tabs -->
          <div style="display: flex; gap: 10px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;">
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'WHATSAPP'" (click)="voterBroadcastChannel.set('WHATSAPP')" style="flex: 1; padding: 10px 14px; border-radius: 8px; border: 1px solid #25d366; background: voterBroadcastChannel() === 'WHATSAPP' ? '#dcfce7' : '#fff'; font-weight: 700; color: #166534; cursor: pointer;">
              🟢 হোয়াটসঅ্যাপ ডিসপ্যাচ (ফ্রি / ০ টাকা)
            </button>
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'SMS'" (click)="voterBroadcastChannel.set('SMS')" style="flex: 1; padding: 10px 14px; border-radius: 8px; border: 1px solid #0284c7; background: voterBroadcastChannel() === 'SMS' ? '#e0f2fe' : '#fff'; font-weight: 700; color: #0369a1; cursor: pointer;">
              📱 মোবাইল বাল্ক SMS গেটওয়ে
            </button>
          </div>

          <!-- WhatsApp Sub-mode & Live Bot QR Controller -->
          @if(voterBroadcastChannel() === 'WHATSAPP'){
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">
              <label style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 8px;">হোয়াটসঅ্যাপ প্রেরণের মোড:</label>
              <div style="display: flex; gap: 10px;">
                <button type="button" [class.active-pill]="waDispatchMode() === 'AUTO_BOT'" (click)="waDispatchMode.set('AUTO_BOT')" class="target-pill" style="flex: 1; text-align: center; padding: 8px 12px; font-weight: 700;">
                  🤖 ১০০% অটো-বট (কোনো ক্লিক ছাড়া একা একা যাবে)
                </button>
                <button type="button" [class.active-pill]="waDispatchMode() === 'MANUAL_CLICK'" (click)="waDispatchMode.set('MANUAL_CLICK')" class="target-pill" style="flex: 1; text-align: center; padding: 8px 12px; font-weight: 700;">
                  📱 ১-ক্লিক ওয়েব কিউ (ব্রাউজার দিয়ে পাঠানো)
                </button>
              </div>

              <!-- Live Auto-Bot Section -->
              @if(waDispatchMode() === 'AUTO_BOT'){
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                  @if(waBotStatus()?.connected){
                    <div style="background: #dcfce7; border: 1px solid #86efac; border-radius: 8px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;">
                      <div>
                        <b style="color: #166534; font-size: 0.95rem; display: block;">✅ হোয়াটসঅ্যাপ রোবট সংযুক্ত রয়েছে!</b>
                        <span style="font-size: 0.82rem; color: #15803d;">প্রেরক অ্যাকাউন্ট: <b>+{{waBotStatus()?.phone}}</b></span>
                      </div>
                      <button type="button" class="btn-sm outline" style="color: #b91c1c; border-color: #fca5a5;" (click)="logoutWaBot()">
                        লগআউট / নতুন নম্বর
                      </button>
                    </div>

                    @if(waBotStatus()?.queueStats?.status === 'PROCESSING'){
                      <div style="margin-top: 10px; background: #fff; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; color: #166534; margin-bottom: 4px;">
                          <span>🔄 ব্যাকগ্রাউন্ডে ভোটারদের পাঠানো হচ্ছে…</span>
                          <span>{{waBotStatus()?.queueStats?.sent}} / {{waBotStatus()?.queueStats?.total}} সম্পন্ন</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b;">
                          বর্তমান ভোটার: <b>{{waBotStatus()?.queueStats?.currentVoter || 'প্রস্তুত হচ্ছে…'}}</b> (স্প্যাম সুরক্ষা বিরতি: ৩.৫ সেঃ)
                        </div>
                      </div>
                    }
                  } @else {
                    <div style="background: #fff; border: 2px dashed #38bdf8; border-radius: 10px; padding: 16px; text-align: center;">
                      <h4 style="margin: 0 0 6px; color: #0369a1;">📱 আপনার মোবাইল WhatsApp দিয়ে একবার কিউআর স্ক্যান করুন</h4>
                      <p style="margin: 0 0 10px; font-size: 0.82rem; color: #64748b;">
                        ফোনের WhatsApp অ্যাপ খুলুন ➔ Settings ➔ <b>Linked Devices</b> ➔ <b>Link a Device</b> নির্বাচন করে ক্যামেরা দিয়ে নিচের কিউআর কোডটি স্ক্যান করুন:
                      </p>
                      @if(waBotQr()){
                        <img [src]="waBotQr()" alt="WhatsApp Pairing QR" style="width: 190px; height: 190px; border-radius: 8px; border: 3px solid #e2e8f0; margin-bottom: 8px;">
                      } @else {
                        <div style="padding: 30px; color: #94a3b8;">কিউআর কোড জেনারেট হচ্ছে…</div>
                      }
                      <div>
                        <button type="button" class="btn-sm outline" (click)="loadWaBotStatus()">🔄 কিউআর রিফ্রেশ করুন</button>
                      </div>
                    </div>
                  }
                </div>
              }
            </div>
          }

          <!-- Target Filter Group -->
          <div class="form-field" style="margin-bottom: 14px;">
            <label style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 6px;">প্রাপক ভোটার ফিল্টার:</label>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px;">
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'ALL'" (click)="voterBroadcastTarget.set('ALL')" class="target-pill">
                সব ভোটার ({{phonesCount()}} জন)
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'UNISSUED_SLIP_ONLY'" (click)="voterBroadcastTarget.set('UNISSUED_SLIP_ONLY')" class="target-pill">
                স্লিপ বাকি ({{voters().length - issuedSlipsCount()}} জন)
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'SUPPORTERS'" (click)="voterBroadcastTarget.set('SUPPORTERS')" class="target-pill">
                সমর্থক ভোটার
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'SWING'" (click)="voterBroadcastTarget.set('SWING')" class="target-pill">
                দোদুল্যমান ভোটার
              </button>
            </div>
          </div>

          <!-- Message Composer with Dynamic Tags -->
          <div class="form-field" style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <label style="font-weight: 700; color: var(--navy);">বার্তা প্রস্তুত করুন (Dynamic Voter Tags):</label>
              <span style="font-size: 0.78rem; color: #64748b;">ক্লিক করে ট্যাগ যুক্ত করুন</span>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px;">
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{নাম}')">+ ভোটারের নাম</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{ভোটকেন্দ্র}')">+ ভোটকেন্দ্র</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{বুথ}')">+ বুথ</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{ক্রমিক}')">+ ক্রমিক নং</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{মার্কা}')">+ প্রার্থীর মার্কা</button>
            </div>
            <textarea [(ngModel)]="voterBroadcastCustomMessage" rows="4" style="width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px; font-size: 0.9rem;" placeholder="বার্তা লিখুন..."></textarea>
          </div>

          <!-- Live Preview & Cost Banner -->
          <div style="background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 12px; margin-bottom: 16px; font-size: 0.85rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span style="color: #64748b; font-weight: 600;">নমুনা মেসেজ প্রিভিউ:</span>
              <span style="color: #0369a1; font-weight: 700;">{{smsCharCount()}} অক্ষর · {{smsPartsCount()}} SMS পার্ট</span>
            </div>
            <div style="background: #fff; border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 0 6px 6px 0; font-style: italic; color: #334155;">
              {{getInterpolatedPreview()}}
            </div>
            @if(voterBroadcastChannel() === 'SMS'){
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0;">
                <span>আনুমানিক মোট খরচ: <b>৳{{calculateSmsCost() | number:'1.2-2'}}</b> (প্রতি SMS ৳০.৩০)</span>
                <span style="color: #059669; font-weight: 700;">গেটওয়ে ব্যালেন্স: ৳{{smsConfig()?.balance || 2499.10 | number:'1.2-2'}}</span>
              </div>
            } @else {
              <div style="margin-top: 8px; color: #166534; font-weight: 700;">
                ✓ হোয়াটসঅ্যাপ কিউ সম্পূর্ণ বিনামূল্যে (৳০.০০) পরিচালিত হবে।
              </div>
            }
          </div>

          <!-- WhatsApp Interactive Auto-Queue Dispatcher -->
          @if(voterBroadcastQueue().length > 0){
            <div class="whatsapp-queue-box" style="border: 2px solid #25d366; border-radius: 12px; padding: 16px; background: #f0fdf4; margin-bottom: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <b style="color: #166534; font-size: 1rem;">হোয়াটসঅ্যাপ প্রেরক কিউ ({{dispatchCurrentIndex() + 1}} / {{voterBroadcastQueue().length}})</b>
                <span class="badge badge-complete">{{calcQueuePercent() | number:'1.0-0'}}% সম্পন্ন</span>
              </div>

              @if(dispatchCurrentIndex() < voterBroadcastQueue().length){
                <div style="background: #fff; border-radius: 8px; padding: 12px; border: 1px solid #bbf7d0; margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <b style="font-size: 1.05rem; color: #064e3b;">{{currentQueueItem()!.fullName}}</b>
                      <span style="display: block; font-size: 0.82rem; color: #475569;">{{currentQueueItem()!.phone}} · কেন্দ্র: {{currentQueueItem()!.centerName}}</span>
                    </div>
                    <a [href]="currentQueueItem()!.waUrl" target="_blank" class="primary-button" style="background: #25d366; text-decoration: none;" (click)="dispatchNextInQueue()">
                      💬 হোয়াটসঅ্যাপে পাঠান ➔
                    </a>
                  </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <button type="button" class="btn-sm" [class.highlight-btn]="isAutoDispatching()" (click)="toggleAutoDispatch()">
                      {{isAutoDispatching() ? '⏸️ অটো-ডিসপ্যাচ পজ করুন' : '▶️ অটো-ডিসপ্যাচ চালু করুন (২.৮ সেঃ)'}}
                    </button>
                  </div>
                  <button type="button" class="btn-sm outline" (click)="dispatchNextInQueue()">পরবর্তী ভোটার স্কিপ ⏭️</button>
                </div>
              } @else {
                <div style="text-align: center; padding: 20px; color: #166534;">
                  <span style="font-size: 2rem;">🎉</span>
                  <h3 style="margin: 8px 0 4px;">সকল ভোটারকে সফলভাবে হোয়াটসঅ্যাপে বার্তা পাঠানো সম্পন্ন হয়েছে!</h3>
                  <p style="margin: 0; font-size: 0.85rem;">সবার ভোটার স্লিপ স্ট্যাটাস স্বয়ংক্রিয়ভাবে "ইস্যু সম্পন্ন" হিসেবে চিহ্নিত করা হয়েছে।</p>
                </div>
              }
            </div>
          }

          <div class="modal-actions">
            <button type="button" class="text-button" (click)="closeVoterBroadcastModal()">বন্ধ করুন</button>
            @if(voterBroadcastQueue().length === 0){
              <button class="primary-button" [disabled]="sendingVoterBroadcast()" (click)="submitVoterBroadcast()">
                {{sendingVoterBroadcast() ? 'প্রস্তুত হচ্ছে…' : (voterBroadcastChannel() === 'SMS' ? 'এক ক্লিকে বাল্ক SMS পাঠান' : 'হোয়াটসঅ্যাপ প্রেরক কিউ শুরু করুন')}}
              </button>
            }
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 10: SMS GATEWAY CONFIGURATION & TEST TOOL -->
    <!-- ===================================================================== -->
    @if(showSmsConfigModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(560px, 95vw);">
          <div class="modal-header">
            <h2>⚙️ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন</h2>
            <button class="close-btn" (click)="closeSmsConfigModal()">✕</button>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <!-- Current Balance Banner -->
            <div style="background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; color: #bae6fd; font-weight: 700;">চলতি SMS অ্যাকাউন্ট ব্যালেন্স</span>
                <b style="font-size: 1.6rem; display: block; margin-top: 2px;">৳{{smsConfig()?.balance || 2499.10 | number:'1.2-2'}}</b>
              </div>
              <span class="badge" style="background: rgba(255,255,255,0.2); color: #fff; font-weight: 700;">{{smsConfigProvider()}}</span>
            </div>

            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px; margin-top: 8px; font-size: 0.82rem; color: #166534; display: flex; align-items: center; gap: 8px;">
              <span>🌐</span>
              <div>
                <b>portal.sms.net.bd ইন্টিগ্রেশন সক্রিয়:</b> API এন্ডপয়েন্ট <code>https://api.sms.net.bd/sendsms</code> এবং আপনার ড্যাশবোর্ডের API কী সেট করা হয়েছে।
              </div>
            </div>

            <div class="form-grid">
              <div class="form-field wide">
                <label>এসএমএস গেটওয়ে প্রোভাইডার *</label>
                <select [(ngModel)]="smsConfigProvider" (ngModelChange)="onSmsProviderChange($event)">
                  <option value="SMS_NET_BD">🇧🇩 এসএমএস.নেট.বিডি (SMS.NET.BD / Alpha SMS - ড্যাশবোর্ড কানেক্টেড)</option>
                  <option value="SIMULATOR">🧪 সিমুলেটর গেটওয়ে (টেস্ট ও ফ্রি সিমুলেশন)</option>
                  <option value="GREENWEB">গ্রিনওয়েব বাংলাদেশ (Greenweb API)</option>
                  <option value="SSL_WIRELESS">এসএসএল ওয়্যারলেস (SSL Wireless)</option>
                  <option value="CUSTOM_HTTP">কাস্টম REST API</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>API Key / টোকেন *</label>
                <input [(ngModel)]="smsConfigApiKey" placeholder="যেমন: gw_live_secret_key_xxxx">
              </div>

              <div class="form-field">
                <label>সেন্ডার আইডি / মাস্কিং নাম</label>
                <input [(ngModel)]="smsConfigSenderId" placeholder="যেমন: SCALE_FARUK">
              </div>

              <div class="form-field">
                <label>এপিআই এন্ডপয়েন্ট URL</label>
                <input [(ngModel)]="smsConfigEndpoint" placeholder="http://api.greenweb.com.bd/api.php">
              </div>
            </div>

            <!-- Test SMS Sandbox Box -->
            <div style="background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 12px; margin-top: 6px;">
              <span style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 6px;">🧪 তাৎক্ষণিক টেস্ট এসএমএস পাঠান:</span>
              <div style="display: flex; gap: 8px;">
                <input [(ngModel)]="smsTestPhone" placeholder="01717208118" style="flex: 1; padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px;">
                <button type="button" class="btn-sm" [disabled]="testingSms()" (click)="sendTestSms()">
                  {{testingSms() ? 'পাঠানো হচ্ছে…' : 'টেস্ট SMS পাঠান'}}
                </button>
              </div>
              @if(smsTestResult()){
                <span style="display: block; font-size: 0.8rem; color: #059669; margin-top: 6px; font-weight: 600;">{{smsTestResult()}}</span>
              }
            </div>

            <div class="modal-actions" style="margin-top: 10px;">
              <button type="button" class="text-button" (click)="closeSmsConfigModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingSmsConfig()" (click)="saveSmsConfig()">
                {{savingSmsConfig() ? 'সংরক্ষণ হচ্ছে…' : 'কনফিগারেশন সংরক্ষণ করুন'}}
              </button>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 11: ADD CAMPAIGN EVENT -->
    <!-- ===================================================================== -->
    @if(showAddCampaignModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন নির্বাচনী প্রচার কর্মসূচি ও সমাবেশ</h2>
            <button class="close-btn" (click)="closeAddCampaignModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewCampaignEvent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>কর্মসূচির শিরোনাম *</label>
                <input [(ngModel)]="newCampaignForm.title" name="cpTitle" required placeholder="যেমন: ১ নং ওয়ার্ডে নির্বাচনী পথসমাবেশ">
              </div>

              <div class="form-field">
                <label>কর্মসূচির ধরন *</label>
                <select [(ngModel)]="newCampaignForm.eventType" name="cpType" required>
                  <option value="RALLY">জনসভা / পথসমাবেশ</option>
                  <option value="YARD_MEETING">উঠান বৈঠক / কর্মী সভা</option>
                  <option value="DOOR_TO_DOOR">ভোটারদের বাড়ি বাড়ি গণসংযোগ</option>
                  <option value="MOTORCADE">মাইকিং রোডশো / পদযাত্রা</option>
                </select>
              </div>

              <div class="form-field">
                <label>জনসভাস্থল নির্বাচন *</label>
                <select [(ngModel)]="newCampaignForm.venueId" name="cpVenue">
                  @for(v of campaignVenues(); track v.venueId){
                    <option [value]="v.venueId">{{v.name}} (ধারনক্ষমতা: {{v.capacity | number}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>শুরুর সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.startTime" name="cpStart" required>
              </div>

              <div class="form-field">
                <label>সমাপ্তির সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.endTime" name="cpEnd" required>
              </div>

              <div class="form-field">
                <label>প্রত্যাশিত জমায়েত (লোকসংখ্যা)</label>
                <input type="number" [(ngModel)]="newCampaignForm.expectedAttendance" name="cpAtt" min="10" placeholder="যেমন: ৫০০">
              </div>

              <div class="form-field">
                <label>অনুমোদনকারী পুলিশ স্টেশন / প্রশাসন</label>
                <input [(ngModel)]="newCampaignForm.policeStationAuthority" name="cpAuth" placeholder="যেমন: দাগনভূঞা থানা ও ইউএনও">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddCampaignModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingCampaignEvent()">
                {{savingCampaignEvent() ? 'সংরক্ষণ হচ্ছে…' : 'প্রচার কর্মসূচি যুক্ত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 12: UPDATE PERMIT STATUS -->
    <!-- ===================================================================== -->
    @if(selectedEventForPermit()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(480px, 95vw);">
          <div class="modal-header">
            <h2>প্রশাসন পারমিট স্ট্যাটাস আপডেট</h2>
            <button class="close-btn" (click)="closeUpdatePermitModal()">✕</button>
          </div>

          <div class="form-grid">
            <div class="form-field wide">
              <label>অনুমোদনের স্ট্যাটাস *</label>
              <select [(ngModel)]="updatePermitStatus">
                <option value="APPROVED">APPROVED (অনুমোদিত)</option>
                <option value="PENDING">PENDING (আবেদন প্রক্রিয়াধীন)</option>
                <option value="REJECTED">REJECTED (প্রত্যাখ্যাত)</option>
              </select>
            </div>

            <div class="form-field wide">
              <label>অনুমোদন স্মারক নম্বর</label>
              <input [(ngModel)]="updatePermitRef" placeholder="যেমন: দাগন-থানা/অনুমতি/২০২৬/১১২">
            </div>

            <div class="form-field wide">
              <label>প্রশাসনের শর্তাবলি / নোট</label>
              <textarea [(ngModel)]="updatePermitConditions" rows="3" placeholder="যেমন: মাইকিং অবশ্যই রাত ৮টার মধ্যে শেষ করতে হবে"></textarea>
            </div>
          </div>

          <div class="modal-actions" style="margin-top: 14px;">
            <button type="button" class="text-button" (click)="closeUpdatePermitModal()">বাতিল</button>
            <button class="primary-button" (click)="submitUpdatePermit()">সংরক্ষণ করুন</button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 13: CAMPAIGN PERMIT NOTICE PRINT PREVIEW -->
    <!-- ===================================================================== -->
    @if(selectedEventForNotice()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>অনুমতিপত্র ও আইনি নোটিশ প্রিন্ট</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closePrintPermitNotice()">✕</button>
            </div>
          </div>

          <div class="official-complaint-paper">
            <div class="complaint-head">
              <div class="gov-seal">🇧🇩</div>
              <h3>নির্বাচনী জনসভা / পথসমাবেশ আয়োজনের অনুমতিপত্র ও আচরণবিধি নোটিশ</h3>
              <p class="complaint-sub">সংসদ নির্বাচন আচরণ বিধিমালা ২০০৮ মোতাবেক</p>
            </div>

            <div class="complaint-date-ref">
              <span>তারিখ: {{selectedEventForNotice()!.startsAt | date:'dd MMMM yyyy'}}</span>
              <span>স্মারক নং: {{selectedEventForNotice()!.permitReferenceNumber || 'ডিবি-অনুমতি/২০২৬/৩১০'}}</span>
            </div>

            <div class="complaint-recipient">
              <p><b>বরাবর,</b><br/>
              অফিসার ইনচার্জ (ওসি), {{selectedEventForNotice()!.issuingAuthority || 'থানা পুলিশ'}} / সহকারী রিটার্নিং অফিসার</p>
            </div>

            <div class="complaint-body-text">
              <p>মহোদয়,</p>
              <p>অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()!.candidate?.name}}</b> (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</b>)-এর পক্ষে জানানো যাচ্ছে যে, আগামী <b>{{selectedEventForNotice()!.startsAt | date:'mediumDate'}}</b> তারিখ বিকাল <b>{{selectedEventForNotice()!.startsAt | date:'shortTime'}}</b> ঘটিকা হইতে <b>{{selectedEventForNotice()!.venueName}}</b> প্রাঙ্গণে এক নির্বাচনী জনসভা আয়োজনের বিষয়ে আপনার কার্যালয়ের অনুমোদন কার্যকর রয়েছে।</p>

              <div class="incident-statement-box">
                <b>কর্মসূচির তথ্যাবলি:</b>
                <p>স্থান: {{selectedEventForNotice()!.venueName}}<br/>
                সময়: {{selectedEventForNotice()!.startsAt | date:'shortTime'}} - {{selectedEventForNotice()!.endsAt | date:'shortTime'}}<br/>
                শব্দযন্ত্র (মাইকিং): আচরণবিধি অনুযায়ী দুপুর ২:০০ থেকে রাত ৮:০০ এর মধ্যে সীমাবদ্ধ রাখা হবে।</p>
              </div>

              <p>উক্ত কর্মসূচিতে পর্যাপ্ত নিরাপত্তা ও ট্রাফিক শৃঙ্খলা বজায় রাখার সদয় অনুরোধ জানাচ্ছি।</p>
            </div>

            <div class="complaint-sig-row">
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>প্রধান নির্বাচনী এজেন্ট</b><br/>
                <span>{{data()!.candidate?.name}}-এর নির্বাচনী পরিচালনা কমিটি</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 14: ADD NEW INCIDENT -->
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
    <!-- MODAL 15: OFFICIAL MAGISTRATE & RETURNING OFFICER LEGAL COMPLAINT -->
    <!-- ===================================================================== -->
    @if(selectedIncidentForComplaint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(850px, 98vw); max-height: 92vh; overflow-y: auto;">
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
                <p style="margin-top: 6px; font-size: 0.82rem; color: #64748b;">
                  <b>অনিয়মের ধরন:</b> {{selectedIncidentForComplaint()!.incidentType}} ·
                  <b>তীব্রতা:</b> {{selectedIncidentForComplaint()!.severity}} ·
                  <b>প্রত্যক্ষদর্শী/সংবাদদাতা:</b> {{selectedIncidentForComplaint()!.reportedBy}} ({{selectedIncidentForComplaint()!.reportedByPhone || 'মোবাইল নেই'}})
                </p>
              </div>

              <p>উক্ত অনাকাঙ্ক্ষিত ঘটনার কারণে কেন্দ্রে সুষ্ঠু ও নিরপেক্ষ ভোটগ্রহণ মারাত্মকভাবে বিঘ্নিত হচ্ছে এবং ভোটার ও সাধারণ এজেন্টরা চরম নিরাপত্তাহীনতায় ভুগছেন।</p>

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

    <!-- ===================================================================== -->
    <!-- MODAL 16: QUICK RESULT ENTRY -->
    <!-- ===================================================================== -->
        <!-- ===================================================================== -->
    <!-- MODAL 15B: ADD OPPONENT CANDIDATE (নতুন প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করুন) -->
    <!-- ===================================================================== -->
    @if(showAddOpponentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(520px, 95vw);">
          <div class="modal-header">
            <h2>➕ নতুন প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করুন</h2>
            <button type="button" class="close-btn" (click)="closeAddOpponentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitAddOpponent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>প্রার্থীর পূর্ণ নাম *</label>
                <input type="text" [(ngModel)]="newOpponentForm.name" name="opp_name" required placeholder="উদাঃ তারেক হাসান / মোঃ কামাল হোসেন" />
              </div>

              <div class="form-field wide">
                <label>দল / রাজনৈতিক পরিচয় *</label>
                <input type="text" [(ngModel)]="newOpponentForm.partyName" name="opp_party" required placeholder="উদাঃ বিএনপি / জাতীয় পার্টি / স্বতন্ত্র প্রার্থী" />
              </div>

              <div class="form-field wide">
                <label>বরাদ্দকৃত প্রতীক *</label>
                <select [(ngModel)]="newOpponentForm.symbolId" name="opp_symbol" required>
                  <option [ngValue]="null" disabled>নির্বাচনী মার্কা / প্রতীক নির্বাচন করুন</option>
                  @for(s of electionSymbols(); track s.id){
                    <option [ngValue]="s.id">{{s.iconEmoji}} {{s.nameBn}} ({{s.nameEn}})</option>
                  }
                </select>
              </div>

              <div class="form-field wide">
                <label>নির্বাচনী স্লোগান (ঐচ্ছিক)</label>
                <input type="text" [(ngModel)]="newOpponentForm.slogan" name="opp_slogan" placeholder="উদাঃ উন্নয়নের মার্কা, জনগণের মার্কা" />
              </div>
            </div>

            <div class="modal-actions" style="margin-top: 18px;">
              <button type="button" class="text-button" (click)="closeAddOpponentModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingOpponent() || !newOpponentForm.name || !newOpponentForm.partyName">
                {{savingOpponent() ? 'সংরক্ষণ হচ্ছে…' : 'প্রার্থী নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 16: QUICK RESULT ENTRY (কেন্দ্রভিত্তিক প্রার্থীওয়ারী ভোট এন্ট্রি) -->
    <!-- ===================================================================== -->
    @if(showQuickResultModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(620px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h2>🗳️ কেন্দ্রের লাইভ ফলাফল এন্ট্রি</h2>
            <button type="button" class="close-btn" (click)="closeQuickResultModal()">✕</button>
          </div>

          <form (ngSubmit)="submitQuickResult()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র নির্বাচন করুন *</label>
                <select [(ngModel)]="quickResultForm.electionCenterId" name="electionCenterId" (change)="onResultCenterSelectChange()" required>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} (কোড: {{c.code}})</option>
                  }
                </select>
              </div>
            </div>

            <!-- Candidate-wise Vote Entry Inputs -->
            <div style="margin: 16px 0 10px; border-top: 1px solid var(--line); padding-top: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <label style="font-weight: 700; color: var(--navy); font-size: 0.95rem;">
                  প্রতিটি প্রার্থীর প্রাপ্ত ভোট লিখুন:
                </label>
                <button type="button" class="text-button" style="font-size: 0.82rem; color: #2563eb;" (click)="openAddOpponentModal()">
                  ➕ নতুন প্রার্থী যোগ করুন
                </button>
              </div>

              <div style="display: flex; flex-direction: column; gap: 10px;">
                @for(cand of candidateListForEntry(); track cand.candidateId){
                  <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-radius: 8px; border: 1px solid;"
                       [style.background]="cand.isPrimary ? '#ecfdf5' : '#f8fafc'"
                       [style.borderColor]="cand.isPrimary ? '#a7f3d0' : '#e2e8f0'">
                    <div style="display: flex; align-items: center; gap: 12px;">
                      <span style="font-size: 1.6rem;">{{cand.symbolEmoji}}</span>
                      <div>
                        <b style="font-size: 0.95rem;" [style.color]="cand.isPrimary ? '#047857' : '#1e293b'">{{cand.name}}</b>
                        <span style="display: block; font-size: 0.78rem; color: #64748b;">{{cand.partyName}} (মার্কা: {{cand.symbolName}})</span>
                      </div>
                    </div>
                    <div style="width: 140px;">
                      <input type="number" min="0" [(ngModel)]="quickResultCandVotes[cand.candidateId]" [name]="'cand_votes_' + cand.candidateId"
                             style="text-align: right; font-weight: 800; font-size: 1.15rem; width: 100%; padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px;"
                             [style.color]="cand.isPrimary ? '#047857' : '#1e293b'"
                             placeholder="0" required />
                    </div>
                  </div>
                }
              </div>
            </div>

            <!-- Live Calculation Info Box -->
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; margin-top: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 0.92rem;">
              <div>
                <span style="color: #64748b; font-size: 0.82rem; display: block;">মোট কাস্টকৃত ভোট</span>
                <b style="font-size: 1.15rem; color: #1e293b;">{{calcModalTotalVotes() | number}}</b>
              </div>
              <div style="text-align: right;">
                <span style="color: #64748b; font-size: 0.82rem; display: block;">ডঃ ফারুকের লিড / ব্যবধান</span>
                <b [style.color]="calcModalLead() >= 0 ? '#15803d' : '#b91c1c'" style="font-size: 1.25rem; font-weight: 800;">
                  {{calcModalLead() >= 0 ? '+' : ''}}{{calcModalLead() | number}}
                </b>
              </div>
            </div>

            <div class="modal-actions" style="margin-top: 18px;">
              <button type="button" class="text-button" (click)="closeQuickResultModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingResult()">
                {{savingResult() ? 'সংরক্ষণ হচ্ছে…' : 'ফলাফল নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
@if(selectedCenterForForm8()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(880px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <h2>ফর্ম-৮ ফলাফল বিবরণী (ভোট গণনা বিবরণী)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ফর্ম-৮ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeForm8Modal()">✕</button>
            </div>
          </div>

          <!-- Official Form-8 Paper Layout -->
          <div class="official-form8-paper">
            <div class="form8-head">
              <div class="gov-seal">🇧🇩</div>
              <h2 class="form8-title">নির্বাচন কমিশন ফরম - ৮</h2>
              <p class="form8-rule">[বিধি ৩৯(১) ও ৪০ দ্রষ্টব্য]</p>
              <h3 class="form8-main-title">ভোট গণনা বিবরণী</h3>
            </div>

            <div class="form8-meta-grid">
              <div><b>নির্বাচনী এলাকার নম্বর ও নাম:</b> {{data()?.areaName || 'নির্বাচনী আসন'}}</div>
              <div><b>ভোটকেন্দ্রের নাম:</b> {{selectedCenterForForm8()!.centerName}} (কোড: {{selectedCenterForForm8()!.centerCode}})</div>
              <div><b>মোট প্রদত্ত ভোট:</b> {{(selectedCenterForForm8()!.totalCastVotes || (selectedCenterForForm8()!.candidateVotes + selectedCenterForForm8()!.runnerUpVotes)) | number}} জন</div>
              <div><b>গণনার বিবরণ:</b> ব্যালট গণনা সমাপ্ত ও ফর্ম-৮ প্রস্তুত</div>
            </div>

            <!-- Votes Tally Table -->
            <table class="form8-tally-table">
              <thead>
                <tr>
                  <th style="width: 50px;">ক্রমিক</th>
                  <th>প্রতিদ্বন্দ্বী প্রার্থীর নাম</th>
                  <th>বরাদ্দকৃত প্রতীক</th>
                  <th style="width: 140px; text-align: right;">প্রাপ্ত বৈধ ভোট</th>
                </tr>
              </thead>
              <tbody>
                @for(cand of getForm8CandidateList(); track cand.candidateId; let idx = $index){
                  <tr [class.highlight-row]="cand.candidateId === resultsSummary()?.candidateId">
                    <td>{{idx + 1}}</td>
                    <td>
                      <b>{{cand.name}}</b>
                      @if(cand.candidateId === resultsSummary()?.candidateId){
                        <span style="font-size: 0.75rem; color: #047857; margin-left: 6px; font-weight: 700;">(আমাদের প্রার্থী)</span>
                      }
                    </td>
                    <td><b>{{cand.symbolEmoji}} {{cand.symbolName}}</b></td>
                    <td style="text-align: right; font-size: 1.05rem; font-weight: 700;" [style.color]="cand.candidateId === resultsSummary()?.candidateId ? '#047857' : '#1e293b'">
                      {{cand.votes | number}}
                    </td>
                  </tr>
                }
                <tr class="total-row">
                  <td colspan="3" style="text-align: right;"><b>মোট প্রদত্ত বৈধ ভোট:</b></td>
                  <td style="text-align: right; font-weight: 800; font-size: 1.1rem;">
                    {{(selectedCenterForForm8()!.totalCastVotes || (selectedCenterForForm8()!.candidateVotes + selectedCenterForForm8()!.runnerUpVotes)) | number}}
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Margin Summary Box -->
            <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 8px; padding: 12px 18px; margin: 18px 0; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <b style="color: #065f46; font-size: 1rem;">অত্র কেন্দ্রে প্রার্থীর লিড মার্জিন:</b>
                <span style="font-size: 0.85rem; color: #047857; display: block;">{{selectedCenterForForm8()!.centerName}}</span>
              </div>
              <b style="font-size: 1.5rem; color: #047857;">
                {{(selectedCenterForForm8()!.candidateVotes - selectedCenterForForm8()!.runnerUpVotes) >= 0 ? '+' : ''}}{{selectedCenterForForm8()!.candidateVotes - selectedCenterForForm8()!.runnerUpVotes | number}} ভোট
              </b>
            </div>

            <!-- Signatures -->
            <div class="form8-sig-row">
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>পোলিং এজেন্টের স্বাক্ষর</b>
                <p>তারিখ ও সময়</p>
              </div>
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>সহকারী প্রিজাইডিং অফিসার</b>
                <p>সিলমোহর</p>
              </div>
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>প্রিজাইডিং অফিসারের পূর্ণ স্বাক্ষর</b>
                <p>ভোটকেন্দ্র সীলমোহর</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ================================================================= -->
    <!-- MODAL: CREATE TEAM USER (মাস্টার প্রার্থীর সাব-ইউজার তৈরি) -->
    <!-- ================================================================= -->
    @if(showCreateTeamUserModal()){
      <div class="modal-backdrop" (click)="closeCreateTeamUserModal()">
        <div class="modal-card" style="max-width: 520px;" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.4rem;">👤</span>
              <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b;">
                নতুন ক্যাম্পেইন কর্মী / সাব-ইউজার তৈরি করুন
              </h3>
            </div>
            <button class="close-btn" (click)="closeCreateTeamUserModal()">✕</button>
          </div>

          <form (ngSubmit)="submitCreateTeamUser()">
            <div class="modal-body" style="display: flex; flex-direction: column; gap: 14px; padding: 20px;">
              <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; font-size: 0.86rem; color: #166534;">
                ℹ️ <b>মাস্টার প্রার্থী স্কোপ:</b> এই ইউজারটি আপনার বর্তমান প্রার্থীর অধীনে তৈরি হবে। তিনি লগইন করে শুধুমাত্র আপনার ভোটার, কেন্দ্র ও ফলাফল এন্ট্রি করতে পারবেন।
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  কর্মীর পূর্ণ নাম <span style="color: #ef4444;">*</span>
                </label>
                <input type="text" [(ngModel)]="newTeamUser.displayName" name="displayName" required
                       placeholder="যেমন: মোঃ তারেক হাসান" class="form-input" style="width: 100%;" />
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  ব্যবহারকারী আইডি / Username <span style="color: #ef4444;">*</span> (ছোট হাতের ইংরেজি)
                </label>
                <input type="text" [(ngModel)]="newTeamUser.username" name="username" required
                       placeholder="যেমন: tarek_agent" class="form-input" style="width: 100%; font-family: monospace;" />
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  দায়িত্ব / রোল নির্বাচন <span style="color: #ef4444;">*</span>
                </label>
                <select [(ngModel)]="newTeamUser.role" name="role" required class="form-input" style="width: 100%;">
                  <option value="ক্যাম্পেইন সমন্বয়ক">ক্যাম্পেইন সমন্বয়ক (Campaign Coordinator)</option>
                  <option value="পোলিং এজেন্ট">পোলিং এজেন্ট (Polling Booth Agent)</option>
                  <option value="ডাটা এন্ট্রি অপারেটর">ডাটা এন্ট্রি অপারেটর (Data Entry Operator)</option>
                  <option value="ওয়ার্ড কো-অর্ডিনেটর">ওয়ার্ড কো-অর্ডিনেটর (Ward Coordinator)</option>
                  <option value="মাঠকর্মী">মাঠকর্মী (Field Volunteer)</option>
                </select>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div>
                  <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    মোবাইল নম্বর
                  </label>
                  <input type="text" [(ngModel)]="newTeamUser.phone" name="phone"
                         placeholder="017xxxxxxxx" class="form-input" style="width: 100%;" />
                </div>
                <div>
                  <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    ইমেইল (ঐচ্ছিক)
                  </label>
                  <input type="email" [(ngModel)]="newTeamUser.email" name="email"
                         placeholder="user@example.com" class="form-input" style="width: 100%;" />
                </div>
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  লগইন পাসওয়ার্ড <span style="color: #ef4444;">*</span> (নূন্যতম ৬ অক্ষর)
                </label>
                <input type="password" [(ngModel)]="newTeamUser.password" name="password" required minlength="6"
                       placeholder="গোপন পাসওয়ার্ড দিন" class="form-input" style="width: 100%;" />
              </div>
            </div>

            <div class="modal-footer" style="padding: 14px 20px; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; border-top: 1px solid #e2e8f0;">
              <button type="button" class="btn btn-secondary" (click)="closeCreateTeamUserModal()">বাতিল</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingTeamUser()">
                {{savingTeamUser() ? 'সংরক্ষণ হচ্ছে...' : '✓ তৈরি ও সক্রিয় করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ================================================================= -->
    <!-- MODAL: RESET TEAM USER PASSWORD -->
    <!-- ================================================================= -->
    @if(showResetPasswordModal()){
      <div class="modal-backdrop" (click)="closeResetPasswordModal()">
        <div class="modal-card" style="max-width: 440px;" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b;">
              🔑 পাসওয়ার্ড রিসেট করুন
            </h3>
            <button class="close-btn" (click)="closeResetPasswordModal()">✕</button>
          </div>

          <form (ngSubmit)="submitResetPassword()">
            <div class="modal-body" style="padding: 20px; display: flex; flex-direction: column; gap: 14px;">
              <p style="margin: 0; font-size: 0.9rem; color: #475569;">
                ব্যবহারকারী: <b>{{selectedUserForReset()?.displayName}}</b> ({{selectedUserForReset()?.username}})
              </p>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  নতুন পাসওয়ার্ড <span style="color: #ef4444;">*</span>
                </label>
                <input type="password" [(ngModel)]="resetNewPassword" name="resetNewPassword" required minlength="6"
                       placeholder="নতুন গোপন পাসওয়ার্ড লিখুন" class="form-input" style="width: 100%;" />
              </div>
            </div>

            <div class="modal-footer" style="padding: 14px 20px; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; border-top: 1px solid #e2e8f0;">
              <button type="button" class="btn btn-secondary" (click)="closeResetPasswordModal()">বাতিল</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingResetPassword() || !resetNewPassword">
                {{savingResetPassword() ? 'সংরক্ষণ হচ্ছে...' : 'পাসওয়ার্ড পরিবর্তন করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
'''
