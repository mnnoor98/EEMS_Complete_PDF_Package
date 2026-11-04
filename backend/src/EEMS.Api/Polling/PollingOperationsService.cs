using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Operations.Domain;
using EEMS.Modules.Operations.Infrastructure;
using EEMS.Modules.Polling.Domain;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.SharedKernel.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Api.Polling;

public sealed class PollingOperationsService(PollingDbContext pollingDb,OperationsDbContext operationsDb,IdentityDbContext identityDb,ITenantContext tenantContext)
{
    public async Task<PollingLookups> GetLookupsAsync(CancellationToken token)=>new(
        await operationsDb.ReadinessStates.Where(x=>x.IsActive).OrderBy(x=>x.Rank).Select(x=>new ReadinessStateSummary(x.Id,x.Code,x.Name,x.Rank)).ToListAsync(token));

    public async Task<PagedResult<CenterDirectoryItem>> GetCentersAsync(Guid electionId,string? search,bool? verified,int page,int pageSize,CancellationToken token)
    {
        var query=from link in pollingDb.ElectionCenters join center in pollingDb.Centers on link.CenterId equals center.Id
            where link.TenantId==tenantContext.TenantId&&link.ElectionId==electionId select new{link,center};
        if(!string.IsNullOrWhiteSpace(search)){var pattern=$"%{search.Trim()}%";query=query.Where(x=>EF.Functions.ILike(x.center.Code,pattern)||EF.Functions.ILike(x.center.Name,pattern)||(x.center.Address!=null&&EF.Functions.ILike(x.center.Address,pattern)));}
        if(verified.HasValue)query=query.Where(x=>x.link.IsVerified==verified.Value);
        var total=await query.CountAsync(token);
        var items=await query.OrderBy(x=>x.center.Name).Skip((page-1)*pageSize).Take(pageSize)
            .Select(x=>new CenterDirectoryItem(x.link.Id,x.center.Id,x.center.AreaId,x.center.Code,x.center.Name,x.center.Address,x.link.IsVerified,
                pollingDb.Booths.Count(b=>b.CenterId==x.center.Id&&b.IsActive),pollingDb.AgentAssignments.Count(a=>a.ElectionCenterId==x.link.Id&&a.IsActive))).ToListAsync(token);
        return new PagedResult<CenterDirectoryItem>(items,total,page,pageSize);
    }

    public async Task<CenterDetail?> GetCenterAsync(Guid electionId,Guid electionCenterId,CancellationToken token)
    {
        var center=await (from link in pollingDb.ElectionCenters join item in pollingDb.Centers on link.CenterId equals item.Id
            where link.TenantId==tenantContext.TenantId&&link.ElectionId==electionId&&link.Id==electionCenterId
            select new CenterDirectoryItem(link.Id,item.Id,item.AreaId,item.Code,item.Name,item.Address,link.IsVerified,0,0)).SingleOrDefaultAsync(token);
        if(center is null)return null;
        var booths=await pollingDb.Booths.Where(x=>x.CenterId==center.CenterId).OrderBy(x=>x.Code).Select(x=>new BoothSummary(x.Id,x.Code,x.Name,x.IsActive)).ToListAsync(token);
        var assignments=await pollingDb.AgentAssignments.Where(x=>x.TenantId==tenantContext.TenantId&&x.ElectionCenterId==electionCenterId).OrderBy(x=>x.StartsAtUtc).ToListAsync(token);
        var verifications=await pollingDb.CenterVerifications.Where(x=>x.TenantId==tenantContext.TenantId&&x.ElectionCenterId==electionCenterId).OrderByDescending(x=>x.VerifiedAtUtc).ToListAsync(token);
        var userIds=assignments.Select(x=>x.UserId).Concat(verifications.Select(x=>x.VerifiedByUserId)).Distinct().ToArray();
        var users=await identityDb.Users.Where(x=>userIds.Contains(x.Id)).ToDictionaryAsync(x=>x.Id,token);
        var agentItems=assignments.Select(x=>new CenterAgentSummary(x.Id,x.UserId,users.GetValueOrDefault(x.UserId)?.DisplayName??"Unknown user",x.StartsAtUtc,x.EndsAtUtc,x.IsActive)).ToList();
        var history=verifications.Select(x=>new VerificationSummary(x.Id,x.VerifiedByUserId,users.GetValueOrDefault(x.VerifiedByUserId)?.DisplayName??"Unknown user",x.VerifiedAtUtc)).ToList();
        var checklists=await operationsDb.Checklists.Where(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.ElectionCenterId==electionCenterId).OrderBy(x=>x.Name).ToListAsync(token);
        var checklistIds=checklists.Select(x=>x.Id).ToArray();
        var items=await operationsDb.ChecklistItems.Where(x=>x.TenantId==tenantContext.TenantId&&checklistIds.Contains(x.ChecklistId)).OrderBy(x=>x.Requirement).ToListAsync(token);
        var readiness=checklists.Select(x=>new ChecklistSummary(x.Id,x.Name,x.StateId,x.Version,items.Where(i=>i.ChecklistId==x.Id).Select(i=>new ChecklistItemSummary(i.Id,i.Requirement,i.IsComplete,i.CompletedByUserId,i.CompletedAtUtc)).ToList())).ToList();
        return new CenterDetail(center with{BoothCount=booths.Count,ActiveAgentCount=agentItems.Count(x=>x.IsActive)},booths,agentItems,readiness,history);
    }

    public async Task<BoothSummary?> AddBoothAsync(Guid electionId,Guid electionCenterId,string code,string name,CancellationToken token)
    {
        var centerId=await pollingDb.ElectionCenters.Where(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==electionCenterId).Select(x=>(Guid?)x.CenterId).SingleOrDefaultAsync(token);
        if(centerId is null)return null;var normalized=code.Trim().ToUpperInvariant();
        if(await pollingDb.Booths.AnyAsync(x=>x.CenterId==centerId&&x.Code==normalized,token))return null;
        var booth=Booth.Create(centerId.Value,normalized,name);pollingDb.Booths.Add(booth);await pollingDb.SaveChangesAsync(token);return new BoothSummary(booth.Id,booth.Code,booth.Name,booth.IsActive);
    }

    public async Task<VerificationSummary?> VerifyAsync(Guid electionId,Guid electionCenterId,Guid userId,CancellationToken token)
    {
        var link=await pollingDb.ElectionCenters.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==electionCenterId,token);if(link is null)return null;
        link.Verify();var verification=CenterVerification.Record(tenantContext.TenantId,electionCenterId,userId);pollingDb.CenterVerifications.Add(verification);await pollingDb.SaveChangesAsync(token);
        var name=await identityDb.Users.Where(x=>x.Id==userId).Select(x=>x.DisplayName).SingleOrDefaultAsync(token)??"Unknown user";return new VerificationSummary(verification.Id,userId,name,verification.VerifiedAtUtc);
    }

    public async Task<bool> DeactivateAgentAsync(Guid electionId,Guid electionCenterId,Guid assignmentId,CancellationToken token)
    {
        var validCenter=await pollingDb.ElectionCenters.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==electionCenterId,token);
        var assignment=await pollingDb.AgentAssignments.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionCenterId==electionCenterId&&x.Id==assignmentId,token);if(!validCenter||assignment is null)return false;assignment.Deactivate();await pollingDb.SaveChangesAsync(token);return true;
    }

    public async Task<ChecklistSummary?> CreateChecklistAsync(Guid electionId,Guid electionCenterId,CreateChecklistCommand command,CancellationToken token)
    {
        var centerExists=await pollingDb.ElectionCenters.AnyAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.Id==electionCenterId,token);
        var firstState=await operationsDb.ReadinessStates.Where(x=>x.IsActive).OrderBy(x=>x.Rank).FirstOrDefaultAsync(token);
        if(!centerExists||firstState is null||command.Requirements.Count==0||command.Requirements.Any(x=>string.IsNullOrWhiteSpace(x)||x.Trim().Length>300))return null;
        var checklist=ReadinessChecklist.Create(tenantContext.TenantId,electionId,electionCenterId,firstState.Id,command.Name);operationsDb.Checklists.Add(checklist);await operationsDb.SaveChangesAsync(token);
        var items=command.Requirements.Select(x=>ChecklistItem.Create(tenantContext.TenantId,checklist.Id,x)).ToList();operationsDb.ChecklistItems.AddRange(items);await operationsDb.SaveChangesAsync(token);
        return new ChecklistSummary(checklist.Id,checklist.Name,checklist.StateId,checklist.Version,items.Select(x=>new ChecklistItemSummary(x.Id,x.Requirement,false,null,null)).ToList());
    }

    public async Task<ChecklistSummary?> CompleteChecklistItemAsync(Guid electionId,Guid electionCenterId,Guid checklistId,Guid itemId,Guid userId,int expectedVersion,CancellationToken token)
    {
        var checklist=await operationsDb.Checklists.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ElectionId==electionId&&x.ElectionCenterId==electionCenterId&&x.Id==checklistId,token);
        var item=await operationsDb.ChecklistItems.SingleOrDefaultAsync(x=>x.TenantId==tenantContext.TenantId&&x.ChecklistId==checklistId&&x.Id==itemId,token);
        if(checklist is null||item is null||item.IsComplete||checklist.Version!=expectedVersion)return null;
        item.Complete(userId);var allItems=await operationsDb.ChecklistItems.Where(x=>x.TenantId==tenantContext.TenantId&&x.ChecklistId==checklistId).ToListAsync(token);
        var completed=allItems.Count(x=>x.IsComplete);var states=await operationsDb.ReadinessStates.Where(x=>x.IsActive).OrderBy(x=>x.Rank).ToListAsync(token);
        var state=completed==allItems.Count?states.Last():states[Math.Min(1,states.Count-1)];checklist.Recalculate(state.Id);await operationsDb.SaveChangesAsync(token);
        return new ChecklistSummary(checklist.Id,checklist.Name,checklist.StateId,checklist.Version,allItems.Select(x=>new ChecklistItemSummary(x.Id,x.Requirement,x.IsComplete,x.CompletedByUserId,x.CompletedAtUtc)).ToList());
    }
}

public sealed record PagedResult<T>(IReadOnlyList<T> Items,int TotalCount,int Page,int PageSize);
public sealed record PollingLookups(IReadOnlyList<ReadinessStateSummary> ReadinessStates);public sealed record ReadinessStateSummary(short Id,string Code,string Name,short Rank);
public sealed record CenterDirectoryItem(Guid ElectionCenterId,Guid CenterId,long AreaId,string Code,string Name,string? Address,bool IsVerified,int BoothCount,int ActiveAgentCount);
public sealed record CenterDetail(CenterDirectoryItem Center,IReadOnlyList<BoothSummary> Booths,IReadOnlyList<CenterAgentSummary> Agents,IReadOnlyList<ChecklistSummary> Checklists,IReadOnlyList<VerificationSummary> VerificationHistory);
public sealed record BoothSummary(Guid BoothId,string Code,string Name,bool IsActive);public sealed record CenterAgentSummary(Guid AssignmentId,Guid UserId,string DisplayName,DateTimeOffset StartsAtUtc,DateTimeOffset EndsAtUtc,bool IsActive);
public sealed record VerificationSummary(Guid VerificationId,Guid VerifiedByUserId,string VerifiedBy,DateTimeOffset VerifiedAtUtc);public sealed record ChecklistSummary(Guid ChecklistId,string Name,short StateId,int Version,IReadOnlyList<ChecklistItemSummary> Items);
public sealed record ChecklistItemSummary(Guid ItemId,string Requirement,bool IsComplete,Guid? CompletedByUserId,DateTimeOffset? CompletedAtUtc);public sealed record CreateChecklistCommand(string Name,IReadOnlyList<string> Requirements);
