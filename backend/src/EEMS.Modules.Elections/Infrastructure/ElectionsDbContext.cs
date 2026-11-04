using EEMS.Modules.Elections.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Elections.Infrastructure;

public sealed class ElectionsDbContext(DbContextOptions<ElectionsDbContext> options):DbContext(options)
{
    public DbSet<ElectionType> ElectionTypes=>Set<ElectionType>(); public DbSet<Position> Positions=>Set<Position>();
    public DbSet<ElectionLifecycleState> LifecycleStates=>Set<ElectionLifecycleState>(); public DbSet<Election> Elections=>Set<Election>();
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("election");
        var type=modelBuilder.Entity<ElectionType>();type.ToTable("election_types");type.HasKey(x=>x.Id);type.Property(x=>x.Id).HasColumnName("election_type_id").ValueGeneratedNever();type.Property(x=>x.Code).HasColumnName("code").HasMaxLength(40);type.Property(x=>x.Name).HasColumnName("name").HasMaxLength(120);type.Property(x=>x.IsActive).HasColumnName("is_active");type.HasIndex(x=>x.Code).IsUnique();
        var pos=modelBuilder.Entity<Position>();pos.ToTable("positions");pos.HasKey(x=>x.Id);pos.Property(x=>x.Id).HasColumnName("position_id").ValueGeneratedNever();pos.Property(x=>x.ElectionTypeId).HasColumnName("election_type_id");pos.Property(x=>x.Code).HasColumnName("code").HasMaxLength(60);pos.Property(x=>x.Name).HasColumnName("name").HasMaxLength(120);pos.Property(x=>x.IsActive).HasColumnName("is_active");pos.HasIndex(x=>new{x.ElectionTypeId,x.Code}).IsUnique();pos.HasOne<ElectionType>().WithMany().HasForeignKey(x=>x.ElectionTypeId).OnDelete(DeleteBehavior.Restrict);
        var state=modelBuilder.Entity<ElectionLifecycleState>();state.ToTable("lifecycle_states");state.HasKey(x=>x.Id);state.Property(x=>x.Id).HasColumnName("lifecycle_state_id").ValueGeneratedNever();state.Property(x=>x.Code).HasColumnName("code").HasMaxLength(40);state.Property(x=>x.Name).HasColumnName("name").HasMaxLength(100);state.Property(x=>x.IsTerminal).HasColumnName("is_terminal");state.Property(x=>x.IsActive).HasColumnName("is_active");state.HasIndex(x=>x.Code).IsUnique();
        var election=modelBuilder.Entity<Election>();election.ToTable("elections");election.HasKey(x=>x.Id);election.Property(x=>x.Id).HasColumnName("election_id");election.Property(x=>x.TenantId).HasColumnName("tenant_id");election.Property(x=>x.ElectionTypeId).HasColumnName("election_type_id");election.Property(x=>x.AreaId).HasColumnName("area_id");election.Property(x=>x.LifecycleStateId).HasColumnName("lifecycle_state_id");election.Property(x=>x.Name).HasColumnName("name").HasMaxLength(200);election.Property(x=>x.ElectionDate).HasColumnName("election_date");election.Property(x=>x.CreatedAtUtc).HasColumnName("created_at");election.Property(x=>x.Version).HasColumnName("version").IsConcurrencyToken();election.HasIndex(x=>new{x.TenantId,x.ElectionDate});election.HasOne<ElectionType>().WithMany().HasForeignKey(x=>x.ElectionTypeId).OnDelete(DeleteBehavior.Restrict);election.HasOne<ElectionLifecycleState>().WithMany().HasForeignKey(x=>x.LifecycleStateId).OnDelete(DeleteBehavior.Restrict);
    }
}
