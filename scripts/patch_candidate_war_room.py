import re

FILE_PATH = r'G:\dotnetproject\EEMS_Complete_PDF_Package\frontend\src\app\features\candidates\candidate-war-room.page.ts'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modals HTML to insert before closing template backtick
modals_html = """
    <!-- ===================================================================== -->
    <!-- MODAL 1: SMART DIGITAL VOTER SLIP CARD WITH QR CODE -->
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
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">জাতীয় পরিচয়পত্র (NID):</span>
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
                <span style="display: inline-block; background: #047857; color: #fff; font-size: 0.7rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; margin-bottom: 4px;">ভোটকেন্দ্র ও বুথ</span>
                <h4 style="margin: 0; font-size: 1rem; color: #047857; font-weight: 800;">{{selectedVoterForSlip()!.centerName}}</h4>
                <p style="margin: 4px 0 0; font-size: 0.85rem; color: #475569; font-weight: 600;">
                  🚪 {{selectedVoterForSlip()!.boothName || 'সাধারণ বুথ'}} (কেন্দ্র কোড: {{selectedVoterForSlip()!.centerCode}})
                </p>
                @if(selectedVoterForSlip()!.areaName){
                  <p style="margin: 2px 0 0; font-size: 0.8rem; color: #64748b;">গ্রাম/মহল্লা: {{selectedVoterForSlip()!.areaName}}</p>
                }
              </div>

              <!-- Dynamic QR Code -->
              <div style="text-align: center;">
                @if(voterQrCodeDataUrl()){
                  <img [src]="voterQrCodeDataUrl()" alt="Voter QR" style="width: 100px; height: 100px; border-radius: 8px; border: 1px solid #cbd5e1; display: block;" />
                } @else {
                  <div style="width: 100px; height: 100px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 0.7rem;">QR Loading...</div>
                }
                <span style="font-size: 0.65rem; color: #64748b; font-weight: 700; display: block; margin-top: 2px;">বুথ ভেরিফিকেশন QR</span>
              </div>
            </div>

            <div style="text-align: center; margin-top: 12px; font-size: 0.8rem; color: #a7f3d0; font-style: italic;">
              "আপনার মূল্যবান ভোট দিয়ে সৎ ও যোগ্য প্রার্থী নির্বাচিত করুন।"
            </div>
          </div>

          <div style="display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap;">
            <button class="primary-button" (click)="sendSingleVoterWhatsApp(selectedVoterForSlip()!)" style="background: #25d366; border: none; font-weight: 700;">
              💬 হোয়াটসঅ্যাপে পাঠান (WA)
            </button>
            <button class="outline-sm-btn" (click)="triggerBrowserPrint()">
              🖨️ প্রিন্ট করুন
            </button>
            <button class="secondary-button" (click)="closeSmartSlip()">
              ✕ বন্ধ করুন
            </button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 2: VOTER BULK BROADCAST HUB & WHATSAPP QUEUE DISPATCHER -->
    <!-- ===================================================================== -->
    @if(showVoterBroadcastModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(760px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <div>
              <h2>📱 ভোটার বাল্ক এসএমএস ও হোয়াটসঅ্যাপ ব্রডকাস্ট হাব</h2>
              <p class="subtitle">প্রার্থীর মার্কা ও স্লিপের তথ্যসহ সকল ভোটারের নিকট এক ক্লিকে বার্তা প্রেরণ</p>
            </div>
            <button class="close-btn" (click)="closeVoterBroadcastModal()">✕</button>
          </div>

          <!-- Channel Selection Tabs -->
          <div style="display: flex; gap: 12px; margin-bottom: 16px;">
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'WHATSAPP'" (click)="voterBroadcastChannel.set('WHATSAPP')" style="flex: 1; text-align: center; font-weight: 700;">
              💬 হোয়াটসঅ্যাপ ব্রডকাস্ট (সম্পূর্ণ ফ্রি - ৳ ০.০০)
            </button>
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'SMS'" (click)="voterBroadcastChannel.set('SMS')" style="flex: 1; text-align: center; font-weight: 700;">
              📱 মোবাইল এসএমএস (টেলিকম গেটওয়ে)
            </button>
          </div>

          <!-- Target Filter & Template -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
            <div class="form-group">
              <label>কাদের কাছে পাঠাবেন (টার্গেট গ্রুপ):</label>
              <select [(ngModel)]="voterBroadcastTarget" (change)="onVoterBroadcastTargetChange()">
                <option value="ALL">সকল ভোটার ({{voters().length}} জন)</option>
                <option value="UNISSUED_SLIP">যাদের স্লিপ এখনও দেওয়া হয়নি ({{unissuedSlipsCount()}} জন)</option>
                <option value="SUPPORTER">শুধুমাত্র বিশ্বস্ত সমর্থক (SUPPORTER)</option>
                <option value="CENTER">নির্দিষ্ট ভোটকেন্দ্রের ভোটার</option>
              </select>
            </div>

            <div class="form-group">
              <label>মেসেজ টেমপ্লেট:</label>
              <select [(ngModel)]="voterBroadcastTemplate" (change)="applyVoterTemplate(voterBroadcastTemplate())">
                <option value="SLIP_NOTICE">🎫 ভোটকেন্দ্র ও স্লিপ নোটিশ</option>
                <option value="ELECTION_DAY_CALL">🗳️ ভোটের দিন ভোরের ভোট প্রার্থনা</option>
                <option value="CUSTOM">✏️ কাস্টম প্রার্থীর বার্তা</option>
              </select>
            </div>
          </div>

          @if(voterBroadcastTarget() === 'CENTER'){
            <div class="form-group" style="margin-bottom: 14px;">
              <label>টার্গেট ভোটকেন্দ্র নির্বাচন করুন:</label>
              <select [(ngModel)]="voterBroadcastCenterId">
                <option value="">সকল কেন্দ্র</option>
                @for(c of centersList(); track c.centerId){
                  <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                }
              </select>
            </div>
          }

          <!-- Tag Chips Toolbar -->
          <div style="margin-bottom: 8px;">
            <label style="display: block; font-size: 0.8rem; font-weight: 700; color: #475569; margin-bottom: 6px;">ডাইনামিক ট্যাগ ইনসার্ট করুন (ক্লিকে স্বয়ংক্রিয় বসবে):</label>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{নাম}')">+ ভোটারের নাম</button>
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{ভোটকেন্দ্র}')">+ ভোটকেন্দ্র</button>
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{বুথ}')">+ বুথ নং</button>
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{ক্রমিক}')">+ ক্রমিক নম্বর</button>
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{ভোটার নং}')">+ ভোটার আইডি</button>
              <button type="button" class="tag-chip-btn" (click)="insertVoterTag('{মার্কা}')">+ প্রতীক</button>
            </div>
          </div>

          <!-- Message Textarea -->
          <div class="form-group" style="margin-bottom: 14px;">
            <label>বার্তার বিষয়বস্তু:</label>
            <textarea [(ngModel)]="voterBroadcastCustomMessage" rows="4" style="width: 100%; border-radius: 8px; border: 1px solid #cbd5e1; padding: 10px; font-family: inherit; font-size: 0.95rem;"></textarea>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-top: 4px;">
              <span>অক্ষর সংখ্যা: {{voterBroadcastCustomMessage().length}} (বাংলা ইউনিকোড)</span>
              @if(voterBroadcastChannel() === 'SMS'){
                <span style="color: #b45309; font-weight: 700;">আনুমানিক খরচ: ০.৩০ টাকা x {{targetVotersCount()}} জন = ৳ {{(targetVotersCount() * 0.30) | number:'1.2-2'}}</span>
              } @else {
                <span style="color: #047857; font-weight: 700;">হোয়াটসঅ্যাপ খরচ: ৳ ০.০০ (সম্পূর্ণ ফ্রি)</span>
              }
            </div>
          </div>

          <!-- Queue Dispatcher View (If WhatsApp Queue Loaded) -->
          @if(voterBroadcastQueue().length > 0){
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #047857; font-size: 1rem; font-weight: 800;">
                  🚀 হোয়াটসঅ্যাপ ডিসপ্যাচ কিউ ({{dispatchCurrentIndex()}} / {{voterBroadcastQueue().length}} প্রেরিত)
                </h4>
                <span style="font-size: 0.85rem; font-weight: 700; color: #0284c7;">
                  অবশিষ্ট: {{voterBroadcastQueue().length - dispatchCurrentIndex()}} জন
                </span>
              </div>

              <!-- Progress Bar -->
              <div style="height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 14px;">
                <div [style.width.%]="(dispatchCurrentIndex() / voterBroadcastQueue().length) * 100" style="height: 100%; background: #25d366; transition: width 0.3s ease;"></div>
              </div>

              @if(dispatchCurrentIndex() < voterBroadcastQueue().length){
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">পরবর্তী প্রাপক:</span>
                    <b style="display: block; font-size: 1rem; color: #0f172a;">{{voterBroadcastQueue()[dispatchCurrentIndex()].fullName}} ({{voterBroadcastQueue()[dispatchCurrentIndex()].phone}})</b>
                    <span style="font-size: 0.8rem; color: #475569;">কেন্দ্র: {{voterBroadcastQueue()[dispatchCurrentIndex()].centerName}} · বুথ: {{voterBroadcastQueue()[dispatchCurrentIndex()].boothName}} · ক্রমিক: {{voterBroadcastQueue()[dispatchCurrentIndex()].serialNumber}}</span>
                  </div>
                  <div>
                    <button class="primary-button-sm" (click)="dispatchNextInQueue()" style="background: #25d366; color: #fff; font-weight: 700; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer;">
                      👉 এই ভোটারের হোয়াটসঅ্যাপ ওপেন করুন
                    </button>
                  </div>
                </div>
              } @else {
                <div style="background: #ecfdf5; border: 1px solid #6ee7b7; color: #065f46; border-radius: 10px; padding: 12px; text-align: center; font-weight: 700;">
                  🎉 অভিনন্দন! কিউ-এর সকল ভোটারের নিকট হোয়াটসঅ্যাপ মেসেজ প্রেরণ সম্পন্ন হয়েছে।
                </div>
              }

              <div style="display: flex; gap: 10px; justify-content: flex-end; align-items: center;">
                @if(!isAutoDispatching() && dispatchCurrentIndex() < voterBroadcastQueue().length){
                  <button class="outline-sm-btn" (click)="startAutoDispatch()" style="border-color: #059669; color: #047857; font-weight: 700;">
                    ▶️ অটো ডিসপ্যাচ চালু করুন (২.৫ সে. বিরতি)
                  </button>
                } @else if(isAutoDispatching()){
                  <button class="outline-sm-btn" (click)="stopAutoDispatch()" style="border-color: #dc2626; color: #dc2626; font-weight: 700;">
                    ⏹️ অটো ডিসপ্যাচ থামান
                  </button>
                }
              </div>
            </div>
          }

          <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <button class="primary-button" (click)="submitVoterBroadcast()" [disabled]="sendingVoterBroadcast()" [style.background]="voterBroadcastChannel() === 'WHATSAPP' ? '#25d366' : '#0284c7'" style="border: none; font-weight: 700;">
              {{sendingVoterBroadcast() ? 'প্রক্রিয়াকরণ হচ্ছে...' : (voterBroadcastChannel() === 'WHATSAPP' ? '💬 হোয়াটসঅ্যাপ কিউ প্রস্তুত করুন' : '📱 বাল্ক এসএমএস পাঠান')}}
            </button>
            <button class="secondary-button" (click)="closeVoterBroadcastModal()">
              ✕ বন্ধ করুন
            </button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 3: SMS GATEWAY CONFIGURATION & TEST CONSOLE -->
    <!-- ===================================================================== -->
    @if(showSmsConfigModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(640px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <div>
              <h2>⚙️ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন</h2>
              <p class="subtitle">বাংলাদেশি বাল্ক এসএমএস এপিআই (Greenweb, SSL Wireless বা টেস্ট সিমুলেটর)</p>
            </div>
            <button class="close-btn" (click)="closeSmsConfigModal()">✕</button>
          </div>

          <!-- Current Balance Highlight Banner -->
          <div style="background: linear-gradient(135deg, #1e293b, #0f172a); color: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <span style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">গেটওয়ে বর্তমান ব্যালেন্স</span>
              <h3 style="margin: 2px 0 0; font-size: 1.5rem; color: #fef08a;">৳ {{smsConfig()?.balance || 2500.00 | number:'1.2-2'}}</h3>
            </div>
            <span style="background: #065f46; color: #34d399; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 6px;">
              ✓ সক্রিয় (ACTIVE)
            </span>
          </div>

          <div class="form-group" style="margin-bottom: 12px;">
            <label>এসএমএস প্রোভাইডার নির্বাচন করুন:</label>
            <select [(ngModel)]="smsConfigProvider">
              <option value="SIMULATOR">🧪 বিল্ট-ইন লোকাল সিমুলেটর (টেস্টিং মোড - ৳ ০ খরচ)</option>
              <option value="GREENWEB">🌐 গ্রীনওয়েব বাংলাদেশ (Greenweb API)</option>
              <option value="SSL_WIRELESS">🔒 এসএসএল ওয়্যারলেস (SSL Wireless SMS Plus)</option>
            </select>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label>API Key / Token:</label>
              <input [(ngModel)]="smsConfigApiKey" placeholder="আপনার SMS এপিআই কী লিখুন..." style="width: 100%; border-radius: 6px; border: 1px solid #cbd5e1; padding: 8px;">
            </div>
            <div class="form-group">
              <label>Sender ID / Masking Name:</label>
              <input [(ngModel)]="smsConfigSenderId" placeholder="যেমন: SCALE_FARUK" style="width: 100%; border-radius: 6px; border: 1px solid #cbd5e1; padding: 8px;">
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label>API Endpoint URL:</label>
            <input [(ngModel)]="smsConfigEndpoint" placeholder="http://api.greenweb.com.bd/api.php" style="width: 100%; border-radius: 6px; border: 1px solid #cbd5e1; padding: 8px;">
          </div>

          <!-- Test SMS Box -->
          <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 14px; margin-bottom: 16px;">
            <h4 style="margin: 0 0 10px; font-size: 0.9rem; color: #1e293b;">📲 টেস্ট এসএমএস যাচাই করুন:</h4>
            <div style="display: flex; gap: 8px;">
              <input [(ngModel)]="smsTestPhone" placeholder="মোবাইল নম্বর (যেমন: 017XXXXXXXX)" style="flex: 1; border-radius: 6px; border: 1px solid #cbd5e1; padding: 8px;">
              <button class="primary-button-sm" (click)="sendTestSms()" [disabled]="testingSms()" style="white-space: nowrap;">
                {{testingSms() ? 'পাঠানো হচ্ছে...' : 'টেস্ট পাঠান'}}
              </button>
            </div>
            @if(smsTestResult()){
              <p style="margin: 8px 0 0; font-size: 0.85rem; color: #047857; font-weight: 600;">{{smsTestResult()}}</p>
            }
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <button class="primary-button" (click)="saveSmsConfig()" [disabled]="savingSmsConfig()">
              {{savingSmsConfig() ? 'সংরক্ষণ হচ্ছে...' : 'সেটিংস সংরক্ষণ করুন'}}
            </button>
            <button class="secondary-button" (click)="closeSmsConfigModal()">
              ✕ বন্ধ করুন
            </button>
          </div>
        </div>
      </div>
    }
"""

template_target = "    }\n\n\n  `,\n  styles: [`"
if template_target in content:
    content = content.replace(template_target, "    }\n" + modals_html + "\n  `,\n  styles: [`")
    print("Modals HTML successfully injected.")
else:
    print("Warning: template_target not found.")

# 2. Add styles for tag-chip-btn
styles_target = ".back { display: inline-block; margin-bottom: 18px; color: var(--teal); font-weight: 700; text-decoration: none; }"
styles_add = """.tag-chip-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
    .tag-chip-btn:hover { background: #e2e8f0; border-color: #94a3b8; }
    .wa-pill-btn:hover { opacity: 0.9; }
    .slip-pill-btn:hover { opacity: 0.9; }
    """
if styles_target in content:
    content = content.replace(styles_target, styles_add + styles_target)
    print("Styles successfully injected.")

# 3. Add Methods and Signals in TypeScript class
ts_methods = """
  // =========================================================================
  // 12. SMART DIGITAL VOTER SLIP & BULK BROADCAST HUB (বিকল্প ২ ও ৩ বর্ধিতকরণ)
  // =========================================================================

  readonly selectedVoterForSlip = signal<CandidateVoterSummary | null>(null);
  readonly voterQrCodeDataUrl = signal<string>('');

  readonly showVoterBroadcastModal = signal<boolean>(false);
  readonly voterBroadcastChannel = signal<'WHATSAPP' | 'SMS'>('WHATSAPP');
  readonly voterBroadcastTarget = signal<string>('ALL');
  readonly voterBroadcastCenterId = signal<string>('');
  readonly voterBroadcastTemplate = signal<string>('SLIP_NOTICE');
  readonly voterBroadcastCustomMessage = signal<string>('আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, ভোটার তালিকা ক্রমিক: {ক্রমিক}। {মার্কা} মার্কায় আপনার মূল্যবান ভোট দিন।');

  readonly voterBroadcastQueue = signal<VoterQueueItem[]>([]);
  readonly dispatchCurrentIndex = signal<number>(0);
  readonly isAutoDispatching = signal<boolean>(false);
  private autoDispatchTimer: any = null;

  readonly showSmsConfigModal = signal<boolean>(false);
  readonly smsConfig = signal<SmsGatewayConfigDto | null>(null);
  readonly smsConfigProvider = signal<string>('SIMULATOR');
  readonly smsConfigApiKey = signal<string>('');
  readonly smsConfigSenderId = signal<string>('SCALE_FARUK');
  readonly smsConfigEndpoint = signal<string>('http://api.greenweb.com.bd/api.php');
  readonly smsTestPhone = signal<string>('01717208118');
  readonly smsTestResult = signal<string>('');

  readonly sendingVoterBroadcast = signal<boolean>(false);
  readonly testingSms = signal<boolean>(false);
  readonly savingSmsConfig = signal<boolean>(false);

  readonly unissuedSlipsCount = computed(() => this.voters().filter(v => !v.slipIssued).length);

  readonly targetVotersCount = computed(() => {
    const list = this.voters();
    const t = this.voterBroadcastTarget();
    if (t === 'UNISSUED_SLIP') return list.filter(v => !v.slipIssued).length;
    if (t === 'SUPPORTER') return list.filter(v => v.category === 'SUPPORTER').length;
    if (t === 'CENTER' && this.voterBroadcastCenterId()) return list.filter(v => v.centerId === this.voterBroadcastCenterId()).length;
    return list.length;
  });

  openSmartSlip(voter: CandidateVoterSummary) {
    this.selectedVoterForSlip.set(voter);
    this.voterQrCodeDataUrl.set('');
    const qrPayload = `EEMS:VTR:${voter.id}:${voter.voterNumber}:${voter.centerCode || 'CEN'}:${voter.serialNumber}`;
    QRCode.toDataURL(qrPayload, { width: 140, margin: 1 })
      .then(url => this.voterQrCodeDataUrl.set(url))
      .catch(err => console.error('QR code generation error:', err));
  }

  closeSmartSlip() {
    this.selectedVoterForSlip.set(null);
    this.voterQrCodeDataUrl.set('');
  }

  sendSingleVoterWhatsApp(v: CandidateVoterSummary) {
    const cand = this.data()?.candidate;
    const candName = cand?.name || 'প্রার্থী';
    const candSymbol = cand?.symbolNameBn || cand?.symbolNameEn || 'মার্কা';
    const msg = `আসসালামু আলাইকুম ${v.fullName}। ${candName} (${candSymbol} মার্কা) এর পক্ষ থেকে নির্বাচনী শুভেচ্ছা।\\n\\n📌 আপনার ভোটকেন্দ্র: ${v.centerName}\\n🚪 নির্ধারিত বুথ: ${v.boothName || 'সাধারণ বুথ'}\\n🔢 ভোটার তালিকা ক্রমিক নম্বর: ${v.serialNumber}\\n🆔 ভোটার নং: ${v.voterNumber}\\n\\nআপনার মূল্যবান ভোট দিয়ে এলাকার উন্নয়নে অংশ নিন।`;
    
    let cleanPhone = (v.phone || '').replace(/\\D/g, '');
    if (cleanPhone.startsWith('880')) cleanPhone = cleanPhone.substring(2);
    
    const waUrl = `https://wa.me/88${cleanPhone}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');

    if (!v.slipIssued) {
      this.toggleSlip(v);
    }
  }

  openVoterBroadcastModal() {
    this.loadVoters();
    this.showVoterBroadcastModal.set(true);
    this.voterBroadcastQueue.set([]);
    this.dispatchCurrentIndex.set(0);
    this.isAutoDispatching.set(false);
  }

  closeVoterBroadcastModal() {
    this.stopAutoDispatch();
    this.showVoterBroadcastModal.set(false);
  }

  onVoterBroadcastTargetChange() {
    // Re-evaluate target count reactively
  }

  applyVoterTemplate(type: string) {
    if (type === 'SLIP_NOTICE') {
      this.voterBroadcastCustomMessage.set('আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, ভোটার তালিকা ক্রমিক: {ক্রমিক}। {মার্কা} মার্কায় আপনার মূল্যবান ভোট দিন।');
    } else if (type === 'ELECTION_DAY_CALL') {
      this.voterBroadcastCustomMessage.set('শ্রদ্ধেয় {নাম}, আজ নির্বাচনের দিন। সকাল সকাল আপনার নির্ধারিত কেন্দ্র {ভোটকেন্দ্র}-এ (বুথ: {বুথ}, ক্রমিক: {ক্রমিক}) গিয়ে {মার্কা} মার্কায় ভোট দিন।');
    }
  }

  insertVoterTag(tag: string) {
    this.voterBroadcastCustomMessage.update(msg => msg + ' ' + tag);
  }

  submitVoterBroadcast() {
    this.sendingVoterBroadcast.set(true);
    const req: SendVoterBroadcastRequest = {
      channel: this.voterBroadcastChannel(),
      targetFilter: this.voterBroadcastTarget(),
      targetCenterId: this.voterBroadcastCenterId() || null,
      templateType: this.voterBroadcastTemplate(),
      messageContent: this.voterBroadcastCustomMessage()
    };

    this.api.sendVoterBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingVoterBroadcast.set(false);
        if (res.channel === 'SMS') {
          alert(`✅ ${res.message}`);
          this.loadVoters();
          this.closeVoterBroadcastModal();
        } else if (res.channel === 'WHATSAPP' && res.queue && res.queue.length > 0) {
          this.voterBroadcastQueue.set(res.queue);
          this.dispatchCurrentIndex.set(0);
          this.loadVoters();
        }
      },
      error: err => {
        this.sendingVoterBroadcast.set(false);
        alert(err?.error?.message || 'ব্রডকাস্ট প্রেরণে সমস্যা হয়েছে।');
      }
    });
  }

  dispatchNextInQueue() {
    const queue = this.voterBroadcastQueue();
    const idx = this.dispatchCurrentIndex();
    if (idx < queue.length) {
      const item = queue[idx];
      window.open(item.waUrl, '_blank');
      // Mark as slip issued in local array
      this.voters.update(list => list.map(v => v.id === item.voterId ? { ...v, slipIssued: true } : v));
      this.dispatchCurrentIndex.update(i => i + 1);
    }
  }

  startAutoDispatch() {
    if (this.dispatchCurrentIndex() >= this.voterBroadcastQueue().length) return;
    this.isAutoDispatching.set(true);
    this.dispatchNextInQueue();
    this.autoDispatchTimer = setInterval(() => {
      if (this.dispatchCurrentIndex() >= this.voterBroadcastQueue().length) {
        this.stopAutoDispatch();
      } else {
        this.dispatchNextInQueue();
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

  openSmsConfigModal() {
    this.showSmsConfigModal.set(true);
    this.smsTestResult.set('');
    this.api.getSmsGatewayConfig(this.electionId).subscribe({
      next: cfg => {
        this.smsConfig.set(cfg);
        this.smsConfigProvider.set(cfg.provider);
        this.smsConfigApiKey.set(cfg.apiKey);
        this.smsConfigSenderId.set(cfg.senderId);
        this.smsConfigEndpoint.set(cfg.endpointUrl || 'http://api.greenweb.com.bd/api.php');
      }
    });
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
      error: () => this.savingSmsConfig.set(false)
    });
  }

  sendTestSms() {
    if (!this.smsTestPhone()) return;
    this.testingSms.set(true);
    this.smsTestResult.set('');
    this.api.testSmsGateway(this.electionId, { phone: this.smsTestPhone(), message: 'EEMS টেস্ট এসএমএস।' }).subscribe({
      next: res => {
        this.testingSms.set(false);
        this.smsTestResult.set(res.message);
      },
      error: () => {
        this.testingSms.set(false);
        this.smsTestResult.set('টেস্ট এসএমএস পাঠাতে ব্যর্থ হয়েছে।');
      }
    });
  }
"""

class_end_pattern = r"(\s+deleteCampaignEvent\(ev: CandidateCampaignEventItem\) \{[\s\S]+?\}\s+\}\s+)(\n\})"
match = re.search(class_end_pattern, content)
if match:
    content = content[:match.start(2)] + ts_methods + content[match.start(2):]
    print("TypeScript methods successfully injected.")
else:
    print("Warning: class end pattern not found.")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
