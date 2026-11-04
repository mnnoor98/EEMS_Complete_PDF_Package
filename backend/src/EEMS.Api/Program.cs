using EEMS.Modules.Tenants;
using EEMS.Modules.Tenants.Infrastructure;
using EEMS.Modules.Identity;
using EEMS.Modules.Identity.Infrastructure;
using EEMS.Modules.Geography;
using EEMS.Modules.Geography.Infrastructure;
using EEMS.Modules.Elections;
using EEMS.Modules.Elections.Infrastructure;
using EEMS.Modules.Candidates;
using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Polling;
using EEMS.Modules.Polling.Infrastructure;
using EEMS.Modules.Teams;
using EEMS.Modules.Teams.Infrastructure;
using EEMS.Modules.Events;
using EEMS.Modules.Events.Infrastructure;
using EEMS.Modules.Finance;
using EEMS.Modules.Finance.Infrastructure;
using EEMS.Modules.Inventory;
using EEMS.Modules.Inventory.Infrastructure;
using EEMS.Modules.Operations;using EEMS.Modules.Operations.Infrastructure;
using EEMS.Modules.Results;using EEMS.Modules.Results.Infrastructure;
using EEMS.Modules.Reporting;using EEMS.Modules.Reporting.Infrastructure;
using EEMS.Api.Tenancy;
using EEMS.Api.Authentication;
using EEMS.Api.OpenApi;
using EEMS.Api.Bootstrap;
using EEMS.Api.Security;
using EEMS.Api.Authorization;
using EEMS.Api.ReferenceData;
using Microsoft.EntityFrameworkCore;
using EEMS.Api.Results;
using EEMS.Api.Inventory;
using EEMS.Api.Finance;
using EEMS.Api.Events;
using EEMS.Api.Dashboard;
using EEMS.Api.Audit;
using EEMS.Api.Time;

var builder = WebApplication.CreateBuilder(args);

builder.Logging.ClearProviders();
builder.Logging.AddConsole();

builder.Services.AddProblemDetails();
builder.Services.AddHealthChecks()
    .AddDbContextCheck<TenantsDbContext>()
    .AddDbContextCheck<IdentityDbContext>()
    .AddDbContextCheck<GeographyDbContext>()
    .AddDbContextCheck<ElectionsDbContext>()
    .AddDbContextCheck<CandidatesDbContext>()
    .AddDbContextCheck<PollingDbContext>()
    .AddDbContextCheck<TeamsDbContext>()
    .AddDbContextCheck<EventsDbContext>()
    .AddDbContextCheck<FinanceDbContext>()
    .AddDbContextCheck<InventoryDbContext>().AddDbContextCheck<OperationsDbContext>().AddDbContextCheck<ResultsDbContext>().AddDbContextCheck<ReportingDbContext>();
builder.Services.AddControllers();
builder.Services.AddScoped<ResultsReportingOperationsService>();
builder.Services.AddScoped<InventoryOperationsService>();
builder.Services.AddScoped<FinanceOperationsService>();
builder.Services.AddScoped<EventOperationsService>();
builder.Services.AddScoped<OperationsDashboardService>();
builder.Services.AddScoped<AuditNotificationService>();
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<IBusinessClock,BusinessClock>();
builder.Services.AddApiAuthentication(builder.Configuration, builder.Environment);
builder.Services.AddApiOpenApi();
builder.Services.AddInitialBootstrap(builder.Configuration);
builder.Services.AddApiSecurity(builder.Configuration);
builder.Services.AddPermissionAuthorization(builder.Configuration);
builder.Services.AddReferenceDataSetup(builder.Configuration);
builder.Services.AddTenantsModule(builder.Configuration);
builder.Services.AddIdentityModule(builder.Configuration);
builder.Services.AddGeographyModule(builder.Configuration);
builder.Services.AddElectionsModule(builder.Configuration);
builder.Services.AddCandidatesModule(builder.Configuration);
builder.Services.AddPollingModule(builder.Configuration);
builder.Services.AddTeamsModule(builder.Configuration);
builder.Services.AddEventsModule(builder.Configuration);
builder.Services.AddFinanceModule(builder.Configuration);
builder.Services.AddInventoryModule(builder.Configuration);
builder.Services.AddOperationsModule(builder.Configuration);
builder.Services.AddResultsModule(builder.Configuration);
builder.Services.AddReportingModule(builder.Configuration);

var app = builder.Build();

if (app.Configuration.GetValue<bool>("Database:ApplyMigrations"))
{
    await using var migrationScope = app.Services.CreateAsyncScope();
    var contexts = new DbContext[]
    {
        migrationScope.ServiceProvider.GetRequiredService<TenantsDbContext>(), migrationScope.ServiceProvider.GetRequiredService<IdentityDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<GeographyDbContext>(), migrationScope.ServiceProvider.GetRequiredService<ElectionsDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<CandidatesDbContext>(), migrationScope.ServiceProvider.GetRequiredService<PollingDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<TeamsDbContext>(), migrationScope.ServiceProvider.GetRequiredService<EventsDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<FinanceDbContext>(), migrationScope.ServiceProvider.GetRequiredService<InventoryDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<OperationsDbContext>(), migrationScope.ServiceProvider.GetRequiredService<ResultsDbContext>(),
        migrationScope.ServiceProvider.GetRequiredService<ReportingDbContext>()
    };
    foreach (var context in contexts) await context.Database.MigrateAsync();
}

await app.Services.BootstrapInitialAdminAsync();
await app.Services.InitializeReferenceDataAsync();
await app.Services.InitializePermissionAuthorizationAsync();

app.UseExceptionHandler();
if (!app.Environment.IsDevelopment()) app.UseHsts();
app.UseApiSecurityHeaders();
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
app.UseHttpsRedirection();
app.UseCors(ApiSecurityExtensions.FrontendCorsPolicy);
app.UseRateLimiter();
app.UseAuthentication();
app.UseMiddleware<PasswordChangeMiddleware>();
app.UseAuthorization();
app.UseMiddleware<TenantTransactionMiddleware>();
app.MapControllers();
app.MapHealthChecks("/health/ready");
app.MapHealthChecks("/health/live", new Microsoft.AspNetCore.Diagnostics.HealthChecks.HealthCheckOptions { Predicate = _ => false });

app.Run();

public partial class Program;
