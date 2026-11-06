import { Routes } from '@angular/router';
import { authGuard, permissionGuard } from './core/guards/auth.guard';
export const routes: Routes = [
    { path: 'login', loadComponent: () => import('./features/auth/login.page').then(m => m.LoginPage) },
    { path: 'change-password', canActivate: [authGuard], loadComponent: () => import('./features/auth/change-password.page').then(m => m.ChangePasswordPage) },
    {
        path: '', canActivate: [authGuard], loadComponent: () => import('./layout/shell/shell.component').then(m => m.ShellComponent), children: [
            { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
            { path: 'dashboard', canActivate: [permissionGuard], data: { permission: 'dashboard.read' }, loadComponent: () => import('./features/dashboard/operations-dashboard.page').then(m => m.OperationsDashboardPage) },
            { path: 'elections', loadComponent: () => import('./features/elections/election-list.page').then(m => m.ElectionListPage) },
            { path: 'elections/:electionId/candidates', canActivate: [permissionGuard], data: { permission: 'elections.read' }, loadComponent: () => import('./features/candidates/candidate-list.page').then(m => m.CandidateListPage) },
            { path: 'candidates/entry', canActivate: [authGuard], loadComponent: () => import('./features/candidates/candidate-entry.page').then(m => m.CandidateEntryPage) },
            { path: 'candidates/master-overview', canActivate: [authGuard], loadComponent: () => import('./features/candidates/master-candidates.page').then(m => m.MasterCandidatesPage) },
            { path: 'elections/:electionId/candidates/entry', canActivate: [authGuard], loadComponent: () => import('./features/candidates/candidate-entry.page').then(m => m.CandidateEntryPage) },
            { path: 'elections/:electionId/candidate-war-room', canActivate: [permissionGuard], data: { permission: 'elections.read' }, loadComponent: () => import('./features/candidates/candidate-war-room.page').then(m => m.CandidateWarRoomPage) },
            { path: 'elections/:electionId/workforce', canActivate: [permissionGuard], data: { permission: 'workforce.read' }, loadComponent: () => import('./features/workforce/workforce-dashboard.page').then(m => m.WorkforceDashboardPage) },
            { path: 'elections/:electionId/workforce/teams', canActivate: [permissionGuard], data: { permission: 'workforce.read' }, loadComponent: () => import('./features/workforce/workforce-teams.page').then(m => m.WorkforceTeamsPage) },
            { path: 'elections/:electionId/workforce/teams/:teamId', canActivate: [permissionGuard], data: { permission: 'workforce.read' }, loadComponent: () => import('./features/workforce/workforce-team-detail.page').then(m => m.WorkforceTeamDetailPage) },
            { path: 'elections/:electionId/workforce/teams/:teamId/members/:memberId', canActivate: [permissionGuard], data: { permission: 'workforce.read' }, loadComponent: () => import('./features/workforce/workforce-field-member-detail.page').then(m => m.WorkforceFieldMemberDetailPage) },
            { path: 'centers', pathMatch: 'full', redirectTo: 'elections/7a2ec4ed-9aba-4707-aa49-a58b51e82713/centers' },
            { path: 'polling-centers', pathMatch: 'full', redirectTo: 'elections/7a2ec4ed-9aba-4707-aa49-a58b51e82713/centers' },
            { path: 'elections/:electionId/centers', canActivate: [permissionGuard], data: { permission: 'polling.read' }, loadComponent: () => import('./features/polling/polling-centers.page').then(m => m.PollingCentersPage) },
            { path: 'elections/:electionId/centers/:electionCenterId', canActivate: [permissionGuard], data: { permission: 'polling.read' }, loadComponent: () => import('./features/polling/polling-center-detail.page').then(m => m.PollingCenterDetailPage) },
            { path: 'elections/:electionId/results', canActivate: [permissionGuard], data: { permission: 'results.read' }, loadComponent: () => import('./features/results/results-reporting.page').then(m => m.ResultsReportingPage) },
            { path: 'elections/:electionId/inventory', canActivate: [permissionGuard], data: { permission: 'inventory.read' }, loadComponent: () => import('./features/inventory/inventory.page').then(m => m.InventoryPage) },
            { path: 'elections/:electionId/finance', canActivate: [permissionGuard], data: { permission: 'finance.read' }, loadComponent: () => import('./features/finance/finance.page').then(m => m.FinancePage) },
            { path: 'elections/:electionId/events', canActivate: [permissionGuard], data: { permission: 'events.read' }, loadComponent: () => import('./features/events/events.page').then(m => m.EventsPage) },
            { path: 'administration', canActivate: [permissionGuard], data: { permission: 'dashboard.read' }, loadComponent: () => import('./features/administration/administration.page').then(m => m.AdministrationPage) },
            { path: 'administration/users', canActivate: [authGuard], loadComponent: () => import('./features/administration/user-creation.page').then(m => m.UserCreationPage) },
            { path: 'administration/master-data', canActivate: [permissionGuard], data: { permission: 'elections.manage' }, loadComponent: () => import('./features/administration/master-data.page').then(m => m.MasterDataPage) },
            { path: 'oversight', canActivate: [permissionGuard], data: { permission: 'reporting.read' }, loadComponent: () => import('./features/oversight/oversight.page').then(m => m.OversightPage) },
            { path: 'forbidden', loadComponent: () => import('./shared/status/forbidden.page').then(m => m.ForbiddenPage) }
        ]
    },
    { path: '**', redirectTo: '' }
];
