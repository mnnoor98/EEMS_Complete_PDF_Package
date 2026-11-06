with open('scripts/war_room_blocks/block2_modals.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                <select [(ngModel)]="smsConfigProvider">
                  <option value="SIMULATOR">সিমুলেটর গেটওয়ে (টেস্ট ও ফ্রি সিমুলেশন)</option>
                  <option value="GREENWEB">গ্রিনওয়েব বাংলাদেশ (Greenweb API)</option>
                  <option value="SSL_WIRELESS">এসএসএল ওয়্যারলেস (SSL Wireless)</option>
                  <option value="CUSTOM_HTTP">কাস্টম REST API</option>
                </select>'''

replacement = '''                <select [(ngModel)]="smsConfigProvider" (ngModelChange)="onSmsProviderChange($event)">
                  <option value="SMS_NET_BD">🇧🇩 এসএমএস.নেট.বিডি (SMS.NET.BD / Alpha SMS - ড্যাশবোর্ড কানেক্টেড)</option>
                  <option value="SIMULATOR">🧪 সিমুলেটর গেটওয়ে (টেস্ট ও ফ্রি সিমুলেশন)</option>
                  <option value="GREENWEB">গ্রিনওয়েব বাংলাদেশ (Greenweb API)</option>
                  <option value="SSL_WIRELESS">এসএসএল ওয়্যারলেস (SSL Wireless)</option>
                  <option value="CUSTOM_HTTP">কাস্টম REST API</option>
                </select>'''

assert target in text, "target not found in block2_modals.py"
text = text.replace(target, replacement)

# Add portal info note above form-grid
old_top = '''            <div style="background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; color: #bae6fd; font-weight: 700;">চলতি SMS অ্যাকাউন্ট ব্যালেন্স</span>
                <b style="font-size: 1.6rem; display: block; margin-top: 2px;">৳{{smsConfig()?.balance || 2499.10 | number:'1.2-2'}}</b>
              </div>
              <span class="badge" style="background: rgba(255,255,255,0.2); color: #fff;">{{smsConfigProvider()}}</span>
            </div>'''

new_top = '''            <div style="background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;">
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
            </div>'''

assert old_top in text, "old_top not found"
text = text.replace(old_top, new_top)

with open('scripts/war_room_blocks/block2_modals.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block2_modals.py successfully!')

