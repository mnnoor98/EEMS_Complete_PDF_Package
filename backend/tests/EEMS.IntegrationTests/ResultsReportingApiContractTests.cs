using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class ResultsReportingApiContractTests
{
    [Theory]
    [InlineData(nameof(ResultsReportingController.Submit), PermissionCodes.ResultsManage, typeof(HttpPostAttribute))]
    [InlineData(nameof(ResultsReportingController.Verify), PermissionCodes.ResultsManage, typeof(HttpPostAttribute))]
    [InlineData(nameof(ResultsReportingController.RequestExport), PermissionCodes.ReportingManage, typeof(HttpPostAttribute))]
    public void MutationEndpointsRequireExpectedPermission(string methodName, string policy, Type verbAttribute)
    {
        var method = typeof(ResultsReportingController).GetMethod(methodName);
        Assert.NotNull(method);
        Assert.NotNull(method.GetCustomAttributes(verbAttribute, true).SingleOrDefault());
        var authorization = Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute), true).Cast<AuthorizeAttribute>());
        Assert.Equal(policy, authorization.Policy);
    }
}
