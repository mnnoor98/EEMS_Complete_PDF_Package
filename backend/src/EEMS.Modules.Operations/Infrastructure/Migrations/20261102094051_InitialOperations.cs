using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Operations.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialOperations : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "operations");

            migrationBuilder.CreateTable(
                name: "checklist_items",
                schema: "operations",
                columns: table => new
                {
                    checklist_item_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    checklist_id = table.Column<Guid>(type: "uuid", nullable: false),
                    requirement = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    is_complete = table.Column<bool>(type: "boolean", nullable: false),
                    completed_by_user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    completed_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_checklist_items", x => x.checklist_item_id);
                });

            migrationBuilder.CreateTable(
                name: "incident_severities",
                schema: "operations",
                columns: table => new
                {
                    incident_severity_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Rank = table.Column<short>(type: "smallint", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_incident_severities", x => x.incident_severity_id);
                });

            migrationBuilder.CreateTable(
                name: "incident_states",
                schema: "operations",
                columns: table => new
                {
                    incident_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    IsTerminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_incident_states", x => x.incident_state_id);
                });

            migrationBuilder.CreateTable(
                name: "readiness_states",
                schema: "operations",
                columns: table => new
                {
                    readiness_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Rank = table.Column<short>(type: "smallint", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_readiness_states", x => x.readiness_state_id);
                });

            migrationBuilder.CreateTable(
                name: "incident_reviews",
                schema: "operations",
                columns: table => new
                {
                    incident_review_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    incident_id = table.Column<Guid>(type: "uuid", nullable: false),
                    reporter_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    reviewer_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    resulting_state_id = table.Column<short>(type: "smallint", nullable: false),
                    resolution = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false),
                    reviewed_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_incident_reviews", x => x.incident_review_id);
                    table.ForeignKey(
                        name: "FK_incident_reviews_incident_states_resulting_state_id",
                        column: x => x.resulting_state_id,
                        principalSchema: "operations",
                        principalTable: "incident_states",
                        principalColumn: "incident_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "incidents",
                schema: "operations",
                columns: table => new
                {
                    incident_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: true),
                    reporter_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    assigned_to_user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    incident_state_id = table.Column<short>(type: "smallint", nullable: false),
                    incident_severity_id = table.Column<short>(type: "smallint", nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    description = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false),
                    is_confidential = table.Column<bool>(type: "boolean", nullable: false),
                    reported_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_incidents", x => x.incident_id);
                    table.ForeignKey(
                        name: "FK_incidents_incident_severities_incident_severity_id",
                        column: x => x.incident_severity_id,
                        principalSchema: "operations",
                        principalTable: "incident_severities",
                        principalColumn: "incident_severity_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_incidents_incident_states_incident_state_id",
                        column: x => x.incident_state_id,
                        principalSchema: "operations",
                        principalTable: "incident_states",
                        principalColumn: "incident_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "checklists",
                schema: "operations",
                columns: table => new
                {
                    checklist_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    readiness_state_id = table.Column<short>(type: "smallint", nullable: false),
                    name = table.Column<string>(type: "character varying(180)", maxLength: 180, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_checklists", x => x.checklist_id);
                    table.ForeignKey(
                        name: "FK_checklists_readiness_states_readiness_state_id",
                        column: x => x.readiness_state_id,
                        principalSchema: "operations",
                        principalTable: "readiness_states",
                        principalColumn: "readiness_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_checklists_readiness_state_id",
                schema: "operations",
                table: "checklists",
                column: "readiness_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_checklists_tenant_id_checklist_id",
                schema: "operations",
                table: "checklists",
                columns: new[] { "tenant_id", "checklist_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_checklists_tenant_id_election_id_election_center_id_name",
                schema: "operations",
                table: "checklists",
                columns: new[] { "tenant_id", "election_id", "election_center_id", "name" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_incident_reviews_resulting_state_id",
                schema: "operations",
                table: "incident_reviews",
                column: "resulting_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_incident_severities_code",
                schema: "operations",
                table: "incident_severities",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_incident_states_code",
                schema: "operations",
                table: "incident_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_incidents_incident_severity_id",
                schema: "operations",
                table: "incidents",
                column: "incident_severity_id");

            migrationBuilder.CreateIndex(
                name: "IX_incidents_incident_state_id",
                schema: "operations",
                table: "incidents",
                column: "incident_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_incidents_tenant_id_election_id_incident_state_id_incident_~",
                schema: "operations",
                table: "incidents",
                columns: new[] { "tenant_id", "election_id", "incident_state_id", "incident_severity_id" });

            migrationBuilder.CreateIndex(
                name: "IX_incidents_tenant_id_incident_id",
                schema: "operations",
                table: "incidents",
                columns: new[] { "tenant_id", "incident_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_readiness_states_code",
                schema: "operations",
                table: "readiness_states",
                column: "code",
                unique: true);

            migrationBuilder.Sql(
                """
                ALTER TABLE operations.checklists ADD CONSTRAINT fk_checklists_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_checklists_election FOREIGN KEY(tenant_id,election_id) REFERENCES election.elections(tenant_id,election_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_checklists_center FOREIGN KEY(tenant_id,election_id,election_center_id) REFERENCES polling.election_centers(tenant_id,election_id,election_center_id) ON DELETE RESTRICT;
                ALTER TABLE operations.checklist_items ADD CONSTRAINT ck_checklist_items_completion CHECK((is_complete AND completed_by_user_id IS NOT NULL AND completed_at IS NOT NULL) OR (NOT is_complete AND completed_by_user_id IS NULL AND completed_at IS NULL)), ADD CONSTRAINT fk_checklist_items_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_checklist_items_checklist FOREIGN KEY(tenant_id,checklist_id) REFERENCES operations.checklists(tenant_id,checklist_id) ON DELETE CASCADE, ADD CONSTRAINT fk_checklist_items_user FOREIGN KEY(tenant_id,completed_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE operations.incidents ADD CONSTRAINT fk_incidents_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_incidents_election FOREIGN KEY(tenant_id,election_id) REFERENCES election.elections(tenant_id,election_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_incidents_center FOREIGN KEY(tenant_id,election_id,election_center_id) REFERENCES polling.election_centers(tenant_id,election_id,election_center_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_incidents_reporter FOREIGN KEY(tenant_id,reporter_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_incidents_assignee FOREIGN KEY(tenant_id,assigned_to_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE operations.incident_reviews ADD CONSTRAINT ck_incident_reviews_separation CHECK(reporter_user_id<>reviewer_user_id), ADD CONSTRAINT fk_reviews_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_reviews_incident FOREIGN KEY(tenant_id,incident_id) REFERENCES operations.incidents(tenant_id,incident_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_reviews_reporter FOREIGN KEY(tenant_id,reporter_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_reviews_reviewer FOREIGN KEY(tenant_id,reviewer_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                DO $rls$ DECLARE n text;BEGIN FOREACH n IN ARRAY ARRAY['checklists','checklist_items','incidents','incident_reviews'] LOOP EXECUTE format('ALTER TABLE operations.%I ENABLE ROW LEVEL SECURITY',n);EXECUTE format('ALTER TABLE operations.%I FORCE ROW LEVEL SECURITY',n);EXECUTE format('CREATE POLICY tenant_isolation_%I ON operations.%I USING(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',n,n);END LOOP;END $rls$;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("ALTER TABLE operations.checklist_items DROP CONSTRAINT IF EXISTS fk_checklist_items_checklist; ALTER TABLE operations.incident_reviews DROP CONSTRAINT IF EXISTS fk_reviews_incident;");

            migrationBuilder.DropTable(
                name: "checklist_items",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "checklists",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "incident_reviews",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "incidents",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "readiness_states",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "incident_severities",
                schema: "operations");

            migrationBuilder.DropTable(
                name: "incident_states",
                schema: "operations");
        }
    }
}
