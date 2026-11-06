file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports for Broadcast
old_import = "  CandidateBroadcastLogItem, SendCandidateBroadcastRequest, SendCandidateBroadcastResponse"
if "CandidateBroadcastLogItem" not in content:
    target_import = "  CandidateBoothAgentSummary,"
    replacement_import = "  CandidateBoothAgentSummary,\n  CandidateBroadcastLogItem,\n  SendCandidateBroadcastRequest,\n  SendCandidateBroadcastResponse,"
    if target_import in content:
        content = content.replace(target_import, replacement_import, 1)
        print("Broadcast models imported.")
    else:
        print("ERROR: could not find target_import")

# 2. Add Toolbar Button in Agent Tab
target_agent_toolbar = """                <button class="outline-sm-btn" (click)="openBatchIdCardsModal()" style="font-weight: 700; border-color: #082136; color: #082136; background: #f0f7ff;">
                  🪪 ব্যাচ আইডি কার্ড প্রিন্ট
                </button>"""

replacement_agent_toolbar = """                <button class="outline-sm-btn broadcast-trigger-btn" (click)="openBroadcastModal()" style="font-weight: 700; border-color: #059669; color: #065f46; background: #ecfdf5;">
                  📢 বাল্ক এসএমএস ও হোয়াটসঅ্যাপ
                </button>
                <button class="outline-sm-btn" (click)="openBatchIdCardsModal()" style="font-weight: 700; border-color: #082136; color: #082136; background: #f0f7ff;">
                  🪪 ব্যাচ আইডি কার্ড প্রিন্ট
                </button>"""

if target_agent_toolbar in content:
    content = content.replace(target_agent_toolbar, replacement_agent_toolbar, 1)
    print("Broadcast trigger button added to agent toolbar.")
else:
    print("ERROR: could not find target_agent_toolbar")

# 3. Add direct WhatsApp button in Booth Agent table row
target_phone_row = """                          <a class="phone-link" href="tel:{{ag.phone}}">📞 {{ag.phone}}</a>"""
replacement_phone_row = """                          <div class="agent-contact-group">
                            <a class="phone-link" href="tel:{{ag.phone}}">📞 {{ag.phone}}</a>
                            <a class="wa-mini-btn" [href]="getWhatsAppAgentUrl(ag.phone, ag.fullName)" target="_blank" title="হোয়াটসঅ্যাপে সরাসরি চ্যাট করুন">
                              💬 WA
                            </a>
                          </div>"""

if target_phone_row in content:
    content = content.replace(target_phone_row, replacement_phone_row, 1)
    print("WhatsApp direct button added to agent table.")
else:
    print("ERROR: could not find target_phone_row")

# 4. Add State & Signals in class
target_signals = "  readonly showBatchIdCardsModal = signal(false);"
replacement_signals = """  readonly showBatchIdCardsModal = signal(false);
  readonly showBroadcastModal = signal(false);
  readonly broadcastLogs = signal<CandidateBroadcastLogItem[]>([]);
  readonly loadingBroadcasts = signal(false);
  readonly sendingBroadcast = signal(false);

  broadcastChannel: 'SMS' | 'WHATSAPP' = 'SMS';
  broadcastTargetCenter = '';
  broadcastTargetAgentType = 'ALL';
  broadcastTemplateType = 'MORNING_CHECKIN';
  broadcastMessage = '';

  readonly targetAgentsCount = computed(() => {
    let list = this.boothAgents();
    if (this.broadcastTargetCenter) {
      list = list.filter(a => a.centerId === this.broadcastTargetCenter);
    }
    if (this.broadcastTargetAgentType && this.broadcastTargetAgentType !== 'ALL') {
      list = list.filter(a => a.agentType === this.broadcastTargetAgentType);
    }
    return list.length;
  });"""

if target_signals in content:
    content = content.replace(target_signals, replacement_signals, 1)
    print("Broadcast signals added.")
else:
    print("ERROR: could not find target_signals")

# 5. Add Methods in class
target_methods = "  openBatchIdCardsModal() {"
replacement_methods = """  openBroadcastModal() {
    this.showBroadcastModal.set(true);
    this.selectBroadcastTemplate('MORNING_CHECKIN');
    this.loadBroadcastLogs();
  }

  closeBroadcastModal() {
    this.showBroadcastModal.set(false);
  }

  loadBroadcastLogs() {
    this.loadingBroadcasts.set(true);
    this.api.getBroadcastLogs(this.electionId).subscribe({
      next: logs => {
        this.broadcastLogs.set(logs);
        this.loadingBroadcasts.set(false);
      },
      error: () => this.loadingBroadcasts.set(false)
    });
  }

  selectBroadcastTemplate(type: string) {
    this.broadcastTemplateType = type;
    const cand = this.data()?.candidate;
    const candName = cand?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক';
    const sym = (cand?.symbolEmoji || '⚖️') + ' ' + (cand?.symbolNameBn || 'দাঁড়িপাল্লা');

    switch (type) {
      case 'MORNING_CHECKIN':
        this.broadcastMessage = `জরুরি নির্দেশ: প্রিয় পোলিং এজেন্ট, সকাল ৭:৩০ এর মধ্যে স্ব স্ব কেন্দ্রের বুথে প্রবেশ করুন। প্রিজাইডিং অফিসারের সম্মুখে খালি ব্যালট বাক্স পরীক্ষা করে সিল নিশ্চিত করুন। কোনো বাধা পেলে অবিলম্বে ওয়ার রুমে জানান। - ${candName} (${sym})`;
        break;
      case 'TURNOUT_REPORT':
        this.broadcastMessage = `টার্নআউট রিপোর্ট: প্রিয় এজেন্ট, দুপুর ১২:০০ টা পর্যন্ত আপনার বুথে মোট কাস্ট হওয়া ভোট ও আনুমানিক উপস্থিতি কত তা দ্রুত ওয়ার রুমে জানান। সতর্ক থাকুন। - ${candName} (${sym})`;
        break;
      case 'FORM8_REMINDER':
        this.broadcastMessage = `চূড়ান্ত নির্দেশ: ভোট গণনা শেষ না হওয়া পর্যন্ত কোনো অবস্থাতেই ভোটকক্ষ ত্যাগ করবেন না। প্রিজাইডিং অফিসারের সই করা ফরম-৮ এর কার্বন কপি সংগ্রহ করে অবিলম্বে ছবি তুলে ওয়ার রুমে পাঠান। - ${candName} (${sym})`;
        break;
      case 'SOS_ALERT':
        this.broadcastMessage = `জরুরি নিরাপত্তা নির্দেশ: ভোটকেন্দ্রে কোনো হুমকি বা বিশৃঙ্খলা হলে সাথে সাথে ওয়ার রুম ও দায়িত্বরত এক্সিকিউটিভ ম্যাজিস্ট্রেটকে জানান। আমরা স্ট্রাইকিং ফোর্স পাঠাচ্ছি। - ${candName} (${sym})`;
        break;
      default:
        this.broadcastMessage = `জরুরি নির্বাচনী বিজ্ঞপ্তি: - ${candName} (${sym})`;
        break;
    }
  }

  submitBroadcast() {
    if (!this.broadcastMessage.trim()) {
      alert('অনুগ্রহ করে মেসেজের বিবরণ লিখুন।');
      return;
    }

    this.sendingBroadcast.set(true);
    const req: SendCandidateBroadcastRequest = {
      channel: this.broadcastChannel,
      recipientGroup: 'POLLING_AGENTS',
      targetCenterId: this.broadcastTargetCenter || null,
      targetAgentType: this.broadcastTargetAgentType,
      templateType: this.broadcastTemplateType,
      messageContent: this.broadcastMessage.trim()
    };

    this.api.sendBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingBroadcast.set(false);
        alert(`সাফল্য: ${res.message}`);
        this.loadBroadcastLogs();
        if (this.broadcastChannel === 'WHATSAPP') {
          const firstAgent = this.boothAgents()[0];
          if (firstAgent && firstAgent.phone) {
            const url = this.getWhatsAppAgentUrl(firstAgent.phone, firstAgent.fullName, this.broadcastMessage);
            window.open(url, '_blank');
          }
        }
      },
      error: err => {
        this.sendingBroadcast.set(false);
        const msg = err?.error?.message || err?.message || 'ব্রডকাস্ট প্রেরণ ব্যর্থ হয়েছে।';
        alert(`ত্রুটি: ${msg}`);
      }
    });
  }

  getWhatsAppAgentUrl(phone?: string, agentName?: string, customMsg?: string): string {
    if (!phone) return 'https://wa.me/';
    let clean = phone.replace(/[^0-9]/g, '');
    if (clean.startsWith('0')) clean = '88' + clean;
    if (!clean.startsWith('88')) clean = '880' + clean;
    const msg = customMsg || `আসসালামু আলাইকুম ${agentName || 'পোলিং এজেন্ট'}, নির্বাচনী কমান্ড সেন্টার থেকে যোগাযোগ করা হচ্ছে। কেন্দ্রের সর্বশেষ পরিস্থিতি আপডেট জানান।`;
    return `https://wa.me/${clean}?text=${encodeURIComponent(msg)}`;
  }

  openBatchIdCardsModal() {"""

if target_methods in content:
    content = content.replace(target_methods, replacement_methods, 1)
    print("Broadcast methods added.")
else:
    print("ERROR: could not find target_methods")

# 6. Add Broadcast Modal Template before showBatchIdCardsModal
target_batch_modal_anchor = "    @if(showBatchIdCardsModal()){"
broadcast_modal_template = """    <!-- ===================================================================== -->
    <!-- MODAL: POLLING AGENT SMS & WHATSAPP BROADCAST GATEWAY -->
    <!-- ===================================================================== -->
    @if(showBroadcastModal()){
      <div class="modal-backdrop print-modal-backdrop">
        <div class="card modal-card broadcast-modal-card">
          <!-- Modal Header -->
          <div class="modal-header broadcast-modal-header no-print">
            <div class="broadcast-titles">
              <h2>📢 পোলিং এজেন্টদের বাল্ক এসএমএস ও হোয়াটসঅ্যাপ ব্রডকাস্ট</h2>
              <p class="subtitle">ভোটের দিন সকালের রিপোর্টিং, দুপুরের উপস্থিতি এবং গণনা শেষে ফরম-৮ প্রেরণের জরুরি বার্তা গেটওয়ে</p>
            </div>
            <button class="close-btn" (click)="closeBroadcastModal()">✕</button>
          </div>

          <div class="broadcast-workspace-body no-print">
            <!-- Channel Selector Strip -->
            <div class="channel-selector-row">
              <span class="sel-label">ডেলিভারি চ্যানেল নির্বাচন:</span>
              <div class="channel-options">
                <label class="channel-pill" [class.active]="broadcastChannel === 'SMS'">
                  <input type="radio" [(ngModel)]="broadcastChannel" value="SMS" />
                  📱 মোবাইল বাল্ক এসএমএস (SMS Gateway)
                </label>
                <label class="channel-pill" [class.active]="broadcastChannel === 'WHATSAPP'">
                  <input type="radio" [(ngModel)]="broadcastChannel" value="WHATSAPP" />
                  💬 হোয়াটসঅ্যাপ ব্রডকাস্ট (WhatsApp Web / Chat)
                </label>
              </div>
            </div>

            <!-- Target Recipient Filters Strip -->
            <div class="broadcast-filter-strip">
              <div class="bf-group">
                <label>ভোটকেন্দ্র ফিল্টার:</label>
                <select [(ngModel)]="broadcastTargetCenter">
                  <option value="">সকল ভোটকেন্দ্র (সকল বুথ)</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>
              <div class="bf-group">
                <label>এজেন্টের ধরন:</label>
                <select [(ngModel)]="broadcastTargetAgentType">
                  <option value="ALL">সকল এজেন্ট (মূল ও বিকল্প)</option>
                  <option value="PRIMARY">শুধুমাত্র মূল এজেন্ট (Primary)</option>
                  <option value="RESERVE">শুধুমাত্র বিকল্প এজেন্ট (Reserve)</option>
                </select>
              </div>
              <div class="bf-count-pill">
                <span>নির্বাচিত প্রাপক: <b>{{targetAgentsCount()}}</b> জন পোলিং এজেন্ট</span>
              </div>
            </div>

            <!-- 4 Statutory Rapid Templates Strip -->
            <div class="templates-section">
              <div class="tpl-title">⚡ সংবিধিবদ্ধ নির্বাচনী রেডিমেড টেমপ্লেট (১-ক্লিকে লোড করুন):</div>
              <div class="tpl-buttons-grid">
                <button type="button" class="tpl-btn" [class.active]="broadcastTemplateType === 'MORNING_CHECKIN'" (click)="selectBroadcastTemplate('MORNING_CHECKIN')">
                  🌅 <b>সকাল ৭:০০</b> বুথ প্রবেশ ও খালি বাক্স সিল চেকিং
                </button>
                <button type="button" class="tpl-btn" [class.active]="broadcastTemplateType === 'TURNOUT_REPORT'" (click)="selectBroadcastTemplate('TURNOUT_REPORT')">
                  🗳️ <b>দুপুর ১২:০০</b> টার্নআউট ও কেন্দ্র রিপোর্ট
                </button>
                <button type="button" class="tpl-btn" [class.active]="broadcastTemplateType === 'FORM8_REMINDER'" (click)="selectBroadcastTemplate('FORM8_REMINDER')">
                  📄 <b>বিকেল ৪:০০</b> গণনা পাহারা ও ফরম-৮ সংগ্রহ (জরুরি)
                </button>
                <button type="button" class="tpl-btn" [class.active]="broadcastTemplateType === 'SOS_ALERT'" (click)="selectBroadcastTemplate('SOS_ALERT')">
                  🚨 <b>আইনি অ্যালার্ট</b> গোলযোগ ও ম্যাজিস্ট্রেট সহায়তা
                </button>
              </div>
            </div>

            <!-- Message Composer Area -->
            <div class="message-composer-box">
              <div class="composer-head">
                <label>বার্তার বিবরণ (Message Content):</label>
                <span class="char-count">{{broadcastMessage.length}} অক্ষর ({{Math.ceil(broadcastMessage.length / 160) || 1}} টি এসএমএস)</span>
              </div>
              <textarea [(ngModel)]="broadcastMessage" rows="4" class="broadcast-textarea" placeholder="পোলিং এজেন্টদের কাছে পাঠানোর জন্য বার্তার বিবরণ লিখুন..."></textarea>
            </div>

            <!-- Send Action Bar -->
            <div class="broadcast-action-bar">
              <button class="primary-button send-btn" [disabled]="sendingBroadcast()" (click)="submitBroadcast()">
                @if(sendingBroadcast()){
                  <span>বার্তা পাঠানো হচ্ছে…</span>
                } @else {
                  <span>🚀 {{broadcastChannel === 'SMS' ? 'এসএমএস ব্রডকাস্ট প্রেরণ করুন' : 'হোয়াটসঅ্যাপে ব্রডকাস্ট পাঠান'}}</span>
                }
              </button>
              <button class="outline-sm-btn" (click)="closeBroadcastModal()">✕ বাতিল</button>
            </div>

            <!-- Recent Broadcasts Outbox History -->
            <div class="broadcast-history-section">
              <div class="hist-head">
                <h4>📜 সাম্প্রতিক প্রেরিত ব্রডকাস্ট হিস্ট্রি (Broadcast Outbox):</h4>
                <button class="refresh-sub-btn" (click)="loadBroadcastLogs()">🔄 রিফ্রেশ</button>
              </div>

              @if(loadingBroadcasts()){
                <div class="empty-hist">হিস্ট্রি লোড হচ্ছে…</div>
              } @else if(broadcastLogs().length === 0){
                <div class="empty-hist">এখন পর্যন্ত কোনো ব্রডকাস্ট পাঠানো হয়নি।</div>
              } @else {
                <div class="history-table-wrap">
                  <table class="history-table">
                    <thead>
                      <tr>
                        <th>চ্যানেল</th>
                        <th>টেমপ্লেট</th>
                        <th>মেসেজের সারসংক্ষেপ</th>
                        <th>প্রাপক</th>
                        <th>স্ট্যাটাস</th>
                        <th>প্রেরণের সময়</th>
                      </tr>
                    </thead>
                    <tbody>
                      @for(log of broadcastLogs(); track log.broadcastId){
                        <tr>
                          <td>
                            <span class="channel-badge" [class.wa]="log.channel === 'WHATSAPP'">
                              {{log.channel === 'WHATSAPP' ? '💬 WhatsApp' : '📱 SMS'}}
                            </span>
                          </td>
                          <td><b>{{log.templateType || 'CUSTOM'}}</b></td>
                          <td class="msg-cell" [title]="log.messageContent">{{log.messageContent}}</td>
                          <td><b>{{log.recipientCount}}</b> জন</td>
                          <td><span class="badge-success">✓ {{log.status}}</span></td>
                          <td><small>{{log.sentAtUtc | date:'hh:mm a, dd MMM'}}</small></td>
                        </tr>
                      }
                    </tbody>
                  </table>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    }\n\n"""

if target_batch_modal_anchor in content:
    content = content.replace(target_batch_modal_anchor, broadcast_modal_template + target_batch_modal_anchor, 1)
    print("Broadcast Modal Template added.")
else:
    print("ERROR: could not find target_batch_modal_anchor")

# 7. Add CSS Styles for Broadcast Modal and WhatsApp Button
old_css_anchor = "    /* Official Polling Agent ID Card & Batch Printing Styles */"
new_broadcast_css = """    /* Polling Agent Broadcast & WhatsApp Styles */
    .agent-contact-group { display: flex; align-items: center; gap: 6px; }
    .wa-mini-btn { background: #dcfce7; color: #15803d; border: 1px solid #86efac; border-radius: 4px; padding: 2px 6px; font-size: 0.68rem; font-weight: 700; text-decoration: none; display: inline-flex; align-items: center; gap: 2px; }
    .wa-mini-btn:hover { background: #bbf7d0; color: #166534; }

    .broadcast-modal-card { width: min(880px, 98vw); max-height: 94vh; overflow-y: auto; background: #f8fafc; padding: 22px; border-radius: 14px; }
    .broadcast-modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px; }
    .broadcast-titles h2 { margin: 0 0 4px 0; color: #082136; font-size: 1.25rem; font-weight: 800; }
    .broadcast-titles .subtitle { margin: 0; font-size: 0.8rem; color: #64748b; }

    .channel-selector-row { display: flex; align-items: center; gap: 14px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; flex-wrap: wrap; }
    .sel-label { font-size: 0.82rem; font-weight: 700; color: #1e293b; }
    .channel-options { display: flex; gap: 10px; flex-wrap: wrap; }
    .channel-pill { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border: 1.5px solid #cbd5e1; border-radius: 20px; font-size: 0.82rem; font-weight: 700; cursor: pointer; color: #475569; background: #f8fafc; }
    .channel-pill.active { border-color: #059669; background: #ecfdf5; color: #065f46; }

    .broadcast-filter-strip { display: flex; gap: 14px; align-items: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 16px; margin-bottom: 16px; flex-wrap: wrap; }
    .bf-group { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; }
    .bf-group label { font-weight: 700; color: #334155; }
    .bf-group select { border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; font-size: 0.82rem; background: #f8fafc; }
    .bf-count-pill { margin-left: auto; background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; }

    .templates-section { margin-bottom: 16px; }
    .tpl-title { font-size: 0.82rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
    .tpl-buttons-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
    .tpl-btn { background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 9px 12px; font-size: 0.78rem; text-align: left; cursor: pointer; color: #1e293b; transition: all 0.2s; }
    .tpl-btn:hover { border-color: #059669; background: #f0fdf4; }
    .tpl-btn.active { border-color: #059669; background: #ecfdf5; color: #065f46; font-weight: 700; }

    .message-composer-box { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; margin-bottom: 16px; }
    .composer-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .composer-head label { font-size: 0.82rem; font-weight: 700; color: #1e293b; }
    .char-count { font-size: 0.75rem; color: #64748b; }
    .broadcast-textarea { width: 100%; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 10px; font-size: 0.88rem; font-family: inherit; line-height: 1.5; box-sizing: border-box; resize: vertical; outline: none; }
    .broadcast-textarea:focus { border-color: #059669; }

    .broadcast-action-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 22px; }
    .send-btn { background: #059669; color: #fff; font-weight: 800; padding: 10px 22px; border: none; border-radius: 8px; font-size: 0.92rem; cursor: pointer; }
    .send-btn:hover { background: #047857; }

    .broadcast-history-section { border-top: 1.5px solid #e2e8f0; padding-top: 16px; }
    .hist-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .hist-head h4 { margin: 0; font-size: 0.88rem; color: #082136; }
    .refresh-sub-btn { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 4px 10px; font-size: 0.72rem; cursor: pointer; }
    .empty-hist { padding: 16px; text-align: center; color: #64748b; font-size: 0.8rem; }
    .history-table-wrap { overflow-x: auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
    .history-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
    .history-table th, .history-table td { padding: 8px 10px; border-bottom: 1px solid #f1f5f9; text-align: left; }
    .history-table th { background: #f8fafc; font-weight: 700; color: #475569; }
    .channel-badge { font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: #e0f2fe; color: #0369a1; }
    .channel-badge.wa { background: #dcfce7; color: #15803d; }
    .msg-cell { max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-style: italic; color: #334155; }\n\n""" + old_css_anchor

if old_css_anchor in content:
    content = content.replace(old_css_anchor, new_broadcast_css, 1)
    print("Broadcast CSS added.")
else:
    print("ERROR: could not find old_css_anchor")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Broadcast UI patch applied successfully!")

