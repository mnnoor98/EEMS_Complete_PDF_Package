using EEMS.Modules.Identity.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Identity.Infrastructure;

public sealed class IdentityDbContext(DbContextOptions<IdentityDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<TenantUser> TenantUsers => Set<TenantUser>();
    public DbSet<Role> Roles => Set<Role>();
    public DbSet<Permission> Permissions => Set<Permission>();
    public DbSet<RolePermission> RolePermissions => Set<RolePermission>();
    public DbSet<UserRole> UserRoles => Set<UserRole>();
    public DbSet<PasswordCredential> PasswordCredentials => Set<PasswordCredential>();
    public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("iam");

        var user = modelBuilder.Entity<User>();
        user.ToTable("users"); user.HasKey(x => x.Id); user.Property(x => x.Id).HasColumnName("user_id");
        user.Property(x => x.ExternalSubject).HasColumnName("external_subject").HasMaxLength(200).IsRequired();
        user.Property(x => x.DisplayName).HasColumnName("display_name").HasMaxLength(200).IsRequired();
        user.Property(x => x.Email).HasColumnName("email").HasMaxLength(320);
        user.Property(x => x.IsActive).HasColumnName("is_active"); user.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        user.HasIndex(x => x.ExternalSubject).IsUnique();

        var role = modelBuilder.Entity<Role>();
        role.ToTable("roles"); role.HasKey(x => x.Id); role.Property(x => x.Id).HasColumnName("role_id");
        role.Property(x => x.TenantId).HasColumnName("tenant_id"); role.Property(x => x.Code).HasColumnName("code").HasMaxLength(80);
        role.Property(x => x.Name).HasColumnName("name").HasMaxLength(120); role.Property(x => x.IsActive).HasColumnName("is_active");
        role.Property(x => x.CreatedAtUtc).HasColumnName("created_at"); role.HasIndex(x => new { x.TenantId, x.Code }).IsUnique();

        var permission = modelBuilder.Entity<Permission>();
        permission.ToTable("permissions"); permission.HasKey(x => x.Id); permission.Property(x => x.Id).HasColumnName("permission_id");
        permission.Property(x => x.Code).HasColumnName("code").HasMaxLength(120); permission.Property(x => x.Name).HasColumnName("name").HasMaxLength(160);
        permission.Property(x => x.Module).HasColumnName("module").HasMaxLength(80); permission.Property(x => x.IsActive).HasColumnName("is_active");
        permission.HasIndex(x => x.Code).IsUnique();

        var tenantUser = modelBuilder.Entity<TenantUser>();
        tenantUser.ToTable("tenant_users"); tenantUser.HasKey(x => new { x.TenantId, x.UserId });
        tenantUser.Property(x => x.TenantId).HasColumnName("tenant_id"); tenantUser.Property(x => x.UserId).HasColumnName("user_id");
        tenantUser.Property(x => x.CandidateId).HasColumnName("candidate_id");
        tenantUser.Property(x => x.IsActive).HasColumnName("is_active"); tenantUser.Property(x => x.JoinedAtUtc).HasColumnName("joined_at");
        tenantUser.HasOne<User>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Restrict);

        var rolePermission = modelBuilder.Entity<RolePermission>();
        rolePermission.ToTable("role_permissions"); rolePermission.HasKey(x => new { x.TenantId, x.RoleId, x.PermissionId });
        rolePermission.Property(x => x.TenantId).HasColumnName("tenant_id"); rolePermission.Property(x => x.RoleId).HasColumnName("role_id");
        rolePermission.Property(x => x.PermissionId).HasColumnName("permission_id");
        rolePermission.HasOne<Role>().WithMany().HasForeignKey(x => x.RoleId).OnDelete(DeleteBehavior.Cascade);
        rolePermission.HasOne<Permission>().WithMany().HasForeignKey(x => x.PermissionId).OnDelete(DeleteBehavior.Cascade);

        var userRole = modelBuilder.Entity<UserRole>();
        userRole.ToTable("user_roles"); userRole.HasKey(x => new { x.TenantId, x.UserId, x.RoleId });
        userRole.Property(x => x.TenantId).HasColumnName("tenant_id"); userRole.Property(x => x.UserId).HasColumnName("user_id");
        userRole.Property(x => x.RoleId).HasColumnName("role_id"); userRole.Property(x => x.AssignedAtUtc).HasColumnName("assigned_at");
        userRole.HasOne<User>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
        userRole.HasOne<Role>().WithMany().HasForeignKey(x => x.RoleId).OnDelete(DeleteBehavior.Cascade);

        var credential = modelBuilder.Entity<PasswordCredential>();
        credential.ToTable("password_credentials"); credential.HasKey(x => x.UserId);
        credential.Property(x => x.UserId).HasColumnName("user_id");
        credential.Property(x => x.PasswordHash).HasColumnName("password_hash").HasMaxLength(1000).IsRequired();
        credential.Property(x => x.UpdatedAtUtc).HasColumnName("updated_at");
        credential.Property(x => x.MustChangePassword).HasColumnName("must_change_password");
        credential.Property(x => x.FailedLoginCount).HasColumnName("failed_login_count");
        credential.Property(x => x.LockoutEndUtc).HasColumnName("lockout_end");
        credential.HasOne<User>().WithOne().HasForeignKey<PasswordCredential>(x => x.UserId).OnDelete(DeleteBehavior.Cascade);

        var refreshToken = modelBuilder.Entity<RefreshToken>();
        refreshToken.ToTable("refresh_tokens"); refreshToken.HasKey(x => x.Id);
        refreshToken.Property(x => x.Id).HasColumnName("refresh_token_id");
        refreshToken.Property(x => x.TenantId).HasColumnName("tenant_id");
        refreshToken.Property(x => x.UserId).HasColumnName("user_id");
        refreshToken.Property(x => x.TokenHash).HasColumnName("token_hash").HasMaxLength(64).IsRequired();
        refreshToken.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        refreshToken.Property(x => x.ExpiresAtUtc).HasColumnName("expires_at");
        refreshToken.Property(x => x.RevokedAtUtc).HasColumnName("revoked_at");
        refreshToken.Property(x => x.ReplacedByTokenId).HasColumnName("replaced_by_token_id");
        refreshToken.Ignore(x => x.IsActive);
        refreshToken.HasIndex(x => new { x.TenantId, x.TokenHash }).IsUnique();
        refreshToken.HasOne<User>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
    }
}
