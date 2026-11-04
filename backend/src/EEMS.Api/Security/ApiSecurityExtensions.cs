using System.Globalization;
using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Options;

namespace EEMS.Api.Security;

public static class ApiSecurityExtensions
{
    public const string AuthenticationRateLimitPolicy = "authentication";
    public const string FrontendCorsPolicy = "frontend";

    public static IServiceCollection AddApiSecurity(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddOptions<ApiSecurityOptions>()
            .Bind(configuration.GetSection(ApiSecurityOptions.SectionName))
            .Validate(options => options.AuthenticationPermitLimit > 0, "Authentication permit limit must be positive.")
            .Validate(options => options.AuthenticationWindowSeconds > 0, "Authentication window must be positive.")
            .Validate(options => options.AuthenticationQueueLimit >= 0, "Authentication queue limit cannot be negative.")
            .ValidateOnStart();

        var options = configuration.GetSection(ApiSecurityOptions.SectionName).Get<ApiSecurityOptions>() ?? new ApiSecurityOptions();
        services.AddRateLimiter(rateLimiter =>
        {
            rateLimiter.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
            rateLimiter.OnRejected = async (context, cancellationToken) =>
            {
                if (context.Lease.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter))
                {
                    context.HttpContext.Response.Headers.RetryAfter =
                        Math.Ceiling(retryAfter.TotalSeconds).ToString(CultureInfo.InvariantCulture);
                }
                await context.HttpContext.Response.WriteAsJsonAsync(
                    new { error = "rate_limit_exceeded" },
                    cancellationToken);
            };
            rateLimiter.AddPolicy(AuthenticationRateLimitPolicy, httpContext =>
                RateLimitPartition.GetFixedWindowLimiter(
                    httpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    _ => new FixedWindowRateLimiterOptions
                    {
                        PermitLimit = options.AuthenticationPermitLimit,
                        Window = TimeSpan.FromSeconds(options.AuthenticationWindowSeconds),
                        QueueLimit = options.AuthenticationQueueLimit,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        AutoReplenishment = true
                    }));
        });

        services.AddCors(cors => cors.AddPolicy(FrontendCorsPolicy, policy =>
        {
            if (options.AllowedOrigins.Length > 0)
            {
                policy.WithOrigins(options.AllowedOrigins)
                    .AllowAnyHeader()
                    .AllowAnyMethod();
            }
        }));
        return services;
    }

    public static IApplicationBuilder UseApiSecurityHeaders(this IApplicationBuilder app) =>
        app.Use(async (context, next) =>
        {
            context.Response.OnStarting(() =>
            {
                context.Response.Headers.XContentTypeOptions = "nosniff";
                context.Response.Headers.XFrameOptions = "DENY";
                context.Response.Headers["Referrer-Policy"] = "no-referrer";
                context.Response.Headers.ContentSecurityPolicy = "default-src 'none'; frame-ancestors 'none'";
                context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
                return Task.CompletedTask;
            });
            await next();
        });
}
