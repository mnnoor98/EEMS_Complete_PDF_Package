using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Candidates.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialCandidates : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "election");

            migrationBuilder.CreateTable(
                name: "candidate_elections",
                schema: "election",
                columns: table => new
                {
                    candidate_election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    candidate_id = table.Column<Guid>(type: "uuid", nullable: false),
                    position_id = table.Column<long>(type: "bigint", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    nomination_reference = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: true),
                    is_active = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_candidate_elections", x => x.candidate_election_id);
                });

            migrationBuilder.CreateTable(
                name: "candidates",
                schema: "election",
                columns: table => new
                {
                    candidate_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    external_reference = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    is_active = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_candidates", x => x.candidate_id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_candidate_elections_tenant_id_candidate_election_id",
                schema: "election",
                table: "candidate_elections",
                columns: new[] { "tenant_id", "candidate_election_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_candidate_elections_tenant_id_election_id_candidate_id_posi~",
                schema: "election",
                table: "candidate_elections",
                columns: new[] { "tenant_id", "election_id", "candidate_id", "position_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_candidates_tenant_id_candidate_id",
                schema: "election",
                table: "candidates",
                columns: new[] { "tenant_id", "candidate_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_candidates_tenant_id_external_reference",
                schema: "election",
                table: "candidates",
                columns: new[] { "tenant_id", "external_reference" },
                unique: true,
                filter: "external_reference IS NOT NULL");

            migrationBuilder.Sql("""
                ALTER TABLE election.elections ADD CONSTRAINT uq_elections_tenant_election UNIQUE (tenant_id, election_id);
                ALTER TABLE election.candidates
                    ADD CONSTRAINT fk_candidates_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT;
                ALTER TABLE election.candidate_elections
                    ADD CONSTRAINT fk_candidate_elections_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_candidate_elections_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_candidate_elections_candidate FOREIGN KEY (tenant_id, candidate_id) REFERENCES election.candidates (tenant_id, candidate_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_candidate_elections_position FOREIGN KEY (position_id) REFERENCES election.positions (position_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_candidate_elections_area FOREIGN KEY (area_id) REFERENCES geo.areas (area_id) ON DELETE RESTRICT;
                ALTER TABLE election.candidates ENABLE ROW LEVEL SECURITY;
                ALTER TABLE election.candidates FORCE ROW LEVEL SECURITY;
                ALTER TABLE election.candidate_elections ENABLE ROW LEVEL SECURITY;
                ALTER TABLE election.candidate_elections FORCE ROW LEVEL SECURITY;
                CREATE POLICY candidates_tenant_policy ON election.candidates USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                CREATE POLICY candidate_elections_tenant_policy ON election.candidate_elections USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DROP POLICY IF EXISTS candidate_elections_tenant_policy ON election.candidate_elections;
                DROP POLICY IF EXISTS candidates_tenant_policy ON election.candidates;
                ALTER TABLE election.candidate_elections DISABLE ROW LEVEL SECURITY;
                ALTER TABLE election.candidates DISABLE ROW LEVEL SECURITY;
                ALTER TABLE election.elections DROP CONSTRAINT IF EXISTS uq_elections_tenant_election;
                """);
            migrationBuilder.DropTable(
                name: "candidate_elections",
                schema: "election");

            migrationBuilder.DropTable(
                name: "candidates",
                schema: "election");
        }
    }
}
