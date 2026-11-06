# 1. Update block4_class.py to subscribe to route.fragment
with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_init = '''  ngOnInit() {
    this.electionId = this.route.snapshot.paramMap.get('electionId') || '';
    if (this.electionId) {
      this.load();
    }
  }'''

new_init = '''  ngOnInit() {
    this.electionId = this.route.snapshot.paramMap.get('electionId') || '';
    if (this.electionId) {
      this.load();
    }

    // Listen to fragment changes from sidebar menu navigation
    this.route.fragment.subscribe(frag => {
      if (frag && ['overview', 'agents', 'voters', 'campaign', 'incidents', 'results', 'expenses'].includes(frag)) {
        this.activeTab.set(frag as WarRoomTab);
      }
    });
  }'''

assert old_init in text, "old_init not found"
text = text.replace(old_init, new_init)

# Update setTab
old_set_tab = '''  setTab(tab: WarRoomTab) {
    this.activeTab.set(tab);
  }'''

new_set_tab = '''  setTab(tab: WarRoomTab) {
    this.activeTab.set(tab);
    this.router.navigate([], { fragment: tab, queryParamsHandling: 'preserve' });
  }'''

assert old_set_tab in text, "old_set_tab not found"
text = text.replace(old_set_tab, new_set_tab)

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block4_class.py with route.fragment listener!')

# 2. Update shell.component.ts
with open('frontend/src/app/layout/shell/shell.component.ts', 'r', encoding='utf-8') as f:
    shell_text = f.read()

old_candidate_menu = '''      } @else {
        <!-- Candidate Dedicated Operations Navigation -->
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">
          <span>🗳️</span> প্রার্থীর ওয়ার রুম
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'agents'">
          <span>👥</span> বুথ এজেন্ট ও কেন্দ্র
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'voters'">
          <span>🗳️</span> ভোটার স্লিপ বিতরণ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'results'">
          <span>📊</span> ফলাফল ও ডিক্লেয়ারেশন
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'incidents'">
          <span>⚠️</span> নির্বাচনী অভিযোগ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
          <span>💰</span> খরচের হিসাব (EC)
        </a>
      }'''

new_candidate_menu = '''      } @else {
        <!-- Candidate Dedicated Operations Navigation with Full Tab Routing -->
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'overview'" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">
          <span>🗳️</span> কমান্ড সেন্টার (সংক্ষেপ)
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'agents'">
          <span>🛡️</span> পোলিং এজেন্ট ও ফরম-৯
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'voters'">
          <span>👥</span> ভোটার স্লিপ ও বাল্ক মেসেজিং
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'campaign'">
          <span>📢</span> প্রচার সূচি ও পারমিট
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'incidents'">
          <span>🚨</span> নির্বাচনী অভিযোগ
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'results'">
          <span>🗳️</span> লাইভ ফলাফল ও ফরম-৮
        </a>
        <a [routerLink]="['/elections', myElectionId(), 'candidate-war-room']" [fragment]="'expenses'">
          <span>💰</span> ইসি ব্যয় রিটার্ন (Form-12)
        </a>

        <!-- Additional Operational Links for Candidate Representative -->
        <div style="border-top: 1px solid #244762; margin: 8px 0; padding-top: 8px;">
          <a [routerLink]="['/elections', myElectionId(), 'centers']" routerLinkActive="active">
            <span>🏫</span> ভোট কেন্দ্র ও বুথ
          </a>
          <a routerLink="/elections" routerLinkActive="active">
            <span>▦</span> নির্বাচন তালিকা
          </a>
        </div>
      }'''

assert old_candidate_menu in shell_text, "old_candidate_menu not found"
shell_text = shell_text.replace(old_candidate_menu, new_candidate_menu)

with open('frontend/src/app/layout/shell/shell.component.ts', 'w', encoding='utf-8') as f:
    f.write(shell_text)

print('Updated shell.component.ts navigation menu!')

