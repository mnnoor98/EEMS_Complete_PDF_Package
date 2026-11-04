using EEMS.Modules.Candidates.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Candidates.Infrastructure;

public sealed class CandidatesDbContext(DbContextOptions<CandidatesDbContext> options):DbContext(options)
{
    public DbSet<Candidate> Candidates=>Set<Candidate>(); public DbSet<CandidateElection> CandidateElections=>Set<CandidateElection>();
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("election");
        var candidate=modelBuilder.Entity<Candidate>();candidate.ToTable("candidates");candidate.HasKey(x=>x.Id);candidate.Property(x=>x.Id).HasColumnName("candidate_id");candidate.Property(x=>x.TenantId).HasColumnName("tenant_id");candidate.Property(x=>x.Name).HasColumnName("name").HasMaxLength(200);candidate.Property(x=>x.ExternalReference).HasColumnName("external_reference").HasMaxLength(100);candidate.Property(x=>x.IsActive).HasColumnName("is_active");candidate.Property(x=>x.CreatedAtUtc).HasColumnName("created_at");candidate.HasIndex(x=>new{x.TenantId,x.Id}).IsUnique();candidate.HasIndex(x=>new{x.TenantId,x.ExternalReference}).IsUnique().HasFilter("external_reference IS NOT NULL");
        var assignment=modelBuilder.Entity<CandidateElection>();assignment.ToTable("candidate_elections");assignment.HasKey(x=>x.Id);assignment.Property(x=>x.Id).HasColumnName("candidate_election_id");assignment.Property(x=>x.TenantId).HasColumnName("tenant_id");assignment.Property(x=>x.ElectionId).HasColumnName("election_id");assignment.Property(x=>x.CandidateId).HasColumnName("candidate_id");assignment.Property(x=>x.PositionId).HasColumnName("position_id");assignment.Property(x=>x.AreaId).HasColumnName("area_id");assignment.Property(x=>x.NominationReference).HasColumnName("nomination_reference").HasMaxLength(120);assignment.Property(x=>x.IsActive).HasColumnName("is_active");assignment.Property(x=>x.CreatedAtUtc).HasColumnName("created_at");assignment.HasIndex(x=>new{x.TenantId,x.ElectionId,x.CandidateId,x.PositionId}).IsUnique();assignment.HasIndex(x=>new{x.TenantId,x.Id}).IsUnique();
    }
}
