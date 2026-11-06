import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CandidateWarRoomHero, RoleSummary, UserSummary } from '../../core/models/api.models';

interface CreatedAccountInfo {
  displayName: string;
  username: string;
  password: string;
  candidateName: string;
  roleName: string;
}

@Component({
  selector: 'eems-user-creation',
  imports: [CommonModule, FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="user-creation-container">
      <div class="breadcrumb-row">
        <a class="back-link" routerLink="/administration">← অ্যাডমিনিস্ট্রেশন ড্যাশবোর্ড</a>
        <span class="sep">/</span>
        <span class="curr-page">ইউজার তৈরি ও প্রার্থী নির্ধারণ</span>
      </div>

      <!-- Header Section -->
      <section class="page-header">
        <div class="header-content">
          <div class="badge-row">
            <span class="module-chip">👥 IDENTITY & ACCESS MANAGEMENT</span>
            <span class="scope-chip">🔒 প্রার্থীর ভিত্তিতে রোল ও তথ্য আইসোলেশন</span>
          </div>
          <h1 class="page-title">ব্যবহারকারী তৈরি ও প্রার্থী স্কোপ নির্ধারণ</h1>
          <p class="page-subtitle">
            নির্বাচনী সিস্টেমের জন্য নতুন ব্যবহারকারী অ্যাকাউন্ট তৈরি করুন, তাদের নির্দিষ্ট প্রার্থীর সাথে সংযুক্ত করুন অথবা কেন্দ্রীয় সুপার অ্যাডমিন হিসেবে দায়িত্ব প্রদান করুন।
          </p>
        </div>

        <div class="header-actions">
          <button class="btn-refresh" (click)="load()">↻ রিফ্রেশ ডাটা</button>
        </div>
      </section>

      <!-- Feedback Banners -->
      @if(error()){
        <div class="alert-banner error">{{error()}} <button (click)="load()">পুনরায় চেষ্টা করুন</button></div>
      }
      @if(notice()){
        <div class="alert-banner success">
          <span>✓</span>
          <div>{{notice()}}</div>
        </div>
      }

      <!-- Top Summary Statistics -->
      <section class="stats-grid">
        <article class="card stat-card">
          <span class="stat-label">মোট ব্যবহারকারী</span>
          <b class="stat-value">{{users().length}}</b>
        </article>
        <article class="card stat-card">
          <span class="stat-label">প্রার্থীভিত্তিক একাউন্ট</span>
          <b class="stat-value highlight-teal">{{candidateAssignedCount()}}</b>
        </article>
        <article class="card stat-card">
          <span class="stat-label">সুপার অ্যাডমিন একাউন্ট</span>
          <b class="stat-value highlight-gold">{{superAdminCount()}}</b>
        </article>
        <article class="card stat-card">
          <span class="stat-label">সক্রিয় ইউজার</span>
          <b class="stat-value highlight-green">{{activeUserCount()}}</b>
        </article>
      </section>

      <!-- Account Ready Credential Box (Shown when a user is successfully created) -->
      @if(createdAccount(); as account){
        <section class="card ready-card">
          <div class="ready-badge-row">
            <span class="ready-icon">✓</span>
            <div>
              <h3>নতুন অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!</h3>
              <p>নিচের অস্থায়ী লগইন তথ্য কপি করে উক্ত ব্যবহারকারীকে নিরাপদ চ্যানেলে (WhatsApp/SMS) প্রদান করুন।</p>
            </div>
            <button class="btn-close-ready" (click)="createdAccount.set(null)">×</button>
          </div>

          <div class="ready-details-grid">
            <div class="ready-item">
              <span class="ready-label">পূর্ণ নাম:</span>
              <b class="ready-val">{{account.displayName}}</b>
            </div>
            <div class="ready-item">
              <span class="ready-label">ইউজারনেম (Login ID):</span>
              <code class="ready-code">{{account.username}}</code>
            </div>
            <div class="ready-item">
              <span class="ready-label">অস্থায়ী পাসওয়ার্ড:</span>
              <code class="ready-code password">{{account.password}}</code>
            </div>
            <div class="ready-item">
              <span class="ready-label">নির্ধারিত প্রার্থী (Scope):</span>
              <b class="ready-val cand-text">{{account.candidateName}}</b>
            </div>
            <div class="ready-item">
              <span class="ready-label">বরাদ্দকৃত রোল:</span>
              <b class="ready-val">{{account.roleName || 'ডিফল্ট অ্যাক্সেস'}}</b>
            </div>
          </div>

          <div class="ready-actions">
            <button class="btn-copy" (click)="copyCredentials(account)">
              {{copiedMessage() || '📋 ক্রেডেনশিয়াল কপি করুন (Copy Login Info)'}}
            </button>
            <button class="btn-done" (click)="createdAccount.set(null)">সম্পন্ন</button>
          </div>
        </section>
      }

      <!-- Main Layout: User Creation Form (Left) & Access Guidelines (Right) -->
      <div class="content-grid">
        <!-- User Creation Form -->
        <section class="card form-card">
          <div class="card-head">
            <div>
              <p class="eyebrow">NEW USER ONBOARDING</p>
              <h2>নতুন ব্যবহারকারী একাউন্ট ফরম</h2>
            </div>
          </div>

          <form (ngSubmit)="createUser()">
            <!-- Step 1: Identity -->
            <div class="section-divider">
              <span>১. ব্যবহারকারীর পরিচয় ও ইউজারনেম</span>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="fullName">ব্যবহারকারীর পূর্ণ নাম (Full Name) *</label>
                <input
                  id="fullName"
                  name="displayName"
                  required
                  maxlength="200"
                  [(ngModel)]="userForm.displayName"
                  placeholder="যেমন: জামাল উদ্দিন / মোঃ তারেক হাসান"
                  (input)="onNameChange()">
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="usernameInput">ইউজারনেম (Username / Login ID) *</label>
                <div class="input-with-action">
                  <input
                    id="usernameInput"
                    name="username"
                    required
                    maxlength="200"
                    autocomplete="off"
                    [(ngModel)]="userForm.username"
                    placeholder="যেমন: jamal.uddin">
                  <button type="button" class="btn-suggest" (click)="suggestUsername()" title="নাম থেকে ইউজারনেম তৈরি করুন">
                    পরামর্শ
                  </button>
                </div>
                <small class="field-hint">লগইনের জন্য ব্যবহৃত হবে এবং অনন্য (Unique) হতে হবে।</small>
              </div>

              <div class="form-group">
                <label for="emailInput">ইমেইল ঠিকানা (Email Address) <em>ঐচ্ছিক</em></label>
                <input
                  id="emailInput"
                  type="email"
                  name="email"
                  maxlength="320"
                  [(ngModel)]="userForm.email"
                  placeholder="jamal@example.com">
              </div>
            </div>

            <!-- Step 2: Candidate Binding & Role Scope -->
            <div class="section-divider">
              <span>২. প্রার্থী নির্ধারণ ও কাজের পরিধি (Candidate Scope)</span>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="candidateSelect">প্রার্থী নির্ধারণ (Candidate Scope) *</label>
                <select id="candidateSelect" name="candidateId" [ngModel]="selectedCandidateId" (ngModelChange)="onCandidateSelectChange($event)">
                  <option value="">👑 কোনো প্রার্থী নয় (Central Super User - সব প্রার্থী অ্যাক্সেস)</option>
                  @for(c of candidates(); track c.candidateId){
                    <option [value]="c.candidateId">{{c.symbolEmoji}} {{c.name}} ({{c.partyName || 'স্বতন্ত্র'}}) · {{c.positionName}}{{c.areaName ? ' [' + c.areaName + ']' : (c.electionName ? ' [' + c.electionName + ']' : '')}}</option>
                  }
                </select>

                @if(selectedCandidate(); as cand){
                  <div class="cand-preview-box">
                    <div class="cand-preview-head">
                      <span class="cand-preview-ico">{{cand.symbolEmoji || '🗳️'}}</span>
                      <div class="cand-preview-main">
                        <div class="cand-preview-title-row">
                          <b>{{cand.name}}</b>
                          <span class="cand-preview-badge">🎯 নির্বাচিত প্রার্থীর নির্বাচনী সেল</span>
                        </div>
                        <span class="cand-preview-detail">
                          {{cand.partyName || 'স্বতন্ত্র প্রার্থী'}} · {{cand.positionName}} · 📍 {{cand.areaName || cand.electionName || 'নির্বাচনী আসন'}}
                        </span>
                      </div>
                    </div>
                    <div class="cand-preview-policy">
                      <span class="icon">🔒</span>
                      <span>
                        <strong>কঠোর প্রার্থীর তথ্য আইসোলেশন:</strong> এই ব্যবহারকারী সিস্টেমে লগইন করলে শুধুমাত্র <u>{{cand.name}}</u>-এর নির্বাচনী ওয়ার রুম, বুথ এজেন্ট, ভোটার লিস্ট ও লাইভ রেজাল্ট পরিচালনা করবে। সেন্ট্রাল অ্যাডমিন বা অন্য কোনো প্রার্থীর ডাটা তার সামনে সম্পূর্ণ অদৃশ্য থাকবে।
                      </span>
                    </div>
                  </div>
                } @else {
                  <div class="super-admin-policy-box">
                    <span class="icon">👑</span>
                    <div>
                      <b>কেন্দ্রীয় সুপার অ্যাডমিন অ্যাক্সেস</b>
                      <p>এই ব্যবহারকারী সিস্টেমের সকল প্রার্থীর তথ্য, ফলাফল, নির্বাচন তালিকা এবং মাস্টার ডাটা তদারকি করতে পারবেন।</p>
                    </div>
                  </div>
                }
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="roleSelect">বরাদ্দকৃত রোল (Access Role) *</label>
                <select id="roleSelect" name="role" [(ngModel)]="selectedRoleId">
                  <option value="">-- রোল নির্বাচন করুন --</option>
                  @for(role of availableRoles(); track role.roleId){
                    <option [value]="role.roleId">{{role.name}} ({{role.code}})</option>
                  }
                </select>
                <small class="field-hint">
                  @if(selectedCandidateId){
                    প্রার্থীর নির্বাচনী কর্মী হিসেবে অ্যাক্সেস সীমাবদ্ধ ভূমিকা প্রদান করুন।
                  } @else {
                    সুপার অ্যাডমিনের জন্য পূর্ণ প্ল্যাটফর্ম ব্যবস্থাপনা ভূমিকা।
                  }
                </small>
              </div>

              <div class="form-group">
                <label for="passwordInput">প্রাথমিক পাসওয়ার্ড (Initial Password) *</label>
                <div class="input-with-action">
                  <input
                    id="passwordInput"
                    [type]="showPassword() ? 'text' : 'password'"
                    name="password"
                    required
                    minlength="12"
                    maxlength="200"
                    autocomplete="new-password"
                    [(ngModel)]="userForm.initialPassword"
                    placeholder="কমপক্ষে ১২ অক্ষর">
                  <button type="button" class="btn-gen-pwd" (click)="generatePassword()" title="শক্তিশালী পাসওয়ার্ড তৈরি করুন">
                    জেনারেট
                  </button>
                  <button type="button" class="btn-toggle-eye" (click)="showPassword.update(v => !v)" title="পাসওয়ার্ড দেখুন/লুকান">
                    {{showPassword() ? '👁️' : '👁️‍🗨️'}}
                  </button>
                </div>
                <small class="field-hint">প্রথমবার লগইন করার পর ইউজারকে পাসওয়ার্ড পরিবর্তন করতে হবে।</small>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="form-actions">
              <button type="button" class="btn-secondary" (click)="resetForm()">রিসেট করুন</button>
              <button type="submit" class="btn-primary" [disabled]="saving() || !isValidUser()">
                {{saving() ? 'অ্যাকাউন্ট তৈরি হচ্ছে…' : '✓ নতুন ব্যবহারকারী তৈরি করুন'}}
              </button>
            </div>
          </form>
        </section>

        <!-- Right Side: Candidate Scoping Explanation & Best Practices -->
        <aside class="info-column">
          <div class="card guide-card">
            <div class="guide-head">
              <span class="guide-icon">🛡️</span>
              <h3>প্রার্থীভিত্তিক অ্যাক্সেস নীতি</h3>
            </div>
            <p class="guide-desc">
              সিস্টেমের গোপনীয়তা ও নির্বাচন কমিশনের নীতি অনুযায়ী রোল ও ডাটা আইসোলেশন কাজ করে:
            </p>

            <ul class="guide-list">
              <li>
                <b>👑 কেন্দ্রীয় সুপার অ্যাডমিন:</b>
                <span>সকল প্রার্থী পর্যবেক্ষণ, নতুন প্রার্থী সংযোজন এবং কেন্দ্রীয় ফলাফল তদারকি করতে পারেন।</span>
              </li>
              <li>
                <b>🎯 প্রার্থীর নির্বাচনী সেল:</b>
                <span>নির্দিষ্ট প্রার্থীর ইউজার কেবল তার প্রার্থীর বুথ এজেন্ট, ভোটার লিস্ট, স্লিপ বিতরণ ও কেন্দ্রের রেজাল্ট দেখতে পায়। অন্য কোনো প্রার্থীর তথ্য তার সামনে দৃশ্যমান নয়।</span>
              </li>
              <li>
                <b>🔄 ডায়নামিক রি-অ্যাসাইন:</b>
                <span>নিচের টেবিল থেকে যেকোনো সময় যেকোনো ইউজারের সাথে প্রার্থীর ট্যাগ পরিবর্তন করা যায়।</span>
              </li>
            </ul>
          </div>

          <div class="card candidate-list-mini">
            <div class="mini-head">
              <h3>বর্তমান সক্রিয় প্রার্থীগণ</h3>
              <span class="mini-count">{{candidates().length}} জন</span>
            </div>
            <div class="mini-cands">
              @for(c of candidates(); track c.candidateId){
                <div class="mini-cand-item">
                  <span class="cand-ico">{{c.symbolEmoji}}</span>
                  <div>
                    <b>{{c.name}}</b>
                    <small>{{c.partyName || 'স্বতন্ত্র'}} · {{c.positionName}}</small>
                    @if(c.areaName || c.electionName){
                      <span class="mini-cand-area">📍 {{c.areaName || c.electionName}}</span>
                    }
                  </div>
                </div>
              }
            </div>
          </div>
        </aside>
      </div>

      <!-- User Directory & Inline Candidate Switcher Table -->
      <section class="card roster-section">
        <div class="roster-header">
          <div>
            <p class="eyebrow">USER DIRECTORY & CANDIDATE MAPPING</p>
            <h2>নিবন্ধিত সকল ব্যবহারকারী ও প্রার্থী সংযোগ ({{filteredUsers().length}} জন)</h2>
          </div>
          <div class="filter-controls-row">
            <select class="table-scope-filter" [value]="tableScopeFilter()" (change)="tableScopeFilter.set($any($event.target).value)">
              <option value="ALL">🌐 সকল ব্যবহারকারী ({{users().length}} জন)</option>
              <option value="SUPER_ADMIN">👑 সুপার অ্যাডমিন একাউন্ট ({{superAdminCount()}} জন)</option>
              <optgroup label="প্রার্থীভিত্তিক ইউজার তালিকা">
                @for(c of candidates(); track c.candidateId){
                  <option [value]="c.candidateId">{{c.symbolEmoji}} {{c.name}} ({{getUserCountForCandidate(c.candidateId)}} জন)</option>
                }
              </optgroup>
            </select>
            <div class="filter-box">
              <input
                type="text"
                placeholder="🔍 নাম বা ইউজারনেম দিয়ে খুঁজুন…"
                [ngModel]="searchQuery()"
                (ngModelChange)="searchQuery.set($event)">
            </div>
          </div>
        </div>

        @if(loading()){
          <div class="empty-state">ইউজার তালিকা লোড হচ্ছে…</div>
        } @else if(!filteredUsers().length){
          <div class="empty-state">
            <p>কোনো ব্যবহারকারী পাওয়া যায়নি।</p>
          </div>
        } @else {
          <div class="users-table-wrap">
            <table class="users-table">
              <thead>
                <tr>
                  <th>ব্যবহারকারী</th>
                  <th>ইউজারনেম ও ইমেইল</th>
                  <th>প্রার্থী স্কোপ (Candidate Scope)</th>
                  <th>বরাদ্দকৃত রোল</th>
                  <th>অবস্থা</th>
                  <th>অ্যাকশন</th>
                </tr>
              </thead>
              <tbody>
                @for(u of filteredUsers(); track u.userId){
                  <tr>
                    <td>
                      <div class="user-profile-cell">
                        <span class="user-avatar">{{u.displayName.charAt(0)}}</span>
                        <b>{{u.displayName}}</b>
                      </div>
                    </td>
                    <td>
                      <div class="username-cell">
                        <code>{{u.username}}</code>
                        <small>{{u.email || 'ইমেইল নেই'}}</small>
                      </div>
                    </td>
                    <td>
                      <div class="cand-selector-cell">
                        <select
                          class="inline-cand-select"
                          [value]="u.candidateId || ''"
                          (change)="onUserCandidateChange(u, $any($event.target).value)">
                          <option value="">👑 কোনো প্রার্থী নয় (Super Admin)</option>
                          @for(c of candidates(); track c.candidateId){
                            <option [value]="c.candidateId">{{c.symbolEmoji}} {{c.name}} ({{c.partyName || 'স্বতন্ত্র'}})</option>
                          }
                        </select>
                        <div class="cand-indicator">
                          @if(u.candidateName){
                            <span class="badge-cand">🏺 {{u.candidateName}}</span>
                          } @else {
                            <span class="badge-super">👑 সুপার অ্যাডমিন</span>
                          }
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="role-tags-cell">
                        @for(code of u.roleCodes; track code){
                          <span class="role-tag">{{code}}</span>
                        } @empty {
                          <span class="muted-tag">রোল নেই</span>
                        }
                        <select class="inline-role-add" (change)="onAddRoleToUser(u, $any($event.target).value); $any($event.target).value=''">
                          <option value="">+ রোল</option>
                          @for(role of roles(); track role.roleId){
                            <option [value]="role.roleId">{{role.name}}</option>
                          }
                        </select>
                      </div>
                    </td>
                    <td>
                      <span [class]="u.isActive ? 'status-pill active' : 'status-pill inactive'">
                        {{u.isActive ? 'সক্রিয়' : 'নিষ্ক্রিয়'}}
                      </span>
                    </td>
                    <td>
                      <button
                        class="btn-toggle-active"
                        [class.danger]="u.isActive"
                        (click)="toggleUserStatus(u)">
                        {{u.isActive ? 'নিষ্ক্রিয় করুন' : 'সক্রিয় করুন'}}
                      </button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        }
      </section>
    </div>
  `,
  styles: [`
    .user-creation-container { display: grid; gap: 20px; }
    .breadcrumb-row { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; }
    .back-link { color: var(--teal); text-decoration: none; }
    .sep { color: var(--muted); }
    .curr-page { color: var(--navy); }
    .page-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; margin-bottom: 6px; }
    .badge-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
    .module-chip { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; color: var(--teal); }
    .scope-chip { font-size: 0.74rem; font-weight: 700; background: #eaf8ef; color: #15803d; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 20px; }
    .page-title { margin: 0 0 6px; font-size: 1.85rem; color: var(--navy-deep); }
    .page-subtitle { margin: 0; color: var(--muted); max-width: 760px; line-height: 1.5; font-size: 0.92rem; }
    .btn-refresh { background: #fff; border: 1.5px solid var(--line); color: var(--navy); padding: 8px 14px; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .alert-banner { display: flex; align-items: center; gap: 12px; padding: 14px 18px; border-radius: 10px; font-weight: 600; font-size: 0.9rem; }
    .alert-banner.error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    .alert-banner.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .card { background: #fff; border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 6px 20px rgba(8,33,54,0.04); }
    .stat-card { padding: 18px 20px; display: grid; gap: 4px; }
    .stat-label { font-size: 0.75rem; color: var(--muted); font-weight: 700; }
    .stat-value { font-size: 1.85rem; color: var(--navy-deep); }
    .highlight-teal { color: var(--teal); }
    .highlight-gold { color: #d97706; }
    .highlight-green { color: #16a34a; }
    .ready-card { background: #f0fdf4; border: 1.5px solid #86efac; padding: 22px 24px; animation: slideDown 0.3s ease-out; }
    .ready-badge-row { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; }
    .ready-icon { width: 42px; height: 42px; border-radius: 50%; background: #22c55e; color: #fff; display: grid; place-items: center; font-size: 1.3rem; font-weight: 800; flex-shrink: 0; }
    .ready-badge-row h3 { margin: 0 0 4px; font-size: 1.25rem; color: #14532d; }
    .ready-badge-row p { margin: 0; font-size: 0.85rem; color: #166534; }
    .btn-close-ready { margin-left: auto; background: transparent; border: 0; font-size: 1.4rem; color: #166534; cursor: pointer; }
    .ready-details-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; background: #fff; border: 1px solid #bbf7d0; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
    .ready-item { display: grid; gap: 3px; }
    .ready-label { font-size: 0.7rem; color: var(--muted); font-weight: 700; text-transform: uppercase; }
    .ready-val { font-size: 0.95rem; color: var(--navy); }
    .cand-text { color: var(--teal); }
    .ready-code { font-family: monospace; font-size: 0.95rem; font-weight: 700; background: #f1f5f9; padding: 3px 6px; border-radius: 4px; color: #0f172a; word-break: break-all; }
    .ready-code.password { color: #b91c1c; background: #fee2e2; }
    .ready-actions { display: flex; gap: 12px; justify-content: flex-end; }
    .btn-copy { background: #15803d; color: #fff; border: 0; padding: 10px 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font-size: 0.88rem; }
    .btn-done { background: #fff; border: 1px solid #cbd5e1; color: var(--navy); padding: 10px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .content-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 20px; }
    .form-card { padding: 24px; }
    .card-head { margin-bottom: 18px; }
    .card-head h2 { margin: 2px 0 0; font-size: 1.3rem; color: var(--navy); }
    .section-divider { display: flex; align-items: center; margin: 20px 0 14px; }
    .section-divider span { font-size: 0.76rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--teal); background: #eaf5f7; padding: 4px 12px; border-radius: 6px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
    .form-group { display: grid; gap: 5px; }
    .form-group.wide { grid-column: 1 / -1; }
    .form-group label { font-size: 0.8rem; font-weight: 700; color: var(--navy); }
    .form-group input, .form-group select { border: 1.5px solid var(--line); border-radius: 9px; padding: 9px 12px; font-size: 0.88rem; background: #fff; color: var(--navy); outline: none; transition: border-color 0.2s; }
    .form-group input:focus, .form-group select:focus { border-color: var(--teal); }
    .input-with-action { display: flex; }
    .input-with-action input { border-top-right-radius: 0; border-bottom-right-radius: 0; flex: 1; }
    .btn-suggest, .btn-gen-pwd, .btn-toggle-eye { border: 1.5px solid var(--line); border-left: 0; background: #f1f5f9; color: var(--teal); font-weight: 700; font-size: 0.8rem; padding: 0 12px; cursor: pointer; }
    .btn-suggest:hover, .btn-gen-pwd:hover { background: #e2e8f0; }
    .btn-toggle-eye { border-top-right-radius: 9px; border-bottom-right-radius: 9px; font-size: 0.95rem; }
    .field-hint { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
    .cand-preview-box { background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 10px; padding: 14px 16px; margin-top: 8px; display: grid; gap: 10px; }
    .cand-preview-head { display: flex; align-items: center; gap: 12px; }
    .cand-preview-ico { font-size: 2.2rem; line-height: 1; flex-shrink: 0; }
    .cand-preview-main { display: grid; gap: 3px; flex: 1; }
    .cand-preview-title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .cand-preview-title-row b { font-size: 1.05rem; color: #14532d; }
    .cand-preview-badge { font-size: 0.7rem; font-weight: 800; background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 12px; border: 1px solid #bbf7d0; }
    .cand-preview-detail { font-size: 0.82rem; color: #166534; font-weight: 600; }
    .cand-preview-policy { display: flex; align-items: flex-start; gap: 8px; font-size: 0.78rem; background: #fff; border: 1px solid #bbf7d0; padding: 8px 12px; border-radius: 8px; color: #15803d; line-height: 1.4; }
    .super-admin-policy-box { display: flex; align-items: flex-start; gap: 10px; background: #fff8ed; border: 1.5px solid #fed7aa; padding: 12px 16px; border-radius: 10px; margin-top: 8px; color: #9a3412; }
    .super-admin-policy-box .icon { font-size: 1.5rem; }
    .super-admin-policy-box b { font-size: 0.92rem; display: block; margin-bottom: 2px; }
    .super-admin-policy-box p { margin: 0; font-size: 0.8rem; line-height: 1.4; }
    .filter-controls-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .table-scope-filter { border: 1.5px solid var(--line); border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; background: #fff; color: var(--navy); font-weight: 700; outline: none; }
    .scope-note { display: flex; align-items: center; gap: 8px; font-size: 0.76rem; background: #f8fafc; border: 1px solid var(--line); padding: 8px 12px; border-radius: 8px; color: #334155; margin-top: 4px; }
    .form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--line); }
    .btn-primary { background: var(--teal); color: #fff; border: 0; padding: 11px 22px; border-radius: 9px; font-weight: 800; cursor: pointer; font-size: 0.9rem; }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-secondary { background: #fff; border: 1.5px solid var(--line); color: var(--navy); padding: 11px 18px; border-radius: 9px; font-weight: 700; cursor: pointer; }
    .info-column { display: grid; gap: 20px; align-content: start; }
    .guide-card { padding: 22px; }
    .guide-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .guide-icon { font-size: 1.4rem; }
    .guide-head h3 { margin: 0; font-size: 1.05rem; color: var(--navy-deep); }
    .guide-desc { margin: 0 0 14px; font-size: 0.82rem; color: var(--muted); line-height: 1.5; }
    .guide-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
    .guide-list li { display: grid; gap: 3px; font-size: 0.82rem; border-bottom: 1px solid var(--line); padding-bottom: 10px; }
    .guide-list li b { color: var(--navy); }
    .guide-list li span { color: #475569; line-height: 1.4; }
    .candidate-list-mini { padding: 20px; }
    .mini-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .mini-head h3 { margin: 0; font-size: 0.95rem; color: var(--navy); }
    .mini-count { font-size: 0.72rem; font-weight: 800; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 12px; }
    .mini-cands { display: grid; gap: 10px; }
    .mini-cand-item { display: flex; align-items: center; gap: 12px; padding: 8px 10px; background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; }
    .cand-ico { font-size: 1.5rem; line-height: 1; }
    .mini-cand-item div { display: grid; gap: 1px; }
    .mini-cand-item b { font-size: 0.85rem; color: var(--navy); }
    .mini-cand-item small { font-size: 0.72rem; color: var(--muted); }
    .mini-cand-area { font-size: 0.7rem; color: var(--teal); font-weight: 600; margin-top: 2px; }
    .roster-section { padding: 22px 24px; margin-top: 6px; }
    .roster-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; flex-wrap: wrap; gap: 12px; }
    .roster-header h2 { margin: 2px 0 0; font-size: 1.25rem; }
    .filter-box input { border: 1.5px solid var(--line); border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; width: 260px; outline: none; }
    .filter-box input:focus { border-color: var(--teal); }
    .empty-state { text-align: center; padding: 36px 20px; color: var(--muted); }
    .users-table-wrap { overflow-x: auto; }
    .users-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .users-table th { text-align: left; padding: 11px 14px; background: #f8fafc; border-bottom: 1.5px solid var(--line); color: var(--navy); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.04em; }
    .users-table td { padding: 12px 14px; border-bottom: 1px solid var(--line); vertical-align: middle; }
    .user-profile-cell { display: flex; align-items: center; gap: 10px; }
    .user-avatar { width: 34px; height: 34px; border-radius: 50%; background: #e0f2fe; color: #0369a1; display: grid; place-items: center; font-weight: 800; font-size: 0.9rem; flex-shrink: 0; }
    .username-cell { display: grid; gap: 2px; }
    .username-cell code { font-family: monospace; font-size: 0.82rem; color: #1e293b; font-weight: 700; }
    .username-cell small { font-size: 0.72rem; color: var(--muted); }
    .cand-selector-cell { display: grid; gap: 4px; }
    .inline-cand-select { border: 1.5px solid var(--line); border-radius: 6px; padding: 5px 8px; font-size: 0.78rem; background: #fff; color: var(--navy); font-weight: 600; outline: none; }
    .badge-cand { display: inline-flex; align-items: center; gap: 4px; background: #eaf8ef; color: #15803d; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
    .badge-super { display: inline-flex; align-items: center; gap: 4px; background: #fff8ed; color: #9a3412; border: 1px solid #fed7aa; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
    .role-tags-cell { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .role-tag { background: #f1f5f9; color: #334155; padding: 3px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
    .muted-tag { font-size: 0.7rem; color: var(--muted); }
    .inline-role-add { border: 1px dashed #cbd5e1; border-radius: 6px; padding: 3px 6px; font-size: 0.7rem; background: #fff; cursor: pointer; }
    .status-pill { padding: 4px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; display: inline-block; }
    .status-pill.active { background: #dcfce7; color: #15803d; }
    .status-pill.inactive { background: #fee2e2; color: #991b1b; }
    .btn-toggle-active { border: 1px solid var(--line); background: #fff; color: var(--navy); padding: 5px 10px; border-radius: 6px; font-weight: 700; font-size: 0.74rem; cursor: pointer; }
    .btn-toggle-active.danger { color: #dc2626; border-color: #fca5a5; }
    .btn-toggle-active:hover { background: #f8fafc; }
    @media (max-width: 992px) {
      .content-grid { grid-template-columns: 1fr; }
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 640px) {
      .form-row { grid-template-columns: 1fr; }
      .stats-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class UserCreationPage {
  readonly api = inject(EemsApiService);
  readonly auth = inject(AuthService);

  readonly users = signal<UserSummary[]>([]);
  readonly roles = signal<RoleSummary[]>([]);
  readonly candidates = signal<CandidateWarRoomHero[]>([]);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly notice = signal('');
  readonly searchQuery = signal('');
  readonly showPassword = signal(false);
  readonly copiedMessage = signal('');

  private readonly router = inject(Router);

  readonly createdAccount = signal<CreatedAccountInfo | null>(null);

  userForm = {
    displayName: '',
    username: '',
    email: '',
    initialPassword: ''
  };

  selectedCandidateId = '';
  selectedRoleId = '';

  readonly selectedCandidate = computed(() => {
    const id = this.selectedCandidateId;
    if (!id) return null;
    return this.candidates().find(c => c.candidateId === id) ?? null;
  });

  readonly availableRoles = computed(() => {
    const isCand = !!this.selectedCandidateId;
    if (isCand) {
      const candRoles = this.roles().filter(r => r.code !== 'TENANT_ADMIN');
      return candRoles.length > 0 ? candRoles : this.roles();
    }
    return this.roles();
  });

  readonly tableScopeFilter = signal<string>('ALL');

  getUserCountForCandidate(candId: string): number {
    return this.users().filter(u => u.candidateId === candId).length;
  }

  readonly candidateAssignedCount = computed(() => {
    return this.users().filter(u => !!u.candidateId).length;
  });

  readonly superAdminCount = computed(() => {
    return this.users().filter(u => !u.candidateId).length;
  });

  readonly activeUserCount = computed(() => {
    return this.users().filter(u => u.isActive).length;
  });

  readonly filteredUsers = computed(() => {
    let list = this.users();
    const scope = this.tableScopeFilter();
    if (scope === 'SUPER_ADMIN') {
      list = list.filter(u => !u.candidateId);
    } else if (scope !== 'ALL') {
      list = list.filter(u => u.candidateId === scope);
    }

    const q = this.searchQuery().trim().toLowerCase();
    if (!q) return list;
    return list.filter(u =>
      u.displayName.toLowerCase().includes(q) ||
      u.username.toLowerCase().includes(q) ||
      (u.email && u.email.toLowerCase().includes(q)) ||
      (u.candidateName && u.candidateName.toLowerCase().includes(q))
    );
  });

  onCandidateSelectChange(newCandId: string) {
    this.selectedCandidateId = newCandId;
    if (newCandId) {
      const cmRole = this.roles().find(r => r.code === 'CAMPAIGN_MANAGER') || this.roles().find(r => r.code === 'FIELD_AGENT') || this.roles().find(r => r.code !== 'TENANT_ADMIN');
      if (cmRole) {
        this.selectedRoleId = cmRole.roleId;
      }
      this.tableScopeFilter.set(newCandId);
    } else {
      const adminRole = this.roles().find(r => r.code === 'TENANT_ADMIN');
      if (adminRole) {
        this.selectedRoleId = adminRole.roleId;
      }
      this.tableScopeFilter.set('ALL');
    }
  }

  constructor() {
    if (!this.auth.isSuperAdmin() && this.auth.candidateId()) {
      const electId = this.auth.candidateElectionId() || '7a2ec4ed-9aba-4707-aa49-a58b51e82713';
      void this.router.navigateByUrl(`/elections/${electId}/candidate-war-room`);
      return;
    }
    this.generatePassword();
    this.load();
  }

  load() {
    this.loading.set(true);
    this.error.set('');

    forkJoin({
      users: this.api.getUsers(),
      roles: this.api.getRoles(),
      candidates: this.api.getAllCandidates()
    }).subscribe({
      next: res => {
        this.users.set(res.users);
        this.roles.set(res.roles);
        this.candidates.set(res.candidates);

        // Pre-select CAMPAIGN_MANAGER or TENANT_ADMIN role if exists
        const defRole = res.roles.find(r => r.code === 'CAMPAIGN_MANAGER') || res.roles.find(r => r.code === 'TENANT_ADMIN') || res.roles[0];
        if (defRole && !this.selectedRoleId) {
          this.selectedRoleId = defRole.roleId;
        }

        this.loading.set(false);
      },
      error: () => {
        this.error.set('ডাটা লোড করতে সমস্যা হয়েছে। অনুগ্রহ করে পেজটি রিফ্রেশ করুন।');
        this.loading.set(false);
      }
    });
  }

  onNameChange() {
    if (!this.userForm.username) {
      this.suggestUsername();
    }
  }

  suggestUsername() {
    const base = this.userForm.displayName
      .trim()
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[^a-z0-9]+/g, '.')
      .replace(/^\.|\.$/g, '');
    this.userForm.username = base || `user.${this.users().length + 1}`;
  }

  generatePassword() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%';
    const values = crypto.getRandomValues(new Uint32Array(16));
    this.userForm.initialPassword = `Eems!${Array.from(values, x => chars[x % chars.length]).join('')}`;
    this.showPassword.set(true);
  }

  resetForm() {
    this.userForm = {
      displayName: '',
      username: '',
      email: '',
      initialPassword: ''
    };
    this.selectedCandidateId = '';
    this.generatePassword();
    this.notice.set('');
  }

  isValidUser() {
    return !!this.userForm.displayName.trim() &&
           !!this.userForm.username.trim() &&
           this.userForm.initialPassword.length >= 12;
  }

  createUser() {
    if (!this.isValidUser() || this.saving()) return;
    this.saving.set(true);
    this.error.set('');
    this.notice.set('');

    const candId = this.selectedCandidateId || null;
    const role = this.roles().find(r => r.roleId === this.selectedRoleId);
    const assignedCand = this.candidates().find(c => c.candidateId === candId);
    const candName = assignedCand ? `${assignedCand.symbolEmoji} ${assignedCand.name}` : '👑 কেন্দ্রীয় সুপার অ্যাডমিন';

    const accountData: CreatedAccountInfo = {
      displayName: this.userForm.displayName.trim(),
      username: this.userForm.username.trim(),
      password: this.userForm.initialPassword,
      candidateName: candName,
      roleName: role ? role.name : 'ডিফল্ট অ্যাক্সেস'
    };

    this.api.createUser({
      displayName: accountData.displayName,
      username: accountData.username,
      email: this.userForm.email.trim() || null,
      initialPassword: accountData.password,
      candidateId: candId
    }).pipe(
      switchMap(newUser => {
        if (role) {
          return this.api.assignRole(newUser.userId, role.roleId).pipe(
            map(() => ({ ...newUser, roleCodes: [role.code] }))
          );
        }
        return of(newUser);
      }),
      switchMap(() => this.api.getUsers())
    ).subscribe({
      next: updatedUsers => {
        this.users.set(updatedUsers);
        this.createdAccount.set(accountData);
        this.notice.set(`✓ ব্যবহারকারী '${accountData.displayName}' সফলভাবে তৈরি হয়েছে!`);
        this.saving.set(false);
        this.resetForm();
      },
      error: () => {
        this.error.set('ব্যবহারকারী তৈরি করা সম্ভব হয়নি। ইউজারনেমটি ইতিমধ্যে বিদ্যমান কিনা পরীক্ষা করুন।');
        this.saving.set(false);
      }
    });
  }

  onUserCandidateChange(user: UserSummary, newCandidateId: string) {
    const candId = newCandidateId ? newCandidateId : null;
    this.api.assignUserCandidate(user.userId, candId).pipe(
      switchMap(() => this.api.getUsers())
    ).subscribe({
      next: updatedUsers => {
        this.users.set(updatedUsers);
        this.notice.set(`✓ ব্যবহারকারী '${user.displayName}'-এর প্রার্থী স্কোপ আপডেট করা হয়েছে।`);
      },
      error: () => {
        this.error.set('প্রার্থী স্কোপ পরিবর্তন করা সম্ভব হয়নি।');
      }
    });
  }

  onAddRoleToUser(user: UserSummary, roleId: string) {
    if (!roleId) return;
    this.api.assignRole(user.userId, roleId).pipe(
      switchMap(() => this.api.getUsers())
    ).subscribe({
      next: updatedUsers => {
        this.users.set(updatedUsers);
        this.notice.set(`✓ রোল সফলভাবে প্রদান করা হয়েছে।`);
      },
      error: () => {
        this.error.set('রোল প্রদান করতে সমস্যা হয়েছে।');
      }
    });
  }

  toggleUserStatus(user: UserSummary) {
    const nextStatus = !user.isActive;
    this.api.setUserActive(user.userId, nextStatus).pipe(
      switchMap(() => this.api.getUsers())
    ).subscribe({
      next: updatedUsers => {
        this.users.set(updatedUsers);
        this.notice.set(`✓ ব্যবহারকারী '${user.displayName}' ${nextStatus ? 'সক্রিয়' : 'নিষ্ক্রিয়'} করা হয়েছে।`);
      },
      error: () => {
        this.error.set('অবস্থা পরিবর্তন করতে সমস্যা হয়েছে।');
      }
    });
  }

  copyCredentials(account: CreatedAccountInfo) {
    const text = `EEMS নির্বাচনী সিস্টেম লগইন তথ্য:\n\n` +
      `ওয়েবসাইট: http://localhost:4200\n` +
      `নাম: ${account.displayName}\n` +
      `ইউজারনেম: ${account.username}\n` +
      `অস্থায়ী পাসওয়ার্ড: ${account.password}\n` +
      `নির্ধারিত প্রার্থী: ${account.candidateName}\n` +
      `রোল: ${account.roleName}\n\n` +
      `* প্রথমবার লগইন করে পাসওয়ার্ড পরিবর্তন করে নিন।`;

    navigator.clipboard.writeText(text).then(() => {
      this.copiedMessage.set('✓ কপি করা হয়েছে! (Copied to Clipboard)');
      setTimeout(() => this.copiedMessage.set(''), 3000);
    });
  }
}
