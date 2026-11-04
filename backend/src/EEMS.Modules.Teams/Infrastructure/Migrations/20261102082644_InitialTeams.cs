using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Teams.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialTeams : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "team");

            migrationBuilder.CreateTable(
                name: "attendance",
                schema: "team",
                columns: table => new
                {
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    training_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    recorded_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_attendance", x => new { x.tenant_id, x.training_id, x.user_id });
                });

            migrationBuilder.CreateTable(
                name: "task_priorities",
                schema: "team",
                columns: table => new
                {
                    task_priority_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    rank = table.Column<short>(type: "smallint", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_task_priorities", x => x.task_priority_id);
                });

            migrationBuilder.CreateTable(
                name: "task_states",
                schema: "team",
                columns: table => new
                {
                    task_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_task_states", x => x.task_state_id);
                });

            migrationBuilder.CreateTable(
                name: "team_members",
                schema: "team",
                columns: table => new
                {
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    responsibility = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    joined_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_team_members", x => new { x.tenant_id, x.team_id, x.user_id });
                });

            migrationBuilder.CreateTable(
                name: "teams",
                schema: "team",
                columns: table => new
                {
                    team_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    name = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_teams", x => x.team_id);
                });

            migrationBuilder.CreateTable(
                name: "trainings",
                schema: "team",
                columns: table => new
                {
                    training_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    starts_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    ends_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_trainings", x => x.training_id);
                });

            migrationBuilder.CreateTable(
                name: "tasks",
                schema: "team",
                columns: table => new
                {
                    task_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: true),
                    assignee_user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    task_state_id = table.Column<short>(type: "smallint", nullable: false),
                    task_priority_id = table.Column<short>(type: "smallint", nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    due_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_tasks", x => x.task_id);
                    table.ForeignKey(
                        name: "FK_tasks_task_priorities_task_priority_id",
                        column: x => x.task_priority_id,
                        principalSchema: "team",
                        principalTable: "task_priorities",
                        principalColumn: "task_priority_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_tasks_task_states_task_state_id",
                        column: x => x.task_state_id,
                        principalSchema: "team",
                        principalTable: "task_states",
                        principalColumn: "task_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_task_priorities_code",
                schema: "team",
                table: "task_priorities",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_task_priorities_rank",
                schema: "team",
                table: "task_priorities",
                column: "rank",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_task_states_code",
                schema: "team",
                table: "task_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_tasks_task_priority_id",
                schema: "team",
                table: "tasks",
                column: "task_priority_id");

            migrationBuilder.CreateIndex(
                name: "IX_tasks_task_state_id",
                schema: "team",
                table: "tasks",
                column: "task_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_tasks_tenant_id_election_id_task_state_id_due_at",
                schema: "team",
                table: "tasks",
                columns: new[] { "tenant_id", "election_id", "task_state_id", "due_at" });

            migrationBuilder.CreateIndex(
                name: "IX_teams_tenant_id_election_id_name",
                schema: "team",
                table: "teams",
                columns: new[] { "tenant_id", "election_id", "name" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_teams_tenant_id_team_id",
                schema: "team",
                table: "teams",
                columns: new[] { "tenant_id", "team_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_trainings_tenant_id_training_id",
                schema: "team",
                table: "trainings",
                columns: new[] { "tenant_id", "training_id" },
                unique: true);

            migrationBuilder.Sql(
                """
                ALTER TABLE team.teams
                    ADD CONSTRAINT fk_teams_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_teams_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_teams_area FOREIGN KEY (area_id) REFERENCES geo.areas (area_id) ON DELETE RESTRICT;

                ALTER TABLE team.team_members
                    ADD CONSTRAINT fk_team_members_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_team_members_team FOREIGN KEY (tenant_id, team_id) REFERENCES team.teams (tenant_id, team_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_team_members_user FOREIGN KEY (tenant_id, user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;

                ALTER TABLE team.tasks
                    ADD CONSTRAINT ck_tasks_has_assignee CHECK (team_id IS NOT NULL OR assignee_user_id IS NOT NULL),
                    ADD CONSTRAINT fk_tasks_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_tasks_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_tasks_team FOREIGN KEY (tenant_id, team_id) REFERENCES team.teams (tenant_id, team_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_tasks_assignee FOREIGN KEY (tenant_id, assignee_user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;

                ALTER TABLE team.trainings
                    ADD CONSTRAINT ck_trainings_valid_period CHECK (ends_at > starts_at),
                    ADD CONSTRAINT fk_trainings_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_trainings_election FOREIGN KEY (tenant_id, election_id) REFERENCES election.elections (tenant_id, election_id) ON DELETE RESTRICT;

                ALTER TABLE team.attendance
                    ADD CONSTRAINT fk_attendance_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_attendance_training FOREIGN KEY (tenant_id, training_id) REFERENCES team.trainings (tenant_id, training_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_attendance_user FOREIGN KEY (tenant_id, user_id) REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE RESTRICT;

                ALTER TABLE team.teams ENABLE ROW LEVEL SECURITY;
                ALTER TABLE team.teams FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_teams ON team.teams
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE team.team_members ENABLE ROW LEVEL SECURITY;
                ALTER TABLE team.team_members FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_team_members ON team.team_members
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE team.tasks ENABLE ROW LEVEL SECURITY;
                ALTER TABLE team.tasks FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_tasks ON team.tasks
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE team.trainings ENABLE ROW LEVEL SECURITY;
                ALTER TABLE team.trainings FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_trainings ON team.trainings
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

                ALTER TABLE team.attendance ENABLE ROW LEVEL SECURITY;
                ALTER TABLE team.attendance FORCE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation_attendance ON team.attendance
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                """
                DROP POLICY IF EXISTS tenant_isolation_attendance ON team.attendance;
                DROP POLICY IF EXISTS tenant_isolation_trainings ON team.trainings;
                DROP POLICY IF EXISTS tenant_isolation_tasks ON team.tasks;
                DROP POLICY IF EXISTS tenant_isolation_team_members ON team.team_members;
                DROP POLICY IF EXISTS tenant_isolation_teams ON team.teams;
                """);

            migrationBuilder.DropTable(
                name: "attendance",
                schema: "team");

            migrationBuilder.DropTable(
                name: "tasks",
                schema: "team");

            migrationBuilder.DropTable(
                name: "team_members",
                schema: "team");

            migrationBuilder.DropTable(
                name: "teams",
                schema: "team");

            migrationBuilder.DropTable(
                name: "trainings",
                schema: "team");

            migrationBuilder.DropTable(
                name: "task_priorities",
                schema: "team");

            migrationBuilder.DropTable(
                name: "task_states",
                schema: "team");
        }
    }
}
