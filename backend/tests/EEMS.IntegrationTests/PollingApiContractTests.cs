using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class PollingApiContractTests
{
    [Theory]
    [InlineData(nameof(PollingController.AddBooth), typeof(HttpPostAttribute))]
    [InlineData(nameof(PollingController.Verify), typeof(HttpPostAttribute))]
    [InlineData(nameof(PollingController.CreateChecklist), typeof(HttpPostAttribute))]
    [InlineData(nameof(PollingController.CompleteItem), typeof(HttpPutAttribute))]
    public void MutationEndpointsRequirePollingManagePermission(string methodName, Type verbAttribute)
    {
        var method = typeof(PollingController).GetMethod(methodName);
        Assert.NotNull(method);
        Assert.NotNull(method.GetCustomAttributes(verbAttribute, true).SingleOrDefault());
        var authorization = Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute), true).Cast<AuthorizeAttribute>());
        Assert.Equal(PermissionCodes.PollingManage, authorization.Policy);
    }
}
