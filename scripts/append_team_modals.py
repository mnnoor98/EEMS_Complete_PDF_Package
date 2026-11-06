with open('scripts/war_room_blocks/block2_modals.py', 'r', encoding='utf-8') as f:
    text = f.read()

team_modals_html = """
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
"""

# Insert right before the last '''
last_quote_pos = text.rfind("'''")
assert last_quote_pos != -1, "closing quote not found"

new_text = text[:last_quote_pos] + team_modals_html + text[last_quote_pos:]

with open('scripts/war_room_blocks/block2_modals.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Appended team modals to block2_modals.py successfully!')

