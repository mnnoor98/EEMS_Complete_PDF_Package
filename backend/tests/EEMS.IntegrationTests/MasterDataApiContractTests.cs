using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class MasterDataApiContractTests
{
    [Theory]
    [InlineData(nameof(MasterDataController.AddArea))]
    [InlineData(nameof(MasterDataController.AddElectionType))]
    [InlineData(nameof(MasterDataController.AddPosition))]
    [InlineData(nameof(MasterDataController.AddTaskState))]
    [InlineData(nameof(MasterDataController.AddTaskPriority))]
    public void MutationsRequireElectionManagePermission(string methodName)
    {
        var method=typeof(MasterDataController).GetMethod(methodName);
        Assert.NotNull(method);Assert.NotNull(method.GetCustomAttributes(typeof(HttpPostAttribute),true).SingleOrDefault());
        var authorization=Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute),true).Cast<AuthorizeAttribute>());
        Assert.Equal(PermissionCodes.ElectionsManage,authorization.Policy);
    }
}
