import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {
  AgentAssignmentSummary, AttendanceSummary, BoothSummary, CandidateSummary, CenterDetail, CenterDirectoryItem, ChecklistSummary,FieldMemberSummary,FieldAttendanceSummary,MemberWorkSummary,
  ElectionCenterSummary, ElectionLookups, ElectionSummary, PagedResult, PollingLookups, TeamMemberSummary, TeamSummary,
  AdministrationDashboard, AllocationSummary, AuditPage, BudgetLineSummary, BudgetSummary, CampaignEventSummary, EventWorkspace, ExpenseSummary, ExportSummary, FinanceWorkspace, InventoryLookups, ItemSummary, MeetingSummary, MovementSummary, NotificationFeed, OperationsDashboard, PermissionSummary, ResultLookups, ResultSubmissionSummary, RoleSummary, TeamTaskSummary, TrainingSummary, UserSummary, VendorSummary, VenueSummary, VerificationSummary, WarehouseSummary, WorkforceLookups
} from '../models/api.models';

@Injectable({providedIn: 'root'})
export class EemsApiService {
  private readonly http = inject(HttpClient);
  getElectionLookups() { return this.http.get<ElectionLookups>('/api/v1/elections/lookups'); }
  getElections() { return this.http.get<ElectionSummary[]>('/api/v1/elections'); }
  createElection(body: {electionTypeId: number; areaId: number; lifecycleStateId: number; name: string; electionDate: string}) { return this.http.post<ElectionSummary>('/api/v1/elections', body); }
  updateElection(election: ElectionSummary, body: {electionTypeId: number; areaId: number; name: string; electionDate: string}) { return this.http.put<ElectionSummary>(`/api/v1/elections/${election.electionId}`, {...body, expectedVersion: election.version}); }
  moveElection(election: ElectionSummary, lifecycleStateId: number) { return this.http.put<void>(`/api/v1/elections/${election.electionId}/lifecycle`, {lifecycleStateId, expectedVersion: election.version}); }
  getCandidates(electionId: string) { return this.http.get<CandidateSummary[]>(`/api/v1/elections/${electionId}/candidates`); }
  addCandidate(electionId: string, body: {name: string; externalReference: string | null; positionId: number; areaId: number; nominationReference: string | null}) { return this.http.post<CandidateSummary>(`/api/v1/elections/${electionId}/candidates`, body); }
  addElectionCenter(electionId: string, body: {areaId: number; code: string; name: string; address: string | null}) { return this.http.post<ElectionCenterSummary>(`/api/v1/elections/${electionId}/centers`, body); }
  getUsers() { return this.http.get<UserSummary[]>('/api/v1/admin/users'); }
  createUser(body: {username:string;displayName:string;email:string|null;initialPassword:string}) { return this.http.post<UserSummary>('/api/v1/admin/users',body); }
  setUserActive(userId:string,isActive:boolean) { return this.http.put<void>(`/api/v1/admin/users/${userId}/active`,{isActive}); }
  getRoles() { return this.http.get<RoleSummary[]>('/api/v1/admin/roles'); }
  createRole(body:{code:string;name:string}) { return this.http.post<RoleSummary>('/api/v1/admin/roles',body); }
  assignRole(userId:string,roleId:string) { return this.http.post<void>(`/api/v1/admin/users/${userId}/roles/${roleId}`,{}); }
  getPermissions() { return this.http.get<PermissionSummary[]>('/api/v1/admin/permissions'); }
  assignPermission(roleId:string,permissionCode:string) { return this.http.post<void>(`/api/v1/admin/roles/${roleId}/permissions`,{permissionCode}); }
  getAdministrationDashboard() { return this.http.get<AdministrationDashboard>('/api/v1/admin/dashboard'); }
  getResultLookups(electionId:string) { return this.http.get<ResultLookups>(`/api/v1/elections/${electionId}/results/lookups`); }
  getResultSubmissions(electionId:string) { return this.http.get<ResultSubmissionSummary[]>(`/api/v1/elections/${electionId}/results`); }
  submitResult(electionId:string,body:object) { return this.http.post<ResultSubmissionSummary>(`/api/v1/elections/${electionId}/results`,body); }
  verifyResult(electionId:string,submission:ResultSubmissionSummary,resultingStateId:number,note:string) { return this.http.post<ResultSubmissionSummary>(`/api/v1/elections/${electionId}/results/${submission.submissionId}/verify`,{resultingStateId,expectedVersion:submission.version,note}); }
  getExports(electionId:string) { return this.http.get<ExportSummary[]>(`/api/v1/elections/${electionId}/results/exports`); }
  requestExport(electionId:string,reportType:string,format:string) { return this.http.post<ExportSummary>(`/api/v1/elections/${electionId}/results/exports`,{reportType,format}); }
  getInventoryLookups(id:string){return this.http.get<InventoryLookups>(`/api/v1/elections/${id}/inventory/lookups`)}
  getWarehouses(id:string){return this.http.get<WarehouseSummary[]>(`/api/v1/elections/${id}/inventory/warehouses`)}
  createWarehouse(id:string,body:{areaId:number;name:string}){return this.http.post<WarehouseSummary>(`/api/v1/elections/${id}/inventory/warehouses`,body)}
  getInventoryItems(id:string){return this.http.get<ItemSummary[]>(`/api/v1/elections/${id}/inventory/items`)}
  createInventoryItem(id:string,body:{sku:string;name:string;unit:string}){return this.http.post<ItemSummary>(`/api/v1/elections/${id}/inventory/items`,body)}
  getMovements(id:string){return this.http.get<MovementSummary[]>(`/api/v1/elections/${id}/inventory/movements`)}
  recordMovement(id:string,body:object){return this.http.post<MovementSummary>(`/api/v1/elections/${id}/inventory/movements`,body)}
  getAllocations(id:string){return this.http.get<AllocationSummary[]>(`/api/v1/elections/${id}/inventory/allocations`)}
  createAllocation(id:string,body:object){return this.http.post<AllocationSummary>(`/api/v1/elections/${id}/inventory/allocations`,body)}
  acknowledgeAllocation(id:string,allocationId:string){return this.http.put<AllocationSummary>(`/api/v1/elections/${id}/inventory/allocations/${allocationId}/acknowledge`,{})}
  getFinance(id:string){return this.http.get<FinanceWorkspace>(`/api/v1/elections/${id}/finance`)}
  createBudget(id:string,body:{name:string;currency:string}){return this.http.post<BudgetSummary>(`/api/v1/elections/${id}/finance/budgets`,body)}
  addBudgetLine(id:string,budgetId:string,body:{category:string;allocatedAmount:number}){return this.http.post<BudgetLineSummary>(`/api/v1/elections/${id}/finance/budgets/${budgetId}/lines`,body)}
  createVendor(id:string,body:{name:string;registrationNumber:string}){return this.http.post<VendorSummary>(`/api/v1/elections/${id}/finance/vendors`,body)}
  submitExpense(id:string,body:object){return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses`,body)}
  decideExpense(id:string,x:ExpenseSummary,stateId:number,note:string){return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses/${x.expenseId}/decision`,{stateId,expectedVersion:x.version,note})}
  recordPayment(id:string,expenseId:string,amount:number,reference:string){return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses/${expenseId}/payments`,{amount,reference})}
  getEvents(id:string){return this.http.get<EventWorkspace>(`/api/v1/elections/${id}/events`)}
  createVenue(id:string,body:object){return this.http.post<VenueSummary>(`/api/v1/elections/${id}/events/venues`,body)}
  createEvent(id:string,body:object){return this.http.post<CampaignEventSummary>(`/api/v1/elections/${id}/events`,body)}
  completeEvent(id:string,x:CampaignEventSummary,report:string){return this.http.put<CampaignEventSummary>(`/api/v1/elections/${id}/events/${x.eventId}/complete`,{expectedVersion:x.version,report})}
  createMeeting(id:string,body:object){return this.http.post<MeetingSummary>(`/api/v1/elections/${id}/events/meetings`,body)}
  addMeetingParticipant(id:string,meetingId:string,userId:string){return this.http.post<void>(`/api/v1/elections/${id}/events/meetings/${meetingId}/participants/${userId}`,{})}
  markMeetingAttendance(id:string,meetingId:string,userId:string){return this.http.put<void>(`/api/v1/elections/${id}/events/meetings/${meetingId}/participants/${userId}/attendance`,{})}
  getOperationsDashboard(){return this.http.get<OperationsDashboard>('/api/v1/dashboard')}
  getAudit(search=''){return this.http.get<AuditPage>('/api/v1/oversight/audit',{params:{search,page:1,pageSize:100}})}
  getNotifications(){return this.http.get<NotificationFeed>('/api/v1/oversight/notifications')}
  getLookups(id: string) { return this.http.get<WorkforceLookups>(`/api/v1/elections/${id}/workforce/lookups`); }
  getTeams(id: string) { return this.http.get<TeamSummary[]>(`/api/v1/elections/${id}/workforce/teams`); }
  createTeam(id: string, body: {areaId: number; name: string}) { return this.http.post<TeamSummary>(`/api/v1/elections/${id}/workforce/teams`, body); }
  getMembers(id: string, teamId: string) { return this.http.get<TeamMemberSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`); }
  addMember(id: string, teamId: string, body: {userId: string; responsibility: string}) { return this.http.post<TeamMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`, body); }
  assignTeamLeader(id:string,teamId:string,userId:string){return this.http.put<TeamSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/leader`,{userId})}
  getFieldMembers(id:string,teamId:string){return this.http.get<FieldMemberSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members`)}
  createFieldMember(id:string,teamId:string,body:object){return this.http.post<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members`,body)}
  updateFieldMember(id:string,teamId:string,memberId:string,body:object){return this.http.put<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members/${memberId}`,body)}
  deactivateFieldMember(id:string,teamId:string,memberId:string){return this.http.put<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members/${memberId}/deactivate`,{})}
  getFieldAttendance(id:string,teamId:string,date:string){return this.http.get<FieldAttendanceSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`,{params:{date}})}
  getFieldMemberAttendance(id:string,teamId:string,memberId:string){return this.http.get<FieldAttendanceSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`,{params:{memberId}})}
  recordFieldAttendance(id:string,teamId:string,body:object){return this.http.post<FieldAttendanceSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`,body)}
  getMemberWork(id:string,teamId:string){return this.http.get<MemberWorkSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work`)}
  assignMemberWork(id:string,teamId:string,body:object){return this.http.post<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work`,body)}
  moveMemberWork(id:string,teamId:string,work:MemberWorkSummary,stateId:number){return this.http.put<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work/${work.assignmentId}/state`,{stateId,expectedVersion:work.version})}
  verifyMemberWork(id:string,teamId:string,work:MemberWorkSummary,note:string){return this.http.put<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work/${work.assignmentId}/verify`,{expectedVersion:work.version,note:note||null})}
  getTasks(id: string) { return this.http.get<TeamTaskSummary[]>(`/api/v1/elections/${id}/workforce/tasks`); }
  createTask(id: string, body: object) { return this.http.post<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks`, body); }
  moveTask(id: string, task: TeamTaskSummary, stateId: number) { return this.http.put<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks/${task.taskId}/state`, {stateId, expectedVersion: task.version}); }
  getTrainings(id: string) { return this.http.get<TrainingSummary[]>(`/api/v1/elections/${id}/workforce/trainings`); }
  createTraining(id: string, body: object) { return this.http.post<TrainingSummary>(`/api/v1/elections/${id}/workforce/trainings`, body); }
  getAttendance(id: string, trainingId: string) { return this.http.get<AttendanceSummary[]>(`/api/v1/elections/${id}/workforce/trainings/${trainingId}/attendance`); }
  recordAttendance(id: string, trainingId: string, userId: string) { return this.http.post<AttendanceSummary>(`/api/v1/elections/${id}/workforce/trainings/${trainingId}/attendance`, {userId, recordedAtUtc: null}); }
  getAgents(id: string) { return this.http.get<AgentAssignmentSummary[]>(`/api/v1/elections/${id}/workforce/agents`); }
  assignAgent(id: string, body: {electionCenterId: string; userId: string; startsAtUtc: string; endsAtUtc: string}) { return this.http.post<AgentAssignmentSummary>(`/api/v1/elections/${id}/workforce/agents`, body); }
  getPollingCenters(id: string, search = '', verified = '') { const params: {[key: string]: string | number} = {page: 1, pageSize: 50}; if (search) params['search'] = search; if (verified) params['verified'] = verified; return this.http.get<PagedResult<CenterDirectoryItem>>(`/api/v1/elections/${id}/polling-centers`, {params}); }
  getPollingCenter(id: string, centerId: string) { return this.http.get<CenterDetail>(`/api/v1/elections/${id}/polling-centers/${centerId}`); }
  getPollingLookups(id: string) { return this.http.get<PollingLookups>(`/api/v1/elections/${id}/polling-centers/lookups`); }
  addBooth(id: string, centerId: string, body: {code: string; name: string}) { return this.http.post<BoothSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/booths`, body); }
  verifyCenter(id: string, centerId: string) { return this.http.post<VerificationSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/verify`, {}); }
  deactivateAgent(id: string, centerId: string, assignmentId: string) { return this.http.put<void>(`/api/v1/elections/${id}/polling-centers/${centerId}/agents/${assignmentId}/deactivate`, {}); }
  createChecklist(id: string, centerId: string, body: {name: string; requirements: string[]}) { return this.http.post<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists`, body); }
  completeChecklistItem(id: string, centerId: string, checklist: ChecklistSummary, itemId: string) { return this.http.put<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists/${checklist.checklistId}/items/${itemId}/complete`, {expectedVersion: checklist.version}); }
}
