using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Elections.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialElections : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "election");

            migrationBuilder.CreateTable(
                name: "election_types",
                schema: "election",
                columns: table => new
                {
                    election_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_election_types", x => x.election_type_id);
                });

            migrationBuilder.CreateTable(
                name: "lifecycle_states",
                schema: "election",
                columns: table => new
                {
                    lifecycle_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_lifecycle_states", x => x.lifecycle_state_id);
                });

            migrationBuilder.CreateTable(
                name: "positions",
                schema: "election",
                columns: table => new
                {
                    position_id = table.Column<long>(type: "bigint", nullable: false),
                    election_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: false),
                    name = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_positions", x => x.position_id);
                    table.ForeignKey(
                        name: "FK_positions_election_types_election_type_id",
                        column: x => x.election_type_id,
                        principalSchema: "election",
                        principalTable: "election_types",
                        principalColumn: "election_type_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "elections",
                schema: "election",
                columns: table => new
                {
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_type_id = table.Column<short>(type: "smallint", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    lifecycle_state_id = table.Column<short>(type: "smallint", nullable: false),
                    name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    election_date = table.Column<DateOnly>(type: "date", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_elections", x => x.election_id);
                    table.ForeignKey(
                        name: "FK_elections_election_types_election_type_id",
                        column: x => x.election_type_id,
                        principalSchema: "election",
                        principalTable: "election_types",
                        principalColumn: "election_type_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_elections_lifecycle_states_lifecycle_state_id",
                        column: x => x.lifecycle_state_id,
                        principalSchema: "election",
                        principalTable: "lifecycle_states",
                        principalColumn: "lifecycle_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_election_types_code",
                schema: "election",
                table: "election_types",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_elections_election_type_id",
                schema: "election",
                table: "elections",
                column: "election_type_id");

            migrationBuilder.CreateIndex(
                name: "IX_elections_lifecycle_state_id",
                schema: "election",
                table: "elections",
                column: "lifecycle_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_elections_tenant_id_election_date",
                schema: "election",
                table: "elections",
                columns: new[] { "tenant_id", "election_date" });

            migrationBuilder.CreateIndex(
                name: "IX_lifecycle_states_code",
                schema: "election",
                table: "lifecycle_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_positions_election_type_id_code",
                schema: "election",
                table: "positions",
                columns: new[] { "election_type_id", "code" },
                unique: true);

            migrationBuilder.Sql("""
                ALTER TABLE election.elections
                    ADD CONSTRAINT fk_elections_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_elections_area FOREIGN KEY (area_id)
                        REFERENCES geo.areas (area_id) ON DELETE RESTRICT;
                ALTER TABLE election.elections ENABLE ROW LEVEL SECURITY;
                ALTER TABLE election.elections FORCE ROW LEVEL SECURITY;
                CREATE POLICY elections_tenant_policy ON election.elections
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("DROP POLICY IF EXISTS elections_tenant_policy ON election.elections; ALTER TABLE election.elections DISABLE ROW LEVEL SECURITY;");

            migrationBuilder.DropTable(
                name: "elections",
                schema: "election");

            migrationBuilder.DropTable(
                name: "positions",
                schema: "election");

            migrationBuilder.DropTable(
                name: "lifecycle_states",
                schema: "election");

            migrationBuilder.DropTable(
                name: "election_types",
                schema: "election");
        }
    }
}
