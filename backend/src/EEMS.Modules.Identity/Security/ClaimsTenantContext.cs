using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Http;

namespace EEMS.Modules.Identity.Security;

public sealed class ClaimsTenantContext(IHttpContextAccessor accessor) : ITenantContext
{
    private string? RawTenantId => accessor.HttpContext?.User.FindFirst(IdentityClaimTypes.TenantId)?.Value;
    public bool IsAvailable => Guid.TryParse(RawTenantId, out var tenantId) && tenantId != Guid.Empty;
    public Guid TenantId => IsAvailable ? Guid.Parse(RawTenantId!) : throw new InvalidOperationException("A verified tenant claim is required.");
}
