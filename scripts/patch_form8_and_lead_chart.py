import os

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add signals and computed properties in class
old_signals = "  readonly showWinnerCertificateModal = signal(false);"
new_signals = """  readonly showWinnerCertificateModal = signal(false);
  readonly selectedCenterForForm8Statement = signal<CandidateCenterResultItem | null>(null);

  readonly totalVotesCastInAllCenters = computed(() => {
    const summary = this.resultsData();
    if (!summary?.allCandidateTallies || summary.allCandidateTallies.length === 0) {
      return (summary?.candidateTotalVotes || 0) + (summary?.runnerUpTotalVotes || 0);
    }
    return summary.allCandidateTallies.reduce((sum, c) => sum + (c.totalVotes || 0), 0);
  });

  readonly ourVoteShare = computed(() => {
    const total = this.totalVotesCastInAllCenters();
    if (!total) return 0;
    const ours = this.resultsData()?.candidateTotalVotes || 0;
    return Math.round((ours / total) * 1000) / 10;
  });

  readonly runnerUpVoteShare = computed(() => {
    const total = this.totalVotesCastInAllCenters();
    if (!total) return 0;
    const theirs = this.resultsData()?.runnerUpTotalVotes || 0;
    return Math.round((theirs / total) * 1000) / 10;
  });

  readonly othersVoteShare = computed(() => {
    const total = this.totalVotesCastInAllCenters();
    if (!total) return 0;
    const diff = 100 - (this.ourVoteShare() + this.runnerUpVoteShare());
    return Math.max(0, Math.round(diff * 10) / 10);
  });"""

if old_signals in content:
    content = content.replace(old_signals, new_signals, 1)
    print("Signals and computed properties added.")
else:
    print("ERROR: could not find old_signals")

# 2. Add methods: openForm8StatementModal, closeForm8StatementModal, calcTotalValidVotes, calcTotalCastVotes, numberToBanglaWords
old_methods_anchor = "  openWinnerCertificateModal() {\n    this.showWinnerCertificateModal.set(true);\n  }"
new_methods = """  openWinnerCertificateModal() {
    this.showWinnerCertificateModal.set(true);
  }

  openForm8StatementModal(center: CandidateCenterResultItem) {
    this.selectedCenterForForm8Statement.set(center);
  }

  closeForm8StatementModal() {
    this.selectedCenterForForm8Statement.set(null);
  }

  calcTotalValidVotes(cr?: CandidateCenterResultItem | null): number {
    if (!cr) return 0;
    if (cr.candidateVotesList && cr.candidateVotesList.length > 0) {
      return cr.candidateVotesList.reduce((acc, v) => acc + (v.votes || 0), 0);
    }
    return (cr.candidateVotes || 0) + (cr.runnerUpVotes || 0);
  }

  calcTotalCastVotes(cr?: CandidateCenterResultItem | null): number {
    if (!cr) return 0;
    return this.calcTotalValidVotes(cr) + (cr.cancelledVotes || 0);
  }

  numberToBanglaWords(num: number): string {
    if (!num || num === 0) return 'শূন্য';
    const ones = ['', 'এক', 'দুই', 'তিন', 'চার', 'পাঁচ', 'ছয়', 'সাত', 'আট', 'নয়', 'দশ',
      'এগারো', 'বারো', 'তেরো', 'চৌদ্দ', 'পনেরো', 'ষোল', 'সতেরো', 'আঠারো', 'উনিশ', 'বিশ',
      'একুশ', 'বাইশ', 'তেইশ', 'চব্বিশ', 'পঁচিশ', 'ছাব্বিশ', 'সাতাশ', 'আঠাশ', 'ঊনত্রিশ', 'ত্রিশ',
      'একত্রিশ', 'বত্রিশ', 'তেত্রিশ', 'চৌত্রিশ', 'পঁয়ত্রিশ', 'ছত্রিশ', 'সাঁইত্রিশ', 'আটত্রিশ', 'ঊনচল্লিশ', 'চল্লিশ',
      'একচল্লিশ', 'বিয়াল্লিশ', 'তেতাল্লিশ', 'চুয়াল্লিশ', 'পঁয়তাল্লিশ', 'ছেচল্লিশ', 'সাতচল্লিশ', 'আটচল্লিশ', 'ঊনপঞ্চাশ', 'পঞ্চাশ',
      'একান্ন', 'বায়ান্ন', 'তিপ্পান্ন', 'চুয়াল্লান্ন', 'পঞ্চান্ন', 'ছাপ্পান্ন', 'সাতান্ন', 'আটান্ন', 'ঊনষাট', 'ষাট',
      'একষট্টি', 'বাষট্টি', 'তেষট্টি', 'চৌষট্টি', 'পঁয়ষট্টি', 'ছেষট্টি', 'সাতষট্টি', 'আটষট্টি', 'ঊনসত্তর', 'সত্তর',
      'একাত্তর', 'বাহাত্তর', 'তিয়াত্তর', 'চুয়াত্তর', 'পঁচাত্তর', 'ছিয়াত্তর', 'সাতাত্তর', 'আটাত্তর', 'ঊনআশি', 'আশি',
      'একাশি', 'বিরাশি', 'তিরাশি', 'চুরাশি', 'পঁচাশি', 'ছিয়াশি', 'সাতাশি', 'অষ্টআশি', 'ঊননব্বই', 'নব্বই',
      'একানব্বই', 'বিরানব্বই', 'তিরানব্বই', 'চুরানব্বই', 'পঁচানব্বই', 'ছিয়ানব্বই', 'সাতানব্বই', 'আটানব্বই', 'নিরানব্বই'];

    const convertChunk = (n: number): string => {
      let str = '';
      const crore = Math.floor(n / 10000000);
      n %= 10000000;
      const lakh = Math.floor(n / 100000);
      n %= 100000;
      const thousand = Math.floor(n / 1000);
      n %= 1000;
      const hundred = Math.floor(n / 100);
      const rest = n % 100;

      if (crore > 0) str += convertChunk(crore) + ' কোটি ';
      if (lakh > 0) str += ones[lakh] + ' লাখ ';
      if (thousand > 0) str += ones[thousand] + ' হাজার ';
      if (hundred > 0) str += ones[hundred] + ' শত ';
      if (rest > 0) str += ones[rest] + ' ';
      return str.trim();
    };

    return convertChunk(num);
  }"""

if old_methods_anchor in content:
    content = content.replace(old_methods_anchor, new_methods, 1)
    print("Methods added.")
else:
    print("ERROR: could not find old_methods_anchor")

# 3. Insert Graphical Lead Margin Tracker in Results Tab (Right after Live Scoreboard)
old_scoreboard_end = """                  <div class="score-card opponent-score">
                    <div class="score-avatar">{{resultsData()!.runnerUpSymbolEmoji}}</div>
                    <div>
                      <span class="score-role">নিকটতম প্রতিদ্বন্দ্বী</span>
                      <h3 class="score-name">{{resultsData()!.runnerUpName}}</h3>
                      <p class="score-symbol">{{resultsData()!.runnerUpSymbol}}</p>
                      <b class="score-votes">{{resultsData()!.runnerUpTotalVotes | number}} ভোট</b>
                    </div>
                  </div>
                </div>
              </div>"""

graphical_lead_tracker = """                  <div class="score-card opponent-score">
                    <div class="score-avatar">{{resultsData()!.runnerUpSymbolEmoji}}</div>
                    <div>
                      <span class="score-role">নিকটতম প্রতিদ্বন্দ্বী</span>
                      <h3 class="score-name">{{resultsData()!.runnerUpName}}</h3>
                      <p class="score-symbol">{{resultsData()!.runnerUpSymbol}}</p>
                      <b class="score-votes">{{resultsData()!.runnerUpTotalVotes | number}} ভোট</b>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ========================================================= -->
              <!-- GRAPHICAL LEAD MARGIN & LIVE VOTE SHARE TRACKER -->
              <!-- ========================================================= -->
              <div class="card graphical-lead-tracker-card">
                <div class="tracker-header">
                  <div class="tracker-titles">
                    <span class="tracker-eyebrow">📈 লাইভ গ্রাফিক্যাল লিড ট্র্যাকার (REAL-TIME LEAD MARGIN & VOTE SHARE)</span>
                    <h3 class="tracker-title">ভোটের হার ও প্রতিদ্বন্দ্বিতার ব্যবধান অ্যানালিটিক্স</h3>
                  </div>
                  <div class="tracker-status-pill" [class.lead-positive]="resultsData()!.isLeading" [class.lead-negative]="!resultsData()!.isLeading && resultsData()!.countedCenters > 0">
                    <span class="status-pulse-dot"></span>
                    @if(resultsData()!.countedCenters === 0){
                      <span>গণনা শুরুর অপেক্ষায়</span>
                    } @else if(resultsData()!.isLeading){
                      <span>🟢 +{{resultsData()!.leadMargin | number}} ভোটে এগিয়ে (LEAD)</span>
                    } @else {
                      <span>🔴 {{resultsData()!.leadMargin | number}} ভোটে পিছিয়ে</span>
                    }
                  </div>
                </div>

                <!-- 1. Head-to-Head Split Bar Meter -->
                <div class="split-meter-wrap">
                  <div class="split-meter-labels">
                    <div class="meter-cand our-cand">
                      <span class="meter-dot our-dot"></span>
                      <b>{{resultsData()!.candidateName}} ({{resultsData()!.candidateSymbolEmoji}})</b>
                      <span class="meter-num">{{resultsData()!.candidateTotalVotes | number}} ভোট ({{ourVoteShare()}}%)</span>
                    </div>
                    <div class="meter-gap-tag">
                      @if(resultsData()!.countedCenters > 0){
                        <span>ব্যবধানে এগিয়ে: <b>+{{resultsData()!.leadMargin | number}} ভোট</b></span>
                      }
                    </div>
                    <div class="meter-cand opp-cand">
                      <span class="meter-dot opp-dot"></span>
                      <b>{{resultsData()!.runnerUpName}} ({{resultsData()!.runnerUpSymbolEmoji}})</b>
                      <span class="meter-num">{{resultsData()!.runnerUpTotalVotes | number}} ভোট ({{runnerUpVoteShare()}}%)</span>
                    </div>
                  </div>

                  <!-- Two-Way Proportional Graphical Bar -->
                  <div class="split-bar-track">
                    <div class="split-segment our-segment" [style.width.%]="ourVoteShare()">
                      @if(ourVoteShare() > 10){
                        <span class="seg-label">{{ourVoteShare()}}%</span>
                      }
                    </div>
                    @if(othersVoteShare() > 0){
                      <div class="split-segment others-segment" [style.width.%]="othersVoteShare()" title="অন্যান্য প্রার্থী: {{othersVoteShare()}}%">
                        @if(othersVoteShare() > 8){
                          <span class="seg-label">{{othersVoteShare()}}%</span>
                        }
                      </div>
                    }
                    <div class="split-segment opp-segment" [style.width.%]="runnerUpVoteShare()">
                      @if(runnerUpVoteShare() > 10){
                        <span class="seg-label">{{runnerUpVoteShare()}}%</span>
                      }
                    </div>
                  </div>
                </div>

                <!-- 2. Candidate Vote Share Graphical Progress Bars -->
                <div class="candidate-bars-section">
                  <h4 class="sub-section-title">📊 প্রার্থীভিত্তিক প্রাপ্ত ভোটের গ্রাফিক্যাল পরিসংখ্যান:</h4>
                  <div class="bars-list">
                    @for(t of resultsData()!.allCandidateTallies; track t.candidateId; let r = $index){
                      <div class="bar-row-item" [class.is-our-candidate]="t.isPrimary" [class.is-winner]="r === 0">
                        <div class="bar-info-head">
                          <div class="cand-badge-group">
                            <span class="rank-num">#{{r + 1}}</span>
                            <span class="symbol-circle">{{t.symbolEmoji}}</span>
                            <b class="cand-title">{{t.name}}</b>
                            <span class="party-tag">({{t.partyName}})</span>
                            @if(t.isPrimary){
                              <span class="our-badge">আমাদের প্রার্থী</span>
                            }
                          </div>
                          <div class="votes-num-group">
                            <b class="votes-bold">{{t.totalVotes | number}} ভোট</b>
                            <span class="pct-pill">{{t.votePercentage}}%</span>
                          </div>
                        </div>

                        <!-- Graphical Progress Bar with Gradient -->
                        <div class="progress-bar-container">
                          <div class="progress-bar-fill" 
                            [style.width.%]="t.votePercentage" 
                            [class.fill-primary]="t.isPrimary" 
                            [class.fill-runner]="!t.isPrimary && r === 1" 
                            [class.fill-other]="!t.isPrimary && r > 1">
                          </div>
                        </div>
                      </div>
                    }
                  </div>
                </div>

                <!-- 3. Center-by-Center Margin Trend Pills Strip -->
                <div class="centers-margin-strip">
                  <h4 class="sub-section-title">🏫 কেন্দ্রভিত্তিক ফলাফল ট্রেন্ড (Center-by-Center Trend):</h4>
                  <div class="centers-trend-grid">
                    @for(cr of resultsData()!.centerResults; track cr.electionCenterId){
                      <div class="center-trend-card" [class.trend-counted]="cr.isCounted" [class.trend-win]="cr.margin > 0" [class.trend-loss]="cr.margin < 0">
                        <div class="ct-top">
                          <span class="ct-code">{{cr.centerCode}}</span>
                          <span class="ct-status">{{cr.isCounted ? (cr.margin > 0 ? '🟢 এগিয়ে' : (cr.margin < 0 ? '🔴 পিছিয়ে' : 'সমান')) : '⏳ বাকি'}}</span>
                        </div>
                        <div class="ct-name" [title]="cr.centerName">{{cr.centerName}}</div>
                        <div class="ct-votes">
                          @if(cr.isCounted){
                            <span class="ct-diff">{{cr.margin > 0 ? '+' + (cr.margin | number) : (cr.margin | number)}} ভোট</span>
                          } @else {
                            <span class="ct-pending">গণনা বাকি</span>
                          }
                        </div>
                      </div>
                    }
                  </div>
                </div>
              </div>"""

if old_scoreboard_end in content:
    content = content.replace(old_scoreboard_end, graphical_lead_tracker, 1)
    print("Graphical Lead Tracker added.")
else:
    print("ERROR: could not find old_scoreboard_end")

# 4. Update Center Results Table row actions: Add '🖨️ ফরম-৮ বিবরণী' button
old_row_actions = """                            <div class="row-actions-group">
                              <button class="btn-sm btn-action" (click)="openQuickResultModal(cr.electionCenterId)">
                                {{cr.isCounted ? '✏️ সংশোধন' : '➕ ভোট এন্ট্রি'}}
                              </button>
                              <button class="btn-sm btn-form8" (click)="openForm8Modal(cr)" [class.has-doc]="cr.form8DocumentUrl">
                                📄 ফরম-৮ শিট
                              </button>
                            </div>"""

new_row_actions = """                            <div class="row-actions-group">
                              <button class="btn-sm btn-action" (click)="openQuickResultModal(cr.electionCenterId)">
                                {{cr.isCounted ? '✏️ সংশোধন' : '➕ ভোট এন্ট্রি'}}
                              </button>
                              <button class="btn-sm btn-print-form8" (click)="openForm8StatementModal(cr)" [disabled]="!cr.isCounted" title="নির্বাচন কমিশন ফরম-৮ ভোট গণনা বিবরণী প্রিন্ট করুন">
                                🖨️ ফরম-৮ বিবরণী
                              </button>
                              <button class="btn-sm btn-form8" (click)="openForm8Modal(cr)" [class.has-doc]="cr.form8DocumentUrl" title="প্রিজাইডিং অফিসারের স্বাক্ষরিত ফরম-৮ অনুলিপি আপলোড / দেখুন">
                                📄 কার্বন কপি
                              </button>
                            </div>"""

if old_row_actions in content:
    content = content.replace(old_row_actions, new_row_actions, 1)
    print("Table row actions updated with Form-8 Statement button.")
else:
    print("ERROR: could not find old_row_actions")

# 5. Add Form-8 Statement Modal template
old_modal_anchor = "    <!-- ===================================================================== -->\n    <!-- PRINTABLE VIEW: WINNER CONSOLIDATION CERTIFICATE -->"
form8_statement_modal = """    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: ELECTION COMMISSION FORM-8 STATEMENT SHEET -->
    <!-- ===================================================================== -->
    @if(selectedCenterForForm8Statement()){
      <div class="modal-backdrop print-modal-backdrop">
        <div class="card modal-card print-preview-card form8-modal-card">
          <div class="modal-header no-print">
            <div>
              <h2>বাংলাদেশ নির্বাচন কমিশন: ফরম - ৮</h2>
              <p class="subtitle">[বিধি ৩৬(১) দ্রষ্টব্য] — ভোট গণনার বিবরণী (Statement of the Count)</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button" (click)="triggerBrowserPrint()">🖨️ ফরম-৮ প্রিন্ট করুন (A4)</button>
              <button class="close-btn" (click)="closeForm8StatementModal()">✕</button>
            </div>
          </div>

          <!-- Official Form-8 Government Statement Paper -->
          <div class="official-form8-sheet">
            <!-- Government Form Header -->
            <div class="f8-gov-head">
              <div class="f8-ec-title">বাংলাদেশ নির্বাচন কমিশন</div>
              <h2 class="f8-form-num">ফরম - ৮</h2>
              <div class="f8-rule-ref">[বিধি ৩৬(১) দ্রষ্টব্য]</div>
              <h3 class="f8-form-name">ভোট গণনার বিবরণী</h3>
            </div>

            <!-- Election & Center Metadata Grid -->
            <div class="f8-meta-table">
              <div class="f8-meta-row">
                <span class="f8-m-lbl">১. নির্বাচনী এলাকার নম্বর ও নাম:</span>
                <b class="f8-m-val">{{data()?.areaName || '৫ নং ইয়াকুবপুর ইউনিয়ন · দাগনভূঞা'}}</b>
              </div>
              <div class="f8-meta-row">
                <span class="f8-m-lbl">২. ভোটকেন্দ্রের ক্রমিক নম্বর ও নাম:</span>
                <b class="f8-m-val">{{selectedCenterForForm8Statement()!.centerCode}} — {{selectedCenterForForm8Statement()!.centerName}}</b>
              </div>
              <div class="f8-meta-row">
                <span class="f8-m-lbl">৩. গণনা সমাপ্তির তারিখ ও সময়:</span>
                <b class="f8-m-val">{{selectedCenterForForm8Statement()!.reportedAtUtc ? (selectedCenterForForm8Statement()!.reportedAtUtc | date:'dd/MM/yyyy, hh:mm a') : 'ভোটগ্রহণের দিন বিকেল ৫:০০'}}</b>
              </div>
            </div>

            <!-- Ballot Accounting Section -->
            <div class="f8-ballot-accounting">
              <div class="f8-sec-title">ব্যালট পেপারের সংবিধিবদ্ধ হিসাব:</div>
              <table class="f8-sub-table">
                <tbody>
                  <tr>
                    <td class="f8-item-lbl">(ক) ব্যালট বাক্সে প্রাপ্ত মোট ব্যালট পেপারের সংখ্যা:</td>
                    <td class="f8-item-val"><b>{{calcTotalCastVotes(selectedCenterForForm8Statement()) | number}}</b> টি</td>
                  </tr>
                  <tr>
                    <td class="f8-item-lbl">(খ) বাতিল বলিয়া গণ্য ব্যালট পেপারের সংখ্যা:</td>
                    <td class="f8-item-val"><b>{{selectedCenterForForm8Statement()!.cancelledVotes || 0 | number}}</b> টি</td>
                  </tr>
                  <tr>
                    <td class="f8-item-lbl">(গ) মোট প্রদত্ত বৈধ ব্যালট পেপারের সংখ্যা [ (ক) - (খ) ]:</td>
                    <td class="f8-item-val highlight-valid"><b>{{calcTotalValidVotes(selectedCenterForForm8Statement()) | number}}</b> টি</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Candidate Votes Table -->
            <div class="f8-candidates-section">
              <div class="f8-sec-title">প্রতিদ্বন্দ্বী প্রার্থীদের প্রাপ্ত বৈধ ভোটের সংখ্যা:</div>
              <table class="f8-votes-table">
                <thead>
                  <tr>
                    <th style="width: 50px;">ক্রমিক</th>
                    <th>প্রতিদ্বন্দ্বী প্রার্থীর নাম</th>
                    <th style="width: 130px;">বরাদ্দকৃত প্রতীক</th>
                    <th>দলীয় পরিচয়</th>
                    <th style="width: 140px;">প্রাপ্ত বৈধ ভোট (অংকে)</th>
                    <th>প্রাপ্ত বৈধ ভোট (কথায়)</th>
                  </tr>
                </thead>
                <tbody>
                  @if(selectedCenterForForm8Statement()!.candidateVotesList && selectedCenterForForm8Statement()!.candidateVotesList!.length > 0){
                    @for(cv of selectedCenterForForm8Statement()!.candidateVotesList; track cv.candidateId; let i = $index){
                      <tr [class.highlight-our-row]="cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId())">
                        <td class="text-center">{{i + 1}}</td>
                        <td>
                          <b>{{cv.candidateName}}</b>
                          @if(cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId())){
                            <span class="f8-our-tag">★ বিজয়ী</span>
                          }
                        </td>
                        <td>
                          <span class="f8-sym-icon">{{cv.symbolEmoji}}</span> {{cv.symbolName || ''}}
                        </td>
                        <td>{{cv.candidateId === (data()?.candidate?.candidateId || auth.candidateId()) ? (data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী') : 'প্রতিদ্বন্দ্বী দল / স্বতন্ত্র'}}</td>
                        <td class="text-right"><b>{{cv.votes | number}}</b></td>
                        <td class="text-left font-bangla">{{numberToBanglaWords(cv.votes)}}</td>
                      </tr>
                    }
                  } @else {
                    <tr class="highlight-our-row">
                      <td class="text-center">১</td>
                      <td><b>{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b></td>
                      <td>{{data()?.candidate?.symbolEmoji || '⚖️'}} {{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</td>
                      <td>{{data()?.candidate?.partyName || 'বাংলাদেশ জামায়াতে ইসলামী'}}</td>
                      <td class="text-right"><b>{{selectedCenterForForm8Statement()!.candidateVotes | number}}</b></td>
                      <td class="text-left font-bangla">{{numberToBanglaWords(selectedCenterForForm8Statement()!.candidateVotes)}}</td>
                    </tr>
                    <tr>
                      <td class="text-center">২</td>
                      <td><b>শীর্ষ প্রতিদ্বন্দ্বী প্রার্থী</b></td>
                      <td>প্রতিদ্বন্দ্বী প্রতীক</td>
                      <td>অন্যান্য দল / স্বতন্ত্র</td>
                      <td class="text-right"><b>{{selectedCenterForForm8Statement()!.runnerUpVotes | number}}</b></td>
                      <td class="text-left font-bangla">{{numberToBanglaWords(selectedCenterForForm8Statement()!.runnerUpVotes)}}</td>
                    </tr>
                  }
                </tbody>
                <tfoot>
                  <tr>
                    <th colspan="4" class="text-right">মোট বৈধ ভোটের সংখ্যা:</th>
                    <th class="text-right"><b>{{calcTotalValidVotes(selectedCenterForForm8Statement()) | number}}</b></th>
                    <th class="text-left font-bangla"><b>{{numberToBanglaWords(calcTotalValidVotes(selectedCenterForForm8Statement()))}}</b></th>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Presiding Officer Certification & Signatures -->
            <div class="f8-cert-box">
              <p class="f8-cert-declaration">
                "আমি এই মর্মে প্রত্যয়ন করিতেছি যে, উপরোক্ত বিবরণী আমার উপস্থিতিতে ও তত্ত্বাবধানে সতর্কতার সহিত ভোট গণনা করিয়া সঠিকভাবে প্রস্তুত করা হইল এবং উপস্থিত প্রতিদ্বন্দ্বী প্রার্থী বা তাহাদের নির্বাচনী এজেন্ট / পোলিং এজেন্টদের উপস্থিতিতে ফলাফল ঘোষণা পূর্বক তাহাদের স্বাক্ষরিত অনুলিপি প্রদান করা হইল।"
              </p>
            </div>

            <!-- Signatures Section -->
            <div class="f8-signatures-grid">
              <div class="f8-po-sign-box">
                <div class="f8-sign-line"></div>
                <b>প্রিজাইডিং অফিসারের স্বাক্ষর ও সিলমোহর</b>
                <span class="f8-po-meta">নাম: {{selectedCenterForForm8Statement()!.presidingOfficerName || 'মোঃ শফিকুল ইসলাম'}}</span>
                <span class="f8-po-meta">মোবাইল: {{selectedCenterForForm8Statement()!.presidingOfficerPhone || '01819234567'}}</span>
                <span class="f8-po-meta">কেন্দ্র: {{selectedCenterForForm8Statement()!.centerName}} ({{selectedCenterForForm8Statement()!.centerCode}})</span>
              </div>

              <div class="f8-agents-signs-box">
                <div class="f8-agents-title">উপস্থিত পোলিং এজেন্টদের স্বাক্ষর:</div>
                <div class="f8-agent-slots">
                  <div class="f8-agent-slot">১. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">২. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">৩. স্বাক্ষর: ................................... প্রতীক: .............</div>
                  <div class="f8-agent-slot">৪. স্বাক্ষর: ................................... প্রতীক: .............</div>
                </div>
              </div>
            </div>

            <!-- Statutory Footer Note -->
            <div class="f8-statutory-footer">
              <span>* নির্বাচন পরিচালনা বিধিমালা অনুযায়ী এই বিবরণীর অনুলিপি সহকারী রিটার্নিং অফিসারের কার্যালয়ে তাৎক্ষণিক প্রেরণ করিতে হইবে।</span>
            </div>
          </div>
        </div>
      </div>
    }\n\n""" + old_modal_anchor

if old_modal_anchor in content:
    content = content.replace(old_modal_anchor, form8_statement_modal, 1)
    print("Form-8 Statement Modal added.")
else:
    print("ERROR: could not find old_modal_anchor")

# 6. Add CSS Styles for Graphical Lead Tracker and Official Form-8 Sheet
old_css_anchor = "    /* Official Polling Agent ID Card & Batch Printing Styles */"
new_css = """    /* Graphical Lead Tracker Card */
    .graphical-lead-tracker-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.04); margin-bottom: 22px; }
    .tracker-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 14px; margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }
    .tracker-eyebrow { font-size: 0.72rem; font-weight: 800; color: #0891b2; letter-spacing: 0.04em; text-transform: uppercase; }
    .tracker-title { margin: 2px 0 0 0; color: #082136; font-size: 1.15rem; font-weight: 800; }
    .tracker-status-pill { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.82rem; background: #f1f5f9; color: #475569; }
    .tracker-status-pill.lead-positive { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .tracker-status-pill.lead-negative { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .status-pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; animation: pulse 1.8s infinite; }

    /* Split Meter */
    .split-meter-wrap { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 22px; }
    .split-meter-labels { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 0.85rem; flex-wrap: wrap; gap: 8px; }
    .meter-cand { display: flex; align-items: center; gap: 6px; }
    .meter-dot { width: 10px; height: 10px; border-radius: 50%; }
    .meter-dot.our-dot { background: #16a34a; }
    .meter-dot.opp-dot { background: #d97706; }
    .meter-num { color: #64748b; font-size: 0.8rem; margin-left: 4px; }
    .meter-gap-tag { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    
    .split-bar-track { display: flex; height: 28px; border-radius: 14px; overflow: hidden; background: #e2e8f0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.06); }
    .split-segment { display: flex; align-items: center; justify-content: center; color: #fff; font-size: 0.76rem; font-weight: 800; transition: width 0.4s ease; }
    .split-segment.our-segment { background: linear-gradient(90deg, #16a34a, #22c55e); }
    .split-segment.opp-segment { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .split-segment.others-segment { background: #94a3b8; }
    .seg-label { text-shadow: 0 1px 2px rgba(0,0,0,0.3); }

    /* Candidate Progress Bars */
    .candidate-bars-section { margin-bottom: 22px; }
    .sub-section-title { font-size: 0.88rem; font-weight: 700; color: #1e293b; margin: 0 0 12px 0; }
    .bars-list { display: flex; flex-direction: column; gap: 10px; }
    .bar-row-item { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; }
    .bar-row-item.is-our-candidate { background: #f0fdf4; border-color: #86efac; }
    .bar-info-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }
    .cand-badge-group { display: flex; align-items: center; gap: 8px; }
    .rank-num { font-size: 0.72rem; font-weight: 800; background: #082136; color: #fff; width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center; }
    .symbol-circle { font-size: 1.25rem; }
    .cand-title { color: #082136; font-size: 0.88rem; }
    .party-tag { color: #64748b; font-size: 0.76rem; }
    .our-badge { background: #166534; color: #fff; font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
    .votes-num-group { display: flex; align-items: center; gap: 8px; }
    .votes-bold { font-size: 0.92rem; color: #082136; }
    .pct-pill { background: #e2e8f0; color: #334155; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; }
    
    .progress-bar-container { height: 10px; border-radius: 5px; background: #e2e8f0; overflow: hidden; }
    .progress-bar-fill { height: 100%; border-radius: 5px; transition: width 0.4s ease; }
    .progress-bar-fill.fill-primary { background: linear-gradient(90deg, #16a34a, #22c55e); }
    .progress-bar-fill.fill-runner { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .progress-bar-fill.fill-other { background: #94a3b8; }

    /* Centers Margin Trend Grid */
    .centers-margin-strip { border-top: 1px solid #f1f5f9; padding-top: 16px; }
    .centers-trend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
    .center-trend-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 10px; display: flex; flex-direction: column; gap: 4px; }
    .center-trend-card.trend-win { border-left: 4px solid #16a34a; background: #f0fdf4; }
    .center-trend-card.trend-loss { border-left: 4px solid #dc2626; background: #fef2f2; }
    .ct-top { display: flex; justify-content: space-between; align-items: center; }
    .ct-code { font-size: 0.68rem; font-weight: 800; color: #475569; }
    .ct-status { font-size: 0.68rem; font-weight: 700; }
    .ct-name { font-size: 0.74rem; font-weight: 700; color: #082136; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ct-votes { font-size: 0.76rem; font-weight: 800; color: #0f172a; }
    .ct-diff { color: #166534; }
    .trend-loss .ct-diff { color: #b91c1c; }
    .ct-pending { color: #94a3b8; font-weight: 500; font-size: 0.7rem; }

    /* Button Print Form-8 */
    .btn-print-form8 { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 0.72rem; font-weight: 700; padding: 5px 8px; border-radius: 6px; cursor: pointer; }
    .btn-print-form8:hover:not([disabled]) { background: #dbeafe; }
    .btn-print-form8[disabled] { opacity: 0.5; cursor: not-allowed; }

    /* Official Form-8 Statement Sheet */
    .form8-modal-card { width: min(880px, 98vw); max-height: 94vh; overflow-y: auto; padding: 24px; background: #f1f5f9; }
    .official-form8-sheet { background: #ffffff; border: 2px solid #000; padding: 36px 42px; font-family: "Hind Siliguri", "Segoe UI", sans-serif; color: #000; box-shadow: 0 4px 16px rgba(0,0,0,0.1); margin: 0 auto; box-sizing: border-box; }
    .f8-gov-head { text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 16px; }
    .f8-ec-title { font-size: 1.15rem; font-weight: 800; letter-spacing: 0.03em; }
    .f8-form-num { font-size: 1.6rem; font-weight: 900; margin: 4px 0 2px 0; }
    .f8-rule-ref { font-size: 0.85rem; font-weight: 600; color: #333; }
    .f8-form-name { font-size: 1.3rem; font-weight: 800; text-decoration: underline; margin: 6px 0 0 0; }
    
    .f8-meta-table { display: flex; flex-direction: column; gap: 6px; margin-bottom: 18px; font-size: 0.9rem; }
    .f8-meta-row { display: flex; gap: 8px; align-items: baseline; }
    .f8-m-lbl { font-weight: 700; width: 230px; flex-shrink: 0; }
    .f8-m-val { flex: 1; border-bottom: 1px dotted #555; padding-bottom: 2px; }

    .f8-sec-title { font-size: 0.95rem; font-weight: 800; margin-bottom: 8px; border-left: 4px solid #000; padding-left: 8px; }
    .f8-ballot-accounting { margin-bottom: 20px; }
    .f8-sub-table { width: 100%; border-collapse: collapse; margin-top: 4px; font-size: 0.88rem; }
    .f8-sub-table td { padding: 6px 10px; border: 1px solid #444; }
    .f8-item-lbl { width: 68%; }
    .f8-item-val { text-align: right; width: 32%; }
    .highlight-valid { background: #f8fafc; font-size: 0.95rem; }

    .f8-candidates-section { margin-bottom: 20px; }
    .f8-votes-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .f8-votes-table th, .f8-votes-table td { border: 1.5px solid #000; padding: 7px 8px; }
    .f8-votes-table thead th { background: #f1f5f9; font-weight: 800; text-align: center; }
    .f8-votes-table tfoot th { background: #f8fafc; font-weight: 800; font-size: 0.92rem; }
    .f8-our-tag { background: #166534; color: #fff; font-size: 0.65rem; padding: 1px 5px; border-radius: 3px; margin-left: 6px; }
    .f8-sym-icon { font-size: 1.2rem; }
    .font-bangla { font-style: italic; color: #222; }

    .f8-cert-box { margin: 20px 0; border: 1px dashed #444; padding: 12px 16px; background: #fafafa; }
    .f8-cert-declaration { margin: 0; font-size: 0.82rem; line-height: 1.6; text-align: justify; font-style: italic; }

    .f8-signatures-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
    .f8-po-sign-box { display: flex; flex-direction: column; align-items: center; text-align: center; font-size: 0.82rem; }
    .f8-sign-line { width: 220px; border-top: 1.5px solid #000; margin-bottom: 6px; margin-top: 40px; }
    .f8-po-meta { font-size: 0.78rem; color: #333; }
    .f8-agents-signs-box { font-size: 0.8rem; }
    .f8-agents-title { font-weight: 800; margin-bottom: 8px; }
    .f8-agent-slots { display: flex; flex-direction: column; gap: 6px; color: #444; }

    .f8-statutory-footer { margin-top: 24px; border-top: 1px solid #999; padding-top: 8px; font-size: 0.72rem; color: #555; font-style: italic; }\n\n""" + old_css_anchor

if old_css_anchor in content:
    content = content.replace(old_css_anchor, new_css, 1)
    print("CSS rules added for Lead Tracker and Form-8.")
else:
    print("ERROR: could not find old_css_anchor")

# 7. Update @media print to include .official-form8-sheet
old_print_target = ".official-winner-cert-paper, .official-winner-cert-paper * {"
new_print_target = """.official-winner-cert-paper, .official-winner-cert-paper *,
      .official-form8-sheet, .official-form8-sheet * {"""

if old_print_target in content:
    content = content.replace(old_print_target, new_print_target, 1)
    content = content.replace(
        ".official-winner-cert-paper {",
        ".official-winner-cert-paper, .official-form8-sheet {",
        1
    )
    print("@media print updated with official-form8-sheet.")
else:
    print("ERROR: could not find old_print_target")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully!")

