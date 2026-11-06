with open('scripts/war_room_blocks/block2_modals.py', 'r', encoding='utf-8') as f:
    text = f.read()

target_anchor = '          <!-- Target Filter Group -->'
assert target_anchor in text, "target_anchor not found"

wa_bot_ui = '''          <!-- WhatsApp Sub-mode & Live Bot QR Controller -->
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

'''

text = text.replace(target_anchor, wa_bot_ui + target_anchor)

with open('scripts/war_room_blocks/block2_modals.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block2_modals.py with WhatsApp Auto-Bot UI!')

