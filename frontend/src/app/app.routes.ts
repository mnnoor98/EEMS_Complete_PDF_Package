import {Routes} from '@angular/router';
import {authGuard,permissionGuard} from './core/guards/auth.guard';
export const routes:Routes=[
 {path:'login',loadComponent:()=>import('./features/auth/login.page').then(m=>m.LoginPage)},
 {path:'',canActivate:[authGuard],loadComponent:()=>import('./layout/shell/shell.component').then(m=>m.ShellComponent),children:[
  {path:'',pathMatch:'full',redirectTo:'dashboard'},
  {path:'dashboard',canActivate:[permissionGuard],data:{permission:'dashboard.read'},loadComponent:()=>import('./features/dashboard/operations-dashboard.page').then(m=>m.OperationsDashboardPage)},
  {path:'elections',loadComponent:()=>import('./features/elections/election-list.page').then(m=>m.ElectionListPage)},
  {path:'elections/:electionId/candidates',canActivate:[permissionGuard],data:{permission:'elections.read'},loadComponent:()=>import('./features/candidates/candidate-list.page').then(m=>m.CandidateListPage)},
  {path:'elections/:electionId/workforce',canActivate:[permissionGuard],data:{permission:'workforce.read'},loadComponent:()=>import('./features/workforce/workforce-dashboard.page').then(m=>m.WorkforceDashboardPage)},
  {path:'elections/:electionId/centers',canActivate:[permissionGuard],data:{permission:'polling.read'},loadComponent:()=>import('./features/polling/polling-centers.page').then(m=>m.PollingCentersPage)},
  {path:'elections/:electionId/centers/:electionCenterId',canActivate:[permissionGuard],data:{permission:'polling.read'},loadComponent:()=>import('./features/polling/polling-center-detail.page').then(m=>m.PollingCenterDetailPage)},
  {path:'elections/:electionId/results',canActivate:[permissionGuard],data:{permission:'results.read'},loadComponent:()=>import('./features/results/results-reporting.page').then(m=>m.ResultsReportingPage)},
  {path:'elections/:electionId/inventory',canActivate:[permissionGuard],data:{permission:'inventory.read'},loadComponent:()=>import('./features/inventory/inventory.page').then(m=>m.InventoryPage)},
  {path:'elections/:electionId/finance',canActivate:[permissionGuard],data:{permission:'finance.read'},loadComponent:()=>import('./features/finance/finance.page').then(m=>m.FinancePage)},
  {path:'elections/:electionId/events',canActivate:[permissionGuard],data:{permission:'events.read'},loadComponent:()=>import('./features/events/events.page').then(m=>m.EventsPage)},
  {path:'administration',canActivate:[permissionGuard],data:{permission:'dashboard.read'},loadComponent:()=>import('./features/administration/administration.page').then(m=>m.AdministrationPage)},
  {path:'oversight',canActivate:[permissionGuard],data:{permission:'reporting.read'},loadComponent:()=>import('./features/oversight/oversight.page').then(m=>m.OversightPage)},
  {path:'forbidden',loadComponent:()=>import('./shared/status/forbidden.page').then(m=>m.ForbiddenPage)}
 ]},
 {path:'**',redirectTo:''}
];
