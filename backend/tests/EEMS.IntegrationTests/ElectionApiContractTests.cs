using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace EEMS.IntegrationTests;

public sealed class ElectionApiContractTests
{
    [Theory]
    [InlineData(nameof(ElectionsController.CreateElection), typeof(HttpPostAttribute))]
    [InlineData(nameof(ElectionsController.UpdateElection), typeof(HttpPutAttribute))]
    [InlineData(nameof(ElectionsController.MoveElection), typeof(HttpPutAttribute))]
    public void MutationEndpointsRequireManagePermission(string methodName, Type verbAttribute)
    {
        var method = typeof(ElectionsController).GetMethod(methodName);
        Assert.NotNull(method);
        Assert.NotNull(method.GetCustomAttributes(verbAttribute, true).SingleOrDefault());
        var authorization = Assert.Single(method.GetCustomAttributes(typeof(AuthorizeAttribute), true).Cast<AuthorizeAttribute>());
        Assert.Equal(PermissionCodes.ElectionsManage, authorization.Policy);
    }

    [Fact]
    public void UpdateEndpointUsesElectionIdentifierRoute()
    {
        var method = typeof(ElectionsController).GetMethod(nameof(ElectionsController.UpdateElection));
        var route = Assert.Single(method!.GetCustomAttributes(typeof(HttpPutAttribute), true).Cast<HttpPutAttribute>());
        Assert.Equal("{electionId:guid}", route.Template);
    }
}
