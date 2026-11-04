using EEMS.Modules.Geography.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Geography.Infrastructure;

public sealed class GeographyDbContext(DbContextOptions<GeographyDbContext> options) : DbContext(options)
{
    public DbSet<AreaType> AreaTypes => Set<AreaType>();
    public DbSet<Area> Areas => Set<Area>();
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("geo");
        var type=modelBuilder.Entity<AreaType>(); type.ToTable("area_types"); type.HasKey(x=>x.Id);
        type.Property(x=>x.Id).HasColumnName("area_type_id").ValueGeneratedNever(); type.Property(x=>x.Code).HasColumnName("code").HasMaxLength(40);
        type.Property(x=>x.Name).HasColumnName("name").HasMaxLength(120); type.Property(x=>x.Level).HasColumnName("level"); type.Property(x=>x.IsActive).HasColumnName("is_active");
        type.HasIndex(x=>x.Code).IsUnique(); type.HasIndex(x=>x.Level).IsUnique();
        var area=modelBuilder.Entity<Area>(); area.ToTable("areas"); area.HasKey(x=>x.Id);
        area.Property(x=>x.Id).HasColumnName("area_id").ValueGeneratedNever(); area.Property(x=>x.ParentAreaId).HasColumnName("parent_area_id");
        area.Property(x=>x.AreaTypeId).HasColumnName("area_type_id"); area.Property(x=>x.Code).HasColumnName("code").HasMaxLength(40);
        area.Property(x=>x.NameBn).HasColumnName("name_bn").HasMaxLength(200); area.Property(x=>x.NameEn).HasColumnName("name_en").HasMaxLength(200);
        area.Property(x=>x.IsActive).HasColumnName("is_active"); area.HasIndex(x=>new{x.AreaTypeId,x.Code}).IsUnique(); area.HasIndex(x=>x.ParentAreaId);
        area.HasOne<AreaType>().WithMany().HasForeignKey(x=>x.AreaTypeId).OnDelete(DeleteBehavior.Restrict);
        area.HasOne<Area>().WithMany().HasForeignKey(x=>x.ParentAreaId).OnDelete(DeleteBehavior.Restrict);
    }
}
