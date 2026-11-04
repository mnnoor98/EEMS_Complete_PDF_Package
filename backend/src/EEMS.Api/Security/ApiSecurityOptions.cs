namespace EEMS.Api.Security;

public sealed class ApiSecurityOptions
{
    public const string SectionName = "Security";

    public int AuthenticationPermitLimit { get; init; } = 10;
    public int AuthenticationWindowSeconds { get; init; } = 60;
    public int AuthenticationQueueLimit { get; init; }
    public string[] AllowedOrigins { get; init; } = [];
}
