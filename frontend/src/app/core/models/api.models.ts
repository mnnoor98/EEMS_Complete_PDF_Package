export interface TokenResponse { accessToken: string; accessTokenExpiresAtUtc: string; refreshToken: string; refreshTokenExpiresAtUtc: string; passwordChangeRequired: boolean; candidateId?: string | null; candidateName?: string | null; isSuperAdmin?: boolean; candidateElectionId?: string | null }
export interface ElectionSummary { electionId: string; name: string; electionTypeId: number; areaId: number; lifecycleStateId: number; electionDate: string; version: number }
export interface ReferenceItem { id: number; code: string; name: string }
export interface LifecycleReference extends ReferenceItem { isTerminal: boolean }
export interface AreaReference { id: number; parentAreaId: number | null; areaTypeId: number; code: string; nameBn: string; nameEn: string | null }
export interface PositionReference extends ReferenceItem { electionTypeId: number }
export interface ElectionLookups { electionTypes: ReferenceItem[]; lifecycleStates: LifecycleReference[]; positions: PositionReference[]; areas: AreaReference[] }
export interface CandidateSummary { candidateId: string; assignmentId: string; name: string; externalReference: string | null; positionId: number; areaId: number; nominationReference: string | null; isActive: boolean; symbolId?: number | null; symbolNameBn?: string | null; symbolNameEn?: string | null; symbolEmoji?: string | null; partyName?: string | null; slogan?: string | null }
export interface ElectionSymbolSummary { id: number; code: string; nameBn: string; nameEn: string; category: string; iconEmoji: string }
export interface CandidateWarRoomHero { candidateId: string; assignmentId: string; name: string; positionName: string; symbolId: number | null; symbolNameBn: string | null; symbolNameEn: string | null; symbolEmoji: string; partyName: string; slogan: string; phone: string | null; campaignOffice: string | null; electionId?: string | null; electionName?: string | null; areaId?: number | null; areaName?: string | null }
export interface CandidateWarRoomSummary { electionId: string; electionName: string; electionDate: string; areaName: string; candidate: CandidateWarRoomHero | null; totalCenters: number; verifiedCenters: number; totalBooths: number; assignedAgents: number; totalTeams: number; totalFieldMembers: number; openTasks: number; totalEvents: number; ecCeiling: number; totalCommittedExpenses: number; remainingBudget: number }
export interface CandidateBoothAgentSummary { boothAgentId: string; centerId: string; centerName: string; centerCode: string; boothId: string; boothCode: string; boothName: string; candidateId: string; candidateName: string; agentType: string; fullName: string; nidNumber: string; phone: string; voterNumber: string | null; photoUrl: string | null; appointmentLetterIssued: boolean; checkedInAtBooth: string | null; status: string; notes: string | null; createdAtUtc: string }
export interface CreateBoothAgentRequest { centerId: string; boothId: string; candidateId: string; agentType: string; fullName: string; nidNumber: string; phone: string; voterNumber?: string; notes?: string }
export interface UpdateBoothAgentRequest { fullName: string; nidNumber: string; phone: string; voterNumber?: string; agentType: string; status: string; appointmentLetterIssued: boolean; notes?: string }
export interface CandidateVoteDetailItem { candidateId: string; candidateName: string; symbolEmoji?: string; symbolName?: string; votes: number }
export interface CandidateTallyItem { candidateId: string; name: string; partyName: string; symbolEmoji: string; symbolName: string; totalVotes: number; votePercentage: number; isPrimary: boolean }
export interface CandidateCenterResultItem {
  electionCenterId: string;
  centerId: string;
  centerCode: string;
  centerName: string;
  candidateVotes: number;
  runnerUpVotes: number;
  margin: number;
  isCounted: boolean;
  form8Verified: boolean;
  reportedAtUtc: string | null;
  candidateVotesList?: CandidateVoteDetailItem[];
  form8DocumentUrl?: string | null;
  presidingOfficerName?: string | null;
  presidingOfficerPhone?: string | null;
  totalCastVotes?: number | null;
  cancelledVotes?: number | null;
  verificationNote?: string | null;
  verifiedAtUtc?: string | null;
}
export interface UploadAndVerifyForm8Request {
  documentData: string;
  fileName?: string;
  presidingOfficerName?: string;
  presidingOfficerPhone?: string;
  cancelledVotes?: number;
  isVerified?: boolean;
  verificationNote?: string;
}
export interface Form8DetailResponse {
  electionCenterId: string;
  centerId: string;
  centerName: string;
  centerCode: string;
  isCounted: boolean;
  form8Verified: boolean;
  documentUrl?: string | null;
  presidingOfficerName?: string | null;
  presidingOfficerPhone?: string | null;
  totalCastVotes?: number | null;
  cancelledVotes?: number | null;
  verificationNote?: string | null;
  verifiedAtUtc?: string | null;
}
export interface CandidateElectionResultsSummary { candidateId: string; candidateName: string; candidateSymbol: string; candidateSymbolEmoji: string; runnerUpName: string; runnerUpSymbol: string; runnerUpSymbolEmoji: string; totalCenters: number; countedCenters: number; remainingCenters: number; candidateTotalVotes: number; runnerUpTotalVotes: number; leadMargin: number; isLeading: boolean; centerResults: CandidateCenterResultItem[]; allCandidateTallies?: CandidateTallyItem[] }
export interface CandidateVoteEntry { candidateId: string; votes: number }
export interface QuickResultSubmissionRequest { electionCenterId: string; candidateVotes?: number; runnerUpVotes?: number; notes?: string; runnerUpCandidateId?: string | null; candidateId?: string | null; candidateVotesList?: CandidateVoteEntry[] }
export interface CreateOpponentCandidateRequest { name: string; partyName: string; symbolId?: number | null; slogan?: string | null; phone?: string | null }
export interface CandidateExpenseVoucherItem {
  id: string;
  invoiceNumber: string;
  category: string;
  categoryBn: string;
  vendorName: string;
  amount: number;
  expenseDate: string;
  paymentMethod: string;
  description?: string | null;
  receiptUrl?: string | null;
  status: string;
  createdAtUtc: string;
}

export interface CreateExpenseVoucherRequest {
  category: string;
  invoiceNumber: string;
  amount: number;
  expenseDate: string;
  vendorName: string;
  description?: string | null;
  paymentMethod?: string | null;
}

export interface EcCategoryScheduleItem { nameBn: string; nameEn: string; allocatedAmount: number; spentAmount: number; remainingAmount: number; voucherCount: number }
export interface EcExpenseScheduleReport {
  ecCeiling: number;
  totalCommitted: number;
  remainingBudget: number;
  utilizationPercentage: number;
  isWithinCeiling: boolean;
  categories: EcCategoryScheduleItem[];
  vouchers: CandidateExpenseVoucherItem[];
}
export interface CandidateVoterSummary { id: string; centerId: string; centerName: string; centerCode: string; boothId: string | null; boothCode: string | null; boothName: string | null; voterNumber: string; serialNumber: number; fullName: string; fatherOrSpouseName: string | null; gender: string; age: number | null; areaName: string | null; category: string; slipIssued: boolean; hasVoted: boolean; phone: string | null; notes: string | null; createdAtUtc: string; candidateId?: string | null }
export interface CreateVoterRequest { centerId: string; boothId: string | null; voterNumber: string; serialNumber: number; fullName: string; fatherOrSpouseName?: string | null; gender?: string | null; age?: number | null; areaName?: string | null; category?: string | null; phone?: string | null; notes?: string | null; candidateId?: string | null }
export interface UpdateVoterRequest { centerId: string; boothId: string | null; voterNumber: string; serialNumber: number; fullName: string; fatherOrSpouseName?: string | null; gender?: string | null; age?: number | null; areaName?: string | null; category?: string | null; phone?: string | null; notes?: string | null; slipIssued: boolean; hasVoted: boolean }
export interface BatchMarkSlipsRequest { voterIds: string[]; slipIssued: boolean }
export interface CandidateIncidentSummary { id: string; centerId: string; centerName: string; centerCode: string; boothId: string | null; boothCode: string | null; boothName: string | null; incidentType: string; severity: string; title: string; description: string; reportedBy: string; reportedByPhone: string | null; reportedAt: string; status: string; evidenceAttachmentUrl: string | null; magistrateName: string | null; actionTaken: string | null; officialComplaintGenerated: boolean; createdAtUtc: string; candidateId?: string | null }
export interface CreateIncidentRequest { centerId: string; boothId: string | null; incidentType: string; severity: string; title: string; description: string; reportedBy: string; reportedByPhone?: string | null; evidenceAttachmentUrl?: string | null; candidateId?: string | null }
export interface UpdateIncidentStatusRequest { status: string; actionTaken?: string | null; magistrateName?: string | null; officialComplaintGenerated?: boolean | null }
export interface TeamSummary { teamId: string; areaId: number; leaderUserId: string | null; name: string; isActive: boolean; createdAtUtc: string }
export interface TeamLeaderAlert { teamId: string; teamName: string; leaderUserId: string | null; activeMembers: number; attendancePending: number; openWork: number; overdueWork: number; verificationPending: number }
export interface TeamLeaderDashboardSummary { attendanceDate: string; activeMembers: number; attendancePending: number; openWork: number; overdueWork: number; verificationPending: number; teams: TeamLeaderAlert[] }
export interface TeamMemberSummary { userId: string; displayName: string; username: string; responsibility: string; joinedAtUtc: string; isActive: boolean }
export interface FieldMemberSummary { memberId: string; teamId: string; fullName: string; phone: string; memberType: string; areaId: number | null; address: string | null; emergencyContact: string | null; joinedAtUtc: string; isActive: boolean }
export interface FieldAttendanceSummary { attendanceId: string; memberId: string; attendanceDate: string; status: string; note: string | null; recordedByUserId: string; recordedAtUtc: string }
export interface MemberWorkSummary { assignmentId: string; memberId: string; stateId: number; priorityId: number; title: string; instructions: string | null; dueAtUtc: string | null; createdAtUtc: string; verifiedByUserId: string | null; verifiedAtUtc: string | null; verificationNote: string | null; version: number }
export interface TaskStateSummary { id: number; code: string; name: string; isTerminal: boolean } export interface TaskPrioritySummary { id: number; code: string; name: string; rank: number }
export interface WorkforceAreaSummary { id: number; code: string; nameBn: string; nameEn: string | null } export interface WorkforceUserSummary { userId: string; displayName: string; username: string } export interface WorkforceCenterSummary { electionCenterId: string; code: string; name: string }
export interface WorkforceLookups { taskStates: TaskStateSummary[]; taskPriorities: TaskPrioritySummary[]; areas: WorkforceAreaSummary[]; users: WorkforceUserSummary[]; centers: WorkforceCenterSummary[] }
export interface TeamTaskSummary { taskId: string; teamId: string | null; assigneeUserId: string | null; stateId: number; priorityId: number; title: string; dueAtUtc: string | null; createdAtUtc: string; version: number }
export interface TrainingSummary { trainingId: string; title: string; startsAtUtc: string; endsAtUtc: string }
export interface AttendanceSummary { userId: string; displayName: string; username: string; recordedAtUtc: string }
export interface AgentAssignmentSummary { assignmentId: string; electionCenterId: string; userId: string; displayName: string; username: string; startsAtUtc: string; endsAtUtc: string; isActive: boolean }
export interface UserSummary { userId: string; username: string; displayName: string; email: string | null; isActive: boolean; roleCodes: string[]; candidateId?: string | null; candidateName?: string | null }
export interface CreateUserRequest { username: string; displayName: string; email: string | null; initialPassword: string; candidateId?: string | null }
export interface AssignCandidateRequest { candidateId: string | null }
export interface RoleSummary { roleId: string; code: string; name: string; isActive: boolean; permissions: string[] }
export interface PermissionSummary { code: string; name: string; module: string }
export interface MasterAreaType { id: number; code: string; name: string; level: number } export interface MasterArea { id: number; parentAreaId: number | null; areaTypeId: number; code: string; nameBn: string; nameEn: string | null; isActive: boolean } export interface MasterElectionType { id: number; code: string; name: string; isActive: boolean } export interface MasterLifecycleState { id: number; code: string; name: string; isTerminal: boolean; isActive: boolean } export interface MasterPosition { id: number; electionTypeId: number; code: string; name: string; isActive: boolean } export interface MasterTaskState { id: number; code: string; name: string; isTerminal: boolean; isActive: boolean } export interface MasterTaskPriority { id: number; code: string; name: string; rank: number; isActive: boolean } export interface MasterEventType { id: number; code: string; name: string; isActive: boolean } export interface MasterMovementType { id: number; code: string; name: string; requiresSource: boolean; requiresDestination: boolean; isActive: boolean } export interface MasterDataWorkspace { areaTypes: MasterAreaType[]; areas: MasterArea[]; electionTypes: MasterElectionType[]; lifecycleStates?: MasterLifecycleState[]; positions: MasterPosition[]; taskStates: MasterTaskState[]; taskPriorities: MasterTaskPriority[]; eventTypes?: MasterEventType[]; movementTypes?: MasterMovementType[] }
export interface SecurityEventSummary { securityEventId: string; userId: string | null; eventType: string; source: string; detail: string; correlationId: string; occurredAtUtc: string }
export interface AdministrationDashboard { totalUsers: number; activeUsers: number; activeRoles: number; recentSecurityEvents: SecurityEventSummary[] }
export interface ResultStateReference { id: number; code: string; name: string; isVerified: boolean } export interface ResultPositionReference { id: number; code: string; name: string } export interface ResultCenterReference { electionCenterId: string; code: string; name: string } export interface ResultCandidateReference { candidateElectionId: string; positionId: number; name: string } export interface ExportStateReference { id: number; code: string; name: string; isTerminal: boolean }
export interface ResultLookups { states: ResultStateReference[]; positions: ResultPositionReference[]; centers: ResultCenterReference[]; candidates: ResultCandidateReference[]; exportStates: ExportStateReference[] }
export interface ResultDetailSummary { candidateElectionId: string; votes: number } export interface ResultVerificationSummary { verifierUserId: string; resultingStateId: number; note: string; verifiedAtUtc: string } export interface ResultSubmissionSummary { submissionId: string; electionCenterId: string; positionId: number; submittedByUserId: string; stateId: number; idempotencyKey: string; declaredTotalVotes: number; createdAtUtc: string; version: number; details: ResultDetailSummary[]; verification: ResultVerificationSummary | null }
export interface ExportSummary { exportId: string; stateId: number; reportType: string; format: string; requestedAtUtc: string; completedAtUtc: string | null; storageKey: string | null }
export interface PagedResult<T> { items: T[]; totalCount: number; page: number; pageSize: number }
export interface CenterDirectoryItem { electionCenterId: string; centerId: string; areaId: number; code: string; name: string; address: string | null; isVerified: boolean; boothCount: number; activeAgentCount: number }
export interface ElectionCenterSummary { electionCenterId: string; centerId: string; areaId: number; code: string; name: string; address: string | null; isVerified: boolean }
export interface BoothSummary { boothId: string; code: string; name: string; isActive: boolean } export interface CenterAgentSummary { assignmentId: string; userId: string; displayName: string; startsAtUtc: string; endsAtUtc: string; isActive: boolean }
export interface ChecklistItemSummary { itemId: string; requirement: string; isComplete: boolean; completedByUserId: string | null; completedAtUtc: string | null } export interface ChecklistSummary { checklistId: string; name: string; stateId: number; version: number; items: ChecklistItemSummary[] }
export interface VerificationSummary { verificationId: string; verifiedByUserId: string; verifiedBy: string; verifiedAtUtc: string } export interface CenterDetail { center: CenterDirectoryItem; booths: BoothSummary[]; agents: CenterAgentSummary[]; checklists: ChecklistSummary[]; verificationHistory: VerificationSummary[] }
export interface ReadinessStateSummary { id: number; code: string; name: string; rank: number } export interface PollingLookups { readinessStates: ReadinessStateSummary[] }
export interface InventoryNamedReference { id: string; name: string } export interface InventoryAreaReference { id: number; name: string } export interface MovementTypeReference { id: number; code: string; name: string; requiresSource: boolean; requiresDestination: boolean } export interface AllocationStateReference { id: number; code: string; name: string; isTerminal: boolean }
export interface InventoryLookups { areas: InventoryAreaReference[]; teams: InventoryNamedReference[]; centers: InventoryNamedReference[]; users: InventoryNamedReference[]; movementTypes: MovementTypeReference[]; allocationStates: AllocationStateReference[] }
export interface WarehouseSummary { warehouseId: string; areaId: number; name: string } export interface ItemSummary { itemId: string; sku: string; name: string; unit: string } export interface MovementSummary { movementId: string; itemId: string; movementTypeId: number; sourceWarehouseId: string | null; destinationWarehouseId: string | null; actorUserId: string; quantity: number; reference: string; occurredAtUtc: string } export interface AllocationSummary { allocationId: string; itemId: string; sourceWarehouseId: string; teamId: string | null; pollingCenterId: string | null; recipientUserId: string; stateId: number; quantity: number; createdAtUtc: string; acknowledgedAtUtc: string | null }
export interface ExpenseStateSummary { id: number; code: string; name: string; isApproved: boolean; isTerminal: boolean } export interface VendorSummary { vendorId: string; name: string; registrationNumber: string } export interface BudgetLineSummary { budgetLineId: string; category: string; allocatedAmount: number; committedAmount: number } export interface BudgetSummary { budgetId: string; name: string; currency: string; createdAtUtc: string; lines: BudgetLineSummary[] } export interface ExpenseSummary { expenseId: string; budgetLineId: string; vendorId: string | null; submittedByUserId: string; stateId: number; invoiceNumber: string; amount: number; expenseDate: string; createdAtUtc: string; version: number; paidAmount: number } export interface FinanceWorkspace { states: ExpenseStateSummary[]; vendors: VendorSummary[]; budgets: BudgetSummary[]; expenses: ExpenseSummary[] }
export interface EventRef { id: number; code: string; name: string; isTerminal: boolean } export interface EventNamed { id: string; name: string } export interface EventArea { id: number; name: string } export interface VenueSummary { venueId: string; areaId: number; name: string; address: string; capacity: number | null } export interface CampaignEventSummary { eventId: string; eventTypeId: number; stateId: number; areaId: number; venueId: string | null; title: string; startsAtUtc: string; endsAtUtc: string; completionReport: string | null; version: number } export interface MeetingSummary { meetingId: string; eventId: string | null; title: string; agenda: string; minutes: string | null; startsAtUtc: string; endsAtUtc: string; participantCount: number; attendedCount: number } export interface EventWorkspace { types: EventRef[]; states: EventRef[]; areas: EventArea[]; users: EventNamed[]; venues: VenueSummary[]; events: CampaignEventSummary[]; meetings: MeetingSummary[] }
export interface DashboardAlert { severity: string; title: string; message: string; route: string } export interface ElectionOperationsCard { electionId: string; name: string; electionDate: string; lifecycleStateId: number; teamCount: number; openTaskCount: number; centerCount: number; verifiedCenterCount: number; allocationCount: number; acknowledgedAllocationCount: number; budgetAllocated: number; expenseCommitted: number; eventCount: number; upcomingEventCount: number; resultSubmissionCount: number; verifiedResultCount: number; alerts: DashboardAlert[] } export interface OperationsDashboard { electionCount: number; activeElectionCount: number; openTaskCount: number; alertCount: number; elections: ElectionOperationsCard[] }
export interface AuditEntry { auditLogId: number; actorUserId: string; actorName: string; action: string; entityType: string; entityId: string; correlationId: string; metadataJson: string; occurredAtUtc: string } export interface AuditPage { items: AuditEntry[]; totalCount: number; page: number; pageSize: number } export interface NotificationItem { id: string; category: string; title: string; message: string; source: string; occurredAtUtc: string; isSecurityEvent: boolean; actionUrl: string | null; severity: string } export interface NotificationFeed { items: NotificationItem[]; unreadCount: number }

export interface VoterBulkRowDto {
  serialNumber?: number | null;
  voterNumber: string;
  fullName: string;
  fatherOrSpouseName?: string | null;
  gender: string;
  age?: number | null;
  areaName?: string | null;
  category: string;
  phone?: string | null;
  notes?: string | null;
  centerCode?: string | null;
  boothCode?: string | null;
  isValid: boolean;
  validationMessages?: string[];
}

export interface VoterBulkPreviewResult {
  totalRowsDetected: number;
  validRowsCount: number;
  invalidRowsCount: number;
  fileName: string;
  fileFormat: string;
  rows: VoterBulkRowDto[];
  warnings?: string[];
}

export interface VoterBulkImportResult {
  success: boolean;
  insertedCount: number;
  skippedCount: number;
  message: string;
  importedVoters: CandidateVoterSummary[];
}

export interface CandidateBroadcastLogItem {
  broadcastId: string;
  channel: string;
  recipientGroup: string;
  recipientCount: number;
  messageContent: string;
  templateType?: string | null;
  status: string;
  sentAtUtc: string;
}

export interface SendCandidateBroadcastRequest {
  channel: string;
  recipientGroup?: string;
  targetCenterId?: string | null;
  targetAgentType?: string | null;
  templateType?: string | null;
  messageContent: string;
}

export interface SendCandidateBroadcastResponse {
  success: boolean;
  broadcastId: string;
  recipientCount: number;
  channel: string;
  status: string;
  message: string;
}

export interface CandidateCampaignVenueItem {
  venueId: string;
  name: string;
  address: string;
  capacity?: number | null;
}

export interface CandidateCampaignEventItem {
  eventId: string;
  title: string;
  eventTypeName: string;
  eventTypeId: number;
  eventStateName: string;
  eventStateId: number;
  venueId?: string | null;
  venueName?: string | null;
  venueAddress?: string | null;
  venueCapacity?: number | null;
  startsAt: string;
  endsAt: string;
  permitId?: string | null;
  permitStatus?: string | null;
  permitStateId?: number | null;
  issuingAuthority?: string | null;
  permitReferenceNumber?: string | null;
  permitExpiresOn?: string | null;
  description?: string | null;
  isMikingHoursCompliant: boolean;
  createdAtUtc: string;
}

export interface CreateCampaignEventRequest {
  title: string;
  eventTypeId: number;
  venueId?: string | null;
  newVenueName?: string | null;
  newVenueAddress?: string | null;
  newVenueCapacity?: number | null;
  startsAt: string;
  endsAt: string;
  issuingAuthority?: string | null;
  permitReferenceNumber?: string | null;
  permitStateId: number;
  description?: string | null;
}

export interface UpdateCampaignEventPermitRequest {
  permitStateId: number;
  issuingAuthority?: string | null;
  permitReferenceNumber?: string | null;
  permitExpiresOn?: string | null;
}

export interface SmsGatewayConfigDto {
  configId: string;
  provider: string;
  apiKey: string;
  apiSecret?: string | null;
  senderId: string;
  endpointUrl?: string | null;
  isActive: boolean;
  balance: number;
  lastTestedAt?: string | null;
  updatedAt: string;
}

export interface UpdateSmsGatewayConfigRequest {
  provider: string;
  apiKey: string;
  apiSecret?: string | null;
  senderId: string;
  endpointUrl?: string | null;
  isActive: boolean;
}

export interface TestSmsRequest {
  phone: string;
  message?: string | null;
  apiKey?: string | null;
  senderId?: string | null;
  provider?: string | null;
  endpointUrl?: string | null;
}

export interface SendVoterBroadcastRequest {
  channel: string;
  targetFilter?: string | null;
  targetCenterId?: string | null;
  templateType?: string | null;
  messageContent: string;
  candidateId?: string | null;
}

export interface VoterQueueItem {
  voterId: string;
  fullName: string;
  phone: string;
  serialNumber: number;
  voterNumber: string;
  centerName: string;
  boothName?: string | null;
  message: string;
  waUrl: string;
}

export interface SendVoterBroadcastResponse {
  success: boolean;
  broadcastId: string;
  recipientCount: number;
  channel: string;
  status: string;
  message: string;
  queue?: VoterQueueItem[];
}
