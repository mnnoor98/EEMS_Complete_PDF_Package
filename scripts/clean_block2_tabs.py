with open('scripts/war_room_blocks/block2_tabs.py', 'r', encoding='utf-8') as f:
    text = f.read()

marker = '        <!-- ================================================================= -->\n        <!-- TAB 8: CAMPAIGN TEAM & SUB-USERS (মাস্টার প্রার্থীর সাব-ইউজার ও কর্মী) -->'

# Clean block
block_to_remove = """

        <!-- ================================================================= -->
        <!-- TAB 8: CAMPAIGN TEAM & SUB-USERS (মাস্টার প্রার্থীর সাব-ইউজার ও কর্মী) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'team'){
          <section class="card table-card">
            <div class="table-header">
              <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                  👥 প্রার্থীর নিজস্ব ক্যাম্পেইন কর্মী ও সাব-ইউজার ব্যবস্থাপনা
                </h3>
                <p style="margin: 4px 0 0; font-size: 0.85rem; color: #64748b;">
                  মাস্টার প্রার্থীর অধীনে সাব-ইউজার ও কর্মী তৈরি করুন। তাদের সব কার্যক্রম স্বয়ংক্রিয়ভাবে এই প্রার্থীর ওয়ার রুমেই জমা হবে।
                </p>
              </div>
              <div class="action-buttons">
                <button class="btn btn-secondary" (click)="loadTeamUsers()" [disabled]="loadingTeamUsers()">
                  🔄 রিফ্রেশ তালিকা
                </button>
                <button class="btn btn-primary" (click)="openCreateTeamUserModal()">
                  ➕ নতুন কর্মী/ইউজার তৈরি করুন
                </button>
              </div>
            </div>

            <!-- Team Users List Table -->
            <table class="data-table">
              <thead>
                <tr>
                  <th>ক্রমিক</th>
                  <th>ব্যবহারকারী নাম (Username)</th>
                  <th>পূর্ণ নাম</th>
                  <th>দায়িত্ব / রোল</th>
                  <th>যোগাযোগ (মোবাইল ও ইমেইল)</th>
                  <th>স্ট্যাটাস</th>
                  <th>তৈরির তারিখ</th>
                  <th style="text-align: right;">অ্যাকশন</th>
                </tr>
              </thead>
              <tbody>
                @for(u of teamUsers(); track u.userId; let idx = $index){
                  <tr>
                    <td>#{{idx + 1}}</td>
                    <td>
                      <span style="font-family: monospace; font-weight: 700; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; color: #0284c7;">
                        {{u.username}}
                      </span>
                    </td>
                    <td>
                      <strong>{{u.displayName}}</strong>
                    </td>
                    <td>
                      <span class="badge" style="background: #e0f2fe; color: #0369a1; font-weight: 600;">
                        {{u.role || 'ক্যাম্পেইন কর্মী'}}
                      </span>
                    </td>
                    <td>
                      <div style="font-size: 0.85rem;">
                        @if(u.phone){ <div>📞 {{u.phone}}</div> }
                        @if(u.email){ <div style="color: #64748b;">✉️ {{u.email}}</div> }
                        @if(!u.phone && !u.email){ <span style="color: #94a3b8;">—</span> }
                      </div>
                    </td>
                    <td>
                      <span class="status-pill" [class.status-active]="u.isActive" [class.status-absent]="!u.isActive">
                        {{u.isActive ? 'সক্রিয় (Active)' : 'নিষ্ক্রিয় (Inactive)'}}
                      </span>
                    </td>
                    <td style="font-size: 0.82rem; color: #64748b;">
                      {{u.createdAtUtc | date:'shortDate'}}
                    </td>
                    <td style="text-align: right;">
                      <div style="display: flex; gap: 6px; justify-content: flex-end;">
                        <button class="btn btn-sm btn-secondary" (click)="openResetPasswordModal(u)" title="পাসওয়ার্ড পরিবর্তন">
                          🔑 রিসেট
                        </button>
                        <button class="btn btn-sm" [class.btn-danger]="u.isActive" [class.btn-primary]="!u.isActive" (click)="toggleTeamUserStatus(u)">
                          {{u.isActive ? 'নিষ্ক্রিয় করুন' : 'সক্রিয় করুন'}}
                        </button>
                      </div>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="8" class="empty-cell" style="padding: 40px 20px; text-align: center;">
                      <div style="font-size: 2.5rem; margin-bottom: 10px;">👥</div>
                      <h4 style="margin: 0 0 6px; color: #334155;">এখনও কোনো ক্যাম্পেইন কর্মী বা সাব-ইউজার তৈরি করা হয়নি</h4>
                      <p style="margin: 0 0 16px; color: #64748b; font-size: 0.9rem;">
                        আপনার নির্বাচনী কাজের জন্য কো-অর্ডিনেটর, ডাটা এন্ট্রি বা পোলিং এজেন্টের নিজস্ব ইউজার আইডি তৈরি করতে উপরের বাটনে ক্লিক করুন।
                      </p>
                      <button class="btn btn-primary" (click)="openCreateTeamUserModal()">
                        ➕ নতুন কর্মী/ইউজার তৈরি করুন
                      </button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }"""

normalized_text = text.replace('\r\n', '\n')
normalized_block = block_to_remove.replace('\r\n', '\n')

print(f'Count of block: {normalized_text.count(normalized_block)}')

# Replace first 4 occurrences
for _ in range(4):
    pos = normalized_text.find(normalized_block)
    if pos != -1:
        normalized_text = normalized_text[:pos] + normalized_text[pos + len(normalized_block):]

print(f'Remaining occurrences: {normalized_text.count(normalized_block)}')

with open('scripts/war_room_blocks/block2_tabs.py', 'w', encoding='utf-8') as f:
    f.write(normalized_text)

print('Done!')
