using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace EEMS.Modules.Reporting.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialReporting : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "audit");

            migrationBuilder.CreateTable(
                name: "audit_logs",
                schema: "audit",
                columns: table => new
                {
                    audit_log_id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    actor_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    action = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    entity_type = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    entity_id = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    correlation_id = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    metadata_json = table.Column<string>(type: "jsonb", nullable: false),
                    occurred_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_audit_logs", x => x.audit_log_id);
                });

            migrationBuilder.CreateTable(
                name: "export_states",
                schema: "audit",
                columns: table => new
                {
                    export_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_export_states", x => x.export_state_id);
                });

            migrationBuilder.CreateTable(
                name: "outbox_messages",
                schema: "audit",
                columns: table => new
                {
                    outbox_message_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    message_type = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    payload_json = table.Column<string>(type: "jsonb", nullable: false),
                    correlation_id = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    occurred_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    processed_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_outbox_messages", x => x.outbox_message_id);
                });

            migrationBuilder.CreateTable(
                name: "security_events",
                schema: "audit",
                columns: table => new
                {
                    security_event_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    event_type = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    source = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    detail = table.Column<string>(type: "character varying(4000)", maxLength: 4000, nullable: false),
                    correlation_id = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    occurred_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_security_events", x => x.security_event_id);
                });

            migrationBuilder.CreateTable(
                name: "export_logs",
                schema: "audit",
                columns: table => new
                {
                    export_log_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    requested_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    export_state_id = table.Column<short>(type: "smallint", nullable: false),
                    report_type = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    format = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    filters_json = table.Column<string>(type: "jsonb", nullable: false),
                    correlation_id = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    storage_key = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true),
                    requested_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    completed_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_export_logs", x => x.export_log_id);
                    table.ForeignKey(
                        name: "FK_export_logs_export_states_export_state_id",
                        column: x => x.export_state_id,
                        principalSchema: "audit",
                        principalTable: "export_states",
                        principalColumn: "export_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_audit_logs_tenant_id_occurred_at",
                schema: "audit",
                table: "audit_logs",
                columns: new[] { "tenant_id", "occurred_at" });

            migrationBuilder.CreateIndex(
                name: "IX_export_logs_export_state_id",
                schema: "audit",
                table: "export_logs",
                column: "export_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_export_states_code",
                schema: "audit",
                table: "export_states",
                column: "code",
                unique: true);

            migrationBuilder.Sql(
                """
                ALTER TABLE audit.audit_logs ADD CONSTRAINT fk_audit_logs_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id), ADD CONSTRAINT fk_audit_logs_actor FOREIGN KEY(tenant_id,actor_user_id) REFERENCES iam.tenant_users(tenant_id,user_id);
                ALTER TABLE audit.security_events ADD CONSTRAINT fk_security_events_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id), ADD CONSTRAINT fk_security_events_user FOREIGN KEY(tenant_id,user_id) REFERENCES iam.tenant_users(tenant_id,user_id);
                ALTER TABLE audit.export_logs ADD CONSTRAINT fk_export_logs_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id), ADD CONSTRAINT fk_export_logs_user FOREIGN KEY(tenant_id,requested_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id);
                ALTER TABLE audit.outbox_messages ADD CONSTRAINT fk_outbox_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id);
                DO $rls$ DECLARE n text;BEGIN FOREACH n IN ARRAY ARRAY['audit_logs','security_events','export_logs','outbox_messages'] LOOP EXECUTE format('ALTER TABLE audit.%I ENABLE ROW LEVEL SECURITY',n);EXECUTE format('ALTER TABLE audit.%I FORCE ROW LEVEL SECURITY',n);EXECUTE format('CREATE POLICY tenant_isolation_%I ON audit.%I USING(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',n,n);END LOOP;END $rls$;
                CREATE FUNCTION audit.prevent_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $fn$ BEGIN RAISE EXCEPTION 'Audit records are append-only'; END $fn$;
                CREATE TRIGGER trg_audit_logs_immutable BEFORE UPDATE OR DELETE ON audit.audit_logs FOR EACH ROW EXECUTE FUNCTION audit.prevent_audit_mutation();
                CREATE TRIGGER trg_security_events_immutable BEFORE UPDATE OR DELETE ON audit.security_events FOR EACH ROW EXECUTE FUNCTION audit.prevent_audit_mutation();
                CREATE SCHEMA IF NOT EXISTS reporting;
                CREATE VIEW reporting.overview WITH (security_invoker=true) AS SELECT e.tenant_id,e.election_id,(SELECT count(*) FROM polling.election_centers c WHERE c.tenant_id=e.tenant_id AND c.election_id=e.election_id) center_count,(SELECT count(*) FROM operations.incidents i WHERE i.tenant_id=e.tenant_id AND i.election_id=e.election_id) incident_count,(SELECT count(*) FROM results.submissions r WHERE r.tenant_id=e.tenant_id AND r.election_id=e.election_id) result_submission_count FROM election.elections e;
                CREATE VIEW reporting.finance_summary WITH (security_invoker=true) AS SELECT tenant_id,count(*) expense_count,COALESCE(sum(amount),0) total_expense FROM finance.expenses GROUP BY tenant_id;
                CREATE VIEW reporting.incident_summary WITH (security_invoker=true) AS SELECT tenant_id,election_id,incident_state_id,incident_severity_id,count(*) incident_count FROM operations.incidents GROUP BY tenant_id,election_id,incident_state_id,incident_severity_id;
                CREATE VIEW reporting.result_summary WITH (security_invoker=true) AS SELECT tenant_id,election_id,submission_state_id,count(*) submission_count,COALESCE(sum(declared_total_votes),0) declared_votes FROM results.submissions GROUP BY tenant_id,election_id,submission_state_id;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("DROP VIEW IF EXISTS reporting.result_summary; DROP VIEW IF EXISTS reporting.incident_summary; DROP VIEW IF EXISTS reporting.finance_summary; DROP VIEW IF EXISTS reporting.overview; DROP TRIGGER IF EXISTS trg_security_events_immutable ON audit.security_events; DROP TRIGGER IF EXISTS trg_audit_logs_immutable ON audit.audit_logs; DROP FUNCTION IF EXISTS audit.prevent_audit_mutation();");

            migrationBuilder.DropTable(
                name: "audit_logs",
                schema: "audit");

            migrationBuilder.DropTable(
                name: "export_logs",
                schema: "audit");

            migrationBuilder.DropTable(
                name: "outbox_messages",
                schema: "audit");

            migrationBuilder.DropTable(
                name: "security_events",
                schema: "audit");

            migrationBuilder.DropTable(
                name: "export_states",
                schema: "audit");
        }
    }
}
