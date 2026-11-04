using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Teams.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddFieldAttendanceAndVerification : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "verification_note",
                schema: "team",
                table: "member_work_assignments",
                type: "character varying(500)",
                maxLength: 500,
                nullable: true);

            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "verified_at",
                schema: "team",
                table: "member_work_assignments",
                type: "timestamp with time zone",
                nullable: true);

            migrationBuilder.AddColumn<Guid>(
                name: "verified_by_user_id",
                schema: "team",
                table: "member_work_assignments",
                type: "uuid",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "field_member_attendance",
                schema: "team",
                columns: table => new
                {
                    attendance_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: false),
                    member_id = table.Column<Guid>(type: "uuid", nullable: false),
                    attendance_date = table.Column<DateOnly>(type: "date", nullable: false),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    recorded_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    note = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: true),
                    recorded_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_field_member_attendance", x => x.attendance_id);
                    table.ForeignKey(
                        name: "FK_field_member_attendance_field_members_member_id",
                        column: x => x.member_id,
                        principalSchema: "team",
                        principalTable: "field_members",
                        principalColumn: "member_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_field_member_attendance_member_id",
                schema: "team",
                table: "field_member_attendance",
                column: "member_id");

            migrationBuilder.CreateIndex(
                name: "IX_field_member_attendance_tenant_id_team_id_member_id_attenda~",
                schema: "team",
                table: "field_member_attendance",
                columns: new[] { "tenant_id", "team_id", "member_id", "attendance_date" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "field_member_attendance",
                schema: "team");

            migrationBuilder.DropColumn(
                name: "verification_note",
                schema: "team",
                table: "member_work_assignments");

            migrationBuilder.DropColumn(
                name: "verified_at",
                schema: "team",
                table: "member_work_assignments");

            migrationBuilder.DropColumn(
                name: "verified_by_user_id",
                schema: "team",
                table: "member_work_assignments");
        }
    }
}
