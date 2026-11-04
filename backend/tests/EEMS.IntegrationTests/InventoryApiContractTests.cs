using EEMS.Api.Authorization;
using EEMS.Api.Controllers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Xunit;

namespace EEMS.IntegrationTests;
public sealed class InventoryApiContractTests
{
    [Theory]
    [InlineData(nameof(InventoryController.CreateWarehouse))]
    [InlineData(nameof(InventoryController.CreateItem))]
    [InlineData(nameof(InventoryController.RecordMovement))]
    [InlineData(nameof(InventoryController.CreateAllocation))]
    [InlineData(nameof(InventoryController.Acknowledge))]
    public void MutationsRequireInventoryManage(string method)
    {
        var info=typeof(InventoryController).GetMethod(method)!;
        Assert.Equal(PermissionCodes.InventoryManage,info.GetCustomAttributes(typeof(AuthorizeAttribute),false).Cast<AuthorizeAttribute>().Single().Policy);
        Assert.True(info.IsDefined(typeof(HttpPostAttribute),false)||info.IsDefined(typeof(HttpPutAttribute),false));
    }
}
