import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { EemsApiService } from '../../core/api/eems-api.service';
import { AuthService } from '../../core/auth/auth.service';

export interface MasterCandidateCard {
  candidateId: string;
  electionId: string;
  electionName: string;
  candidateName: string;
  symbolName: string;
  symbolEmoji: string;
  partyName: string;
  slogan: string;
  phone: string | null;
  campaignOffice: string | null;
  primaryUsername: string | null;
  primaryDisplayName: string | null;
  teamCount: number;
  agentCount: number;
  voterCount: number;
  slipsIssuedCount: number;
  slipPercentage: number;
  totalVotes: number;
}

@Component({
  standalone: true,
  selector: 'app-master-candidates',
  imports: [CommonModule, FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="master-hub-container">
      <!-- HEADER -->
      <header class="hub-header">
        <div class="header-titles">
          <div class="badge-row">
            <span class="hub-badge">👑 সুপার অ্যাডমিন কন্ট্রোল প্যানেল</span>
            <span class="live-pulse-badge"><span class="pulse-dot"></span> লাইভ ডাটা সিঙ্ক</span>
          </div>
          <h1>মাস্টার প্রার্থী তদারকি ও নিয়ন্ত্রণ হাব</h1>
          <p>সকল প্রার্থীর নির্বাচনী ক্যাম্পেইন, সাব-ইউজার টিম, পোলিং এজেন্ট ও লাইভ ভোট অগ্রগতির এক নজরে কেন্দ্রীয় দৃশ্যপট</p>
        </div>
        <div class="header-actions">
          <button class="btn-primary" routerLink="/candidates/entry">
            <span>➕</span> নতুন মাস্টার প্রার্থী এন্ট্রি
          </button>
          <button class="btn-secondary" routerLink="/administration/users">
            <span>👤</span> ইউজার ম্যানেজমেন্ট
          </button>
          <button class="btn-icon" (click)="loadOverview()" [disabled]="loading()" title="রিফ্রেশ করুন">
            🔄
          </button>
        </div>
      </header>

      <!-- KPI METRIC ROLLUPS -->
      <section class="kpi-grid">
        <div class="kpi-card gold">
          <div class="kpi-icon">🏆</div>
          <div class="kpi-info">
            <span class="kpi-label">মোট মাস্টার প্রার্থী</span>
            <span class="kpi-value">{{ totalCandidates() }}</span>
            <span class="kpi-sub">সক্রিয় প্রতিদ্বন্দ্বী প্রার্থী</span>
          </div>
        </div>

        <div class="kpi-card blue">
          <div class="kpi-icon">👥</div>
          <div class="kpi-info">
            <span class="kpi-label">ক্যাম্পেইন সাব-ইউজার</span>
            <span class="kpi-value">{{ totalTeamUsers() }}</span>
            <span class="kpi-sub">প্রার্থীর নিজস্ব মাঠকর্মী</span>
          </div>
        </div>

        <div class="kpi-card purple">
          <div class="kpi-icon">🛡️</div>
          <div class="kpi-info">
            <span class="kpi-label">নিযুক্ত পোলিং এজেন্ট</span>
            <span class="kpi-value">{{ totalAgents() }}</span>
            <span class="kpi-sub">কেন্দ্র ও বুথভিত্তিক</span>
          </div>
        </div>

        <div class="kpi-card green">
          <div class="kpi-icon">📋</div>
          <div class="kpi-info">
            <span class="kpi-label">মোট ভোটার / স্লিপ</span>
            <span class="kpi-value">{{ totalVoters() }} / {{ totalSlips() }}</span>
            <span class="kpi-sub">ডিজিটাল স্লিপ অগ্রগতি: {{ overallSlipPercentage() }}%</span>
          </div>
        </div>

        <div class="kpi-card emerald">
          <div class="kpi-icon">🗳️</div>
          <div class="kpi-info">
            <span class="kpi-label">সংগৃহীত কেন্দ্র ভোট</span>
            <span class="kpi-value">{{ totalVotesCount() }}</span>
            <span class="kpi-sub">ফর্ম-৮ লাইভ ফলাফল</span>
          </div>
        </div>
      </section>

      <!-- SEARCH & FILTER CONTROLS -->
      <section class="filter-bar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            [(ngModel)]="searchQuery"
            placeholder="প্রার্থীর নাম, প্রতীক, রাজনৈতিক দল অথবা ইউজার আইডি দিয়ে খুঁজুন..."
          />
        </div>
        <div class="filter-tags">
          <button
            type="button"
            class="tag-pill"
            [class.active]="selectedPartyFilter() === 'ALL'"
            (click)="selectedPartyFilter.set('ALL')"
          >
            সকল দল ({{ candidates().length }})
          </button>
          <button
            type="button"
            class="tag-pill"
            [class.active]="selectedPartyFilter() === 'WITH_USER'"
            (click)="selectedPartyFilter.set('WITH_USER')"
          >
            লগইন সক্রিয় ({{ withUserCount() }})
          </button>
          <button
            type="button"
            class="tag-pill"
            [class.active]="selectedPartyFilter() === 'NO_USER'"
            (click)="selectedPartyFilter.set('NO_USER')"
          >
            ইউজার বাকি ({{ noUserCount() }})
          </button>
        </div>
      </section>

      <!-- LOADING & ERROR STATES -->
      @if (loading()) {
        <div class="loading-state">
          <div class="spinner"></div>
          <p>মাস্টার প্রার্থীদের সার্বিক তথ্য লোড হচ্ছে...</p>
        </div>
      } @else if (filteredCandidates().length === 0) {
        <div class="empty-state">
          <span class="empty-icon">📭</span>
          <h3>কোনো মাস্টার প্রার্থী পাওয়া যায়নি</h3>
          <p>আপনার অনুসন্ধানের সাথে মিল পাওয়া যায়নি অথবা এখনো কোনো প্রার্থী নিবন্ধন করা হয়নি।</p>
          <button class="btn-primary" routerLink="/candidates/entry">➕ নতুন প্রার্থী নিবন্ধন করুন</button>
        </div>
      } @else {
        <!-- CANDIDATES DOSSIER CARDS GRID -->
        <section class="candidates-grid">
          @for (c of filteredCandidates(); track c.candidateId) {
            <article class="candidate-dossier-card">
              <!-- CARD HEADER -->
              <div class="dossier-header">
                <div class="symbol-badge" title="নির্বাচনী প্রতীক">
                  <span class="symbol-emoji">{{ c.symbolEmoji }}</span>
                  <span class="symbol-name">{{ c.symbolName }}</span>
                </div>
                <div class="cand-details">
                  <div class="party-badge">{{ c.partyName || 'স্বতন্ত্র' }}</div>
                  <h2 class="cand-name">{{ c.candidateName }}</h2>
                  <span class="election-tag">🏛️ {{ c.electionName }}</span>
                </div>
              </div>

              <!-- SLOGAN / MOTTO -->
              @if (c.slogan) {
                <div class="cand-slogan">
                  💬 “{{ c.slogan }}”
                </div>
              }

              <!-- PRIMARY LOGIN ACCOUNT -->
              <div class="user-assignment-box" [class.assigned]="c.primaryUsername">
                <div class="user-box-header">
                  <span class="box-label">🔑 প্রার্থীর মূল লগইন অ্যাকাউন্ট</span>
                  @if (c.primaryUsername) {
                    <span class="status-active">● অ্যাকাউন্ট সক্রিয়</span>
                  } @else {
                    <span class="status-missing">⚠️ ইউজার নেই</span>
                  }
                </div>
                @if (c.primaryUsername) {
                  <div class="user-meta">
                    <span class="user-badge">👤 {{ c.primaryUsername }}</span>
                    <span class="user-display">{{ c.primaryDisplayName }}</span>
                  </div>
                } @else {
                  <div class="no-user-cta">
                    <span>এই প্রার্থীর ওয়ার রুমে প্রবেশ করার জন্য কোনো ইউজার নেই।</span>
                    <button class="btn-create-user" routerLink="/administration/users">
                      ➕ ইউজার তৈরি করুন
                    </button>
                  </div>
                }
              </div>

              <!-- VOTER SLIP PROGRESS -->
              <div class="slip-progress-section">
                <div class="progress-labels">
                  <span>স্মার্ট ভোটার স্লিপ ডেলিভারি</span>
                  <span class="progress-nums">{{ c.slipsIssuedCount }} / {{ c.voterCount }} ({{ c.slipPercentage }}%)</span>
                </div>
                <div class="progress-track">
                  <div class="progress-fill" [style.width.%]="c.slipPercentage"></div>
                </div>
              </div>

              <!-- MINI STATS GRID -->
              <div class="mini-metrics">
                <div class="metric-item">
                  <span class="m-icon">👥</span>
                  <div class="m-text">
                    <span class="m-val">{{ c.teamCount }} জন</span>
                    <span class="m-lbl">সাব-ইউজার টিম</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="m-icon">🛡️</span>
                  <div class="m-text">
                    <span class="m-val">{{ c.agentCount }} জন</span>
                    <span class="m-lbl">বুথ এজেন্ট</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="m-icon">🗳️</span>
                  <div class="m-text">
                    <span class="m-val highlight">{{ c.totalVotes | number }}</span>
                    <span class="m-lbl">কেন্দ্র ফলাফল ভোট</span>
                  </div>
                </div>
                <div class="metric-item">
                  <span class="m-icon">📞</span>
                  <div class="m-text">
                    <span class="m-val">{{ c.phone || 'দেওয়া হয়নি' }}</span>
                    <span class="m-lbl">যোগাযোগ</span>
                  </div>
                </div>
              </div>

              <!-- CARD ACTIONS -->
              <div class="card-footer-actions">
                <button
                  type="button"
                  class="btn-enter-war-room"
                  (click)="enterCandidateWarRoom(c)"
                  title="এই প্রার্থীর নির্বাচনী ওয়ার রুমে প্রবেশ করুন"
                >
                  <span>📊</span> প্রার্থীর ওয়ার রুমে প্রবেশ
                </button>
                <button
                  type="button"
                  class="btn-manage-team"
                  (click)="enterCandidateTeam(c)"
                  title="প্রার্থীর ক্যাম্পেইন কর্মী ও সাব-ইউজার পরিচালনা"
                >
                  <span>👥</span> কর্মী তালিকা
                </button>
              </div>
            </article>
          }
        </section>
      }
    </div>
  `,
  styles: [`
    .master-hub-container {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
      font-family: inherit;
      color: #1e293b;
    }

    .hub-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      gap: 20px;
      flex-wrap: wrap;
    }

    .header-titles h1 {
      font-size: 26px;
      font-weight: 800;
      color: #0f172a;
      margin: 6px 0 4px 0;
    }

    .header-titles p {
      color: #64748b;
      font-size: 14px;
      margin: 0;
    }

    .badge-row {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .hub-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #fef3c7, #fde68a);
      color: #92400e;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid #fcd34d;
    }

    .live-pulse-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #ecfdf5;
      color: #065f46;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid #a7f3d0;
    }

    .pulse-dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .header-actions {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .btn-primary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #0284c7;
      color: #ffffff;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      border: none;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
    }
    .btn-primary:hover { background: #0369a1; transform: translateY(-1px); }

    .btn-secondary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #f1f5f9;
      color: #334155;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      border: 1px solid #cbd5e1;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
    }
    .btn-secondary:hover { background: #e2e8f0; }

    .btn-icon {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      padding: 9px 12px;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-icon:hover { background: #e2e8f0; }

    /* KPI METRIC CARDS */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .kpi-card {
      background: #ffffff;
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      position: relative;
      overflow: hidden;
    }

    .kpi-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; width: 4px; height: 100%;
    }
    .kpi-card.gold::before { background: #f59e0b; }
    .kpi-card.blue::before { background: #0284c7; }
    .kpi-card.purple::before { background: #8b5cf6; }
    .kpi-card.green::before { background: #10b981; }
    .kpi-card.emerald::before { background: #059669; }

    .kpi-icon {
      font-size: 28px;
      background: #f8fafc;
      width: 52px;
      height: 52px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #e2e8f0;
    }

    .kpi-info {
      display: flex;
      flex-direction: column;
    }

    .kpi-label {
      font-size: 12px;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .kpi-value {
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.2;
    }

    .kpi-sub {
      font-size: 11px;
      color: #94a3b8;
      margin-top: 2px;
    }

    /* FILTER BAR */
    .filter-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      background: #ffffff;
      padding: 12px 18px;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }

    .search-box {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #f8fafc;
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid #cbd5e1;
      flex: 1;
      min-width: 280px;
    }

    .search-box input {
      border: none;
      background: transparent;
      outline: none;
      width: 100%;
      font-size: 14px;
      color: #1e293b;
    }

    .filter-tags {
      display: flex;
      gap: 8px;
    }

    .tag-pill {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      transition: all 0.15s;
    }
    .tag-pill:hover { background: #e2e8f0; }
    .tag-pill.active {
      background: #0284c7;
      color: #ffffff;
      border-color: #0284c7;
    }

    /* CANDIDATES GRID */
    .candidates-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 20px;
    }

    .candidate-dossier-card {
      background: #ffffff;
      border-radius: 14px;
      border: 1px solid #e2e8f0;
      padding: 20px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
      gap: 16px;
      transition: all 0.2s;
    }
    .candidate-dossier-card:hover {
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
      border-color: #cbd5e1;
      transform: translateY(-2px);
    }

    .dossier-header {
      display: flex;
      gap: 16px;
      align-items: center;
    }

    .symbol-badge {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 68px;
      height: 68px;
      background: #eff6ff;
      border: 2px solid #bfdbfe;
      border-radius: 12px;
      flex-shrink: 0;
    }

    .symbol-emoji {
      font-size: 28px;
      line-height: 1;
    }

    .symbol-name {
      font-size: 11px;
      font-weight: 700;
      color: #1d4ed8;
      margin-top: 2px;
      max-width: 62px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .cand-details {
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow: hidden;
    }

    .party-badge {
      display: inline-block;
      align-self: flex-start;
      background: #f1f5f9;
      color: #475569;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }

    .cand-name {
      font-size: 18px;
      font-weight: 700;
      color: #0f172a;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .election-tag {
      font-size: 12px;
      color: #64748b;
    }

    .cand-slogan {
      background: #fafaf9;
      border-left: 3px solid #eab308;
      padding: 8px 12px;
      font-size: 13px;
      font-style: italic;
      color: #57534e;
      border-radius: 0 6px 6px 0;
    }

    /* USER ASSIGNMENT BOX */
    .user-assignment-box {
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      padding: 10px 14px;
      border-radius: 8px;
    }
    .user-assignment-box.assigned {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
    }

    .user-box-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 600;
    }

    .box-label { color: #64748b; }
    .status-active { color: #15803d; font-weight: 700; }
    .status-missing { color: #b45309; font-weight: 700; }

    .user-meta {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .user-badge {
      background: #dcfce7;
      color: #166534;
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 13px;
      font-family: monospace;
    }

    .user-display {
      font-size: 13px;
      color: #334155;
    }

    .no-user-cta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: #b45309;
    }

    .btn-create-user {
      background: #f59e0b;
      color: #ffffff;
      border: none;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }
    .btn-create-user:hover { background: #d97706; }

    /* SLIP PROGRESS */
    .slip-progress-section {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .progress-labels {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #475569;
      font-weight: 600;
    }

    .progress-track {
      height: 8px;
      background: #e2e8f0;
      border-radius: 9999px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #10b981, #059669);
      border-radius: 9999px;
      transition: width 0.4s ease;
    }

    /* MINI METRICS */
    .mini-metrics {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      background: #f8fafc;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
    }

    .metric-item {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .m-icon {
      font-size: 20px;
      background: #ffffff;
      width: 34px;
      height: 34px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #e2e8f0;
      flex-shrink: 0;
    }

    .m-text {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .m-val {
      font-size: 13px;
      font-weight: 700;
      color: #0f172a;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .m-val.highlight { color: #0284c7; }

    .m-lbl {
      font-size: 11px;
      color: #64748b;
    }

    /* CARD FOOTER */
    .card-footer-actions {
      display: flex;
      gap: 10px;
      margin-top: 4px;
    }

    .btn-enter-war-room {
      flex: 2;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: #0284c7;
      color: #ffffff;
      padding: 10px 14px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 13px;
      border: none;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-enter-war-room:hover { background: #0369a1; }

    .btn-manage-team {
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: #f1f5f9;
      color: #334155;
      padding: 10px 12px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
      border: 1px solid #cbd5e1;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-manage-team:hover { background: #e2e8f0; }

    .loading-state, .empty-state {
      text-align: center;
      padding: 60px 20px;
      background: #ffffff;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #e2e8f0;
      border-top-color: #0284c7;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 16px auto;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
  `]
})
export class MasterCandidatesPage implements OnInit {
  private readonly api = inject(EemsApiService);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly loading = signal(true);
  readonly candidates = signal<MasterCandidateCard[]>([]);
  readonly searchQuery = signal('');
  readonly selectedPartyFilter = signal<'ALL' | 'WITH_USER' | 'NO_USER'>('ALL');

  // Aggregated KPIs
  readonly totalCandidates = computed(() => this.candidates().length);
  readonly totalTeamUsers = computed(() => this.candidates().reduce((sum, c) => sum + c.teamCount, 0));
  readonly totalAgents = computed(() => this.candidates().reduce((sum, c) => sum + c.agentCount, 0));
  readonly totalVoters = computed(() => this.candidates().reduce((sum, c) => sum + c.voterCount, 0));
  readonly totalSlips = computed(() => this.candidates().reduce((sum, c) => sum + c.slipsIssuedCount, 0));
  readonly totalVotesCount = computed(() => this.candidates().reduce((sum, c) => sum + c.totalVotes, 0));

  readonly overallSlipPercentage = computed(() => {
    const v = this.totalVoters();
    if (v === 0) return 0;
    return Math.round((this.totalSlips() * 100) / v);
  });

  readonly withUserCount = computed(() => this.candidates().filter(c => !!c.primaryUsername).length);
  readonly noUserCount = computed(() => this.candidates().filter(c => !c.primaryUsername).length);

  readonly filteredCandidates = computed(() => {
    let list = this.candidates();
    const filter = this.selectedPartyFilter();

    if (filter === 'WITH_USER') {
      list = list.filter(c => !!c.primaryUsername);
    } else if (filter === 'NO_USER') {
      list = list.filter(c => !c.primaryUsername);
    }

    const q = this.searchQuery().trim().toLowerCase();
    if (!q) return list;

    return list.filter(c =>
      c.candidateName.toLowerCase().includes(q) ||
      c.symbolName.toLowerCase().includes(q) ||
      c.partyName.toLowerCase().includes(q) ||
      (c.primaryUsername && c.primaryUsername.toLowerCase().includes(q)) ||
      (c.primaryDisplayName && c.primaryDisplayName.toLowerCase().includes(q)) ||
      (c.electionName && c.electionName.toLowerCase().includes(q))
    );
  });

  ngOnInit() {
    this.loadOverview();
  }

  loadOverview() {
    this.loading.set(true);
    this.api.getMasterCandidateOverview().subscribe({
      next: data => {
        this.candidates.set(data);
        this.loading.set(false);
      },
      error: err => {
        this.loading.set(false);
        console.error('Failed to load master candidates overview', err);
      }
    });
  }

  enterCandidateWarRoom(c: MasterCandidateCard) {
    this.router.navigate([`/elections/${c.electionId}/candidate-war-room`]);
  }

  enterCandidateTeam(c: MasterCandidateCard) {
    this.router.navigate([`/elections/${c.electionId}/candidate-war-room`], {
      queryParams: { tab: 'team' }
    });
  }
}

