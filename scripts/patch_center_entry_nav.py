# -*- coding: utf-8 -*-

# 1. Update shell.component.ts
shell_path = 'frontend/src/app/layout/shell/shell.component.ts'
with open(shell_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_nav = '''      } @else {
        <!-- Candidate Dedicated Operations Navigation with Working Tab Navigation -->
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'overview'">
          <span>📊</span> কমান্ড সেন্টার (সংক্ষেপ)
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'agents'">
          <span>🛡️</span> পোলিং এজেন্ট ও কেন্দ্র
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'voters'">
          <span>👥</span> ভোটার স্লিপ ও বাল্ক মেসেজ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'campaign'">
          <span>📢</span> প্রচার সূচি ও পারমিট
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'incidents'">
          <span>🚨</span> নির্বাচনী অভিযোগ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'results'">
          <span>🗳️</span> ভোট গণনা ও ফলাফল
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
          <span>💰</span> ইসি ব্যয় রিটার্ন (Form-12)
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'team'">
          <span>👥</span> ক্যাম্পেইন কর্মী ও ইউজার
        </a>

        <!-- Additional Operational System Links -->
        <div style="border-top: 1px solid #244762; margin: 8px 0; padding-top: 8px;">
          <a routerLink="/administration/users" routerLinkActive="active">
            <span>👤</span> ইউজার তৈরি ও রোল
          </a>
          <a [routerLink]="['/elections', myElectionId(), 'centers']" routerLinkActive="active">
            <span>🏫</span> ভোট কেন্দ্র ও বুথ
          </a>
          <a routerLink="/elections" routerLinkActive="active">
            <span>▦</span> নির্বাচন বিবরণ
          </a>
        </div>
      }'''

new_nav = '''      } @else {
        <!-- Candidate Dedicated Operations Navigation with Working Tab Navigation -->
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'overview'">
          <span>📊</span> কমান্ড সেন্টার (সংক্ষেপ)
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'centers']" routerLinkActive="active">
          <span>🏫</span> ভোট কেন্দ্র ও বুথ এন্ট্রি
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'agents'">
          <span>🛡️</span> পোলিং এজেন্ট ও কেন্দ্র
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'voters'">
          <span>👥</span> ভোটার স্লিপ ও বাল্ক মেসেজ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'campaign'">
          <span>📢</span> প্রচার সূচি ও পারমিট
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'incidents'">
          <span>🚨</span> নির্বাচনী অভিযোগ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'results'">
          <span>🗳️</span> ভোট গণনা ও ফলাফল
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
          <span>💰</span> ইসি ব্যয় রিটার্ন (Form-12)
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'team'">
          <span>👥</span> ক্যাম্পেইন কর্মী ও ইউজার
        </a>
        <a routerLink="/administration/users" routerLinkActive="active">
          <span>👤</span> ইউজার তৈরি ও রোল
        </a>

        <!-- Additional Operational System Links -->
        <div style="border-top: 1px solid #244762; margin: 8px 0; padding-top: 8px;">
          <a routerLink="/elections" routerLinkActive="active">
            <span>▦</span> নির্বাচন বিবরণ
          </a>
        </div>
      }'''

assert old_nav in text, 'old_nav not found'
text = text.replace(old_nav, new_nav, 1)

with open(shell_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('1. shell.component.ts navigation updated!')

# 2. Update block2_tabs.py
tabs_path = 'scripts/war_room_blocks/block2_tabs.py'
with open(tabs_path, 'r', encoding='utf-8') as f:
    tabs_text = f.read()

# In Pillar 1
old_p1_actions = '''              <div class="op-actions">
                <button class="btn-sm" (click)="setTab('agents')">এজেন্ট তালিকা দেখুন</button>
                <button class="btn-sm outline" (click)="openAddAgentModal()">+ এজেন্ট নিয়োগ</button>
                <button class="btn-sm badge-btn" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড প্রিন্ট</button>
              </div>'''

new_p1_actions = '''              <div class="op-actions">
                <a [routerLink]="['/elections', electionId, 'centers']" class="btn-sm" style="text-decoration: none; background: #e0f2fe; color: #0369a1; font-weight: 700;">🏫 কেন্দ্র ও বুথ এন্ট্রি</a>
                <button class="btn-sm" (click)="setTab('agents')">এজেন্ট তালিকা দেখুন</button>
                <button class="btn-sm outline" (click)="openAddAgentModal()">+ এজেন্ট নিয়োগ</button>
                <button class="btn-sm badge-btn" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড প্রিন্ট</button>
              </div>'''

assert old_p1_actions in tabs_text, 'old_p1_actions not found'
tabs_text = tabs_text.replace(old_p1_actions, new_p1_actions, 1)

# In Quick Action Bar
old_q_actions = '''            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="btn-sm" style="background: #e0e7ff; color: #4338ca; font-weight: 700; border-color: #c7d2fe;" (click)="setTab('team')">👥 কর্মী ও ইউজার তৈরি</button>
              <button class="btn-sm" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড</button>'''

new_q_actions = '''            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <a [routerLink]="['/elections', electionId, 'centers']" class="btn-sm" style="text-decoration: none; background: #f0fdf4; color: #166534; font-weight: 700; border-color: #bbf7d0;">🏫 কেন্দ্র ও বুথ এন্ট্রি</a>
              <button class="btn-sm" style="background: #e0e7ff; color: #4338ca; font-weight: 700; border-color: #c7d2fe;" (click)="setTab('team')">👥 কর্মী ও ইউজার তৈরি</button>
              <button class="btn-sm" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড</button>'''

assert old_q_actions in tabs_text, 'old_q_actions not found'
tabs_text = tabs_text.replace(old_q_actions, new_q_actions, 1)

# In centers table header
old_tbl_head = '''            <div class="table-header">
              <h3>ভোটকেন্দ্র ও পোলিং এজেন্ট কভারেজ পর্যবেক্ষণ</h3>
              <button class="outline-btn" (click)="load()">রিলোড</button>
            </div>'''

new_tbl_head = '''            <div class="table-header">
              <h3>ভোটকেন্দ্র ও পোলিং এজেন্ট কভারেজ পর্যবেক্ষণ</h3>
              <div style="display: flex; gap: 8px; align-items: center;">
                <a [routerLink]="['/elections', electionId, 'centers']" class="primary-button" style="text-decoration: none; font-size: 0.85rem; padding: 6px 14px;">
                  ➕ নতুন ভোট কেন্দ্র ও বুথ এন্ট্রি
                </a>
                <button class="outline-btn" (click)="load()">রিলোড</button>
              </div>
            </div>'''

assert old_tbl_head in tabs_text, 'old_tbl_head not found'
tabs_text = tabs_text.replace(old_tbl_head, new_tbl_head, 1)

with open(tabs_path, 'w', encoding='utf-8') as f:
    f.write(tabs_text)
print('2. block2_tabs.py updated!')

