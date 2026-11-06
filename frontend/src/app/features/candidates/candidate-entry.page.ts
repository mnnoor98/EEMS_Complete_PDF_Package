import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin, switchMap } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import { CandidateSummary, CandidateWarRoomHero, ElectionLookups, ElectionSummary, ElectionSymbolSummary } from '../../core/models/api.models';

interface CandidateEntryForm {
  candidateId?: string | null;
  name: string;
  externalReference: string;
  positionId: number;
  areaId: number;
  nominationReference: string;
  symbolId: number | null;
  partyName: string;
  slogan: string;
  phone: string;
  campaignOffice: string;
}

@Component({
  selector: 'eems-candidate-entry',
  imports: [CommonModule, FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="candidate-entry-container">
      <div class="breadcrumb-row">
        <a class="back-link" routerLink="/elections">← নির্বাচন তালিকা</a>
        <span class="sep">/</span>
        <a class="back-link" [routerLink]="['/elections', electionId(), 'candidate-war-room']">🗳️ প্রার্থী ওয়ার রুম</a>
      </div>

      <!-- Header Section -->
      <section class="page-header">
        <div class="header-content">
          <div class="badge-row">
            <span class="module-chip">👤 CANDIDATE PROFILES & REGISTRATION</span>
            @if(isEditMode()){
              <span class="mode-badge edit">✏️ তথ্য সম্পাদনা মোড (Edit Mode)</span>
            } @else {
              <span class="mode-badge new">➕ নতুন প্রার্থী নিবন্ধন (New Registration)</span>
            }
          </div>
          <h1 class="page-title">প্রার্থী তথ্য ও নির্বাচনী মার্কা এন্ট্রি</h1>
          <p class="page-subtitle">
            প্রার্থীর পূর্ণাঙ্গ পরিচিতি, নির্বাচন কমিশন নির্ধারিত প্রতীক/মার্কা বরাদ্দ, রাজনৈতিক অধিভুক্তি, নির্বাচনী ক্যাম্প ও প্রচার যোগাযোগের তথ্য এন্ট্রি ও পরিচালনা করুন।
          </p>
        </div>

        <div class="header-actions">
          <a class="btn-war-room" [routerLink]="['/elections', electionId(), 'candidate-war-room']">
            🎖️ নির্বাচনী ওয়ার রুম খুলুন →
          </a>
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

      <!-- Main Layout: Form (Left) & Real-time Live Preview (Right) -->
      <div class="content-grid">
        <!-- Form Section -->
        <section class="card form-card">
          <div class="card-head">
            <div>
              <p class="eyebrow">{{isEditMode() ? 'UPDATE CANDIDATE & CAMPAIGN' : 'NOMINATION & ELECTORAL IDENTITY'}}</p>
              <h2>{{isEditMode() ? 'প্রার্থীর তথ্য ও মার্কা আপডেট' : 'নতুন প্রার্থীর তথ্য দাখিল'}}</h2>
            </div>
            @if(isEditMode()){
              <button class="btn-cancel-edit" type="button" (click)="resetForm()">
                ✕ নতুন ফর্ম খুলুন
              </button>
            }
          </div>

          <form (ngSubmit)="saveCandidate()">
            <!-- 1. নির্বাচন ও এলাকা নির্বাচন -->
            <div class="section-divider">
              <span>১. নির্বাচন ও নির্বাচনী আসন</span>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="electionSelect">নির্বাচন (Election) *</label>
                <select id="electionSelect" [value]="electionId()" (change)="onElectionChange($any($event.target).value)">
                  @for(e of elections(); track e.electionId){
                    <option [value]="e.electionId">{{e.name}}</option>
                  }
                </select>
              </div>

              <div class="form-group">
                <label for="areaSelect">নির্বাচনী আসন / এলাকা (Constituency) *</label>
                <select id="areaSelect" [(ngModel)]="form.areaId" name="areaId" required>
                  <option [ngValue]="0">-- আসন নির্বাচন করুন --</option>
                  @for(a of lookups()?.areas ?? []; track a.id){
                    <option [ngValue]="a.id">{{a.nameEn || a.nameBn}} ({{a.code}})</option>
                  }
                </select>
              </div>
            </div>

            <!-- 2. প্রার্থীর মৌলিক তথ্য -->
            <div class="section-divider">
              <span>২. প্রার্থীর মৌলিক পরিচিতি</span>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="candidateName">প্রার্থীর পূর্ণ নাম (Candidate Full Name) *</label>
                <input
                  id="candidateName"
                  name="name"
                  required
                  maxlength="200"
                  [(ngModel)]="form.name"
                  [disabled]="isEditMode()"
                  placeholder="যেমন: জনাব মোঃ রফিকুল ইসলাম চৌধুরী">
                @if(isEditMode()){
                  <small class="field-hint">নোট: মূল নাম পরিবর্তন কেন্দ্রীয় অ্যাডমিন বা নির্বাচন কমিশন থেকে অনুমোদিত হতে হয়।</small>
                }
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="positionSelect">প্রতিদ্বন্দ্বিতা করার পদ (Contesting Position) *</label>
                <select id="positionSelect" [(ngModel)]="form.positionId" name="positionId" required [disabled]="isEditMode()">
                  <option [ngValue]="0">-- পদ নির্বাচন করুন --</option>
                  @for(p of positions(); track p.id){
                    <option [ngValue]="p.id">{{p.name}} ({{p.code}})</option>
                  }
                </select>
              </div>

              <div class="form-group">
                <label for="partyName">দলীয় অধিভুক্তি / রাজনৈতিক দল (Party Affiliation)</label>
                <input
                  id="partyName"
                  name="partyName"
                  maxlength="150"
                  [(ngModel)]="form.partyName"
                  placeholder="যেমন: স্বতন্ত্র প্রার্থী / বাংলাদেশ আওয়ামী লীগ / বিএনপি">
              </div>
            </div>

            <!-- 3. প্রতীক ও নির্বাচনী পরিচয় -->
            <div class="section-divider">
              <span>৩. প্রতীক ও নির্বাচনী মার্কা (Electoral Symbol)</span>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="symbolSelect">নির্বাচন কমিশনের প্রতীক / মার্কা বরাদ্দ *</label>
                <select id="symbolSelect" [(ngModel)]="form.symbolId" name="symbolId">
                  <option [ngValue]="null">-- প্রতীক এখনও বরাদ্দ হয়নি (Pending Allocation) --</option>
                  @for(s of symbols(); track s.id){
                    <option [ngValue]="s.id">{{s.iconEmoji}} {{s.nameBn}} ({{s.nameEn}}) · [{{s.category}}]</option>
                  }
                </select>
                <small class="field-hint">নির্বাচন কমিশন (EC) কর্তৃক গেজেটভুক্ত মার্কা নির্বাচন করুন।</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="candidateSlogan">নির্বাচনী স্লোগান (Campaign Slogan)</label>
                <input
                  id="candidateSlogan"
                  name="slogan"
                  maxlength="300"
                  [(ngModel)]="form.slogan"
                  placeholder="যেমন: উন্নয়ন, সুশাসন ও জনগণের ক্ষমতায়নে আমাদের অঙ্গীকার">
              </div>
            </div>

            <!-- 4. যোগাযোগ ও ক্যাম্প অফিস -->
            <div class="section-divider">
              <span>৪. প্রচারণা ক্যাম্প ও যোগাযোগের তথ্য</span>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="campaignPhone">অফিসিয়াল ফোন / হেল্পলাইন নম্বর</label>
                <input
                  id="campaignPhone"
                  name="phone"
                  maxlength="30"
                  [(ngModel)]="form.phone"
                  placeholder="যেমন: 01711223344">
              </div>

              <div class="form-group">
                <label for="externalRef">জাতীয় পরিচয়পত্র / রেফারেন্স (NID)</label>
                <input
                  id="externalRef"
                  name="externalReference"
                  maxlength="100"
                  [(ngModel)]="form.externalReference"
                  [disabled]="isEditMode()"
                  placeholder="যেমন: NID-1985269123456789">
              </div>
            </div>

            <div class="form-row">
              <div class="form-group wide">
                <label for="campaignOffice">কেন্দ্রীয় নির্বাচনী ক্যাম্প / প্রধান কার্যালয়</label>
                <textarea
                  id="campaignOffice"
                  name="campaignOffice"
                  rows="2"
                  maxlength="300"
                  [(ngModel)]="form.campaignOffice"
                  placeholder="যেমন: দোহার কেন্দ্রীয় নির্বাচনী ক্যাম্প, থানা রোড, ঢাকা"></textarea>
              </div>
            </div>

            <div class="form-row" *ngIf="!isEditMode()">
              <div class="form-group wide">
                <label for="nominationRef">ইসি মনোনয়নপত্র নম্বর (Nomination Reference)</label>
                <input
                  id="nominationRef"
                  name="nominationReference"
                  maxlength="120"
                  [(ngModel)]="form.nominationReference"
                  placeholder="যেমন: EC-NOM-2026-DHK01">
              </div>
            </div>

            <!-- Form Actions -->
            <div class="form-actions">
              <button type="button" class="btn-secondary" (click)="resetForm()">রিসেট করুন</button>
              <button type="submit" class="btn-primary" [disabled]="saving() || !isValidForm()">
                {{saving() ? 'সংরক্ষণ হচ্ছে…' : (isEditMode() ? '💾 তথ্য আপডেট করুন' : '✓ নতুন প্রার্থী হিসেবে দাখিল করুন')}}
              </button>
            </div>
          </form>
        </section>

        <!-- Right Column: Real-Time Live Preview & Symbol Display -->
        <aside class="preview-column">
          <!-- Real-Time Candidate Card Preview -->
          <div class="card preview-card">
            <div class="preview-badge-bar">
              <span class="preview-tag">🔴 লাইভ প্রিভিউ কার্ড (LIVE PREVIEW)</span>
              <span class="status-chip">সক্রিয় প্রার্থী</span>
            </div>

            <div class="preview-symbol-box">
              <span class="big-symbol">{{selectedSymbol()?.iconEmoji || '🗳️'}}</span>
              <div class="symbol-meta">
                <span class="symbol-caption">বরাদ্দকৃত মার্কা:</span>
                <b class="symbol-title">{{selectedSymbol()?.nameBn || selectedSymbol()?.nameEn || 'মার্কা নির্ধারিত হয়নি'}}</b>
                <span class="symbol-category">{{selectedSymbol()?.category || 'নির্বাচন কমিশন গেজেট'}}</span>
              </div>
            </div>

            <div class="preview-details">
              <h3 class="preview-candidate-name">{{form.name.trim() || 'প্রার্থীর নাম এখানে দেখা যাবে'}}</h3>
              <p class="preview-position">
                {{selectedPositionName()}} · {{selectedAreaName()}}
              </p>
              <div class="preview-party-badge">
                {{form.partyName.trim() || 'স্বতন্ত্র প্রার্থী (Independent)'}}
              </div>

              @if(form.slogan.trim()){
                <blockquote class="preview-slogan">
                  "{{form.slogan.trim()}}"
                </blockquote>
              }

              <div class="preview-contacts">
                <div class="contact-item">
                  <span class="icon">📞</span>
                  <span>{{form.phone.trim() || 'ফোন নম্বর প্রদান করা হয়নি'}}</span>
                </div>
                <div class="contact-item">
                  <span class="icon">🏢</span>
                  <span>{{form.campaignOffice.trim() || 'ক্যাম্প কার্যালয় ঠিকানা দেওয়া হয়নি'}}</span>
                </div>
                @if(form.externalReference.trim()){
                  <div class="contact-item">
                    <span class="icon">🪪</span>
                    <span>NID: {{form.externalReference.trim()}}</span>
                  </div>
                }
              </div>

              <div class="preview-footer-action">
                @if(isEditMode() && form.candidateId){
                  <a class="btn-war-room-preview" [routerLink]="['/elections', electionId(), 'candidate-war-room']">
                    🗳️ প্রার্থীর ওয়ার রুম খুলুন
                  </a>
                } @else {
                  <span class="preview-note">ফর্মটি সংরক্ষণ করার পর সরাসরি এই প্রার্থীর ওয়ার রুম তৈরি হয়ে যাবে।</span>
                }
              </div>
            </div>
          </div>

          <!-- Quick Symbol Palette / Grid -->
          <div class="card symbol-palette-card">
            <div class="palette-head">
              <h3>জনপ্রিয় নির্বাচনী প্রতীকসমূহ</h3>
              <span>মোট {{symbols().length}} টি মার্কা</span>
            </div>
            <p class="palette-desc">যেকোনো প্রতীকে ক্লিক করে সরাসরি ফর্মে নির্বাচন করুন:</p>

            <div class="palette-grid">
              @for(s of popularSymbols(); track s.id){
                <button
                  type="button"
                  class="symbol-tile"
                  [class.selected]="form.symbolId === s.id"
                  (click)="form.symbolId = s.id">
                  <span class="tile-emoji">{{s.iconEmoji}}</span>
                  <span class="tile-name">{{s.nameBn}}</span>
                </button>
              }
            </div>
          </div>
        </aside>
      </div>

      <!-- Registered Candidates Directory -->
      <section class="card roster-section">
        <div class="roster-header">
          <div>
            <p class="eyebrow">ACTIVE CONTESTING ROSTER</p>
            <h2>{{selectedRosterFilter() === 'ALL' ? 'সকল নির্বাচনের প্রার্থী তালিকা (সিস্টেমের মোট প্রার্থী)' : 'এই নির্বাচনের বর্তমান প্রার্থী তালিকা'}}</h2>
          </div>
          <div class="roster-actions">
            <select class="roster-filter-select" [value]="selectedRosterFilter()" (change)="onRosterFilterChange($any($event.target).value)">
              <option value="ALL">🌐 সকল নির্বাচন (All Candidates - {{allCandidates().length}} জন)</option>
              @for(e of elections(); track e.electionId){
                <option [value]="e.electionId">📍 {{e.name}}</option>
              }
            </select>
            <span class="count-tag">{{displayedCandidates().length}} জন প্রার্থী</span>
          </div>
        </div>

        @if(loading()){
          <div class="empty-state">তথ্য লোড হচ্ছে…</div>
        } @else if(!displayedCandidates().length){
          <div class="empty-state">
            <p>এই ফিল্টারে কোনো প্রার্থী দাখিল করা হয়নি। ওপরের ফর্মটি পূরণ করে প্রার্থী নিবন্ধন করুন।</p>
          </div>
        } @else {
          <div class="candidates-table-wrap">
            <table class="candidates-table">
              <thead>
                <tr>
                  <th>প্রতীক</th>
                  <th>প্রার্থীর নাম ও দল</th>
                  <th>প্রতিদ্বন্দ্বিতা পদ ও আসন</th>
                  <th>স্লোগান</th>
                  <th>যোগাযোগ ও অফিস</th>
                  <th>অ্যাকশন</th>
                </tr>
              </thead>
              <tbody>
                @for(c of displayedCandidates(); track c.candidateId){
                  <tr [class.highlighted]="form.candidateId === c.candidateId">
                    <td class="symbol-cell">
                      <div class="table-symbol-avatar">
                        <span class="symbol-ico">{{c.symbolEmoji || '🗳️'}}</span>
                        <small>{{c.symbolNameBn || 'মার্কা'}}</small>
                      </div>
                    </td>
                    <td>
                      <div class="candidate-main-info">
                        <b class="cand-name">{{c.name}}</b>
                        <span class="party-label">{{c.partyName || 'স্বতন্ত্র প্রার্থী'}}</span>
                      </div>
                    </td>
                    <td>
                      <div class="position-info">
                        <b>{{c.positionName}}</b>
                        <small>{{c.areaName || selectedAreaName()}}</small>
                        @if(c.electionName){
                          <span class="table-election-tag">📍 {{c.electionName}}</span>
                        }
                      </div>
                    </td>
                    <td>
                      @if(c.slogan){
                        <span class="slogan-preview" title="{{c.slogan}}">"{{c.slogan}}"</span>
                      } @else {
                        <span class="muted-text">—</span>
                      }
                    </td>
                    <td>
                      <div class="contact-mini">
                        @if(c.phone){
                          <div>📞 {{c.phone}}</div>
                        }
                        @if(c.campaignOffice){
                          <small title="{{c.campaignOffice}}">🏢 {{c.campaignOffice}}</small>
                        }
                        @if(!c.phone && !c.campaignOffice){
                          <span class="muted-text">—</span>
                        }
                      </div>
                    </td>
                    <td class="actions-cell">
                      <button class="btn-table-edit" (click)="editCandidate(c)" title="সম্পাদনা করুন">
                        ✏️ তথ্য এডিট
                      </button>
                      <a class="btn-table-wr" [routerLink]="['/elections', c.electionId || electionId(), 'candidate-war-room']" (click)="auth.setActiveCandidate(c.candidateId)" title="ওয়ার রুম খুলুন">
                        🎖️ ওয়ার রুম
                      </a>
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
    .candidate-entry-container { display: grid; gap: 20px; }
    .breadcrumb-row { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; }
    .back-link { color: var(--teal); text-decoration: none; }
    .sep { color: var(--muted); }
    .page-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; margin-bottom: 6px; }
    .badge-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .module-chip { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; color: var(--teal); }
    .mode-badge { font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
    .mode-badge.new { background: #e6f6f2; color: #10665e; border: 1px solid #9ddac9; }
    .mode-badge.edit { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .page-title { margin: 0 0 6px; font-size: 1.85rem; color: var(--navy-deep); }
    .page-subtitle { margin: 0; color: var(--muted); max-width: 760px; line-height: 1.5; font-size: 0.92rem; }
    .btn-war-room { background: #0f172a; color: #38bdf8; border: 1px solid #1e293b; padding: 11px 18px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 0.88rem; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px rgba(15,23,42,0.18); }
    .btn-war-room:hover { background: #1e293b; color: #7dd3fc; }
    .alert-banner { display: flex; align-items: center; gap: 12px; padding: 14px 18px; border-radius: 10px; font-weight: 600; font-size: 0.9rem; }
    .alert-banner.error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    .alert-banner.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .content-grid { display: grid; grid-template-columns: 1.35fr 1fr; gap: 20px; }
    .card { background: #fff; border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 6px 20px rgba(8,33,54,0.04); }
    .form-card { padding: 24px; }
    .card-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px; }
    .card-head h2 { margin: 2px 0 0; font-size: 1.3rem; color: var(--navy); }
    .btn-cancel-edit { background: #f1f5f9; border: 1px solid #cbd5e1; color: #475569; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 0.78rem; cursor: pointer; }
    .section-divider { display: flex; align-items: center; margin: 20px 0 14px; }
    .section-divider span { font-size: 0.76rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--teal); background: #eaf5f7; padding: 4px 12px; border-radius: 6px; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
    .form-group { display: grid; gap: 5px; }
    .form-group.wide { grid-column: 1 / -1; }
    .form-group label { font-size: 0.8rem; font-weight: 700; color: var(--navy); }
    .form-group input, .form-group select, .form-group textarea { border: 1.5px solid var(--line); border-radius: 9px; padding: 9px 12px; font-size: 0.88rem; background: #fff; color: var(--navy); outline: none; transition: border-color 0.2s; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--teal); }
    .field-hint { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }
    .form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--line); }
    .btn-primary { background: var(--teal); color: #fff; border: 0; padding: 11px 22px; border-radius: 9px; font-weight: 800; cursor: pointer; font-size: 0.9rem; }
    .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
    .btn-secondary { background: #fff; border: 1.5px solid var(--line); color: var(--navy); padding: 11px 18px; border-radius: 9px; font-weight: 700; cursor: pointer; }
    .preview-column { display: grid; gap: 20px; align-content: start; }
    .preview-card { padding: 22px; border-top: 4px solid var(--teal); background: linear-gradient(180deg, #fafcfd, #fff); }
    .preview-badge-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .preview-tag { font-size: 0.7rem; font-weight: 800; color: #dc2626; letter-spacing: 0.05em; }
    .status-chip { background: #eaf8ef; color: #15803d; border: 1px solid #bbf7d0; padding: 3px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; }
    .preview-symbol-box { display: flex; align-items: center; gap: 16px; background: linear-gradient(135deg, #0f273f, #1e3a5f); color: #fff; padding: 18px 20px; border-radius: 12px; margin-bottom: 16px; }
    .big-symbol { font-size: 3rem; line-height: 1; }
    .symbol-meta { display: grid; gap: 2px; }
    .symbol-caption { font-size: 0.68rem; text-transform: uppercase; color: #7dd3fc; font-weight: 700; letter-spacing: 0.04em; }
    .symbol-title { font-size: 1.35rem; color: #fff; }
    .symbol-category { font-size: 0.72rem; color: #94a3b8; }
    .preview-details { display: grid; gap: 8px; }
    .preview-candidate-name { margin: 0; font-size: 1.45rem; color: var(--navy-deep); }
    .preview-position { margin: 0; color: var(--muted); font-size: 0.85rem; }
    .preview-party-badge { display: inline-block; align-self: start; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin: 4px 0 6px; }
    .preview-slogan { margin: 6px 0; padding: 10px 14px; background: #f8fafc; border-left: 3px solid var(--teal); border-radius: 0 8px 8px 0; font-style: italic; color: #334155; font-size: 0.85rem; line-height: 1.4; }
    .preview-contacts { display: grid; gap: 6px; padding: 12px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); margin: 6px 0; font-size: 0.82rem; }
    .contact-item { display: flex; align-items: center; gap: 8px; color: #334155; }
    .contact-item .icon { font-size: 0.95rem; }
    .preview-footer-action { margin-top: 8px; }
    .btn-war-room-preview { display: block; text-align: center; background: #0f172a; color: #38bdf8; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 0.85rem; }
    .preview-note { font-size: 0.74rem; color: var(--muted); text-align: center; display: block; }
    .symbol-palette-card { padding: 18px 20px; }
    .palette-head { display: flex; justify-content: space-between; align-items: baseline; }
    .palette-head h3 { margin: 0; font-size: 0.95rem; color: var(--navy); }
    .palette-head span { font-size: 0.72rem; color: var(--muted); }
    .palette-desc { margin: 4px 0 12px; font-size: 0.78rem; color: var(--muted); }
    .palette-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .symbol-tile { background: #f8fafc; border: 1.5px solid var(--line); border-radius: 10px; padding: 8px 4px; display: grid; place-items: center; gap: 3px; cursor: pointer; transition: all 0.15s; }
    .symbol-tile:hover { background: #edf7f9; border-color: var(--teal); }
    .symbol-tile.selected { background: #e0f2fe; border-color: #0284c7; box-shadow: 0 0 0 2px rgba(2,132,199,0.2); }
    .tile-emoji { font-size: 1.4rem; line-height: 1; }
    .tile-name { font-size: 0.68rem; font-weight: 700; color: #1e293b; text-align: center; }
    .roster-section { padding: 22px 24px; margin-top: 6px; }
    .roster-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
    .roster-header h2 { margin: 2px 0 0; font-size: 1.25rem; }
    .count-tag { font-size: 0.78rem; background: #f1f5f9; padding: 4px 10px; border-radius: 12px; font-weight: 700; color: #475569; }
    .empty-state { text-align: center; padding: 36px 20px; color: var(--muted); }
    .candidates-table-wrap { overflow-x: auto; }
    .candidates-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .candidates-table th { text-align: left; padding: 11px 14px; background: #f8fafc; border-bottom: 1.5px solid var(--line); color: var(--navy); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.04em; }
    .candidates-table td { padding: 13px 14px; border-bottom: 1px solid var(--line); vertical-align: middle; }
    .candidates-table tr.highlighted { background: #f0fdfa; }
    .symbol-cell { width: 70px; }
    .table-symbol-avatar { display: grid; place-items: center; width: 48px; height: 48px; background: #f1f5f9; border-radius: 10px; border: 1px solid var(--line); }
    .table-symbol-avatar .symbol-ico { font-size: 1.4rem; line-height: 1; }
    .table-symbol-avatar small { font-size: 0.6rem; color: var(--muted); font-weight: 700; }
    .candidate-main-info { display: grid; gap: 3px; }
    .cand-name { font-size: 0.95rem; color: var(--navy-deep); }
    .party-label { font-size: 0.74rem; color: var(--teal); font-weight: 600; }
    .position-info { display: grid; gap: 2px; }
    .position-info small { color: var(--muted); font-size: 0.74rem; }
    .slogan-preview { font-size: 0.8rem; font-style: italic; color: #475569; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .contact-mini { font-size: 0.76rem; display: grid; gap: 2px; color: #475569; }
    .muted-text { color: var(--muted); }
    .actions-cell { white-space: nowrap; }
    .btn-table-edit { background: #f8fafc; border: 1px solid #cbd5e1; color: var(--navy); padding: 6px 10px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer; margin-right: 6px; }
    .btn-table-edit:hover { background: #e2e8f0; }
    .btn-table-wr { background: #0f172a; color: #38bdf8; border: 1px solid #1e293b; padding: 6px 10px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; text-decoration: none; display: inline-block; }
    .table-election-tag { font-size: 0.7rem; color: var(--teal); background: #eaf5f7; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 3px; font-weight: 600; }
    .roster-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .roster-filter-select { border: 1.5px solid var(--line); border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; background: #fff; color: var(--navy); font-weight: 700; outline: none; }
    @media (max-width: 992px) {
      .content-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 640px) {
      .form-row { grid-template-columns: 1fr; }
      .palette-grid { grid-template-columns: repeat(3, 1fr); }
    }
  `]
})
export class CandidateEntryPage {
  readonly api = inject(EemsApiService);
  readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly electionId = signal<string>(
    this.route.snapshot.paramMap.get('electionId') || '7a2ec4ed-9aba-4707-aa49-a58b51e82713'
  );

  readonly elections = signal<ElectionSummary[]>([]);
  readonly candidates = signal<CandidateWarRoomHero[]>([]);
  readonly allCandidates = signal<CandidateWarRoomHero[]>([]);
  readonly selectedRosterFilter = signal<string>('ALL');
  readonly symbols = signal<ElectionSymbolSummary[]>([]);
  readonly lookups = signal<ElectionLookups | null>(null);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly notice = signal('');

  readonly isEditMode = computed(() => !!this.form.candidateId);

  readonly displayedCandidates = computed(() => {
    const filter = this.selectedRosterFilter();
    if (filter === 'ALL') {
      return this.allCandidates();
    }
    return this.allCandidates().filter(c => c.electionId === filter);
  });

  form: CandidateEntryForm = this.emptyForm();

  readonly positions = computed(() => {
    const currentElection = this.elections().find(e => e.electionId === this.electionId());
    const typeId = currentElection?.electionTypeId;
    if (!typeId) return this.lookups()?.positions ?? [];
    return (this.lookups()?.positions ?? []).filter(p => p.electionTypeId === typeId);
  });

  readonly selectedSymbol = computed(() => {
    if (!this.form.symbolId) return null;
    return this.symbols().find(s => s.id === this.form.symbolId) ?? null;
  });

  readonly selectedPositionName = computed(() => {
    if (!this.form.positionId) return 'পদবি নির্বাচন করুন';
    const pos = this.lookups()?.positions.find(p => p.id === this.form.positionId);
    return pos?.name || `Position ${this.form.positionId}`;
  });

  readonly selectedAreaName = computed(() => {
    if (!this.form.areaId) return 'আসন নির্বাচন করুন';
    const area = this.lookups()?.areas.find(a => a.id === this.form.areaId);
    return area ? (area.nameEn || area.nameBn) : `Area ${this.form.areaId}`;
  });

  readonly popularSymbols = computed(() => {
    return this.symbols().slice(0, 12);
  });

  constructor() {
    if (!this.auth.isSuperAdmin() && this.auth.candidateId()) {
      const electId = this.auth.candidateElectionId() || '7a2ec4ed-9aba-4707-aa49-a58b51e82713';
      void this.router.navigateByUrl(`/elections/${electId}/candidate-war-room`);
      return;
    }
    this.load();
  }

  emptyForm(): CandidateEntryForm {
    return {
      candidateId: null,
      name: '',
      externalReference: '',
      positionId: 0,
      areaId: 0,
      nominationReference: '',
      symbolId: 14, // Default to Pitcher (কলস)
      partyName: '',
      slogan: '',
      phone: '',
      campaignOffice: ''
    };
  }

  load() {
    this.loading.set(true);
    this.error.set('');

    forkJoin({
      elections: this.api.getElections(),
      candidates: this.api.getCandidatesForElection(this.electionId()),
      allCandidates: this.api.getAllCandidates(),
      symbols: this.api.getElectionSymbols(),
      lookups: this.api.getElectionLookups()
    }).subscribe({
      next: res => {
        this.elections.set(res.elections);
        this.candidates.set(res.candidates);
        this.allCandidates.set(res.allCandidates);
        this.symbols.set(res.symbols);
        this.lookups.set(res.lookups);

        const currentElection = res.elections.find(e => e.electionId === this.electionId());
        if (currentElection && !this.form.areaId) {
          this.form.areaId = currentElection.areaId;
        }
        if (this.positions().length > 0 && !this.form.positionId) {
          this.form.positionId = this.positions()[0].id;
        }

        this.loading.set(false);
      },
      error: () => {
        this.error.set('তথ্য লোড করতে সমস্যা হয়েছে। অনুগ্রহ করে পেজটি রিফ্রেশ করুন।');
        this.loading.set(false);
      }
    });
  }

  onRosterFilterChange(newFilter: string) {
    this.selectedRosterFilter.set(newFilter);
  }

  onElectionChange(newElectionId: string) {
    if (!newElectionId || newElectionId === this.electionId()) return;
    this.electionId.set(newElectionId);
    this.load();
  }

  editCandidate(c: CandidateWarRoomHero) {
    const matchedPos = this.positions().find(p => p.name === c.positionName) || this.positions()[0];
    const matchedArea = this.lookups()?.areas.find(a => a.id === c.areaId) || this.lookups()?.areas[0];
    this.form = {
      candidateId: c.candidateId,
      name: c.name,
      externalReference: '',
      positionId: matchedPos?.id ?? (this.positions()[0]?.id ?? 0),
      areaId: c.areaId ?? matchedArea?.id ?? (this.lookups()?.areas[0]?.id ?? 0),
      nominationReference: '',
      symbolId: c.symbolId,
      partyName: c.partyName || '',
      slogan: c.slogan || '',
      phone: c.phone || '',
      campaignOffice: c.campaignOffice || ''
    };
    window.scrollTo({ top: 120, behavior: 'smooth' });
  }

  resetForm(keepNotice = false) {
    this.form = this.emptyForm();
    const currentElection = this.elections().find(e => e.electionId === this.electionId());
    if (currentElection) {
      this.form.areaId = currentElection.areaId;
    }
    if (this.positions().length > 0) {
      this.form.positionId = this.positions()[0].id;
    }
    if (!keepNotice) {
      this.notice.set('');
    }
  }

  isValidForm() {
    return !!this.form.name.trim() &&
           this.form.name.trim().length <= 200 &&
           this.form.positionId > 0 &&
           this.form.areaId > 0;
  }

  saveCandidate() {
    if (!this.isValidForm() || this.saving()) return;
    this.saving.set(true);
    this.error.set('');
    this.notice.set('');

    const elId = this.electionId();

    if (this.isEditMode() && this.form.candidateId) {
      // 1. Update Existing Candidate Campaign
      this.api.updateCandidateCampaign(elId, this.form.candidateId, {
        symbolId: this.form.symbolId,
        partyName: this.form.partyName.trim() || null,
        slogan: this.form.slogan.trim() || null,
        phone: this.form.phone.trim() || null,
        campaignOffice: this.form.campaignOffice.trim() || null
      }).pipe(
        switchMap(() => this.api.getCandidatesForElection(elId))
      ).subscribe({
        next: updatedList => {
          this.candidates.set(updatedList);
          this.notice.set('✓ প্রার্থীর নির্বাচনী তথ্য ও মার্কা সফলভাবে আপডেট করা হয়েছে।');
          this.saving.set(false);
          this.resetForm(true);
        },
        error: () => {
          this.error.set('প্রার্থীর তথ্য আপডেট করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।');
          this.saving.set(false);
        }
      });
    } else {
      // 2. Register New Candidate Nomination
      this.api.addCandidate(elId, {
        name: this.form.name.trim(),
        externalReference: this.form.externalReference.trim() || null,
        positionId: this.form.positionId,
        areaId: this.form.areaId,
        nominationReference: this.form.nominationReference.trim() || null,
        symbolId: this.form.symbolId,
        partyName: this.form.partyName.trim() || null,
        slogan: this.form.slogan.trim() || null
      }).pipe(
        switchMap(newCand => {
          if (this.form.phone.trim() || this.form.campaignOffice.trim()) {
            return this.api.updateCandidateCampaign(elId, newCand.candidateId, {
              symbolId: this.form.symbolId,
              partyName: this.form.partyName.trim() || null,
              slogan: this.form.slogan.trim() || null,
              phone: this.form.phone.trim() || null,
              campaignOffice: this.form.campaignOffice.trim() || null
            }).pipe(switchMap(() => this.api.getCandidatesForElection(elId)));
          }
          return this.api.getCandidatesForElection(elId);
        })
      ).subscribe({
        next: updatedList => {
          this.candidates.set(updatedList);
          this.notice.set('✓ নতুন প্রার্থী ও নির্বাচনী প্রতীক সফলভাবে নিবন্ধন করা হয়েছে!');
          this.saving.set(false);
          this.resetForm(true);
        },
        error: () => {
          this.error.set('নতুন প্রার্থী নিবন্ধন করতে ব্যর্থ হয়েছে। অনুগ্রহ করে ইনপুট চেক করুন।');
          this.saving.set(false);
        }
      });
    }
  }
}
