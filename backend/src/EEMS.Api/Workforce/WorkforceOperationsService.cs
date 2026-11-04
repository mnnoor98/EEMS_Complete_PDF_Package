using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Teams.Domain;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Workforce;

public sealed class WorkforceOperationsService(
    TeamsDbContext teamsDb,
    PollingDbContext pollingDb,
    ElectionsDbContext electionsDb,
    GeographyDbContext geographyDb,
    IdentityDbContext identityDb,
    ITenantContext tenantContext)
{
    public async Task<WorkforceLookups> GetLookupsAsync(Guid electionId, CancellationToken token) => new(
        await teamsDb.TaskStates.Where(x => x.IsActive).OrderBy(x => x.Id)
            .Select(x => new TaskStateSummary(x.Id, x.Code, x.Name, x.IsTerminal)).ToListAsync(token),
        await teamsDb.TaskPriorities.Where(x => x.IsActive).OrderBy(x => x.Rank)
            .Select(x => new TaskPrioritySummary(x.Id, x.Code, x.Name, x.Rank)).ToListAsync(token),
        await geographyDb.Areas.Where(x => x.IsActive).OrderBy(x => x.NameBn)
            .Select(x => new WorkforceAreaSummary(x.Id, x.Code, x.NameBn, x.NameEn)).ToListAsync(token),
        await (from user in identityDb.Users join membership in identityDb.TenantUsers on user.Id equals membership.UserId
               where user.IsActive && membership.IsActive && membership.TenantId == tenantContext.TenantId
               orderby user.DisplayName select new WorkforceUserSummary(user.Id, user.DisplayName, user.ExternalSubject)).ToListAsync(token),
        await (from link in pollingDb.ElectionCenters join center in pollingDb.Centers on link.CenterId equals center.Id
               where link.TenantId == tenantContext.TenantId && link.ElectionId == electionId
               orderby center.Name select new WorkforceCenterSummary(link.Id, center.Code, center.Name)).ToListAsync(token));

    public async Task<IReadOnlyList<TeamSummary>> GetTeamsAsync(Guid electionId, CancellationToken token) =>
        await teamsDb.Teams.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId)
            .OrderBy(x => x.Name)
            .Select(x => new TeamSummary(x.Id, x.AreaId, x.LeaderUserId, x.Name, x.IsActive, x.CreatedAtUtc))
            .ToListAsync(token);

    public async Task<TeamSummary?> CreateTeamAsync(Guid electionId, CreateTeamCommand command, CancellationToken token)
    {
        if (!await ElectionExistsAsync(electionId, token) || !await geographyDb.Areas.AnyAsync(x => x.Id == command.AreaId && x.IsActive, token)) return null;
        var team = Team.Create(tenantContext.TenantId, electionId, command.AreaId, command.Name);
        teamsDb.Teams.Add(team);
        await teamsDb.SaveChangesAsync(token);
        return new TeamSummary(team.Id, team.AreaId, team.LeaderUserId, team.Name, team.IsActive, team.CreatedAtUtc);
    }

    public async Task<TeamSummary?> AssignTeamLeaderAsync(Guid electionId, Guid teamId, Guid userId, CancellationToken token)
    {
        var team=await teamsDb.Teams.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId&&x.IsActive,token);
        if(team is null||await GetActiveTenantUserAsync(userId,token) is null)return null;
        team.AssignLeader(userId);await teamsDb.SaveChangesAsync(token);
        return new TeamSummary(team.Id,team.AreaId,team.LeaderUserId,team.Name,team.IsActive,team.CreatedAtUtc);
    }

    public async Task<IReadOnlyList<FieldMemberSummary>> GetFieldMembersAsync(Guid electionId,Guid teamId,CancellationToken token)
    {
        if(!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId,token))return [];
        return await teamsDb.FieldMembers.Where(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId).OrderBy(x=>x.FullName)
            .Select(x=>new FieldMemberSummary(x.Id,x.TeamId,x.FullName,x.Phone,x.MemberType,x.AreaId,x.Address,x.EmergencyContact,x.JoinedAtUtc,x.IsActive)).ToListAsync(token);
    }

    public async Task<FieldMemberSummary?> CreateFieldMemberAsync(Guid electionId,Guid teamId,CreateFieldMemberCommand command,CancellationToken token)
    {
        if(!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId&&x.IsActive,token)||command.AreaId is not null&&!await geographyDb.Areas.AnyAsync(x=>x.Id==command.AreaId&&x.IsActive,token))return null;
        if(await teamsDb.FieldMembers.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Phone==command.Phone.Trim(),token))return null;
        var member=FieldMember.Create(tenantContext.TenantId,teamId,command.FullName,command.Phone,command.MemberType,command.AreaId,command.Address,command.EmergencyContact);teamsDb.FieldMembers.Add(member);await teamsDb.SaveChangesAsync(token);
        return new FieldMemberSummary(member.Id,member.TeamId,member.FullName,member.Phone,member.MemberType,member.AreaId,member.Address,member.EmergencyContact,member.JoinedAtUtc,member.IsActive);
    }

    public async Task<FieldMemberSummary?> UpdateFieldMemberAsync(Guid electionId,Guid teamId,Guid memberId,UpdateFieldMemberCommand command,CancellationToken token)
    {
        var member=await teamsDb.FieldMembers.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Id==memberId,token);
        if(member is null||!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId,token)||command.AreaId is not null&&!await geographyDb.Areas.AnyAsync(x=>x.Id==command.AreaId&&x.IsActive,token))return null;
        var phone=command.Phone.Trim();
        if(await teamsDb.FieldMembers.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Phone==phone&&x.Id!=memberId,token))return null;
        member.Update(command.FullName,phone,command.MemberType,command.AreaId,command.Address,command.EmergencyContact);await teamsDb.SaveChangesAsync(token);
        return ToSummary(member);
    }

    public async Task<FieldMemberSummary?> DeactivateFieldMemberAsync(Guid electionId,Guid teamId,Guid memberId,CancellationToken token)
    {
        var member=await teamsDb.FieldMembers.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Id==memberId,token);
        if(member is null||!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId,token))return null;
        member.Deactivate();await teamsDb.SaveChangesAsync(token);return ToSummary(member);
    }

    public async Task<IReadOnlyList<FieldAttendanceSummary>> GetFieldAttendanceAsync(Guid electionId,Guid teamId,DateOnly attendanceDate,CancellationToken token)
    {
        if(!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId,token))return [];
        return await teamsDb.FieldMemberAttendances.Where(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.AttendanceDate==attendanceDate)
            .OrderBy(x=>x.RecordedAtUtc).Select(x=>new FieldAttendanceSummary(x.Id,x.MemberId,x.AttendanceDate,x.Status,x.Note,x.RecordedByUserId,x.RecordedAtUtc)).ToListAsync(token);
    }

    public async Task<FieldAttendanceSummary?> RecordFieldAttendanceAsync(Guid electionId,Guid teamId,RecordFieldAttendanceCommand command,Guid recordedByUserId,CancellationToken token)
    {
        var status=command.Status.Trim().ToUpperInvariant();
        if(status is not ("PRESENT" or "ABSENT" or "LEAVE")||!await teamsDb.Teams.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==teamId&&x.IsActive,token)||!await teamsDb.FieldMembers.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Id==command.MemberId&&x.IsActive,token))return null;
        var attendance=await teamsDb.FieldMemberAttendances.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.MemberId==command.MemberId&&x.AttendanceDate==command.AttendanceDate,token);
        if(attendance is not null)return null;
        attendance=FieldMemberAttendance.Record(tenantContext.TenantId,teamId,command.MemberId,command.AttendanceDate,status,recordedByUserId,command.Note);teamsDb.FieldMemberAttendances.Add(attendance);await teamsDb.SaveChangesAsync(token);
        return new FieldAttendanceSummary(attendance.Id,attendance.MemberId,attendance.AttendanceDate,attendance.Status,attendance.Note,attendance.RecordedByUserId,attendance.RecordedAtUtc);
    }

    public async Task<IReadOnlyList<MemberWorkSummary>> GetMemberWorkAsync(Guid electionId,Guid teamId,CancellationToken token)=>
        await teamsDb.MemberWorkAssignments.Where(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.TeamId==teamId).OrderBy(x=>x.DueAtUtc)
            .Select(x=>new MemberWorkSummary(x.Id,x.MemberId,x.StateId,x.PriorityId,x.Title,x.Instructions,x.DueAtUtc,x.CreatedAtUtc,x.VerifiedByUserId,x.VerifiedAtUtc,x.VerificationNote,x.Version)).ToListAsync(token);

    public async Task<MemberWorkSummary?> AssignMemberWorkAsync(Guid electionId,Guid teamId,AssignMemberWorkCommand command,CancellationToken token)
    {
        if(!await teamsDb.FieldMembers.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.TeamId==teamId&&x.Id==command.MemberId&&x.IsActive,token)||!await teamsDb.TaskStates.AnyAsync(x=>x.Id==command.StateId&&x.IsActive,token)||!await teamsDb.TaskPriorities.AnyAsync(x=>x.Id==command.PriorityId&&x.IsActive,token))return null;
        var work=MemberWorkAssignment.Create(tenantContext.TenantId,electionId,teamId,command.MemberId,command.StateId,command.PriorityId,command.Title,command.Instructions,command.DueAtUtc);teamsDb.MemberWorkAssignments.Add(work);await teamsDb.SaveChangesAsync(token);
        return ToSummary(work);
    }

    public async Task<MemberWorkSummary?> MoveMemberWorkAsync(Guid electionId,Guid teamId,Guid assignmentId,short stateId,int expectedVersion,CancellationToken token)
    {
        var work=await teamsDb.MemberWorkAssignments.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.TeamId==teamId&&x.Id==assignmentId,token);
        if(work is null||work.Version!=expectedVersion||!await teamsDb.TaskStates.AnyAsync(x=>x.Id==stateId&&x.IsActive,token))return null;
        work.MoveTo(stateId);await teamsDb.SaveChangesAsync(token);return ToSummary(work);
    }

    public async Task<MemberWorkSummary?> VerifyMemberWorkAsync(Guid electionId,Guid teamId,Guid assignmentId,int expectedVersion,Guid verifierUserId,string? note,CancellationToken token)
    {
        var work=await teamsDb.MemberWorkAssignments.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.TeamId==teamId&&x.Id==assignmentId,token);
        if(work is null||work.Version!=expectedVersion||work.VerifiedAtUtc is not null||!await teamsDb.TaskStates.AnyAsync(x=>x.Id==work.StateId&&x.IsActive&&x.IsTerminal,token))return null;
        work.Verify(verifierUserId,note);await teamsDb.SaveChangesAsync(token);return ToSummary(work);
    }

    public async Task<IReadOnlyList<TeamMemberSummary>> GetTeamMembersAsync(Guid electionId, Guid teamId, CancellationToken token)
    {
        if (!await teamsDb.Teams.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == teamId, token)) return [];
        var members = await teamsDb.TeamMembers.Where(x => x.TenantId == tenantContext.TenantId && x.TeamId == teamId).ToListAsync(token);
        var users = await GetUsersAsync(members.Select(x => x.UserId), token);
        return members.Where(x => users.ContainsKey(x.UserId)).Select(x =>
        {
            var user = users[x.UserId];
            return new TeamMemberSummary(x.UserId, user.DisplayName, user.ExternalSubject, x.Responsibility, x.JoinedAtUtc, x.IsActive);
        }).OrderBy(x => x.DisplayName).ToList();
    }

    public async Task<TeamMemberSummary?> AddTeamMemberAsync(Guid electionId, Guid teamId, AddTeamMemberCommand command, CancellationToken token)
    {
        var teamExists = await teamsDb.Teams.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == teamId && x.IsActive, token);
        var user = await GetActiveTenantUserAsync(command.UserId, token);
        if (!teamExists || user is null) return null;
        if (await teamsDb.TeamMembers.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.TeamId == teamId && x.UserId == command.UserId, token)) return null;
        var member = new TeamMember(tenantContext.TenantId, teamId, command.UserId, command.Responsibility);
        teamsDb.TeamMembers.Add(member);
        await teamsDb.SaveChangesAsync(token);
        return new TeamMemberSummary(member.UserId, user.DisplayName, user.ExternalSubject, member.Responsibility, member.JoinedAtUtc, member.IsActive);
    }

    public async Task<IReadOnlyList<TeamTaskSummary>> GetTasksAsync(Guid electionId, CancellationToken token) =>
        await teamsDb.Tasks.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId)
            .OrderBy(x => x.DueAtUtc).ThenBy(x => x.Title)
            .Select(x => new TeamTaskSummary(x.Id, x.TeamId, x.AssigneeUserId, x.StateId, x.PriorityId, x.Title, x.DueAtUtc, x.CreatedAtUtc, x.Version))
            .ToListAsync(token);

    public async Task<TeamTaskSummary?> CreateTaskAsync(Guid electionId, CreateTaskCommand command, CancellationToken token)
    {
        if (command.TeamId is null && command.AssigneeUserId is null ||
            !await ElectionExistsAsync(electionId, token) ||
            !await teamsDb.TaskStates.AnyAsync(x => x.Id == command.StateId && x.IsActive, token) ||
            !await teamsDb.TaskPriorities.AnyAsync(x => x.Id == command.PriorityId && x.IsActive, token) ||
            command.TeamId is not null && !await teamsDb.Teams.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == command.TeamId && x.IsActive, token) ||
            command.AssigneeUserId is not null && await GetActiveTenantUserAsync(command.AssigneeUserId.Value, token) is null) return null;
        var task = TeamTask.Create(tenantContext.TenantId, electionId, command.TeamId, command.AssigneeUserId, command.StateId, command.PriorityId, command.Title, command.DueAtUtc);
        teamsDb.Tasks.Add(task);
        await teamsDb.SaveChangesAsync(token);
        return ToSummary(task);
    }

    public async Task<TeamTaskSummary?> MoveTaskAsync(Guid electionId, Guid taskId, short stateId, int expectedVersion, CancellationToken token)
    {
        var task = await teamsDb.Tasks.SingleOrDefaultAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == taskId, token);
        if (task is null || task.Version != expectedVersion || !await teamsDb.TaskStates.AnyAsync(x => x.Id == stateId && x.IsActive, token)) return null;
        task.MoveTo(stateId);
        await teamsDb.SaveChangesAsync(token);
        return ToSummary(task);
    }

    public async Task<IReadOnlyList<TrainingSummary>> GetTrainingsAsync(Guid electionId, CancellationToken token) =>
        await teamsDb.Trainings.Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId)
            .OrderBy(x => x.StartsAtUtc)
            .Select(x => new TrainingSummary(x.Id, x.Title, x.StartsAtUtc, x.EndsAtUtc))
            .ToListAsync(token);

    public async Task<TrainingSummary?> CreateTrainingAsync(Guid electionId, CreateTrainingCommand command, CancellationToken token)
    {
        if (!await ElectionExistsAsync(electionId, token) || command.EndsAtUtc <= command.StartsAtUtc) return null;
        var training = Training.Create(tenantContext.TenantId, electionId, command.Title, command.StartsAtUtc, command.EndsAtUtc);
        teamsDb.Trainings.Add(training);
        await teamsDb.SaveChangesAsync(token);
        return new TrainingSummary(training.Id, training.Title, training.StartsAtUtc, training.EndsAtUtc);
    }

    public async Task<IReadOnlyList<AttendanceSummary>> GetAttendanceAsync(Guid electionId, Guid trainingId, CancellationToken token)
    {
        if (!await teamsDb.Trainings.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == trainingId, token)) return [];
        var attendance = await teamsDb.Attendances.Where(x => x.TenantId == tenantContext.TenantId && x.TrainingId == trainingId).ToListAsync(token);
        var users = await GetUsersAsync(attendance.Select(x => x.UserId), token);
        return attendance.Where(x => users.ContainsKey(x.UserId)).Select(x =>
        {
            var user = users[x.UserId];
            return new AttendanceSummary(x.UserId, user.DisplayName, user.ExternalSubject, x.RecordedAtUtc);
        }).OrderBy(x => x.DisplayName).ToList();
    }

    public async Task<AttendanceSummary?> RecordAttendanceAsync(Guid electionId, Guid trainingId, Guid userId, DateTimeOffset? recordedAtUtc, CancellationToken token)
    {
        var trainingExists = await teamsDb.Trainings.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == trainingId, token);
        var user = await GetActiveTenantUserAsync(userId, token);
        if (!trainingExists || user is null || await teamsDb.Attendances.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.TrainingId == trainingId && x.UserId == userId, token)) return null;
        var attendance = new Attendance(tenantContext.TenantId, trainingId, userId, recordedAtUtc ?? DateTimeOffset.UtcNow);
        teamsDb.Attendances.Add(attendance);
        await teamsDb.SaveChangesAsync(token);
        return new AttendanceSummary(user.Id, user.DisplayName, user.ExternalSubject, attendance.RecordedAtUtc);
    }

    public async Task<IReadOnlyList<AgentAssignmentSummary>> GetAgentAssignmentsAsync(Guid electionId, CancellationToken token)
    {
        var centerIds = await pollingDb.ElectionCenters
            .Where(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId)
            .Select(x => x.Id).ToListAsync(token);
        var assignments = await pollingDb.AgentAssignments
            .Where(x => x.TenantId == tenantContext.TenantId && centerIds.Contains(x.ElectionCenterId))
            .ToListAsync(token);
        var users = await GetUsersAsync(assignments.Select(x => x.UserId), token);
        return assignments.Where(x => users.ContainsKey(x.UserId)).Select(x =>
        {
            var user = users[x.UserId];
            return new AgentAssignmentSummary(x.Id, x.ElectionCenterId, x.UserId, user.DisplayName, user.ExternalSubject, x.StartsAtUtc, x.EndsAtUtc, x.IsActive);
        }).OrderBy(x => x.StartsAtUtc).ToList();
    }

    public async Task<AgentAssignmentSummary?> AssignAgentAsync(Guid electionId, AssignAgentCommand command, CancellationToken token)
    {
        var centerExists = await pollingDb.ElectionCenters.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.ElectionId == electionId && x.Id == command.ElectionCenterId, token);
        var user = await GetActiveTenantUserAsync(command.UserId, token);
        var duplicate = await pollingDb.AgentAssignments.AnyAsync(x => x.TenantId == tenantContext.TenantId &&
            x.ElectionCenterId == command.ElectionCenterId && x.UserId == command.UserId && x.StartsAtUtc == command.StartsAtUtc, token);
        if (!centerExists || user is null || duplicate || command.EndsAtUtc <= command.StartsAtUtc) return null;
        var assignment = AgentAssignment.Create(tenantContext.TenantId, command.ElectionCenterId, command.UserId, command.StartsAtUtc, command.EndsAtUtc);
        pollingDb.AgentAssignments.Add(assignment);
        await pollingDb.SaveChangesAsync(token);
        return new AgentAssignmentSummary(assignment.Id, assignment.ElectionCenterId, assignment.UserId, user.DisplayName, user.ExternalSubject, assignment.StartsAtUtc, assignment.EndsAtUtc, assignment.IsActive);
    }

    private Task<bool> ElectionExistsAsync(Guid electionId, CancellationToken token) =>
        electionsDb.Elections.AnyAsync(x => x.TenantId == tenantContext.TenantId && x.Id == electionId, token);

    private async Task<EEMS.Modules.Identity.Domain.User?> GetActiveTenantUserAsync(Guid userId, CancellationToken token)
    {
        var tenantId = tenantContext.TenantId;
        return await (from user in identityDb.Users
                      join membership in identityDb.TenantUsers on user.Id equals membership.UserId
                      where user.Id == userId && user.IsActive && membership.TenantId == tenantId && membership.IsActive
                      select user).SingleOrDefaultAsync(token);
    }

    private async Task<IReadOnlyDictionary<Guid, EEMS.Modules.Identity.Domain.User>> GetUsersAsync(IEnumerable<Guid> userIds, CancellationToken token)
    {
        var ids = userIds.Distinct().ToArray();
        return await identityDb.Users.Where(x => ids.Contains(x.Id)).ToDictionaryAsync(x => x.Id, token);
    }

    private static TeamTaskSummary ToSummary(TeamTask task) =>
        new(task.Id, task.TeamId, task.AssigneeUserId, task.StateId, task.PriorityId, task.Title, task.DueAtUtc, task.CreatedAtUtc, task.Version);
    private static FieldMemberSummary ToSummary(FieldMember member)=>new(member.Id,member.TeamId,member.FullName,member.Phone,member.MemberType,member.AreaId,member.Address,member.EmergencyContact,member.JoinedAtUtc,member.IsActive);
    private static MemberWorkSummary ToSummary(MemberWorkAssignment work)=>new(work.Id,work.MemberId,work.StateId,work.PriorityId,work.Title,work.Instructions,work.DueAtUtc,work.CreatedAtUtc,work.VerifiedByUserId,work.VerifiedAtUtc,work.VerificationNote,work.Version);
}

public sealed record WorkforceLookups(IReadOnlyList<TaskStateSummary> TaskStates, IReadOnlyList<TaskPrioritySummary> TaskPriorities, IReadOnlyList<WorkforceAreaSummary> Areas, IReadOnlyList<WorkforceUserSummary> Users, IReadOnlyList<WorkforceCenterSummary> Centers);
public sealed record WorkforceAreaSummary(long Id, string Code, string NameBn, string? NameEn);
public sealed record WorkforceUserSummary(Guid UserId, string DisplayName, string Username);
public sealed record WorkforceCenterSummary(Guid ElectionCenterId, string Code, string Name);
public sealed record TaskStateSummary(short Id, string Code, string Name, bool IsTerminal);
public sealed record TaskPrioritySummary(short Id, string Code, string Name, short Rank);
public sealed record TeamSummary(Guid TeamId, long AreaId, Guid? LeaderUserId, string Name, bool IsActive, DateTimeOffset CreatedAtUtc);
public sealed record TeamMemberSummary(Guid UserId, string DisplayName, string Username, string Responsibility, DateTimeOffset JoinedAtUtc, bool IsActive);
public sealed record FieldMemberSummary(Guid MemberId,Guid TeamId,string FullName,string Phone,string MemberType,long? AreaId,string? Address,string? EmergencyContact,DateTimeOffset JoinedAtUtc,bool IsActive);
public sealed record FieldAttendanceSummary(Guid AttendanceId,Guid MemberId,DateOnly AttendanceDate,string Status,string? Note,Guid RecordedByUserId,DateTimeOffset RecordedAtUtc);
public sealed record MemberWorkSummary(Guid AssignmentId,Guid MemberId,short StateId,short PriorityId,string Title,string? Instructions,DateTimeOffset? DueAtUtc,DateTimeOffset CreatedAtUtc,Guid? VerifiedByUserId,DateTimeOffset? VerifiedAtUtc,string? VerificationNote,int Version);
public sealed record TeamTaskSummary(Guid TaskId, Guid? TeamId, Guid? AssigneeUserId, short StateId, short PriorityId, string Title, DateTimeOffset? DueAtUtc, DateTimeOffset CreatedAtUtc, int Version);
public sealed record TrainingSummary(Guid TrainingId, string Title, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc);
public sealed record AttendanceSummary(Guid UserId, string DisplayName, string Username, DateTimeOffset RecordedAtUtc);
public sealed record AgentAssignmentSummary(Guid AssignmentId, Guid ElectionCenterId, Guid UserId, string DisplayName, string Username, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc, bool IsActive);
public sealed record CreateTeamCommand(long AreaId, string Name);
public sealed record AddTeamMemberCommand(Guid UserId, string Responsibility);
public sealed record UpdateFieldMemberCommand(string FullName,string Phone,string MemberType,long? AreaId,string? Address,string? EmergencyContact);
public sealed record RecordFieldAttendanceCommand(Guid MemberId,DateOnly AttendanceDate,string Status,string? Note);
public sealed record CreateFieldMemberCommand(string FullName,string Phone,string MemberType,long? AreaId,string? Address,string? EmergencyContact);
public sealed record AssignMemberWorkCommand(Guid MemberId,short StateId,short PriorityId,string Title,string? Instructions,DateTimeOffset? DueAtUtc);
public sealed record CreateTaskCommand(Guid? TeamId, Guid? AssigneeUserId, short StateId, short PriorityId, string Title, DateTimeOffset? DueAtUtc);
public sealed record CreateTrainingCommand(string Title, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc);
public sealed record AssignAgentCommand(Guid ElectionCenterId, Guid UserId, DateTimeOffset StartsAtUtc, DateTimeOffset EndsAtUtc);
