file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "  async openBatchIdCardsModal() {"

methods = """  openBroadcastModal() {
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
  }\n\n"""

if target in content:
    content = content.replace(target, methods + target, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Methods injected successfully!")
else:
    print("Could not find target")

