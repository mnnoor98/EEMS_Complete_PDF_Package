using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class WorkforceApiContractTests
{
    [Theory]
    [InlineData(nameof(WorkforceController.CreateTeam), typeof(HttpPostAttribute))]
    [InlineData(nameof(WorkforceController.AddMember), typeof(HttpPostAttribute))]
    [InlineData(nameof(WorkforceController.CreateTask), typeof(HttpPostAttribute))]
    [InlineData(nameof(WorkforceController.MoveTask), typeof(HttpPutAttribute))]
    [InlineData(nameof(WorkforceController.CreateTraining), typeof(HttpPostAttribute))]
    [InlineData(nameof(WorkforceController.RecordAttendance), typeof(HttpPostAttribute))]
    [InlineData(nameof(WorkforceController.AssignAgent), typeof(HttpPostAttribute))]
    public void MutationEndpointsRequireWorkforceManagePermission(string methodName, Type verbAttribute)
    {
        var method = typeof(WorkforceController).GetMethod(methodName);
        Assert.NotNull(method);
        Assert.NotNull(method.GetCustomAttributes(verbAttribute, true).SingleOrDefault());
        var authorization = Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute), true).Cast<AuthorizeAttribute>());
        Assert.Equal(PermissionCodes.WorkforceManage, authorization.Policy);
    }
}
