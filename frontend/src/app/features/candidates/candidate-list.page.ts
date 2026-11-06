import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CandidateSummary, ElectionLookups, ElectionSummary, ElectionSymbolSummary } from '../../core/models/api.models';

interface CandidateForm {
  name: string;
  externalReference: string;
  positionId: number;
  areaId: number;
  nominationReference: string;
  symbolId: number | null;
  partyName: string;
  slogan: string;
}

@Component({
  selector: 'eems-candidate-list',
  imports: [FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <a class="back" routerLink="/elections">← Election workspaces</a>
    <section class="heading">
      <div>
        <p class="eyebrow">CANDIDATE & CAMPAIGN MANAGEMENT</p>
        <h1 class="page-title">{{election()?.name || 'Election candidates'}}</h1>
        <p>Register nominations, electoral symbols (প্রতীক), and review the active campaign roster.</p>
      </div>
      <div class="heading-actions">
        <a class="war-room-link" [routerLink]="['/elections', electionId, 'candidates', 'entry']" style="background:#eef6f8;color:var(--teal);border-color:#bfe4ed;">
          👤 প্রার্থী তথ্য এন্ট্রি পেজ →
        </a>
        <a class="war-room-link" [routerLink]="['/elections', electionId, 'candidate-war-room']">
          🎖️ Candidate War Room
        </a>
        @if(canManage()){
          <button class="primary-button" (click)="toggleForm()">
            {{showForm() ? 'Close form' : '+ Register candidate'}}
          </button>
        }
      </div>
    </section>

    @if(error()){
      <div class="error-banner">{{error()}} <button (click)="load()">Retry</button></div>
    }
    @if(notice()){
      <div class="success-banner">{{notice()}}</div>
    }

    @if(showForm()){
      <section class="card form-card">
        <div>
          <p class="eyebrow">NOMINATION & ELECTORAL IDENTITY</p>
          <h2>Candidate & Symbol Registration</h2>
        </div>
        <form (ngSubmit)="save()">
          <div class="form-grid">
            <div class="form-field wide">
              <label for="candidate-name">Candidate name (প্রার্থীর পূর্ণ নাম) *</label>
              <input id="candidate-name" name="name" required maxlength="200" [(ngModel)]="form.name" placeholder="e.g. জনাব মোহাম্মদ আশরাফুল ইসলাম">
            </div>

            <div class="form-field">
              <label for="candidate-symbol">Electoral Symbol (নির্বাচনী প্রতীক)</label>
              <select id="candidate-symbol" name="symbolId" [(ngModel)]="form.symbolId">
                <option [ngValue]="null">No symbol yet (Pending allocation)</option>
                @for(s of symbols(); track s.id){
                  <option [ngValue]="s.id">{{s.iconEmoji}} {{s.nameBn}} ({{s.nameEn}}) · {{s.category}}</option>
                }
              </select>
            </div>

            <div class="form-field">
              <label for="candidate-party">Political Party / Affiliation (দলীয় অধিভুক্তি)</label>
              <input id="candidate-party" name="partyName" maxlength="150" [(ngModel)]="form.partyName" placeholder="e.g. বাংলাদেশ আওয়ামী লীগ / বিএনপি / স্বতন্ত্র">
            </div>

            <div class="form-field wide">
              <label for="candidate-slogan">Campaign Slogan (নির্বাচনী স্লোগান)</label>
              <input id="candidate-slogan" name="slogan" maxlength="300" [(ngModel)]="form.slogan" placeholder="e.g. উন্নয়ন, ন্যায়বিচার ও জনগণের সেবায় নিবেদিতপ্রাণ">
            </div>

            <div class="form-field">
              <label for="candidate-position">Contesting Position (পদের নাম) *</label>
              <select id="candidate-position" name="position" required [(ngModel)]="form.positionId">
                <option [ngValue]="0">Select position</option>
                @for(item of positions(); track item.id){
                  <option [ngValue]="item.id">{{item.name}} · {{item.code}}</option>
                }
              </select>
            </div>

            <div class="form-field">
              <label for="candidate-area">Constituency / Area (নির্বাচনী আসন) *</label>
              <select id="candidate-area" name="area" required [(ngModel)]="form.areaId">
                <option [ngValue]="0">Select area</option>
                @for(item of lookups()?.areas ?? []; track item.id){
                  <option [ngValue]="item.id">{{item.nameEn || item.nameBn}} · {{item.code}}</option>
                }
              </select>
            </div>

            <div class="form-field">
              <label for="nomination-reference">Nomination Reference</label>
              <input id="nomination-reference" name="nominationReference" maxlength="120" [(ngModel)]="form.nominationReference" placeholder="e.g. EC-NOM-2026-001">
            </div>

            <div class="form-field">
              <label for="candidate-reference">External/NID Reference</label>
              <input id="candidate-reference" name="externalReference" maxlength="100" [(ngModel)]="form.externalReference" placeholder="e.g. NID-1985458920">
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="text-button" (click)="toggleForm()">Cancel</button>
            <button class="primary-button" [disabled]="saving() || !validForm()">
              {{saving() ? 'Saving…' : 'Register nomination & symbol'}}
            </button>
          </div>
        </form>
      </section>
    }

    @if(loading()){
      <div class="card empty">Loading candidates…</div>
    } @else if(!candidates().length){
      <div class="card empty">
        <h2>No candidates registered</h2>
        <p>Register the candidate profile and assign an electoral symbol for this election.</p>
      </div>
    } @else {
      <section class="roster">
        <div class="roster-heading">
          <h2>Contesting Candidates & Symbols</h2>
          <span>{{candidates().length}} registered</span>
        </div>

        <div class="candidate-grid">
          @for(item of candidates(); track item.assignmentId){
            <article class="card candidate-card">
              <div class="symbol-banner">
                <div class="symbol-icon">{{item.symbolEmoji || '🗳️'}}</div>
                <div class="symbol-text">
                  <span class="symbol-label">Electoral Symbol</span>
                  <b class="symbol-name">{{item.symbolNameBn || item.symbolNameEn || 'প্রতীক নির্ধারিত হয়নি'}}</b>
                </div>
                <span class="status-pill">{{item.isActive ? 'Active' : 'Inactive'}}</span>
              </div>

              <div class="candidate-body">
                <h3>{{item.name}}</h3>
                <p class="party-text">{{item.partyName || 'স্বতন্ত্র প্রার্থী (Independent)'}}</p>
                <p class="position-sub">{{positionName(item.positionId)}} · {{areaName(item.areaId)}}</p>

                @if(item.slogan){
                  <blockquote class="slogan-quote">"{{item.slogan}}"</blockquote>
                }

                <div class="ref-row">
                  <span><b>Nomination:</b> {{item.nominationReference || '—'}}</span>
                  <span><b>Ref/NID:</b> {{item.externalReference || '—'}}</span>
                </div>

                <div class="card-footer">
                  <a class="hub-btn" [routerLink]="['/elections', electionId, 'candidate-war-room']">
                    🎖️ Candidate War Room →
                  </a>
                </div>
              </div>
            </article>
          }
        </div>
      </section>
    }
  `,
  styles: [`
    .back { display: inline-block; margin-bottom: 18px; color: var(--teal); font-weight: 700; text-decoration: none; }
    .heading { display: flex; justify-content: space-between; align-items: end; gap: 20px; margin-bottom: 26px; }
    .heading p { color: var(--muted); margin-bottom: 0; }
    .heading-actions { display: flex; gap: 12px; align-items: center; }
    .war-room-link { background: #0f172a; color: #38bdf8; padding: 10px 16px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 0.85rem; border: 1px solid #1e293b; display: inline-flex; align-items: center; gap: 6px; }
    .war-room-link:hover { background: #1e293b; }
    .form-card { padding: 24px; margin-bottom: 26px; }
    .form-card h2 { margin-top: 0; }
    .form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .wide { grid-column: 1 / -1; }
    .form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
    .text-button { border: 0; background: transparent; color: var(--teal); font-weight: 700; cursor: pointer; }
    .success-banner { border: 1px solid #a8ddd1; background: #effbf8; color: #126b64; padding: 12px 14px; border-radius: 10px; margin-bottom: 20px; font-weight: 600; }
    .error-banner { margin-bottom: 20px; }
    .roster-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .roster-heading h2 { margin: 0; }
    .roster-heading span { color: var(--muted); font-size: 0.82rem; }
    .candidate-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }
    .candidate-card { padding: 0; overflow: hidden; display: flex; flex-direction: column; }
    .symbol-banner { background: linear-gradient(135deg, #0e2942, #17395b); color: #fff; padding: 16px 20px; display: flex; align-items: center; gap: 14px; }
    .symbol-icon { font-size: 2.2rem; line-height: 1; }
    .symbol-text { display: grid; flex: 1; }
    .symbol-label { font-size: 0.68rem; text-transform: uppercase; color: #82ddd5; letter-spacing: 0.05em; font-weight: 700; }
    .symbol-name { font-size: 1.25rem; font-weight: 800; color: #ffffff; }
    .status-pill { font-size: 0.68rem; background: rgba(255,255,255,0.15); padding: 4px 8px; border-radius: 99px; text-transform: uppercase; font-weight: 700; }
    .candidate-body { padding: 20px; display: flex; flex-direction: column; flex: 1; }
    .candidate-body h3 { margin: 0 0 4px; font-size: 1.25rem; color: var(--navy); }
    .party-text { color: var(--teal); font-weight: 700; font-size: 0.88rem; margin: 0 0 4px; }
    .position-sub { color: var(--muted); font-size: 0.8rem; margin: 0 0 12px; }
    .slogan-quote { margin: 0 0 16px; padding: 8px 12px; background: #f8fafc; border-left: 3px solid var(--teal); font-style: italic; font-size: 0.82rem; color: #334155; }
    .ref-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.76rem; color: var(--muted); padding-top: 10px; border-top: 1px solid var(--line); margin-bottom: 16px; }
    .ref-row b { color: var(--navy); }
    .card-footer { margin-top: auto; padding-top: 10px; }
    .hub-btn { display: flex; justify-content: center; align-items: center; gap: 6px; background: #f1f5f9; color: #0f172a; border-radius: 8px; padding: 10px; font-size: 0.82rem; font-weight: 700; text-decoration: none; transition: all 0.15s; }
    .hub-btn:hover { background: #e2e8f0; color: #0284c7; }
    @media (max-width: 650px) {
      .heading { display: grid; align-items: start; }
      .heading-actions { flex-direction: column; align-items: stretch; }
      .form-grid { grid-template-columns: 1fr; }
      .wide { grid-column: auto; }
      .candidate-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class CandidateListPage {
  private readonly api = inject(EemsApiService);
  private readonly auth = inject(AuthService);
  readonly electionId = inject(ActivatedRoute).snapshot.paramMap.get('electionId') ?? '';

  readonly candidates = signal<CandidateSummary[]>([]);
  readonly symbols = signal<ElectionSymbolSummary[]>([]);
  readonly lookups = signal<ElectionLookups | null>(null);
  readonly election = signal<ElectionSummary | null>(null);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly showForm = signal(false);
  readonly error = signal('');
  readonly notice = signal('');
  readonly canManage = () => this.auth.hasPermission('elections.manage');

  readonly positions = computed(() => {
    const typeId = this.election()?.electionTypeId;
    return (this.lookups()?.positions ?? []).filter(item => item.electionTypeId === typeId);
  });

  form: CandidateForm = this.emptyForm();

  constructor() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.error.set('');
    forkJoin({
      candidates: this.api.getCandidates(this.electionId),
      symbols: this.api.getElectionSymbols(),
      elections: this.api.getElections(),
      lookups: this.api.getElectionLookups()
    }).subscribe({
      next: value => {
        this.candidates.set(value.candidates);
        this.symbols.set(value.symbols);
        this.election.set(value.elections.find(item => item.electionId === this.electionId) ?? null);
        this.lookups.set(value.lookups);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load candidate and symbol data.');
        this.loading.set(false);
      }
    });
  }

  toggleForm() {
    this.showForm.update(value => !value);
    this.form = this.emptyForm();
    if (this.showForm()) {
      this.form.positionId = this.positions()[0]?.id ?? 0;
      this.form.areaId = this.election()?.areaId ?? this.lookups()?.areas[0]?.id ?? 0;
    }
  }

  validForm() {
    return !!this.form.name.trim() &&
           this.form.name.length <= 200 &&
           this.form.positionId > 0 &&
           this.form.areaId > 0;
  }

  save() {
    if (!this.validForm() || this.saving()) return;
    this.saving.set(true);
    this.error.set('');
    this.api.addCandidate(this.electionId, {
      name: this.form.name.trim(),
      externalReference: this.form.externalReference.trim() || null,
      positionId: this.form.positionId,
      areaId: this.form.areaId,
      nominationReference: this.form.nominationReference.trim() || null,
      symbolId: this.form.symbolId,
      partyName: this.form.partyName.trim() || null,
      slogan: this.form.slogan.trim() || null
    }).subscribe({
      next: item => {
        this.candidates.update(items => [...items, item].sort((a, b) => a.name.localeCompare(b.name)));
        this.notice.set('Candidate and Electoral Symbol registered successfully.');
        this.saving.set(false);
        this.showForm.set(false);
        this.form = this.emptyForm();
      },
      error: () => {
        this.error.set('Could not register candidate. Check the position and area.');
        this.saving.set(false);
      }
    });
  }

  positionName(id: number) {
    return this.lookups()?.positions.find(item => item.id === id)?.name ?? `Position ${id}`;
  }

  areaName(id: number) {
    const item = this.lookups()?.areas.find(area => area.id === id);
    return item ? (item.nameEn || item.nameBn) : `Area ${id}`;
  }

  private emptyForm(): CandidateForm {
    return {
      name: '',
      externalReference: '',
      positionId: 0,
      areaId: 0,
      nominationReference: '',
      symbolId: null,
      partyName: '',
      slogan: ''
    };
  }
}
