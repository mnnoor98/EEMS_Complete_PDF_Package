import { ChangeDetectionStrategy, Component, inject, input, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin, Observable } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CenterDetail, ChecklistSummary, PollingLookups } from '../../core/models/api.models';

@Component({
  selector: 'eems-polling-center-detail',
  imports: [DatePipe, ReactiveFormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="page-container">
      @if(error()){
        <div class="alert alert-error" role="alert">
          <span>⚠️</span> {{error()}}
        </div>
      }

      @if(loading()){
        <div class="loading-state card">
          <div class="spinner"></div>
          <p>ভোট কেন্দ্রের বিস্তারিত লোড হচ্ছে…</p>
        </div>
      } @else if(detail(); as data){
        <!-- Breadcrumb Navigation -->
        <nav class="breadcrumb">
          <a [routerLink]="['/elections', electionId(), 'centers']">← ভোট কেন্দ্র তালিকা</a>
          <span>/</span>
          <span class="code-tag">{{data.center.code}}</span>
          <span>/</span>
          <span class="current">{{data.center.name}}</span>
        </nav>

        <!-- Center Hero -->
        <section class="hero-card card">
          <div class="hero-content">
            <div class="hero-tag-row">
              <span class="center-badge">🏫 ভোট কেন্দ্র পরিচিতি</span>
              <span class="code-pill">কোড: {{data.center.code}}</span>
            </div>
            <h1 class="hero-title">{{data.center.name}}</h1>
            <p class="hero-address">
              <span class="pin">📍</span> {{data.center.address || 'ঠিকানা এন্ট্রি নেই'}}
            </p>
          </div>
          <div class="hero-actions">
            <span [class]="data.center.isVerified ? 'badge-verified' : 'badge-pending'">
              {{data.center.isVerified ? '✓ যাচাইকৃত কেন্দ্র' : '⏳ যাচাই অপেক্ষমাণ'}}
            </span>
            @if(canManage && !data.center.isVerified){
              <button type="button" class="btn-verify" (click)="verify()">
                🛡️ কেন্দ্র যাচাই নিশ্চিত করুন
              </button>
            }
          </div>
        </section>

        <!-- Stats Grid -->
        <section class="stats-grid">
          <article class="stat-card card">
            <span class="stat-icon">🗄️</span>
            <div class="stat-info">
              <b>{{data.booths.length}}</b>
              <span>মোট বুথ / ভোটকক্ষ</span>
            </div>
          </article>
          <article class="stat-card card">
            <span class="stat-icon">👤</span>
            <div class="stat-info">
              <b>{{activeAgents(data)}}</b>
              <span>সক্রিয় এজেন্ট</span>
            </div>
          </article>
          <article class="stat-card card">
            <span class="stat-icon">📋</span>
            <div class="stat-info">
              <b>{{completion(data)}}%</b>
              <span>প্রস্তুতি সম্পন্ন</span>
            </div>
          </article>
          <article class="stat-card card">
            <span class="stat-icon">📜</span>
            <div class="stat-info">
              <b>{{data.verificationHistory.length}}</b>
              <span>যাচাইকরণ অডিট</span>
            </div>
          </article>
        </section>

        <!-- Panels Layout -->
        <div class="panels-layout">
          <!-- Left: Booths Setup -->
          <section class="card panel">
            <header class="panel-header">
              <div>
                <p class="panel-eyebrow">ভোটকক্ষ বিন্যাস</p>
                <h2 class="panel-title">বুথ তালিকা (Booths Setup)</h2>
              </div>
              @if(canManage){
                <button type="button" class="btn-panel-action" (click)="showBooth.set(!showBooth())">
                  {{showBooth() ? '✕ বন্ধ করুন' : '➕ নতুন বুথ যোগ'}}
                </button>
              }
            </header>

            @if(showBooth()){
              <form [formGroup]="boothForm" (ngSubmit)="addBooth()" class="panel-form">
                <h4>নতুন বুথ এন্ট্রি</h4>
                <div class="form-row">
                  <div class="form-field">
                    <label>বুথ কোড (Booth Code) *</label>
                    <input formControlName="code" placeholder="যেমন: B-01 বা B-02" />
                  </div>
                  <div class="form-field">
                    <label>বুথ নাম / বিবরণ (Booth Name) *</label>
                    <input formControlName="name" placeholder="যেমন: পুরুষ ভোটকক্ষ ১ বা নিচতলা পূর্ব" />
                  </div>
                </div>
                <div class="form-btns">
                  <button type="button" class="btn-cancel" (click)="showBooth.set(false)">বাতিল</button>
                  <button type="submit" class="btn-save" [disabled]="boothForm.invalid || saving()">
                    {{saving() ? 'সংরক্ষণ হচ্ছে…' : '💾 বুথ সংরক্ষণ করুন'}}
                  </button>
                </div>
              </form>
            }

            <div class="booth-list">
              @for(booth of data.booths; track booth.boothId){
                <article class="booth-item">
                  <span class="booth-code">{{booth.code}}</span>
                  <div class="booth-details">
                    <b>{{booth.name}}</b>
                    <small [class.active]="booth.isActive">{{booth.isActive ? 'সক্রিয় ভোটকক্ষ' : 'নিষ্ক্রিয়'}}</small>
                  </div>
                </article>
              } @empty {
                <div class="empty-notice">
                  <span class="empty-ico">🗄️</span>
                  <p>এই কেন্দ্রে এখনও কোনো বুথ এন্ট্রি করা হয়নি। উপরের <b>"+ নতুন বুথ যোগ"</b> বাটনে চাপ দিন।</p>
                </div>
              }
            </div>
          </section>

          <!-- Right: Assigned Agents -->
          <section class="card panel">
            <header class="panel-header">
              <div>
                <p class="panel-eyebrow">নিযুক্ত ব্যক্তিবর্গ</p>
                <h2 class="panel-title">দায়িত্বপ্রাপ্ত এজেন্টগণ (Assigned Staff)</h2>
              </div>
            </header>

            <div class="agent-list">
              @for(agent of data.agents; track agent.assignmentId){
                <article class="agent-item">
                  <span class="agent-avatar">{{agent.displayName.charAt(0)}}</span>
                  <div class="agent-details">
                    <b>{{agent.displayName}}</b>
                    <small>শিফট: {{agent.startsAtUtc | date:'dd MMM, HH:mm'}} – {{agent.endsAtUtc | date:'dd MMM, HH:mm'}}</small>
                  </div>
                  <div class="agent-status-wrap">
                    <span [class.active-tag]="agent.isActive" class="status-tag">
                      {{agent.isActive ? 'দায়িত্বরত' : 'অব্যাহতি'}}
                    </span>
                    @if(agent.isActive && canManage){
                      <button type="button" class="btn-deactivate" (click)="deactivate(agent.assignmentId)">
                        বাতিল
                      </button>
                    }
                  </div>
                </article>
              } @empty {
                <div class="empty-notice">
                  <span class="empty-ico">👤</span>
                  <p>এই কেন্দ্রে কোনো এজেন্ট অ্যাসাইন করা হয়নি। ওয়ার রুম বা ওয়ার্কফোর্স থেকে এজেন্ট যুক্ত করা যাবে।</p>
                </div>
              }
            </div>
          </section>

          <!-- Readiness Checklists -->
          <section class="card panel">
            <header class="panel-header">
              <div>
                <p class="panel-eyebrow">ভোটের দিন পূর্বপ্রস্তুতি</p>
                <h2 class="panel-title">প্রস্তুতি চেকলিস্ট (Readiness Checklist)</h2>
              </div>
              @if(canManage){
                <button type="button" class="btn-panel-action" (click)="showChecklist.set(!showChecklist())">
                  {{showChecklist() ? '✕ বন্ধ করুন' : '➕ নতুন চেকলিস্ট'}}
                </button>
              }
            </header>

            @if(showChecklist()){
              <form [formGroup]="checklistForm" (ngSubmit)="createChecklist()" class="panel-form">
                <h4>নতুন চেকলিস্ট এন্ট্রি</h4>
                <div class="form-field">
                  <label>চেকলিস্টের নাম *</label>
                  <input formControlName="name" placeholder="যেমন: সকালের ব্যালট পেপার ও বাক্স যাচাই" />
                </div>
                <div class="form-field">
                  <label>প্রয়োজনীয় আইটেম তালিকা (প্রতি লাইনে ১টি করে) *</label>
                  <textarea formControlName="requirements" rows="3" placeholder="ব্যালট বাক্স সিল পরীক্ষা&#10;ভোটার তালিকার কপি উপস্থিতি&#10;অমোচনীয় কালি সরবরাহ"></textarea>
                </div>
                <div class="form-btns">
                  <button type="button" class="btn-cancel" (click)="showChecklist.set(false)">বাতিল</button>
                  <button type="submit" class="btn-save" [disabled]="checklistForm.invalid || saving()">
                    💾 চেকলিস্ট তৈরি করুন
                  </button>
                </div>
              </form>
            }

            <div class="checklists-container">
              @for(list of data.checklists; track list.checklistId){
                <article class="checklist-box">
                  <div class="check-box-head">
                    <b>{{list.name}}</b>
                    <span class="check-state">{{stateName(list.stateId)}} · v{{list.version}}</span>
                  </div>
                  @for(item of list.items; track item.itemId){
                    <label class="check-item-row">
                      <input
                        type="checkbox"
                        [checked]="item.isComplete"
                        [disabled]="item.isComplete || !canManage || saving()"
                        (change)="complete(list, item.itemId)"
                      />
                      <span [class.completed]="item.isComplete">{{item.requirement}}</span>
                    </label>
                  }
                </article>
              } @empty {
                <div class="empty-notice">
                  <p>কোনো প্রস্তুতি চেকলিস্ট তৈরি করা হয়নি।</p>
                </div>
              }
            </div>
          </section>

          <!-- Audit History -->
          <section class="card panel">
            <header class="panel-header">
              <div>
                <p class="panel-eyebrow">নিরাপত্তা ও নিরীক্ষা</p>
                <h2 class="panel-title">যাচাইকরণের ইতিহাস (Verification History)</h2>
              </div>
            </header>

            <div class="timeline">
              @for(event of data.verificationHistory; track event.verificationId){
                <article class="timeline-row">
                  <span class="timeline-dot"></span>
                  <div class="timeline-info">
                    <b>কেন্দ্র পরিদর্শন ও যাচাই নিশ্চিতকরণ</b>
                    <small>যাচাইকারী: {{event.verifiedBy}} · {{event.verifiedAtUtc | date:'dd MMM yyyy, HH:mm'}} UTC</small>
                  </div>
                </article>
              } @empty {
                <div class="empty-notice">
                  <p>এখনও কোনো আনুষ্ঠানিক যাচাইকরণ রেকর্ড হয়নি।</p>
                </div>
              }
            </div>
          </section>
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
      font-weight: 600;
    }
    .code-tag {
      background: #f1f5f9;
      color: #334155;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.78rem;
    }
    .current {
      color: #0f172a;
      font-weight: 600;
    }

    .hero-card {
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
    .hero-tag-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }
    .center-badge {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
    }
    .code-pill {
      background: rgba(255, 255, 255, 0.1);
      color: #cbd5e1;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
    }
    .hero-title {
      font-size: clamp(1.6rem, 3vw, 2.3rem);
      font-weight: 800;
      margin: 4px 0 8px;
      letter-spacing: -0.02em;
    }
    .hero-address {
      color: #94a3b8;
      margin: 0;
      font-size: 0.95rem;
    }
    .pin {
      color: #e11d48;
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .badge-verified {
      background: #ecfdf5;
      color: #059669;
      border: 1px solid #a7f3d0;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 700;
    }
    .badge-pending {
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fde68a;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 700;
    }
    .btn-verify {
      background: #0284c7;
      color: #fff;
      border: 0;
      border-radius: 10px;
      padding: 10px 18px;
      font-weight: 700;
      font-size: 0.88rem;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
    }
    .stat-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .stat-icon {
      font-size: 2rem;
      background: #f8fafc;
      width: 48px;
      height: 48px;
      display: grid;
      place-items: center;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
    }
    .stat-info b {
      font-size: 1.6rem;
      font-weight: 800;
      color: #0f172a;
      display: block;
      line-height: 1.1;
    }
    .stat-info span {
      font-size: 0.78rem;
      color: #64748b;
      font-weight: 600;
    }

    .panels-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .panel {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 22px;
    }
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 18px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 12px;
    }
    .panel-eyebrow {
      font-size: 0.72rem;
      font-weight: 800;
      color: #0284c7;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 0 0 2px;
    }
    .panel-title {
      font-size: 1.15rem;
      font-weight: 800;
      color: #0f172a;
      margin: 0;
    }
    .btn-panel-action {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      color: #334155;
      border-radius: 8px;
      padding: 6px 12px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
    }
    .btn-panel-action:hover {
      background: #f1f5f9;
    }

    .panel-form {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .panel-form h4 {
      margin: 0;
      color: #0f172a;
      font-size: 0.95rem;
    }
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .form-field {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .form-field label {
      font-size: 0.8rem;
      font-weight: 700;
      color: #475569;
    }
    .form-field input, .form-field textarea {
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 0.88rem;
      outline: none;
      background: #fff;
    }
    .form-btns {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    .btn-cancel {
      background: transparent;
      border: 1px solid #cbd5e1;
      color: #64748b;
      padding: 6px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.82rem;
      cursor: pointer;
    }
    .btn-save {
      background: #0284c7;
      border: 0;
      color: #fff;
      padding: 6px 16px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.82rem;
      cursor: pointer;
    }

    .booth-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .booth-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border: 1px solid #f1f5f9;
      border-radius: 10px;
      background: #f8fafc;
    }
    .booth-code {
      background: #e0f2fe;
      color: #0369a1;
      font-size: 0.8rem;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
    }
    .booth-details {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .booth-details b {
      color: #0f172a;
      font-size: 0.92rem;
    }
    .booth-details small {
      font-size: 0.75rem;
      color: #94a3b8;
    }
    .booth-details small.active {
      color: #059669;
    }

    .agent-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .agent-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border: 1px solid #f1f5f9;
      border-radius: 10px;
    }
    .agent-avatar {
      width: 38px;
      height: 38px;
      background: #f0fdf4;
      color: #15803d;
      font-weight: 800;
      border-radius: 50%;
      display: grid;
      place-items: center;
    }
    .agent-details {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .agent-details b {
      color: #0f172a;
      font-size: 0.92rem;
    }
    .agent-details small {
      color: #64748b;
      font-size: 0.75rem;
    }
    .agent-status-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .status-tag {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      background: #f1f5f9;
      color: #64748b;
    }
    .status-tag.active-tag {
      background: #ecfdf5;
      color: #047857;
    }
    .btn-deactivate {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      cursor: pointer;
    }

    .checklists-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .checklist-box {
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 12px;
    }
    .check-box-head {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .check-box-head b {
      color: #0f172a;
      font-size: 0.9rem;
    }
    .check-state {
      font-size: 0.72rem;
      color: #0284c7;
      font-weight: 700;
    }
    .check-item-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 5px 0;
      font-size: 0.85rem;
      cursor: pointer;
    }
    .check-item-row input {
      accent-color: #0284c7;
    }
    .check-item-row span.completed {
      text-decoration: line-through;
      color: #94a3b8;
    }

    .timeline {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .timeline-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 8px 0;
      border-bottom: 1px solid #f8fafc;
    }
    .timeline-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #0284c7;
      margin-top: 5px;
    }
    .timeline-info b {
      display: block;
      color: #0f172a;
      font-size: 0.88rem;
    }
    .timeline-info small {
      color: #64748b;
      font-size: 0.75rem;
    }

    .empty-notice {
      text-align: center;
      padding: 24px 12px;
      color: #94a3b8;
      font-size: 0.85rem;
    }
    .empty-ico {
      font-size: 1.8rem;
      display: block;
      margin-bottom: 6px;
    }

    .loading-state {
      text-align: center;
      padding: 48px;
      color: #64748b;
    }
    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #e2e8f0;
      border-top-color: #0284c7;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 12px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .alert-error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      padding: 12px 16px;
      border-radius: 10px;
      font-weight: 600;
    }

    @media (max-width: 850px) {
      .panels-layout {
        grid-template-columns: 1fr;
      }
      .stats-grid {
        grid-template-columns: 1fr 1fr;
      }
    }
  `]
})
export class PollingCenterDetailPage {
  readonly electionId = input.required<string>();
  readonly electionCenterId = input.required<string>();
  private readonly api = inject(EemsApiService);
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  readonly detail = signal<CenterDetail | null>(null);
  readonly lookups = signal<PollingLookups>({ readinessStates: [] });
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly showBooth = signal(false);
  readonly showChecklist = signal(false);

  readonly boothForm = this.fb.nonNullable.group({
    code: ['', [Validators.required, Validators.maxLength(50)]],
    name: ['', [Validators.required, Validators.maxLength(120)]]
  });

  readonly checklistForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(180)]],
    requirements: ['', Validators.required]
  });

  get canManage() {
    return (
      this.auth.isSuperAdmin() ||
      this.auth.hasPermission('polling.manage') ||
      this.auth.hasPermission('elections.manage')
    );
  }

  constructor() {
    queueMicrotask(() => this.load());
  }

  load() {
    this.loading.set(true);
    forkJoin({
      detail: this.api.getPollingCenter(this.electionId(), this.electionCenterId()),
      lookups: this.api.getPollingLookups(this.electionId())
    }).subscribe({
      next: x => {
        this.detail.set(x.detail);
        this.lookups.set(x.lookups);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('ভোট কেন্দ্রের তথ্য লোড করা যায়নি।');
        this.loading.set(false);
      }
    });
  }

  addBooth() {
    if (this.boothForm.invalid) return;
    this.save(
      this.api.addBooth(this.electionId(), this.electionCenterId(), this.boothForm.getRawValue())
    );
  }

  verify() {
    this.save(this.api.verifyCenter(this.electionId(), this.electionCenterId()));
  }

  deactivate(id: string) {
    this.save(this.api.deactivateAgent(this.electionId(), this.electionCenterId(), id));
  }

  createChecklist() {
    if (this.checklistForm.invalid) return;
    const raw = this.checklistForm.getRawValue();
    const requirements = raw.requirements
      .split(/\r?\n/)
      .map(x => x.trim())
      .filter(Boolean);
    if (!requirements.length) return;
    this.save(
      this.api.createChecklist(this.electionId(), this.electionCenterId(), {
        name: raw.name,
        requirements
      })
    );
  }

  complete(list: ChecklistSummary, itemId: string) {
    this.save(
      this.api.completeChecklistItem(this.electionId(), this.electionCenterId(), list, itemId)
    );
  }

  stateName(id: number) {
    return this.lookups().readinessStates.find(x => x.id === id)?.name ?? 'অজ্ঞাত';
  }

  activeAgents(data: CenterDetail) {
    return data.agents.filter(x => x.isActive).length;
  }

  completion(data: CenterDetail) {
    const items = data.checklists.flatMap(x => x.items);
    return items.length
      ? Math.round((items.filter(x => x.isComplete).length / items.length) * 100)
      : 0;
  }

  private save(observable: Observable<unknown>) {
    this.saving.set(true);
    this.error.set('');
    observable.subscribe({
      next: () => {
        this.saving.set(false);
        this.showBooth.set(false);
        this.showChecklist.set(false);
        this.load();
      },
      error: () => {
        this.error.set('অপারেশনটি সফল হয়নি। পুনরায় চেষ্টা করুন।');
        this.saving.set(false);
      }
    });
  }
}
