using EEMS.Modules.Elections.Domain;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Geography.Domain;
using EEMS.Modules.Geography.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using EEMS.Modules.Teams.Domain;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.Modules.Operations.Domain;
using EEMS.Modules.Operations.Infrastructure;
using EEMS.Modules.Results.Domain;
using EEMS.Modules.Results.Infrastructure;
using EEMS.Modules.Reporting.Domain;
using EEMS.Modules.Reporting.Infrastructure;
using EEMS.Modules.Inventory.Domain;
using EEMS.Modules.Inventory.Infrastructure;
using EEMS.Modules.Finance.Domain;
using EEMS.Modules.Finance.Infrastructure;
using EEMS.Modules.Events.Domain;
using EEMS.Modules.Events.Infrastructure;

namespace EEMS.Api.ReferenceData;

public static class ReferenceDataExtensions
{
    public static IServiceCollection AddReferenceDataSetup(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddOptions<ReferenceDataOptions>()
            .Bind(configuration.GetSection(ReferenceDataOptions.SectionName))
            .Validate(IsValid, "Reference-data definitions must have positive IDs and non-empty codes and names.")
            .ValidateOnStart();
        return services;
    }

    public static async Task InitializeReferenceDataAsync(this IServiceProvider services, CancellationToken token = default)
    {
        await using var scope = services.CreateAsyncScope();
        var options = scope.ServiceProvider.GetRequiredService<IOptions<ReferenceDataOptions>>().Value;
        var geography = scope.ServiceProvider.GetRequiredService<GeographyDbContext>();
        foreach (var definition in options.AreaTypes.OrderBy(item => item.Level))
            if (!await geography.AreaTypes.AnyAsync(item => item.Id == definition.Id, token))
                geography.AreaTypes.Add(AreaType.Create(definition.Id, definition.Code, definition.Name, definition.Level));
        await geography.SaveChangesAsync(token);

        foreach (var definition in options.Areas)
        {
            var parentAreaId = definition.ParentAreaId is > 0 ? definition.ParentAreaId : null;
            if (parentAreaId is null)
            {
                await geography.Database.ExecuteSqlInterpolatedAsync($"""
                    INSERT INTO geo.areas (area_id, parent_area_id, area_type_id, code, name_bn, name_en, is_active)
                    VALUES ({definition.Id}, NULL, {definition.AreaTypeId}, {definition.Code.ToUpperInvariant()},
                            {definition.NameBn}, {definition.NameEn}, TRUE)
                    ON CONFLICT (area_id) DO NOTHING
                    """, token);
            }
            else
            {
                await geography.Database.ExecuteSqlInterpolatedAsync($"""
                    INSERT INTO geo.areas (area_id, parent_area_id, area_type_id, code, name_bn, name_en, is_active)
                    VALUES ({definition.Id}, {parentAreaId.Value}, {definition.AreaTypeId}, {definition.Code.ToUpperInvariant()},
                            {definition.NameBn}, {definition.NameEn}, TRUE)
                    ON CONFLICT (area_id) DO NOTHING
                    """, token);
            }
        }

        var elections = scope.ServiceProvider.GetRequiredService<ElectionsDbContext>();
        foreach (var definition in options.ElectionTypes)
            if (!await elections.ElectionTypes.AnyAsync(item => item.Id == definition.Id, token))
                elections.ElectionTypes.Add(ElectionType.Create(definition.Id, definition.Code, definition.Name));
        foreach (var definition in options.LifecycleStates)
            if (!await elections.LifecycleStates.AnyAsync(item => item.Id == definition.Id, token))
                elections.LifecycleStates.Add(ElectionLifecycleState.Create(definition.Id, definition.Code, definition.Name, definition.IsTerminal));
        await elections.SaveChangesAsync(token);

        foreach (var definition in options.Positions)
            if (!await elections.Positions.AnyAsync(item => item.Id == definition.Id, token))
                elections.Positions.Add(Position.Create(definition.Id, definition.ElectionTypeId, definition.Code, definition.Name));
        await elections.SaveChangesAsync(token);

        var teams = scope.ServiceProvider.GetRequiredService<TeamsDbContext>();
        foreach (var definition in options.TaskStates)
            if (!await teams.TaskStates.AnyAsync(item => item.Id == definition.Id, token))
                teams.TaskStates.Add(TaskState.Create(definition.Id, definition.Code, definition.Name, definition.IsTerminal));
        foreach (var definition in options.TaskPriorities)
            if (!await teams.TaskPriorities.AnyAsync(item => item.Id == definition.Id, token))
                teams.TaskPriorities.Add(TaskPriority.Create(definition.Id, definition.Code, definition.Name, definition.Rank));
        await teams.SaveChangesAsync(token);

        var operations = scope.ServiceProvider.GetRequiredService<OperationsDbContext>();
        foreach (var definition in options.ReadinessStates)
            if (!await operations.ReadinessStates.AnyAsync(item => item.Id == definition.Id, token))
                operations.ReadinessStates.Add(ReadinessState.Create(definition.Id, definition.Code, definition.Name, definition.Rank));
        await operations.SaveChangesAsync(token);

        var results = scope.ServiceProvider.GetRequiredService<ResultsDbContext>();
        foreach (var definition in options.SubmissionStates)
            if (!await results.States.AnyAsync(item => item.Id == definition.Id, token))
                results.States.Add(SubmissionState.Create(definition.Id, definition.Code, definition.Name, definition.IsVerified));
        await results.SaveChangesAsync(token);

        var reporting = scope.ServiceProvider.GetRequiredService<ReportingDbContext>();
        foreach (var definition in options.ExportStates)
            if (!await reporting.ExportStates.AnyAsync(item => item.Id == definition.Id, token))
                reporting.ExportStates.Add(ExportState.Create(definition.Id, definition.Code, definition.Name, definition.IsTerminal));
        await reporting.SaveChangesAsync(token);

        var inventory = scope.ServiceProvider.GetRequiredService<InventoryDbContext>();
        foreach (var definition in options.MovementTypes)
            if (!await inventory.MovementTypes.AnyAsync(item => item.Id == definition.Id, token))
                inventory.MovementTypes.Add(MovementType.Create(definition.Id, definition.Code, definition.Name, definition.RequiresSource, definition.RequiresDestination));
        foreach (var definition in options.AllocationStates)
            if (!await inventory.AllocationStates.AnyAsync(item => item.Id == definition.Id, token))
                inventory.AllocationStates.Add(AllocationState.Create(definition.Id, definition.Code, definition.Name, definition.IsTerminal));
        await inventory.SaveChangesAsync(token);

        var finance = scope.ServiceProvider.GetRequiredService<FinanceDbContext>();
        foreach (var definition in options.ExpenseStates)
            if (!await finance.ExpenseStates.AnyAsync(item => item.Id == definition.Id, token))
                finance.ExpenseStates.Add(ExpenseState.Create(definition.Id, definition.Code, definition.Name, definition.IsApproved, definition.IsTerminal));
        await finance.SaveChangesAsync(token);
        var eventDb = scope.ServiceProvider.GetRequiredService<EventsDbContext>();
        foreach(var x in options.EventTypes)if(!await eventDb.EventTypes.AnyAsync(y=>y.Id==x.Id,token))eventDb.EventTypes.Add(EventType.Create(x.Id,x.Code,x.Name));
        foreach(var x in options.EventStates)if(!await eventDb.EventStates.AnyAsync(y=>y.Id==x.Id,token))eventDb.EventStates.Add(EventState.Create(x.Id,x.Code,x.Name,x.IsTerminal));
        foreach(var x in options.PermitStates)if(!await eventDb.PermitStates.AnyAsync(y=>y.Id==x.Id,token))eventDb.PermitStates.Add(PermitState.Create(x.Id,x.Code,x.Name));
        await eventDb.SaveChangesAsync(token);
    }

    private static bool IsValid(ReferenceDataOptions options) =>
        options.ElectionTypes.Length > 0 && options.LifecycleStates.Length > 0 && options.TaskStates.Length > 0 && options.TaskPriorities.Length > 0 && options.ReadinessStates.Length > 0 && options.SubmissionStates.Length > 0 && options.ExportStates.Length > 0 && options.MovementTypes.Length > 0 && options.AllocationStates.Length > 0 && options.ExpenseStates.Length > 0 && options.EventTypes.Length > 0 && options.EventStates.Length > 0 && options.PermitStates.Length > 0 &&
        options.Positions.Length > 0 && options.AreaTypes.Length > 0 && options.Areas.Length > 0 &&
        options.ElectionTypes.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.LifecycleStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.TaskStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.TaskPriorities.All(item => item.Id > 0 && item.Rank > 0 && HasText(item.Code, item.Name)) &&
        options.ReadinessStates.All(item => item.Id > 0 && item.Rank > 0 && HasText(item.Code, item.Name)) &&
        options.SubmissionStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) && options.ExportStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.MovementTypes.All(item => item.Id > 0 && (item.RequiresSource || item.RequiresDestination) && HasText(item.Code, item.Name)) && options.AllocationStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.ExpenseStates.All(item => item.Id > 0 && HasText(item.Code, item.Name)) &&
        options.EventTypes.All(item=>item.Id>0&&HasText(item.Code,item.Name)) && options.EventStates.All(item=>item.Id>0&&HasText(item.Code,item.Name)) && options.PermitStates.All(item=>item.Id>0&&HasText(item.Code,item.Name)) &&
        options.Positions.All(item => item.Id > 0 && item.ElectionTypeId > 0 && HasText(item.Code, item.Name)) &&
        options.AreaTypes.All(item => item.Id > 0 && item.Level > 0 && HasText(item.Code, item.Name)) &&
        options.Areas.All(item => item.Id > 0 && item.AreaTypeId > 0 && HasText(item.Code, item.NameBn));

    private static bool HasText(string first, string second) =>
        !string.IsNullOrWhiteSpace(first) && !string.IsNullOrWhiteSpace(second);
}
