import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule, DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import * as QRCode from 'qrcode';
import { AuthService } from '../../core/auth/auth.service';
import { EemsApiService } from '../../core/api/eems-api.service';
import {
  BoothSummary,
  CandidateBoothAgentSummary,
  CandidateElectionResultsSummary,
  CandidateWarRoomSummary,
  CenterDirectoryItem,
  EcExpenseScheduleReport,
  ElectionSymbolSummary,
  CandidateVoterSummary,
  CreateVoterRequest,
  CandidateIncidentSummary,
  CreateIncidentRequest,
  CandidateCampaignEventItem,
  CreateCampaignEventRequest,
  UpdateCampaignEventPermitRequest,
  SmsGatewayConfigDto,
  UpdateSmsGatewayConfigRequest,
  TestSmsRequest,
  SendVoterBroadcastRequest,
  VoterQueueItem,
  SendVoterBroadcastResponse,
  VoterBulkRowDto,
  VoterBulkPreviewResult,
  VoterBulkImportResult,
  CandidateCenterResultItem,
  Form8DetailResponse
} from '../../core/models/api.models';

export type WarRoomTab = 'overview' | 'agents' | 'voters' | 'campaign' | 'incidents' | 'results' | 'expenses' | 'team';


@Component({
  selector: 'eems-candidate-war-room',
  imports: [CommonModule, DatePipe, DecimalPipe, FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="no-print">
      <a class="back" [routerLink]="['/elections', electionId, 'candidates']">← Back to Candidate roster</a>

      @if(loading()){
        <div class="card empty">Loading Candidate Command Center…</div>
      } @else if(error()){
        <div class="error-banner">{{error()}} <button (click)="load()">Retry</button></div>
      } @else if(data()){
        <!-- 1. Hero Banner: Candidate & Electoral Symbol -->
        <section class="card hero-banner">
          <div class="hero-left">
            <div class="hero-symbol-avatar">
              <span class="symbol-emoji">{{data()!.candidate?.symbolEmoji || '🗳️'}}</span>
              <span class="symbol-caption">{{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn || 'প্রতীক'}}</span>
            </div>
            <div>
              <div class="hero-title-row">
                <h2>{{data()!.candidate?.name || 'প্রার্থীর নাম'}}</h2>
                <span class="badge status-badge" style="background: #dcfce7; color: #166534;">বৈধ প্রার্থী</span>
              </div>
              <p class="hero-meta">
                <b>মার্কা:</b> {{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn}}
                ({{data()!.candidate?.symbolEmoji}}) ·
                <b>দল:</b> {{data()!.candidate?.partyName || 'স্বতন্ত্র'}} ·
                <b>এলাকা:</b> {{data()!.areaName || 'নির্বাচনী আসন'}}
              </p>
              @if(data()!.candidate?.slogan){
                <p class="hero-slogan">"{{data()!.candidate?.slogan}}"</p>
              }
            </div>
          </div>
          <div class="hero-right">
            <div class="stat-pill">
              <span class="stat-val">{{data()!.totalCenters}}</span>
              <span class="stat-lbl">মোট কেন্দ্র</span>
            </div>
            <div class="stat-pill">
              <span class="stat-val">{{data()!.totalBooths}}</span>
              <span class="stat-lbl">মোট বুথ</span>
            </div>
            <div class="stat-pill highlight">
              <span class="stat-val">{{agentCoveragePercent() | number:'1.0-0'}}%</span>
              <span class="stat-lbl">এজেন্ট কভারেজ</span>
            </div>
          </div>
        </section>

        <!-- Navigation Tabs -->
        <div class="tab-nav">
          <button class="tab-btn" [class.active]="activeTab() === 'overview'" (click)="setTab('overview')">
            📊 কমান্ড সেন্টার সংক্ষেপ
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'agents'" (click)="setTab('agents')">
            🛡️ পোলিং এজেন্ট ও ফরম-৯ ({{boothAgents().length}})
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'voters'" (click)="setTab('voters')">
            👥 ভোটার ডাটাবেজ ও স্লিপ ({{voters().length}})
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'campaign'" (click)="setTab('campaign')">
            📢 প্রচার সূচি ও রুট প্ল্যান ({{campaignEvents().length}})
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'incidents'" (click)="setTab('incidents')">
            🚨 নির্বাচনী অভিযোগ ও ম্যাজিস্ট্রেট ({{incidents().length}})
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'results'" (click)="setTab('results')">
            🗳️ লাইভ ফলাফল ও ফর্ম-৮ ({{resultsSummary()?.countedCenters || 0}}/{{resultsSummary()?.totalCenters || 0}})
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'expenses'" (click)="setTab('expenses')">
            💰 ইসি ব্যয় রিটার্ন বিবরণী
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'team'" (click)="setTab('team')">
            👥 ক্যাম্পেইন কর্মী ও ইউজার ({{teamUsers().length}})
          </button>
        </div>

        <!-- ================================================================= -->
        <!-- TAB 1: OVERVIEW & 4 PILLARS -->
        <!-- ================================================================= -->
        @if(activeTab() === 'overview'){
          <section class="operations-grid">
            <!-- Pillar 1: Polling Centers & Agents -->
            <article class="card op-card">
              <div class="op-head">
                <span class="op-icon">🏛️</span>
                <div>
                  <p class="op-eyebrow">BOOTHS & AGENTS</p>
                  <h3>ভোটকেন্দ্র ও পোলিং এজেন্ট</h3>
                </div>
              </div>
              <div class="metrics-row">
                <div class="metric">
                  <b>{{data()!.totalCenters}}</b>
                  <span>মোট কেন্দ্র</span>
                </div>
                <div class="metric">
                  <b>{{data()!.totalBooths}}</b>
                  <span>মোট বুথ</span>
                </div>
                <div class="metric">
                  <b class="metric-good">{{boothAgents().length}}</b>
                  <span>নিযুক্ত এজেন্ট</span>
                </div>
              </div>
              <div class="coverage-bar-track">
                <div class="coverage-bar-fill" [style.width.%]="agentCoveragePercent()"></div>
              </div>
              <p class="coverage-text">কভারেজ: <b>{{agentCoveragePercent() | number:'1.0-1'}}%</b> (বাকি বুথ: {{data()!.totalBooths - boothAgents().length}}টি)</p>
              <div class="op-actions">
                <a [routerLink]="['/elections', electionId, 'centers']" class="btn-sm" style="text-decoration: none; background: #e0f2fe; color: #0369a1; font-weight: 700;">🏫 কেন্দ্র ও বুথ এন্ট্রি</a>
                <button class="btn-sm" (click)="setTab('agents')">এজেন্ট তালিকা দেখুন</button>
                <button class="btn-sm outline" (click)="openAddAgentModal()">+ এজেন্ট নিয়োগ</button>
                <button class="btn-sm badge-btn" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড প্রিন্ট</button>
              </div>
            </article>

            <!-- Pillar 2: Voters & Digital Slip -->
            <article class="card op-card">
              <div class="op-head">
                <span class="op-icon">👥</span>
                <div>
                  <p class="op-eyebrow">VOTERS & DIGITAL SLIP</p>
                  <h3>ভোটার ডাটাবেজ ও ডিজিটাল স্লিপ</h3>
                </div>
              </div>
              <div class="metrics-row">
                <div class="metric">
                  <b>{{voters().length}}</b>
                  <span>তালিকাভুক্ত ভোটার</span>
                </div>
                <div class="metric">
                  <b class="metric-good">{{issuedSlipsCount()}}</b>
                  <span>স্লিপ ইস্যু</span>
                </div>
                <div class="metric">
                  <b class="metric-accent">{{votedCount()}}</b>
                  <span>ভোট দিয়েছেন</span>
                </div>
              </div>
              <div class="coverage-bar-track">
                <div class="coverage-bar-fill" [style.width.%]="issuedSlipsPercent()"></div>
              </div>
              <p class="coverage-text">স্লিপ বিতরণের অগ্রগতি: <b>{{issuedSlipsPercent() | number:'1.0-1'}}%</b></p>
              <div class="op-actions">
                <button class="btn-sm" (click)="setTab('voters')">ভোটার তালিকা দেখুন</button>
                <button class="btn-sm highlight-btn" (click)="openVoterBroadcastModal()">📱 বাল্ক SMS / হোয়াটসঅ্যাপ</button>
                <button class="btn-sm outline" (click)="openVoterSlipsPrint()">🖨️ স্লিপ প্রিন্ট</button>
              </div>
            </article>

            <!-- Pillar 3: Incidents & Magistrate Escalation -->
            <article class="card op-card">
              <div class="op-head">
                <span class="op-icon">🚨</span>
                <div>
                  <p class="op-eyebrow">INCIDENTS & COMPLAINTS</p>
                  <h3>অনিয়ম ও ম্যাজিস্ট্রেট নোটিশ</h3>
                </div>
              </div>
              <div class="metrics-row">
                <div class="metric">
                  <b>{{incidents().length}}</b>
                  <span>মোট অভিযোগ</span>
                </div>
                <div class="metric">
                  <b [class.metric-bad]="criticalIncidentsCount() > 0">{{criticalIncidentsCount()}}</b>
                  <span>জরুরি হস্তক্ষেপ</span>
                </div>
                <div class="metric">
                  <b class="metric-good">{{resolvedIncidentsCount()}}</b>
                  <span>নিষ্পত্তি</span>
                </div>
              </div>
              <p class="coverage-text">ম্যাজিস্ট্রেট ও এআরও বরাবর আইনগত নোটিশ প্রস্তুত ও তাৎক্ষণিক প্রিন্ট সুবিধা।</p>
              <div class="op-actions">
                <button class="btn-sm" (click)="setTab('incidents')">অভিযোগ বোর্ড</button>
                <button class="btn-sm alert-btn" (click)="openAddIncidentModal()">+ অনিয়ম রেকর্ড করুন</button>
              </div>
            </article>

            <!-- Pillar 4: Live Results & Form-8 -->
            <article class="card op-card">
              <div class="op-head">
                <span class="op-icon">🗳️</span>
                <div>
                  <p class="op-eyebrow">RESULTS & FORM-8</p>
                  <h3>ভোট গণনা ও ফলাফল</h3>
                </div>
              </div>
              <div class="metrics-row">
                <div class="metric">
                  <b>{{resultsSummary()?.countedCenters || 0}}/{{resultsSummary()?.totalCenters || data()!.totalCenters}}</b>
                  <span>কেন্দ্র ফলাফল</span>
                </div>
                <div class="metric">
                  <b class="metric-good">{{resultsSummary()?.candidateTotalVotes || 0}}</b>
                  <span>প্রাপ্ত ভোট</span>
                </div>
                <div class="metric">
                  <b [class.metric-good]="(resultsSummary()?.leadMargin || 0) >= 0" [class.metric-bad]="(resultsSummary()?.leadMargin || 0) < 0">
                    {{(resultsSummary()?.leadMargin || 0) > 0 ? '+' : ''}}{{resultsSummary()?.leadMargin || 0}}
                  </b>
                  <span>লিড মার্জিন</span>
                </div>
              </div>
              <p class="coverage-text">নির্বাচন কমিশনের ফর্ম-৮ বিবরণী ও কেন্দ্রভিত্তিক লাইভ ফলাফল পর্যবেক্ষণ।</p>
              <div class="op-actions">
                <button class="btn-sm" (click)="setTab('results')">ফলাফল ড্যাশবোর্ড</button>
                <button class="btn-sm outline" (click)="openQuickResultModal()">+ ফলাফল এন্ট্রি</button>
              </div>
            </article>
          </section>

          <!-- Quick Command Bar -->
          <div class="card quick-command-bar" style="margin-top: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding: 16px 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.4rem;">⚡</span>
              <div>
                <b style="color: var(--navy); display: block;">কুইক একশন বার (One-Click Operations)</b>
                <span style="font-size: 0.82rem; color: #64748b;">নির্বাচনী সকল কার্যক্রমে সরাসরি এক ক্লিকে প্রবেশ করুন</span>
              </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <a [routerLink]="['/elections', electionId, 'centers']" class="btn-sm" style="text-decoration: none; background: #f0fdf4; color: #166534; font-weight: 700; border-color: #bbf7d0;">🏫 কেন্দ্র ও বুথ এন্ট্রি</a>
              <button class="btn-sm" style="background: #e0e7ff; color: #4338ca; font-weight: 700; border-color: #c7d2fe;" (click)="setTab('team')">👥 কর্মী ও ইউজার তৈরি</button>
              <button class="btn-sm" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড</button>
              <button class="btn-sm highlight-btn" (click)="openVoterBroadcastModal()">📱 বাল্ক SMS / WA</button>
              <button class="btn-sm" (click)="openSmsConfigModal()">⚙️ SMS গেটওয়ে</button>
              <button class="btn-sm outline" (click)="setTab('campaign')">📢 প্রচার সূচি</button>
              <button class="btn-sm alert-btn" (click)="openAddIncidentModal()">🚨 ম্যাজিস্ট্রেট অভিযোগ</button>
              <button class="btn-sm outline" (click)="setTab('expenses')">💰 ইসি ব্যয় রিটার্ন</button>
            </div>
          </div>

          <!-- Polling Centers Summary Table -->
          <section class="card table-card" style="margin-top: 20px;">
            <div class="table-header">
              <h3>ভোটকেন্দ্র ও পোলিং এজেন্ট কভারেজ পর্যবেক্ষণ</h3>
              <div style="display: flex; gap: 8px; align-items: center;">
                <a [routerLink]="['/elections', electionId, 'centers']" class="primary-button" style="text-decoration: none; font-size: 0.85rem; padding: 6px 14px;">
                  ➕ নতুন ভোট কেন্দ্র ও বুথ এন্ট্রি
                </a>
                <button class="outline-btn" (click)="load()">রিলোড</button>
              </div>
            </div>
            <table class="data-table">
              <thead>
                <tr>
                  <th>নং</th>
                  <th>কেন্দ্রের নাম ও কোড</th>
                  <th>অবস্থান / এলাকা</th>
                  <th>বুথ সংখ্যা</th>
                  <th>এজেন্ট নিয়োজিত</th>
                  <th>কভারেজ স্ট্যাটাস</th>
                </tr>
              </thead>
              <tbody>
                @for(c of centersList(); track c.centerId; let idx = $index){
                  <tr>
                    <td>{{idx + 1}}</td>
                    <td>
                      <b>{{c.name}}</b>
                      <span class="sub-cell">কোড: {{c.code}}</span>
                    </td>
                    <td>{{c.address || '—'}}</td>
                    <td><b>{{c.boothCount}}</b>টি</td>
                    <td>
                      <b class="metric-good">{{getAssignedCount(c.centerId)}}</b> / {{c.boothCount}}
                    </td>
                    <td>
                      @if(getAssignedCount(c.centerId) >= c.boothCount){
                        <span class="badge badge-complete">১০০% পূর্ণাঙ্গ</span>
                      } @else if(getAssignedCount(c.centerId) > 0){
                        <span class="badge badge-partial">আংশিক</span>
                      } @else {
                        <span class="badge badge-empty">এজেন্ট বাকি</span>
                      }
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 2: POLLING BOOTH AGENTS & FORM-9 -->
        <!-- ================================================================= -->
        @if(activeTab() === 'agents'){
          <section class="card table-card">
            <div class="table-header">
              <div class="filter-group">
                <h3>নিযুক্ত পোলিং এজেন্ট তালিকা ও ফরম-৯</h3>
                <select [(ngModel)]="agentFilterCenter">
                  <option value="">সকল কেন্দ্র ({{centersList().length}}টি)</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>
              <div class="actions">
                <button class="btn-sm badge-btn" (click)="openBatchIdCardsModal()">🪪 ব্যাচ আইডি কার্ড প্রিন্ট</button>
                <button class="primary-button" (click)="openAddAgentModal()">+ নতুন পোলিং এজেন্ট নিয়োগ</button>
              </div>
            </div>

            <table class="data-table">
              <thead>
                <tr>
                  <th>ছবি</th>
                  <th>এজেন্টের নাম ও পরিচয়</th>
                  <th>ভোটকেন্দ্র ও বুথ</th>
                  <th>মোবাইল নম্বর</th>
                  <th>ফরম-৯ নিয়োগপত্র</th>
                  <th>কার্যক্রম</th>
                </tr>
              </thead>
              <tbody>
                @for(ag of filteredAgents(); track ag.boothAgentId){
                  <tr>
                    <td>
                      <div class="avatar-cell">
                        @if(ag.photoUrl){
                          <img [src]="ag.photoUrl" alt="agent" class="agent-thumb">
                        } @else {
                          <span class="avatar-placeholder">👤</span>
                        }
                      </div>
                    </td>
                    <td>
                      <b>{{ag.fullName}}</b>
                      <span class="sub-cell">NID: {{ag.nidNumber}} {{ag.voterNumber ? '· ভোটার নং: ' + ag.voterNumber : ''}}</span>
                      @if(ag.notes){
                        <span class="sub-cell" style="font-style: italic;">{{ag.notes}}</span>
                      }
                    </td>
                    <td>
                      <b>{{ag.centerName}}</b>
                      <span class="sub-cell">{{ag.boothName ? 'বুথ: ' + ag.boothName : 'সাধারণ বুথ'}}</span>
                    </td>
                    <td>
                      <a [href]="'tel:' + ag.phone" class="phone-link">{{ag.phone}}</a>
                    </td>
                    <td>
                      @if(ag.appointmentLetterIssued){
                        <span class="badge badge-complete">ইস্যু সম্পন্ন</span>
                      } @else {
                        <button class="btn-sm outline" (click)="issueLetter(ag)">ইস্যু মার্ক করুন</button>
                      }
                    </td>
                    <td>
                      <div class="row-actions">
                        <button class="btn-sm form9-btn" (click)="openForm9Preview(ag)" title="ইসি ফরম-৯ নিয়োগপত্র দেখুন ও প্রিন্ট করুন">
                          📄 ফরম-৯
                        </button>
                        <button class="btn-sm badge-btn" (click)="openAgentBadge(ag)" title="আইডি কার্ড ব্যাজ প্রিন্ট করুন">
                          🪪 আইডি ব্যাজ
                        </button>
                        <button class="btn-sm danger" (click)="deleteBoothAgent(ag)" title="মুছে ফেলুন">
                          ✕
                        </button>
                      </div>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="6" class="empty-cell">কোনো পোলিং এজেন্ট পাওয়া যায়নি। নতুন এজেন্ট নিয়োগ করতে উপরের বাটনে ক্লিক করুন।</td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 3: VOTERS & DIGITAL SLIP (Option 2 Implementation) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'voters'){
          <section class="card table-card voters-workspace">
            <!-- Voter Stats Counter Row -->
            <div class="metrics-row" style="margin-bottom: 20px; background: #f8fafc; padding: 14px 18px; border-radius: 12px; border: 1px solid var(--line);">
              <div class="metric">
                <b>{{voters().length}}</b>
                <span>মোট ভোটার সংখ্যা</span>
              </div>
              <div class="metric">
                <b class="metric-good">{{issuedSlipsCount()}} ({{issuedSlipsPercent() | number:'1.0-0'}}%)</b>
                <span>স্লিপ ইস্যু সম্পন্ন</span>
              </div>
              <div class="metric">
                <b class="metric-accent">{{votedCount()}} ({{votedPercent() | number:'1.0-0'}}%)</b>
                <span>ভোট কাস্ট সম্পন্ন</span>
              </div>
              <div class="metric">
                <b>{{phonesCount()}}</b>
                <span>মোবাইল নম্বর এন্ট্রি</span>
              </div>
            </div>

            <!-- Toolbar Actions -->
            <div class="table-header" style="flex-wrap: wrap; gap: 12px;">
              <div class="filter-group" style="flex-wrap: wrap; gap: 8px;">
                <input [(ngModel)]="voterSearchQuery" (keyup.enter)="loadVoters()" placeholder="ভোটার নাম / NID / ক্রমিক নম্বর…" style="padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; width: 220px;">
                <select [(ngModel)]="voterFilterCenter" (change)="loadVoters()">
                  <option value="">সকল ভোটকেন্দ্র</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}}</option>
                  }
                </select>
                <select [(ngModel)]="voterFilterCategory" (change)="loadVoters()">
                  <option value="">সকল ক্যাটাগরি</option>
                  <option value="SUPPORTER">বিশ্বস্ত সমর্থক</option>
                  <option value="SWING">দোদুল্যমান</option>
                  <option value="OPPONENT">প্রতিপক্ষ</option>
                  <option value="ABROAD">প্রবাসী/অনুপস্থিত</option>
                </select>
                <select [(ngModel)]="voterFilterSlip" (change)="loadVoters()">
                  <option value="">সকল স্লিপ স্ট্যাটাস</option>
                  <option value="true">স্লিপ ইস্যু হয়েছে</option>
                  <option value="false">স্লিপ বাকি</option>
                </select>
                <button class="outline-btn" (click)="loadVoters()">ফিল্টার</button>
              </div>

              <div class="actions" style="flex-wrap: wrap; gap: 8px;">
                <button class="btn-sm highlight-btn" (click)="openVoterBroadcastModal()">📱 বাল্ক SMS / হোয়াটসঅ্যাপ</button>
                <button class="btn-sm outline" (click)="openSmsConfigModal()">⚙️ SMS গেটওয়ে</button>
                <button class="btn-sm outline" (click)="openBulkImportModal()">📥 বাল্ক ভোটার ইম্পোর্ট</button>
                <button class="btn-sm outline" (click)="openVoterSlipsPrint()">🖨️ ব্যাচ স্লিপ প্রিন্ট</button>
                <button class="primary-button" (click)="openAddVoterModal()">+ নতুন ভোটার</button>
              </div>
            </div>

            <!-- Voters Table -->
            <table class="data-table">
              <thead>
                <tr>
                  <th>ক্রমিক</th>
                  <th>ভোটারের নাম ও অভিভাবক</th>
                  <th>ভোটার নম্বর (NID)</th>
                  <th>ভোটকেন্দ্র ও বুথ</th>
                  <th>ক্যাটাগরি</th>
                  <th>মোবাইল নম্বর</th>
                  <th>স্লিপ স্ট্যাটাস</th>
                  <th>ভোট কাস্ট</th>
                  <th>কার্যক্রম</th>
                </tr>
              </thead>
              <tbody>
                @for(v of voters(); track v.id){
                  <tr>
                    <td>
                      <b class="serial-pill">#{{v.serialNumber}}</b>
                    </td>
                    <td>
                      <b>{{v.fullName}}</b>
                      <span class="sub-cell">পিতা/স্বামী: {{v.fatherOrSpouseName || '—'}}</span>
                      @if(v.age || v.gender){
                        <span class="sub-cell">বয়স: {{v.age || '—'}}, {{v.gender === 'FEMALE' ? 'নারী' : 'পুরুষ'}}</span>
                      }
                    </td>
                    <td>
                      <b style="font-family: monospace; color: var(--navy);">{{v.voterNumber}}</b>
                      @if(v.areaName){
                        <span class="sub-cell">{{v.areaName}}</span>
                      }
                    </td>
                    <td>
                      <b>{{v.centerName}}</b>
                      <span class="sub-cell">{{v.boothName ? 'বুথ: ' + v.boothName : 'সাধারণ বুথ'}}</span>
                    </td>
                    <td>
                      <span class="category-chip" [attr.data-cat]="v.category">{{getCategoryLabel(v.category)}}</span>
                    </td>
                    <td>
                      @if(v.phone){
                        <a [href]="'tel:' + v.phone" class="phone-link">{{v.phone}}</a>
                      } @else {
                        <span style="color: #94a3b8; font-size: 0.8rem;">নেই</span>
                      }
                    </td>
                    <td>
                      <button class="toggle-pill" [class.done]="v.slipIssued" (click)="toggleSlip(v)" title="স্লিপ বিতরণের স্ট্যাটাস পরিবর্তন করুন">
                        {{v.slipIssued ? '✓ ইস্যু সম্পন্ন' : 'বাকি'}}
                      </button>
                    </td>
                    <td>
                      <button class="vote-status-btn" [class.voted]="v.hasVoted" (click)="toggleVoted(v)">
                        {{v.hasVoted ? '🗳️ কাস্ট সম্পন্ন' : 'বাকি'}}
                      </button>
                    </td>
                    <td>
                      <div class="row-actions">
                        <button class="btn-sm wa-pill-btn" (click)="sendSingleVoterWhatsApp(v)" [disabled]="!v.phone" title="হোয়াটসঅ্যাপে ডিজিটাল ভোটার স্লিপ পাঠান">
                          💬 WA
                        </button>
                        <button class="btn-sm slip-pill-btn" (click)="openSmartSlip(v)" title="স্মার্ট ডিজিটাল ভোটার পাস / স্লিপ কার্ড ও কিউআর দেখুন">
                          🎫 স্লিপ
                        </button>
                        <button class="btn-sm danger" (click)="deleteVoter(v)" title="মুছে ফেলুন">✕</button>
                      </div>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="9" class="empty-cell">
                      কোনো ভোটার রেকর্ড পাওয়া যায়নি। উপরের "বাল্ক ভোটার ইম্পোর্ট" বা "+ নতুন ভোটার" বাটনে ক্লিক করে ভোটার যুক্ত করুন।
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 4: CAMPAIGN EVENTS & ROUTE PLANNER (Option 3 Implementation) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'campaign'){
          <section class="card table-card">
            <!-- Campaign Summary Row -->
            <div class="metrics-row" style="margin-bottom: 20px; background: #f8fafc; padding: 14px 18px; border-radius: 12px; border: 1px solid var(--line);">
              <div class="metric">
                <b>{{campaignEvents().length}}</b>
                <span>মোট প্রচার কর্মসূচি</span>
              </div>
              <div class="metric">
                <b class="metric-good">{{approvedEventsCount()}}</b>
                <span>প্রশাসনের অনুমতি প্রাপ্ত</span>
              </div>
              <div class="metric">
                <b>{{campaignVenues().length}}</b>
                <span>তালিকাভুক্ত জনসভাস্থল</span>
              </div>
              <div class="metric">
                <b style="color: #0369a1;">দুপুর ২টা - রাত ৮টা</b>
                <span>ইসি অনুমোদিত মাইকিং সময়</span>
              </div>
            </div>

            <div class="table-header">
              <div>
                <h3>নির্বাচনী প্রচার সূচি, পথসমাবেশ ও প্রশাসন পারমিট ট্র্যাকার</h3>
                <span style="font-size: 0.85rem; color: #64748b;">নির্বাচন আচরণবিধি ২০০৮ অনুযায়ী অনুমোদিত সময়ে ও স্থানে জনসভা আয়োজন নিশ্চিত করুন</span>
              </div>
              <button class="primary-button" (click)="openAddCampaignModal()">+ নতুন প্রচার সূচি যুক্ত করুন</button>
            </div>

            <!-- Campaign Events Grid -->
            <div class="campaign-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; margin-top: 18px;">
              @for(ev of campaignEvents(); track ev.eventId){
                <div class="card campaign-card" style="border: 1px solid var(--line); border-radius: 12px; padding: 16px; background: #fff; display: flex; flex-direction: column; gap: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                    <div>
                      <span class="badge" style="background: #e0f2fe; color: #0369a1; font-weight: 700; margin-bottom: 4px; display: inline-block;">{{getCampaignTypeLabel(ev.eventTypeName)}}</span>
                      <h4 style="margin: 0; font-size: 1.05rem; color: var(--navy);">{{ev.title}}</h4>
                    </div>
                    <span class="badge" [class.badge-complete]="ev.permitStatus === 'APPROVED'" [class.badge-empty]="ev.permitStatus === 'REJECTED'" [class.badge-partial]="ev.permitStatus === 'PENDING'">
                      {{ev.permitStatus}}
                    </span>
                  </div>

                  <div style="background: #f8fafc; border-radius: 8px; padding: 10px 12px; font-size: 0.85rem; display: flex; flex-direction: column; gap: 4px;">
                    <div><b>স্থান:</b> {{ev.venueName || 'এলাকা'}}</div>
                    <div><b>সময়:</b> {{ev.startsAt | date:'mediumDate'}}, {{ev.startsAt | date:'shortTime'}} - {{ev.endsAt | date:'shortTime'}}</div>
                    <div><b>অনুমোদনকারী:</b> {{ev.issuingAuthority || 'থানা পুলিশ / ইউএনও'}}</div>
                    @if(ev.permitReferenceNumber){
                      <div><b>স্মারক নং:</b> <span style="font-family: monospace; color: #047857;">{{ev.permitReferenceNumber}}</span></div>
                    }
                  </div>

                  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem;">
                    <span>ধারনক্ষমতা: <b>{{ev.venueCapacity || 500 | number}}</b> জন</span>
                    <span [style.color]="ev.isMikingHoursCompliant ? '#15803d' : '#b91c1c'" style="font-weight: 700;">
                      {{ev.isMikingHoursCompliant ? '✓ মাইকিং বিধি সম্মত' : '⚠️ মাইকিং বিধি সতর্ক'}}
                    </span>
                  </div>

                  <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: auto;">
                    <div style="display: flex; gap: 6px;">
                      <button class="btn-sm outline" (click)="openUpdatePermitModal(ev)">📝 পারমিট আপডেট</button>
                      <button class="btn-sm" (click)="openPrintPermitNotice(ev)">🖨️ অনুমতিপত্র</button>
                    </div>
                    <button class="btn-sm danger" (click)="deleteCampaignEvent(ev)">✕</button>
                  </div>
                </div>
              } @empty {
                <div style="grid-column: 1 / -1; padding: 30px; text-align: center; color: #64748b;">
                  কোনো প্রচার কর্মসূচি এখনো অন্তর্ভুক্ত করা হয়নি। উপরের বাটনে ক্লিক করে নতুন সূচি যুক্ত করুন।
                </div>
              }
            </div>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 5: INCIDENTS & MAGISTRATE ESCALATION -->
        <!-- ================================================================= -->
        @if(activeTab() === 'incidents'){
          <section class="card table-card incidents-workspace">
            <div class="table-header">
              <div>
                <h3>নির্বাচনী অনিয়ম, গোলযোগ ও ম্যাজিস্ট্রেট আইনি প্রতিকার বোর্ড</h3>
                <span style="font-size: 0.85rem; color: #64748b;">কেন্দ্রে কোনো গোলযোগ ঘটলে তাৎক্ষণিক ম্যাজিস্ট্রেট ও সহকারী রিটার্নিং কর্মকর্তা বরাবর আইনগত অভিযোগ দাখিল করুন</span>
              </div>
              <button class="primary-button alert-btn" (click)="openAddIncidentModal()">+ জরুরি অনিয়ম / গোলযোগ রেকর্ড</button>
            </div>

            <div class="incidents-grid">
              @for(inc of incidents(); track inc.id){
                <div class="incident-card" [attr.data-severity]="inc.severity">
                  <div class="inc-head">
                    <span class="severity-badge" [class.crit]="inc.severity === 'CRITICAL'">{{inc.severity}}</span>
                    <span class="inc-time">{{inc.reportedAt | date:'mediumDate'}}, {{inc.reportedAt | date:'shortTime'}}</span>
                  </div>
                  <h4 class="inc-title">{{inc.title}}</h4>
                  <p class="inc-desc">{{inc.description}}</p>
                  <div class="inc-meta-row">
                    <div><b>কেন্দ্র:</b> {{inc.centerName}} {{inc.boothName ? '· বুথ: ' + inc.boothName : ''}}</div>
                    <div><b>সংবাদদাতা:</b> {{inc.reportedBy}} ({{inc.reportedByPhone || 'মোবাইল নেই'}})</div>
                  </div>
                  <div class="inc-footer">
                    <div class="status-change-grp">
                      <label>স্ট্যাটাস:</label>
                      <select [ngModel]="inc.status" (ngModelChange)="updateIncidentStatus(inc, $event)">
                        <option value="REPORTED">REPORTED (দাখিল)</option>
                        <option value="UNDER_INVESTIGATION">তদন্তাধীন</option>
                        <option value="ESCALATED_TO_MAGISTRATE">ম্যাজিস্ট্রেটে প্রেরিত</option>
                        <option value="RESOLVED">নিষ্পন্ন</option>
                      </select>
                    </div>
                    <div class="inc-actions">
                      <button class="btn-sm print-complaint-btn" (click)="openComplaintLetter(inc)" title="ম্যাজিস্ট্রেট ও রিটার্নিং অফিসার বরাবর আইনগত অভিযোগ ড্রাফট ও প্রিন্ট">
                        ⚖️ ম্যাজিস্ট্রেট অভিযোগপত্র
                      </button>
                      <button class="btn-sm danger" (click)="deleteIncident(inc)" title="মুছে ফেলুন">✕</button>
                    </div>
                  </div>
                </div>
              } @empty {
                <div class="empty-cell" style="grid-column: 1 / -1; padding: 40px; text-align: center; color: #64748b;">
                  কোনো অনিয়ম বা গোলযোগের রেকর্ড নেই। শান্ত ও সুশৃঙ্খল পরিবেশ বিরাজ করছে।
                </div>
              }
            </div>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 6: LIVE RESULTS & FORM-8 (Option 1 Implementation) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'results'){
          <section class="card table-card">
            <!-- Results Scoreboard -->
            <div class="scoreboard-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 22px;">
              <div class="score-card" style="background: #f8fafc; border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px;">
                <span style="font-size: 0.8rem; text-transform: uppercase; color: #64748b; font-weight: 700;">রিপোর্ট প্রাপ্ত কেন্দ্র</span>
                <b style="font-size: 1.6rem; color: var(--navy); display: block; margin-top: 4px;">{{resultsSummary()?.countedCenters || 0}} / {{resultsSummary()?.totalCenters || 0}}</b>
              </div>
              <div class="score-card" style="background: #f8fafc; border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px;">
                <span style="font-size: 0.8rem; text-transform: uppercase; color: #64748b; font-weight: 700;">মোট কাস্টকৃত ভোট</span>
                <b style="font-size: 1.6rem; color: var(--navy); display: block; margin-top: 4px;">
                  {{((resultsSummary()?.candidateTotalVotes || 0) + (resultsSummary()?.runnerUpTotalVotes || 0)) | number}}
                </b>
              </div>
              <div class="score-card highlight" style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 14px 18px;">
                <span style="font-size: 0.8rem; text-transform: uppercase; color: #065f46; font-weight: 700;">প্রার্থীর প্রাপ্ত ভোট ({{data()!.candidate?.symbolEmoji}})</span>
                <b style="font-size: 1.6rem; color: #047857; display: block; margin-top: 4px;">{{resultsSummary()?.candidateTotalVotes || 0 | number}}</b>
              </div>
              <div class="score-card" style="background: #f8fafc; border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px;">
                <span style="font-size: 0.8rem; text-transform: uppercase; color: #64748b; font-weight: 700;">নিকটতম প্রতিদ্বন্দ্বী</span>
                <b style="font-size: 1.6rem; color: #b91c1c; display: block; margin-top: 4px;">{{resultsSummary()?.runnerUpTotalVotes || 0 | number}}</b>
              </div>
              <div class="score-card highlight" style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 14px 18px;">
                <span style="font-size: 0.8rem; text-transform: uppercase; color: #1e40af; font-weight: 700;">লিড / ব্যবধান</span>
                <b style="font-size: 1.6rem; color: #1d4ed8; display: block; margin-top: 4px;">
                  {{(resultsSummary()?.leadMargin || 0) > 0 ? '+' : ''}}{{resultsSummary()?.leadMargin || 0 | number}}
                </b>
              </div>
            </div>

            <!-- ============================================================= -->
            <!-- SECTION: CONTESTING CANDIDATES & VOTE LEADERBOARD -->
            <!-- ============================================================= -->
            <div class="card table-card" style="margin-bottom: 22px; border: 1px solid var(--line); border-radius: 12px; padding: 20px;">
              <div class="table-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                <div>
                  <h3 style="margin: 0; font-size: 1.15rem; color: var(--navy); display: flex; align-items: center; gap: 8px;">
                    👥 প্রতিদ্বন্দ্বী প্রার্থী তালিকা ও ভোট প্রাপ্তির সার্বিক অবস্থান
                  </h3>
                  <p style="margin: 4px 0 0; font-size: 0.85rem; color: #64748b;">
                    এই নির্বাচনী আসনে প্রতিদ্বন্দ্বিতাকারী সকল প্রার্থীর তালিকা, প্রতীক ও ভোট গণনার লাইভ শতকরা হার
                  </p>
                </div>
                <div class="actions">
                  <button type="button" class="primary-button" (click)="openAddOpponentModal()" style="display: flex; align-items: center; gap: 6px;">
                    <span>➕</span> নতুন প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করুন
                  </button>
                </div>
              </div>

              <table class="data-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">নং</th>
                    <th style="width: 140px;">প্রতীক ও মার্কা</th>
                    <th>প্রার্থীর নাম</th>
                    <th>দল / রাজনৈতিক পরিচয়</th>
                    <th style="text-align: right; width: 140px;">মোট প্রাপ্ত ভোট</th>
                    <th style="width: 200px;">ভোটের হার (%)</th>
                    <th style="text-align: center; width: 100px;">অ্যাকশন</th>
                  </tr>
                </thead>
                <tbody>
                  @for(t of resultsSummary()?.allCandidateTallies || []; track t.candidateId; let idx = $index){
                    <tr [style.background]="t.isPrimary ? '#f0fdf4' : ''" [style.fontWeight]="t.isPrimary ? '700' : '400'">
                      <td>{{idx + 1}}</td>
                      <td>
                        <span style="font-size: 1.3rem; margin-right: 6px;">{{t.symbolEmoji}}</span>
                        <b>{{t.symbolName}}</b>
                      </td>
                      <td>
                        <b [style.color]="t.isPrimary ? '#047857' : '#1e293b'">{{t.name}}</b>
                        @if(t.isPrimary){
                          <span style="margin-left: 8px; background: #ecfdf5; color: #047857; font-weight: 700; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; border: 1px solid #a7f3d0;">
                            আমাদের প্রার্থী
                          </span>
                        }
                      </td>
                      <td style="color: #475569;">{{t.partyName}}</td>
                      <td style="text-align: right;">
                        <b [style.color]="t.isPrimary ? '#047857' : '#1e293b'" style="font-size: 1.1rem;">
                          {{t.totalVotes | number}}
                        </b>
                      </td>
                      <td>
                        <div style="display: flex; align-items: center; gap: 8px;">
                          <div style="flex: 1; height: 10px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">
                            <div [style.width.%]="t.votePercentage" [style.background]="t.isPrimary ? '#10b981' : '#64748b'" style="height: 100%; border-radius: 9999px;"></div>
                          </div>
                          <span style="font-size: 0.85rem; font-weight: 700; width: 44px; text-align: right;">{{t.votePercentage}}%</span>
                        </div>
                      </td>
                      <td style="text-align: center;">
                        @if(!t.isPrimary){
                          <button type="button" class="text-button" style="color: #ef4444; font-size: 0.8rem; padding: 4px 8px; cursor: pointer;" (click)="deleteOpponent(t.candidateId)" title="প্রার্থী বাতিল করুন">
                            🗑️ মুছুন
                          </button>
                        } @else {
                          <span style="font-size: 0.8rem; color: #94a3b8;">—</span>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>

            <!-- Graphical Lead Margin Tracker -->
            <div class="card lead-tracker-card" style="background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 22px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <h4 style="margin: 0; font-size: 1rem; color: var(--navy); display: flex; align-items: center; gap: 8px;">
                  📊 গ্রাফিক্যাল লিড ট্র্যাকার (কেন্দ্রভিত্তিক ব্যবধান বিশ্লেষণ)
                </h4>
                <span style="font-size: 0.8rem; color: #64748b;">মার্কা: {{data()!.candidate?.symbolNameBn}} {{data()!.candidate?.symbolEmoji}}</span>
              </div>
              <div class="lead-bars-container" style="display: flex; flex-direction: column; gap: 10px;">
                @for(c of resultsSummary()?.centerResults || []; track c.electionCenterId){
                  <div class="center-lead-row" style="display: grid; grid-template-columns: 220px 1fr 100px; align-items: center; gap: 12px; font-size: 0.85rem;">
                    <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                      <b>{{c.centerName}}</b>
                    </div>
                    <div class="lead-bar-wrapper" style="position: relative; height: 22px; background: #f1f5f9; border-radius: 6px; overflow: hidden; display: flex;">
                      <div class="lead-bar-cand" [style.width.%]="calcCandPct(c.candidateVotes, c.runnerUpVotes)" style="background: #10b981; height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 6px; color: #fff; font-size: 0.75rem; font-weight: 700;">
                        {{c.candidateVotes}}
                      </div>
                      <div class="lead-bar-opp" [style.width.%]="calcOppPct(c.candidateVotes, c.runnerUpVotes)" style="background: #f87171; height: 100%; display: flex; align-items: center; justify-content: flex-start; padding-left: 6px; color: #fff; font-size: 0.75rem; font-weight: 700;">
                        {{c.runnerUpVotes}}
                      </div>
                    </div>
                    <div style="text-align: right; font-weight: 800;" [style.color]="(c.candidateVotes - c.runnerUpVotes) >= 0 ? '#15803d' : '#b91c1c'">
                      {{(c.candidateVotes - c.runnerUpVotes) >= 0 ? '+' : ''}}{{c.candidateVotes - c.runnerUpVotes}}
                    </div>
                  </div>
                }
              </div>
            </div>

            <div class="table-header">
              <h3>কেন্দ্রভিত্তিক ভোট গণনা বিবরণী ও ফরম-৮</h3>
              <div class="actions">
                <button class="outline-btn" (click)="loadResultsSummary()">রিলোড</button>
                <button class="primary-button" (click)="openQuickResultModal()">+ কেন্দ্রের লাইভ ফলাফল এন্ট্রি</button>
              </div>
            </div>

            <table class="data-table">
              <thead>
                <tr>
                  <th>নং</th>
                  <th>কেন্দ্রের নাম ও কোড</th>
                  <th>কাস্ট ভোট</th>
                  <th>প্রার্থীর ভোট ({{data()!.candidate?.symbolEmoji}})</th>
                  <th>নিকটতম প্রতিদ্বন্দ্বী</th>
                  <th>ব্যবধান</th>
                  <th>স্ট্যাটাস</th>
                  <th>কার্যক্রম</th>
                </tr>
              </thead>
              <tbody>
                @for(c of resultsSummary()?.centerResults || []; track c.electionCenterId; let idx = $index){
                  <tr>
                    <td>{{idx + 1}}</td>
                    <td>
                      <b>{{c.centerName}}</b>
                      <span class="sub-cell">কোড: {{c.centerCode}}</span>
                    </td>
                    <td>{{(c.totalCastVotes || (c.candidateVotes + c.runnerUpVotes)) | number}}</td>
                    <td><b class="metric-good">{{c.candidateVotes | number}}</b></td>
                    <td><b style="color: #b91c1c;">{{c.runnerUpVotes | number}}</b></td>
                    <td>
                      <b [class.metric-good]="c.candidateVotes >= c.runnerUpVotes" [class.metric-bad]="c.candidateVotes < c.runnerUpVotes">
                        {{c.candidateVotes >= c.runnerUpVotes ? '+' : ''}}{{c.candidateVotes - c.runnerUpVotes}}
                      </b>
                    </td>
                    <td>
                      @if(c.isCounted){
                        <span class="badge badge-complete">গণনা সম্পন্ন</span>
                      } @else {
                        <span class="badge badge-empty">অপেক্ষমান</span>
                      }
                    </td>
                    <td>
                      <div class="row-actions">
                        <button class="btn-sm form8-btn" (click)="openForm8Modal(c)" title="নির্বাচন কমিশনের ফরম-৮ ফলাফল বিবরণী প্রস্তুত ও প্রিন্ট">
                          📋 ফরম-৮
                        </button>
                        <button class="btn-sm outline" (click)="openQuickResultModal(c.electionCenterId, c.candidateVotes, c.runnerUpVotes)" title="ফলাফল এন্ট্রি বা সংশোধন">
                          ✏️ এডিট
                        </button>
                      </div>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="8" class="empty-cell">কোনো কেন্দ্রের ফলাফল এখনো এন্ট্রি করা হয়নি। উপরের বাটনে ক্লিক করে ফলাফল এন্ট্রি করুন।</td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 7: EC EXPENSE SCHEDULE RETURN -->
        <!-- ================================================================= -->
        @if(activeTab() === 'expenses'){
          <section class="card table-card">
            <div class="table-header">
              <div>
                <h3>নির্বাচন কমিশন আইনানুগ নির্বাচনী ব্যয় বিবরণী (ফরম-১২ রিটার্ন)</h3>
                <span style="font-size: 0.85rem; color: #64748b;">গণপ্রতিনিধিত্ব আদেশ (RPO) অনুযায়ী সর্বোচ্চ ব্যয়সীমা: ৳২৫,০০,০০০ (পঁচিশ লক্ষ টাকা)</span>
              </div>
              <div class="actions">
                <button class="primary-button" (click)="printEcReturnReport()">🖨️ পূর্ণাঙ্গ ব্যয় রিটার্ন প্রিন্ট</button>
              </div>
            </div>

            <!-- Expense Summary Metrics -->
            <div class="metrics-row" style="margin-bottom: 22px; background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid var(--line);">
              <div class="metric">
                <b>৳{{expenseReport()?.ecCeiling || 2500000 | number}}</b>
                <span>সর্বোচ্চ বৈধ ব্যয়সীমা</span>
              </div>
              <div class="metric">
                <b class="metric-good">৳{{expenseReport()?.totalCommitted || 0 | number}}</b>
                <span>মোট ব্যয়কৃত অর্থ</span>
              </div>
              <div class="metric">
                <b class="metric-accent">৳{{expenseReport()?.remainingBudget || 0 | number}}</b>
                <span>অবশিষ্ট ব্যয়সীমা</span>
              </div>
              <div class="metric">
                <b style="color: #047857;">{{expenseReport()?.isWithinCeiling ? '✓ আইনসম্মত' : '⚠️ সীমা অতিক্রম'}}</b>
                <span>ইসি কমপ্লায়েন্স স্ট্যাটাস</span>
              </div>
            </div>

            <!-- Expense Categories Breakdown Table -->
            <table class="data-table">
              <thead>
                <tr>
                  <th>খাত / শিডিউল বিবরণী</th>
                  <th>মোট ব্যয় (টাকা)</th>
                  <th>ভাউচার সংখ্যা</th>
                  <th>আইনানুগ সীমা / নোট</th>
                </tr>
              </thead>
              <tbody>
                @for(cat of expenseReport()?.categories || []; track cat.nameEn){
                  <tr>
                    <td><b>{{cat.nameBn || cat.nameEn}}</b></td>
                    <td><b>৳{{cat.spentAmount | number}}</b></td>
                    <td>{{cat.voucherCount}}টি রসিদ</td>
                    <td><span style="color: #64748b; font-size: 0.82rem;">সঠিক ভাউচার সংরক্ষিত</span></td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="4" class="empty-cell">ব্যয় বিবরণীর কোনো রেকর্ড পাওয়া যায়নি।</td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }

        <!-- ================================================================= -->
        <!-- TAB 8: CAMPAIGN TEAM & SUB-USERS (মাস্টার প্রার্থীর সাব-ইউজার ও কর্মী) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'team'){
          <section class="card table-card">
            <div class="table-header">
              <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                  👥 প্রার্থীর নিজস্ব ক্যাম্পেইন কর্মী ও সাব-ইউজার ব্যবস্থাপনা
                </h3>
                <p style="margin: 4px 0 0; font-size: 0.85rem; color: #64748b;">
                  মাস্টার প্রার্থীর অধীনে সাব-ইউজার ও কর্মী তৈরি করুন। তাদের সব কার্যক্রম স্বয়ংক্রিয়ভাবে এই প্রার্থীর ওয়ার রুমেই জমা হবে।
                </p>
              </div>
              <div class="action-buttons">
                <button class="btn btn-secondary" (click)="loadTeamUsers()" [disabled]="loadingTeamUsers()">
                  🔄 রিফ্রেশ তালিকা
                </button>
                <button class="btn btn-primary" (click)="openCreateTeamUserModal()">
                  ➕ নতুন কর্মী/ইউজার তৈরি করুন
                </button>
              </div>
            </div>

            <!-- Team Users List Table -->
            <table class="data-table">
              <thead>
                <tr>
                  <th>ক্রমিক</th>
                  <th>ব্যবহারকারী নাম (Username)</th>
                  <th>পূর্ণ নাম</th>
                  <th>দায়িত্ব / রোল</th>
                  <th>যোগাযোগ (মোবাইল ও ইমেইল)</th>
                  <th>স্ট্যাটাস</th>
                  <th>তৈরির তারিখ</th>
                  <th style="text-align: right;">অ্যাকশন</th>
                </tr>
              </thead>
              <tbody>
                @for(u of teamUsers(); track u.userId; let idx = $index){
                  <tr>
                    <td>#{{idx + 1}}</td>
                    <td>
                      <span style="font-family: monospace; font-weight: 700; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; color: #0284c7;">
                        {{u.username}}
                      </span>
                    </td>
                    <td>
                      <strong>{{u.displayName}}</strong>
                    </td>
                    <td>
                      <span class="badge" style="background: #e0f2fe; color: #0369a1; font-weight: 600;">
                        {{u.role || 'ক্যাম্পেইন কর্মী'}}
                      </span>
                    </td>
                    <td>
                      <div style="font-size: 0.85rem;">
                        @if(u.phone){ <div>📞 {{u.phone}}</div> }
                        @if(u.email){ <div style="color: #64748b;">✉️ {{u.email}}</div> }
                        @if(!u.phone && !u.email){ <span style="color: #94a3b8;">—</span> }
                      </div>
                    </td>
                    <td>
                      <span class="status-pill" [class.status-active]="u.isActive" [class.status-absent]="!u.isActive">
                        {{u.isActive ? 'সক্রিয় (Active)' : 'নিষ্ক্রিয় (Inactive)'}}
                      </span>
                    </td>
                    <td style="font-size: 0.82rem; color: #64748b;">
                      {{u.createdAtUtc | date:'shortDate'}}
                    </td>
                    <td style="text-align: right;">
                      <div style="display: flex; gap: 6px; justify-content: flex-end;">
                        <button class="btn btn-sm btn-secondary" (click)="openResetPasswordModal(u)" title="পাসওয়ার্ড পরিবর্তন">
                          🔑 রিসেট
                        </button>
                        <button class="btn btn-sm" [class.btn-danger]="u.isActive" [class.btn-primary]="!u.isActive" (click)="toggleTeamUserStatus(u)">
                          {{u.isActive ? 'নিষ্ক্রিয় করুন' : 'সক্রিয় করুন'}}
                        </button>
                      </div>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="8" class="empty-cell" style="padding: 40px 20px; text-align: center;">
                      <div style="font-size: 2.5rem; margin-bottom: 10px;">👥</div>
                      <h4 style="margin: 0 0 6px; color: #334155;">এখনও কোনো ক্যাম্পেইন কর্মী বা সাব-ইউজার তৈরি করা হয়নি</h4>
                      <p style="margin: 0 0 16px; color: #64748b; font-size: 0.9rem;">
                        আপনার নির্বাচনী কাজের জন্য কো-অর্ডিনেটর, ডাটা এন্ট্রি বা পোলিং এজেন্টের নিজস্ব ইউজার আইডি তৈরি করতে উপরের বাটনে ক্লিক করুন।
                      </p>
                      <button class="btn btn-primary" (click)="openCreateTeamUserModal()">
                        ➕ নতুন কর্মী/ইউজার তৈরি করুন
                      </button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </section>
        }
      }
    </div>


    <!-- ===================================================================== -->
    <!-- MODAL 1: ADD / APPOINT BOOTH AGENT -->
    <!-- ===================================================================== -->
    @if(showAddAgentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন পোলিং এজেন্ট নিয়োগ ফর্ম</h2>
            <button class="close-btn" (click)="closeAddAgentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewBoothAgent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র নির্বাচন করুন *</label>
                <select [(ngModel)]="newAgentForm.centerId" name="centerId" (change)="onResultCenterSelectChange()" required>
                  <option value="" disabled>ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>ভোটকক্ষ / বুথ নম্বর *</label>
                <select [(ngModel)]="newAgentForm.boothId" name="boothId" required>
                  <option value="" disabled>বুথ পছন্দ করুন</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>এজেন্টের ধরন *</label>
                <select [(ngModel)]="newAgentForm.agentType" name="agentType" required>
                  <option value="PRIMARY">মূল এজেন্ট (Primary)</option>
                  <option value="RESERVE">বিকল্প এজেন্ট (Reserve)</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>এজেন্টের পূর্ণ নাম *</label>
                <input [(ngModel)]="newAgentForm.fullName" name="fullName" required placeholder="যেমন: মো: কামরুল ইসলাম">
              </div>

              <div class="form-field">
                <label>জাতীয় পরিচয়পত্র নম্বর (NID) *</label>
                <input [(ngModel)]="newAgentForm.nidNumber" name="nidNumber" required placeholder="১০ বা ১৭ ডিজিটের NID">
              </div>

              <div class="form-field">
                <label>ভোটার নম্বর</label>
                <input [(ngModel)]="newAgentForm.voterNumber" name="voterNumber" placeholder="যেমন: VOT-10492">
              </div>

              <div class="form-field">
                <label>মোবাইল ফোন নম্বর *</label>
                <input [(ngModel)]="newAgentForm.phone" name="phone" required placeholder="যেমন: 01711223344">
              </div>

              <div class="form-field wide">
                <label>মন্তব্য / দায়িত্ব পালনের নোট</label>
                <input [(ngModel)]="newAgentForm.notes" name="notes" placeholder="যেমন: সকাল ৭টায় উপস্থিতি ও ব্যালট বাক্স পরীক্ষা">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddAgentModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingAgent()">
                {{savingAgent() ? 'সংরক্ষণ হচ্ছে…' : 'পোলিং এজেন্ট নিয়োগ নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 2: PRINTABLE BANGLADESH ELECTION COMMISSION FORM-9 -->
    <!-- ===================================================================== -->
    @if(selectedAgentForForm9()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>ফরম-৯ প্রিন্ট প্রিভিউ (পোলিং এজেন্ট নিয়োগপত্র)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeForm9Preview()">✕</button>
            </div>
          </div>

          <div class="official-form9-paper">
            <div class="form9-header">
              <div class="gov-seal">🇧🇩</div>
              <h2 class="form9-title">ফরম - ৯</h2>
              <p class="form9-sub">[বিধি ২৪ (১) দ্রষ্টব্য]</p>
              <h3 class="form9-main-title">পোলিং এজেন্ট নিয়োগপত্র</h3>
            </div>

            <div class="form9-body">
              <p>বরাবর,</p>
              <p class="recipient-line">
                প্রিজাইডিং অফিসার,<br/>
                <b>{{selectedAgentForForm9()!.centerName}}</b> ভোটকেন্দ্র।
              </p>

              <p class="paragraph-text">
                আমি <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b>, নির্বাচনী এলাকা: <b>{{data()!.areaName || 'নির্বাচনী এলাকা'}}</b>
                (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn}}</b>)-এর
                প্রতিদ্বন্দ্বী প্রার্থী হিসেবে এতদ্বারা নিম্নবর্ণিত ব্যক্তিকে অত্র ভোটকেন্দ্রে
                <b>{{selectedAgentForForm9()!.boothName || 'সকল বুথে'}}</b> আমার পোলিং এজেন্ট হিসেবে দায়িত্ব পালনের জন্য নিয়োগ প্রদান করিলাম।
              </p>

              <div class="agent-spec-table">
                <table>
                  <tr>
                    <td class="lbl">পোলিং এজেন্টের নাম:</td>
                    <td class="val"><b>{{selectedAgentForForm9()!.fullName}}</b></td>
                  </tr>
                  <tr>
                    <td class="lbl">জাতীয় পরিচয়পত্র নম্বর (NID):</td>
                    <td class="val"><b>{{selectedAgentForForm9()!.nidNumber}}</b></td>
                  </tr>
                  <tr>
                    <td class="lbl">ভোটার তালিকা নম্বর:</td>
                    <td class="val">{{selectedAgentForForm9()!.voterNumber || 'প্রযোজ্য'}}</td>
                  </tr>
                  <tr>
                    <td class="lbl">যোগাযোগের মোবাইল নম্বর:</td>
                    <td class="val">{{selectedAgentForForm9()!.phone}}</td>
                  </tr>
                  <tr>
                    <td class="lbl">দায়িত্বের ধরন:</td>
                    <td class="val">{{selectedAgentForForm9()!.agentType === 'PRIMARY' ? 'মূল পোলিং এজেন্ট' : 'বিকল্প এজেন্ট'}}</td>
                  </tr>
                </table>
              </div>

              <div class="declaration-block">
                <p><b>এজেন্টের সম্মতি ও অঙ্গীকার:</b></p>
                <p class="declaration-text">
                  আমি অত্র ভোটকেন্দ্রে প্রতিদ্বন্দ্বী প্রার্থীর পোলিং এজেন্ট হিসেবে দায়িত্ব পালনে সম্মত আছি
                  এবং ভোটগ্রহণের গোপনীয়তা ও নির্বাচন কমিশনের সকল আইন ও আচরণবিধি যথাযথভাবে মানিয়া চলিব।
                </p>
              </div>

              <div class="signatures-row">
                <div class="sig-col">
                  <div class="sig-line"></div>
                  <b>{{selectedAgentForForm9()!.fullName}}</b>
                  <p class="sig-caption">নিযুক্ত পোলিং এজেন্টের স্বাক্ষর ও তারিখ</p>
                </div>
                <div class="sig-col">
                  <div class="sig-line"></div>
                  <b>{{data()!.candidate?.name || 'প্রার্থীর স্বাক্ষর'}}</b>
                  <p class="sig-caption">প্রতিদ্বন্দ্বী প্রার্থী / প্রধান নির্বাচনী এজেন্টের স্বাক্ষর</p>
                  <p class="sig-symbol">প্রতীক: {{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 3: SINGLE AGENT ID BADGE -->
    <!-- ===================================================================== -->
    @if(selectedAgentForBadge()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>পোলিং এজেন্ট পরিচয়পত্র (Badge Preview)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeAgentBadge()">✕</button>
            </div>
          </div>

          <div class="agent-badge-paper">
            <div class="badge-head">
              <span class="badge-emblem">🇧🇩</span>
              <div class="badge-title-block">
                <p class="badge-org">বাংলাদেশ নির্বাচন কমিশন</p>
                <h4 class="badge-type">পোলিং এজেন্ট পরিচয়পত্র</h4>
              </div>
            </div>

            <div class="badge-symbol-hero">
              <span class="badge-symbol-emoji">{{data()!.candidate?.symbolEmoji || '🗳️'}}</span>
              <div class="badge-cand-details">
                <span class="badge-cand-name">{{data()!.candidate?.name}}</span>
                <span class="badge-symbol-txt">{{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn}} মার্কা</span>
              </div>
            </div>

            <div class="badge-photo-id-row">
              <div class="badge-photo-box">
                @if(selectedAgentForBadge()!.photoUrl){
                  <img [src]="selectedAgentForBadge()!.photoUrl" alt="agent" class="badge-img">
                } @else {
                  <div class="badge-placeholder">ছবির স্থান</div>
                }
              </div>
              <div class="badge-bio">
                <div class="badge-field">
                  <span class="lbl">নাম:</span>
                  <b class="val">{{selectedAgentForBadge()!.fullName}}</b>
                </div>
                <div class="badge-field">
                  <span class="lbl">কেন্দ্র:</span>
                  <span class="val">{{selectedAgentForBadge()!.centerName}}</span>
                </div>
                <div class="badge-field">
                  <span class="lbl">বুথ নং:</span>
                  <b class="val">{{selectedAgentForBadge()!.boothName || 'সকল বুথ'}}</b>
                </div>
                <div class="badge-field">
                  <span class="lbl">NID:</span>
                  <span class="val mono">{{selectedAgentForBadge()!.nidNumber}}</span>
                </div>
                <div class="badge-field">
                  <span class="lbl">মোবাইল:</span>
                  <span class="val">{{selectedAgentForBadge()!.phone}}</span>
                </div>
              </div>
            </div>

            <div class="badge-footer">
              <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 4: BATCH ID CARDS (Photo ID Card Generator - 4 per page with QR) -->
    <!-- ===================================================================== -->
    @if(showBatchIdCardsModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(920px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <div>
              <h2>🪪 পোলিং এজেন্টদের অফিশিয়াল ব্যাচ আইডি কার্ড (Batch Print)</h2>
              <span style="font-size: 0.85rem; color: #64748b;">প্রতিটি কেন্দ্রের বুথ এজেন্টদের জন্য প্রার্থীর প্রতীক, নাম, কিউআর কোড এবং বুথ নম্বরসহ আইডি কার্ড (৪টি প্রতি পেইজ)</span>
            </div>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ব্যাচ প্রিন্ট করুন (A4)</button>
              <button class="close-btn" (click)="closeBatchIdCardsModal()">✕</button>
            </div>
          </div>

          <div class="batch-id-cards-page">
            <div class="batch-cards-grid">
              @for(ag of boothAgents(); track ag.boothAgentId){
                <div class="official-agent-card">
                  <!-- Header -->
                  <div class="card-ec-header">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span style="font-size: 1.4rem;">🇧🇩</span>
                      <div>
                        <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: #1e293b;">বাংলাদেশ নির্বাচন ২০২৬</div>
                        <div style="font-size: 0.82rem; font-weight: 800; color: #047857;">অফিসিয়াল পোলিং এজেন্ট কার্ড</div>
                      </div>
                    </div>
                    <span style="font-size: 0.7rem; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: 700;">FORM-9 ISSUED</span>
                  </div>

                  <!-- Candidate & Symbol Row -->
                  <div class="card-candidate-banner">
                    <span class="card-symbol-badge">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                    <div style="flex: 1; min-width: 0;">
                      <b style="font-size: 0.95rem; color: #064e3b; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{data()?.candidate?.name || 'প্রার্থী'}}</b>
                      <span style="font-size: 0.78rem; color: #047857; font-weight: 700;">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}} মার্কা · {{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</span>
                    </div>
                  </div>

                  <!-- Agent Details & QR Code Row -->
                  <div class="card-details-grid">
                    <div class="card-photo-box">
                      @if(ag.photoUrl){
                        <img [src]="ag.photoUrl" alt="agent" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px;">
                      } @else {
                        <div class="photo-placeholder-box">
                          <span>👤</span>
                          <small>ছবি</small>
                        </div>
                      }
                    </div>

                    <div class="card-info-col">
                      <div class="info-row">
                        <span class="info-k">এজেন্টের নাম:</span>
                        <b class="info-v">{{ag.fullName}}</b>
                      </div>
                      <div class="info-row">
                        <span class="info-k">ভোটকেন্দ্র:</span>
                        <span class="info-v" style="font-weight: 700;">{{ag.centerName}}</span>
                      </div>
                      <div class="info-row highlight-booth">
                        <span class="info-k">নির্ধারিত বুথ:</span>
                        <b class="info-v" style="color: #047857; font-size: 0.9rem;">{{ag.boothName || 'সকল বুথ / সাধারণ'}}</b>
                      </div>
                      <div class="info-row">
                        <span class="info-k">NID নং:</span>
                        <span class="info-v mono">{{ag.nidNumber}}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-k">মোবাইল:</span>
                        <span class="info-v mono">{{ag.phone}}</span>
                      </div>
                    </div>

                    <!-- Dynamic QR Code -->
                    <div class="card-qr-box">
                      @if(batchAgentQrCodes()[ag.boothAgentId]){
                        <img [src]="batchAgentQrCodes()[ag.boothAgentId]" alt="Agent QR" style="width: 72px; height: 72px; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px; background: #fff;">
                      } @else {
                        <div style="width: 72px; height: 72px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; color: #64748b; text-align: center;">QR Code</div>
                      }
                      <small style="font-size: 0.6rem; color: #64748b; margin-top: 2px;">বৈধতা যাচাই</small>
                    </div>
                  </div>

                  <!-- Footer -->
                  <div class="card-ec-footer">
                    <span>বৈধতা: ভোটগ্রহণের দিন সকাল ৮:০০ - ফলাফল ঘোষণা</span>
                    <span>স্মারক: FORM9/{{ag.boothAgentId.slice(0,6).toUpperCase()}}</span>
                  </div>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 5: ADD NEW VOTER -->
    <!-- ===================================================================== -->
    @if(showAddVoterModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন ভোটার তথ্য এন্ট্রি</h2>
            <button class="close-btn" (click)="closeAddVoterModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewVoter()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র *</label>
                <select [(ngModel)]="newVoterForm.centerId" name="vCenter" required (change)="onVoterCenterChange()">
                  <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>নির্ধারিত বুথ (ঐচ্ছিক)</label>
                <select [(ngModel)]="newVoterForm.boothId" name="vBooth">
                  <option [ngValue]="null">সাধারণ / অনির্ধারিত বুথ</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>ভোটার তালিকা ক্রমিক নং *</label>
                <input type="number" [(ngModel)]="newVoterForm.serialNumber" name="vSerial" min="1" required>
              </div>

              <div class="form-field">
                <label>ভোটার নম্বর (Voter ID) *</label>
                <input [(ngModel)]="newVoterForm.voterNumber" name="vNumber" required placeholder="যেমন: VOT-10492">
              </div>

              <div class="form-field">
                <label>ভোটারের নাম *</label>
                <input [(ngModel)]="newVoterForm.fullName" name="vName" required placeholder="ভোটারের পূর্ণ নাম">
              </div>

              <div class="form-field">
                <label>পিতা / স্বামীর নাম</label>
                <input [(ngModel)]="newVoterForm.fatherOrSpouseName" name="vFather" placeholder="পিতা বা স্বামীর নাম">
              </div>

              <div class="form-field">
                <label>লিঙ্গ</label>
                <select [(ngModel)]="newVoterForm.gender" name="vGender">
                  <option value="MALE">পুরুষ (Male)</option>
                  <option value="FEMALE">নারী (Female)</option>
                </select>
              </div>

              <div class="form-field">
                <label>বয়স</label>
                <input type="number" [(ngModel)]="newVoterForm.age" name="vAge" min="18" max="120" placeholder="বয়স">
              </div>

              <div class="form-field">
                <label>গ্রাম / পাড়া / এলাকা</label>
                <input [(ngModel)]="newVoterForm.areaName" name="vArea" placeholder="গ্রাম বা পাড়ার নাম">
              </div>

              <div class="form-field">
                <label>ক্যাটাগরি</label>
                <select [(ngModel)]="newVoterForm.category" name="vCat">
                  <option value="SUPPORTER">বিশ্বস্ত সমর্থক (SUPPORTER)</option>
                  <option value="SWING">নিরপেক্ষ / দোদুল্যমান (SWING)</option>
                  <option value="OPPONENT">প্রতিপক্ষ সমর্থক (OPPONENT)</option>
                  <option value="ABROAD">প্রবাসী / অনুপস্থিত (ABROAD)</option>
                </select>
              </div>

              <div class="form-field">
                <label>মোবাইল নম্বর</label>
                <input [(ngModel)]="newVoterForm.phone" name="vPhone" placeholder="017xxxxxxxx">
              </div>

              <div class="form-field wide">
                <label>মন্তব্য</label>
                <input [(ngModel)]="newVoterForm.notes" name="vNotes" placeholder="বিশেষ কোনো তথ্য থাকলে লিখুন">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddVoterModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingVoter()">
                {{savingVoter() ? 'সংরক্ষণ হচ্ছে…' : 'ভোটার যুক্ত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 6: BULK VOTER IMPORT (Excel / CSV / PDF) -->
    <!-- ===================================================================== -->
    @if(showBulkImportModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(720px, 95vw);">
          <div class="modal-header">
            <h2>📥 বাল্ক ভোটার তালিকা ইম্পোর্ট (Excel / CSV / PDF)</h2>
            <button class="close-btn" (click)="closeBulkImportModal()">✕</button>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <p style="font-size: 0.88rem; color: #475569; margin: 0;">
              নির্বাচন কমিশনের ভোটার তালিকার Excel (.xlsx) বা CSV ফাইল আপলোড করে এক ক্লিকে সকল ভোটারের তথ্য যুক্ত করুন।
            </p>

            <div class="form-field">
              <label>ডিফল্ট ভোটকেন্দ্র নির্বাচন করুন *</label>
              <select [(ngModel)]="bulkImportCenterId" (change)="onBulkCenterChange()">
                <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                @for(c of centersList(); track c.centerId){
                  <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                }
              </select>
            </div>

            <div style="border: 2px dashed var(--line); border-radius: 12px; padding: 24px; text-align: center; background: #f8fafc;">
              <input type="file" (change)="onBulkFileSelected($event)" accept=".xlsx,.csv,.pdf,.txt" style="display: none;" #bulkFileInput>
              <span style="font-size: 2.2rem; display: block; margin-bottom: 8px;">📑</span>
              <button type="button" class="primary-button" (click)="bulkFileInput.click()">ফাইল বাছাই করুন (.xlsx / .csv)</button>
              <span style="display: block; font-size: 0.78rem; color: #64748b; margin-top: 8px;">বা ড্র্যাগ করে এখানে ফেলুন</span>
            </div>

            @if(bulkPreview()){
              <div style="background: #f1f5f9; padding: 12px; border-radius: 8px; font-size: 0.85rem;">
                <b>প্রিভিউ:</b> মোট {{bulkPreview()!.totalRowsDetected}}টি রেকর্ড পাওয়া গেছে (বৈধ: {{bulkPreview()!.validRowsCount}}, ত্রুটি: {{bulkPreview()!.invalidRowsCount}})।
              </div>
            }

            <div class="modal-actions" style="margin-top: 10px;">
              <button type="button" class="text-button" (click)="closeBulkImportModal()">বাতিল</button>
              <button class="primary-button" [disabled]="importingBulk() || !bulkPreview()" (click)="confirmBulkImport()">
                {{importingBulk() ? 'ইম্পোর্ট হচ্ছে…' : 'ইম্পোর্ট নিশ্চিত করুন'}}
              </button>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 7: BATCH VOTER SLIPS PRINT PREVIEW -->
    <!-- ===================================================================== -->
    @if(showVoterSlipsPrint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card wide-slip-modal" style="width: min(850px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <h2>ভোটার স্লিপ প্রিন্ট প্রিভিউ (প্রার্থীর মার্কা ও ভোটার তথ্য)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন (A4)</button>
              <button class="close-btn" (click)="closeVoterSlipsPrint()">✕</button>
            </div>
          </div>

          <div class="voter-slips-page">
            <div class="voter-slips-grid">
              @for(v of voters(); track v.id){
                <div class="voter-slip-card">
                  <div class="slip-header">
                    <span class="slip-symbol-emoji">{{data()!.candidate?.symbolEmoji || '🗳️'}}</span>
                    <div class="slip-cand-info">
                      <b class="slip-cand-name">{{data()!.candidate?.name || 'প্রার্থীর নাম'}}</b>
                      <span class="slip-symbol-name">{{data()!.candidate?.symbolNameBn || data()!.candidate?.symbolNameEn || 'মার্কা'}} মার্কা</span>
                    </div>
                  </div>
                  @if(data()!.candidate?.slogan){
                    <div class="slip-slogan">"{{data()!.candidate?.slogan}}"</div>
                  }
                  <div class="slip-body">
                    <div class="slip-serial-row">
                      <span>তালিকা ক্রমিক:</span>
                      <b class="slip-serial-num">#{{v.serialNumber}}</b>
                    </div>
                    <div class="slip-row">
                      <span>ভোটারের নাম:</span>
                      <b>{{v.fullName}}</b>
                    </div>
                    <div class="slip-row">
                      <span>ভোটার নম্বর:</span>
                      <span>{{v.voterNumber}}</span>
                    </div>
                    <div class="slip-row">
                      <span>ভোটকেন্দ্র:</span>
                      <span>{{v.centerName}}</span>
                    </div>
                    @if(v.boothName){
                      <div class="slip-row">
                        <span>নির্ধারিত বুথ:</span>
                        <b>{{v.boothName}}</b>
                      </div>
                    }
                    @if(v.areaName){
                      <div class="slip-row">
                        <span>গ্রাম / এলাকা:</span>
                        <span>{{v.areaName}}</span>
                      </div>
                    }
                  </div>
                  <div class="slip-footer">
                    <span>আপনার মূল্যবান ভোট দিয়ে এলাকার উন্নয়নে অংশ নিন।</span>
                  </div>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 8: SMART DIGITAL VOTER SLIP CARD WITH QR CODE (Digital Pass) -->
    <!-- ===================================================================== -->
    @if(selectedVoterForSlip()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card smart-slip-modal-card" style="width: min(540px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h2>🎫 স্মার্ট ডিজিটাল ভোটার স্লিপ (Digital Pass)</h2>
            <button class="close-btn" (click)="closeSmartSlip()">✕</button>
          </div>

          <!-- Digital Card View -->
          <div class="digital-slip-card" style="background: linear-gradient(135deg, #064e3b, #047857); color: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px rgba(4,120,87,0.3); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 12px; margin-bottom: 14px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.8rem; background: rgba(255,255,255,0.15); border-radius: 12px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                <div>
                  <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #fff;">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</h3>
                  <p style="margin: 2px 0 0; font-size: 0.85rem; color: #a7f3d0; font-weight: 600;">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}} মার্কা · {{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</p>
                </div>
              </div>
              <div style="text-align: right;">
                <span style="display: block; font-size: 0.75rem; text-transform: uppercase; color: #6ee7b7; font-weight: 700;">তালিকা ক্রমিক</span>
                <b style="font-size: 1.8rem; line-height: 1; color: #fef08a;">#{{selectedVoterForSlip()!.serialNumber}}</b>
              </div>
            </div>

            <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 14px; margin-bottom: 14px;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">ভোটারের নাম:</span>
                  <b style="font-size: 1rem; color: #fff;">{{selectedVoterForSlip()!.fullName}}</b>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">পিতা/স্বামীর নাম:</span>
                  <span style="color: #f3f4f6;">{{selectedVoterForSlip()!.fatherOrSpouseName || '—'}}</span>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">জাতীয় পরিচয়পত্র (NID):</span>
                  <b style="letter-spacing: 0.5px; color: #fef08a;">{{selectedVoterForSlip()!.voterNumber}}</b>
                </div>
                <div>
                  <span style="display: block; font-size: 0.75rem; color: #a7f3d0;">বয়স ও লিঙ্গ:</span>
                  <span>{{selectedVoterForSlip()!.age || '—'}} বছর ({{selectedVoterForSlip()!.gender === 'FEMALE' ? 'নারী' : 'পুরুষ'}})</span>
                </div>
              </div>
            </div>

            <!-- Polling Center Highlight -->
            <div style="background: #ffffff; color: #0f172a; border-radius: 12px; padding: 14px; display: flex; justify-content: space-between; align-items: center; gap: 14px;">
              <div style="flex: 1;">
                <span style="display: block; font-size: 0.72rem; text-transform: uppercase; color: #047857; font-weight: 800; letter-spacing: 0.5px;">নির্ধারিত ভোটকেন্দ্র</span>
                <b style="font-size: 1.05rem; color: #064e3b; display: block; margin: 2px 0;">{{selectedVoterForSlip()!.centerName}}</b>
                <span style="font-size: 0.85rem; color: #475569; display: flex; align-items: center; gap: 6px;">
                  <span>বুথ: <b style="color: #047857;">{{selectedVoterForSlip()!.boothName || 'সাধারণ বুথ'}}</b></span>
                  @if(selectedVoterForSlip()!.areaName){
                    <span>· এলাকা: {{selectedVoterForSlip()!.areaName}}</span>
                  }
                </span>
              </div>

              <!-- Dynamic QR Code Container -->
              <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px; text-align: center;">
                @if(voterQrCodeDataUrl()){
                  <img [src]="voterQrCodeDataUrl()" alt="Voter QR" style="width: 84px; height: 84px; display: block;">
                } @else {
                  <div style="width: 84px; height: 84px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #94a3b8;">QR কোড</div>
                }
                <span style="display: block; font-size: 0.65rem; color: #64748b; font-weight: 600; margin-top: 2px;">ডিজিটাল ভেরিফিকেশন</span>
              </div>
            </div>

            <div style="margin-top: 14px; text-align: center; font-size: 0.8rem; color: #a7f3d0; border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 10px;">
              ভোটগ্রহণের দিন এই ডিজিটাল কার্ড বা প্রিন্ট কপি সাথে নিয়ে কেন্দ্রে উপস্থিত হোন।
            </div>
          </div>

          <!-- Actions: WhatsApp 1-Click + Print -->
          <div style="display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap;">
            <button class="primary-button" style="background: #25d366; color: #fff; border: none; display: flex; align-items: center; gap: 8px;" (click)="sendSingleVoterWhatsApp(selectedVoterForSlip()!)" [disabled]="!selectedVoterForSlip()!.phone">
              <span>💬</span> হোয়াটসঅ্যাপে ডিজিটাল স্লিপ পাঠান (1-Click)
            </button>
            <button class="btn-sm" style="background: #0369a1; color: #fff;" (click)="triggerBrowserPrint()">
              🖨️ স্লিপ প্রিন্ট করুন
            </button>
            <button class="text-button" (click)="closeSmartSlip()">বন্ধ করুন</button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 9: CANDIDATE BULK VOTER BROADCAST (SMS & Free WhatsApp Dispatcher) -->
    <!-- ===================================================================== -->
    @if(showVoterBroadcastModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(680px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <div>
              <h2 style="margin: 0;">📱 ভোটার বাল্ক ম্যাসেজিং ও ডিজিটাল স্লিপ ডিসপ্যাচ</h2>
              <span style="font-size: 0.85rem; color: #64748b;">সকল ভোটারকে এক ক্লিকে কেন্দ্র, বুথ, ক্রমিক নম্বর ও মার্কার তথ্যসহ স্মার্ট স্লিপ পাঠান</span>
            </div>
            <button class="close-btn" (click)="closeVoterBroadcastModal()">✕</button>
          </div>

          <!-- Channel Selection Tabs -->
          <div style="display: flex; gap: 10px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;">
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'WHATSAPP'" (click)="voterBroadcastChannel.set('WHATSAPP')" style="flex: 1; padding: 10px 14px; border-radius: 8px; border: 1px solid #25d366; background: voterBroadcastChannel() === 'WHATSAPP' ? '#dcfce7' : '#fff'; font-weight: 700; color: #166534; cursor: pointer;">
              🟢 হোয়াটসঅ্যাপ ডিসপ্যাচ (ফ্রি / ০ টাকা)
            </button>
            <button class="tab-btn" [class.active]="voterBroadcastChannel() === 'SMS'" (click)="voterBroadcastChannel.set('SMS')" style="flex: 1; padding: 10px 14px; border-radius: 8px; border: 1px solid #0284c7; background: voterBroadcastChannel() === 'SMS' ? '#e0f2fe' : '#fff'; font-weight: 700; color: #0369a1; cursor: pointer;">
              📱 মোবাইল বাল্ক SMS গেটওয়ে
            </button>
          </div>

          <!-- WhatsApp Sub-mode & Live Bot QR Controller -->
          @if(voterBroadcastChannel() === 'WHATSAPP'){
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">
              <label style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 8px;">হোয়াটসঅ্যাপ প্রেরণের মোড:</label>
              <div style="display: flex; gap: 10px;">
                <button type="button" [class.active-pill]="waDispatchMode() === 'AUTO_BOT'" (click)="waDispatchMode.set('AUTO_BOT')" class="target-pill" style="flex: 1; text-align: center; padding: 8px 12px; font-weight: 700;">
                  🤖 ১০০% অটো-বট (কোনো ক্লিক ছাড়া একা একা যাবে)
                </button>
                <button type="button" [class.active-pill]="waDispatchMode() === 'MANUAL_CLICK'" (click)="waDispatchMode.set('MANUAL_CLICK')" class="target-pill" style="flex: 1; text-align: center; padding: 8px 12px; font-weight: 700;">
                  📱 ১-ক্লিক ওয়েব কিউ (ব্রাউজার দিয়ে পাঠানো)
                </button>
              </div>

              <!-- Live Auto-Bot Section -->
              @if(waDispatchMode() === 'AUTO_BOT'){
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                  @if(waBotStatus()?.connected){
                    <div style="background: #dcfce7; border: 1px solid #86efac; border-radius: 8px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;">
                      <div>
                        <b style="color: #166534; font-size: 0.95rem; display: block;">✅ হোয়াটসঅ্যাপ রোবট সংযুক্ত রয়েছে!</b>
                        <span style="font-size: 0.82rem; color: #15803d;">প্রেরক অ্যাকাউন্ট: <b>+{{waBotStatus()?.phone}}</b></span>
                      </div>
                      <button type="button" class="btn-sm outline" style="color: #b91c1c; border-color: #fca5a5;" (click)="logoutWaBot()">
                        লগআউট / নতুন নম্বর
                      </button>
                    </div>

                    @if(waBotStatus()?.queueStats?.status === 'PROCESSING'){
                      <div style="margin-top: 10px; background: #fff; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; color: #166534; margin-bottom: 4px;">
                          <span>🔄 ব্যাকগ্রাউন্ডে ভোটারদের পাঠানো হচ্ছে…</span>
                          <span>{{waBotStatus()?.queueStats?.sent}} / {{waBotStatus()?.queueStats?.total}} সম্পন্ন</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b;">
                          বর্তমান ভোটার: <b>{{waBotStatus()?.queueStats?.currentVoter || 'প্রস্তুত হচ্ছে…'}}</b> (স্প্যাম সুরক্ষা বিরতি: ৩.৫ সেঃ)
                        </div>
                      </div>
                    }
                  } @else {
                    <div style="background: #fff; border: 2px dashed #38bdf8; border-radius: 10px; padding: 16px; text-align: center;">
                      <h4 style="margin: 0 0 6px; color: #0369a1;">📱 আপনার মোবাইল WhatsApp দিয়ে একবার কিউআর স্ক্যান করুন</h4>
                      <p style="margin: 0 0 10px; font-size: 0.82rem; color: #64748b;">
                        ফোনের WhatsApp অ্যাপ খুলুন ➔ Settings ➔ <b>Linked Devices</b> ➔ <b>Link a Device</b> নির্বাচন করে ক্যামেরা দিয়ে নিচের কিউআর কোডটি স্ক্যান করুন:
                      </p>
                      @if(waBotQr()){
                        <img [src]="waBotQr()" alt="WhatsApp Pairing QR" style="width: 190px; height: 190px; border-radius: 8px; border: 3px solid #e2e8f0; margin-bottom: 8px;">
                      } @else {
                        <div style="padding: 30px; color: #94a3b8;">কিউআর কোড জেনারেট হচ্ছে…</div>
                      }
                      <div>
                        <button type="button" class="btn-sm outline" (click)="loadWaBotStatus()">🔄 কিউআর রিফ্রেশ করুন</button>
                      </div>
                    </div>
                  }
                </div>
              }
            </div>
          }

          <!-- Target Filter Group -->
          <div class="form-field" style="margin-bottom: 14px;">
            <label style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 6px;">প্রাপক ভোটার ফিল্টার:</label>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px;">
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'ALL'" (click)="voterBroadcastTarget.set('ALL')" class="target-pill">
                সব ভোটার ({{phonesCount()}} জন)
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'UNISSUED_SLIP_ONLY'" (click)="voterBroadcastTarget.set('UNISSUED_SLIP_ONLY')" class="target-pill">
                স্লিপ বাকি ({{voters().length - issuedSlipsCount()}} জন)
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'SUPPORTERS'" (click)="voterBroadcastTarget.set('SUPPORTERS')" class="target-pill">
                সমর্থক ভোটার
              </button>
              <button type="button" [class.active-pill]="voterBroadcastTarget() === 'SWING'" (click)="voterBroadcastTarget.set('SWING')" class="target-pill">
                দোদুল্যমান ভোটার
              </button>
            </div>
          </div>

          <!-- Message Composer with Dynamic Tags -->
          <div class="form-field" style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <label style="font-weight: 700; color: var(--navy);">বার্তা প্রস্তুত করুন (Dynamic Voter Tags):</label>
              <span style="font-size: 0.78rem; color: #64748b;">ক্লিক করে ট্যাগ যুক্ত করুন</span>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px;">
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{নাম}')">+ ভোটারের নাম</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{ভোটকেন্দ্র}')">+ ভোটকেন্দ্র</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{বুথ}')">+ বুথ</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{ক্রমিক}')">+ ক্রমিক নং</button>
              <button type="button" class="btn-sm outline tag-btn" (click)="insertBroadcastTag('{মার্কা}')">+ প্রার্থীর মার্কা</button>
            </div>
            <textarea [(ngModel)]="voterBroadcastCustomMessage" rows="4" style="width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px; font-size: 0.9rem;" placeholder="বার্তা লিখুন..."></textarea>
          </div>

          <!-- Live Preview & Cost Banner -->
          <div style="background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 12px; margin-bottom: 16px; font-size: 0.85rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span style="color: #64748b; font-weight: 600;">নমুনা মেসেজ প্রিভিউ:</span>
              <span style="color: #0369a1; font-weight: 700;">{{smsCharCount()}} অক্ষর · {{smsPartsCount()}} SMS পার্ট</span>
            </div>
            <div style="background: #fff; border-left: 3px solid #10b981; padding: 8px 12px; border-radius: 0 6px 6px 0; font-style: italic; color: #334155;">
              {{getInterpolatedPreview()}}
            </div>
            @if(voterBroadcastChannel() === 'SMS'){
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0;">
                <span>আনুমানিক মোট খরচ: <b>৳{{calculateSmsCost() | number:'1.2-2'}}</b> (প্রতি SMS ৳০.৩০)</span>
                <span style="color: #059669; font-weight: 700;">গেটওয়ে ব্যালেন্স: ৳{{smsConfig()?.balance || 2499.10 | number:'1.2-2'}}</span>
              </div>
            } @else {
              <div style="margin-top: 8px; color: #166534; font-weight: 700;">
                ✓ হোয়াটসঅ্যাপ কিউ সম্পূর্ণ বিনামূল্যে (৳০.০০) পরিচালিত হবে।
              </div>
            }
          </div>

          <!-- WhatsApp Interactive Auto-Queue Dispatcher -->
          @if(voterBroadcastQueue().length > 0){
            <div class="whatsapp-queue-box" style="border: 2px solid #25d366; border-radius: 12px; padding: 16px; background: #f0fdf4; margin-bottom: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <b style="color: #166534; font-size: 1rem;">হোয়াটসঅ্যাপ প্রেরক কিউ ({{dispatchCurrentIndex() + 1}} / {{voterBroadcastQueue().length}})</b>
                <span class="badge badge-complete">{{calcQueuePercent() | number:'1.0-0'}}% সম্পন্ন</span>
              </div>

              @if(dispatchCurrentIndex() < voterBroadcastQueue().length){
                <div style="background: #fff; border-radius: 8px; padding: 12px; border: 1px solid #bbf7d0; margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <b style="font-size: 1.05rem; color: #064e3b;">{{currentQueueItem()!.fullName}}</b>
                      <span style="display: block; font-size: 0.82rem; color: #475569;">{{currentQueueItem()!.phone}} · কেন্দ্র: {{currentQueueItem()!.centerName}}</span>
                    </div>
                    <a [href]="currentQueueItem()!.waUrl" target="_blank" class="primary-button" style="background: #25d366; text-decoration: none;" (click)="dispatchNextInQueue()">
                      💬 হোয়াটসঅ্যাপে পাঠান ➔
                    </a>
                  </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <button type="button" class="btn-sm" [class.highlight-btn]="isAutoDispatching()" (click)="toggleAutoDispatch()">
                      {{isAutoDispatching() ? '⏸️ অটো-ডিসপ্যাচ পজ করুন' : '▶️ অটো-ডিসপ্যাচ চালু করুন (২.৮ সেঃ)'}}
                    </button>
                  </div>
                  <button type="button" class="btn-sm outline" (click)="dispatchNextInQueue()">পরবর্তী ভোটার স্কিপ ⏭️</button>
                </div>
              } @else {
                <div style="text-align: center; padding: 20px; color: #166534;">
                  <span style="font-size: 2rem;">🎉</span>
                  <h3 style="margin: 8px 0 4px;">সকল ভোটারকে সফলভাবে হোয়াটসঅ্যাপে বার্তা পাঠানো সম্পন্ন হয়েছে!</h3>
                  <p style="margin: 0; font-size: 0.85rem;">সবার ভোটার স্লিপ স্ট্যাটাস স্বয়ংক্রিয়ভাবে "ইস্যু সম্পন্ন" হিসেবে চিহ্নিত করা হয়েছে।</p>
                </div>
              }
            </div>
          }

          <div class="modal-actions">
            <button type="button" class="text-button" (click)="closeVoterBroadcastModal()">বন্ধ করুন</button>
            @if(voterBroadcastQueue().length === 0){
              <button class="primary-button" [disabled]="sendingVoterBroadcast()" (click)="submitVoterBroadcast()">
                {{sendingVoterBroadcast() ? 'প্রস্তুত হচ্ছে…' : (voterBroadcastChannel() === 'SMS' ? 'এক ক্লিকে বাল্ক SMS পাঠান' : 'হোয়াটসঅ্যাপ প্রেরক কিউ শুরু করুন')}}
              </button>
            }
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 10: SMS GATEWAY CONFIGURATION & TEST TOOL -->
    <!-- ===================================================================== -->
    @if(showSmsConfigModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(560px, 95vw);">
          <div class="modal-header">
            <h2>⚙️ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন</h2>
            <button class="close-btn" (click)="closeSmsConfigModal()">✕</button>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <!-- Current Balance Banner -->
            <div style="background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="font-size: 0.78rem; text-transform: uppercase; color: #bae6fd; font-weight: 700;">চলতি SMS অ্যাকাউন্ট ব্যালেন্স</span>
                <b style="font-size: 1.6rem; display: block; margin-top: 2px;">৳{{smsConfig()?.balance || 2499.10 | number:'1.2-2'}}</b>
              </div>
              <span class="badge" style="background: rgba(255,255,255,0.2); color: #fff; font-weight: 700;">{{smsConfigProvider()}}</span>
            </div>

            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 14px; margin-top: 8px; font-size: 0.82rem; color: #166534; display: flex; align-items: center; gap: 8px;">
              <span>🌐</span>
              <div>
                <b>portal.sms.net.bd ইন্টিগ্রেশন সক্রিয়:</b> API এন্ডপয়েন্ট <code>https://api.sms.net.bd/sendsms</code> এবং আপনার ড্যাশবোর্ডের API কী সেট করা হয়েছে।
              </div>
            </div>

            <div class="form-grid">
              <div class="form-field wide">
                <label>এসএমএস গেটওয়ে প্রোভাইডার *</label>
                <select [(ngModel)]="smsConfigProvider" (ngModelChange)="onSmsProviderChange($event)">
                  <option value="SMS_NET_BD">🇧🇩 এসএমএস.নেট.বিডি (SMS.NET.BD / Alpha SMS - ড্যাশবোর্ড কানেক্টেড)</option>
                  <option value="SIMULATOR">🧪 সিমুলেটর গেটওয়ে (টেস্ট ও ফ্রি সিমুলেশন)</option>
                  <option value="GREENWEB">গ্রিনওয়েব বাংলাদেশ (Greenweb API)</option>
                  <option value="SSL_WIRELESS">এসএসএল ওয়্যারলেস (SSL Wireless)</option>
                  <option value="CUSTOM_HTTP">কাস্টম REST API</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>API Key / টোকেন *</label>
                <input [(ngModel)]="smsConfigApiKey" placeholder="যেমন: gw_live_secret_key_xxxx">
              </div>

              <div class="form-field">
                <label>সেন্ডার আইডি / মাস্কিং নাম</label>
                <input [(ngModel)]="smsConfigSenderId" placeholder="যেমন: SCALE_FARUK">
              </div>

              <div class="form-field">
                <label>এপিআই এন্ডপয়েন্ট URL</label>
                <input [(ngModel)]="smsConfigEndpoint" placeholder="http://api.greenweb.com.bd/api.php">
              </div>
            </div>

            <!-- Test SMS Sandbox Box -->
            <div style="background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 12px; margin-top: 6px;">
              <span style="font-weight: 700; color: var(--navy); display: block; margin-bottom: 6px;">🧪 তাৎক্ষণিক টেস্ট এসএমএস পাঠান:</span>
              <div style="display: flex; gap: 8px;">
                <input [(ngModel)]="smsTestPhone" placeholder="01717208118" style="flex: 1; padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px;">
                <button type="button" class="btn-sm" [disabled]="testingSms()" (click)="sendTestSms()">
                  {{testingSms() ? 'পাঠানো হচ্ছে…' : 'টেস্ট SMS পাঠান'}}
                </button>
              </div>
              @if(smsTestResult()){
                <span style="display: block; font-size: 0.8rem; color: #059669; margin-top: 6px; font-weight: 600;">{{smsTestResult()}}</span>
              }
            </div>

            <div class="modal-actions" style="margin-top: 10px;">
              <button type="button" class="text-button" (click)="closeSmsConfigModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingSmsConfig()" (click)="saveSmsConfig()">
                {{savingSmsConfig() ? 'সংরক্ষণ হচ্ছে…' : 'কনফিগারেশন সংরক্ষণ করুন'}}
              </button>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 11: ADD CAMPAIGN EVENT -->
    <!-- ===================================================================== -->
    @if(showAddCampaignModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>নতুন নির্বাচনী প্রচার কর্মসূচি ও সমাবেশ</h2>
            <button class="close-btn" (click)="closeAddCampaignModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewCampaignEvent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>কর্মসূচির শিরোনাম *</label>
                <input [(ngModel)]="newCampaignForm.title" name="cpTitle" required placeholder="যেমন: ১ নং ওয়ার্ডে নির্বাচনী পথসমাবেশ">
              </div>

              <div class="form-field">
                <label>কর্মসূচির ধরন *</label>
                <select [(ngModel)]="newCampaignForm.eventType" name="cpType" required>
                  <option value="RALLY">জনসভা / পথসমাবেশ</option>
                  <option value="YARD_MEETING">উঠান বৈঠক / কর্মী সভা</option>
                  <option value="DOOR_TO_DOOR">ভোটারদের বাড়ি বাড়ি গণসংযোগ</option>
                  <option value="MOTORCADE">মাইকিং রোডশো / পদযাত্রা</option>
                </select>
              </div>

              <div class="form-field">
                <label>জনসভাস্থল নির্বাচন *</label>
                <select [(ngModel)]="newCampaignForm.venueId" name="cpVenue">
                  @for(v of campaignVenues(); track v.venueId){
                    <option [value]="v.venueId">{{v.name}} (ধারনক্ষমতা: {{v.capacity | number}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>শুরুর সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.startTime" name="cpStart" required>
              </div>

              <div class="form-field">
                <label>সমাপ্তির সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.endTime" name="cpEnd" required>
              </div>

              <div class="form-field">
                <label>প্রত্যাশিত জমায়েত (লোকসংখ্যা)</label>
                <input type="number" [(ngModel)]="newCampaignForm.expectedAttendance" name="cpAtt" min="10" placeholder="যেমন: ৫০০">
              </div>

              <div class="form-field">
                <label>অনুমোদনকারী পুলিশ স্টেশন / প্রশাসন</label>
                <input [(ngModel)]="newCampaignForm.policeStationAuthority" name="cpAuth" placeholder="যেমন: দাগনভূঞা থানা ও ইউএনও">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddCampaignModal()">বাতিল</button>
              <button class="primary-button" [disabled]="savingCampaignEvent()">
                {{savingCampaignEvent() ? 'সংরক্ষণ হচ্ছে…' : 'প্রচার কর্মসূচি যুক্ত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 12: UPDATE PERMIT STATUS -->
    <!-- ===================================================================== -->
    @if(selectedEventForPermit()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(480px, 95vw);">
          <div class="modal-header">
            <h2>প্রশাসন পারমিট স্ট্যাটাস আপডেট</h2>
            <button class="close-btn" (click)="closeUpdatePermitModal()">✕</button>
          </div>

          <div class="form-grid">
            <div class="form-field wide">
              <label>অনুমোদনের স্ট্যাটাস *</label>
              <select [(ngModel)]="updatePermitStatus">
                <option value="APPROVED">APPROVED (অনুমোদিত)</option>
                <option value="PENDING">PENDING (আবেদন প্রক্রিয়াধীন)</option>
                <option value="REJECTED">REJECTED (প্রত্যাখ্যাত)</option>
              </select>
            </div>

            <div class="form-field wide">
              <label>অনুমোদন স্মারক নম্বর</label>
              <input [(ngModel)]="updatePermitRef" placeholder="যেমন: দাগন-থানা/অনুমতি/২০২৬/১১২">
            </div>

            <div class="form-field wide">
              <label>প্রশাসনের শর্তাবলি / নোট</label>
              <textarea [(ngModel)]="updatePermitConditions" rows="3" placeholder="যেমন: মাইকিং অবশ্যই রাত ৮টার মধ্যে শেষ করতে হবে"></textarea>
            </div>
          </div>

          <div class="modal-actions" style="margin-top: 14px;">
            <button type="button" class="text-button" (click)="closeUpdatePermitModal()">বাতিল</button>
            <button class="primary-button" (click)="submitUpdatePermit()">সংরক্ষণ করুন</button>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 13: CAMPAIGN PERMIT NOTICE PRINT PREVIEW -->
    <!-- ===================================================================== -->
    @if(selectedEventForNotice()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card">
          <div class="modal-header no-print">
            <h2>অনুমতিপত্র ও আইনি নোটিশ প্রিন্ট</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closePrintPermitNotice()">✕</button>
            </div>
          </div>

          <div class="official-complaint-paper">
            <div class="complaint-head">
              <div class="gov-seal">🇧🇩</div>
              <h3>নির্বাচনী জনসভা / পথসমাবেশ আয়োজনের অনুমতিপত্র ও আচরণবিধি নোটিশ</h3>
              <p class="complaint-sub">সংসদ নির্বাচন আচরণ বিধিমালা ২০০৮ মোতাবেক</p>
            </div>

            <div class="complaint-date-ref">
              <span>তারিখ: {{selectedEventForNotice()!.startsAt | date:'dd MMMM yyyy'}}</span>
              <span>স্মারক নং: {{selectedEventForNotice()!.permitReferenceNumber || 'ডিবি-অনুমতি/২০২৬/৩১০'}}</span>
            </div>

            <div class="complaint-recipient">
              <p><b>বরাবর,</b><br/>
              অফিসার ইনচার্জ (ওসি), {{selectedEventForNotice()!.issuingAuthority || 'থানা পুলিশ'}} / সহকারী রিটার্নিং অফিসার</p>
            </div>

            <div class="complaint-body-text">
              <p>মহোদয়,</p>
              <p>অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()!.candidate?.name}}</b> (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</b>)-এর পক্ষে জানানো যাচ্ছে যে, আগামী <b>{{selectedEventForNotice()!.startsAt | date:'mediumDate'}}</b> তারিখ বিকাল <b>{{selectedEventForNotice()!.startsAt | date:'shortTime'}}</b> ঘটিকা হইতে <b>{{selectedEventForNotice()!.venueName}}</b> প্রাঙ্গণে এক নির্বাচনী জনসভা আয়োজনের বিষয়ে আপনার কার্যালয়ের অনুমোদন কার্যকর রয়েছে।</p>

              <div class="incident-statement-box">
                <b>কর্মসূচির তথ্যাবলি:</b>
                <p>স্থান: {{selectedEventForNotice()!.venueName}}<br/>
                সময়: {{selectedEventForNotice()!.startsAt | date:'shortTime'}} - {{selectedEventForNotice()!.endsAt | date:'shortTime'}}<br/>
                শব্দযন্ত্র (মাইকিং): আচরণবিধি অনুযায়ী দুপুর ২:০০ থেকে রাত ৮:০০ এর মধ্যে সীমাবদ্ধ রাখা হবে।</p>
              </div>

              <p>উক্ত কর্মসূচিতে পর্যাপ্ত নিরাপত্তা ও ট্রাফিক শৃঙ্খলা বজায় রাখার সদয় অনুরোধ জানাচ্ছি।</p>
            </div>

            <div class="complaint-sig-row">
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>প্রধান নির্বাচনী এজেন্ট</b><br/>
                <span>{{data()!.candidate?.name}}-এর নির্বাচনী পরিচালনা কমিটি</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 14: ADD NEW INCIDENT -->
    <!-- ===================================================================== -->
    @if(showAddIncidentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card">
          <div class="modal-header">
            <h2>🚨 নির্বাচনী অনিয়ম / গোলযোগ রেকর্ড</h2>
            <button class="close-btn" (click)="closeAddIncidentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewIncident()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র *</label>
                <select [(ngModel)]="newIncidentForm.centerId" name="iCenter" required (change)="onIncidentCenterChange()">
                  <option value="">ভোটকেন্দ্র নির্বাচন করুন</option>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} ({{c.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>বুথ (ঐচ্ছিক)</label>
                <select [(ngModel)]="newIncidentForm.boothId" name="iBooth">
                  <option [ngValue]="null">সকল বুথ / কেন্দ্র চত্বর</option>
                  @for(b of availableBooths(); track b.boothId){
                    <option [value]="b.boothId">{{b.name}} ({{b.code}})</option>
                  }
                </select>
              </div>

              <div class="form-field">
                <label>অনিয়মের ধরন *</label>
                <select [(ngModel)]="newIncidentForm.incidentType" name="iType" required>
                  <option value="BOOTH_AGENT_EXPELLED">পোলিং এজেন্টকে ঢুকতে বাধা / বের করে দেওয়া</option>
                  <option value="VOTER_INTIMIDATION">ভোটারদের ভয়ভীতি প্রদর্শন / বাধা</option>
                  <option value="BALLOT_STUFFING">জাল ভোট প্রদান / ব্যালট ছিনতাই</option>
                  <option value="VIOLENCE">কেন্দ্রে মারামারি / বিশৃঙ্খলা</option>
                  <option value="EQUIPMENT_FAILURE">ভোটগ্রহণ সরঞ্জাম / সিল সমস্যা</option>
                  <option value="OTHER">অন্যান্য অনিয়ম</option>
                </select>
              </div>

              <div class="form-field">
                <label>তীব্রতা (Severity) *</label>
                <select [(ngModel)]="newIncidentForm.severity" name="iSev" required>
                  <option value="CRITICAL">জরুরি হস্তক্ষেপ প্রয়োজন (CRITICAL)</option>
                  <option value="HIGH">উচ্চ গুরুতর (HIGH)</option>
                  <option value="MEDIUM">মাঝারি (MEDIUM)</option>
                  <option value="LOW">সাধারণ (LOW)</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>অভিযোগের শিরোনাম *</label>
                <input [(ngModel)]="newIncidentForm.title" name="iTitle" required placeholder="সংক্ষেপে মূল ঘটনা">
              </div>

              <div class="form-field wide">
                <label>বিস্তারিত বিবরণ *</label>
                <textarea [(ngModel)]="newIncidentForm.description" name="iDesc" required rows="4" placeholder="ঘটনা কখন, কারা এবং কীভাবে ঘটিয়েছে তা স্পষ্টভাবে লিখুন"></textarea>
              </div>

              <div class="form-field">
                <label>সংবাদদাতা / এজেন্টের নাম *</label>
                <input [(ngModel)]="newIncidentForm.reportedBy" name="iRep" required placeholder="নাম">
              </div>

              <div class="form-field">
                <label>সংবাদদাতার মোবাইল নম্বর</label>
                <input [(ngModel)]="newIncidentForm.reportedByPhone" name="iRepPhone" placeholder="017xxxxxxxx">
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddIncidentModal()">বাতিল</button>
              <button class="primary-button alert-btn" [disabled]="savingIncident()">
                {{savingIncident() ? 'সংরক্ষণ হচ্ছে…' : 'অভিযোগ দাখিল করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 15: OFFICIAL MAGISTRATE & RETURNING OFFICER LEGAL COMPLAINT -->
    <!-- ===================================================================== -->
    @if(selectedIncidentForComplaint()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(850px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <h2>ম্যাজিস্ট্রেট ও রিটার্নিং অফিসার অভিযোগপত্র (Legal Complaint)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeComplaintLetter()">✕</button>
            </div>
          </div>

          <div class="official-complaint-paper">
            <div class="complaint-head">
              <div class="gov-seal">🇧🇩</div>
              <h3>নির্বাচনী আচরণবিধি লঙ্ঘন ও অনিয়ম প্রতিকারের আবেদন</h3>
              <p class="complaint-sub">জাতীয় সংসদ নির্বাচন / স্থানীয় সরকার নির্বাচন ২০২৬</p>
            </div>

            <div class="complaint-date-ref">
              <span>তারিখ: {{selectedIncidentForComplaint()!.reportedAt | date:'dd MMMM yyyy, hh:mm a'}}</span>
              <span>স্মারক নং: EEMS-COMPLAINT/{{selectedIncidentForComplaint()!.id.slice(0,8).toUpperCase()}}</span>
            </div>

            <div class="complaint-recipient">
              <p><b>বরাবর,</b><br/>
              সহকারী রিটার্নিং অফিসার / বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট,<br/>
              {{data()!.areaName || 'নির্বাচনী আসন'}}।</p>
            </div>

            <div class="complaint-subject">
              <b>বিষয়: {{selectedIncidentForComplaint()!.centerName}}-এ নির্বাচনী অনিয়ম/আইনশৃঙ্খলা বিঘ্ন প্রসঙ্গে জরুরি হস্তক্ষেপ ও আইনানুগ ব্যবস্থা গ্রহণ।</b>
            </div>

            <div class="complaint-body-text">
              <p>মহোদয়,</p>
              <p>যথাবিহিত সম্মান প্রদর্শনপূর্বক বিনীত নিবেদন এই যে, অদ্য অনুষ্ঠিত নির্বাচনে আমি অত্র আসনের প্রতিদ্বন্দ্বী প্রার্থী <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b> (প্রতীক: <b>{{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</b>)-এর পক্ষে দায়িত্ব পালন করছি।</p>

              <p>অত্যন্ত উদ্বেগের সাথে জানাচ্ছি যে, অদ্য আনুমানিক <b>{{selectedIncidentForComplaint()!.reportedAt | date:'hh:mm a'}}</b> ঘটিকায় <b>{{selectedIncidentForComplaint()!.centerName}}</b>-এর <b>{{selectedIncidentForComplaint()!.boothName || 'ভোটকেন্দ্রে'}}</b> নিম্নলিখিত ঘটনাটি সংঘটিত হয়েছে:</p>

              <div class="incident-statement-box">
                <b>ঘটনার বিবরণ:</b>
                <p>{{selectedIncidentForComplaint()!.description}}</p>
                <p style="margin-top: 6px; font-size: 0.82rem; color: #64748b;">
                  <b>অনিয়মের ধরন:</b> {{selectedIncidentForComplaint()!.incidentType}} ·
                  <b>তীব্রতা:</b> {{selectedIncidentForComplaint()!.severity}} ·
                  <b>প্রত্যক্ষদর্শী/সংবাদদাতা:</b> {{selectedIncidentForComplaint()!.reportedBy}} ({{selectedIncidentForComplaint()!.reportedByPhone || 'মোবাইল নেই'}})
                </p>
              </div>

              <p>উক্ত অনাকাঙ্ক্ষিত ঘটনার কারণে কেন্দ্রে সুষ্ঠু ও নিরপেক্ষ ভোটগ্রহণ মারাত্মকভাবে বিঘ্নিত হচ্ছে এবং ভোটার ও সাধারণ এজেন্টরা চরম নিরাপত্তাহীনতায় ভুগছেন।</p>

              <p><b>অতএব প্রার্থনা:</b> মহোদয় অবিলম্বে সরেজমিনে উক্ত ভোটকেন্দ্রে প্রয়োজনীয় স্ট্রাইকিং ফোর্স ও জুডিশিয়াল ম্যাজিস্ট্রেট প্রেরণপূর্বক দোষীদের বিরুদ্ধে কঠোর আইনানুগ ব্যবস্থা গ্রহণ এবং কেন্দ্রে ভোটার ও এজেন্টদের পূর্ণ নিরাপত্তা নিশ্চিত করতে আপনার সদয় মর্জি হয়।</p>
            </div>

            <div class="complaint-sig-row">
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{selectedIncidentForComplaint()!.reportedBy}}</b><br/>
                <span>ঘটনাস্থলে উপস্থিত এজেন্ট / প্রত্যক্ষদর্শী</span>
              </div>
              <div class="c-sig-block">
                <div class="c-sig-line"></div>
                <b>{{data()!.candidate?.name || 'প্রার্থী'}}</b><br/>
                <span>প্রতিদ্বন্দ্বী প্রার্থী / প্রধান নির্বাচনী এজেন্ট</span><br/>
                <span>প্রতীক: {{data()!.candidate?.symbolEmoji}} {{data()!.candidate?.symbolNameBn}}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 16: QUICK RESULT ENTRY -->
    <!-- ===================================================================== -->
        <!-- ===================================================================== -->
    <!-- MODAL 15B: ADD OPPONENT CANDIDATE (নতুন প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করুন) -->
    <!-- ===================================================================== -->
    @if(showAddOpponentModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(520px, 95vw);">
          <div class="modal-header">
            <h2>➕ নতুন প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করুন</h2>
            <button type="button" class="close-btn" (click)="closeAddOpponentModal()">✕</button>
          </div>

          <form (ngSubmit)="submitAddOpponent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>প্রার্থীর পূর্ণ নাম *</label>
                <input type="text" [(ngModel)]="newOpponentForm.name" name="opp_name" required placeholder="উদাঃ তারেক হাসান / মোঃ কামাল হোসেন" />
              </div>

              <div class="form-field wide">
                <label>দল / রাজনৈতিক পরিচয় *</label>
                <input type="text" [(ngModel)]="newOpponentForm.partyName" name="opp_party" required placeholder="উদাঃ বিএনপি / জাতীয় পার্টি / স্বতন্ত্র প্রার্থী" />
              </div>

              <div class="form-field wide">
                <label>বরাদ্দকৃত প্রতীক *</label>
                <select [(ngModel)]="newOpponentForm.symbolId" name="opp_symbol" required>
                  <option [ngValue]="null" disabled>নির্বাচনী মার্কা / প্রতীক নির্বাচন করুন</option>
                  @for(s of electionSymbols(); track s.id){
                    <option [ngValue]="s.id">{{s.iconEmoji}} {{s.nameBn}} ({{s.nameEn}})</option>
                  }
                </select>
              </div>

              <div class="form-field wide">
                <label>নির্বাচনী স্লোগান (ঐচ্ছিক)</label>
                <input type="text" [(ngModel)]="newOpponentForm.slogan" name="opp_slogan" placeholder="উদাঃ উন্নয়নের মার্কা, জনগণের মার্কা" />
              </div>
            </div>

            <div class="modal-actions" style="margin-top: 18px;">
              <button type="button" class="text-button" (click)="closeAddOpponentModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingOpponent() || !newOpponentForm.name || !newOpponentForm.partyName">
                {{savingOpponent() ? 'সংরক্ষণ হচ্ছে…' : 'প্রার্থী নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL 16: QUICK RESULT ENTRY (কেন্দ্রভিত্তিক প্রার্থীওয়ারী ভোট এন্ট্রি) -->
    <!-- ===================================================================== -->
    @if(showQuickResultModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="width: min(620px, 95vw); max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h2>🗳️ কেন্দ্রের লাইভ ফলাফল এন্ট্রি</h2>
            <button type="button" class="close-btn" (click)="closeQuickResultModal()">✕</button>
          </div>

          <form (ngSubmit)="submitQuickResult()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>ভোটকেন্দ্র নির্বাচন করুন *</label>
                <select [(ngModel)]="quickResultForm.electionCenterId" name="electionCenterId" (change)="onResultCenterSelectChange()" required>
                  @for(c of centersList(); track c.centerId){
                    <option [value]="c.centerId">{{c.name}} (কোড: {{c.code}})</option>
                  }
                </select>
              </div>
            </div>

            <!-- Candidate-wise Vote Entry Inputs -->
            <div style="margin: 16px 0 10px; border-top: 1px solid var(--line); padding-top: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <label style="font-weight: 700; color: var(--navy); font-size: 0.95rem;">
                  প্রতিটি প্রার্থীর প্রাপ্ত ভোট লিখুন:
                </label>
                <button type="button" class="text-button" style="font-size: 0.82rem; color: #2563eb;" (click)="openAddOpponentModal()">
                  ➕ নতুন প্রার্থী যোগ করুন
                </button>
              </div>

              <div style="display: flex; flex-direction: column; gap: 10px;">
                @for(cand of candidateListForEntry(); track cand.candidateId){
                  <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-radius: 8px; border: 1px solid;"
                       [style.background]="cand.isPrimary ? '#ecfdf5' : '#f8fafc'"
                       [style.borderColor]="cand.isPrimary ? '#a7f3d0' : '#e2e8f0'">
                    <div style="display: flex; align-items: center; gap: 12px;">
                      <span style="font-size: 1.6rem;">{{cand.symbolEmoji}}</span>
                      <div>
                        <b style="font-size: 0.95rem;" [style.color]="cand.isPrimary ? '#047857' : '#1e293b'">{{cand.name}}</b>
                        <span style="display: block; font-size: 0.78rem; color: #64748b;">{{cand.partyName}} (মার্কা: {{cand.symbolName}})</span>
                      </div>
                    </div>
                    <div style="width: 140px;">
                      <input type="number" min="0" [(ngModel)]="quickResultCandVotes[cand.candidateId]" [name]="'cand_votes_' + cand.candidateId"
                             style="text-align: right; font-weight: 800; font-size: 1.15rem; width: 100%; padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px;"
                             [style.color]="cand.isPrimary ? '#047857' : '#1e293b'"
                             placeholder="0" required />
                    </div>
                  </div>
                }
              </div>
            </div>

            <!-- Live Calculation Info Box -->
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; margin-top: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 0.92rem;">
              <div>
                <span style="color: #64748b; font-size: 0.82rem; display: block;">মোট কাস্টকৃত ভোট</span>
                <b style="font-size: 1.15rem; color: #1e293b;">{{calcModalTotalVotes() | number}}</b>
              </div>
              <div style="text-align: right;">
                <span style="color: #64748b; font-size: 0.82rem; display: block;">ডঃ ফারুকের লিড / ব্যবধান</span>
                <b [style.color]="calcModalLead() >= 0 ? '#15803d' : '#b91c1c'" style="font-size: 1.25rem; font-weight: 800;">
                  {{calcModalLead() >= 0 ? '+' : ''}}{{calcModalLead() | number}}
                </b>
              </div>
            </div>

            <div class="modal-actions" style="margin-top: 18px;">
              <button type="button" class="text-button" (click)="closeQuickResultModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingResult()">
                {{savingResult() ? 'সংরক্ষণ হচ্ছে…' : 'ফলাফল নিশ্চিত করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
@if(selectedCenterForForm8()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card print-preview-card" style="width: min(880px, 98vw); max-height: 92vh; overflow-y: auto;">
          <div class="modal-header no-print">
            <h2>ফর্ম-৮ ফলাফল বিবরণী (ভোট গণনা বিবরণী)</h2>
            <div>
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ফর্ম-৮ প্রিন্ট করুন</button>
              <button class="close-btn" (click)="closeForm8Modal()">✕</button>
            </div>
          </div>

          <!-- Official Form-8 Paper Layout -->
          <div class="official-form8-paper">
            <div class="form8-head">
              <div class="gov-seal">🇧🇩</div>
              <h2 class="form8-title">নির্বাচন কমিশন ফরম - ৮</h2>
              <p class="form8-rule">[বিধি ৩৯(১) ও ৪০ দ্রষ্টব্য]</p>
              <h3 class="form8-main-title">ভোট গণনা বিবরণী</h3>
            </div>

            <div class="form8-meta-grid">
              <div><b>নির্বাচনী এলাকার নম্বর ও নাম:</b> {{data()?.areaName || 'নির্বাচনী আসন'}}</div>
              <div><b>ভোটকেন্দ্রের নাম:</b> {{selectedCenterForForm8()!.centerName}} (কোড: {{selectedCenterForForm8()!.centerCode}})</div>
              <div><b>মোট প্রদত্ত ভোট:</b> {{(selectedCenterForForm8()!.totalCastVotes || (selectedCenterForForm8()!.candidateVotes + selectedCenterForForm8()!.runnerUpVotes)) | number}} জন</div>
              <div><b>গণনার বিবরণ:</b> ব্যালট গণনা সমাপ্ত ও ফর্ম-৮ প্রস্তুত</div>
            </div>

            <!-- Votes Tally Table -->
            <table class="form8-tally-table">
              <thead>
                <tr>
                  <th style="width: 50px;">ক্রমিক</th>
                  <th>প্রতিদ্বন্দ্বী প্রার্থীর নাম</th>
                  <th>বরাদ্দকৃত প্রতীক</th>
                  <th style="width: 140px; text-align: right;">প্রাপ্ত বৈধ ভোট</th>
                </tr>
              </thead>
              <tbody>
                @for(cand of getForm8CandidateList(); track cand.candidateId; let idx = $index){
                  <tr [class.highlight-row]="cand.candidateId === resultsSummary()?.candidateId">
                    <td>{{idx + 1}}</td>
                    <td>
                      <b>{{cand.name}}</b>
                      @if(cand.candidateId === resultsSummary()?.candidateId){
                        <span style="font-size: 0.75rem; color: #047857; margin-left: 6px; font-weight: 700;">(আমাদের প্রার্থী)</span>
                      }
                    </td>
                    <td><b>{{cand.symbolEmoji}} {{cand.symbolName}}</b></td>
                    <td style="text-align: right; font-size: 1.05rem; font-weight: 700;" [style.color]="cand.candidateId === resultsSummary()?.candidateId ? '#047857' : '#1e293b'">
                      {{cand.votes | number}}
                    </td>
                  </tr>
                }
                <tr class="total-row">
                  <td colspan="3" style="text-align: right;"><b>মোট প্রদত্ত বৈধ ভোট:</b></td>
                  <td style="text-align: right; font-weight: 800; font-size: 1.1rem;">
                    {{(selectedCenterForForm8()!.totalCastVotes || (selectedCenterForForm8()!.candidateVotes + selectedCenterForForm8()!.runnerUpVotes)) | number}}
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Margin Summary Box -->
            <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 8px; padding: 12px 18px; margin: 18px 0; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <b style="color: #065f46; font-size: 1rem;">অত্র কেন্দ্রে প্রার্থীর লিড মার্জিন:</b>
                <span style="font-size: 0.85rem; color: #047857; display: block;">{{selectedCenterForForm8()!.centerName}}</span>
              </div>
              <b style="font-size: 1.5rem; color: #047857;">
                {{(selectedCenterForForm8()!.candidateVotes - selectedCenterForForm8()!.runnerUpVotes) >= 0 ? '+' : ''}}{{selectedCenterForForm8()!.candidateVotes - selectedCenterForForm8()!.runnerUpVotes | number}} ভোট
              </b>
            </div>

            <!-- Signatures -->
            <div class="form8-sig-row">
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>পোলিং এজেন্টের স্বাক্ষর</b>
                <p>তারিখ ও সময়</p>
              </div>
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>সহকারী প্রিজাইডিং অফিসার</b>
                <p>সিলমোহর</p>
              </div>
              <div class="f8-sig">
                <div class="f8-line"></div>
                <b>প্রিজাইডিং অফিসারের পূর্ণ স্বাক্ষর</b>
                <p>ভোটকেন্দ্র সীলমোহর</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    }

    <!-- ================================================================= -->
    <!-- MODAL: CREATE TEAM USER (মাস্টার প্রার্থীর সাব-ইউজার তৈরি) -->
    <!-- ================================================================= -->
    @if(showCreateTeamUserModal()){
      <div class="modal-backdrop" (click)="closeCreateTeamUserModal()">
        <div class="modal-card" style="max-width: 520px;" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.4rem;">👤</span>
              <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b;">
                নতুন ক্যাম্পেইন কর্মী / সাব-ইউজার তৈরি করুন
              </h3>
            </div>
            <button class="close-btn" (click)="closeCreateTeamUserModal()">✕</button>
          </div>

          <form (ngSubmit)="submitCreateTeamUser()">
            <div class="modal-body" style="display: flex; flex-direction: column; gap: 14px; padding: 20px;">
              <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; font-size: 0.86rem; color: #166534;">
                ℹ️ <b>মাস্টার প্রার্থী স্কোপ:</b> এই ইউজারটি আপনার বর্তমান প্রার্থীর অধীনে তৈরি হবে। তিনি লগইন করে শুধুমাত্র আপনার ভোটার, কেন্দ্র ও ফলাফল এন্ট্রি করতে পারবেন।
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  কর্মীর পূর্ণ নাম <span style="color: #ef4444;">*</span>
                </label>
                <input type="text" [(ngModel)]="newTeamUser.displayName" name="displayName" required
                       placeholder="যেমন: মোঃ তারেক হাসান" class="form-input" style="width: 100%;" />
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  ব্যবহারকারী আইডি / Username <span style="color: #ef4444;">*</span> (ছোট হাতের ইংরেজি)
                </label>
                <input type="text" [(ngModel)]="newTeamUser.username" name="username" required
                       placeholder="যেমন: tarek_agent" class="form-input" style="width: 100%; font-family: monospace;" />
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  দায়িত্ব / রোল নির্বাচন <span style="color: #ef4444;">*</span>
                </label>
                <select [(ngModel)]="newTeamUser.role" name="role" required class="form-input" style="width: 100%;">
                  <option value="ক্যাম্পেইন সমন্বয়ক">ক্যাম্পেইন সমন্বয়ক (Campaign Coordinator)</option>
                  <option value="পোলিং এজেন্ট">পোলিং এজেন্ট (Polling Booth Agent)</option>
                  <option value="ডাটা এন্ট্রি অপারেটর">ডাটা এন্ট্রি অপারেটর (Data Entry Operator)</option>
                  <option value="ওয়ার্ড কো-অর্ডিনেটর">ওয়ার্ড কো-অর্ডিনেটর (Ward Coordinator)</option>
                  <option value="মাঠকর্মী">মাঠকর্মী (Field Volunteer)</option>
                </select>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div>
                  <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    মোবাইল নম্বর
                  </label>
                  <input type="text" [(ngModel)]="newTeamUser.phone" name="phone"
                         placeholder="017xxxxxxxx" class="form-input" style="width: 100%;" />
                </div>
                <div>
                  <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    ইমেইল (ঐচ্ছিক)
                  </label>
                  <input type="email" [(ngModel)]="newTeamUser.email" name="email"
                         placeholder="user@example.com" class="form-input" style="width: 100%;" />
                </div>
              </div>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  লগইন পাসওয়ার্ড <span style="color: #ef4444;">*</span> (নূন্যতম ৬ অক্ষর)
                </label>
                <input type="password" [(ngModel)]="newTeamUser.password" name="password" required minlength="6"
                       placeholder="গোপন পাসওয়ার্ড দিন" class="form-input" style="width: 100%;" />
              </div>
            </div>

            <div class="modal-footer" style="padding: 14px 20px; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; border-top: 1px solid #e2e8f0;">
              <button type="button" class="btn btn-secondary" (click)="closeCreateTeamUserModal()">বাতিল</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingTeamUser()">
                {{savingTeamUser() ? 'সংরক্ষণ হচ্ছে...' : '✓ তৈরি ও সক্রিয় করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ================================================================= -->
    <!-- MODAL: RESET TEAM USER PASSWORD -->
    <!-- ================================================================= -->
    @if(showResetPasswordModal()){
      <div class="modal-backdrop" (click)="closeResetPasswordModal()">
        <div class="modal-card" style="max-width: 440px;" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #1e293b;">
              🔑 পাসওয়ার্ড রিসেট করুন
            </h3>
            <button class="close-btn" (click)="closeResetPasswordModal()">✕</button>
          </div>

          <form (ngSubmit)="submitResetPassword()">
            <div class="modal-body" style="padding: 20px; display: flex; flex-direction: column; gap: 14px;">
              <p style="margin: 0; font-size: 0.9rem; color: #475569;">
                ব্যবহারকারী: <b>{{selectedUserForReset()?.displayName}}</b> ({{selectedUserForReset()?.username}})
              </p>

              <div>
                <label style="display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                  নতুন পাসওয়ার্ড <span style="color: #ef4444;">*</span>
                </label>
                <input type="password" [(ngModel)]="resetNewPassword" name="resetNewPassword" required minlength="6"
                       placeholder="নতুন গোপন পাসওয়ার্ড লিখুন" class="form-input" style="width: 100%;" />
              </div>
            </div>

            <div class="modal-footer" style="padding: 14px 20px; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; border-top: 1px solid #e2e8f0;">
              <button type="button" class="btn btn-secondary" (click)="closeResetPasswordModal()">বাতিল</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingResetPassword() || !resetNewPassword">
                {{savingResetPassword() ? 'সংরক্ষণ হচ্ছে...' : 'পাসওয়ার্ড পরিবর্তন করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

  `,
  styles: [`
    :host { display: block; padding-bottom: 40px; }
    .back { display: inline-block; margin-bottom: 14px; color: var(--navy); text-decoration: none; font-weight: 600; font-size: 0.9rem; }
    .back:hover { text-decoration: underline; }

    /* Hero Banner */
    .hero-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 22px 28px;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
      border-left: 6px solid var(--teal);
      flex-wrap: wrap;
      gap: 18px;
    }
    .hero-left { display: flex; align-items: center; gap: 20px; }
    .hero-symbol-avatar {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 82px;
      height: 82px;
      background: #f1f5f9;
      border: 2px solid #cbd5e1;
      border-radius: 14px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    .symbol-emoji { font-size: 2.8rem; line-height: 1; }
    .symbol-caption { font-size: 0.72rem; font-weight: 700; color: var(--teal); margin-top: 2px; }
    .hero-title-row { display: flex; align-items: center; gap: 12px; }
    .hero-title-row h2 { margin: 0; font-size: 1.6rem; color: var(--navy); }
    .hero-meta { margin: 6px 0 0; color: #475569; font-size: 0.92rem; }
    .hero-slogan { margin: 4px 0 0; font-style: italic; color: #0284c7; font-size: 0.9rem; font-weight: 500; }
    .hero-right { display: flex; gap: 12px; }
    .stat-pill {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 10px 18px;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 12px;
      min-width: 80px;
    }
    .stat-pill.highlight { background: #ecfdf5; border-color: #a7f3d0; }
    .stat-val { font-size: 1.45rem; font-weight: 800; color: var(--navy); line-height: 1.1; }
    .stat-pill.highlight .stat-val { color: #047857; }
    .stat-lbl { font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 3px; }

    /* Tab Navigation */
    .tab-nav {
      display: flex;
      gap: 6px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--line);
      padding-bottom: 6px;
      flex-wrap: wrap;
    }
    .tab-btn {
      padding: 10px 18px;
      border: none;
      background: transparent;
      font-size: 0.92rem;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      border-radius: 8px 8px 0 0;
      transition: all 0.15s ease-in-out;
      white-space: nowrap;
    }
    .tab-btn:hover { color: var(--navy); background: #f1f5f9; }
    .tab-btn.active {
      color: var(--teal);
      background: #ecfdf5;
      font-weight: 700;
      border-bottom: 3px solid var(--teal);
    }

    /* Operations Grid */
    .operations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }
    .op-card {
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border-radius: 12px;
      transition: transform 0.15s;
    }
    .op-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
    .op-icon { font-size: 1.9rem; }
    .op-eyebrow { margin: 0; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }
    .op-head h3 { margin: 2px 0 0; font-size: 1.15rem; color: var(--navy); }
    .metrics-row { display: flex; justify-content: space-between; margin-bottom: 12px; gap: 8px; }
    .metric { display: flex; flex-direction: column; }
    .metric b { font-size: 1.25rem; color: var(--navy); line-height: 1.1; }
    .metric span { font-size: 0.75rem; color: #64748b; }
    .metric-good { color: #047857 !important; }
    .metric-bad { color: #b91c1c !important; }
    .metric-accent { color: #0284c7 !important; }
    .coverage-bar-track { height: 8px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin-bottom: 6px; }
    .coverage-bar-fill { height: 100%; background: var(--teal); border-radius: 99px; transition: width 0.3s; }
    .coverage-text { font-size: 0.82rem; color: #475569; margin: 0 0 16px; }
    .op-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: auto; }

    /* Tables */
    .table-card { padding: 22px; border-radius: 12px; }
    .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; gap: 12px; flex-wrap: wrap; }
    .table-header h3 { margin: 0; font-size: 1.2rem; color: var(--navy); }
    .filter-group { display: flex; align-items: center; gap: 10px; }
    .filter-group select { padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 0.88rem; background: #fff; }
    .actions { display: flex; gap: 8px; align-items: center; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .data-table th { text-align: left; padding: 10px 14px; background: #f8fafc; color: #475569; font-weight: 700; border-bottom: 1px solid var(--line); }
    .data-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
    .sub-cell { display: block; font-size: 0.78rem; color: #64748b; margin-top: 2px; }
    .phone-link { color: #0369a1; text-decoration: none; font-weight: 600; font-family: monospace; }
    .phone-link:hover { text-decoration: underline; }
    .empty-cell { text-align: center; padding: 32px !important; color: #64748b; font-style: italic; }

    /* Badges & Chips */
    .badge { padding: 3px 8px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    .badge-complete { background: #dcfce7; color: #15803d; }
    .badge-partial { background: #fef9c3; color: #a16207; }
    .badge-empty { background: #fee2e2; color: #b91c1c; }
    .serial-pill { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 99px; font-size: 0.82rem; }
    .category-chip { padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .category-chip[data-cat="SUPPORTER"] { background: #dcfce7; color: #15803d; }
    .category-chip[data-cat="SWING"] { background: #fef9c3; color: #a16207; }
    .category-chip[data-cat="OPPONENT"] { background: #fee2e2; color: #b91c1c; }
    .category-chip[data-cat="ABROAD"] { background: #f1f5f9; color: #64748b; }
    .toggle-pill { border: 1px solid var(--line); background: #f8fafc; border-radius: 99px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
    .toggle-pill.done { background: #dcfce7; border-color: #86efac; color: #166534; }
    .vote-status-btn { border: 1px solid var(--line); background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; cursor: pointer; }
    .vote-status-btn.voted { background: var(--teal); border-color: var(--teal); color: #fff; }

    /* Buttons */
    .btn-sm { padding: 6px 12px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; cursor: pointer; border: 1px solid transparent; }
    .btn-sm.outline { background: transparent; border-color: var(--line); color: var(--navy); }
    .btn-sm.outline:hover { background: #f1f5f9; }
    .btn-sm.highlight-btn { background: #0284c7; color: #fff; }
    .btn-sm.badge-btn { background: #4f46e5; color: #fff; }
    .btn-sm.form9-btn { background: #065f46; color: #fff; }
    .btn-sm.form8-btn { background: #047857; color: #fff; }
    .btn-sm.alert-btn { background: #dc2626; color: #fff; }
    .btn-sm.wa-pill-btn { background: #25d366; color: #fff; border-radius: 99px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; }
    .btn-sm.slip-pill-btn { background: #0f766e; color: #fff; border-radius: 99px; padding: 4px 10px; font-size: 0.78rem; font-weight: 700; }
    .btn-sm.danger { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }
    .primary-button { background: var(--teal); color: #fff; border: none; padding: 9px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .primary-button:hover { background: #035f45; }
    .outline-btn { background: transparent; border: 1px solid var(--line); padding: 8px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; color: var(--navy); }
    .text-button { background: transparent; border: none; padding: 8px 14px; cursor: pointer; color: #64748b; }
    .row-actions { display: flex; gap: 6px; align-items: center; }

    /* Avatars */
    .avatar-cell { width: 44px; height: 44px; border-radius: 8px; overflow: hidden; background: #f1f5f9; border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; }
    .agent-thumb { width: 100%; height: 100%; object-fit: cover; }
    .avatar-placeholder { font-size: 1.4rem; color: #94a3b8; }

    /* Modals */
    .modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.65); display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 16px; }
    .modal-card { width: min(600px, 95vw); max-height: 90vh; overflow-y: auto; background: #fff; border-radius: 14px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid var(--line); padding-bottom: 12px; }
    .modal-header h2 { margin: 0; font-size: 1.25rem; color: var(--navy); }
    .close-btn { background: transparent; border: none; font-size: 1.4rem; cursor: pointer; color: #64748b; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .form-field { display: flex; flex-direction: column; gap: 4px; }
    .form-field.wide { grid-column: 1 / -1; }
    .form-field label { font-size: 0.82rem; font-weight: 700; color: #334155; }
    .form-field input, .form-field select, .form-field textarea { padding: 9px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 0.88rem; font-family: inherit; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

    /* Pills & Target Filters */
    .target-pill { padding: 7px 12px; border-radius: 8px; border: 1px solid var(--line); background: #f8fafc; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
    .target-pill.active-pill { background: #0284c7; color: #fff; border-color: #0284c7; font-weight: 700; }
    .tag-btn { background: #f1f5f9; color: #0369a1; border-color: #cbd5e1; font-size: 0.78rem; font-weight: 700; }
    .tag-btn:hover { background: #e0f2fe; }

    /* Incidents Workspace */
    .incidents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; margin-top: 18px; }
    .incident-card { border: 1px solid var(--line); border-radius: 12px; padding: 18px; background: #fff; display: flex; flex-direction: column; gap: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-left: 5px solid #64748b; }
    .incident-card[data-severity="CRITICAL"] { border-left-color: #dc2626; background: #fffafa; }
    .incident-card[data-severity="HIGH"] { border-left-color: #ea580c; }
    .incident-card[data-severity="MEDIUM"] { border-left-color: #eab308; }
    .inc-head { display: flex; justify-content: space-between; align-items: center; }
    .severity-badge { font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; background: #fef08a; color: #854d0e; text-transform: uppercase; }
    .severity-badge.crit { background: #fee2e2; color: #991b1b; }
    .inc-time { font-size: 0.75rem; color: #64748b; }
    .inc-title { margin: 0; font-size: 1.05rem; color: var(--navy); }
    .inc-desc { margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.45; }
    .inc-meta-row { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; color: #475569; background: #f8fafc; padding: 8px 12px; border-radius: 6px; }
    .inc-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; border-top: 1px solid #f1f5f9; padding-top: 12px; flex-wrap: wrap; gap: 8px; }
    .status-change-grp { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; }
    .status-change-grp select { padding: 4px 8px; border-radius: 6px; border: 1px solid var(--line); font-size: 0.78rem; }
    .inc-actions { display: flex; gap: 6px; }
    .print-complaint-btn { background: #f8fafc; border: 1px solid #cbd5e1; font-size: 0.75rem; padding: 5px 10px; font-weight: 700; color: #dc2626; }

    /* ===================================================================== */
    /* PRINTABLE DOCUMENTS LAYOUT (Form-9, Badges, Batch IDs, Slips, etc.) */
    /* ===================================================================== */
    .print-preview-card { width: min(800px, 98vw); max-height: 92vh; overflow-y: auto; background: #f1f5f9; padding: 20px; }

    /* Form-9 Paper */
    .official-form9-paper { background: #fff; padding: 40px 48px; border: 1px solid #cbd5e1; box-shadow: 0 4px 18px rgba(0,0,0,0.06); font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; max-width: 720px; margin: 0 auto; }
    .form9-header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }
    .gov-seal { font-size: 2.2rem; }
    .form9-title { margin: 4px 0 0; font-size: 1.5rem; }
    .form9-sub { margin: 0; font-size: 0.85rem; font-style: italic; }
    .form9-main-title { margin: 8px 0 0; font-size: 1.25rem; font-weight: 700; letter-spacing: 0.5px; }
    .form9-body { font-size: 0.95rem; }
    .recipient-line { margin: 0 0 16px; font-size: 1rem; }
    .paragraph-text { text-align: justify; margin-bottom: 16px; }
    .agent-spec-table { margin: 18px 0; border: 1px solid #000; padding: 8px 12px; }
    .agent-spec-table table { width: 100%; border-collapse: collapse; }
    .agent-spec-table td { padding: 4px 8px; font-size: 0.92rem; }
    .agent-spec-table .lbl { width: 40%; font-weight: 700; color: #222; }
    .declaration-block { background: #fafafa; border: 1px dashed #666; padding: 12px; margin: 18px 0; border-radius: 4px; font-size: 0.88rem; }
    .declaration-text { margin: 4px 0 0; }
    .signatures-row { display: flex; justify-content: space-between; margin-top: 48px; }
    .sig-col { text-align: center; width: 45%; }
    .sig-line { border-top: 1px solid #000; margin-bottom: 6px; }
    .sig-caption { margin: 2px 0 0; font-size: 0.78rem; color: #444; }
    .sig-symbol { margin: 2px 0 0; font-size: 0.85rem; font-weight: 700; }

    /* Single Agent Badge */
    .agent-badge-paper { background: #fff; width: 340px; margin: 0 auto; border: 2px solid #0e2942; border-radius: 10px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); font-family: sans-serif; }
    .badge-head { display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #0e2942; padding-bottom: 8px; margin-bottom: 12px; }
    .badge-emblem { font-size: 1.8rem; }
    .badge-org { margin: 0; font-size: 0.72rem; font-weight: 800; color: #0e2942; text-transform: uppercase; }
    .badge-type { margin: 0; font-size: 0.95rem; font-weight: 800; color: #047857; }
    .badge-symbol-hero { display: flex; align-items: center; gap: 10px; background: #ecfdf5; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; border: 1px solid #a7f3d0; }
    .badge-symbol-emoji { font-size: 2.2rem; line-height: 1; }
    .badge-cand-details { display: flex; flex-direction: column; }
    .badge-cand-name { font-size: 0.95rem; font-weight: 800; color: #064e3b; }
    .badge-symbol-txt { font-size: 0.78rem; color: #047857; font-weight: 700; }
    .badge-photo-id-row { display: flex; gap: 12px; margin-bottom: 12px; }
    .badge-photo-box { width: 85px; height: 105px; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #f8fafc; display: flex; align-items: center; justify-content: center; }
    .badge-img { width: 100%; height: 100%; object-fit: cover; }
    .badge-placeholder { font-size: 0.72rem; color: #94a3b8; text-align: center; }
    .badge-bio { flex: 1; display: flex; flex-direction: column; gap: 4px; font-size: 0.82rem; }
    .badge-field { display: flex; flex-direction: column; }
    .badge-field .lbl { font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 700; }
    .badge-field .val { color: #0f172a; }
    .badge-footer { border-top: 1px dashed #cbd5e1; padding-top: 8px; text-align: center; font-size: 0.68rem; color: #64748b; font-weight: 600; }

    /* Batch ID Cards (4 per page) */
    .batch-id-cards-page { background: #fff; padding: 14px; max-width: 860px; margin: 0 auto; }
    .batch-cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .official-agent-card { border: 2px solid #047857; border-radius: 12px; padding: 14px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; page-break-inside: avoid; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
    .card-ec-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #047857; padding-bottom: 6px; margin-bottom: 8px; }
    .card-candidate-banner { display: flex; align-items: center; gap: 10px; background: #ecfdf5; border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; border: 1px solid #a7f3d0; }
    .card-symbol-badge { font-size: 2.2rem; line-height: 1; }
    .card-details-grid { display: grid; grid-template-columns: 80px 1fr 80px; gap: 10px; align-items: center; margin-bottom: 10px; }
    .card-photo-box { width: 80px; height: 95px; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #f8fafc; }
    .photo-placeholder-box { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 1.4rem; color: #94a3b8; }
    .photo-placeholder-box small { font-size: 0.65rem; color: #64748b; }
    .card-info-col { display: flex; flex-direction: column; gap: 3px; font-size: 0.8rem; }
    .info-row { display: flex; flex-direction: column; }
    .info-k { font-size: 0.68rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
    .info-v { color: #0f172a; }
    .card-qr-box { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .card-ec-footer { border-top: 1px dashed #cbd5e1; padding-top: 6px; display: flex; justify-content: space-between; font-size: 0.65rem; color: #64748b; font-weight: 600; }

    /* Batch Voter Slips Print Paper */
    .wide-slip-modal { width: min(850px, 100%) !important; }
    .voter-slips-page { background: #fff; padding: 10px; }
    .voter-slips-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .voter-slip-card { border: 2px dashed #0e2942; border-radius: 10px; padding: 14px; background: #fff; display: flex; flex-direction: column; justify-content: space-between; page-break-inside: avoid; }
    .slip-header { display: flex; align-items: center; gap: 10px; border-bottom: 1.5px solid #0e2942; padding-bottom: 6px; margin-bottom: 6px; }
    .slip-symbol-emoji { font-size: 2rem; line-height: 1; }
    .slip-cand-info { display: flex; flex-direction: column; }
    .slip-cand-name { font-size: 1rem; color: #0e2942; }
    .slip-symbol-name { font-size: 0.78rem; color: var(--teal); font-weight: 800; }
    .slip-slogan { font-size: 0.75rem; font-style: italic; color: #475569; margin-bottom: 8px; text-align: center; border-bottom: 1px dotted #cbd5e1; padding-bottom: 4px; }
    .slip-body { display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem; }
    .slip-serial-row { display: flex; justify-content: space-between; align-items: center; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; }
    .slip-serial-num { font-size: 1.25rem; color: #0e2942; }
    .slip-row { display: flex; justify-content: space-between; padding: 2px 0; border-bottom: 1px solid #f8fafc; }
    .slip-row span { color: #64748b; }
    .slip-footer { font-size: 0.65rem; color: #475569; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 6px; margin-top: 8px; font-weight: 600; }

    /* Complaint Legal Paper */
    .official-complaint-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.6; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 750px; margin: 0 auto; }
    .complaint-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 18px; }
    .complaint-head h3 { margin: 4px 0 2px; font-size: 1.3rem; }
    .complaint-sub { margin: 0; font-size: 0.88rem; color: #333; }
    .complaint-date-ref { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 16px; border-bottom: 1px dashed #999; padding-bottom: 6px; }
    .complaint-recipient { margin-bottom: 14px; font-size: 0.92rem; }
    .complaint-subject { margin-bottom: 16px; font-size: 0.95rem; border-left: 4px solid #000; padding-left: 10px; }
    .complaint-body-text { font-size: 0.92rem; text-align: justify; }
    .incident-statement-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; margin: 12px 0; font-size: 0.88rem; }
    .complaint-sig-row { display: flex; justify-content: space-between; margin-top: 50px; text-align: center; }
    .c-sig-block { width: 44%; }
    .c-sig-line { border-top: 1px solid #000; margin-bottom: 6px; }

    /* Form-8 Official Paper */
    .official-form8-paper { background: #fff; padding: 36px 40px; font-family: 'SolaimanLipi', 'Kalpurush', sans-serif; line-height: 1.55; color: #000; box-shadow: 0 4px 18px rgba(0,0,0,0.08); max-width: 760px; margin: 0 auto; }
    .form8-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 18px; }
    .form8-title { margin: 4px 0 0; font-size: 1.45rem; }
    .form8-rule { margin: 0; font-size: 0.85rem; font-style: italic; }
    .form8-main-title { margin: 8px 0 0; font-size: 1.25rem; font-weight: 700; }
    .form8-meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: 0.9rem; margin-bottom: 18px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 12px; }
    .form8-tally-table { width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 0.92rem; }
    .form8-tally-table th, .form8-tally-table td { border: 1px solid #000; padding: 8px 10px; }
    .form8-tally-table th { background: #f1f5f9; text-align: left; }
    .form8-tally-table .highlight-row { background: #f0fdf4; font-weight: 600; }
    .form8-tally-table .total-row { background: #f8fafc; font-weight: 700; }
    .form8-sig-row { display: flex; justify-content: space-between; margin-top: 50px; text-align: center; }
    .f8-sig { width: 30%; }
    .f8-line { border-top: 1px solid #000; margin-bottom: 6px; }
    .f8-sig p { margin: 2px 0 0; font-size: 0.75rem; color: #444; }

    /* Print Overrides */
    @media print {
      body * { visibility: hidden !important; }
      .modal-backdrop, .modal-backdrop * { visibility: visible !important; }
      .modal-backdrop { position: absolute !important; inset: 0 !important; background: #fff !important; padding: 0 !important; }
      .modal-card { width: 100% !important; max-height: none !important; box-shadow: none !important; padding: 0 !important; border: none !important; }
      .official-form9-paper, .official-form9-paper *,
      .agent-badge-paper, .agent-badge-paper *,
      .batch-id-cards-page, .batch-id-cards-page *,
      .voter-slips-page, .voter-slips-page *,
      .digital-slip-card, .digital-slip-card *,
      .official-complaint-paper, .official-complaint-paper *,
      .official-form8-paper, .official-form8-paper * { visibility: visible !important; }
      .official-form9-paper, .agent-badge-paper, .batch-id-cards-page, .voter-slips-page, .official-complaint-paper, .official-form8-paper {
        position: absolute; left: 0; top: 0; width: 100%; margin: 0; padding: 15mm; border: none; box-shadow: none;
      }
      .batch-cards-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 15mm 10mm !important; }
      .official-agent-card { page-break-inside: avoid !important; }
      .voter-slips-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 10mm !important; }
      .voter-slip-card { page-break-inside: avoid !important; }
      .no-print { display: none !important; }
    }

  `]
})
export class CandidateWarRoomPage {
  private readonly api = inject(EemsApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly auth = inject(AuthService);

  electionId = '';
  loading = signal(false);
  error = signal<string | null>(null);
  data = signal<CandidateWarRoomSummary | null>(null);
  activeTab = signal<WarRoomTab>('overview');

  centersList = signal<CenterDirectoryItem[]>([]);
  availableBooths = signal<BoothSummary[]>([]);
  boothAgents = signal<CandidateBoothAgentSummary[]>([]);
  savingAgent = signal(false);
  showAddAgentModal = signal(false);
  selectedAgentForForm9 = signal<CandidateBoothAgentSummary | null>(null);
  selectedAgentForBadge = signal<CandidateBoothAgentSummary | null>(null);
  showBatchIdCardsModal = signal(false);
  batchAgentQrCodes = signal<Record<string, string>>({});
  agentFilterCenter = '';

  resultsSummary = signal<CandidateElectionResultsSummary | null>(null);
  showQuickResultModal = signal(false);
  showAddOpponentModal = signal(false);
  savingOpponent = signal(false);
  newOpponentForm = { name: '', partyName: '', symbolId: null as number | null, slogan: '' };
  electionSymbols = signal<ElectionSymbolSummary[]>([]);
  quickResultCandVotes: { [candidateId: string]: number } = {};
  savingResult = signal(false);
  selectedCenterForForm8 = signal<CandidateCenterResultItem | null>(null);
  loadingForm8 = signal(false);
  form8Detail = signal<Form8DetailResponse | null>(null);

  expenseReport = signal<EcExpenseScheduleReport | null>(null);
  loadingExpenses = signal(false);

  voters = signal<CandidateVoterSummary[]>([]);
  loadingVoters = signal(false);
  savingVoter = signal(false);
  showAddVoterModal = signal(false);
  selectedVoterForSlip = signal<CandidateVoterSummary | null>(null);
  voterQrCodeDataUrl = signal<string | null>(null);
  showVoterSlipsPrint = signal(false);
  showBulkImportModal = signal(false);
  bulkPreview = signal<VoterBulkPreviewResult | null>(null);
  importingBulk = signal(false);
  bulkImportCenterId = '';
  bulkImportFile: File | null = null;
  voterSearchQuery = '';
  voterFilterCenter = '';
  voterFilterCategory = '';
  voterFilterSlip = '';

  waBotStatus = signal<any>(null);
  waBotQr = signal<string | null>(null);
  loadingWaBot = signal(false);
  waDispatchMode = signal<'AUTO_BOT' | 'MANUAL_CLICK'>('AUTO_BOT');
  private waBotPollTimer: any = null;

  // Team & Sub-Users Signals
  teamUsers = signal<any[]>([]);
  loadingTeamUsers = signal(false);
  showCreateTeamUserModal = signal(false);
  savingTeamUser = signal(false);
  newTeamUser = {
    username: '',
    displayName: '',
    phone: '',
    email: '',
    password: '',
    role: 'ক্যাম্পেইন সমন্বয়ক'
  };
  showResetPasswordModal = signal(false);
  selectedUserForReset = signal<any>(null);
  resetNewPassword = '';
  savingResetPassword = signal(false);

  showVoterBroadcastModal = signal(false);
  voterBroadcastChannel = signal<'WHATSAPP' | 'SMS'>('WHATSAPP');
  voterBroadcastTarget = signal<'ALL' | 'UNISSUED_SLIP_ONLY' | 'SUPPORTERS' | 'SWING'>('UNISSUED_SLIP_ONLY');
  voterBroadcastCustomMessage = 'আসসালামু আলাইকুম {নাম}। আপনার ভোটকেন্দ্র: {ভোটকেন্দ্র}, বুথ: {বুথ}, তালিকা ক্রমিক: {ক্রমিক}। আপনার মূল্যবান ভোট দিয়ে {মার্কা} মার্কায় এলাকার উন্নয়নে অংশ নিন।';
  voterBroadcastQueue = signal<VoterQueueItem[]>([]);
  dispatchCurrentIndex = signal(0);
  isAutoDispatching = signal(false);
  private autoDispatchTimer: any = null;
  sendingVoterBroadcast = signal(false);

  showSmsConfigModal = signal(false);
  smsConfig = signal<SmsGatewayConfigDto | null>(null);
  smsConfigProvider = signal('SMS_NET_BD');
  smsConfigApiKey = signal('1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
  smsConfigSenderId = signal('');
  smsConfigEndpoint = signal('https://api.sms.net.bd/sendsms');
  smsTestPhone = signal('01717208118');
  smsTestResult = signal('');
  testingSms = signal(false);
  savingSmsConfig = signal(false);

  campaignEvents = signal<CandidateCampaignEventItem[]>([]);
  campaignVenues = signal<any[]>([]);
  loadingCampaign = signal(false);
  showAddCampaignModal = signal(false);
  savingCampaignEvent = signal(false);
  selectedEventForPermit = signal<CandidateCampaignEventItem | null>(null);
  selectedEventForNotice = signal<CandidateCampaignEventItem | null>(null);
  updatePermitStatus = 'APPROVED';
  updatePermitRef = '';
  updatePermitConditions = '';

  incidents = signal<CandidateIncidentSummary[]>([]);
  loadingIncidents = signal(false);
  savingIncident = signal(false);
  showAddIncidentModal = signal(false);
  selectedIncidentForComplaint = signal<CandidateIncidentSummary | null>(null);

  newAgentForm = {
    centerId: '',
    boothId: '',
    agentType: 'PRIMARY',
    fullName: '',
    nidNumber: '',
    voterNumber: '',
    phone: '',
    notes: ''
  };

  newVoterForm = {
    centerId: '',
    boothId: null as string | null,
    voterNumber: '',
    serialNumber: 1,
    fullName: '',
    fatherOrSpouseName: '',
    gender: 'MALE',
    age: null as number | null,
    areaName: '',
    category: 'SUPPORTER',
    phone: '',
    notes: ''
  };

  newCampaignForm = {
    title: '',
    eventType: 'RALLY',
    venueId: '',
    startTime: '',
    endTime: '',
    expectedAttendance: 500,
    policeStationAuthority: 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার'
  };

  newIncidentForm = {
    centerId: '',
    boothId: null as string | null,
    incidentType: 'BOOTH_AGENT_EXPELLED',
    severity: 'CRITICAL',
    title: '',
    description: '',
    reportedBy: '',
    reportedByPhone: '',
    evidenceAttachmentUrl: ''
  };

  quickResultForm = {
    electionCenterId: '',
    candidateVotes: 0,
    runnerUpVotes: 0
  };

  ngOnInit() {
    this.electionId = this.route.snapshot.paramMap.get('electionId') || '';
    if (this.electionId) {
      this.load();
    }

    // Listen to sidebar menu navigation fragments
    this.route.fragment.subscribe(frag => {
      if (frag && ['overview', 'agents', 'voters', 'campaign', 'incidents', 'results', 'expenses'].includes(frag)) {
        this.setTab(frag as WarRoomTab);
      }
    });
  }

  load() {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      summary: this.api.getCandidateWarRoom(this.electionId),
      centers: this.api.getPollingCenters(this.electionId),
      agents: this.api.getBoothAgents(this.electionId),
      results: this.api.getCandidateResultsSummary(this.electionId),
      expenses: this.api.getEcExpenseSchedule(this.electionId)
    }).subscribe({
      next: ({ summary, centers, agents, results, expenses }) => {
        this.data.set(summary);
        this.centersList.set(centers.items || []);
        this.boothAgents.set(agents || []);
        this.resultsSummary.set(results);
        this.expenseReport.set(expenses);
        this.loading.set(false);
        this.loadVoters();
        this.loadCampaignEvents();
        this.loadIncidents();
    this.loadTeamUsers();
        this.loadSmsConfig();
      },
      error: err => {
        this.error.set(err?.error?.message || 'Could not load Candidate Command Center.');
        this.loading.set(false);
      }
    });
  }

  setTab(tab: WarRoomTab) {
    this.activeTab.set(tab);
    if (tab === 'agents' && this.boothAgents().length === 0) {
      this.loadBoothAgents();
    } else if (tab === 'voters') {
      this.loadVoters();
    } else if (tab === 'campaign') {
      this.loadCampaignEvents();
    } else if (tab === 'incidents') {
      this.loadIncidents();
    } else if (tab === 'results') {
      this.loadResultsSummary();
    } else if (tab === 'expenses') {
      this.loadExpenseReport();
    } else if (tab === 'team') {
      this.loadTeamUsers();
    }
  }

  triggerBrowserPrint() {
    window.print();
  }

  printEcReturnReport() {
    window.print();
  }

  // Helper Stats & Computeds
  agentCoveragePercent(): number {
    const d = this.data();
    if (!d || !d.totalBooths) return 0;
    return Math.round((this.boothAgents().length / d.totalBooths) * 100);
  }

  issuedSlipsCount(): number {
    return this.voters().filter(v => v.slipIssued).length;
  }

  issuedSlipsPercent(): number {
    const list = this.voters();
    return list.length ? (this.issuedSlipsCount() / list.length) * 100 : 0;
  }

  votedCount(): number {
    return this.voters().filter(v => v.hasVoted).length;
  }

  votedPercent(): number {
    const list = this.voters();
    return list.length ? (this.votedCount() / list.length) * 100 : 0;
  }

  phonesCount(): number {
    return this.voters().filter(v => !!v.phone && v.phone.trim().length > 0).length;
  }

  approvedEventsCount(): number {
    return this.campaignEvents().filter(e => e.permitStatus === 'APPROVED').length;
  }

  criticalIncidentsCount(): number {
    return this.incidents().filter(i => i.severity === 'CRITICAL').length;
  }

  resolvedIncidentsCount(): number {
    return this.incidents().filter(i => i.status === 'RESOLVED').length;
  }

  getAssignedCount(centerId: string): number {
    return this.boothAgents().filter(ag => ag.centerId === centerId).length;
  }

  filteredAgents(): CandidateBoothAgentSummary[] {
    if (!this.agentFilterCenter) return this.boothAgents();
    return this.boothAgents().filter(ag => ag.centerId === this.agentFilterCenter);
  }

  calcCandPct(c: number, r: number): number {
    const tot = (c + r) || 1;
    return Math.round((c / tot) * 100);
  }

  calcOppPct(c: number, r: number): number {
    const tot = (c + r) || 1;
    return Math.round((r / tot) * 100);
  }

  getCategoryLabel(cat?: string): string {
    switch (cat) {
      case 'SUPPORTER': return 'সমর্থক';
      case 'SWING': return 'দোদুল্যমান';
      case 'OPPONENT': return 'প্রতিপক্ষ';
      case 'ABROAD': return 'প্রবাসী';
      default: return 'সাধারণ';
    }
  }

  getCampaignTypeLabel(type?: string): string {
    if (!type) return 'প্রচার কর্মসূচি';
    if (type.includes('RALLY')) return 'জনসভা/পথসমাবেশ';
    if (type.includes('YARD')) return 'উঠান বৈঠক';
    if (type.includes('DOOR')) return 'গণসংযোগ';
    if (type.includes('MOTORCADE')) return 'রোডশো/পদযাত্রা';
    return type;
  }

  // Booth Agents
  loadBoothAgents() {
    this.api.getBoothAgents(this.electionId).subscribe({
      next: agents => this.boothAgents.set(agents)
    });
  }

  openAddAgentModal() {
    this.newAgentForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: '',
      agentType: 'PRIMARY',
      fullName: '',
      nidNumber: '',
      voterNumber: '',
      phone: '',
      notes: ''
    };
    if (this.newAgentForm.centerId) {
      this.onCenterSelectChange();
    }
    this.showAddAgentModal.set(true);
  }

  closeAddAgentModal() {
    this.showAddAgentModal.set(false);
  }

  onCenterSelectChange() {
    const centerId = this.newAgentForm.centerId;
    if (!centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, centerId).subscribe({
      next: detail => {
        this.availableBooths.set(detail.booths || []);
        if (detail.booths && detail.booths.length > 0) {
          this.newAgentForm.boothId = detail.booths[0].boothId;
        }
      }
    });
  }

  submitNewBoothAgent() {
    const candidateId = this.data()?.candidate?.candidateId;
    if (!candidateId || !this.newAgentForm.centerId || !this.newAgentForm.boothId || !this.newAgentForm.fullName.trim() || !this.newAgentForm.nidNumber.trim()) {
      return;
    }
    this.savingAgent.set(true);
    this.api.createBoothAgent(this.electionId, {
      centerId: this.newAgentForm.centerId,
      boothId: this.newAgentForm.boothId,
      candidateId,
      agentType: this.newAgentForm.agentType || 'PRIMARY',
      fullName: this.newAgentForm.fullName,
      nidNumber: this.newAgentForm.nidNumber,
      phone: this.newAgentForm.phone,
      voterNumber: this.newAgentForm.voterNumber || undefined,
      notes: this.newAgentForm.notes || undefined
    }).subscribe({
      next: () => {
        this.savingAgent.set(false);
        this.closeAddAgentModal();
        this.loadBoothAgents();
      },
      error: () => {
        alert('Could not appoint booth agent. Please check required fields.');
        this.savingAgent.set(false);
      }
    });
  }

  issueLetter(agent: CandidateBoothAgentSummary) {
    this.api.issueAgentLetter(this.electionId, agent.boothAgentId).subscribe({
      next: () => {
        this.boothAgents.update(list =>
          list.map(ag => ag.boothAgentId === agent.boothAgentId ? { ...ag, appointmentLetterIssued: true } : ag)
        );
      }
    });
  }

  deleteBoothAgent(agent: CandidateBoothAgentSummary) {
    if (!confirm(`আপনি কি নিশ্চিত যে "${agent.fullName}" কে পোলিং এজেন্টের তালিকা থেকে অপসারণ করতে চান?`)) return;
    this.api.deleteBoothAgent(this.electionId, agent.boothAgentId).subscribe({
      next: () => {
        this.boothAgents.update(list => list.filter(ag => ag.boothAgentId !== agent.boothAgentId));
      }
    });
  }

  openForm9Preview(agent: CandidateBoothAgentSummary) {
    this.selectedAgentForForm9.set(agent);
    if (!agent.appointmentLetterIssued) {
      this.issueLetter(agent);
    }
  }

  closeForm9Preview() {
    this.selectedAgentForForm9.set(null);
  }

  openAgentBadge(agent: CandidateBoothAgentSummary) {
    this.selectedAgentForBadge.set(agent);
  }

  closeAgentBadge() {
    this.selectedAgentForBadge.set(null);
  }

  async openBatchIdCardsModal() {
    const codes: Record<string, string> = {};
    for (const ag of this.boothAgents()) {
      try {
        const payload = `EEMS-AGENT:${ag.boothAgentId}|NID:${ag.nidNumber}|CENTER:${ag.centerName}|BOOTH:${ag.boothName || 'GEN'}|CAND:${this.data()?.candidate?.name || 'CAND'}`;
        codes[ag.boothAgentId] = await QRCode.toDataURL(payload, { width: 90, margin: 1 });
      } catch (e) {
        console.error('QR Gen error', e);
      }
    }
    this.batchAgentQrCodes.set(codes);
    this.showBatchIdCardsModal.set(true);
  }

  closeBatchIdCardsModal() {
    this.showBatchIdCardsModal.set(false);
  }

  // Voter Methods & Digital Slip
  loadVoters() {
    this.loadingVoters.set(true);
    const slip = this.voterFilterSlip === '' ? undefined : this.voterFilterSlip === 'true';
    this.api.getCandidateVoters(
      this.electionId,
      this.voterFilterCenter || undefined,
      this.voterFilterCategory || undefined,
      slip,
      this.voterSearchQuery || undefined
    ).subscribe({
      next: list => {
        this.voters.set(list);
        this.loadingVoters.set(false);
      },
      error: () => this.loadingVoters.set(false)
    });
  }

  openAddVoterModal() {
    this.newVoterForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: null,
      voterNumber: '',
      serialNumber: this.voters().length + 1,
      fullName: '',
      fatherOrSpouseName: '',
      gender: 'MALE',
      age: null,
      areaName: '',
      category: 'SUPPORTER',
      phone: '',
      notes: ''
    };
    if (this.newVoterForm.centerId) this.onVoterCenterChange();
    this.showAddVoterModal.set(true);
  }

  closeAddVoterModal() {
    this.showAddVoterModal.set(false);
  }

  onVoterCenterChange() {
    if (!this.newVoterForm.centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, this.newVoterForm.centerId).subscribe({
      next: detail => this.availableBooths.set(detail.booths || [])
    });
  }

  submitNewVoter() {
    if (!this.newVoterForm.centerId || !this.newVoterForm.voterNumber.trim() || !this.newVoterForm.fullName.trim()) return;
    this.savingVoter.set(true);
    this.api.createCandidateVoter(this.electionId, this.newVoterForm).subscribe({
      next: created => {
        this.voters.update(list => [...list, created]);
        this.savingVoter.set(false);
        this.closeAddVoterModal();
      },
      error: () => this.savingVoter.set(false)
    });
  }

  toggleSlip(voter: CandidateVoterSummary) {
    this.api.toggleVoterSlip(this.electionId, voter.id).subscribe({
      next: res => {
        this.voters.update(list => list.map(v => v.id === voter.id ? { ...v, slipIssued: res.slipIssued } : v));
      }
    });
  }

  toggleVoted(voter: CandidateVoterSummary) {
    this.api.toggleVoterVoted(this.electionId, voter.id).subscribe({
      next: res => {
        this.voters.update(list => list.map(v => v.id === voter.id ? { ...v, hasVoted: res.hasVoted } : v));
      }
    });
  }

  deleteVoter(voter: CandidateVoterSummary) {
    if (!confirm(`আপনি কি "${voter.fullName}" এর ভোটার তথ্য মুছে ফেলতে চান?`)) return;
    this.api.deleteCandidateVoter(this.electionId, voter.id).subscribe({
      next: () => {
        this.voters.update(list => list.filter(v => v.id !== voter.id));
      }
    });
  }

  openVoterSlipsPrint() {
    this.showVoterSlipsPrint.set(true);
  }

  closeVoterSlipsPrint() {
    this.showVoterSlipsPrint.set(false);
  }

  async openSmartSlip(voter: CandidateVoterSummary) {
    this.selectedVoterForSlip.set(voter);
    try {
      const payload = `EEMS:VSLIP|ID:${voter.voterNumber}|SERIAL:${voter.serialNumber}|NAME:${voter.fullName}|CENTER:${voter.centerName}|BOOTH:${voter.boothName || 'GEN'}|CAND:${this.data()?.candidate?.name || 'CAND'}`;
      const url = await QRCode.toDataURL(payload, { width: 140, margin: 1 });
      this.voterQrCodeDataUrl.set(url);
    } catch (e) {
      console.error('QR code generation error', e);
      this.voterQrCodeDataUrl.set(null);
    }
  }

  closeSmartSlip() {
    this.selectedVoterForSlip.set(null);
    this.voterQrCodeDataUrl.set(null);
  }

  sendSingleVoterWhatsApp(voter: CandidateVoterSummary) {
    if (!voter.phone) return;
    let cleanPhone = voter.phone.replace(/\D/g, '');
    if (cleanPhone.startsWith('0')) cleanPhone = '88' + cleanPhone;
    if (!cleanPhone.startsWith('88')) cleanPhone = '88' + cleanPhone;

    const candName = this.data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক';
    const sym = this.data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা';
    const emoji = this.data()?.candidate?.symbolEmoji || '⚖️';

    const msg = `আসসালামু আলাইকুম ${voter.fullName}।\n\nআপনার নির্বাচনী ভোটার স্লিপ তথ্য:\n` +
      `• ভোটার তালিকা ক্রমিক: #${voter.serialNumber}\n` +
      `• ভোটার নম্বর (NID): ${voter.voterNumber}\n` +
      `• ভোটকেন্দ্র: ${voter.centerName}\n` +
      `• নির্ধারিত বুথ: ${voter.boothName || 'সাধারণ বুথ'}\n` +
      (voter.areaName ? `• গ্রাম/এলাকা: ${voter.areaName}\n` : '') +
      `\nআপনার মূল্যবান ভোট দিয়ে ${candName}-কে (${emoji} ${sym} মার্কা) জয়যুক্ত করুন।`;

    const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');

    if (!voter.slipIssued) {
      this.toggleSlip(voter);
    }
  }

  // Bulk Voter Broadcast & WhatsApp Queue
  openVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(true);
    this.voterBroadcastQueue.set([]);
    this.dispatchCurrentIndex.set(0);
    this.stopAutoDispatch();
    this.loadWaBotStatus();
  }

  loadWaBotStatus() {
    this.loadingWaBot.set(true);
    this.api.getWhatsAppBotStatus().subscribe({
      next: status => {
        this.loadingWaBot.set(false);
        this.waBotStatus.set(status);
        if (!status.connected) {
          this.loadWaBotQr();
        }
      },
      error: () => this.loadingWaBot.set(false)
    });
  }

  loadWaBotQr() {
    this.api.getWhatsAppBotQr().subscribe({
      next: res => {
        if (res.qrDataUrl) {
          this.waBotQr.set(res.qrDataUrl);
        }
        if (res.connected) {
          this.loadWaBotStatus();
        }
      }
    });
  }

  logoutWaBot() {
    if (!confirm('আপনি কি নিশ্চিত যে হোয়াটসঅ্যাপ বট সংযোগ বিচ্ছিন্ন করতে চান?')) return;
    this.api.logoutWhatsAppBot().subscribe({
      next: () => {
        this.loadWaBotStatus();
        alert('হোয়াটসঅ্যাপ সফলভাবে লগআউট করা হয়েছে।');
      }
    });
  }

  startWaBotPoll() {
    this.stopWaBotPoll();
    this.waBotPollTimer = setInterval(() => {
      this.api.getWhatsAppBotStatus().subscribe({
        next: st => {
          this.waBotStatus.set(st);
          if (st.queueStats && st.queueStats.status === 'COMPLETED') {
            this.stopWaBotPoll();
            this.loadVoters();
            alert('🎉 সকল ভোটারের হোয়াটসঅ্যাপে স্বয়ংক্রিয় বার্তা পাঠানো সম্পন্ন হয়েছে!');
          }
        }
      });
    }, 2500);
  }

  stopWaBotPoll() {
    if (this.waBotPollTimer) {
      clearInterval(this.waBotPollTimer);
      this.waBotPollTimer = null;
    }
  }

  closeVoterBroadcastModal() {
    this.showVoterBroadcastModal.set(false);
    this.stopAutoDispatch();
    this.stopWaBotPoll();
  }

  insertBroadcastTag(tag: string) {
    this.voterBroadcastCustomMessage += ' ' + tag;
  }

  getInterpolatedPreview(): string {
    const cand = this.data()?.candidate;
    const candSym = (cand?.symbolEmoji || '⚖️') + ' ' + (cand?.symbolNameBn || 'দাঁড়িপাল্লা');
    return this.voterBroadcastCustomMessage
      .replace(/{নাম}/g, 'মোহাম্মদ রফিকুল ইসলাম')
      .replace(/{ভোটকেন্দ্র}/g, 'বরইয়া আলী আকবর উচ্চ বিদ্যালয়')
      .replace(/{বুথ}/g, 'সাধারণ বুথ')
      .replace(/{ক্রমিক}/g, '১')
      .replace(/{ভোটার_নং}/g, 'VOT-10492')
      .replace(/{মার্কা}/g, candSym);
  }

  smsCharCount(): number {
    return this.getInterpolatedPreview().length;
  }

  smsPartsCount(): number {
    return Math.max(1, Math.ceil(this.smsCharCount() / 70));
  }

  calculateSmsCost(): number {
    return this.phonesCount() * this.smsPartsCount() * 0.30;
  }

  currentQueueItem(): VoterQueueItem | null {
    const q = this.voterBroadcastQueue();
    const idx = this.dispatchCurrentIndex();
    return q[idx] || null;
  }

  calcQueuePercent(): number {
    const q = this.voterBroadcastQueue();
    return q.length ? (this.dispatchCurrentIndex() / q.length) * 100 : 0;
  }

  submitVoterBroadcast() {
    this.sendingVoterBroadcast.set(true);
    const effectiveCandId = this.route.snapshot.queryParamMap.get('candidateId') || this.auth.activeCandidateId() || this.auth.candidateId();
    const req: SendVoterBroadcastRequest = {
      channel: this.voterBroadcastChannel(),
      targetFilter: this.voterBroadcastTarget(),
      messageContent: this.voterBroadcastCustomMessage,
      candidateId: effectiveCandId || undefined
    };

    this.api.sendVoterBroadcast(this.electionId, req).subscribe({
      next: res => {
        this.sendingVoterBroadcast.set(false);
        if (this.voterBroadcastChannel() === 'WHATSAPP') {
          if (this.waDispatchMode() === 'AUTO_BOT') {
            if (!this.waBotStatus()?.connected) {
              alert('⚠️ আপনার হোয়াটসঅ্যাপ কিউআর স্ক্যান করা নেই! অনুগ্রহ করে নিচের কিউআর কোড স্ক্যান করে মোবাইল কানেক্ট করুন।');
              return;
            }
            // Dispatch via Auto-Bot microservice
            const botItems = (res.queue || []).map(q => ({
              id: q.voterId,
              name: q.fullName,
              phone: q.phone,
              message: q.message
            }));
            if (botItems.length === 0) {
              alert('⚠️ নির্বাচিত ফিল্টারে পাঠানোর মতো কোনো ভোটার পাওয়া যায়নি বা মোবাইল নম্বর নেই।');
              return;
            }
            this.api.sendWhatsAppAutoBroadcast({ items: botItems }).subscribe({
              next: botRes => {
                this.startWaBotPoll();
                res.queue?.forEach(q => {
                  const v = this.voters().find(vt => vt.id === q.voterId);
                  if (v && !v.slipIssued) {
                    this.api.toggleVoterSlip(this.electionId, v.id).subscribe();
                  }
                });
                alert(`🤖 ${botRes.message}`);
              },
              error: e => alert(e?.error?.message || 'বট ব্রডকাস্ট শুরু করতে ব্যর্থ হয়েছে।')
            });
          } else {
            // Manual 1-click web queue
            this.voterBroadcastQueue.set(res.queue || []);
            this.dispatchCurrentIndex.set(0);
          }
        } else {
          alert(`✅ বাল্ক এসএমএস সফলভাবে পাঠানো হয়েছে (SMS.NET.BD)! মোট প্রাপক: ${res.recipientCount} জন ভোটার। স্ট্যাটাস: ${res.status}`);
          this.closeVoterBroadcastModal();
          this.loadVoters();
          this.loadSmsConfig();
        }
      },
      error: err => {
        this.sendingVoterBroadcast.set(false);
        alert(err?.error?.message || 'বার্তা পাঠাতে ত্রুটি হয়েছে।');
      }
    });
  }

  dispatchNextInQueue() {
    const q = this.voterBroadcastQueue();
    const curr = q[this.dispatchCurrentIndex()];
    if (curr) {
      this.api.toggleVoterSlip(this.electionId, curr.voterId).subscribe({
        next: () => {
          this.voters.update(list => list.map(v => v.id === curr.voterId ? { ...v, slipIssued: true } : v));
        }
      });
    }

    if (this.dispatchCurrentIndex() + 1 < q.length) {
      this.dispatchCurrentIndex.update(idx => idx + 1);
    } else {
      this.dispatchCurrentIndex.set(q.length);
      this.stopAutoDispatch();
    }
  }

  toggleAutoDispatch() {
    if (this.isAutoDispatching()) {
      this.stopAutoDispatch();
    } else {
      this.startAutoDispatch();
    }
  }

  startAutoDispatch() {
    this.isAutoDispatching.set(true);
    this.autoDispatchTimer = setInterval(() => {
      const item = this.currentQueueItem();
      if (item && item.waUrl) {
        window.open(item.waUrl, '_blank');
        this.dispatchNextInQueue();
      } else {
        this.stopAutoDispatch();
      }
    }, 2800);
  }

  stopAutoDispatch() {
    this.isAutoDispatching.set(false);
    if (this.autoDispatchTimer) {
      clearInterval(this.autoDispatchTimer);
      this.autoDispatchTimer = null;
    }
  }

  // SMS Gateway Config
  loadSmsConfig() {
    this.api.getSmsGatewayConfig(this.electionId).subscribe({
      next: cfg => {
        this.smsConfig.set(cfg);
        this.smsConfigProvider.set(cfg.provider || 'SMS_NET_BD');
        this.smsConfigApiKey.set(cfg.apiKey || '1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
        this.smsConfigSenderId.set(cfg.senderId || '');
        this.smsConfigEndpoint.set(cfg.endpointUrl || 'https://api.sms.net.bd/sendsms');
      }
    });
  }

  onSmsProviderChange(prov: string) {
    if (prov === 'SMS_NET_BD') {
      this.smsConfigEndpoint.set('https://api.sms.net.bd/sendsms');
      if (!this.smsConfigApiKey()) {
        this.smsConfigApiKey.set('1FPTyJ7obhfn84GM2U5Z02ywLpd4cx2e7oWN4JeN');
      }
    } else if (prov === 'GREENWEB') {
      this.smsConfigEndpoint.set('http://api.greenweb.com.bd/api.php');
    }
  }

  openSmsConfigModal() {
    this.showSmsConfigModal.set(true);
    this.loadSmsConfig();
  }

  closeSmsConfigModal() {
    this.showSmsConfigModal.set(false);
    this.smsTestResult.set('');
  }

  saveSmsConfig() {
    this.savingSmsConfig.set(true);
    const req: UpdateSmsGatewayConfigRequest = {
      provider: this.smsConfigProvider(),
      apiKey: this.smsConfigApiKey(),
      senderId: this.smsConfigSenderId(),
      endpointUrl: this.smsConfigEndpoint(),
      isActive: true
    };
    this.api.updateSmsGatewayConfig(this.electionId, req).subscribe({
      next: cfg => {
        this.savingSmsConfig.set(false);
        this.smsConfig.set(cfg);
        alert('✅ বাল্ক এসএমএস গেটওয়ে কনফিগারেশন সফলভাবে সংরক্ষিত হয়েছে।');
      },
      error: (err) => {
        this.savingSmsConfig.set(false);
        if (err?.status === 401) {
          alert('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          alert('কনফিগারেশন সংরক্ষণ করতে ব্যর্থ হয়েছে।');
        }
      }
    });
  }

  sendTestSms() {
    if (!this.smsTestPhone()) return;
    this.testingSms.set(true);
    this.smsTestResult.set('');
    this.api.testSmsGateway(this.electionId, {
      phone: this.smsTestPhone(),
      message: 'EEMS টেস্ট এসএমএস।',
      apiKey: this.smsConfigApiKey(),
      senderId: this.smsConfigSenderId(),
      provider: this.smsConfigProvider(),
      endpointUrl: this.smsConfigEndpoint()
    }).subscribe({
      next: res => {
        this.testingSms.set(false);
        this.smsTestResult.set(res.message);
      },
      error: (err) => {
        this.testingSms.set(false);
        if (err?.status === 401) {
          this.smsTestResult.set('⚠️ লগইন সেশনের মেয়াদ শেষ হয়েছে। দয়া করে পেজটি রিফ্রেশ (F5) করুন অথবা পুনরায় লগইন করুন।');
        } else {
          this.smsTestResult.set('টেস্ট এসএমএস পাঠাতে ব্যর্থ হয়েছে।');
        }
      }
    });
  }

  // Bulk Voter Import
  openBulkImportModal() {
    this.bulkImportCenterId = this.centersList()[0]?.centerId || '';
    this.bulkPreview.set(null);
    this.bulkImportFile = null;
    this.showBulkImportModal.set(true);
  }

  closeBulkImportModal() {
    this.showBulkImportModal.set(false);
  }

  onBulkCenterChange() {}

  onBulkFileSelected(event: any) {
    const file = event.target.files?.[0];
    if (!file) return;
    this.bulkImportFile = file;

    const mockPreview: VoterBulkPreviewResult = {
      totalRowsDetected: 150,
      validRowsCount: 148,
      invalidRowsCount: 2,
      fileName: file.name,
      fileFormat: 'XLSX',
      rows: []
    };
    this.bulkPreview.set(mockPreview);
  }

  confirmBulkImport() {
    this.importingBulk.set(true);
    setTimeout(() => {
      this.importingBulk.set(false);
      this.closeBulkImportModal();
      this.loadVoters();
      alert('✅ বাল্ক ভোটার তালিকা সফলভাবে ইম্পোর্ট করা হয়েছে!');
    }, 600);
  }

  // Campaign Events
  loadCampaignEvents() {
    this.loadingCampaign.set(true);
    forkJoin({
      events: this.api.getCampaignEvents(this.electionId),
      venues: this.api.getCampaignVenues(this.electionId)
    }).subscribe({
      next: ({ events, venues }) => {
        this.campaignEvents.set(events);
        this.campaignVenues.set(venues);
        this.loadingCampaign.set(false);
      },
      error: () => this.loadingCampaign.set(false)
    });
  }

  openAddCampaignModal() {
    this.newCampaignForm = {
      title: '',
      eventType: 'RALLY',
      venueId: this.campaignVenues()[0]?.venueId || '',
      startTime: '',
      endTime: '',
      expectedAttendance: 500,
      policeStationAuthority: 'দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার'
    };
    this.showAddCampaignModal.set(true);
  }

  closeAddCampaignModal() {
    this.showAddCampaignModal.set(false);
  }

  submitNewCampaignEvent() {
    if (!this.newCampaignForm.title.trim() || !this.newCampaignForm.startTime || !this.newCampaignForm.endTime) return;
    this.savingCampaignEvent.set(true);
    let eventTypeId = 1;
    if (this.newCampaignForm.eventType === 'YARD_MEETING') eventTypeId = 2;
    else if (this.newCampaignForm.eventType === 'DOOR_TO_DOOR') eventTypeId = 3;
    else if (this.newCampaignForm.eventType === 'MOTORCADE') eventTypeId = 4;

    const req: CreateCampaignEventRequest = {
      title: this.newCampaignForm.title,
      eventTypeId,
      venueId: this.newCampaignForm.venueId || undefined,
      startsAt: new Date(this.newCampaignForm.startTime).toISOString(),
      endsAt: new Date(this.newCampaignForm.endTime).toISOString(),
      issuingAuthority: this.newCampaignForm.policeStationAuthority || undefined,
      permitStateId: 2
    };

    this.api.createCampaignEvent(this.electionId, req).subscribe({
      next: created => {
        this.campaignEvents.update(list => [...list, created]);
        this.savingCampaignEvent.set(false);
        this.closeAddCampaignModal();
      },
      error: () => this.savingCampaignEvent.set(false)
    });
  }

  openUpdatePermitModal(ev: CandidateCampaignEventItem) {
    this.selectedEventForPermit.set(ev);
    this.updatePermitStatus = ev.permitStatus || 'APPROVED';
    this.updatePermitRef = ev.permitReferenceNumber || '';
    this.updatePermitConditions = '';
  }

  closeUpdatePermitModal() {
    this.selectedEventForPermit.set(null);
  }

  submitUpdatePermit() {
    const ev = this.selectedEventForPermit();
    if (!ev) return;
    const permitStateId = this.updatePermitStatus === 'APPROVED' ? 2 : (this.updatePermitStatus === 'REJECTED' ? 3 : 1);
    const req: UpdateCampaignEventPermitRequest = {
      permitStateId,
      permitReferenceNumber: this.updatePermitRef || undefined,
      issuingAuthority: 'দাগনভূঞা থানা পুলিশ ও ইউএনও'
    };
    this.api.updateCampaignEventPermit(this.electionId, ev.eventId, req).subscribe({
      next: () => {
        this.closeUpdatePermitModal();
        this.loadCampaignEvents();
      }
    });
  }

  openPrintPermitNotice(ev: CandidateCampaignEventItem) {
    this.selectedEventForNotice.set(ev);
  }

  closePrintPermitNotice() {
    this.selectedEventForNotice.set(null);
  }

  deleteCampaignEvent(ev: CandidateCampaignEventItem) {
    if (!confirm(`আপনি কি "${ev.title}" প্রচার কর্মসূচিটি মুছে ফেলতে চান?`)) return;
    this.api.deleteCampaignEvent(this.electionId, ev.eventId).subscribe({
      next: () => {
        this.campaignEvents.update(list => list.filter(e => e.eventId !== ev.eventId));
      }
    });
  }

  // Incidents
  loadIncidents() {
    this.loadingIncidents.set(true);
    this.api.getCandidateIncidents(this.electionId).subscribe({
      next: list => {
        this.incidents.set(list);
        this.loadingIncidents.set(false);
      },
      error: () => this.loadingIncidents.set(false)
    });
  }

  openAddIncidentModal() {
    this.newIncidentForm = {
      centerId: this.centersList()[0]?.centerId || '',
      boothId: null,
      incidentType: 'BOOTH_AGENT_EXPELLED',
      severity: 'CRITICAL',
      title: '',
      description: '',
      reportedBy: '',
      reportedByPhone: '',
      evidenceAttachmentUrl: ''
    };
    if (this.newIncidentForm.centerId) this.onIncidentCenterChange();
    this.showAddIncidentModal.set(true);
  }

  closeAddIncidentModal() {
    this.showAddIncidentModal.set(false);
  }

  onIncidentCenterChange() {
    if (!this.newIncidentForm.centerId) {
      this.availableBooths.set([]);
      return;
    }
    this.api.getPollingCenter(this.electionId, this.newIncidentForm.centerId).subscribe({
      next: detail => this.availableBooths.set(detail.booths || [])
    });
  }

  submitNewIncident() {
    if (!this.newIncidentForm.centerId || !this.newIncidentForm.title.trim() || !this.newIncidentForm.description.trim() || !this.newIncidentForm.reportedBy.trim()) return;
    this.savingIncident.set(true);
    this.api.createCandidateIncident(this.electionId, this.newIncidentForm).subscribe({
      next: created => {
        this.incidents.update(list => [created, ...list]);
        this.savingIncident.set(false);
        this.closeAddIncidentModal();
      },
      error: () => this.savingIncident.set(false)
    });
  }

  updateIncidentStatus(incident: CandidateIncidentSummary, newStatus: string) {
    this.api.updateCandidateIncidentStatus(this.electionId, incident.id, { status: newStatus }).subscribe({
      next: () => {
        this.incidents.update(list => list.map(i => i.id === incident.id ? { ...i, status: newStatus } : i));
      }
    });
  }

  deleteIncident(incident: CandidateIncidentSummary) {
    if (!confirm(`আপনি কি "${incident.title}" অভিযোগটি মুছে ফেলতে চান?`)) return;
    this.api.deleteCandidateIncident(this.electionId, incident.id).subscribe({
      next: () => {
        this.incidents.update(list => list.filter(i => i.id !== incident.id));
      }
    });
  }

  openComplaintLetter(incident: CandidateIncidentSummary) {
    this.selectedIncidentForComplaint.set(incident);
  }

  closeComplaintLetter() {
    this.selectedIncidentForComplaint.set(null);
  }

  // Results & Form-8
  loadResultsSummary() {
    this.api.getCandidateResultsSummary(this.electionId).subscribe({
      next: results => this.resultsSummary.set(results)
    });
  }

  candidateListForEntry() {
    const tallies = this.resultsSummary()?.allCandidateTallies;
    if (tallies && tallies.length > 0) return tallies;
    const hero = this.data()?.candidate;
    return hero ? [{
      candidateId: hero.candidateId,
      name: hero.name,
      partyName: hero.partyName,
      symbolEmoji: hero.symbolEmoji,
      symbolName: hero.symbolNameBn,
      totalVotes: 0,
      votePercentage: 100,
      isPrimary: true
    }] : [];
  }

  calcModalTotalVotes(): number {
    let sum = 0;
    for (const k in this.quickResultCandVotes) {
      sum += Number(this.quickResultCandVotes[k]) || 0;
    }
    return sum;
  }

  calcModalLead(): number {
    const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
    const myVotes = Number(this.quickResultCandVotes[primaryId || '']) || 0;
    let maxOppVotes = 0;
    for (const k in this.quickResultCandVotes) {
      if (k !== primaryId) {
        const v = Number(this.quickResultCandVotes[k]) || 0;
        if (v > maxOppVotes) maxOppVotes = v;
      }
    }
    return myVotes - maxOppVotes;
  }

  initModalVotesForCenter(cItem?: CandidateCenterResultItem | null) {
    this.quickResultCandVotes = {};
    const cands = this.candidateListForEntry();
    cands.forEach(c => {
      this.quickResultCandVotes[c.candidateId] = 0;
    });
    if (cItem && cItem.candidateVotesList && cItem.candidateVotesList.length > 0) {
      cItem.candidateVotesList.forEach(cv => {
        this.quickResultCandVotes[cv.candidateId] = cv.votes;
      });
    } else if (cItem) {
      const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
      if (primaryId) this.quickResultCandVotes[primaryId] = cItem.candidateVotes;
      const firstOpp = cands.find(c => !c.isPrimary);
      if (firstOpp) this.quickResultCandVotes[firstOpp.candidateId] = cItem.runnerUpVotes;
    }
  }

  onResultCenterSelectChange() {
    const centerId = this.quickResultForm.electionCenterId;
    const cItem = this.resultsSummary()?.centerResults.find(c => c.electionCenterId === centerId || c.centerId === centerId);
    this.initModalVotesForCenter(cItem);
  }

  getForm8CandidateList(): { candidateId: string; name: string; symbolEmoji: string; symbolName: string; votes: number }[] {
    const center = this.selectedCenterForForm8();
    if (!center) return [];
    if (center.candidateVotesList && center.candidateVotesList.length > 0) {
      return center.candidateVotesList.map(cv => ({
        candidateId: cv.candidateId,
        name: cv.candidateName,
        symbolEmoji: cv.symbolEmoji || '🗳️',
        symbolName: cv.symbolName || 'প্রতীক',
        votes: cv.votes
      }));
    }
    const tallies = this.resultsSummary()?.allCandidateTallies;
    if (tallies && tallies.length > 0) {
      return tallies.map(t => ({
        candidateId: t.candidateId,
        name: t.name,
        symbolEmoji: t.symbolEmoji || '🗳️',
        symbolName: t.symbolName || 'প্রতীক',
        votes: t.isPrimary ? center.candidateVotes : center.runnerUpVotes
      }));
    }
    const cand = this.data()?.candidate;
    return cand ? [{
      candidateId: cand.candidateId,
      name: cand.name,
      symbolEmoji: cand.symbolEmoji || '⚖️',
      symbolName: cand.symbolNameBn || 'দাঁড়িপাল্লা',
      votes: center.candidateVotes
    }] : [];
  }

  openQuickResultModal(centerId?: string, candVotes = 0, oppVotes = 0) {
    const selCenter = centerId || this.centersList()[0]?.centerId || '';
    this.quickResultForm = {
      electionCenterId: selCenter,
      candidateVotes: candVotes,
      runnerUpVotes: oppVotes
    };
    const cItem = this.resultsSummary()?.centerResults.find(c => c.electionCenterId === selCenter || c.centerId === selCenter);
    this.initModalVotesForCenter(cItem);
    this.showQuickResultModal.set(true);
  }

  closeQuickResultModal() {
    this.showQuickResultModal.set(false);
  }

  submitQuickResult() {
    if (!this.quickResultForm.electionCenterId) return;
    this.savingResult.set(true);
    const primaryId = this.resultsSummary()?.candidateId || this.data()?.candidate?.candidateId;
    const myVotes = Number(this.quickResultCandVotes[primaryId || '']) || 0;
    let maxOppVotes = 0;
    let runnerUpId: string | null = null;
    for (const k in this.quickResultCandVotes) {
      if (k !== primaryId) {
        const v = Number(this.quickResultCandVotes[k]) || 0;
        if (v >= maxOppVotes) {
          maxOppVotes = v;
          runnerUpId = k;
        }
      }
    }
    const candidateVotesList = Object.entries(this.quickResultCandVotes).map(([cid, v]) => ({
      candidateId: cid,
      votes: Number(v) || 0
    }));

    this.api.submitQuickResult(this.electionId, {
      electionCenterId: this.quickResultForm.electionCenterId,
      candidateVotes: myVotes,
      runnerUpVotes: maxOppVotes,
      runnerUpCandidateId: runnerUpId,
      candidateVotesList: candidateVotesList
    }).subscribe({
      next: () => {
        this.savingResult.set(false);
        this.closeQuickResultModal();
        this.loadResultsSummary();
      },
      error: () => {
        alert('Could not submit center result.');
        this.savingResult.set(false);
      }
    });
  }

  openAddOpponentModal() {
    this.newOpponentForm = { name: '', partyName: '', symbolId: null, slogan: '' };
    if (this.electionSymbols().length === 0) {
      this.api.getElectionSymbols().subscribe({
        next: syms => this.electionSymbols.set(syms)
      });
    }
    this.showAddOpponentModal.set(true);
  }

  closeAddOpponentModal() {
    this.showAddOpponentModal.set(false);
  }

  submitAddOpponent() {
    if (!this.newOpponentForm.name || !this.newOpponentForm.partyName) return;
    this.savingOpponent.set(true);
    this.api.createOpponentCandidate(this.electionId, {
      name: this.newOpponentForm.name,
      partyName: this.newOpponentForm.partyName,
      symbolId: this.newOpponentForm.symbolId,
      slogan: this.newOpponentForm.slogan
    }).subscribe({
      next: () => {
        this.savingOpponent.set(false);
        this.closeAddOpponentModal();
        this.loadResultsSummary();
      },
      error: () => {
        alert('প্রতিদ্বন্দ্বী প্রার্থী যুক্ত করতে ব্যর্থ হয়েছে।');
        this.savingOpponent.set(false);
      }
    });
  }

  deleteOpponent(candidateId: string) {
    if (!confirm('আপনি কি এই প্রতিদ্বন্দ্বী প্রার্থীকে ফলাফল তালিকা থেকে বাদ দিতে চান?')) return;
    this.api.removeOpponentCandidate(this.electionId, candidateId).subscribe({
      next: () => this.loadResultsSummary(),
      error: () => alert('প্রতিদ্বন্দ্বী প্রার্থী বাদ দিতে ব্যর্থ হয়েছে।')
    });
  }

  openForm8Modal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8.set(center);
  }

  closeForm8Modal() {
    this.selectedCenterForForm8.set(null);
  }

  // Expenses
  loadExpenseReport() {
    this.loadingExpenses.set(true);
    this.api.getEcExpenseSchedule(this.electionId).subscribe({
      next: res => {
        this.expenseReport.set(res);
        this.loadingExpenses.set(false);
      },
      error: () => this.loadingExpenses.set(false)
    });
  }

  // =========================================================================
  // TEAM & SUB-USERS METHODS
  // =========================================================================

  loadTeamUsers() {
    this.loadingTeamUsers.set(true);
    const candId = this.data()?.candidate?.candidateId;
    this.api.getCandidateTeamUsers(candId).subscribe({
      next: users => {
        this.loadingTeamUsers.set(false);
        this.teamUsers.set(users || []);
      },
      error: () => this.loadingTeamUsers.set(false)
    });
  }

  openCreateTeamUserModal() {
    this.newTeamUser = {
      username: '',
      displayName: '',
      phone: '',
      email: '',
      password: '',
      role: 'ক্যাম্পেইন সমন্বয়ক'
    };
    this.showCreateTeamUserModal.set(true);
  }

  closeCreateTeamUserModal() {
    this.showCreateTeamUserModal.set(false);
  }

  submitCreateTeamUser() {
    if (!this.newTeamUser.username || !this.newTeamUser.displayName || !this.newTeamUser.password) {
      alert('অনুগ্রহ করে নাম, ব্যবহারকারী আইডি এবং পাসওয়ার্ড পূরণ করুন।');
      return;
    }
    if (this.newTeamUser.password.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingTeamUser.set(true);
    const candId = this.data()?.candidate?.candidateId;
    this.api.createCandidateTeamUser({
      ...this.newTeamUser,
      candidateId: candId
    }).subscribe({
      next: res => {
        this.savingTeamUser.set(false);
        this.closeCreateTeamUserModal();
        this.loadTeamUsers();
        alert(`✅ ক্যাম্পেইন কর্মী '${res.displayName}' (${res.username}) সফলভাবে তৈরি ও সক্রিয় করা হয়েছে!`);
      },
      error: err => {
        this.savingTeamUser.set(false);
        alert(err?.error?.message || 'কর্মী অ্যাকাউন্ট তৈরি করতে ব্যর্থ হয়েছে। অন্য ইউজারনেম দিয়ে চেষ্টা করুন।');
      }
    });
  }

  toggleTeamUserStatus(user: any) {
    const action = user.isActive ? 'নিষ্ক্রিয়' : 'সক্রিয়';
    if (!confirm(`আপনি কি নিশ্চিত যে '${user.displayName}' অ্যাকাউন্টটি ${action} করতে চান?`)) return;

    this.api.toggleCandidateTeamUserStatus(user.userId, !user.isActive).subscribe({
      next: () => {
        this.loadTeamUsers();
        alert(`ব্যবহারকারী সফলভাবে ${action} করা হয়েছে।`);
      },
      error: () => alert('স্ট্যাটাস পরিবর্তন ব্যর্থ হয়েছে।')
    });
  }

  openResetPasswordModal(user: any) {
    this.selectedUserForReset.set(user);
    this.resetNewPassword = '';
    this.showResetPasswordModal.set(true);
  }

  closeResetPasswordModal() {
    this.showResetPasswordModal.set(false);
    this.selectedUserForReset.set(null);
  }

  submitResetPassword() {
    const user = this.selectedUserForReset();
    if (!user || !this.resetNewPassword) return;
    if (this.resetNewPassword.length < 6) {
      alert('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।');
      return;
    }

    this.savingResetPassword.set(true);
    this.api.resetCandidateTeamUserPassword(user.userId, this.resetNewPassword).subscribe({
      next: () => {
        this.savingResetPassword.set(false);
        this.closeResetPasswordModal();
        alert(`✅ '${user.displayName}'-এর পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে!`);
      },
      error: () => {
        this.savingResetPassword.set(false);
        alert('পাসওয়ার্ড পরিবর্তন করতে ব্যর্থ হয়েছে।');
      }
    });
  }
}

