using EEMS.Modules.Tenants.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Tenants.Infrastructure;

public sealed class TenantsDbContext(DbContextOptions<TenantsDbContext> options) : DbContext(options)
{
    public DbSet<Tenant> Tenants => Set<Tenant>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var tenant = modelBuilder.Entity<Tenant>();
        tenant.ToTable("tenants", "core");
        tenant.HasKey(item => item.Id).HasName("pk_tenants");
        tenant.Property(item => item.Id).HasColumnName("tenant_id");
        tenant.Property(item => item.Code).HasColumnName("code").HasMaxLength(40).IsRequired();
        tenant.Property(item => item.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
        tenant.Property(item => item.Status).HasColumnName("status").HasConversion<string>().HasMaxLength(20).IsRequired();
        tenant.Property(item => item.CreatedAtUtc).HasColumnName("created_at").IsRequired();
        tenant.HasIndex(item => item.Code).IsUnique().HasDatabaseName("ux_tenants_code");
    }
}
