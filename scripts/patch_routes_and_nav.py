import sys

# 1. Patch app.routes.ts
with open('frontend/src/app/app.routes.ts', 'r', encoding='utf-8') as f:
    routes_content = f.read()

cand_target = "  {path:'elections/:electionId/candidates',canActivate:[permissionGuard],data:{permission:'elections.read'},loadComponent:()=>import('./features/candidates/candidate-list.page').then(m=>m.CandidateListPage)},\n"

cand_repl = (
    "  {path:'elections/:electionId/candidates',canActivate:[permissionGuard],data:{permission:'elections.read'},loadComponent:()=>import('./features/candidates/candidate-list.page').then(m=>m.CandidateListPage)},\n"
    "  {path:'candidates/entry',canActivate:[authGuard],loadComponent:()=>import('./features/candidates/candidate-entry.page').then(m=>m.CandidateEntryPage)},\n"
    "  {path:'elections/:electionId/candidates/entry',canActivate:[authGuard],loadComponent:()=>import('./features/candidates/candidate-entry.page').then(m=>m.CandidateEntryPage)},\n"
)

admin_target = "  {path:'administration',canActivate:[permissionGuard],data:{permission:'dashboard.read'},loadComponent:()=>import('./features/administration/administration.page').then(m=>m.AdministrationPage)},\n"

admin_repl = (
    "  {path:'administration',canActivate:[permissionGuard],data:{permission:'dashboard.read'},loadComponent:()=>import('./features/administration/administration.page').then(m=>m.AdministrationPage)},\n"
    "  {path:'administration/users',canActivate:[authGuard],loadComponent:()=>import('./features/administration/user-creation.page').then(m=>m.UserCreationPage)},\n"
)

if cand_target in routes_content and admin_target in routes_content:
    routes_content = routes_content.replace(cand_target, cand_repl).replace(admin_target, admin_repl)
    with open('frontend/src/app/app.routes.ts', 'w', encoding='utf-8') as f:
        f.write(routes_content)
    print("app.routes.ts patched successfully!")
else:
    print("Could not find targets in app.routes.ts")

# 2. Patch shell.component.ts navigation
with open('frontend/src/app/layout/shell/shell.component.ts', 'r', encoding='utf-8') as f:
    shell_content = f.read()

nav_target = """      <a routerLink="/elections/7a2ec4ed-9aba-4707-aa49-a58b51e82713/candidate-war-room" routerLinkActive="active"><span>🗳️</span> প্রার্থী ওয়ার রুম</a>
      <a routerLink="/elections" routerLinkActive="active"><span>▦</span> নির্বাচন তালিকা</a>"""

nav_repl = """      <a routerLink="/elections/7a2ec4ed-9aba-4707-aa49-a58b51e82713/candidate-war-room" routerLinkActive="active"><span>🗳️</span> প্রার্থী ওয়ার রুম</a>
      <a routerLink="/candidates/entry" routerLinkActive="active"><span>👤</span> প্রার্থী তথ্য এন্ট্রি</a>
      <a routerLink="/administration/users" routerLinkActive="active"><span>👥</span> ইউজার তৈরি ও রোল</a>
      <a routerLink="/elections" routerLinkActive="active"><span>▦</span> নির্বাচন তালিকা</a>"""

if nav_target in shell_content:
    shell_content = shell_content.replace(nav_target, nav_repl)
    with open('frontend/src/app/layout/shell/shell.component.ts', 'w', encoding='utf-8') as f:
        f.write(shell_content)
    print("shell.component.ts patched successfully!")
else:
    print("Could not find nav_target in shell.component.ts")

# 3. Patch administration.page.ts header to link to user creation page
with open('frontend/src/app/features/administration/administration.page.ts', 'r', encoding='utf-8') as f:
    admin_content = f.read()

admin_btn_target = """<button class="primary-button" (click)="openOnboarding()">+ Onboard staff</button>"""
admin_btn_repl = """<div style="display:flex;gap:8px;"><a routerLink="/administration/users" class="outline" style="text-decoration:none;font-size:0.8rem;display:inline-flex;align-items:center;background:#eef6f8;color:var(--teal);">👥 ইউজার তৈরি পেজ →</a><button class="primary-button" (click)="openOnboarding()">+ Onboard staff</button></div>"""

if admin_btn_target in admin_content:
    admin_content = admin_content.replace(admin_btn_target, admin_btn_repl)
    # Check if RouterLink is imported in administration.page.ts
    if "import {RouterLink} from '@angular/router';" not in admin_content and "RouterLink" not in admin_content.split("@Component")[1].split("imports:")[1].split("]")[0]:
        admin_content = admin_content.replace("imports:[DatePipe,FormsModule]", "imports:[DatePipe,FormsModule,RouterLink]")
        admin_content = "import {RouterLink} from '@angular/router';\n" + admin_content
    with open('frontend/src/app/features/administration/administration.page.ts', 'w', encoding='utf-8') as f:
        f.write(admin_content)
    print("administration.page.ts patched successfully!")
else:
    print("Could not find admin_btn_target in administration.page.ts")

print("All done!")

