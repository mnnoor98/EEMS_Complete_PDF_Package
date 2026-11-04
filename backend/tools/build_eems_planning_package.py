from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT = Path('output/docx/EEMS_Complete_Planning_Package_BN.docx')
OUT.parent.mkdir(parents=True, exist_ok=True)

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.7); sec.bottom_margin = Inches(0.65)
sec.left_margin = Inches(0.75); sec.right_margin = Inches(0.75)

styles = doc.styles
for name, size, bold in [('Normal', 10.2, False), ('Title', 26, True), ('Subtitle', 12, False),
                         ('Heading 1', 18, True), ('Heading 2', 14, True), ('Heading 3', 11.5, True)]:
    st = styles[name]
    st.font.name = 'Nirmala UI'; st.font.size = Pt(size); st.font.bold = bold; st.font.color.rgb = RGBColor(0,0,0)
    st._element.rPr.rFonts.set(qn('w:ascii'), 'Nirmala UI')
    st._element.rPr.rFonts.set(qn('w:hAnsi'), 'Nirmala UI')
    st._element.rPr.rFonts.set(qn('w:cs'), 'Nirmala UI')
styles['Normal'].paragraph_format.space_after = Pt(5)
styles['Normal'].paragraph_format.line_spacing = 1.12
styles['Heading 1'].paragraph_format.space_before = Pt(16); styles['Heading 1'].paragraph_format.space_after = Pt(7)
styles['Heading 1'].paragraph_format.keep_with_next = True
styles['Heading 2'].paragraph_format.space_before = Pt(11); styles['Heading 2'].paragraph_format.space_after = Pt(5)
styles['Heading 2'].paragraph_format.keep_with_next = True
styles['Heading 3'].paragraph_format.space_before = Pt(8); styles['Heading 3'].paragraph_format.space_after = Pt(3)
styles['Heading 3'].paragraph_format.keep_with_next = True

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = tcPr.find(qn('w:shd'))
    if shd is None: shd = OxmlElement('w:shd'); tcPr.append(shd)
    shd.set(qn('w:fill'), fill)

def borders(table):
    tblPr = table._tbl.tblPr
    el = tblPr.find(qn('w:tblBorders'))
    if el is None: el=OxmlElement('w:tblBorders'); tblPr.append(el)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        x=OxmlElement('w:'+edge); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),'4'); x.set(qn('w:color'),'D9D9D9'); el.append(x)

def set_cell_margin(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr(); mar = tcPr.first_child_found_in('w:tcMar')
    if mar is None: mar=OxmlElement('w:tcMar'); tcPr.append(mar)
    for k,v in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node=mar.find(qn('w:'+k))
        if node is None: node=OxmlElement('w:'+k); mar.append(node)
        node.set(qn('w:w'),str(v)); node.set(qn('w:type'),'dxa')

def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    trPr=t.rows[0]._tr.get_or_add_trPr(); repeat=OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true'); trPr.append(repeat)
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=h; shade(c,'17395B'); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; set_cell_margin(c)
        for r in c.paragraphs[0].runs: r.font.bold=True; r.font.color.rgb=RGBColor(255,255,255); r.font.size=Pt(9)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        trPr=t.rows[-1]._tr.get_or_add_trPr(); no_split=OxmlElement('w:cantSplit'); trPr.append(no_split)
        for i,val in enumerate(row):
            cells[i].text=str(val); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; set_cell_margin(cells[i])
            if ri%2: shade(cells[i],'F2F6F8')
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(1)
                for r in p.runs: r.font.size=Pt(8.7)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Inches(w)
    borders(t); doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t

def bullet(text, level=0):
    p=doc.add_paragraph(style='List Bullet' if level==0 else 'List Bullet 2'); p.add_run(text); return p

def page(): doc.add_page_break()
def h1(x): doc.add_heading(x,1)
def h2(x): doc.add_heading(x,2)
def h3(x): doc.add_heading(x,3)
def para(x, boldlead=None):
    p=doc.add_paragraph()
    if boldlead: p.add_run(boldlead).bold=True
    p.add_run(x)
    return p

# Cover
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(80)
r=p.add_run('EEMS'); r.bold=True; r.font.size=Pt(16); r.font.color.rgb=RGBColor(23,57,91)
p=doc.add_paragraph('নির্বাচন কার্যক্রম ব্যবস্থাপনা সফটওয়্যার', style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph('সমন্বিত পরিকল্পনা ও উন্নয়ন হ্যান্ডঅফ', style='Subtitle'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(22)
p.add_run('Software Requirements Specification  |  User Stories  |  Data Design  |  Sprint Backlog').bold=True
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(100)
p.add_run('সংস্করণ ১.০\n২ নভেম্বর ২০২৬\nপ্রস্তুতকৃত Development Planning Baseline')
page()

h1('ডকুমেন্টের উদ্দেশ্য ও সিদ্ধান্ত')
para('এই ডকুমেন্ট সংসদ, উপজেলা, ইউনিয়ন, পৌরসভা ও সিটি কর্পোরেশন নির্বাচন পরিচালনার জন্য EEMS সফটওয়্যারের কার্যকর উন্নয়ন ভিত্তি নির্ধারণ করে। এটি product owner, business analyst, architect, developer, QA, DevOps, security reviewer এবং প্রকল্প মালিকের অভিন্ন handoff হিসেবে ব্যবহারযোগ্য।')
para('প্রস্তাবিত সিদ্ধান্ত হলো ASP.NET Core ও Angular ভিত্তিক modular monolith দিয়ে শুরু করা, PostgreSQL Row Level Security দিয়ে tenant বিচ্ছিন্নতা নিশ্চিত করা এবং মাঠপর্যায়ের কাজের জন্য mobile first interface তৈরি করা। প্রথম production release-এ নির্বাচন সেটআপ, কেন্দ্র, টিম, readiness, incident, result verification এবং audit অগ্রাধিকার পাবে।')
h2('পরিধি')
table(['অন্তর্ভুক্ত', 'প্রথম সংস্করণে অন্তর্ভুক্ত নয়'], [
    ['নির্বাচন, প্রার্থী, এলাকা, কেন্দ্র ও বুথ', 'ভোটারের রাজনৈতিক পছন্দ অনুমান'],
    ['টিম, এজেন্ট, প্রশিক্ষণ, উপস্থিতি ও কাজ', 'ব্যক্তিভিত্তিক persuasion score'],
    ['বাজেট, ব্যয়, inventory ও approval', 'অননুমোদিত সরকারি ফলাফল প্রকাশ'],
    ['incident, evidence, ফলাফল ও audit', 'আইনের বিকল্প হিসেবে automated legal decision'],
], [3.2,3.2])
h2('নকশার মূল নীতি')
for x in ['প্রতিটি tenant-owned record-এ tenant_id এবং fail-closed authorization থাকবে।','Role-এর পাশাপাশি election, area, center ও action scope যাচাই হবে।','Field result এবং official result দৃশ্যত ও ডেটাবেসে আলাদা থাকবে।','Maker এবং checker একই ব্যক্তি হতে পারবে না।','বাংলা ও ইংরেজি interface, mobile responsive layout এবং accessibility বাধ্যতামূলক।','বর্তমান নির্বাচন আইন, আচরণবিধি ও privacy requirement অনুযায়ী go-live-এর আগে স্বাধীন legal এবং security review হবে।']: bullet(x)

h1('১ ব্যবসায়িক চাহিদা')
h2('১.১ লক্ষ্য')
table(['ID','চাহিদা','সাফল্য মাপকাঠি'], [
 ['BR-01','এক platform থেকে একাধিক নির্বাচন পরিচালনা','সমর্থিত পাঁচ election type configuration দিয়ে চালু করা যায়'],
 ['BR-02','এলাকা ও কেন্দ্রভিত্তিক দায়িত্ব নিয়ন্ত্রণ','অননুমোদিত এলাকার data API ও UI উভয় স্তরে অদৃশ্য'],
 ['BR-03','Election day operational visibility','center readiness, agent, incident ও result status dashboard-এ দৃশ্যমান'],
 ['BR-04','অর্থ ও সম্পদের জবাবদিহি','প্রতিটি approval ও movement actor/time সহ audit হয়'],
 ['BR-05','বিশ্বাসযোগ্য ফলাফল সংগ্রহ','source evidence ও independent verification ছাড়া verified নয়'],
 ['BR-06','দুর্বল internet-এ সীমিত কাজ','অনুমোদিত workflow encrypted offline draft সমর্থন করে'],
], [0.7,3.7,2.1])
h2('১.২ নির্বাচন ও পদ configuration')
table(['Election type','উদাহরণ পদ','Scope'], [
 ['PARLIAMENTARY','সংসদ সদস্য','সংসদীয় আসন'],['UPAZILA','চেয়ারম্যান, ভাইস চেয়ারম্যান','উপজেলা'],
 ['UNION','চেয়ারম্যান, সাধারণ সদস্য, সংরক্ষিত সদস্য','ইউনিয়ন ও ওয়ার্ড'],
 ['MUNICIPALITY','মেয়র, কাউন্সিলর','পৌরসভা ও ওয়ার্ড'],['CITY','মেয়র, কাউন্সিলর','সিটি ও ওয়ার্ড']
], [1.35,2.7,2.45])

h1('২ ব্যবহারকারী ও অনুমতি')
table(['Persona','মূল দায়িত্ব','Scope'], [
 ['Platform operator','tenant, plan ও platform audit','সব tenant; কঠোর privileged audit'],
 ['Tenant admin','user, role, election ও settings','নিজ tenant'],
 ['Election manager','নির্বাচনের configuration ও operation','assigned election'],
 ['Area coordinator','team, task, readiness ও incident','assigned area descendants'],
 ['Center coordinator','agent, checklist ও center status','assigned center'],
 ['Finance maker','budget line ও expense submission','assigned election/area'],
 ['Finance checker','expense review ও approval','maker থেকে পৃথক'],
 ['Result submitter','source document সহ ফলাফল দাখিল','assigned center'],
 ['Result verifier','ফলাফল যাচাই বা dispute','submitter থেকে পৃথক'],
 ['Auditor','report ও immutable audit review','read-only, masked PII'],
], [1.45,3.05,2.0])
h2('২.১ Permission model')
para('Authorization decision = tenant membership + permission code + election scope + area/center scope + resource state। UI menu শুধু সুবিধার স্তর; চূড়ান্ত সিদ্ধান্ত API এবং data access layer নেবে।')
table(['Permission family','উদাহরণ'], [
 ['Election','election.read, election.create, election.publish'],['Polling','polling.center.read, polling.agent.assign'],
 ['Finance','finance.expense.create, finance.expense.approve'],['Operations','incident.create, incident.review'],
 ['Results','results.submit, results.verify, results.official.read'],['Audit','audit.read, audit.export']
], [2.0,4.5])

h1('৩ Functional Requirements')
modules = [
('FR-01 Tenant ও Identity',['organization account এবং status','user invitation, MFA ও session management','role permission matrix এবং scope assignment','privilege escalation prevention']),
('FR-02 Geography',['hierarchical area tree','constituency ও area mapping','authorized source import with provenance, checksum, effective date','cycle এবং duplicate prevention']),
('FR-03 Election ও Candidate',['draft election, type, date, area ও milestone','config validation শেষে publish','candidate profile, nomination reference ও document','position-election compatibility']),
('FR-04 Polling',['canonical center ও election assignment আলাদা','booth, address, verification ও readiness','agent shift ও conflicting assignment detection','center workspace']),
('FR-05 Team ও Task',['team, leader, member ও area assignment','training এবং attendance','task owner, due date, priority ও status','area dashboard']),
('FR-06 Event',['calendar, venue, permit ও attachment','task linkage এবং completion report','start/end validation','document evidence']),
('FR-07 Finance',['budget, category, line, vendor ও expense','invoice duplicate check','maker-checker workflow','approved history immutable; adjustment record']),
('FR-08 Inventory',['item, warehouse, receipt ও transfer','center/team allocation','return, consumed বা lost disposition','balanced stock movement ledger']),
('FR-09 Operations',['readiness checklist ও RAG status','incident, evidence, confidentiality ও assignment','timeline ও escalation','resolution review']),
('FR-10 Results',['center/position/candidate vote entry','nonnegative এবং total consistency','source document ও hash','independent verification, dispute ও reconciliation','official result আলাদা dataset']),
('FR-11 Report ও Audit',['overview, finance, center, incident ও result report','authorized Excel/PDF export','PII masking','export এবং security audit']),
]
for title, items in modules:
    h2(title)
    for x in items: bullet(x)

h1('৪ Workflow ও Business Rules')
table(['বস্তু','অবস্থা','প্রধান guard'], [
 ['Election','DRAFT → ACTIVE → CLOSED → ARCHIVED','configuration complete এবং publish permission'],
 ['Expense','DRAFT → SUBMITTED → REVIEW → APPROVED বা RETURNED','maker/checker পৃথক; budget constraint'],
 ['Incident','REPORTED → TRIAGED → ASSIGNED → RESOLVED → CLOSED','evidence, reviewer ও resolution'],
 ['Result','DRAFT → SUBMITTED → REVIEW → VERIFIED বা DISPUTED → ARCHIVED','source evidence ও independent verifier'],
 ['Inventory','RECEIVED → ALLOCATED → RETURNED বা CONSUMED','balanced ledger ও recipient acknowledgement'],
], [1.1,2.8,2.6])
h2('৪.১ অপরিবর্তনীয় নিয়ম')
for x in ['Client পাঠানো tenant_id বিশ্বাস করা যাবে না।','নিজের expense নিজে approve করা যাবে না।','নিজের result submission নিজে verify করা যাবে না।','Closed election পরিবর্তন privileged, reasoned এবং audited operation ছাড়া সম্ভব নয়।','Approved financial record overwrite নয়; adjustment/reversal record তৈরি হবে।','Verified result-এর evidence পরিবর্তন হলে verification পুনরায় প্রয়োজন।','Official result কেবল authorized workflow/উৎস থেকে আসবে এবং field tally থেকে পৃথক থাকবে।']: bullet(x)

h1('৫ Nonfunctional Requirements')
table(['ক্ষেত্র','Requirement'], [
 ['Security','OIDC, PKCE/BFF cookie, MFA, CSRF protection, rate limit, secure upload, least privilege'],
 ['Performance','প্রতিনিধিত্বমূলক workload-এ ১,০০০ concurrent user design target; p95 SLA load test-এ নির্ধারিত'],
 ['Availability','health check, monitored deployment, rollback path, backup ও restore rehearsal'],
 ['Accessibility','WCAG 2.2 AA target, keyboard, screen reader landmark, 200% zoom ও contrast'],
 ['Localization','Bangla/English strings; stable English permission code; Asia/Dhaka election context'],
 ['Auditability','security, approval, result, export ও privileged action actor/time/correlation সহ'],
 ['Privacy','data minimization, masking, retention, no inferred political preference'],
 ['Observability','structured log, trace, metric; secrets ও sensitive narrative log-এ নয়'],
], [1.45,5.05])

h1('৬ Solution Architecture')
para('Angular client → ASP.NET Core API modular monolith → PostgreSQL, Redis এবং object storage। Background worker report export, notification, malware scan callback, reconciliation ও archival চালাবে। Domain data এবং outbox message একই transaction-এ লেখা হবে।')
table(['Layer','প্রযুক্তি ও দায়িত্ব'], [
 ['Frontend','Angular standalone components, strict TypeScript, reactive forms, lazy routes'],
 ['API','ASP.NET Core, RFC 7807, /api/v1, idempotency, ETag/version'],
 ['Application','commands/queries, validation, authorization, transaction boundary'],
 ['Domain','aggregate, invariant, workflow transition'],
 ['Infrastructure','EF Core, Npgsql, Redis, object storage, Hangfire, outbox'],
 ['Operations','Docker, reverse proxy, CI/CD, OpenTelemetry, monitoring'],
], [1.45,5.05])
h2('৬.১ Module boundary')
para('Tenants | Identity | Geography | Elections | Candidates | Polling | Teams | Events | Finance | Inventory | Operations | Results | Reporting। প্রতিটি module নিজের domain, application, infrastructure এবং API contract নিয়ন্ত্রণ করবে।')

h1('৭ Production Data Design')
h2('৭.১ Logical ERD')
para('Tenant 1—N Election; Tenant 1—N TenantUser; ElectionType 1—N Position; Area 1—N child Area; Election 1—N CandidateElection; Election 1—N ElectionCenter; Election 1—N Team; Budget 1—N BudgetLine 1—N Expense; ResultSubmission 1—N ResultDetail এবং 1—N ResultVerification।')
table(['Schema','প্রধান entity'], [
 ['core','tenants, tenant_settings, plans, subscriptions'],['iam','users, tenant_users, roles, permissions, user_roles, user_scopes, sessions'],
 ['geo','area_types, areas, constituencies, constituency_areas, imports'],['election','election_types, positions, elections, milestones, candidates, candidate_elections'],
 ['polling','centers, booths, election_centers, agent_assignments'],['team','teams, team_members, tasks, attendance, trainings'],
 ['campaign','events, venues, permits, event_documents'],['finance','budgets, budget_lines, vendors, expenses, approvals, payments, adjustments'],
 ['inventory','items, warehouses, stock_movements, allocations'],['operations','checklists, checklist_items, incidents, incident_reviews'],
 ['results','submissions, details, verifications, disputes, official_results, result_documents'],['audit','audit_logs, security_events, export_logs, outbox_messages'],
], [1.25,5.25])
h2('৭.২ Production hardening')
for x in ['প্রতিটি tenant reference-এ composite unique key এবং composite foreign key।','Submission-এর center ও candidate একই tenant এবং election-এর কিনা database constraint।','সব tenant table-এ ENABLE এবং FORCE RLS; runtime role table owner বা BYPASSRLS নয়।','Transaction শুরুতে verified context থেকে SET LOCAL app.tenant_id।','Geo hierarchy cycle trigger/validator এবং automated test।','version integer বা documented xmin concurrency strategy।','Document metadata: storage key, SHA-256, MIME, size, scan status, retention।','Audit table volume অনুযায়ী monthly partition; অনুমানভিত্তিক premature partition নয়।']: bullet(x)

h1('৮ API Contract')
table(['নীতি','চুক্তি'], [
 ['Base','/api/v1; REST resource noun; JSON'],['Errors','RFC 7807 ProblemDetails + traceId'],
 ['Create','201 Created + Location; Idempotency-Key critical create command-এ'],['Update','ETag/version; conflict হলে 409'],
 ['Pagination','page/pageSize বা cursor; maximum 100'],['Time','UTC ISO 8601 timestamp; election date local calendar date'],
 ['Files','signed short-lived URL; scan pending state; hash'],['Compatibility','v1-এর মধ্যে backward compatible additive change'],
], [1.3,5.2])
h2('৮.১ প্রধান endpoint')
table(['Module','Endpoint sample'], [
 ['Election','GET/POST /elections; PUT /elections/{id}; POST /elections/{id}/publish'],['Polling','GET/POST /polling-centers; POST /elections/{id}/centers; POST /agent-assignments'],
 ['Finance','GET/POST /expenses; POST /expenses/{id}/submit; POST /expenses/{id}/approve'],['Operations','GET /readiness; POST /incidents; POST /incidents/{id}/review'],
 ['Results','POST /results/submissions; POST /results/{id}/verify; GET /results/official'],['Reports','GET /reports/overview; GET /reports/expenses; GET /audit-logs'],
], [1.35,5.15])

h1('৯ Frontend Screen Catalog')
table(['Feature','Screens'], [
 ['Identity','Users, Roles, Permissions, Scopes, Sessions'],['Elections','List, Create, Workspace, Schedule, Positions'],
 ['Candidates','Directory, Profile, Candidate Election'],['Geography','Area Tree, Constituencies, Imports'],
 ['Polling','Centers, Center Detail, Booths, Assignments'],['Teams','Teams, Members, Assignment, Training, Attendance'],
 ['Events','Calendar, Event, Permits, Task Board'],['Finance','Budgets, Expenses, Approvals, Vendors, Payments'],
 ['Inventory','Items, Receipts, Transfers, Allocations'],['Operations','Readiness, Agents, Incidents, Timeline'],
 ['Results','Submission, Review, Official, Reconciliation'],['Reports','Overview, Finance, Centers, Incidents, Results, Audit'],
], [1.45,5.05])
h2('৯.১ UX acceptance')
for x in ['প্রতিটি list-এ server filter, sort, pagination, loading, empty, error ও retry state।','প্রতিটি form-এ create/edit/read-only, dirty warning, inline/server error এবং concurrency token।','Forbidden route পরিষ্কার 403 দেখাবে; redirect loop নয়।','মোবাইলে center checklist, attendance, incident ও result entry ব্যবহারযোগ্য।','Offline কেবল অনুমোদিত draft; encrypted storage, explicit sync এবং conflict review।']: bullet(x)

h1('১০ User Story Backlog')
stories = [
('US-001','Tenant admin','ব্যবহারকারী আমন্ত্রণ ও scope দিতে চাই','সঠিক নির্বাচনী এলাকা ছাড়া data access হয় না','Must'),
('US-002','Election manager','খসড়া নির্বাচন তৈরি ও publish করতে চাই','configuration অসম্পূর্ণ হলে publish বন্ধ','Must'),
('US-003','Election manager','নির্বাচনের ধরন অনুযায়ী পদ নির্ধারণ চাই','অসামঞ্জস্য position reject','Must'),
('US-004','Area coordinator','এলাকার center ও team দেখতে চাই','শুধু authorized descendant area','Must'),
('US-005','Center coordinator','readiness checklist পূরণ করতে চাই','actor/time সহ current status','Must'),
('US-006','Team leader','member task ও attendance নিতে চাই','conflicting assignment warning','Should'),
('US-007','Finance maker','invoice সহ expense submit করতে চাই','positive amount ও duplicate check','Should'),
('US-008','Finance checker','expense approve বা return করতে চাই','নিজের submission approve নয়','Should'),
('US-009','Inventory manager','center-এ item allocate করতে চাই','balanced movement ও recipient record','Could'),
('US-010','Agent','incident evidenceসহ report করতে চাই','time, source, confidentiality required','Must'),
('US-011','Result submitter','center result ও source document দাখিল করতে চাই','nonnegative, total check, idempotent','Must'),
('US-012','Result verifier','submission verify বা dispute করতে চাই','submitter থেকে আলাদা identity','Must'),
('US-013','Auditor','approval ও পরিবর্তনের history দেখতে চাই','read-only, masked personal data','Must'),
('US-014','Manager','election-day dashboard চাই','readiness, agent, incident, result status','Must'),
('US-015','Field user','offline draft রেখে পরে sync চাই','encrypted, confirmation, conflict handling','Could'),
]
table(['ID','Actor','চাহিদা','Acceptance summary','Priority'], stories, [0.65,1.05,2.2,2.15,0.7])

h1('১১ Release ও Sprint Plan')
para('দুই সপ্তাহের sprint ধরে ১৬টি sprint-এর একটি বাস্তবসম্মত baseline নিচে দেওয়া হলো। Team capacity ও discovery অনুযায়ী backlog পুনরায় estimate হবে।')
sprints = [
('Sprint 0','Discovery','workflow workshop, legal/security assumptions, architecture decision, UX map'),
('Sprint 1','Foundation','solution, CI, environments, tenant skeleton, observability'),
('Sprint 2','Identity','OIDC, MFA, user invitation, role/permission baseline'),
('Sprint 3','Geography','area tree, constituency, import provenance, scope tests'),
('Sprint 4','Election','election type, position, election lifecycle, publish guard'),
('Sprint 5','Candidate','candidate, documents, candidate-election mapping'),
('Sprint 6','Polling','center, booth, election center, verification/import'),
('Sprint 7','Teams','team, member, assignment, training, attendance'),
('Sprint 8','Operations','readiness checklist, agent coverage, dashboard'),
('Sprint 9','Incident','report, triage, evidence, review, timeline'),
('Sprint 10','Finance','budget, expense, maker-checker, audit'),
('Sprint 11','Inventory','item, warehouse, stock movement, allocation'),
('Sprint 12','Results entry','submission, detail, source document, validations'),
('Sprint 13','Verification','verify/dispute, reconciliation, official separation'),
('Sprint 14','Reports','overview, exports, masking, export audit'),
('Sprint 15','Hardening','security, performance, accessibility, backup restore, UAT'),
]
table(['Sprint','Theme','Deliverable'], sprints, [0.9,1.35,4.1])
h2('১১.১ Release gates')
table(['Gate','Exit criteria'], [
 ['MVP Pilot','Sprint 9 শেষে identity, election, polling, team, readiness ও incident pilot-ready'],
 ['Operations Release','Sprint 11 শেষে finance ও inventoryসহ operational workflow'],
 ['Election Day Release','Sprint 14 শেষে result, reconciliation ও reports'],
 ['Production','Sprint 15 security review, UAT, restore ও rollback pass'],
], [1.45,4.95])

h1('১২ Testing ও Definition of Done')
table(['Test layer','আবশ্যক পরীক্ষা'], [
 ['Unit','domain invariant, validator, permission scope, totals'],['Integration','real PostgreSQL migration, RLS, transaction, outbox'],
 ['Security','cross-tenant IDOR, privilege escalation, token misuse, upload malware'],['Contract','OpenAPI compatibility, ProblemDetails, generated client'],
 ['E2E','tenant switch, unauthorized route, expense approval, result discrepancy'],['Performance','representative data, 1,000-user design target, queue age'],
 ['Accessibility','keyboard, screen reader, 200% zoom, Bangla font, contrast'],['Recovery','backup restore, point-in-time recovery, deployment rollback'],
], [1.35,5.15])
h2('Definition of Done')
for x in ['Database migration reviewed এবং rollback/forward strategy documented।','Backend authorization ও frontend guard দুটোই implemented।','Audit event ও correlation ID observable।','Unit, integration, security-relevant এবং acceptance test pass।','Bangla/English text এবং responsive layout verified।','API contract ও release note updated।','Product owner acceptance criteria sign-off।']: bullet(x)

h1('১৩ Deployment ও Operations')
for x in ['Development, staging এবং production আলাদা environment ও secret।','Migration CI/CD release job চালাবে; application startup-এ uncontrolled migration নয়।','Nightly full backup + WAL/PITR; নিয়মিত restore drill।','Health check, p95 latency, error rate, failed login, queue age, DB pool ও replication lag alert।','Canary বা blue-green deployment যেখানে সমর্থিত; প্রতিটি release-এ rollback path।','Incident response runbook এবং privileged access review।']: bullet(x)

page()
h1('১৪ Risk Register')
table(['Risk','প্রভাব','Mitigation'], [
 ['আইন বা নির্বাচন প্রক্রিয়া পরিবর্তন','workflow অচল বা noncompliant','configurable workflow; legal review before release'],
 ['দুর্বল internet','field update বিলম্ব','mobile first; limited encrypted offline draft'],
 ['Cross-tenant leak','অত্যন্ত গুরুতর privacy/security breach','RLS, scoped authorization, negative security test'],
 ['ভুল বা duplicate result','বিশ্বাসযোগ্যতা ক্ষতি','idempotency, source hash, independent verifier, reconciliation'],
 ['Insider privilege misuse','data/approval manipulation','least privilege, MFA, maker-checker, immutable audit'],
 ['Traffic spike','election-day outage','load test, caching, queue, capacity plan, monitoring'],
 ['Malicious upload','system compromise','MIME/size controls, malware scan, isolated object storage'],
 ['Scope growth','সময় ও বাজেট বৃদ্ধি','MVP gate, backlog priority, change control'],
], [1.6,2.0,2.9])

h1('১৫ Team ও Governance')
table(['Role','প্রস্তাবিত দায়িত্ব'], [
 ['Product owner / BA','domain decision, backlog, acceptance'],['Architect / Tech lead','architecture, security boundary, code review'],
 ['Backend developers 2','API, domain, database, integration'],['Frontend developers 2','Angular, mobile UX, accessibility'],
 ['QA / Automation','test strategy, regression, security cases'],['DevOps','CI/CD, environment, monitoring, recovery'],
 ['UI UX','workflow research, prototype, design system'],['Security ও Legal reviewer','independent go-live assessment'],
], [2.0,4.5])

h1('১৬ প্রথম ৩০ দিনের কর্মপরিকল্পনা')
table(['সময়','কাজ','Output'], [
 ['দিন ১–৫','stakeholder workshop, election workflow ও role validation','approved scope এবং glossary'],
 ['দিন ৬–১০','user journey, wireframe, data classification','prototype এবং privacy map'],
 ['দিন ১১–১৫','architecture decision, repository ও CI baseline','running skeleton in staging'],
 ['দিন ১৬–২০','tenant, identity, permission ও RLS spike','cross-tenant isolation proof'],
 ['দিন ২১–২৫','geography import এবং election aggregate','reviewed migration/API contract'],
 ['দিন ২৬–৩০','demo, threat review, backlog re-estimate','Sprint 1 acceptance ও revised roadmap'],
], [1.0,3.2,2.3])

h1('১৭ Open Decisions')
for x in ['প্রথম pilot কোন election type এবং কোন geographic scope-এ হবে?','OIDC provider এবং hosting model cloud, on-premise নাকি hybrid?','Official geography ও polling center data-এর অনুমোদিত উৎস কী?','SMS/email/push notification-এর provider ও consent policy কী?','Document retention এবং closed election archive period কত?','Offline result draft অনুমোদিত হবে কি না? হলে কোন device/security policy-তে?','Peak center, user, attachment এবং result volume কত?']: bullet(x)

h1('১৮ উৎস ও ব্যবহার নির্দেশনা')
para('এই planning package EEMS PostgreSQL Database Blueprint, Backend Development Blueprint এবং Frontend Development Blueprint version 1.0-এর সমন্বিত উন্নয়ন handoff। Blueprint-এর starter DDL production-ready সম্পূর্ণ schema নয়; implementation-এর সময় এই ডকুমেন্টের production hardening, acceptance criteria এবং legal/security review অনুসরণ করতে হবে।')
para('পরবর্তী অনুমোদিত artefact হওয়া উচিত: বিস্তারিত screen wireframe, OpenAPI specification, production migration set, test matrix এবং deployment runbook।')

# Footer page field
for section in doc.sections:
    footer=section.footer
    p=footer.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('EEMS Planning Package  |  '); r.font.size=Pt(8); r.font.color.rgb=RGBColor(90,90,90)
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); p._p.append(fld)

doc.core_properties.title='EEMS নির্বাচন কার্যক্রম ব্যবস্থাপনা সফটওয়্যার সমন্বিত পরিকল্পনা'
doc.core_properties.subject='SRS, user stories, production data design and sprint backlog'
doc.core_properties.author='EEMS Project'
doc.save(OUT)
print(OUT.resolve())
