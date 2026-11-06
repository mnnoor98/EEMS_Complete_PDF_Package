# -*- coding: utf-8 -*-

def get_template_tabs():
    return '''
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
'''
