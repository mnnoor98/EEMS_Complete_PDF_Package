namespace EEMS.Api.Authorization;

public sealed class AuthorizationOptions
{
    public const string SectionName = "AuthorizationSetup";
    public string InitialTenantCode { get; init; } = string.Empty;
    public string InitialAdministratorUsername { get; init; } = string.Empty;
    public string AdministratorRoleCode { get; init; } = string.Empty;
    public string AdministratorRoleName { get; init; } = string.Empty;
    public PermissionDefinition[] Permissions { get; init; } = [];
}

public sealed class PermissionDefinition
{
    public string Code { get; init; } = string.Empty;
    public string Name { get; init; } = string.Empty;
    public string Module { get; init; } = string.Empty;
}
