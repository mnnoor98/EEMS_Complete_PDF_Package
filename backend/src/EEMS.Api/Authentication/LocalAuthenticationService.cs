using EEMS.Modules.Candidates.Infrastructure;
using EEMS.Modules.Identity.Domain;
using EEMS.Modules.Identity.Infrastructure;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace EEMS.Api.Authentication;

public sealed class LocalAuthenticationService(
    IdentityDbContext dbContext,
    CandidatesDbContext candidatesDbContext,
    IPasswordHasher<User> passwordHasher,
    TokenService tokenService,
    IOptions<JwtOptions> jwtOptions,
    SecurityAuditService securityAudit)
{
    private readonly JwtOptions _jwtOptions = jwtOptions.Value;

    public async Task<TokenPair?> LoginAsync(Guid tenantId, string username, string password, CancellationToken cancellationToken)
    {
        var ownsTransaction = dbContext.Database.CurrentTransaction == null;
        var transaction = ownsTransaction ? await dbContext.Database.BeginTransactionAsync(cancellationToken) : null;
        try
        {
            await SetTenantAsync(tenantId, cancellationToken);

            var normalizedUsername = username.Trim();
            var user = await dbContext.Users.SingleOrDefaultAsync(
                candidate => candidate.ExternalSubject == normalizedUsername && candidate.IsActive,
                cancellationToken);
            if (user is null || !await IsActiveTenantUserAsync(tenantId, user.Id, cancellationToken)) return null;

            var credential = await dbContext.PasswordCredentials.SingleOrDefaultAsync(
                item => item.UserId == user.Id,
                cancellationToken);
            if (credential is null || credential.IsLockedOut(DateTimeOffset.UtcNow)) return null;

            var verification = passwordHasher.VerifyHashedPassword(user, credential.PasswordHash, password);
            if (verification == PasswordVerificationResult.Failed)
            {
                credential.RecordFailedLogin(
                    _jwtOptions.MaximumFailedLoginAttempts,
                    DateTimeOffset.UtcNow.AddMinutes(_jwtOptions.LockoutMinutes));
                await dbContext.SaveChangesAsync(cancellationToken);
                if (transaction != null) await transaction.CommitAsync(cancellationToken);
                await securityAudit.RecordAsync(
                    tenantId,
                    user.Id,
                    credential.IsLockedOut(DateTimeOffset.UtcNow) ? "login_locked" : "login_failed",
                    "Local password authentication failed.",
                    cancellationToken);
                return null;
            }
            credential.RecordSuccessfulLogin();
            if (verification == PasswordVerificationResult.SuccessRehashNeeded)
            {
                credential.ChangePassword(passwordHasher.HashPassword(user, password));
            }

            var result = await IssueTokenPairAsync(tenantId, user, credential.MustChangePassword, cancellationToken);
            await dbContext.SaveChangesAsync(cancellationToken);
            if (transaction != null) await transaction.CommitAsync(cancellationToken);
            await securityAudit.RecordAsync(
                tenantId,
                user.Id,
                "login_succeeded",
                "Local password authentication succeeded.",
                cancellationToken);
            return result;
        }
        finally
        {
            if (transaction != null) await transaction.DisposeAsync();
        }
    }

    public async Task<TokenPair?> RefreshAsync(Guid tenantId, string rawRefreshToken, CancellationToken cancellationToken)
    {
        var ownsTransaction = dbContext.Database.CurrentTransaction == null;
        var transaction = ownsTransaction ? await dbContext.Database.BeginTransactionAsync(cancellationToken) : null;
        try
        {
            await SetTenantAsync(tenantId, cancellationToken);

            var hash = TokenService.HashRefreshToken(rawRefreshToken);
            var current = await dbContext.RefreshTokens.SingleOrDefaultAsync(
                token => token.TenantId == tenantId && token.TokenHash == hash,
                cancellationToken);
            if (current is null || !current.IsActive) return null;

            var user = await dbContext.Users.SingleOrDefaultAsync(
                candidate => candidate.Id == current.UserId && candidate.IsActive,
                cancellationToken);
            if (user is null || !await IsActiveTenantUserAsync(tenantId, user.Id, cancellationToken)) return null;

            var credential = await dbContext.PasswordCredentials.SingleOrDefaultAsync(
                item => item.UserId == user.Id,
                cancellationToken);
            if (credential is null) return null;

            var result = await IssueTokenPairAsync(tenantId, user, credential.MustChangePassword, cancellationToken);
            await dbContext.SaveChangesAsync(cancellationToken);
            current.Revoke(result.RefreshTokenId);
            await dbContext.SaveChangesAsync(cancellationToken);
            if (transaction != null) await transaction.CommitAsync(cancellationToken);
            return result;
        }
        finally
        {
            if (transaction != null) await transaction.DisposeAsync();
        }
    }

    public async Task LogoutAsync(Guid tenantId, Guid userId, string rawRefreshToken, CancellationToken cancellationToken)
    {
        var hash = TokenService.HashRefreshToken(rawRefreshToken);
        var token = await dbContext.RefreshTokens.SingleOrDefaultAsync(
            item => item.TenantId == tenantId && item.UserId == userId && item.TokenHash == hash,
            cancellationToken);
        if (token is null) return;
        token.Revoke();
        await dbContext.SaveChangesAsync(cancellationToken);
    }

    public async Task<bool> ChangePasswordAsync(
        Guid tenantId,
        Guid userId,
        string currentPassword,
        string newPassword,
        CancellationToken cancellationToken)
    {
        var user = await dbContext.Users.SingleOrDefaultAsync(
            candidate => candidate.Id == userId && candidate.IsActive,
            cancellationToken);
        var credential = await dbContext.PasswordCredentials.SingleOrDefaultAsync(
            item => item.UserId == userId,
            cancellationToken);
        if (user is null || credential is null) return false;
        if (passwordHasher.VerifyHashedPassword(user, credential.PasswordHash, currentPassword) == PasswordVerificationResult.Failed)
            return false;

        credential.ChangePassword(passwordHasher.HashPassword(user, newPassword));
        var activeTokens = await dbContext.RefreshTokens
            .Where(token => token.TenantId == tenantId && token.UserId == userId && token.RevokedAtUtc == null)
            .ToListAsync(cancellationToken);
        foreach (var token in activeTokens) token.Revoke();
        await dbContext.SaveChangesAsync(cancellationToken);
        await securityAudit.RecordAsync(
            tenantId,
            userId,
            "password_changed",
            "Password changed and active refresh tokens revoked.",
            cancellationToken);
        return true;
    }

    private async Task<TokenPair> IssueTokenPairAsync(
        Guid tenantId,
        User user,
        bool passwordChangeRequired,
        CancellationToken cancellationToken)
    {
        var tenantUser = await dbContext.TenantUsers.SingleOrDefaultAsync(
            tu => tu.TenantId == tenantId && tu.UserId == user.Id,
            cancellationToken);

        Guid? candidateId = tenantUser?.CandidateId;
        string? candidateName = null;
        Guid? candidateElectionId = null;

        if (candidateId.HasValue)
        {
            var ownsTx = candidatesDbContext.Database.CurrentTransaction == null;
            var tx = ownsTx ? await candidatesDbContext.Database.BeginTransactionAsync(cancellationToken) : null;
            try
            {
                await candidatesDbContext.Database.ExecuteSqlInterpolatedAsync(
                    $"SELECT set_config('app.tenant_id', {tenantId.ToString()}, true)",
                    cancellationToken);
                var candidate = await candidatesDbContext.Candidates
                    .AsNoTracking()
                    .SingleOrDefaultAsync(c => c.TenantId == tenantId && c.Id == candidateId.Value, cancellationToken);
                candidateName = candidate?.Name;

                var ce = await candidatesDbContext.CandidateElections
                    .AsNoTracking()
                    .FirstOrDefaultAsync(x => x.TenantId == tenantId && x.CandidateId == candidateId.Value && x.IsActive, cancellationToken);
                candidateElectionId = ce?.ElectionId;
                if (tx != null) await tx.CommitAsync(cancellationToken);
            }
            finally
            {
                if (tx != null) await tx.DisposeAsync();
            }
        }

        var permissions = await (
            from userRole in dbContext.UserRoles
            join role in dbContext.Roles on userRole.RoleId equals role.Id
            join rolePermission in dbContext.RolePermissions on role.Id equals rolePermission.RoleId
            join permission in dbContext.Permissions on rolePermission.PermissionId equals permission.Id
            where userRole.TenantId == tenantId && userRole.UserId == user.Id && role.IsActive && permission.IsActive
            select permission.Code)
            .Distinct()
            .ToListAsync(cancellationToken);

        var access = tokenService.CreateAccessToken(user, tenantId, permissions, passwordChangeRequired, candidateId, candidateName, candidateElectionId);
        var refresh = tokenService.CreateRefreshToken(tenantId, user.Id);
        dbContext.RefreshTokens.Add(refresh.Entity);
        return new TokenPair(
            access.Token,
            access.ExpiresAtUtc,
            refresh.RawToken,
            refresh.Entity.ExpiresAtUtc,
            refresh.Entity.Id,
            passwordChangeRequired,
            candidateId,
            candidateName,
            !candidateId.HasValue,
            candidateElectionId);
    }

    private Task<bool> IsActiveTenantUserAsync(Guid tenantId, Guid userId, CancellationToken cancellationToken) =>
        dbContext.TenantUsers.AnyAsync(
            tenantUser => tenantUser.TenantId == tenantId && tenantUser.UserId == userId && tenantUser.IsActive,
            cancellationToken);

    private Task<int> SetTenantAsync(Guid tenantId, CancellationToken cancellationToken) =>
        dbContext.Database.ExecuteSqlInterpolatedAsync(
            $"SELECT set_config('app.tenant_id', {tenantId.ToString()}, true)",
            cancellationToken);
}

public sealed record TokenPair(
    string AccessToken,
    DateTimeOffset AccessTokenExpiresAtUtc,
    string RefreshToken,
    DateTimeOffset RefreshTokenExpiresAtUtc,
    Guid RefreshTokenId,
    bool PasswordChangeRequired,
    Guid? CandidateId = null,
    string? CandidateName = null,
    bool IsSuperAdmin = true,
    Guid? CandidateElectionId = null);
