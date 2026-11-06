# Update block4_class.py
with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add signals
signal_anchor = '  showVoterBroadcastModal = signal(false);'
new_signals = '''  waBotStatus = signal<any>(null);
  waBotQr = signal<string | null>(null);
  loadingWaBot = signal(false);
  waDispatchMode = signal<'AUTO_BOT' | 'MANUAL_CLICK'>('AUTO_BOT');
  private waBotPollTimer: any = null;

  showVoterBroadcastModal = signal(false);'''

assert signal_anchor in text, "signal_anchor not found"
text = text.replace(signal_anchor, new_signals)

# 2. Update openVoterBroadcastModal and add bot methods
open_anchor = '''  openVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(true);
    this.voterBroadcastQueue.set([]);
    this.dispatchCurrentIndex.set(0);
    this.stopAutoDispatch();
  }'''

new_open = '''  openVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(true);
    this.voterBroadcastQueue.set([]);
    this.dispatchCurrentIndex.set(0);
    this.stopAutoDispatch();
    this.loadWaBotStatus();
  }

  loadWaBotStatus() {
    this.loadingWaBot.set(true);
    this.api.getWhatsAppBotStatus().subscribe({
      next: status => {
        this.loadingWaBot.set(false);
        this.waBotStatus.set(status);
        if (!status.connected) {
          this.loadWaBotQr();
        }
      },
      error: () => this.loadingWaBot.set(false)
    });
  }

  loadWaBotQr() {
    this.api.getWhatsAppBotQr().subscribe({
      next: res => {
        if (res.qrDataUrl) {
          this.waBotQr.set(res.qrDataUrl);
        }
        if (res.connected) {
          this.loadWaBotStatus();
        }
      }
    });
  }

  logoutWaBot() {
    if (!confirm('আপনি কি নিশ্চিত যে হোয়াটসঅ্যাপ বট সংযোগ বিচ্ছিন্ন করতে চান?')) return;
    this.api.logoutWhatsAppBot().subscribe({
      next: () => {
        this.loadWaBotStatus();
        alert('হোয়াটসঅ্যাপ সফলভাবে লগআউট করা হয়েছে।');
      }
    });
  }

  startWaBotPoll() {
    this.stopWaBotPoll();
    this.waBotPollTimer = setInterval(() => {
      this.api.getWhatsAppBotStatus().subscribe({
        next: st => {
          this.waBotStatus.set(st);
          if (st.queueStats && st.queueStats.status === 'COMPLETED') {
            this.stopWaBotPoll();
            this.loadVoters();
            alert('🎉 সকল ভোটারের হোয়াটসঅ্যাপে স্বয়ংক্রিয় বার্তা পাঠানো সম্পন্ন হয়েছে!');
          }
        }
      });
    }, 2500);
  }

  stopWaBotPoll() {
    if (this.waBotPollTimer) {
      clearInterval(this.waBotPollTimer);
      this.waBotPollTimer = null;
    }
  }'''

assert open_anchor in text, "open_anchor not found"
text = text.replace(open_anchor, new_open)

# 3. Update closeVoterBroadcastModal
close_anchor = '''  closeVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(false);
    this.stopAutoDispatch();
  }'''

new_close = '''  closeVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(false);
    this.stopAutoDispatch();
    this.stopWaBotPoll();
  }'''

assert close_anchor in text, "close_anchor not found"
text = text.replace(close_anchor, new_close)

# 4. Enhance submitVoterBroadcast to trigger auto bot if selected
old_submit = '''    this.api.sendVoterBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingVoterBroadcast.set(false);
        if (this.voterBroadcastChannel() === 'WHATSAPP') {
          this.voterBroadcastQueue.set(res.queue || []);
          this.dispatchCurrentIndex.set(0);
        } else {
          alert(`✅ বাল্ক এসএমএস সফলভাবে পাঠানো হয়েছে! মোট প্রাপক: ${res.recipientCount} জন ভোটার। স্ট্যাটাস: ${res.status}`);
          this.closeVoterBroadcastModal();
          this.loadVoters();
          this.loadSmsConfig();
        }
      },
      error: err => {
        this.sendingVoterBroadcast.set(false);
        alert(err?.error?.message || 'বার্তা পাঠাতে ত্রুটি হয়েছে।');
      }
    });'''

new_submit = '''    this.api.sendVoterBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingVoterBroadcast.set(false);
        if (this.voterBroadcastChannel() === 'WHATSAPP') {
          if (this.waDispatchMode() === 'AUTO_BOT') {
            if (!this.waBotStatus()?.connected) {
              alert('⚠️ আপনার হোয়াটসঅ্যাপ কিউআর স্ক্যান করা নেই! অনুগ্রহ করে নিচের কিউআর কোড স্ক্যান করে মোবাইল কানেক্ট করুন।');
              return;
            }
            // Dispatch via Auto-Bot microservice
            const botItems = (res.queue || []).map(q => ({
              id: q.voterId,
              name: q.fullName,
              phone: q.phone,
              message: q.message
            }));
            this.api.sendWhatsAppAutoBroadcast({ items: botItems }).subscribe({
              next: botRes => {
                this.startWaBotPoll();
                alert(`🤖 ${botRes.message}`);
              },
              error: e => alert(e?.error?.message || 'বট ব্রডকাস্ট শুরু করতে ব্যর্থ হয়েছে।')
            });
          } else {
            // Manual 1-click web queue
            this.voterBroadcastQueue.set(res.queue || []);
            this.dispatchCurrentIndex.set(0);
          }
        } else {
          alert(`✅ বাল্ক এসএমএস সফলভাবে পাঠানো হয়েছে (SMS.NET.BD)! মোট প্রাপক: ${res.recipientCount} জন ভোটার। স্ট্যাটাস: ${res.status}`);
          this.closeVoterBroadcastModal();
          this.loadVoters();
          this.loadSmsConfig();
        }
      },
      error: err => {
        this.sendingVoterBroadcast.set(false);
        alert(err?.error?.message || 'বার্তা পাঠাতে ত্রুটি হয়েছে।');
      }
    });'''

assert old_submit in text, "old_submit not found"
text = text.replace(old_submit, new_submit)

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block4_class.py with WhatsApp bot signals and dispatcher!')

