import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  AgentAssignmentSummary, AttendanceSummary, BoothSummary, CandidateSummary, CandidateWarRoomHero, CandidateWarRoomSummary, CenterDetail, CenterDirectoryItem, ChecklistSummary, ElectionSymbolSummary, FieldMemberSummary, FieldAttendanceSummary, MemberWorkSummary,
  ElectionCenterSummary, ElectionLookups, ElectionSummary, PagedResult, PollingLookups, TeamLeaderDashboardSummary, TeamMemberSummary, TeamSummary,
  AdministrationDashboard, AllocationSummary, AuditPage, BudgetLineSummary, BudgetSummary, CampaignEventSummary, EventWorkspace, ExpenseSummary, ExportSummary, FinanceWorkspace, InventoryLookups, ItemSummary, MasterArea, MasterAreaType, MasterDataWorkspace, MasterElectionType, MasterEventType, MasterLifecycleState, MasterMovementType, MasterPosition, MasterTaskPriority, MasterTaskState, MeetingSummary, MovementSummary, NotificationFeed, OperationsDashboard, PermissionSummary, ResultLookups, ResultSubmissionSummary, RoleSummary, TeamTaskSummary, TrainingSummary, UserSummary, VendorSummary, VenueSummary, VerificationSummary, WarehouseSummary, WorkforceLookups,
  CandidateBoothAgentSummary, CreateBoothAgentRequest, UpdateBoothAgentRequest, CandidateElectionResultsSummary, QuickResultSubmissionRequest, CreateOpponentCandidateRequest, EcExpenseScheduleReport, CandidateExpenseVoucherItem, CreateExpenseVoucherRequest,
  UploadAndVerifyForm8Request, Form8DetailResponse,
  BatchMarkSlipsRequest, CandidateIncidentSummary, CandidateVoterSummary, CreateIncidentRequest, CreateVoterRequest, UpdateIncidentStatusRequest, UpdateVoterRequest,
  VoterBulkImportResult, VoterBulkPreviewResult, VoterBulkRowDto,
  CandidateBroadcastLogItem, SendCandidateBroadcastRequest, SendCandidateBroadcastResponse,
  CandidateCampaignVenueItem, CandidateCampaignEventItem, CreateCampaignEventRequest, UpdateCampaignEventPermitRequest,
  SmsGatewayConfigDto, UpdateSmsGatewayConfigRequest, TestSmsRequest, SendVoterBroadcastRequest, SendVoterBroadcastResponse
} from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class EemsApiService {
  private readonly http = inject(HttpClient);
  getElectionSymbols() { return this.http.get<ElectionSymbolSummary[]>('/api/v1/candidate/symbols'); }
  getCandidateWarRoom(electionId: string, candidateId?: string | null) {
    const params: { [key: string]: string } = {};
    if (candidateId) params['candidateId'] = candidateId;
    return this.http.get<CandidateWarRoomSummary>(`/api/v1/candidate/elections/${electionId}/war-room`, { params });
  }
  getCandidatesForElection(electionId: string) {
    return this.http.get<CandidateWarRoomHero[]>(`/api/v1/candidate/elections/${electionId}/candidates`);
  }
  getAllCandidates() {
    return this.http.get<CandidateWarRoomHero[]>('/api/v1/candidate/candidates');
  }
  updateCandidateCampaign(electionId: string, candidateId: string, body: { symbolId?: number | null; partyName?: string | null; slogan?: string | null; phone?: string | null; campaignOffice?: string | null }) {
    return this.http.put<void>(`/api/v1/candidate/elections/${electionId}/candidates/${candidateId}/campaign`, body);
  }
  getBoothAgents(electionId: string, centerId?: string, status?: string, agentType?: string, candidateId?: string | null) {
    const params: { [key: string]: string } = {};
    if (centerId) params['centerId'] = centerId;
    if (status) params['status'] = status;
    if (agentType) params['agentType'] = agentType;
    if (candidateId) params['candidateId'] = candidateId;
    return this.http.get<CandidateBoothAgentSummary[]>(`/api/v1/candidate/elections/${electionId}/booth-agents`, { params });
  }
  createBoothAgent(electionId: string, body: CreateBoothAgentRequest) {
    return this.http.post<CandidateBoothAgentSummary>(`/api/v1/candidate/elections/${electionId}/booth-agents`, body);
  }
  updateBoothAgent(electionId: string, agentId: string, body: UpdateBoothAgentRequest) {
    return this.http.put<void>(`/api/v1/candidate/elections/${electionId}/booth-agents/${agentId}`, body);
  }
  issueAgentLetter(electionId: string, agentId: string) {
    return this.http.post<void>(`/api/v1/candidate/elections/${electionId}/booth-agents/${agentId}/issue-letter`, {});
  }
  deleteBoothAgent(electionId: string, agentId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/booth-agents/${agentId}`);
  }
  getCandidateResultsSummary(electionId: string, candidateId?: string | null) {
    const params: { [key: string]: string } = {};
    if (candidateId) params['candidateId'] = candidateId;
    return this.http.get<CandidateElectionResultsSummary>(`/api/v1/candidate/elections/${electionId}/results-summary`, { params });
  }
  submitQuickResult(electionId: string, body: QuickResultSubmissionRequest) {
    return this.http.post<{ success: boolean; submissionId: string; declaredVotes: number }>(`/api/v1/candidate/elections/${electionId}/quick-result`, body);
  }
  createOpponentCandidate(electionId: string, body: CreateOpponentCandidateRequest) {
    return this.http.post<CandidateWarRoomHero>(`/api/v1/candidate/elections/${electionId}/opponents`, body);
  }
  removeOpponentCandidate(electionId: string, candidateId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/opponents/${candidateId}`);
  }
  getEcExpenseSchedule(electionId: string) {
    return this.http.get<EcExpenseScheduleReport>(`/api/v1/candidate/elections/${electionId}/expenses/ec-schedule`);
  }
  createExpenseVoucher(electionId: string, body: CreateExpenseVoucherRequest) {
    return this.http.post<CandidateExpenseVoucherItem>(`/api/v1/candidate/elections/${electionId}/expenses`, body);
  }
  deleteExpenseVoucher(electionId: string, expenseId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/expenses/${expenseId}`);
  }
  downloadEcExpenseCsvUrl(electionId: string): string {
    return `/api/v1/candidate/elections/${electionId}/expenses/ec-schedule/csv`;
  }
  uploadForm8(electionId: string, centerId: string, body: UploadAndVerifyForm8Request) {
    return this.http.post<Form8DetailResponse>(`/api/v1/candidate/elections/${electionId}/centers/${centerId}/form8`, body);
  }
  getForm8FileUrl(electionId: string, centerId: string): string {
    return `/api/v1/candidate/elections/${electionId}/centers/${centerId}/form8/file`;
  }
  getCandidateVoters(electionId: string, centerId?: string, category?: string, slipIssued?: boolean, search?: string, candidateId?: string | null) {
    const params: { [key: string]: string } = {};
    if (centerId) params['centerId'] = centerId;
    if (category) params['category'] = category;
    if (slipIssued !== undefined) params['slipIssued'] = String(slipIssued);
    if (search) params['search'] = search;
    if (candidateId) params['candidateId'] = candidateId;
    return this.http.get<CandidateVoterSummary[]>(`/api/v1/candidate/elections/${electionId}/voters`, { params });
  }
  createCandidateVoter(electionId: string, body: CreateVoterRequest) {
    return this.http.post<CandidateVoterSummary>(`/api/v1/candidate/elections/${electionId}/voters`, body);
  }
  updateCandidateVoter(electionId: string, voterId: string, body: UpdateVoterRequest) {
    return this.http.put<void>(`/api/v1/candidate/elections/${electionId}/voters/${voterId}`, body);
  }
  toggleVoterSlip(electionId: string, voterId: string) {
    return this.http.post<{ slipIssued: boolean }>(`/api/v1/candidate/elections/${electionId}/voters/${voterId}/toggle-slip`, {});
  }
  toggleVoterVoted(electionId: string, voterId: string) {
    return this.http.post<{ hasVoted: boolean }>(`/api/v1/candidate/elections/${electionId}/voters/${voterId}/toggle-voted`, {});
  }
  batchMarkVoterSlips(electionId: string, body: BatchMarkSlipsRequest) {
    return this.http.post<{ updatedCount: number; slipIssued: boolean }>(`/api/v1/candidate/elections/${electionId}/voters/batch-mark-slips`, body);
  }
  deleteCandidateVoter(electionId: string, voterId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/voters/${voterId}`);
  }
  previewVoterBulk(electionId: string, centerId: string, boothId: string | null | undefined, file: File) {
    const formData = new FormData();
    formData.append('centerId', centerId);
    if (boothId) formData.append('boothId', boothId);
    formData.append('file', file, file.name);
    return this.http.post<VoterBulkPreviewResult>(`/api/v1/candidate/elections/${electionId}/voters/bulk-preview`, formData);
  }
  confirmVoterBulkImport(electionId: string, body: { centerId: string; boothId?: string | null; candidateId?: string | null; rows: VoterBulkRowDto[] }) {
    return this.http.post<VoterBulkImportResult>(`/api/v1/candidate/elections/${electionId}/voters/bulk-import`, body);
  }
  downloadVoterSampleTemplateUrl(): string {
    return '/api/v1/candidate/voters/sample-template';
  }
  getCandidateIncidents(electionId: string, centerId?: string, candidateId?: string | null, severity?: string, status?: string) {
    const params: { [key: string]: string } = {};
    if (centerId) params['centerId'] = centerId;
    if (candidateId) params['candidateId'] = candidateId;
    if (severity) params['severity'] = severity;
    if (status) params['status'] = status;
    return this.http.get<CandidateIncidentSummary[]>(`/api/v1/candidate/elections/${electionId}/incidents`, { params });
  }
  createCandidateIncident(electionId: string, body: CreateIncidentRequest) {
    return this.http.post<CandidateIncidentSummary>(`/api/v1/candidate/elections/${electionId}/incidents`, body);
  }
  updateCandidateIncidentStatus(electionId: string, incidentId: string, body: UpdateIncidentStatusRequest) {
    return this.http.put<void>(`/api/v1/candidate/elections/${electionId}/incidents/${incidentId}/status`, body);
  }
  deleteCandidateIncident(electionId: string, incidentId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/incidents/${incidentId}`);
  }
  getBroadcastLogs(electionId: string) {
    return this.http.get<CandidateBroadcastLogItem[]>(`/api/v1/candidate/elections/${electionId}/broadcasts`);
  }
  sendBroadcast(electionId: string, body: SendCandidateBroadcastRequest) {
    return this.http.post<SendCandidateBroadcastResponse>(`/api/v1/candidate/elections/${electionId}/broadcasts`, body);
  }
  getCampaignEvents(electionId: string) {
    return this.http.get<CandidateCampaignEventItem[]>(`/api/v1/candidate/elections/${electionId}/campaign-events`);
  }
  getCampaignVenues(electionId: string) {
    return this.http.get<CandidateCampaignVenueItem[]>(`/api/v1/candidate/elections/${electionId}/campaign-venues`);
  }
  createCampaignEvent(electionId: string, body: CreateCampaignEventRequest) {
    return this.http.post<CandidateCampaignEventItem>(`/api/v1/candidate/elections/${electionId}/campaign-events`, body);
  }
  updateCampaignEventPermit(electionId: string, eventId: string, body: UpdateCampaignEventPermitRequest) {
    return this.http.patch<void>(`/api/v1/candidate/elections/${electionId}/campaign-events/${eventId}/permit`, body);
  }
  deleteCampaignEvent(electionId: string, eventId: string) {
    return this.http.delete<void>(`/api/v1/candidate/elections/${electionId}/campaign-events/${eventId}`);
  }
  getSmsGatewayConfig(electionId: string) {
    return this.http.get<SmsGatewayConfigDto>(`/api/v1/candidate/elections/${electionId}/sms-config`);
  }
  updateSmsGatewayConfig(electionId: string, body: UpdateSmsGatewayConfigRequest) {
    return this.http.post<SmsGatewayConfigDto>(`/api/v1/candidate/elections/${electionId}/sms-config`, body);
  }
  testSmsGateway(electionId: string, body: TestSmsRequest) {
    return this.http.post<{ success: boolean; provider: string; phone: string; message: string }>(`/api/v1/candidate/elections/${electionId}/sms-test`, body);
  }
  getWhatsAppBotStatus() {
    return this.http.get<{ connected: boolean; phone: string | null; isConnecting: boolean; hasQR: boolean; queueStats: any; queueRemaining: number }>('/api/v1/candidate/whatsapp/status');
  }
  getWhatsAppBotQr() {
    return this.http.get<{ connected: boolean; phone: string | null; qrDataUrl: string | null }>('/api/v1/candidate/whatsapp/qr');
  }
  sendWhatsAppAutoBroadcast(body: { items: { id?: string; name?: string; phone: string; message: string }[] }) {
    return this.http.post<{ success: boolean; message: string; queueStats: any }>('/api/v1/candidate/whatsapp/auto-broadcast', body);
  }
  logoutWhatsAppBot() {
    return this.http.post<{ success: boolean; message: string }>('/api/v1/candidate/whatsapp/logout', {});
  }
  getCandidateTeamUsers(candidateId?: string) {
    const params = candidateId ? `?candidateId=${candidateId}` : '';
    return this.http.get<{ userId: string; username: string; displayName: string; email: string | null; phone: string | null; role: string; isActive: boolean; createdAtUtc: string }[]>(`/api/v1/candidate/team-users${params}`);
  }
  createCandidateTeamUser(body: { username: string; displayName: string; email?: string | null; phone?: string | null; password: string; role?: string | null; candidateId?: string | null }) {
    return this.http.post<{ userId: string; username: string; displayName: string; email: string | null; phone: string | null; role: string; isActive: boolean; createdAtUtc: string }>('/api/v1/candidate/team-users', body);
  }
  toggleCandidateTeamUserStatus(userId: string, isActive: boolean) {
    return this.http.put<void>(`/api/v1/candidate/team-users/${userId}/status`, { isActive });
  }
  resetCandidateTeamUserPassword(userId: string, newPassword: string) {
    return this.http.post<void>(`/api/v1/candidate/team-users/${userId}/reset-password`, { newPassword });
  }
  getMasterCandidateOverview(electionId?: string) {
    const params = electionId ? `?electionId=${electionId}` : '';
    return this.http.get<{
      candidateId: string;
      electionId: string;
      electionName: string;
      candidateName: string;
      symbolName: string;
      symbolEmoji: string;
      partyName: string;
      slogan: string;
      phone: string | null;
      campaignOffice: string | null;
      primaryUsername: string | null;
      primaryDisplayName: string | null;
      teamCount: number;
      agentCount: number;
      voterCount: number;
      slipsIssuedCount: number;
      slipPercentage: number;
      totalVotes: number;
    }[]>(`/api/v1/candidate/master-overview${params}`);
  }
  sendVoterBroadcast(electionId: string, body: SendVoterBroadcastRequest) {
    return this.http.post<SendVoterBroadcastResponse>(`/api/v1/candidate/elections/${electionId}/voter-broadcasts`, body);
  }
  getElectionLookups() { return this.http.get<ElectionLookups>('/api/v1/elections/lookups'); }
  getElections() { return this.http.get<ElectionSummary[]>('/api/v1/elections'); }
  createElection(body: { electionTypeId: number; areaId: number; lifecycleStateId: number; name: string; electionDate: string }) { return this.http.post<ElectionSummary>('/api/v1/elections', body); }
  updateElection(election: ElectionSummary, body: { electionTypeId: number; areaId: number; name: string; electionDate: string }) { return this.http.put<ElectionSummary>(`/api/v1/elections/${election.electionId}`, { ...body, expectedVersion: election.version }); }
  moveElection(election: ElectionSummary, lifecycleStateId: number) { return this.http.put<void>(`/api/v1/elections/${election.electionId}/lifecycle`, { lifecycleStateId, expectedVersion: election.version }); }
  getCandidates(electionId: string) { return this.http.get<CandidateSummary[]>(`/api/v1/elections/${electionId}/candidates`); }
  addCandidate(electionId: string, body: { name: string; externalReference: string | null; positionId: number; areaId: number; nominationReference: string | null; symbolId?: number | null; partyName?: string | null; slogan?: string | null }) { return this.http.post<CandidateSummary>(`/api/v1/elections/${electionId}/candidates`, body); }
  addElectionCenter(electionId: string, body: { areaId: number; code: string; name: string; address: string | null }) { return this.http.post<ElectionCenterSummary>(`/api/v1/elections/${electionId}/centers`, body); }
  getUsers() { return this.http.get<UserSummary[]>('/api/v1/admin/users'); }
  createUser(body: { username: string; displayName: string; email: string | null; initialPassword: string; candidateId?: string | null }) { return this.http.post<UserSummary>('/api/v1/admin/users', body); }
  setUserActive(userId: string, isActive: boolean) { return this.http.put<void>(`/api/v1/admin/users/${userId}/active`, { isActive }); }
  assignUserCandidate(userId: string, candidateId: string | null) { return this.http.put<void>(`/api/v1/admin/users/${userId}/candidate`, { candidateId }); }
  getRoles() { return this.http.get<RoleSummary[]>('/api/v1/admin/roles'); }
  createRole(body: { code: string; name: string }) { return this.http.post<RoleSummary>('/api/v1/admin/roles', body); }
  assignRole(userId: string, roleId: string) { return this.http.post<void>(`/api/v1/admin/users/${userId}/roles/${roleId}`, {}); }
  getPermissions() { return this.http.get<PermissionSummary[]>('/api/v1/admin/permissions'); }
  assignPermission(roleId: string, permissionCode: string) { return this.http.post<void>(`/api/v1/admin/roles/${roleId}/permissions`, { permissionCode }); }
  getAdministrationDashboard() { return this.http.get<AdministrationDashboard>('/api/v1/admin/dashboard'); }
  getMasterData() { return this.http.get<MasterDataWorkspace>('/api/v1/master-data') }
  addMasterArea(body: object) { return this.http.post<MasterArea>('/api/v1/master-data/areas', body) }
  addMasterAreaType(body: object) { return this.http.post<MasterAreaType>('/api/v1/master-data/area-types', body) }
  addMasterElectionType(body: object) { return this.http.post<MasterElectionType>('/api/v1/master-data/election-types', body) }
  addMasterLifecycleState(body: object) { return this.http.post<MasterLifecycleState>('/api/v1/master-data/lifecycle-states', body) }
  addMasterPosition(body: object) { return this.http.post<MasterPosition>('/api/v1/master-data/positions', body) }
  addMasterTaskState(body: object) { return this.http.post<MasterTaskState>('/api/v1/master-data/task-states', body) }
  addMasterTaskPriority(body: object) { return this.http.post<MasterTaskPriority>('/api/v1/master-data/task-priorities', body) }
  addMasterEventType(body: object) { return this.http.post<MasterEventType>('/api/v1/master-data/event-types', body) }
  addMasterMovementType(body: object) { return this.http.post<MasterMovementType>('/api/v1/master-data/movement-types', body) }
  getResultLookups(electionId: string) { return this.http.get<ResultLookups>(`/api/v1/elections/${electionId}/results/lookups`); }
  getResultSubmissions(electionId: string) { return this.http.get<ResultSubmissionSummary[]>(`/api/v1/elections/${electionId}/results`); }
  submitResult(electionId: string, body: object) { return this.http.post<ResultSubmissionSummary>(`/api/v1/elections/${electionId}/results`, body); }
  verifyResult(electionId: string, submission: ResultSubmissionSummary, resultingStateId: number, note: string) { return this.http.post<ResultSubmissionSummary>(`/api/v1/elections/${electionId}/results/${submission.submissionId}/verify`, { resultingStateId, expectedVersion: submission.version, note }); }
  getExports(electionId: string) { return this.http.get<ExportSummary[]>(`/api/v1/elections/${electionId}/results/exports`); }
  requestExport(electionId: string, reportType: string, format: string) { return this.http.post<ExportSummary>(`/api/v1/elections/${electionId}/results/exports`, { reportType, format }); }
  getInventoryLookups(id: string) { return this.http.get<InventoryLookups>(`/api/v1/elections/${id}/inventory/lookups`) }
  getWarehouses(id: string) { return this.http.get<WarehouseSummary[]>(`/api/v1/elections/${id}/inventory/warehouses`) }
  createWarehouse(id: string, body: { areaId: number; name: string }) { return this.http.post<WarehouseSummary>(`/api/v1/elections/${id}/inventory/warehouses`, body) }
  getInventoryItems(id: string) { return this.http.get<ItemSummary[]>(`/api/v1/elections/${id}/inventory/items`) }
  createInventoryItem(id: string, body: { sku: string; name: string; unit: string }) { return this.http.post<ItemSummary>(`/api/v1/elections/${id}/inventory/items`, body) }
  getMovements(id: string) { return this.http.get<MovementSummary[]>(`/api/v1/elections/${id}/inventory/movements`) }
  recordMovement(id: string, body: object) { return this.http.post<MovementSummary>(`/api/v1/elections/${id}/inventory/movements`, body) }
  getAllocations(id: string) { return this.http.get<AllocationSummary[]>(`/api/v1/elections/${id}/inventory/allocations`) }
  createAllocation(id: string, body: object) { return this.http.post<AllocationSummary>(`/api/v1/elections/${id}/inventory/allocations`, body) }
  acknowledgeAllocation(id: string, allocationId: string) { return this.http.put<AllocationSummary>(`/api/v1/elections/${id}/inventory/allocations/${allocationId}/acknowledge`, {}) }
  getFinance(id: string) { return this.http.get<FinanceWorkspace>(`/api/v1/elections/${id}/finance`) }
  createBudget(id: string, body: { name: string; currency: string }) { return this.http.post<BudgetSummary>(`/api/v1/elections/${id}/finance/budgets`, body) }
  addBudgetLine(id: string, budgetId: string, body: { category: string; allocatedAmount: number }) { return this.http.post<BudgetLineSummary>(`/api/v1/elections/${id}/finance/budgets/${budgetId}/lines`, body) }
  createVendor(id: string, body: { name: string; registrationNumber: string }) { return this.http.post<VendorSummary>(`/api/v1/elections/${id}/finance/vendors`, body) }
  submitExpense(id: string, body: object) { return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses`, body) }
  decideExpense(id: string, x: ExpenseSummary, stateId: number, note: string) { return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses/${x.expenseId}/decision`, { stateId, expectedVersion: x.version, note }) }
  recordPayment(id: string, expenseId: string, amount: number, reference: string) { return this.http.post<ExpenseSummary>(`/api/v1/elections/${id}/finance/expenses/${expenseId}/payments`, { amount, reference }) }
  getEvents(id: string) { return this.http.get<EventWorkspace>(`/api/v1/elections/${id}/events`) }
  createVenue(id: string, body: object) { return this.http.post<VenueSummary>(`/api/v1/elections/${id}/events/venues`, body) }
  createEvent(id: string, body: object) { return this.http.post<CampaignEventSummary>(`/api/v1/elections/${id}/events`, body) }
  completeEvent(id: string, x: CampaignEventSummary, report: string) { return this.http.put<CampaignEventSummary>(`/api/v1/elections/${id}/events/${x.eventId}/complete`, { expectedVersion: x.version, report }) }
  createMeeting(id: string, body: object) { return this.http.post<MeetingSummary>(`/api/v1/elections/${id}/events/meetings`, body) }
  addMeetingParticipant(id: string, meetingId: string, userId: string) { return this.http.post<void>(`/api/v1/elections/${id}/events/meetings/${meetingId}/participants/${userId}`, {}) }
  markMeetingAttendance(id: string, meetingId: string, userId: string) { return this.http.put<void>(`/api/v1/elections/${id}/events/meetings/${meetingId}/participants/${userId}/attendance`, {}) }
  getOperationsDashboard() { return this.http.get<OperationsDashboard>('/api/v1/dashboard') }
  getAudit(search = '') { return this.http.get<AuditPage>('/api/v1/oversight/audit', { params: { search, page: 1, pageSize: 100 } }) }
  getNotifications() { return this.http.get<NotificationFeed>('/api/v1/oversight/notifications') }
  getLookups(id: string) { return this.http.get<WorkforceLookups>(`/api/v1/elections/${id}/workforce/lookups`); }
  getTeams(id: string) { return this.http.get<TeamSummary[]>(`/api/v1/elections/${id}/workforce/teams`); }
  getTeamLeaderDashboard(id: string) { return this.http.get<TeamLeaderDashboardSummary>(`/api/v1/elections/${id}/workforce/leader-dashboard`) }
  createTeam(id: string, body: { areaId: number; name: string }) { return this.http.post<TeamSummary>(`/api/v1/elections/${id}/workforce/teams`, body); }
  getMembers(id: string, teamId: string) { return this.http.get<TeamMemberSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`); }
  addMember(id: string, teamId: string, body: { userId: string; responsibility: string }) { return this.http.post<TeamMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`, body); }
  assignTeamLeader(id: string, teamId: string, userId: string) { return this.http.put<TeamSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/leader`, { userId }) }
  getFieldMembers(id: string, teamId: string) { return this.http.get<FieldMemberSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members`) }
  createFieldMember(id: string, teamId: string, body: object) { return this.http.post<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members`, body) }
  updateFieldMember(id: string, teamId: string, memberId: string, body: object) { return this.http.put<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members/${memberId}`, body) }
  deactivateFieldMember(id: string, teamId: string, memberId: string) { return this.http.put<FieldMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-members/${memberId}/deactivate`, {}) }
  getFieldAttendance(id: string, teamId: string, date: string) { return this.http.get<FieldAttendanceSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`, { params: { date } }) }
  getFieldMemberAttendance(id: string, teamId: string, memberId: string) { return this.http.get<FieldAttendanceSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`, { params: { memberId } }) }
  recordFieldAttendance(id: string, teamId: string, body: object) { return this.http.post<FieldAttendanceSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/field-attendance`, body) }
  getMemberWork(id: string, teamId: string) { return this.http.get<MemberWorkSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work`) }
  assignMemberWork(id: string, teamId: string, body: object) { return this.http.post<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work`, body) }
  moveMemberWork(id: string, teamId: string, work: MemberWorkSummary, stateId: number) { return this.http.put<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work/${work.assignmentId}/state`, { stateId, expectedVersion: work.version }) }
  verifyMemberWork(id: string, teamId: string, work: MemberWorkSummary, note: string) { return this.http.put<MemberWorkSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/member-work/${work.assignmentId}/verify`, { expectedVersion: work.version, note: note || null }) }
  getTasks(id: string) { return this.http.get<TeamTaskSummary[]>(`/api/v1/elections/${id}/workforce/tasks`); }
  createTask(id: string, body: object) { return this.http.post<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks`, body); }
  moveTask(id: string, task: TeamTaskSummary, stateId: number) { return this.http.put<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks/${task.taskId}/state`, { stateId, expectedVersion: task.version }); }
  getTrainings(id: string) { return this.http.get<TrainingSummary[]>(`/api/v1/elections/${id}/workforce/trainings`); }
  createTraining(id: string, body: object) { return this.http.post<TrainingSummary>(`/api/v1/elections/${id}/workforce/trainings`, body); }
  getAttendance(id: string, trainingId: string) { return this.http.get<AttendanceSummary[]>(`/api/v1/elections/${id}/workforce/trainings/${trainingId}/attendance`); }
  recordAttendance(id: string, trainingId: string, userId: string) { return this.http.post<AttendanceSummary>(`/api/v1/elections/${id}/workforce/trainings/${trainingId}/attendance`, { userId, recordedAtUtc: null }); }
  getAgents(id: string) { return this.http.get<AgentAssignmentSummary[]>(`/api/v1/elections/${id}/workforce/agents`); }
  assignAgent(id: string, body: { electionCenterId: string; userId: string; startsAtUtc: string; endsAtUtc: string }) { return this.http.post<AgentAssignmentSummary>(`/api/v1/elections/${id}/workforce/agents`, body); }
  getPollingCenters(id: string, search = '', verified = '') { const params: { [key: string]: string | number } = { page: 1, pageSize: 50 }; if (search) params['search'] = search; if (verified) params['verified'] = verified; return this.http.get<PagedResult<CenterDirectoryItem>>(`/api/v1/elections/${id}/polling-centers`, { params }); }
  getPollingCenter(id: string, centerId: string) { return this.http.get<CenterDetail>(`/api/v1/elections/${id}/polling-centers/${centerId}`); }
  getPollingLookups(id: string) { return this.http.get<PollingLookups>(`/api/v1/elections/${id}/polling-centers/lookups`); }
  addBooth(id: string, centerId: string, body: { code: string; name: string }) { return this.http.post<BoothSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/booths`, body); }
  verifyCenter(id: string, centerId: string) { return this.http.post<VerificationSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/verify`, {}); }
  deactivateAgent(id: string, centerId: string, assignmentId: string) { return this.http.put<void>(`/api/v1/elections/${id}/polling-centers/${centerId}/agents/${assignmentId}/deactivate`, {}); }
  createChecklist(id: string, centerId: string, body: { name: string; requirements: string[] }) { return this.http.post<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists`, body); }
  completeChecklistItem(id: string, centerId: string, checklist: ChecklistSummary, itemId: string) { return this.http.put<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists/${checklist.checklistId}/items/${itemId}/complete`, { expectedVersion: checklist.version }); }
  createCandidateCenter(electionId: string, body: { code: string; name: string; areaId?: number; address?: string | null; initialBoothCode?: string | null; initialBoothName?: string | null; candidateId?: string | null }) {
    return this.http.post<CenterDirectoryItem>(`/api/v1/candidate/elections/${electionId}/centers`, body);
  }
  createCandidateBooth(electionId: string, centerId: string, body: { code: string; name: string }) {
    return this.http.post<BoothSummary>(`/api/v1/candidate/elections/${electionId}/centers/${centerId}/booths`, body);
  }
  getCandidateCenterBooths(electionId: string, centerId: string) {
    return this.http.get<BoothSummary[]>(`/api/v1/candidate/elections/${electionId}/centers/${centerId}/booths`);
  }
}
