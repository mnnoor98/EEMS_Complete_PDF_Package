using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class AdministrationApiContractTests
{
    [Theory]
    [InlineData(nameof(AdministrationController.CreateUser), PermissionCodes.UsersManage, typeof(HttpPostAttribute))]
    [InlineData(nameof(AdministrationController.SetUserActive), PermissionCodes.UsersManage, typeof(HttpPutAttribute))]
    [InlineData(nameof(AdministrationController.AssignRole), PermissionCodes.RolesManage, typeof(HttpPostAttribute))]
    [InlineData(nameof(AdministrationController.CreateRole), PermissionCodes.RolesManage, typeof(HttpPostAttribute))]
    [InlineData(nameof(AdministrationController.AssignPermission), PermissionCodes.RolesManage, typeof(HttpPostAttribute))]
    public void MutationEndpointsRequireExpectedPermission(string methodName, string policy, Type verbAttribute)
    {
        var method = typeof(AdministrationController).GetMethod(methodName);
        Assert.NotNull(method);
        Assert.NotNull(method.GetCustomAttributes(verbAttribute, true).SingleOrDefault());
        var authorization = Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute), true).Cast<AuthorizeAttribute>());
        Assert.Equal(policy, authorization.Policy);
    }
}
