using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Teams.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddFieldMembersAndWorkAssignments : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<Guid>(
                name: "leader_user_id",
                schema: "team",
                table: "teams",
                type: "uuid",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "field_members",
                schema: "team",
                columns: table => new
                {
                    member_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: false),
                    full_name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    phone = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    member_type = table.Column<string>(type: "character varying(80)", maxLength: 80, nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: true),
                    address = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true),
                    emergency_contact = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: true),
                    joined_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_field_members", x => x.member_id);
                });

            migrationBuilder.CreateTable(
                name: "member_work_assignments",
                schema: "team",
                columns: table => new
                {
                    assignment_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: false),
                    member_id = table.Column<Guid>(type: "uuid", nullable: false),
                    task_state_id = table.Column<short>(type: "smallint", nullable: false),
                    task_priority_id = table.Column<short>(type: "smallint", nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    instructions = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: true),
                    due_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_member_work_assignments", x => x.assignment_id);
                    table.ForeignKey(
                        name: "FK_member_work_assignments_field_members_member_id",
                        column: x => x.member_id,
                        principalSchema: "team",
                        principalTable: "field_members",
                        principalColumn: "member_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_member_work_assignments_task_priorities_task_priority_id",
                        column: x => x.task_priority_id,
                        principalSchema: "team",
                        principalTable: "task_priorities",
                        principalColumn: "task_priority_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_member_work_assignments_task_states_task_state_id",
                        column: x => x.task_state_id,
                        principalSchema: "team",
                        principalTable: "task_states",
                        principalColumn: "task_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_field_members_tenant_id_team_id_phone",
                schema: "team",
                table: "field_members",
                columns: new[] { "tenant_id", "team_id", "phone" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_member_work_assignments_member_id",
                schema: "team",
                table: "member_work_assignments",
                column: "member_id");

            migrationBuilder.CreateIndex(
                name: "IX_member_work_assignments_task_priority_id",
                schema: "team",
                table: "member_work_assignments",
                column: "task_priority_id");

            migrationBuilder.CreateIndex(
                name: "IX_member_work_assignments_task_state_id",
                schema: "team",
                table: "member_work_assignments",
                column: "task_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_member_work_assignments_tenant_id_team_id_member_id_task_st~",
                schema: "team",
                table: "member_work_assignments",
                columns: new[] { "tenant_id", "team_id", "member_id", "task_state_id" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "member_work_assignments",
                schema: "team");

            migrationBuilder.DropTable(
                name: "field_members",
                schema: "team");

            migrationBuilder.DropColumn(
                name: "leader_user_id",
                schema: "team",
                table: "teams");
        }
    }
}
