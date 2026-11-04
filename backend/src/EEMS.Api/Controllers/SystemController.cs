using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/v1/system")]
public sealed class SystemController(ITenantContext tenantContext) : ControllerBase
{
    [HttpGet("context")]
    [ProducesResponseType<SystemContextResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public ActionResult<SystemContextResponse> GetContext()
    {
        return Ok(new SystemContextResponse(tenantContext.TenantId));
    }
}

public sealed record SystemContextResponse(Guid TenantId);
