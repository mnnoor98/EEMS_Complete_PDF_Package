namespace EEMS.Api.Bootstrap;

public sealed class BootstrapOptions
{
    public const string SectionName = "Bootstrap";

    public bool Enabled { get; init; }
    public string TenantCode { get; init; } = string.Empty;
    public string TenantName { get; init; } = string.Empty;
    public string AdminUsername { get; init; } = string.Empty;
    public string AdminDisplayName { get; init; } = string.Empty;
    public string? AdminEmail { get; init; }
    public string AdminPassword { get; init; } = string.Empty;
}
