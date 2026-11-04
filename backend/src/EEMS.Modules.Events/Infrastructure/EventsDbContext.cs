using EEMS.Modules.Events.Domain;
using Microsoft.EntityFrameworkCore;

namespace EEMS.Modules.Events.Infrastructure;

public sealed class EventsDbContext(DbContextOptions<EventsDbContext> options) : DbContext(options)
{
    public DbSet<EventType> EventTypes => Set<EventType>();
    public DbSet<EventState> EventStates => Set<EventState>();
    public DbSet<PermitState> PermitStates => Set<PermitState>();
    public DbSet<Venue> Venues => Set<Venue>();
    public DbSet<CampaignEvent> Events => Set<CampaignEvent>();
    public DbSet<EventPermit> Permits => Set<EventPermit>();
    public DbSet<EventDocument> Documents => Set<EventDocument>();
    public DbSet<Meeting> Meetings => Set<Meeting>();
    public DbSet<MeetingParticipant> MeetingParticipants => Set<MeetingParticipant>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("campaign");

        var type = modelBuilder.Entity<EventType>();
        type.ToTable("event_types");
        type.HasKey(x => x.Id);
        type.Property(x => x.Id).HasColumnName("event_type_id").ValueGeneratedNever();
        type.Property(x => x.Code).HasColumnName("code").HasMaxLength(40);
        type.Property(x => x.Name).HasColumnName("name").HasMaxLength(100);
        type.Property(x => x.IsActive).HasColumnName("is_active");
        type.HasIndex(x => x.Code).IsUnique();

        var state = modelBuilder.Entity<EventState>();
        state.ToTable("event_states");
        state.HasKey(x => x.Id);
        state.Property(x => x.Id).HasColumnName("event_state_id").ValueGeneratedNever();
        state.Property(x => x.Code).HasColumnName("code").HasMaxLength(40);
        state.Property(x => x.Name).HasColumnName("name").HasMaxLength(100);
        state.Property(x => x.IsTerminal).HasColumnName("is_terminal");
        state.Property(x => x.IsActive).HasColumnName("is_active");
        state.HasIndex(x => x.Code).IsUnique();

        var permitState = modelBuilder.Entity<PermitState>();
        permitState.ToTable("permit_states");
        permitState.HasKey(x => x.Id);
        permitState.Property(x => x.Id).HasColumnName("permit_state_id").ValueGeneratedNever();
        permitState.Property(x => x.Code).HasColumnName("code").HasMaxLength(40);
        permitState.Property(x => x.Name).HasColumnName("name").HasMaxLength(100);
        permitState.Property(x => x.IsActive).HasColumnName("is_active");
        permitState.HasIndex(x => x.Code).IsUnique();

        var venue = modelBuilder.Entity<Venue>();
        venue.ToTable("venues");
        venue.HasKey(x => x.Id);
        venue.Property(x => x.Id).HasColumnName("venue_id");
        venue.Property(x => x.TenantId).HasColumnName("tenant_id");
        venue.Property(x => x.AreaId).HasColumnName("area_id");
        venue.Property(x => x.Name).HasColumnName("name").HasMaxLength(160);
        venue.Property(x => x.Address).HasColumnName("address").HasMaxLength(300);
        venue.Property(x => x.Capacity).HasColumnName("capacity");
        venue.Property(x => x.IsActive).HasColumnName("is_active");
        venue.HasIndex(x => new { x.TenantId, x.Id }).IsUnique();
        venue.HasIndex(x => new { x.TenantId, x.AreaId, x.Name }).IsUnique();

        var campaignEvent = modelBuilder.Entity<CampaignEvent>();
        campaignEvent.ToTable("events");
        campaignEvent.HasKey(x => x.Id);
        campaignEvent.Property(x => x.Id).HasColumnName("event_id");
        campaignEvent.Property(x => x.TenantId).HasColumnName("tenant_id");
        campaignEvent.Property(x => x.ElectionId).HasColumnName("election_id");
        campaignEvent.Property(x => x.EventTypeId).HasColumnName("event_type_id");
        campaignEvent.Property(x => x.StateId).HasColumnName("event_state_id");
        campaignEvent.Property(x => x.AreaId).HasColumnName("area_id");
        campaignEvent.Property(x => x.VenueId).HasColumnName("venue_id");
        campaignEvent.Property(x => x.TaskId).HasColumnName("task_id");
        campaignEvent.Property(x => x.Title).HasColumnName("title").HasMaxLength(200);
        campaignEvent.Property(x => x.StartsAtUtc).HasColumnName("starts_at");
        campaignEvent.Property(x => x.EndsAtUtc).HasColumnName("ends_at");
        campaignEvent.Property(x => x.CompletionReport).HasColumnName("completion_report").HasMaxLength(4000);
        campaignEvent.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        campaignEvent.Property(x => x.Version).HasColumnName("version").IsConcurrencyToken();
        campaignEvent.HasOne<EventType>().WithMany().HasForeignKey(x => x.EventTypeId).OnDelete(DeleteBehavior.Restrict);
        campaignEvent.HasOne<EventState>().WithMany().HasForeignKey(x => x.StateId).OnDelete(DeleteBehavior.Restrict);
        campaignEvent.HasIndex(x => new { x.TenantId, x.Id }).IsUnique();
        campaignEvent.HasIndex(x => new { x.TenantId, x.ElectionId, x.StartsAtUtc });

        var permit = modelBuilder.Entity<EventPermit>();
        permit.ToTable("permits");
        permit.HasKey(x => x.Id);
        permit.Property(x => x.Id).HasColumnName("permit_id");
        permit.Property(x => x.TenantId).HasColumnName("tenant_id");
        permit.Property(x => x.EventId).HasColumnName("event_id");
        permit.Property(x => x.StateId).HasColumnName("permit_state_id");
        permit.Property(x => x.IssuingAuthority).HasColumnName("issuing_authority").HasMaxLength(160);
        permit.Property(x => x.ReferenceNumber).HasColumnName("reference_number").HasMaxLength(100);
        permit.Property(x => x.ExpiresOn).HasColumnName("expires_on");
        permit.HasOne<PermitState>().WithMany().HasForeignKey(x => x.StateId).OnDelete(DeleteBehavior.Restrict);
        permit.HasIndex(x => new { x.TenantId, x.EventId, x.ReferenceNumber }).IsUnique();

        var document = modelBuilder.Entity<EventDocument>();
        document.ToTable("event_documents");
        document.HasKey(x => x.Id);
        document.Property(x => x.Id).HasColumnName("event_document_id");
        document.Property(x => x.TenantId).HasColumnName("tenant_id");
        document.Property(x => x.EventId).HasColumnName("event_id");
        document.Property(x => x.UploadedByUserId).HasColumnName("uploaded_by_user_id");
        document.Property(x => x.FileName).HasColumnName("file_name").HasMaxLength(255);
        document.Property(x => x.StorageKey).HasColumnName("storage_key").HasMaxLength(500);
        document.Property(x => x.ContentType).HasColumnName("content_type").HasMaxLength(120);
        document.Property(x => x.Checksum).HasColumnName("checksum").HasMaxLength(128);
        document.Property(x => x.UploadedAtUtc).HasColumnName("uploaded_at");
        document.HasIndex(x => new { x.TenantId, x.StorageKey }).IsUnique();

        var meeting = modelBuilder.Entity<Meeting>();
        meeting.ToTable("meetings");
        meeting.HasKey(x => x.Id);
        meeting.Property(x => x.Id).HasColumnName("meeting_id");
        meeting.Property(x => x.TenantId).HasColumnName("tenant_id");
        meeting.Property(x => x.ElectionId).HasColumnName("election_id");
        meeting.Property(x => x.OrganizerUserId).HasColumnName("organizer_user_id");
        meeting.Property(x => x.EventId).HasColumnName("event_id");
        meeting.Property(x => x.Title).HasColumnName("title").HasMaxLength(200);
        meeting.Property(x => x.Agenda).HasColumnName("agenda").HasMaxLength(4000);
        meeting.Property(x => x.Minutes).HasColumnName("minutes").HasMaxLength(8000);
        meeting.Property(x => x.StartsAtUtc).HasColumnName("starts_at");
        meeting.Property(x => x.EndsAtUtc).HasColumnName("ends_at");
        meeting.Property(x => x.CreatedAtUtc).HasColumnName("created_at");
        meeting.HasIndex(x => new { x.TenantId, x.Id }).IsUnique();
        meeting.HasIndex(x => new { x.TenantId, x.ElectionId, x.StartsAtUtc });

        var participant = modelBuilder.Entity<MeetingParticipant>();
        participant.ToTable("meeting_participants");
        participant.HasKey(x => new { x.TenantId, x.MeetingId, x.UserId });
        participant.Property(x => x.TenantId).HasColumnName("tenant_id");
        participant.Property(x => x.MeetingId).HasColumnName("meeting_id");
        participant.Property(x => x.UserId).HasColumnName("user_id");
        participant.Property(x => x.Attended).HasColumnName("attended");
        participant.Property(x => x.AttendanceRecordedAtUtc).HasColumnName("attendance_recorded_at");
    }
}
