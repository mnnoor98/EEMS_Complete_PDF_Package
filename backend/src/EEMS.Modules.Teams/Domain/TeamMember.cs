namespace EEMS.Modules.Teams.Domain;
public sealed class TeamMember
{
    private TeamMember(){} public TeamMember(Guid tenantId,Guid teamId,Guid userId,string responsibility){if(tenantId==Guid.Empty||teamId==Guid.Empty||userId==Guid.Empty)throw new ArgumentException("Tenant, team and user are required.");TenantId=tenantId;TeamId=teamId;UserId=userId;Responsibility=Require(responsibility,120);JoinedAtUtc=DateTimeOffset.UtcNow;IsActive=true;}
    public Guid TenantId{get;private set;}public Guid TeamId{get;private set;}public Guid UserId{get;private set;}public string Responsibility{get;private set;}=string.Empty;public DateTimeOffset JoinedAtUtc{get;private set;}public bool IsActive{get;private set;}
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
