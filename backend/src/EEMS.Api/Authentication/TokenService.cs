using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Security;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;

namespace EEMS.Api.Authentication;

public sealed class TokenService(IOptions<JwtOptions> options)
{
    private readonly JwtOptions _options = options.Value;

    public (string Token, DateTimeOffset ExpiresAtUtc) CreateAccessToken(
        User user,
        Guid tenantId,
        IReadOnlyCollection<string> permissions,
        bool passwordChangeRequired)
    {
        EnsureSigningKey();
        var expiresAt = DateTimeOffset.UtcNow.AddMinutes(_options.AccessTokenMinutes);
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Name, user.DisplayName),
            new(IdentityClaimTypes.TenantId, tenantId.ToString()),
            new(IdentityClaimTypes.PasswordChangeRequired, passwordChangeRequired.ToString().ToLowerInvariant())
        };
        claims.AddRange(permissions.Select(permission => new Claim(IdentityClaimTypes.Permission, permission)));

        var credentials = new SigningCredentials(
            new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_options.SigningKey)),
            SecurityAlgorithms.HmacSha256);
        var token = new JwtSecurityToken(
            _options.Issuer,
            _options.Audience,
            claims,
            DateTime.UtcNow,
            expiresAt.UtcDateTime,
            credentials);

        return (new JwtSecurityTokenHandler().WriteToken(token), expiresAt);
    }

    public (RefreshToken Entity, string RawToken) CreateRefreshToken(Guid tenantId, Guid userId)
    {
        var rawToken = Base64UrlEncoder.Encode(RandomNumberGenerator.GetBytes(64));
        var entity = RefreshToken.Create(
            tenantId,
            userId,
            HashRefreshToken(rawToken),
            DateTimeOffset.UtcNow.AddDays(_options.RefreshTokenDays));
        return (entity, rawToken);
    }

    public static string HashRefreshToken(string rawToken) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(rawToken)));

    private void EnsureSigningKey()
    {
        if (_options.SigningKey.Length < 32)
        {
            throw new InvalidOperationException("JWT signing key must contain at least 32 characters.");
        }
    }
}
