import sys

file_path = 'frontend/src/app/features/candidates/candidate-war-room.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
old_import = "  CreateExpenseVoucherRequest,\n  EcExpenseScheduleReport,"
new_import = "  CandidateCenterResultItem,\n  UploadAndVerifyForm8Request,\n  Form8DetailResponse,\n  CreateExpenseVoucherRequest,\n  EcExpenseScheduleReport,"
if old_import in content:
    content = content.replace(old_import, new_import, 1)
    print("Updated imports.")
else:
    print("Could not find old_import")

# 2. Add header button in Results tab
old_results_btn = """                  <button class="primary-button quick-vote-btn" (click)="openQuickResultModal()">
                    ⚡ কেন্দ্রের ভোট এন্ট্রি করুন
                  </button>"""

new_results_btn = """                  <div class="results-top-actions">
                    <button class="primary-button quick-vote-btn" (click)="openQuickResultModal()">
                      ⚡ কেন্দ্রের ভোট এন্ট্রি করুন
                    </button>
                    <button class="outline-button print-cert-btn" (click)="openWinnerCertificateModal()">
                      🖨️ ফলাফল সংহতকরণ প্রত্যয়নপত্র প্রিন্ট
                    </button>
                  </div>"""

if old_results_btn in content:
    content = content.replace(old_results_btn, new_results_btn, 1)
    print("Updated results header button.")
else:
    print("Could not find old_results_btn")

# 3. Update center table row to add Form-8 button and link
old_center_row = """                          <td>
                            @if(cr.form8Verified){
                              <span class="badge-success">✓ ফরম-৮ যাচাইকৃত</span>
                            } @else if(cr.isCounted){
                              <span class="badge-pending">ফলাফল প্রাপ্ত</span>
                            } @else {
                              <span class="badge-muted">অপেক্ষমান</span>
                            }
                          </td>
                          <td>
                            <button class="btn-sm btn-action" (click)="openQuickResultModal(cr.electionCenterId)">
                              {{cr.isCounted ? '✏️ সংশোধন' : '➕ ভোট এন্ট্রি'}}
                            </button>
                          </td>"""

new_center_row = """                          <td>
                            @if(cr.form8Verified || cr.form8DocumentUrl){
                              <span class="badge-success">✓ ফরম-৮ যাচাইকৃত</span>
                              @if(cr.form8DocumentUrl){
                                <a [href]="cr.form8DocumentUrl" target="_blank" class="form8-link" title="সংযুক্ত ফরম-৮ শিট দেখুন">📄 ফাইল</a>
                              }
                            } @else if(cr.isCounted){
                              <span class="badge-pending">ফলাফল প্রাপ্ত</span>
                            } @else {
                              <span class="badge-muted">অপেক্ষমান</span>
                            }
                          </td>
                          <td>
                            <div class="row-actions-group">
                              <button class="btn-sm btn-action" (click)="openQuickResultModal(cr.electionCenterId)">
                                {{cr.isCounted ? '✏️ সংশোধন' : '➕ ভোট এন্ট্রি'}}
                              </button>
                              <button class="btn-sm btn-form8" (click)="openForm8Modal(cr)" [class.has-doc]="cr.form8DocumentUrl">
                                📄 ফরম-৮ শিট
                              </button>
                            </div>
                          </td>"""

if old_center_row in content:
    content = content.replace(old_center_row, new_center_row, 1)
    print("Updated center table row.")
else:
    print("Could not find old_center_row")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved part 1.")

