using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Polling.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class CenterVerificationAudit : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "center_verifications",
                schema: "polling",
                columns: table => new
                {
                    center_verification_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    verified_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    verified_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_center_verifications", x => x.center_verification_id);
                    table.ForeignKey(
                        name: "FK_center_verifications_election_centers_election_center_id",
                        column: x => x.election_center_id,
                        principalSchema: "polling",
                        principalTable: "election_centers",
                        principalColumn: "election_center_id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_center_verifications_election_center_id",
                schema: "polling",
                table: "center_verifications",
                column: "election_center_id");

            migrationBuilder.CreateIndex(
                name: "IX_center_verifications_tenant_id_election_center_id_verified_~",
                schema: "polling",
                table: "center_verifications",
                columns: new[] { "tenant_id", "election_center_id", "verified_at" });

            migrationBuilder.Sql("""
                ALTER TABLE polling.center_verifications ENABLE ROW LEVEL SECURITY;
                ALTER TABLE polling.center_verifications FORCE ROW LEVEL SECURITY;
                CREATE POLICY center_verifications_tenant_policy ON polling.center_verifications
                USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "center_verifications",
                schema: "polling");
        }
    }
}
