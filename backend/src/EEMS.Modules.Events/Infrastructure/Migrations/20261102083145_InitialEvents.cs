using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Events.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialEvents : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "campaign");

            migrationBuilder.CreateTable(
                name: "event_documents",
                schema: "campaign",
                columns: table => new
                {
                    event_document_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    event_id = table.Column<Guid>(type: "uuid", nullable: false),
                    uploaded_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    file_name = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    storage_key = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: false),
                    content_type = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    checksum = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    uploaded_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_event_documents", x => x.event_document_id);
                });

            migrationBuilder.CreateTable(
                name: "event_states",
                schema: "campaign",
                columns: table => new
                {
                    event_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_event_states", x => x.event_state_id);
                });

            migrationBuilder.CreateTable(
                name: "event_types",
                schema: "campaign",
                columns: table => new
                {
                    event_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_event_types", x => x.event_type_id);
                });

            migrationBuilder.CreateTable(
                name: "meeting_participants",
                schema: "campaign",
                columns: table => new
                {
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    meeting_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    attended = table.Column<bool>(type: "boolean", nullable: false),
                    attendance_recorded_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_meeting_participants", x => new { x.tenant_id, x.meeting_id, x.user_id });
                });

            migrationBuilder.CreateTable(
                name: "meetings",
                schema: "campaign",
                columns: table => new
                {
                    meeting_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    organizer_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    event_id = table.Column<Guid>(type: "uuid", nullable: true),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    agenda = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false),
                    minutes = table.Column<string>(type: "character varying(8000)", maxLength: 8000, nullable: true),
                    starts_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    ends_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_meetings", x => x.meeting_id);
                });

            migrationBuilder.CreateTable(
                name: "permit_states",
                schema: "campaign",
                columns: table => new
                {
                    permit_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_permit_states", x => x.permit_state_id);
                });

            migrationBuilder.CreateTable(
                name: "venues",
                schema: "campaign",
                columns: table => new
                {
                    venue_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    name = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    address = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    capacity = table.Column<int>(type: "integer", nullable: true),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_venues", x => x.venue_id);
                });

            migrationBuilder.CreateTable(
                name: "events",
                schema: "campaign",
                columns: table => new
                {
                    event_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    event_type_id = table.Column<short>(type: "smallint", nullable: false),
                    event_state_id = table.Column<short>(type: "smallint", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    venue_id = table.Column<Guid>(type: "uuid", nullable: true),
                    task_id = table.Column<Guid>(type: "uuid", nullable: true),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    starts_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    ends_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    completion_report = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_events", x => x.event_id);
                    table.ForeignKey(
                        name: "FK_events_event_states_event_state_id",
                        column: x => x.event_state_id,
                        principalSchema: "campaign",
                        principalTable: "event_states",
                        principalColumn: "event_state_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_events_event_types_event_type_id",
                        column: x => x.event_type_id,
                        principalSchema: "campaign",
                        principalTable: "event_types",
                        principalColumn: "event_type_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "permits",
                schema: "campaign",
                columns: table => new
                {
                    permit_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    event_id = table.Column<Guid>(type: "uuid", nullable: false),
                    permit_state_id = table.Column<short>(type: "smallint", nullable: false),
                    issuing_authority = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    reference_number = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    expires_on = table.Column<DateOnly>(type: "date", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_permits", x => x.permit_id);
                    table.ForeignKey(
                        name: "FK_permits_permit_states_permit_state_id",
                        column: x => x.permit_state_id,
                        principalSchema: "campaign",
                        principalTable: "permit_states",
                        principalColumn: "permit_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_event_documents_tenant_id_storage_key",
                schema: "campaign",
                table: "event_documents",
                columns: new[] { "tenant_id", "storage_key" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_event_states_code",
                schema: "campaign",
                table: "event_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_event_types_code",
                schema: "campaign",
                table: "event_types",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_events_event_state_id",
                schema: "campaign",
                table: "events",
                column: "event_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_events_event_type_id",
                schema: "campaign",
                table: "events",
                column: "event_type_id");

            migrationBuilder.CreateIndex(
                name: "IX_events_tenant_id_election_id_starts_at",
                schema: "campaign",
                table: "events",
                columns: new[] { "tenant_id", "election_id", "starts_at" });

            migrationBuilder.CreateIndex(
                name: "IX_events_tenant_id_event_id",
                schema: "campaign",
                table: "events",
                columns: new[] { "tenant_id", "event_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_meetings_tenant_id_election_id_starts_at",
                schema: "campaign",
                table: "meetings",
                columns: new[] { "tenant_id", "election_id", "starts_at" });

            migrationBuilder.CreateIndex(
                name: "IX_meetings_tenant_id_meeting_id",
                schema: "campaign",
                table: "meetings",
                columns: new[] { "tenant_id", "meeting_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_permit_states_code",
                schema: "campaign",
                table: "permit_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_permits_permit_state_id",
                schema: "campaign",
                table: "permits",
                column: "permit_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_permits_tenant_id_event_id_reference_number",
                schema: "campaign",
                table: "permits",
                columns: new[] { "tenant_id", "event_id", "reference_number" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_venues_tenant_id_area_id_name",
                schema: "campaign",
                table: "venues",
                columns: new[] { "tenant_id", "area_id", "name" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_venues_tenant_id_venue_id",
                schema: "campaign",
                table: "venues",
                columns: new[] { "tenant_id", "venue_id" },
                unique: true);

            migrationBuilder.Sql(
                """
                CREATE UNIQUE INDEX ux_team_tasks_tenant_task
                    ON team.tasks (tenant_id, task_id);

                ALTER TABLE campaign.venues
                    ADD CONSTRAINT ck_venues_capacity CHECK (capacity IS NULL OR capacity > 0),
                    ADD CONSTRAINT fk_venues_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_venues_area FOREIGN KEY (area_id) REFERENCES geo.areas (area_id) ON DELETE RESTRICT;

                ALTER TABLE campaign.events
                    ADD CONSTRAINT ck_events_valid_period CHECK (ends_at > starts_at),
                    ADD CONSTRAINT fk_events_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_events_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_events_area FOREIGN KEY (area_id) REFERENCES geo.areas (area_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_events_venue FOREIGN KEY (tenant_id, venue_id) REFERENCES campaign.venues (tenant_id, venue_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_events_task FOREIGN KEY (tenant_id, task_id) REFERENCES team.tasks (tenant_id, task_id) ON DELETE RESTRICT;

                ALTER TABLE campaign.permits
                    ADD CONSTRAINT fk_permits_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_permits_event FOREIGN KEY (tenant_id, event_id) REFERENCES campaign.events (tenant_id, event_id) ON DELETE CASCADE;

                ALTER TABLE campaign.event_documents
                    ADD CONSTRAINT fk_event_documents_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_event_documents_event FOREIGN KEY (tenant_id, event_id) REFERENCES campaign.events (tenant_id, event_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_event_documents_uploader FOREIGN KEY (tenant_id, uploaded_by_user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;

                ALTER TABLE campaign.meetings
                    ADD CONSTRAINT ck_meetings_valid_period CHECK (ends_at > starts_at),
                    ADD CONSTRAINT fk_meetings_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_meetings_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_meetings_organizer FOREIGN KEY (tenant_id, organizer_user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_meetings_event FOREIGN KEY (tenant_id, event_id) REFERENCES campaign.events (tenant_id, event_id) ON DELETE SET NULL (event_id);

                ALTER TABLE campaign.meeting_participants
                    ADD CONSTRAINT ck_meeting_participant_attendance CHECK (
                        (attended AND attendance_recorded_at IS NOT NULL)
                        OR (NOT attended AND attendance_recorded_at IS NULL)),
                    ADD CONSTRAINT fk_meeting_participants_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_meeting_participants_meeting FOREIGN KEY (tenant_id, meeting_id) REFERENCES campaign.meetings (tenant_id, meeting_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_meeting_participants_user FOREIGN KEY (tenant_id, user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;

                ALTER TABLE campaign.venues ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.venues FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_venues ON campaign.venues
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE campaign.events ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.events FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_events ON campaign.events
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE campaign.permits ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.permits FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_permits ON campaign.permits
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE campaign.event_documents ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.event_documents FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_event_documents ON campaign.event_documents
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE campaign.meetings ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.meetings FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_meetings ON campaign.meetings
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE campaign.meeting_participants ENABLE ROW LEVEL SECURITY;
                ALTER TABLE campaign.meeting_participants FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_meeting_participants ON campaign.meeting_participants
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                """
                DROP POLICY IF EXISTS tenant_isolation_meeting_participants ON campaign.meeting_participants;
                DROP POLICY IF EXISTS tenant_isolation_meetings ON campaign.meetings;
                DROP POLICY IF EXISTS tenant_isolation_event_documents ON campaign.event_documents;
                DROP POLICY IF EXISTS tenant_isolation_permits ON campaign.permits;
                DROP POLICY IF EXISTS tenant_isolation_events ON campaign.events;
                DROP POLICY IF EXISTS tenant_isolation_venues ON campaign.venues;

                ALTER TABLE campaign.meeting_participants
                    DROP CONSTRAINT IF EXISTS fk_meeting_participants_tenant,
                    DROP CONSTRAINT IF EXISTS fk_meeting_participants_meeting,
                    DROP CONSTRAINT IF EXISTS fk_meeting_participants_user;
                ALTER TABLE campaign.meetings
                    DROP CONSTRAINT IF EXISTS fk_meetings_tenant,
                    DROP CONSTRAINT IF EXISTS fk_meetings_election,
                    DROP CONSTRAINT IF EXISTS fk_meetings_organizer,
                    DROP CONSTRAINT IF EXISTS fk_meetings_event;
                ALTER TABLE campaign.event_documents
                    DROP CONSTRAINT IF EXISTS fk_event_documents_tenant,
                    DROP CONSTRAINT IF EXISTS fk_event_documents_event,
                    DROP CONSTRAINT IF EXISTS fk_event_documents_uploader;
                ALTER TABLE campaign.permits
                    DROP CONSTRAINT IF EXISTS fk_permits_tenant,
                    DROP CONSTRAINT IF EXISTS fk_permits_event;
                ALTER TABLE campaign.events
                    DROP CONSTRAINT IF EXISTS fk_events_tenant,
                    DROP CONSTRAINT IF EXISTS fk_events_election,
                    DROP CONSTRAINT IF EXISTS fk_events_area,
                    DROP CONSTRAINT IF EXISTS fk_events_venue,
                    DROP CONSTRAINT IF EXISTS fk_events_task;
                ALTER TABLE campaign.venues
                    DROP CONSTRAINT IF EXISTS fk_venues_tenant,
                    DROP CONSTRAINT IF EXISTS fk_venues_area;
                DROP INDEX IF EXISTS team.ux_team_tasks_tenant_task;
                """);

            migrationBuilder.DropTable(
                name: "event_documents",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "events",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "meeting_participants",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "meetings",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "permits",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "venues",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "event_states",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "event_types",
                schema: "campaign");

            migrationBuilder.DropTable(
                name: "permit_states",
                schema: "campaign");
        }
    }
}
