import { ChangeDetectionStrategy, Component, computed, inject, OnInit, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService, cleanBanglaText } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CandidateWarRoomHero } from '../../core/models/api.models';

@Component({
  selector: 'eems-shell', imports: [RouterOutlet, RouterLink, RouterLinkActive], changeDetection: ChangeDetectionStrategy.OnPush, template: `
<div class="shell">
  <aside>
    <a class="logo" [routerLink]="auth.isSuperAdmin() ? '/dashboard' : ['/elections', myElectionId(), 'candidate-war-room']">
      <b>E</b><span>EEMS</span>
    </a>
    <nav aria-label="Main navigation">
      @if(auth.isSuperAdmin()){
        @if(auth.hasPermission('dashboard.read')){<a routerLink="/dashboard" routerLinkActive="active"><span>⌂</span> ড্যাশবোর্ড</a>}
        <a [routerLink]="['/elections', activeElectionId(), 'candidate-war-room']" routerLinkActive="active"><span>🗳️</span> প্রার্থী ওয়ার রুম</a>
        <a routerLink="/candidates/master-overview" routerLinkActive="active"><span>⭐</span> মাস্টার প্রার্থী তদারকি</a>
        <a routerLink="/candidates/entry" routerLinkActive="active"><span>👤</span> প্রার্থী তথ্য এন্ট্রি</a>
        <a routerLink="/administration/users" routerLinkActive="active"><span>👥</span> ইউজার তৈরি ও রোল</a>
        <a [routerLink]="['/elections', activeElectionId(), 'centers']" routerLinkActive="active"><span>🏫</span> ভোট কেন্দ্র ও বুথ এন্ট্রি</a>
        <a routerLink="/elections" routerLinkActive="active"><span>▦</span> নির্বাচন তালিকা</a>
        @if(auth.hasPermission('dashboard.read')){<a routerLink="/administration" routerLinkActive="active"><span>⚙</span> অ্যাডমিনিস্ট্রেশন</a>}
        @if(auth.hasPermission('elections.manage')){<a routerLink="/administration/master-data" routerLinkActive="active"><span>◆</span> মাস্টার ডাটা</a>}
        @if(auth.hasPermission('reporting.read')){<a routerLink="/oversight" routerLinkActive="active"><span>◉</span> ওভারসাইট</a>}
      } @else {
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
      }
    </nav>
    <div class="security">
      @if(auth.isSuperAdmin()){
        <b>👑 কেন্দ্রীয় অ্যাডমিন প্ল্যাটফর্ম</b>
        <span>RLS + সর্বজনীন নিয়ন্ত্রণ</span>
      } @else {
        <b>🎯 {{candidateDisplayName()}}</b>
        <span>{{candidatePartyName()}} · {{candidateAreaName()}}</span>
      }
    </div>
  </aside>

  <div class="main">
    <header>
      <div class="header-left">
        @if(auth.isSuperAdmin()){
          <span class="super-badge">👑 সুপার অ্যাডমিন (Central Super Admin)</span>
          @if(electionCandidates().length > 0){
            <select class="candidate-select" aria-label="Switch candidate" [value]="auth.activeCandidateId() ?? ''" (change)="onCandidateChange($any($event.target).value)">
              <option value="">👥 সকল প্রার্থী ভিউ (All Candidates)</option>
              @for(c of electionCandidates(); track c.candidateId){
                <option [value]="c.candidateId">{{c.symbolEmoji}} {{c.name}} ({{c.partyName}}){{c.areaName ? ' · ' + c.areaName : ''}}</option>
              }
            </select>
          }
        }@else{
          <span class="candidate-badge">
            <span class="pulse-dot"></span>
            {{myCandidate()?.symbolEmoji || '🏺'}} <b>{{candidateDisplayName()}}</b> ({{candidatePartyName()}}) · {{candidateAreaName()}}
          </span>
        }
      </div>

      <div class="profile">
        <span class="avatar">{{initial}}</span>
        <div class="desktop-only">
          <b>{{auth.displayName()}}</b>
          <small>{{auth.isSuperAdmin() ? 'সুপার ইউজার' : (candidateDisplayName() + ' প্রতিনিধি')}}</small>
        </div>
        <button (click)="auth.logout()" title="লগআউট" aria-label="Sign out">↗</button>
      </div>
    </header>

    <main><router-outlet /></main>
  </div>
</div>
`, styles: [`
.shell{min-height:100vh;display:grid;grid-template-columns:250px 1fr}
aside{background:var(--navy-deep);color:#d9e6ed;padding:24px 16px;display:flex;flex-direction:column}
.logo{display:flex;align-items:center;gap:10px;color:#fff;text-decoration:none;padding:0 10px 28px;font-weight:800;letter-spacing:.08em}
.logo b{display:grid;place-items:center;width:36px;height:36px;border-radius:10px;background:var(--mint);color:#082136}
nav{display:grid;gap:6px}
nav a{color:#bdd0da;text-decoration:none;padding:12px 13px;border-radius:10px;display:flex;gap:12px;align-items:center;font-weight:600;font-size:.9rem}
nav a.active,nav a:hover:not(.disabled){background:#244762;color:#fff}
nav .disabled{opacity:.55}
nav small{margin-left:auto;font-size:.6rem;text-transform:uppercase}
.security{margin-top:auto;border-top:1px solid #29475e;padding:18px 10px 0;display:grid;gap:4px;font-size:.72rem}
.security span{color:#87a6b7}
.main{min-width:0}
header{height:72px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 clamp(18px,4vw,42px);color:var(--muted);font-size:.8rem}
.header-left{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.super-badge{background:#fff8ed;border:1px solid #f9cca4;color:#8f4500;padding:6px 14px;border-radius:20px;font-weight:700;display:inline-flex;align-items:center;gap:6px;font-size:.8rem}
.candidate-badge{background:#eaf8ef;border:1px solid #82d89b;color:#136c34;padding:6px 14px;border-radius:20px;font-weight:700;display:inline-flex;align-items:center;gap:8px;font-size:.82rem}
.pulse-dot{width:8px;height:8px;border-radius:50%;background:#1db954;display:inline-block;animation:pulse 1.8s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(29,185,84,.7)}70%{box-shadow:0 0 0 6px rgba(29,185,84,0)}100%{box-shadow:0 0 0 0 rgba(29,185,84,0)}}
.candidate-select{border:1.5px solid #d0dbe2;border-radius:9px;padding:6px 10px;font-size:.78rem;background:#fff;color:var(--navy);font-weight:600;outline:none}
.profile{display:flex;align-items:center;gap:10px}
.profile div{display:grid}
.profile small{font-size:.68rem}
.avatar{width:36px;height:36px;display:grid;place-items:center;border-radius:50%;background:#dff3f1;color:#116b64;font-weight:800}
.profile button{border:0;background:#eef3f6;border-radius:8px;width:34px;height:34px;cursor:pointer}
main{padding:clamp(20px,4vw,44px)}
@media(max-width:800px){
  .shell{grid-template-columns:1fr}
  aside{position:fixed;z-index:10;left:0;right:0;bottom:0;height:68px;padding:8px 12px;display:block}
  .logo,.security{display:none}
  nav{display:flex;overflow-x:auto}
  nav a{padding:8px 5px;display:grid;place-items:center;gap:2px;font-size:.65rem;min-width:92px;flex:1}
  nav small{display:none}
  .main{padding-bottom:70px}
  header{height:auto;padding:12px 16px}
  main{padding:20px 16px}
}
`]
})
export class ShellComponent implements OnInit {
  readonly auth = inject(AuthService);
  private readonly api = inject(EemsApiService);
  readonly electionCandidates = signal<CandidateWarRoomHero[]>([]);
  readonly fallbackElectionId = signal<string>('');

  readonly myCandidate = computed(() => {
    const rawId = this.auth.candidateId() || this.auth.activeCandidateId();
    const id = rawId ? rawId.toLowerCase() : '';
    const all = this.electionCandidates();
    if (all.length === 0) return null;
    const found = id ? all.find(c => c.candidateId?.toLowerCase() === id) : null;
    const cand = found || all[0];
    return cand ? {
      ...cand,
      name: cleanBanglaText(cand.name),
      partyName: cleanBanglaText(cand.partyName),
      areaName: cleanBanglaText(cand.areaName)
    } : null;
  });

  readonly candidateDisplayName = computed(() => {
    const cand = this.myCandidate();
    if (cand?.name && !cand.name.includes('à¦') && !cand.name.includes('à§')) {
      return cand.name;
    }
    const fromAuth = cleanBanglaText(this.auth.candidateName());
    if (fromAuth && !fromAuth.includes('à¦') && !fromAuth.includes('à§')) {
      return fromAuth;
    }
    return cand?.name || fromAuth || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক';
  });

  readonly candidatePartyName = computed(() => {
    return cleanBanglaText(this.myCandidate()?.partyName) || 'বাংলাদেশ জামায়াতে ইসলামী';
  });

  readonly candidateAreaName = computed(() => {
    return cleanBanglaText(this.myCandidate()?.areaName) || 'নির্বাচনী আসন';
  });

  readonly myElectionId = computed(() => {
    return this.auth.candidateElectionId() ||
      this.myCandidate()?.electionId ||
      this.fallbackElectionId() ||
      (this.electionCandidates().length > 0 ? this.electionCandidates()[0].electionId || '' : '');
  });

  readonly activeElectionId = computed(() => {
    const activeCandId = this.auth.activeCandidateId();
    if (activeCandId) {
      const activeCand = this.electionCandidates().find(c => c.candidateId === activeCandId);
      if (activeCand?.electionId) return activeCand.electionId;
    }
    return this.myElectionId();
  });

  get initial() {
    return this.auth.displayName().charAt(0).toUpperCase();
  }

  private readonly router = inject(Router);

  ngOnInit() {
    if (this.auth.authenticated()) {
      this.loadCandidates();
      this.loadFallbackElection();
      this.checkCandidateAccess(this.router.url);
    }
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe((e: any) => {
      if (this.auth.authenticated()) {
        this.loadCandidates();
        this.loadFallbackElection();
        this.checkCandidateAccess(e.urlAfterRedirects || e.url);
      }
    });
  }

  private loadFallbackElection() {
    this.api.getElections().subscribe({
      next: els => {
        if (els && els.length > 0 && !this.fallbackElectionId()) {
          this.fallbackElectionId.set(els[0].electionId);
        }
      },
      error: () => { }
    });
  }

  private checkCandidateAccess(currentUrl: string) {
    if (!this.auth.isSuperAdmin() && this.auth.candidateId()) {
      const adminOnlyPaths = ['/dashboard', '/elections', '/candidates/entry', '/candidates/master-overview', '/administration', '/administration/users', '/administration/master-data', '/oversight'];
      const isRestricted = adminOnlyPaths.some(p => currentUrl === p || (p !== '/' && currentUrl.startsWith(p + '/')));
      if (isRestricted || currentUrl === '/') {
        const electId = this.myElectionId();
        void this.router.navigateByUrl(`/elections/${electId}/candidate-war-room`);
      }
    }
  }

  loadCandidates() {
    this.api.getAllCandidates().subscribe({
      next: items => {
        const cleaned = items.map(c => ({
          ...c,
          name: cleanBanglaText(c.name),
          partyName: cleanBanglaText(c.partyName),
          areaName: cleanBanglaText(c.areaName)
        }));
        this.electionCandidates.set(cleaned);
        const candId = this.auth.candidateId()?.toLowerCase();
        const myCand = cleaned.find(c => c.candidateId?.toLowerCase() === candId);
        if (myCand?.name && !myCand.name.includes('à¦')) {
          this.auth.updateCandidateName(myCand.name);
        }
      },
      error: () => { }
    });
  }

  onCandidateChange(candId: string) {
    this.auth.setActiveCandidate(candId ? candId : null);
  }
}
