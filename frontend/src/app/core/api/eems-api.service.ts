import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {
  AgentAssignmentSummary, BoothSummary, CandidateSummary, CenterDetail, CenterDirectoryItem, ChecklistSummary,
  ElectionCenterSummary, ElectionLookups, ElectionSummary, PagedResult, PollingLookups, TeamMemberSummary, TeamSummary,
  TeamTaskSummary, TrainingSummary, UserSummary, VerificationSummary, WorkforceLookups
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
  getLookups(id: string) { return this.http.get<WorkforceLookups>(`/api/v1/elections/${id}/workforce/lookups`); }
  getTeams(id: string) { return this.http.get<TeamSummary[]>(`/api/v1/elections/${id}/workforce/teams`); }
  createTeam(id: string, body: {areaId: number; name: string}) { return this.http.post<TeamSummary>(`/api/v1/elections/${id}/workforce/teams`, body); }
  getMembers(id: string, teamId: string) { return this.http.get<TeamMemberSummary[]>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`); }
  addMember(id: string, teamId: string, body: {userId: string; responsibility: string}) { return this.http.post<TeamMemberSummary>(`/api/v1/elections/${id}/workforce/teams/${teamId}/members`, body); }
  getTasks(id: string) { return this.http.get<TeamTaskSummary[]>(`/api/v1/elections/${id}/workforce/tasks`); }
  createTask(id: string, body: object) { return this.http.post<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks`, body); }
  moveTask(id: string, task: TeamTaskSummary, stateId: number) { return this.http.put<TeamTaskSummary>(`/api/v1/elections/${id}/workforce/tasks/${task.taskId}/state`, {stateId, expectedVersion: task.version}); }
  getTrainings(id: string) { return this.http.get<TrainingSummary[]>(`/api/v1/elections/${id}/workforce/trainings`); }
  createTraining(id: string, body: object) { return this.http.post<TrainingSummary>(`/api/v1/elections/${id}/workforce/trainings`, body); }
  getAgents(id: string) { return this.http.get<AgentAssignmentSummary[]>(`/api/v1/elections/${id}/workforce/agents`); }
  getPollingCenters(id: string, search = '', verified = '') { const params: {[key: string]: string | number} = {page: 1, pageSize: 50}; if (search) params['search'] = search; if (verified) params['verified'] = verified; return this.http.get<PagedResult<CenterDirectoryItem>>(`/api/v1/elections/${id}/polling-centers`, {params}); }
  getPollingCenter(id: string, centerId: string) { return this.http.get<CenterDetail>(`/api/v1/elections/${id}/polling-centers/${centerId}`); }
  getPollingLookups(id: string) { return this.http.get<PollingLookups>(`/api/v1/elections/${id}/polling-centers/lookups`); }
  addBooth(id: string, centerId: string, body: {code: string; name: string}) { return this.http.post<BoothSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/booths`, body); }
  verifyCenter(id: string, centerId: string) { return this.http.post<VerificationSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/verify`, {}); }
  deactivateAgent(id: string, centerId: string, assignmentId: string) { return this.http.put<void>(`/api/v1/elections/${id}/polling-centers/${centerId}/agents/${assignmentId}/deactivate`, {}); }
  createChecklist(id: string, centerId: string, body: {name: string; requirements: string[]}) { return this.http.post<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists`, body); }
  completeChecklistItem(id: string, centerId: string, checklist: ChecklistSummary, itemId: string) { return this.http.put<ChecklistSummary>(`/api/v1/elections/${id}/polling-centers/${centerId}/checklists/${checklist.checklistId}/items/${itemId}/complete`, {expectedVersion: checklist.version}); }
}
