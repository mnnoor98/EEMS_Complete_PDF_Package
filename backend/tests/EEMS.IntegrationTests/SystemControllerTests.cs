using EEMS.Api.Controllers;
using EEMS.SharedKernel.Tenancy;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class SystemControllerTests
{
    [Fact]
    public void GetContextReturnsAuthenticatedTenantIdentifier()
    {
        var tenantId = Guid.NewGuid();
        var controller = new SystemController(new StubTenantContext(tenantId));

        var result = controller.GetContext();

        var ok = Assert.IsType<OkObjectResult>(result.Result);
        var response = Assert.IsType<SystemContextResponse>(ok.Value);
        Assert.Equal(tenantId, response.TenantId);
    }

    private sealed class StubTenantContext(Guid tenantId) : ITenantContext
    {
        public Guid TenantId { get; } = tenantId;
        public bool IsAvailable => true;
    }
}
