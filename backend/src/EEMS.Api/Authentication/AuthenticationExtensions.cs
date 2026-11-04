using System.Text;
using EEMS.Modules.Identity.Security;
using EEMS.Modules.Identity.Domain;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using EEMS.Api.Administration;
using EEMS.Api.Elections;
using EEMS.Api.Workforce;
using EEMS.Api.Polling;

namespace EEMS.Api.Authentication;

public static class AuthenticationExtensions
{
    public static IServiceCollection AddApiAuthentication(
        this IServiceCollection services,
        IConfiguration configuration,
        IWebHostEnvironment environment)
    {
        var jwt = configuration.GetSection(JwtOptions.SectionName).Get<JwtOptions>() ?? new JwtOptions();

        services.AddOptions<JwtOptions>()
            .Bind(configuration.GetSection(JwtOptions.SectionName))
            .Validate(
                options => environment.IsDevelopment() || IsProductionConfigurationValid(options),
                "JWT issuer, audience, and a signing key of at least 32 characters are required.")
            .ValidateOnStart();
        services.AddScoped<IPasswordHasher<User>, PasswordHasher<User>>();
        services.AddScoped<TokenService>();
        services.AddScoped<LocalAuthenticationService>();
        services.AddScoped<SecurityAuditService>();
        services.AddScoped<IdentityAdministrationService>();
        services.AddScoped<ElectionOperationsService>();
        services.AddScoped<WorkforceOperationsService>();
        services.AddScoped<PollingOperationsService>();
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.MapInboundClaims = false;
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidIssuer = jwt.Issuer,
                    ValidateAudience = true,
                    ValidAudience = jwt.Audience,
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = string.IsNullOrWhiteSpace(jwt.SigningKey)
                        ? null
                        : new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwt.SigningKey)),
                    ValidateLifetime = true,
                    ClockSkew = TimeSpan.FromMinutes(1)
                };
                options.Events = new JwtBearerEvents
                {
                    OnTokenValidated = context =>
                    {
                        var tenantClaim = context.Principal?.FindFirst(IdentityClaimTypes.TenantId)?.Value;
                        if (!Guid.TryParse(tenantClaim, out _))
                        {
                            context.Fail("A valid tenant_id claim is required.");
                        }

                        return Task.CompletedTask;
                    }
                };
            });

        return services;
    }

    private static bool IsProductionConfigurationValid(JwtOptions options) =>
        !string.IsNullOrWhiteSpace(options.Issuer) &&
        !string.IsNullOrWhiteSpace(options.Audience) &&
        options.SigningKey.Length >= 32;
}
