using EEMS.Modules.Candidates.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Candidates.Infrastructure;

public sealed class CandidatesDbContext(DbContextOptions<CandidatesDbContext> options) : DbContext(options)
{
    public DbSet<Candidate> Candidates => Set<Candidate>();
    public DbSet<CandidateElection> CandidateElections => Set<CandidateElection>();
    public DbSet<ElectionSymbol> Symbols => Set<ElectionSymbol>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("election");

        var symbol = modelBuilder.Entity<ElectionSymbol>();
        symbol.ToTable("symbols");
        symbol.HasKey(x => x.Id);
        symbol.Property(x => x.Id).HasColumnName("symbol_id");
        symbol.Property(x => x.Code).HasColumnName("code").HasMaxLength(40);
        symbol.Property(x => x.NameBn).HasColumnName("name_bn").HasMaxLength(100);
        symbol.Property(x => x.NameEn).HasColumnName("name_en").HasMaxLength(100);
        symbol.Property(x => x.Category).HasColumnName("category").HasMaxLength(40);
        symbol.Property(x => x.IconEmoji).HasColumnName("icon_emoji").HasMaxLength(20);
        symbol.Property(x => x.IsActive).HasColumnName("is_active");
        symbol.HasIndex(x => x.Code).IsUnique();

        var candidate = modelBuilder.Entity<Candidate>();
        candidate.ToTable("candidates");
        candidate.HasKey(x => x.Id);
        candidate.Property(x => x.Id).HasColumnName("candidate_id");
        candidate.Property(x => x.TenantId).HasColumnName("tenant_id");
        candidate.Property(x => x.Name).HasColumnName("name").HasMaxLength(200);
        candidate.Property(x => x.ExternalReference).HasColumnName("external_reference").HasMaxLength(100);
        candidate.Property(x => x.SymbolId).HasColumnName("symbol_id");
        candidate.Property(x => x.PartyNameBn).HasColumnName("party_name_bn").HasMaxLength(150);
        candidate.Property(x => x.PartyNameEn).HasColumnName("party_name_en").HasMaxLength(150);
        candidate.Property(x => x.Slogan).HasColumnName("slogan").HasMaxLength(300);
        candidate.Property(x => x.Phone).HasColumnName("phone").HasMaxLength(30);
        candidate.Property(x => x.PhotoUrl).HasColumnName("photo_url").HasMaxLength(500);
        candidate.Property(x => x.CampaignOffice).HasColumnName("campaign_office").HasMaxLength(300);
        candidate.Property(x => x.IsActive).HasColumnName("is_active");
        candidate.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        candidate.HasIndex(x => new { x.TenantId, x.Id }).IsUnique();
        candidate.HasIndex(x => new { x.TenantId, x.ExternalReference }).IsUnique().HasFilter("external_reference IS NOT NULL");

        var assignment = modelBuilder.Entity<CandidateElection>();
        assignment.ToTable("candidate_elections");
        assignment.HasKey(x => x.Id);
        assignment.Property(x => x.Id).HasColumnName("candidate_election_id");
        assignment.Property(x => x.TenantId).HasColumnName("tenant_id");
        assignment.Property(x => x.ElectionId).HasColumnName("election_id");
        assignment.Property(x => x.CandidateId).HasColumnName("candidate_id");
        assignment.Property(x => x.PositionId).HasColumnName("position_id");
        assignment.Property(x => x.AreaId).HasColumnName("area_id");
        assignment.Property(x => x.NominationReference).HasColumnName("nomination_reference").HasMaxLength(120);
        assignment.Property(x => x.SymbolId).HasColumnName("symbol_id");
        assignment.Property(x => x.PartyName).HasColumnName("party_name").HasMaxLength(150);
        assignment.Property(x => x.Slogan).HasColumnName("slogan").HasMaxLength(300);
        assignment.Property(x => x.IsActive).HasColumnName("is_active");
        assignment.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        assignment.HasIndex(x => new { x.TenantId, x.ElectionId, x.CandidateId, x.PositionId }).IsUnique();
        assignment.HasIndex(x => new { x.TenantId, x.Id }).IsUnique();
    }
}
