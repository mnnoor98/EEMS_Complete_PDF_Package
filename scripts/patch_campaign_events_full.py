# -*- coding: utf-8 -*-
import sys

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
if 'CandidateCampaignEventItem' not in content:
    old_imports = """  CandidateBroadcastLogItem,
  SendCandidateBroadcastRequest,
  SendCandidateBroadcastResponse,"""
    new_imports = """  CandidateBroadcastLogItem,
  SendCandidateBroadcastRequest,
  SendCandidateBroadcastResponse,
  CandidateCampaignVenueItem,
  CandidateCampaignEventItem,
  CreateCampaignEventRequest,
  UpdateCampaignEventPermitRequest,"""
    if old_imports in content:
        content = content.replace(old_imports, new_imports, 1)
        print("Campaign models imported.")
    else:
        print("WARN: old_imports not found for Campaign models")

# 2. Update WarRoomTab type
if "'campaign'" not in content:
    content = content.replace(
        "type WarRoomTab = 'overview' | 'agents' | 'voters' | 'incidents' | 'results' | 'expenses';",
        "type WarRoomTab = 'overview' | 'agents' | 'voters' | 'incidents' | 'results' | 'expenses' | 'campaign';",
        1
    )
    print("WarRoomTab updated.")

# 3. Add Tab 7 button in Tab bar
old_tab_expenses = """          <button class="tab-btn" [class.active]="activeTab() === 'expenses'" (click)="setTab('expenses')">
            💰 ইসি ব্যয় রিটার্ন বিবরণী
          </button>"""
new_tab_expenses = """          <button class="tab-btn" [class.active]="activeTab() === 'expenses'" (click)="setTab('expenses')">
            💰 ইসি ব্যয় রিটার্ন বিবরণী
          </button>
          <button class="tab-btn" [class.active]="activeTab() === 'campaign'" (click)="setTab('campaign')">
            📅 সমাবেশ রুট ও পুলিশ পারমিট ({{campaignEvents().length}})
          </button>"""
if "📅 সমাবেশ রুট ও পুলিশ পারমিট" not in content and old_tab_expenses in content:
    content = content.replace(old_tab_expenses, new_tab_expenses, 1)
    print("Campaign Tab button added to header.")

# 4. Add Campaign Link in Overview Pillar 2
old_pillar2_action = """              <div class="op-action">
                <a class="op-link" [routerLink]="['/elections', electionId, 'workforce']">
                  মাঠকর্মী ও টিম ম্যানেজমেন্ট খুলুন →
                </a>
              </div>"""
new_pillar2_action = """              <div class="op-action" style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button class="btn-text-action" (click)="setTab('campaign')">
                  📅 নির্বাচনী সভা ও পুলিশ পারমিট ট্র্যাকার ({{campaignEvents().length}}) →
                </button>
                <a class="op-link" [routerLink]="['/elections', electionId, 'workforce']">
                  মাঠকর্মী ও টিম ম্যানেজমেন্ট খুলুন →
                </a>
              </div>"""
if old_pillar2_action in content:
    content = content.replace(old_pillar2_action, new_pillar2_action, 1)
    print("Overview pillar 2 updated.")

# 5. Insert Tab 7 HTML
tab7_html = """
        <!-- ================================================================= -->
        <!-- TAB 7: CAMPAIGN EVENTS, RALLIES & POLICE/EC PERMITS (বিকল্প ৩) -->
        <!-- ================================================================= -->
        @if(activeTab() === 'campaign'){
          <section class="card tab-panel campaign-events-panel">
            <!-- Header Strip -->
            <div class="panel-header-strip">
              <div>
                <h2>📅 নির্বাচনী সভা-সমাবেশ, মাইকিং রুট ও পুলিশ পারমিট ট্র্যাকার</h2>
                <p class="subtitle">
                  নির্বাচনী আচরণবিধি ২০০৮ অনুযায়ী দুপুর ২:০০ ঘটিকা হতে রাত ৮:০০ ঘটিকা পর্যন্ত মাইকিং এবং সভা-সমাবেশের জন্য ২৪ ঘণ্টা পূর্বে পুলিশ ও প্রশাসন হতে লিখিত অনুমতি গ্রহণ ও রুট ট্র্যাকিং।
                </p>
              </div>
              <div class="panel-header-actions">
                <button class="primary-button" (click)="openAddCampaignModal()">
                  + নতুন নির্বাচনী সমাবেশ / রোডশো যুক্ত করুন
                </button>
                <button class="outline-button" (click)="loadCampaignEvents()">
                  🔄 রিফ্রেশ
                </button>
              </div>
            </div>

            <!-- KPI Summary Cards -->
            <div class="campaign-kpi-grid">
              <div class="kpi-card">
                <div class="kpi-icon">📢</div>
                <div class="kpi-content">
                  <span class="kpi-label">মোট নির্ধারিত কর্মসূচি</span>
                  <b class="kpi-val">{{campaignEvents().length}} টি</b>
                  <span class="kpi-hint">জনসভা, উঠান বৈঠক ও রোডশো</span>
                </div>
              </div>

              <div class="kpi-card approved">
                <div class="kpi-icon">✅</div>
                <div class="kpi-content">
                  <span class="kpi-label">পুলিশ ও প্রশাসন অনুমোদিত</span>
                  <b class="kpi-val">{{approvedCampaignEventsCount()}} টি</b>
                  <span class="kpi-hint">লিখিত অনাপত্তি/পারমিট প্রাপ্ত</span>
                </div>
              </div>

              <div class="kpi-card pending">
                <div class="kpi-icon">⏳</div>
                <div class="kpi-content">
                  <span class="kpi-label">পারমিট অনুমোদন অপেক্ষমান</span>
                  <b class="kpi-val">{{pendingCampaignEventsCount()}} টি</b>
                  <span class="kpi-hint">থানা ও এআরও দফতরে আবেদনকৃত</span>
                </div>
              </div>

              <div class="kpi-card miking-compliance">
                <div class="kpi-icon">🔊</div>
                <div class="kpi-content">
                  <span class="kpi-label">মাইকিং আচরণবিধি ট্র্যাকার</span>
                  <b class="kpi-val">{{compliantMikingCount()}} / {{campaignEvents().length}}</b>
                  <span class="kpi-hint">দুপুর ২টা হতে রাত ৮টার বৈধ সময়সীমা</span>
                </div>
              </div>
            </div>

            <!-- EC Code of Conduct Notice Banner -->
            <div class="statutory-miking-rule-strip">
              <div class="rule-icon">⚖️</div>
              <div class="rule-text">
                <b>বাংলাদেশ নির্বাচন কমিশন আচরণবিধি গাইডেন্স (বিধি ১২ দ্রষ্টব্য):</b>
                নির্বাচনী প্রচারণায় কোনো নিবন্ধিত রাজনৈতিক দল বা প্রতিদ্বন্দ্বী প্রার্থী দুপুর ২:০০ ঘটিকার পূর্বে এবং রাত ৮:০০ ঘটিকার পরে কোনো ধরনের লাউডস্পিকার বা মাইক ব্যবহার করতে পারবেন না। যেকোনো পথসভা বা জনসভার স্থান ও সময় সম্পর্কে অন্তত ২৪ ঘণ্টা পূর্বে স্থানীয় পুলিশ প্রশাসনকে অবহিত করে লিখিত পারমিট গ্রহণ বাধ্যতামূলক।
              </div>
            </div>

            <!-- Filter Controls -->
            <div class="campaign-filter-strip">
              <div class="filter-col">
                <label>কর্মসূচির ধরন:</label>
                <select [ngModel]="campaignFilterType()" (ngModelChange)="campaignFilterType.set($event)">
                  <option value="ALL">সকল কর্মসূচি ({{campaignEvents().length}})</option>
                  <option value="RALLY">জনসভা ও পথসমাবেশ (Rally)</option>
                  <option value="MEETING">কর্মী সম্মেলন ও বৈঠক (Meeting)</option>
                  <option value="TRAINING">মাঠ প্রশিক্ষণ ও অন্যান্য (Training)</option>
                </select>
              </div>

              <div class="filter-col">
                <label>পুলিশ/ইসি পারমিট স্ট্যাটাস:</label>
                <select [ngModel]="campaignFilterPermit()" (ngModelChange)="campaignFilterPermit.set($event)">
                  <option value="ALL">সকল স্ট্যাটাস</option>
                  <option value="APPROVED">✓ অনুমোদিত (Approved)</option>
                  <option value="PENDING">⏳ অনুমোদন অপেক্ষমান (Pending)</option>
                  <option value="REJECTED">❌ প্রত্যাখ্যাত (Rejected)</option>
                </select>
              </div>

              <div class="filter-count">
                প্রদর্শিত কর্মসূচি: <b>{{filteredCampaignEvents().length}}</b> টি
              </div>
            </div>

            <!-- Campaign Events Table -->
            @if(loadingCampaign()){
              <div class="empty">কর্মসূচি তালিকা লোড হচ্ছে...</div>
            } @else if(filteredCampaignEvents().length === 0){
              <div class="empty">
                কোনো নির্বাচনী কর্মসূচি পাওয়া যায়নি। "+ নতুন নির্বাচনী সমাবেশ / রোডশো যুক্ত করুন" বাটনে ক্লিক করে নতুন শিডিউল যোগ করুন।
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table-modern campaign-table">
                  <thead>
                    <tr>
                      <th>কর্মসূচি ও বিবরণ</th>
                      <th>ধরন</th>
                      <th>তারিখ ও সময় (BST)</th>
                      <th>সভাস্থল / ভেন্যু</th>
                      <th>পুলিশ ও ইসি পারমিট</th>
                      <th>মাইকিং সময়সীমা</th>
                      <th style="text-align: right;">অ্যাকশন</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for(ev of filteredCampaignEvents(); track ev.eventId){
                      <tr>
                        <!-- 1. Title & Description -->
                        <td class="col-title">
                          <div class="event-title-text">{{ev.title}}</div>
                          @if(ev.description){
                            <div class="event-sub-desc">{{ev.description}}</div>
                          }
                          <small class="event-meta-created">তৈরি: {{ev.createdAtUtc | date:'dd MMM yyyy, h:mm a'}}</small>
                        </td>

                        <!-- 2. Type Badge -->
                        <td>
                          @if(ev.eventTypeId === 1){
                            <span class="type-pill rally">📢 জনসভা/পথসমাবেশ</span>
                          } @else if(ev.eventTypeId === 2){
                            <span class="type-pill meeting">🤝 কর্মী সম্মেলন</span>
                          } @else {
                            <span class="type-pill other">📋 {{ev.eventTypeName}}</span>
                          }
                        </td>

                        <!-- 3. Date & Time -->
                        <td class="col-datetime">
                          <div class="date-txt">📅 {{ev.startsAt | date:'dd MMM yyyy'}}</div>
                          <div class="time-txt">🕒 {{ev.startsAt | date:'hh:mm a'}} - {{ev.endsAt | date:'hh:mm a'}}</div>
                        </td>

                        <!-- 4. Venue -->
                        <td class="col-venue">
                          <div class="venue-name">📍 {{ev.venueName || 'সভাস্থল নির্ধারিত নেই'}}</div>
                          @if(ev.venueAddress){
                            <div class="venue-addr">{{ev.venueAddress}}</div>
                          }
                          @if(ev.venueCapacity){
                            <span class="venue-cap-badge">ধারণক্ষমতা: {{ev.venueCapacity | number:'1.0-0'}} জন</span>
                          }
                        </td>

                        <!-- 5. Permit Status -->
                        <td>
                          @if(ev.permitStatus === 'APPROVED'){
                            <span class="permit-badge approved">✓ অনুমোদিত</span>
                          } @else if(ev.permitStatus === 'REJECTED'){
                            <span class="permit-badge rejected">❌ প্রত্যাখ্যাত</span>
                          } @else {
                            <span class="permit-badge pending">⏳ অনুমোদন অপেক্ষমান</span>
                          }
                          @if(ev.permitReferenceNumber){
                            <div class="permit-ref">স্মারক: {{ev.permitReferenceNumber}}</div>
                          }
                          @if(ev.issuingAuthority){
                            <div class="permit-auth">{{ev.issuingAuthority}}</div>
                          }
                        </td>

                        <!-- 6. Miking Compliance -->
                        <td>
                          @if(ev.isMikingHoursCompliant){
                            <span class="miking-badge legal" title="দুপুর ২টা থেকে রাত ৮টা পর্যন্ত মাইকিং আচরণবিধির সাথে সঙ্গতিপূর্ণ">
                              🔊 বৈধ সময় (২pm - ৮pm)
                            </span>
                          } @else {
                            <span class="miking-badge violation" title="আচরণবিধি সতর্কতা: দুপুর ২টার পূর্বে বা রাত ৮টার পরে মাইকিং নিষিদ্ধ">
                              ⚠️ সময় সতর্কবার্তা
                            </span>
                          }
                        </td>

                        <!-- 7. Actions -->
                        <td style="text-align: right;">
                          <div class="action-buttons-group">
                            <button class="btn-sm btn-print-notice" (click)="openPrintPermitNotice(ev)" title="পুলিশ ও সহকারী রিটার্নিং অফিসার বরাবর অনুমতির আনুষ্ঠানিক আবেদনপত্র প্রিন্ট">
                              🖨️ আবেদনপত্র
                            </button>
                            <button class="btn-sm btn-update-permit" (click)="openUpdatePermitModal(ev)" title="পারমিট অনুমোদন স্ট্যাটাস ও স্মারক হালনাগাদ">
                              📝 পারমিট
                            </button>
                            <button class="btn-sm btn-delete-event" (click)="deleteCampaignEvent(ev)" title="কর্মসূচি বাতিল করুন">
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            }
          </section>
        }
"""

target_end_of_expenses = """                          <td>
                            <button class="btn-sm btn-danger" (click)="deleteExpense(v)" title="ভাউচারটি মুছে ফেলুন">✕ মুছে ফেলুন</button>
                          </td>
                        </tr>
                      }
                    </tbody>
                  </table>
                </div>
              }
            }
          </section>
        }"""

if target_end_of_expenses in content and "<!-- TAB 7: CAMPAIGN EVENTS" not in content:
    content = content.replace(target_end_of_expenses, target_end_of_expenses + "\n" + tab7_html, 1)
    print("Tab 7 HTML inserted successfully.")
else:
    print("WARN: target_end_of_expenses not found or Tab 7 already present.")

# 6. Insert Modals: Add Campaign Event, Update Permit, Printable Police Permission Notice
modals_html = """
    <!-- ===================================================================== -->
    <!-- MODAL: ADD CAMPAIGN EVENT -->
    <!-- ===================================================================== -->
    @if(showAddCampaignModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card campaign-modal-card">
          <div class="modal-header">
            <div>
              <h2>📅 নতুন নির্বাচনী সভা-সমাবেশ ও রোডশো এন্ট্রি</h2>
              <p class="subtitle">সভা, উঠান বৈঠক, মাইকিং রোডশো এবং পুলিশ পারমিটের তথ্য নির্ধারিত ফর্মে এন্ট্রি করুন</p>
            </div>
            <button class="close-btn" (click)="closeAddCampaignModal()">✕</button>
          </div>

          <form (ngSubmit)="submitNewCampaignEvent()">
            <div class="form-grid">
              <div class="form-field wide">
                <label>কর্মসূচির শিরোনাম *</label>
                <input [(ngModel)]="newCampaignForm.title" name="title" placeholder="যেমন: ইয়াকুবপুর কেন্দ্রীয় নির্বাচনী জনসভা ও পথসমাবেশ" required />
              </div>

              <div class="form-field">
                <label>কর্মসূচির ধরন *</label>
                <select [(ngModel)]="newCampaignForm.eventTypeId" name="eventTypeId" required>
                  <option [value]="1">📢 নির্বাচনী জনসভা ও পথসমাবেশ (Rally)</option>
                  <option [value]="2">🤝 কর্মী সম্মেলন ও উঠান বৈঠক (Meeting)</option>
                  <option [value]="3">📋 মাঠ প্রশিক্ষণ ও অন্যান্য (Training)</option>
                </select>
              </div>

              <div class="form-field">
                <label>সভা বা সমাবেশের স্থান (ভেন্যু) *</label>
                <select [(ngModel)]="newCampaignForm.venueId" name="venueId">
                  <option value="">-- নতুন ভেন্যু এন্ট্রি করুন --</option>
                  @for(v of campaignVenues(); track v.venueId){
                    <option [value]="v.venueId">{{v.name}} ({{v.address}})</option>
                  }
                </select>
              </div>

              @if(!newCampaignForm.venueId){
                <div class="form-field">
                  <label>নতুন ভেন্যুর নাম *</label>
                  <input [(ngModel)]="newCampaignForm.newVenueName" name="newVenueName" placeholder="যেমন: বরইয়া সরকারি প্রাথমিক বিদ্যালয় মাঠ" />
                </div>
                <div class="form-field">
                  <label>ভেন্যুর পূর্ণ ঠিকানা *</label>
                  <input [(ngModel)]="newCampaignForm.newVenueAddress" name="newVenueAddress" placeholder="যেমন: বরইয়া বাজার, দাগনভূঞা" />
                </div>
                <div class="form-field">
                  <label>আনুমানিক ধারণক্ষমতা (ব্যক্তি)</label>
                  <input type="number" [(ngModel)]="newCampaignForm.newVenueCapacity" name="newVenueCapacity" placeholder="যেমন: ২০০০" />
                </div>
              }

              <div class="form-field">
                <label>শুরুর তারিখ ও সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.startsAt" name="startsAt" required />
              </div>

              <div class="form-field">
                <label>সমাপ্তির তারিখ ও সময় *</label>
                <input type="datetime-local" [(ngModel)]="newCampaignForm.endsAt" name="endsAt" required />
              </div>

              <!-- Realtime Miking Hours Legal Alert -->
              <div class="form-field wide">
                @if(isNewEventMikingCompliant()){
                  <div class="miking-alert-box legal">
                    <b>✓ মাইকিং আইনানুগ সময়সীমা:</b> নির্ধারিত সময়সীমা (দুপুর ২:০০টা হতে রাত ৮:০০টা) নির্বাচন কমিশন আচরণবিধি ২০০৮ এর বিধি ১২(১) এর সাথে সম্পূর্ণ সঙ্গতিপূর্ণ।
                  </div>
                } @else {
                  <div class="miking-alert-box alert">
                    <b>⚠️ নির্বাচন আচরণবিধি সতর্কতা:</b> নির্বাচন আচরণবিধিমালা ২০০৮ এর বিধি ১২(১) অনুযায়ী দুপুর ২:০০ ঘটিকার পূর্বে বা রাত ৮:০০ ঘটিকার পরে কোনো ধরনের লাউডস্পিকার বা মাইকিং ব্যবহার দণ্ডনীয় অপরাধ।
                  </div>
                }
              </div>

              <div class="form-field">
                <label>অনুমোদন প্রদানকারী কর্তৃপক্ষ</label>
                <input [(ngModel)]="newCampaignForm.issuingAuthority" name="authority" placeholder="যেমন: দাগনভূঞা থানা পুলিশ ও সহকারী রিটার্নিং অফিসার" />
              </div>

              <div class="form-field">
                <label>আবেদন ট্র্যাকিং / পারমিট স্মারক নং</label>
                <input [(ngModel)]="newCampaignForm.permitReferenceNumber" name="permitRef" placeholder="যেমন: আবেদন-২০২৬/১১২" />
              </div>

              <div class="form-field">
                <label>প্রাথমিক পারমিট স্ট্যাটাস</label>
                <select [(ngModel)]="newCampaignForm.permitStateId" name="permitStateId">
                  <option [value]="1">⏳ অনুমোদন অপেক্ষমান (Pending)</option>
                  <option [value]="2">✓ অনুমোদিত (Approved)</option>
                </select>
              </div>

              <div class="form-field wide">
                <label>কর্মসূচির রুট ও সংক্ষিপ্ত বিবরণ / আলোচ্য বিষয়</label>
                <textarea [(ngModel)]="newCampaignForm.description" name="description" rows="2" placeholder="কর্মসূচির বিস্তারিত বিবরণ ও মাইকিং রুট..."></textarea>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeAddCampaignModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingCampaignEvent()">
                {{savingCampaignEvent() ? 'সংরক্ষণ হচ্ছে...' : 'কর্মসূচি সংরক্ষণ করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- MODAL: UPDATE CAMPAIGN PERMIT STATUS -->
    <!-- ===================================================================== -->
    @if(showUpdatePermitModal()){
      <div class="modal-backdrop no-print">
        <div class="card modal-card" style="max-width: 500px;">
          <div class="modal-header">
            <div>
              <h2>📝 পুলিশ ও ইসি পারমিট স্ট্যাটাস হালনাগাদ</h2>
              <p class="subtitle">{{selectedEventForPermit()?.title}}</p>
            </div>
            <button class="close-btn" (click)="closeUpdatePermitModal()">✕</button>
          </div>

          <form (ngSubmit)="submitUpdatePermit()">
            <div class="form-field wide" style="margin-bottom: 12px;">
              <label>পারমিট অনুমোদন অবস্থা *</label>
              <select [(ngModel)]="updatePermitForm.permitStateId" name="upPermitState" required>
                <option [value]="2">✓ অনুমোদিত (Approved)</option>
                <option [value]="1">⏳ আবেদন অপেক্ষমান (Pending)</option>
                <option [value]="3">❌ বাতিল / প্রত্যাখ্যাত (Rejected)</option>
              </select>
            </div>

            <div class="form-field wide" style="margin-bottom: 12px;">
              <label>অনুমোদন প্রদানকারী কর্তৃপক্ষ *</label>
              <input [(ngModel)]="updatePermitForm.issuingAuthority" name="upAuth" placeholder="অফিসার ইনচার্জ (ওসি), দাগনভূঞা থানা" required />
            </div>

            <div class="form-field wide" style="margin-bottom: 12px;">
              <label>অফিসিয়াল স্মারক / রেফারেন্স নম্বর *</label>
              <input [(ngModel)]="updatePermitForm.permitReferenceNumber" name="upRef" placeholder="যেমন: দাগন-থানা/পারমিট-অনুমোদন/২০২৬/১১২" required />
            </div>

            <div class="form-field wide" style="margin-bottom: 16px;">
              <label>মেয়াদ উত্তীর্ণের তারিখ</label>
              <input type="date" [(ngModel)]="updatePermitForm.expiresOn" name="upExpires" />
            </div>

            <div class="modal-actions">
              <button type="button" class="text-button" (click)="closeUpdatePermitModal()">বাতিল</button>
              <button type="submit" class="primary-button" [disabled]="savingCampaignPermit()">
                {{savingCampaignPermit() ? 'হালনাগাদ হচ্ছে...' : 'পারমিট তথ্য সংরক্ষণ করুন'}}
              </button>
            </div>
          </form>
        </div>
      </div>
    }

    <!-- ===================================================================== -->
    <!-- PRINTABLE VIEW: OFFICIAL POLICE & ARO PERMIT APPLICATION NOTICE -->
    <!-- ===================================================================== -->
    @if(showPrintPermitNoticeModal()){
      <div class="modal-backdrop print-modal-backdrop">
        <div class="card modal-card permit-notice-modal-card">
          <!-- Control Strip (Hidden in Print) -->
          <div class="modal-header permit-notice-header no-print">
            <div>
              <h2>🖨️ নির্বাচনী সভা ও মাইক ব্যবহারের অনুমতির অফিশিয়াল আবেদনপত্র</h2>
              <p class="subtitle">অফিসার ইনচার্জ (ওসি), দাগনভূঞা থানা এবং সহকারী রিটার্নিং অফিসার বরাবর পেশযোগ্য A4 আবেদনপত্র</p>
            </div>
            <div class="modal-header-actions">
              <button class="primary-button print-action-btn" (click)="triggerBrowserPrint()">
                🖨️ আবেদনপত্র প্রিন্ট করুন (A4)
              </button>
              <button class="close-btn" (click)="closePrintPermitNotice()">✕</button>
            </div>
          </div>

          <!-- Formal Application Letterhead & Body -->
          <div class="official-police-notice-sheet">
            <!-- Formal Letterhead -->
            <div class="notice-letterhead">
              <div class="cand-sym-avatar">
                <span class="avatar-icon">{{data()?.candidate?.symbolEmoji || '⚖️'}}</span>
                <span class="avatar-caption">{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</span>
              </div>
              <div class="cand-text-head">
                <h1 class="cand-official-name">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</h1>
                <div class="cand-post-sub">চেয়ারম্যান পদপ্রার্থী · ৫ নং ইয়াকুবপুর ইউনিয়ন পরিষদ সাধারণ নির্বাচন ২০২৬</div>
                <div class="cand-office-line">কেন্দ্রীয় নির্বাচনী প্রধান কার্যালয়: ইয়াকুবপুর বাজার, দাগনভূঞা, ফেনী। মোবাইল: ০১৭০৭-XXXXXX</div>
              </div>
            </div>

            <div class="notice-divider-line"></div>

            <!-- Memo & Date Row -->
            <div class="memo-date-row">
              <div class="memo-col">স্মারক নং: ইসি/আবেদন/২০২৬/{{selectedEventForNotice()?.permitReferenceNumber || '১১২'}}</div>
              <div class="date-col">তারিখ: {{selectedEventForNotice()?.startsAt | date:'dd MMMM yyyy'}} খ্রিষ্টাব্দ</div>
            </div>

            <!-- Addressed Authority -->
            <div class="addressed-block">
              <b>বরাবর,</b><br/>
              <b>অফিসার ইনচার্জ (ওসি)</b><br/>
              দাগনভূঞা থানা পুলিশ, ফেনী।<br/><br/>
              <b>অনুলিপি সদয় অবগতির জন্য:</b><br/>
              সহকারী রিটার্নিং অফিসার ও উপজেলা নির্বাহী অফিসার (ইউএনও), দাগনভূঞা, ফেনী।
            </div>

            <!-- Subject -->
            <div class="subject-line">
              <b>বিষয়: আসন্ন ইউনিয়ন পরিষদ নির্বাচনে নির্বাচনী পথসভা/জনসভা অনুষ্ঠান ও মাইক ব্যবহারের লিখিত অনুমতি প্রদান প্রসঙ্গে।</b>
            </div>

            <!-- Context & Statutory Rules -->
            <div class="body-paragraphs">
              <p>
                জনাব,<br/>
                যথাযথ সম্মানপূর্বক বিনীত নিবেদন এই যে, আমি নিম্নস্বাক্ষরকারী আসন্ন ৫ নং ইয়াকুবপুর ইউনিয়ন পরিষদ নির্বাচনে বাংলাদেশ নির্বাচন কমিশন কর্তৃক বৈধভাবে মনোনীত ও প্রতীকপ্রাপ্ত প্রতিদ্বন্দ্বী প্রার্থী (প্রতীক: <b>{{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}}</b>)। নির্বাচনী গণসংযোগ ও ভোটার সাধারণের সাথে সরাসরি মতবিনিময়ের নিমিত্তে আমার নির্বাচনী এলাকায় নিম্নবর্ণিত সূচি অনুযায়ী একটি শান্তিপূর্ণ নির্বাচনী সভা অনুষ্ঠানের প্রয়োজনীয়তা দেখা দিয়েছে।
              </p>

              <!-- Event Specification Table -->
              <table class="permit-details-table">
                <tbody>
                  <tr>
                    <td class="lbl">কর্মসূচির শিরোনাম:</td>
                    <td class="val"><b>{{selectedEventForNotice()?.title}}</b></td>
                  </tr>
                  <tr>
                    <td class="lbl">কর্মসূচির ধরন:</td>
                    <td class="val">{{selectedEventForNotice()?.eventTypeName}}</td>
                  </tr>
                  <tr>
                    <td class="lbl">নির্ধারিত স্থান (ভেন্যু):</td>
                    <td class="val"><b>{{selectedEventForNotice()?.venueName}}</b> ({{selectedEventForNotice()?.venueAddress}})</td>
                  </tr>
                  <tr>
                    <td class="lbl">তারিখ ও সময়সীমা:</td>
                    <td class="val">
                      <b>{{selectedEventForNotice()?.startsAt | date:'dd MMMM yyyy (EEEE)'}}, বেলা {{selectedEventForNotice()?.startsAt | date:'hh:mm a'}} হতে {{selectedEventForNotice()?.endsAt | date:'hh:mm a'}} পর্যন্ত</b>
                      <span class="time-assurance-tag">✓ দুপুর ২:০০টা হতে রাত ৮:০০টার আইনি সময়সীমাভুক্ত</span>
                    </td>
                  </tr>
                  <tr>
                    <td class="lbl">প্রত্যাশিত জনসমাগম:</td>
                    <td class="val">আনুমানিক {{selectedEventForNotice()?.venueCapacity || 2000 | number}} জন ভোটার ও কর্মী-সমর্থক</td>
                  </tr>
                  <tr>
                    <td class="lbl">সাউন্ড সিস্টেম সরঞ্জাম:</td>
                    <td class="val">সর্বোচ্চ ২টি মাঝারি সাউন্ড বক্স / হ্যান্ড মাইক (শব্দদূষণ নিয়ন্ত্রণে রাখা হবে)</td>
                  </tr>
                </tbody>
              </table>

              <!-- Formal Statutory Undertaking (অঙ্গীকারনামা) -->
              <div class="undertaking-box">
                <div class="undertaking-title"><b>প্রার্থীর সুস্পষ্ট অঙ্গীকারনামা (Conduct of Elections Undertaking):</b></div>
                <ol class="undertaking-list">
                  <li>নির্বাচন কমিশন প্রণীত স্থানীয় সরকার (নির্বাচন আচরণ) বিধিমালা, ২০০৮ এর বিধি ১২(১) অক্ষরে অক্ষরে পালনপূর্বক কেবল দুপুর ২:০০ ঘটিকা হতে রাত ৮:০০ ঘটিকার মধ্যে সীমাবদ্ধ শব্দযন্ত্র পরিচালিত হবে।</li>
                  <li>জনসাধারণের স্বাভাবিক চলাচলে কোনো প্রতিবন্ধকতা কিংবা রাস্তায় কোনো প্রকার যানজট সৃষ্টি হতে দেওয়া হবে না।</li>
                  <li>কোনো উসকানিমূলক বক্তব্য, শান্তি-শৃঙ্খলা বিনষ্টকারী তৎপরতা কিংবা আইনপরিপন্থী কোনো আচরণ সম্পূর্ণ নিষিদ্ধ থাকবে।</li>
                  <li>দায়িত্বপ্রাপ্ত পুলিশ প্রশাসন ও বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেটের যেকোনো তাৎক্ষণিক দিকনির্দেশনা ও সিদ্ধান্ত চূড়ান্ত বলিয়া মানিয়া লওয়া হইবে।</li>
                </ol>
              </div>

              <p class="closing-prayer">
                অতএব, মহোদয়ের নিকট আকুল আবেদন, উপরোল্লিখিত নির্ধারিত স্থান ও সময়ে শান্তিপূর্ণ নির্বাচনী জনসভা পরিচালনা ও সীমিত পরিসরে মাইক ব্যবহারের লিখিত অনুমতি প্রদানপূর্বক প্রয়োজনীয় আইন-শৃঙ্খলা নিরাপত্তা ও সার্বিক সহযোগিতা প্রদানে আপনার সদয় মর্জি হয়।
              </p>
            </div>

            <!-- Signatures Grid -->
            <div class="police-notice-signatures">
              <div class="sign-slot">
                <div class="sign-line"></div>
                <b>প্রধান নির্বাচনী এজেন্টের স্বাক্ষর</b>
                <span>নাম: .................................................</span>
                <span>মোবাইল: .............................................</span>
              </div>
              <div class="sign-slot">
                <div class="sign-line"></div>
                <b>বিনীত নিবেদক (প্রতিদ্বন্দ্বী প্রার্থী)</b>
                <b class="cand-bold">{{data()?.candidate?.name || 'ডঃ কাজী উবায়েদ উল্লাহ ফারুক'}}</b>
                <span>চেয়ারম্যান পদপ্রার্থী (প্রতীক: {{data()?.candidate?.symbolNameBn || 'দাঁড়িপাল্লা'}})</span>
              </div>
            </div>

            <!-- Carbon Copies (CC) -->
            <div class="notice-cc-box">
              <b>অনুলিপি সদয় অবগতি ও প্রয়োজনীয় কার্যার্থে প্রেরিত:</b><br/>
              ১. মাননীয় রিটার্নিং অফিসার ও জেলা নির্বাচন কর্মকর্তা, ফেনী জেলা।<br/>
              ২. পুলিশ সুপার (SP), ফেনী জেলা।<br/>
              ৩. বিজ্ঞ এক্সিকিউটিভ ম্যাজিস্ট্রেট (ভ্রাম্যমাণ আদালত), দাগনভূঞা উপজেলা, ফেনী।<br/>
              ৪. সহকারী পুলিশ সুপার (দাগনভূঞা সার্কেল), ফেনী।<br/>
              ৫. অফিস কপি।
            </div>
          </div>
        </div>
      </div>
    }
"""

if "<!-- MODAL: ADD CAMPAIGN EVENT -->" not in content:
    idx_styles = content.find("  styles: [`")
    if idx_styles != -1:
        content = content[:idx_styles] + modals_html + "\n\n  " + content[idx_styles:]
        print("Campaign modals inserted successfully.")
    else:
        print("ERROR: styles anchor not found.")

# 7. Add CSS rules for Campaign Events and Police Notice
campaign_css = """
    /* =========================================================================
       CAMPAIGN EVENTS, RALLIES & PERMITS STYLES (বিকল্প ৩)
       ========================================================================= */
    .campaign-events-panel { margin-top: 16px; }
    .campaign-kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 18px 0; }
    .campaign-kpi-grid .kpi-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; display: flex; gap: 12px; align-items: center; }
    .campaign-kpi-grid .kpi-card.approved { background: #f0fdf4; border-color: #bbf7d0; }
    .campaign-kpi-grid .kpi-card.pending { background: #fffbeb; border-color: #fde68a; }
    .campaign-kpi-grid .kpi-card.miking-compliance { background: #f5f3ff; border-color: #ddd6fe; }
    .campaign-kpi-grid .kpi-icon { font-size: 26px; }
    .campaign-kpi-grid .kpi-content { display: flex; flex-direction: column; }
    .campaign-kpi-grid .kpi-label { font-size: 0.78rem; font-weight: 600; color: #475569; }
    .campaign-kpi-grid .kpi-val { font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1.2; margin: 2px 0; }
    .campaign-kpi-grid .kpi-hint { font-size: 0.72rem; color: #64748b; }

    .statutory-miking-rule-strip { display: flex; gap: 12px; background: #fff8eb; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 0.85rem; color: #78350f; line-height: 1.45; }
    .statutory-miking-rule-strip .rule-icon { font-size: 22px; flex-shrink: 0; }

    .campaign-filter-strip { display: flex; gap: 14px; align-items: flex-end; background: #f8fafc; padding: 12px 16px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 16px; flex-wrap: wrap; }
    .campaign-filter-strip .filter-col { display: flex; flex-direction: column; gap: 4px; }
    .campaign-filter-strip .filter-col label { font-size: 0.76rem; font-weight: 700; color: #475569; }
    .campaign-filter-strip .filter-col select { padding: 6px 12px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.84rem; background: #fff; }
    .campaign-filter-strip .filter-count { margin-left: auto; font-size: 0.85rem; font-weight: 600; color: #334155; }

    .campaign-table { width: 100%; border-collapse: collapse; }
    .campaign-table th { background: #f1f5f9; padding: 10px 12px; font-size: 0.8rem; font-weight: 700; color: #334155; text-align: left; border-bottom: 2px solid #cbd5e1; }
    .campaign-table td { padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 0.86rem; vertical-align: top; }
    .campaign-table .col-title .event-title-text { font-weight: 700; color: #0f172a; font-size: 0.92rem; }
    .campaign-table .col-title .event-sub-desc { font-size: 0.78rem; color: #64748b; margin-top: 3px; }
    .campaign-table .col-title .event-meta-created { font-size: 0.72rem; color: #94a3b8; display: block; margin-top: 4px; }

    .type-pill { display: inline-block; padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 700; }
    .type-pill.rally { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .type-pill.meeting { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    .type-pill.other { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    .col-datetime .date-txt { font-weight: 700; color: #1e293b; }
    .col-datetime .time-txt { font-size: 0.78rem; color: #64748b; margin-top: 2px; }

    .col-venue .venue-name { font-weight: 600; color: #0f172a; }
    .col-venue .venue-addr { font-size: 0.76rem; color: #64748b; }
    .col-venue .venue-cap-badge { display: inline-block; margin-top: 3px; font-size: 0.7rem; background: #f1f5f9; padding: 1px 6px; border-radius: 4px; color: #475569; }

    .permit-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.74rem; font-weight: 700; }
    .permit-badge.approved { background: #dcfce7; color: #166534; }
    .permit-badge.pending { background: #fef3c7; color: #92400e; }
    .permit-badge.rejected { background: #fee2e2; color: #991b1b; }
    .permit-ref { font-size: 0.74rem; font-weight: 600; color: #334155; margin-top: 3px; }
    .permit-auth { font-size: 0.7rem; color: #64748b; }

    .miking-badge { display: inline-block; padding: 3px 8px; border-radius: 8px; font-size: 0.74rem; font-weight: 700; }
    .miking-badge.legal { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
    .miking-badge.violation { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }

    .action-buttons-group { display: flex; gap: 6px; justify-content: flex-end; }
    .btn-print-notice { background: #082136; color: #fff; border: none; border-radius: 6px; padding: 4px 9px; font-weight: 600; cursor: pointer; }
    .btn-update-permit { background: #e2e8f0; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 4px 8px; font-weight: 600; cursor: pointer; }
    .btn-delete-event { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; border-radius: 6px; padding: 4px 8px; cursor: pointer; }

    .miking-alert-box { padding: 10px 14px; border-radius: 8px; font-size: 0.82rem; line-height: 1.4; margin-top: 6px; }
    .miking-alert-box.legal { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
    .miking-alert-box.alert { background: #fff7ed; border: 1px solid #fdba74; color: #9a3412; }

    /* Official Printable Notice Letter Styles */
    .official-police-notice-sheet { font-family: 'SolaimanLipi', 'Kalpurush', 'Nikosh', Arial, sans-serif; padding: 24px 32px; background: #fff; color: #111; line-height: 1.5; font-size: 14px; }
    .notice-letterhead { display: flex; align-items: center; gap: 18px; margin-bottom: 12px; }
    .cand-sym-avatar { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 68px; height: 68px; border: 2px solid #082136; border-radius: 12px; background: #f8fafc; }
    .cand-sym-avatar .avatar-icon { font-size: 32px; line-height: 1; }
    .cand-sym-avatar .avatar-caption { font-size: 11px; font-weight: 800; color: #082136; margin-top: 2px; }
    .cand-text-head .cand-official-name { font-size: 22px; font-weight: 800; color: #082136; margin: 0; line-height: 1.2; }
    .cand-text-head .cand-post-sub { font-size: 13px; font-weight: 700; color: #334155; margin: 2px 0; }
    .cand-text-head .cand-office-line { font-size: 11.5px; color: #64748b; }
    .notice-divider-line { height: 2px; background: #082136; margin: 10px 0 16px 0; }

    .memo-date-row { display: flex; justify-content: space-between; font-weight: 600; font-size: 13px; margin-bottom: 14px; }
    .addressed-block { font-size: 13.5px; line-height: 1.45; margin-bottom: 14px; }
    .subject-line { font-size: 14.5px; background: #f1f5f9; padding: 8px 12px; border-left: 4px solid #082136; margin-bottom: 14px; }

    .permit-details-table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px; }
    .permit-details-table td { padding: 6px 10px; border: 1px solid #cbd5e1; }
    .permit-details-table td.lbl { background: #f8fafc; font-weight: 700; width: 28%; color: #334155; }
    .permit-details-table td.val { color: #0f172a; }
    .time-assurance-tag { display: inline-block; margin-left: 8px; font-size: 11px; background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; padding: 1px 6px; border-radius: 4px; font-weight: 700; }

    .undertaking-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; margin: 14px 0; }
    .undertaking-title { font-size: 13px; color: #082136; margin-bottom: 6px; }
    .undertaking-list { margin: 0; padding-left: 20px; font-size: 12.5px; line-height: 1.5; color: #1e293b; }

    .closing-prayer { margin-top: 14px; font-size: 13.5px; line-height: 1.5; }

    .police-notice-signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 45px; text-align: center; }
    .police-notice-signatures .sign-slot { display: flex; flex-direction: column; align-items: center; font-size: 12.5px; }
    .police-notice-signatures .sign-line { width: 180px; border-top: 1.5px dashed #334155; margin-bottom: 6px; }
    .police-notice-signatures .cand-bold { font-size: 14px; font-weight: 800; color: #082136; margin-top: 2px; }

    .notice-cc-box { margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-size: 11.5px; color: #475569; line-height: 1.5; }
"""

if "CAMPAIGN EVENTS, RALLIES & PERMITS STYLES" not in content:
    idx_closing_styles = content.rfind("  `]")
    if idx_closing_styles != -1:
        content = content[:idx_closing_styles] + campaign_css + "\n  `]" + content[idx_closing_styles+4:]
        print("Campaign CSS rules added.")
    else:
        print("ERROR: closing styles anchor not found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Base campaign template patched successfully.")

