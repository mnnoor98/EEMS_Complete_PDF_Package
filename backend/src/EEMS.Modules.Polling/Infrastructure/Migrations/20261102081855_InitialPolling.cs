using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Polling.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialPolling : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "polling");

            migrationBuilder.CreateTable(
                name: "centers",
                schema: "polling",
                columns: table => new
                {
                    center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    code = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    name = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    address = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_centers", x => x.center_id);
                });

            migrationBuilder.CreateTable(
                name: "booths",
                schema: "polling",
                columns: table => new
                {
                    booth_id = table.Column<Guid>(type: "uuid", nullable: false),
                    center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    code = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    name = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_booths", x => x.booth_id);
                    table.ForeignKey(
                        name: "FK_booths_centers_center_id",
                        column: x => x.center_id,
                        principalSchema: "polling",
                        principalTable: "centers",
                        principalColumn: "center_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "election_centers",
                schema: "polling",
                columns: table => new
                {
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    is_verified = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_election_centers", x => x.election_center_id);
                    table.ForeignKey(
                        name: "FK_election_centers_centers_center_id",
                        column: x => x.center_id,
                        principalSchema: "polling",
                        principalTable: "centers",
                        principalColumn: "center_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "agent_assignments",
                schema: "polling",
                columns: table => new
                {
                    agent_assignment_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    starts_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    ends_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_agent_assignments", x => x.agent_assignment_id);
                    table.ForeignKey(
                        name: "FK_agent_assignments_election_centers_election_center_id",
                        column: x => x.election_center_id,
                        principalSchema: "polling",
                        principalTable: "election_centers",
                        principalColumn: "election_center_id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_agent_assignments_election_center_id",
                schema: "polling",
                table: "agent_assignments",
                column: "election_center_id");

            migrationBuilder.CreateIndex(
                name: "IX_agent_assignments_tenant_id_election_center_id_user_id_star~",
                schema: "polling",
                table: "agent_assignments",
                columns: new[] { "tenant_id", "election_center_id", "user_id", "starts_at" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_booths_center_id_code",
                schema: "polling",
                table: "booths",
                columns: new[] { "center_id", "code" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_centers_area_id_code",
                schema: "polling",
                table: "centers",
                columns: new[] { "area_id", "code" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_election_centers_center_id",
                schema: "polling",
                table: "election_centers",
                column: "center_id");

            migrationBuilder.CreateIndex(
                name: "IX_election_centers_tenant_id_election_center_id",
                schema: "polling",
                table: "election_centers",
                columns: new[] { "tenant_id", "election_center_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_election_centers_tenant_id_election_id_center_id",
                schema: "polling",
                table: "election_centers",
                columns: new[] { "tenant_id", "election_id", "center_id" },
                unique: true);

            migrationBuilder.Sql("""
                ALTER TABLE polling.centers ADD CONSTRAINT fk_centers_area FOREIGN KEY (area_id) REFERENCES geo.areas (area_id) ON DELETE RESTRICT;
                ALTER TABLE polling.election_centers
                    ADD CONSTRAINT fk_election_centers_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_election_centers_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT;
                ALTER TABLE polling.agent_assignments
                    ADD CONSTRAINT fk_agent_assignments_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_agent_assignments_center FOREIGN KEY (tenant_id, election_center_id) REFERENCES polling.election_centers (tenant_id, election_center_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_agent_assignments_user FOREIGN KEY (tenant_id, user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;
                ALTER TABLE polling.election_centers ENABLE ROW LEVEL SECURITY;
                ALTER TABLE polling.election_centers FORCE ROW LEVEL SECURITY;
                ALTER TABLE polling.agent_assignments ENABLE ROW LEVEL SECURITY;
                ALTER TABLE polling.agent_assignments FORCE ROW LEVEL SECURITY;
                CREATE POLICY election_centers_tenant_policy ON polling.election_centers USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                CREATE POLICY agent_assignments_tenant_policy ON polling.agent_assignments USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DROP POLICY IF EXISTS agent_assignments_tenant_policy ON polling.agent_assignments;
                DROP POLICY IF EXISTS election_centers_tenant_policy ON polling.election_centers;
                ALTER TABLE polling.agent_assignments DISABLE ROW LEVEL SECURITY;
                ALTER TABLE polling.election_centers DISABLE ROW LEVEL SECURITY;
                """);
            migrationBuilder.DropTable(
                name: "agent_assignments",
                schema: "polling");

            migrationBuilder.DropTable(
                name: "booths",
                schema: "polling");

            migrationBuilder.DropTable(
                name: "election_centers",
                schema: "polling");

            migrationBuilder.DropTable(
                name: "centers",
                schema: "polling");
        }
    }
}
