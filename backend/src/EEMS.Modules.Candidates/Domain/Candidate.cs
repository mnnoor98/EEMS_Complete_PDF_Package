using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Candidates.Domain;

public sealed class Candidate : Entity<Guid>
{
    private Candidate() { }
    private Candidate(Guid id, Guid tenantId, string name, string? externalReference)
    {
        if (tenantId == Guid.Empty) throw new ArgumentException("Tenant is required.", nameof(tenantId));
        Id=id; TenantId=tenantId; Name=Require(name,200); ExternalReference=Optional(externalReference,100); IsActive=true; CreatedAtUtc=DateTimeOffset.UtcNow;
    }
    public Guid TenantId{get;private set;} public string Name{get;private set;}=string.Empty; public string? ExternalReference{get;private set;}
    public bool IsActive{get;private set;} public DateTimeOffset CreatedAtUtc{get;private set;}
    public static Candidate Create(Guid tenantId,string name,string? externalReference=null)=>new(Guid.NewGuid(),tenantId,name,externalReference);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
    private static string? Optional(string? value,int max){var text=value?.Trim();if(string.IsNullOrEmpty(text))return null;return text.Length<=max?text:throw new ArgumentException("Value is too long.");}
}
