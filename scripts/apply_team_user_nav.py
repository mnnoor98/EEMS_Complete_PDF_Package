# -*- coding: utf-8 -*-

# 1. Update shell.component.ts
shell_path = 'frontend/src/app/layout/shell/shell.component.ts'
with open(shell_path, 'r', encoding='utf-8') as f:
    shell_text = f.read()

old_shell_block = '''        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
          <span>💰</span> ইসি ব্যয় রিটার্ন (Form-12)
        </a>

        <!-- Additional Operational System Links -->
        <div style="border-top: 1px solid #244762; margin: 8px 0; padding-top: 8px;">
          <a [routerLink]="['/elections', myElectionId(), 'centers']" routerLinkActive="active">
            <span>🏫</span> ভোট কেন্দ্র ও বুথ
          </a>
          <a routerLink="/elections" routerLinkActive="active">
            <span>▦</span> নির্বাচন বিবরণ
          </a>
        </div>'''

new_shell_block = '''        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
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
        </div>'''

assert old_shell_block in shell_text, 'old_shell_block not found'
shell_text = shell_text.replace(old_shell_block, new_shell_block, 1)

with open(shell_path, 'w', encoding='utf-8') as f:
    f.write(shell_text)
print('1. shell.component.ts updated!')

# 2. Update block3_styles.py for flex-wrap on .tab-nav
styles_path = 'scripts/war_room_blocks/block3_styles.py'
with open(styles_path, 'r', encoding='utf-8') as f:
    styles_text = f.read()

old_tab_style = '''.tab-nav {
      display: flex;
      gap: 6px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--line);
      padding-bottom: 6px;
      overflow-x: auto;
    }'''

new_tab_style = '''.tab-nav {
      display: flex;
      gap: 6px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--line);
      padding-bottom: 6px;
      flex-wrap: wrap;
    }'''

assert old_tab_style in styles_text, 'old_tab_style not found'
styles_text = styles_text.replace(old_tab_style, new_tab_style, 1)

with open(styles_path, 'w', encoding='utf-8') as f:
    f.write(styles_text)
print('2. block3_styles.py updated!')

# 3. Update block2_tabs.py for quick action button
tabs_path = 'scripts/war_room_blocks/block2_tabs.py'
with open(tabs_path, 'r', encoding='utf-8') as f:
    tabs_text = f.read()

old_quick_bar = '''            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="btn-sm" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড</button>
              <button class="btn-sm highlight-btn" (click)="openVoterBroadcastModal()">📱 বাল্ক SMS / WA</button>
              <button class="btn-sm" (click)="openSmsConfigModal()">⚙️ SMS গেটওয়ে</button>
              <button class="btn-sm outline" (click)="setTab('campaign')">📢 প্রচার সূচি</button>
              <button class="btn-sm alert-btn" (click)="openAddIncidentModal()">🚨 ম্যাজিস্ট্রেট অভিযোগ</button>
              <button class="btn-sm outline" (click)="setTab('expenses')">💰 ইসি ব্যয় রিটার্ন</button>
            </div>'''

new_quick_bar = '''            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button class="btn-sm" style="background: #e0e7ff; color: #4338ca; font-weight: 700; border-color: #c7d2fe;" (click)="setTab('team')">👥 কর্মী ও ইউজার তৈরি</button>
              <button class="btn-sm" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড</button>
              <button class="btn-sm highlight-btn" (click)="openVoterBroadcastModal()">📱 বাল্ক SMS / WA</button>
              <button class="btn-sm" (click)="openSmsConfigModal()">⚙️ SMS গেটওয়ে</button>
              <button class="btn-sm outline" (click)="setTab('campaign')">📢 প্রচার সূচি</button>
              <button class="btn-sm alert-btn" (click)="openAddIncidentModal()">🚨 ম্যাজিস্ট্রেট অভিযোগ</button>
              <button class="btn-sm outline" (click)="setTab('expenses')">💰 ইসি ব্যয় রিটার্ন</button>
            </div>'''

assert old_quick_bar in tabs_text, 'old_quick_bar not found'
tabs_text = tabs_text.replace(old_quick_bar, new_quick_bar, 1)

with open(tabs_path, 'w', encoding='utf-8') as f:
    f.write(tabs_text)
print('3. block2_tabs.py updated!')

# 4. Update block4_class.py for setTab and load
class_path = 'scripts/war_room_blocks/block4_class.py'
with open(class_path, 'r', encoding='utf-8') as f:
    class_text = f.read()

old_set_tab = '''    } else if (tab === 'expenses') {
      this.loadExpenseReport();
    }
  }'''

new_set_tab = '''    } else if (tab === 'expenses') {
      this.loadExpenseReport();
    } else if (tab === 'team') {
      this.loadTeamUsers();
    }
  }'''

assert old_set_tab in class_text, 'old_set_tab not found'
class_text = class_text.replace(old_set_tab, new_set_tab, 1)

old_load_subscribe = '''      this.loadVoters();
    });'''

new_load_subscribe = '''      this.loadVoters();
      this.loadTeamUsers();
    });'''

if old_load_subscribe in class_text:
    class_text = class_text.replace(old_load_subscribe, new_load_subscribe, 1)

with open(class_path, 'w', encoding='utf-8') as f:
    f.write(class_text)
print('4. block4_class.py updated!')

