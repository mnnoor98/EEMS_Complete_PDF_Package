import { ChangeDetectionStrategy, Component, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CenterDirectoryItem, ElectionLookups } from '../../core/models/api.models';

interface CenterForm {
  areaId: number;
  code: string;
  name: string;
  address: string;
}

@Component({
  selector: 'eems-polling-centers',
  imports: [FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-container">
      <!-- Breadcrumb & Top Bar -->
      <nav class="breadcrumb">
        <a [routerLink]="['/elections']">নির্বাচন তালিকা</a>
        <span>/</span>
        <span class="current">ভোট কেন্দ্র ও বুথ ব্যবস্থাপনা</span>
      </nav>

      <section class="heading-card">
        <div class="heading-content">
          <div class="badge-row">
            <span class="portal-badge">🏫 POLLING CENTERS DIRECTORY</span>
            <span class="sub-badge">কেন্দ্র ও বুথ ব্যবস্থাপনা</span>
          </div>
          <h1 class="page-title">ভোট কেন্দ্র তালিকা ও নতুন কেন্দ্র এন্ট্রি</h1>
          <p class="subtitle">
            নির্বাচনী আসনের আওতাধীন সকল ভোট কেন্দ্র পরিচালনা করুন, নতুন ভোট কেন্দ্র এন্ট্রি দিন এবং ভেতরের বুথ / ভোটকক্ষ বিন্যাস করুন।
          </p>
        </div>
        <div class="heading-actions">
          @if(canManage()){
            <button type="button" class="action-btn" [class.active-btn]="showForm()" (click)="toggleForm()">
              @if(showForm()){ ✕ ফরম বন্ধ করুন } @else { ➕ নতুন ভোট কেন্দ্র এন্ট্রি }
            </button>
          }
        </div>
      </section>

      @if(error()){
        <div class="alert alert-error" role="alert">
          <span class="alert-ico">⚠️</span>
          <span>{{error()}}</span>
        </div>
      }
      @if(notice()){
        <div class="alert alert-success" role="alert">
          <span class="alert-ico">✓</span>
          <span>{{notice()}}</span>
        </div>
      }

      <!-- Center Entry Form -->
      @if(showForm()){
        <section class="card form-card">
          <div class="form-header">
            <div class="form-header-title">
              <span class="form-icon">🏫</span>
              <div>
                <h2>নতুন ভোট কেন্দ্র এন্ট্রি ফরম (Add Polling Center)</h2>
                <p>কেন্দ্রের তথ্য পূরণ করে সংরক্ষণ বাটনে চাপ দিন। পরবর্তীতে কেন্দ্রের ভেতর বুথ/কক্ষ যোগ করতে পারবেন।</p>
              </div>
            </div>
            <button type="button" class="btn-close" (click)="toggleForm()">✕</button>
          </div>

          <form (ngSubmit)="saveCenter()">
            <div class="form-grid">
              <div class="form-field">
                <label for="center-code">কেন্দ্রের শনাক্তকারী কোড (Center Code) *</label>
                <input
                  id="center-code"
                  name="code"
                  required
                  maxlength="50"
                  [(ngModel)]="form.code"
                  placeholder="যেমন: DHAKA1-CENTER-002 বা C-102"
                />
                <small class="field-hint">অফিসিয়াল কেন্দ্র নম্বর বা ইউনিক কোড লিখুন</small>
              </div>

              <div class="form-field">
                <label for="center-name">ভোট কেন্দ্রের পূর্ণ নাম (Center Name) *</label>
                <input
                  id="center-name"
                  name="name"
                  required
                  maxlength="250"
                  [(ngModel)]="form.name"
                  placeholder="যেমন: ধানমন্ডি সরকারি উচ্চ বিদ্যালয়"
                />
                <small class="field-hint">স্কুল/কলেজ/মাদ্রাসা বা প্রতিষ্ঠানের প্রাতিষ্ঠানিক নাম</small>
              </div>

              <div class="form-field">
                <label for="center-area">নির্বাচনী এলাকা / আসন (Area / Seat) *</label>
                <select id="center-area" name="area" required [(ngModel)]="form.areaId">
                  <option [ngValue]="0">নির্বাচনী আসন নির্বাচন করুন</option>
                  @for(area of lookups()?.areas ?? []; track area.id){
                    <option [ngValue]="area.id">
                      {{area.nameBn || area.nameEn}} ({{area.code}}) · {{area.nameEn}}
                    </option>
                  }
                </select>
                <small class="field-hint">যে আসনের আওতাভুক্ত এই কেন্দ্র</small>
              </div>

              <div class="form-field">
                <label for="center-address">কেন্দ্রের সম্পূর্ণ ঠিকানা ও অবস্থান (Address)</label>
                <input
                  id="center-address"
                  name="address"
                  maxlength="500"
                  [(ngModel)]="form.address"
                  placeholder="যেমন: রোড নং ৮/এ, ধানমন্ডি আ/এ, ঢাকা-১২০৯"
                />
                <small class="field-hint">কেন্দ্রের ভৌগোলিক অবস্থান বা সড়কের ঠিকানা</small>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary" (click)="toggleForm()">বাতিল (Cancel)</button>
              <button type="submit" class="btn-primary" [disabled]="saving() || !validForm()">
                {{saving() ? 'সংরক্ষণ করা হচ্ছে…' : '💾 কেন্দ্র সংরক্ষণ ও অন্তর্ভুক্ত করুন'}}
              </button>
            </div>
          </form>
        </section>
      }

      <!-- Search & Filters -->
      <section class="card filter-card">
        <div class="filter-inputs">
          <div class="form-field search-field">
            <label for="centerSearch">কেন্দ্র অনুসন্ধান (Search)</label>
            <div class="search-input-wrap">
              <span class="search-icon">🔍</span>
              <input
                id="centerSearch"
                [(ngModel)]="search"
                (keyup.enter)="loadCenters()"
                placeholder="কেন্দ্রের নাম, কোড বা ঠিকানা দিয়ে খুঁজুন…"
              />
            </div>
          </div>

          <div class="form-field status-field">
            <label for="verifiedSelect">যাচাইকরণের অবস্থা (Verification)</label>
            <select id="verifiedSelect" [(ngModel)]="verified" (change)="loadCenters()">
              <option value="">সকল ভোট কেন্দ্র (All)</option>
              <option value="true">✓ যাচাইকৃত (Verified)</option>
              <option value="false">⏳ যাচাই বাকি (Awaiting Verification)</option>
            </select>
          </div>

          <div class="filter-btn-wrap">
            <button type="button" class="btn-filter" (click)="loadCenters()">
              ফিল্টার প্রয়োগ
            </button>
          </div>
        </div>
      </section>

      <!-- Center Cards List -->
      <div class="list-summary-bar">
        <span><b>{{total()}}</b> টি ভোট কেন্দ্র তালিকাভুক্ত রয়েছে</span>
        @if(search || verified){
          <span class="filter-active-tag">ফিল্টার সক্রিয়</span>
        }
      </div>

      @if(loading()){
        <div class="loading-state card">
          <div class="spinner"></div>
          <p>ভোট কেন্দ্রের তালিকা লোড হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন…</p>
        </div>
      } @else {
        <div class="center-grid">
          @for(center of centers(); track center.electionCenterId){
            <article class="card center-card">
              <div class="center-card-header">
                <span class="center-code-badge">
                  🏫 {{center.code}}
                </span>
                <span [class]="center.isVerified ? 'badge-verified' : 'badge-pending'">
                  {{center.isVerified ? '✓ যাচাইকৃত' : '⏳ যাচাই বাকি'}}
                </span>
              </div>

              <div class="center-card-body">
                <h3 class="center-name">{{center.name}}</h3>
                <p class="center-address">
                  <span class="pin">📍</span> {{center.address || 'ঠিকানা এন্ট্রি নেই'}}
                </p>
                <div class="center-area-tag">
                  🎯 {{areaName(center.areaId)}}
                </div>
              </div>

              <div class="center-metrics">
                <div class="metric-item">
                  <span class="metric-num">{{center.boothCount}}</span>
                  <span class="metric-label">টি বুথ / ভোটকক্ষ</span>
                </div>
                <div class="metric-item">
                  <span class="metric-num">{{center.activeAgentCount}}</span>
                  <span class="metric-label">জন এজেন্ট নিযুক্ত</span>
                </div>
              </div>

              <div class="center-card-footer">
                <a [routerLink]="[center.electionCenterId]" class="btn-manage-center">
                  <span>বুথ ও বিস্তারিত পরিচালনা</span>
                  <span>➜</span>
                </a>
              </div>
            </article>
          } @empty {
            <div class="card empty-state">
              <div class="empty-icon">🏫</div>
              <h3>কোনো ভোট কেন্দ্র পাওয়া যায়নি</h3>
              <p>নতুন কেন্দ্র যোগ করতে উপরের <b>"+ নতুন ভোট কেন্দ্র এন্ট্রি"</b> বাটনে চাপ দিন অথবা ফিল্টার পরিবর্তন করুন।</p>
            </div>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .page-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: #64748b;
    }
    .breadcrumb a {
      color: #0284c7;
      text-decoration: none;
      font-weight: 500;
    }
    .breadcrumb .current {
      color: #0f172a;
      font-weight: 600;
    }

    .heading-card {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: #fff;
      padding: 28px 32px;
      border-radius: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .badge-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }
    .portal-badge {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
    }
    .sub-badge {
      background: rgba(255, 255, 255, 0.1);
      color: #cbd5e1;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
    }
    .page-title {
      font-size: clamp(1.6rem, 2.8vw, 2.2rem);
      font-weight: 800;
      margin: 4px 0 8px;
      letter-spacing: -0.02em;
    }
    .subtitle {
      color: #94a3b8;
      max-width: 650px;
      margin: 0;
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .action-btn {
      background: #0ea5e9;
      color: #fff;
      border: 0;
      border-radius: 12px;
      padding: 12px 22px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
      transition: all 0.2s;
    }
    .action-btn:hover {
      background: #0284c7;
      transform: translateY(-1px);
    }
    .action-btn.active-btn {
      background: #e2e8f0;
      color: #334155;
      box-shadow: none;
    }

    .alert {
      padding: 14px 18px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 600;
      font-size: 0.92rem;
    }
    .alert-error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
    }
    .alert-success {
      background: #ecfdf5;
      border: 1px solid #a7f3d0;
      color: #047857;
    }

    .form-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 26px;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
      animation: fadeIn 0.2s ease-out;
    }
    .form-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 22px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 16px;
    }
    .form-header-title {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .form-icon {
      font-size: 2rem;
      background: #f0f9ff;
      border-radius: 12px;
      width: 48px;
      height: 48px;
      display: grid;
      place-items: center;
    }
    .form-header h2 {
      margin: 0 0 4px;
      font-size: 1.25rem;
      color: #0f172a;
    }
    .form-header p {
      margin: 0;
      color: #64748b;
      font-size: 0.88rem;
    }
    .btn-close {
      background: transparent;
      border: 0;
      font-size: 1.2rem;
      color: #94a3b8;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 6px;
    }
    .btn-close:hover {
      background: #f1f5f9;
      color: #0f172a;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }
    .form-field {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .form-field label {
      font-size: 0.88rem;
      font-weight: 700;
      color: #334155;
    }
    .form-field input, .form-field select {
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 10px 14px;
      font-size: 0.92rem;
      color: #0f172a;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
      background: #fff;
    }
    .form-field input:focus, .form-field select:focus {
      border-color: #0284c7;
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
    }
    .field-hint {
      color: #94a3b8;
      font-size: 0.78rem;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 14px;
      margin-top: 24px;
      padding-top: 18px;
      border-top: 1px solid #f1f5f9;
    }
    .btn-secondary {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      color: #475569;
      padding: 10px 20px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-primary {
      background: #0284c7;
      border: 0;
      color: #fff;
      padding: 10px 24px;
      border-radius: 10px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
    }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .filter-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 18px 22px;
    }
    .filter-inputs {
      display: grid;
      grid-template-columns: 2fr 1fr auto;
      gap: 16px;
      align-items: flex-end;
    }
    .search-input-wrap {
      position: relative;
      display: flex;
      align-items: center;
    }
    .search-icon {
      position: absolute;
      left: 12px;
      font-size: 0.9rem;
      pointer-events: none;
      color: #94a3b8;
    }
    .search-input-wrap input {
      width: 100%;
      padding-left: 36px;
    }
    .btn-filter {
      background: #0f172a;
      color: #fff;
      border: 0;
      border-radius: 10px;
      padding: 10px 20px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      height: 42px;
    }

    .list-summary-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.88rem;
      color: #64748b;
      padding: 0 4px;
    }
    .filter-active-tag {
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
    }

    .center-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 18px;
    }
    .center-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .center-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.08);
      border-color: #cbd5e1;
    }

    .center-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .center-code-badge {
      font-size: 0.75rem;
      font-weight: 800;
      color: #0284c7;
      background: #f0f9ff;
      border: 1px solid #e0f2fe;
      padding: 3px 8px;
      border-radius: 6px;
      letter-spacing: 0.04em;
    }
    .badge-verified {
      background: #ecfdf5;
      color: #059669;
      border: 1px solid #a7f3d0;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .badge-pending {
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fde68a;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
    }

    .center-name {
      margin: 0 0 6px;
      font-size: 1.15rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.35;
    }
    .center-address {
      color: #64748b;
      font-size: 0.85rem;
      margin: 0 0 8px;
      line-height: 1.4;
    }
    .pin {
      color: #e11d48;
    }
    .center-area-tag {
      display: inline-block;
      font-size: 0.78rem;
      color: #475569;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      padding: 2px 8px;
      border-radius: 6px;
    }

    .center-metrics {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      padding: 12px 0;
      border-top: 1px solid #f1f5f9;
      border-bottom: 1px solid #f1f5f9;
    }
    .metric-item {
      display: flex;
      flex-direction: column;
    }
    .metric-num {
      font-size: 1.25rem;
      font-weight: 800;
      color: #0f172a;
    }
    .metric-label {
      font-size: 0.72rem;
      color: #64748b;
    }

    .btn-manage-center {
      background: #0f172a;
      color: #fff;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 11px 16px;
      border-radius: 10px;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.88rem;
      transition: background 0.15s;
    }
    .btn-manage-center:hover {
      background: #0284c7;
    }

    .empty-state {
      grid-column: 1 / -1;
      text-align: center;
      padding: 48px 24px;
    }
    .empty-icon {
      font-size: 3rem;
      margin-bottom: 12px;
    }
    .empty-state h3 {
      font-size: 1.3rem;
      margin: 0 0 6px;
      color: #0f172a;
    }
    .empty-state p {
      color: #64748b;
      margin: 0;
    }

    .loading-state {
      text-align: center;
      padding: 48px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
      color: #64748b;
    }
    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #e2e8f0;
      border-top-color: #0284c7;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
      .form-grid {
        grid-template-columns: 1fr;
      }
      .filter-inputs {
        grid-template-columns: 1fr;
      }
      .heading-card {
        padding: 20px;
      }
    }
  `]
})
export class PollingCentersPage {
  readonly electionId = input.required<string>();
  private readonly api = inject(EemsApiService);
  private readonly auth = inject(AuthService);

  readonly centers = signal<CenterDirectoryItem[]>([]);
  readonly lookups = signal<ElectionLookups | null>(null);
  readonly total = signal(0);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly showForm = signal(false);
  readonly error = signal('');
  readonly notice = signal('');

  readonly canManage = () =>
    this.auth.isSuperAdmin() ||
    this.auth.hasPermission('elections.manage') ||
    this.auth.hasPermission('polling.manage');

  search = '';
  verified = '';
  form: CenterForm = this.emptyForm();

  constructor() {
    queueMicrotask(() => this.load());
  }

  load() {
    this.loading.set(true);
    this.error.set('');
    forkJoin({
      centers: this.api.getPollingCenters(this.electionId(), this.search, this.verified),
      lookups: this.api.getElectionLookups()
    }).subscribe({
      next: data => {
        this.centers.set(data.centers.items);
        this.total.set(data.centers.totalCount);
        this.lookups.set(data.lookups);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('ভোট কেন্দ্রের তথ্য লোড করা যায়নি। অনুগ্রহ করে পুনরায় চেষ্টা করুন।');
        this.loading.set(false);
      }
    });
  }

  loadCenters() {
    this.loading.set(true);
    this.api.getPollingCenters(this.electionId(), this.search, this.verified).subscribe({
      next: data => {
        this.centers.set(data.items);
        this.total.set(data.totalCount);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('ভোট কেন্দ্রের তথ্য লোড করা যায়নি।');
        this.loading.set(false);
      }
    });
  }

  toggleForm() {
    this.showForm.update(val => !val);
    this.form = this.emptyForm();
    if (this.showForm()) {
      this.form.areaId = this.lookups()?.areas[0]?.id ?? 0;
    }
  }

  validForm() {
    return (
      this.form.areaId > 0 &&
      !!this.form.code.trim() &&
      this.form.code.length <= 50 &&
      !!this.form.name.trim() &&
      this.form.name.length <= 250 &&
      this.form.address.length <= 500
    );
  }

  saveCenter() {
    if (!this.validForm() || this.saving()) return;
    this.saving.set(true);
    this.error.set('');
    this.notice.set('');

    this.api
      .addElectionCenter(this.electionId(), {
        areaId: this.form.areaId,
        code: this.form.code.trim(),
        name: this.form.name.trim(),
        address: this.form.address.trim() || null
      })
      .subscribe({
        next: () => {
          this.notice.set('ভোট কেন্দ্র সফলভাবে এন্ট্রি ও অন্তর্ভুক্ত করা হয়েছে।');
          this.saving.set(false);
          this.showForm.set(false);
          this.form = this.emptyForm();
          this.loadCenters();
        },
        error: () => {
          this.error.set('কেন্দ্র এন্ট্রি করা সম্ভব হয়নি। কেন্দ্রের কোড ও তথ্য যাচাই করুন।');
          this.saving.set(false);
        }
      });
  }

  areaName(id: number) {
    const area = this.lookups()?.areas.find(item => item.id === id);
    return area ? `${area.nameBn || area.nameEn} · ${area.code}` : `Area ${id}`;
  }

  private emptyForm(): CenterForm {
    return { areaId: 0, code: '', name: '', address: '' };
  }
}
