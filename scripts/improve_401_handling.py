with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_save = '''    this.api.updateSmsGatewayConfig(this.electionId, req).subscribe({
      next: cfg => {
        this.savingSmsConfig.set(false);
        this.smsConfig.set(cfg);
        alert('✅ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন সফলভাবে সংরক্ষিত হয়েছে।');
      },
      error: () => this.savingSmsConfig.set(false)
    });'''

new_save = '''    this.api.updateSmsGatewayConfig(this.electionId, req).subscribe({
      next: cfg => {
        this.savingSmsConfig.set(false);
        this.smsConfig.set(cfg);
        alert('✅ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন সফলভাবে সংরক্ষিত হয়েছে।');
      },
      error: (err) => {
        this.savingSmsConfig.set(false);
        if (err?.status === 401) {
          alert('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          alert('কনফিগারেশন সংরক্ষণ করতে ব্যর্থ হয়েছে।');
        }
      }
    });'''

assert old_save in text, "old_save not found"
text = text.replace(old_save, new_save)

old_test = '''    this.api.testSmsGateway(this.electionId, { phone: this.smsTestPhone(), message: 'EEMS টেস্ট এসএমএস।' }).subscribe({
      next: res => {
        this.testingSms.set(false);
        this.smsTestResult.set(res.message);
      },
      error: () => {
        this.testingSms.set(false);
        this.smsTestResult.set('টেস্ট এসএমএস পাঠাতে ব্যর্থ হয়েছে।');
      }
    });'''

new_test = '''    this.api.testSmsGateway(this.electionId, { phone: this.smsTestPhone(), message: 'EEMS টেস্ট এসএমএস।' }).subscribe({
      next: res => {
        this.testingSms.set(false);
        this.smsTestResult.set(res.message);
      },
      error: (err) => {
        this.testingSms.set(false);
        if (err?.status === 401) {
          this.smsTestResult.set('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          this.smsTestResult.set('টেস্ট এসএমএস পাঠাতে ব্যর্থ হয়েছে।');
        }
      }
    });'''

assert old_test in text, "old_test not found"
text = text.replace(old_test, new_test)

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block4_class.py with 401 session expiry handling!')

