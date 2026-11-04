using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Results.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialResults : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "results");

            migrationBuilder.CreateTable(
                name: "details",
                schema: "results",
                columns: table => new
                {
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    submission_id = table.Column<Guid>(type: "uuid", nullable: false),
                    candidate_election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    votes = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_details", x => new { x.tenant_id, x.submission_id, x.candidate_election_id });
                });

            migrationBuilder.CreateTable(
                name: "disputes",
                schema: "results",
                columns: table => new
                {
                    dispute_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    submission_id = table.Column<Guid>(type: "uuid", nullable: false),
                    RaisedByUserId = table.Column<Guid>(type: "uuid", nullable: false),
                    Reason = table.Column<string>(type: "text", nullable: false),
                    RaisedAtUtc = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_disputes", x => x.dispute_id);
                });

            migrationBuilder.CreateTable(
                name: "documents",
                schema: "results",
                columns: table => new
                {
                    result_document_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    submission_id = table.Column<Guid>(type: "uuid", nullable: false),
                    UploadedByUserId = table.Column<Guid>(type: "uuid", nullable: false),
                    StorageKey = table.Column<string>(type: "text", nullable: false),
                    Sha256 = table.Column<string>(type: "text", nullable: false),
                    MimeType = table.Column<string>(type: "text", nullable: false),
                    SizeBytes = table.Column<long>(type: "bigint", nullable: false),
                    UploadedAtUtc = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_documents", x => x.result_document_id);
                });

            migrationBuilder.CreateTable(
                name: "official_results",
                schema: "results",
                columns: table => new
                {
                    official_result_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    position_id = table.Column<long>(type: "bigint", nullable: false),
                    candidate_election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    votes = table.Column<long>(type: "bigint", nullable: false),
                    authority_source = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    published_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    published_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_official_results", x => x.official_result_id);
                });

            migrationBuilder.CreateTable(
                name: "submission_states",
                schema: "results",
                columns: table => new
                {
                    submission_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_verified = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_submission_states", x => x.submission_state_id);
                });

            migrationBuilder.CreateTable(
                name: "verifications",
                schema: "results",
                columns: table => new
                {
                    verification_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    submission_id = table.Column<Guid>(type: "uuid", nullable: false),
                    SubmitterUserId = table.Column<Guid>(type: "uuid", nullable: false),
                    VerifierUserId = table.Column<Guid>(type: "uuid", nullable: false),
                    ResultingStateId = table.Column<short>(type: "smallint", nullable: false),
                    Note = table.Column<string>(type: "text", nullable: false),
                    VerifiedAtUtc = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_verifications", x => x.verification_id);
                });

            migrationBuilder.CreateTable(
                name: "submissions",
                schema: "results",
                columns: table => new
                {
                    submission_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_center_id = table.Column<Guid>(type: "uuid", nullable: false),
                    position_id = table.Column<long>(type: "bigint", nullable: false),
                    submitted_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    submission_state_id = table.Column<short>(type: "smallint", nullable: false),
                    idempotency_key = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    declared_total_votes = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_submissions", x => x.submission_id);
                    table.ForeignKey(
                        name: "FK_submissions_submission_states_submission_state_id",
                        column: x => x.submission_state_id,
                        principalSchema: "results",
                        principalTable: "submission_states",
                        principalColumn: "submission_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_official_results_tenant_id_election_id_position_id_candidat~",
                schema: "results",
                table: "official_results",
                columns: new[] { "tenant_id", "election_id", "position_id", "candidate_election_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_submission_states_code",
                schema: "results",
                table: "submission_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_submissions_submission_state_id",
                schema: "results",
                table: "submissions",
                column: "submission_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_submissions_tenant_id_election_id_election_center_id_positi~",
                schema: "results",
                table: "submissions",
                columns: new[] { "tenant_id", "election_id", "election_center_id", "position_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_submissions_tenant_id_idempotency_key",
                schema: "results",
                table: "submissions",
                columns: new[] { "tenant_id", "idempotency_key" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_submissions_tenant_id_submission_id",
                schema: "results",
                table: "submissions",
                columns: new[] { "tenant_id", "submission_id" },
                unique: true);

            migrationBuilder.Sql(
                """
                ALTER TABLE results.submissions ADD CONSTRAINT ck_submissions_total CHECK(declared_total_votes>=0), ADD CONSTRAINT fk_submissions_tenant FOREIGN KEY(tenant_id) REFERENCES core.tenants(tenant_id), ADD CONSTRAINT fk_submissions_election FOREIGN KEY(tenant_id,election_id) REFERENCES election.elections(tenant_id,election_id), ADD CONSTRAINT fk_submissions_center FOREIGN KEY(tenant_id,election_id,election_center_id) REFERENCES polling.election_centers(tenant_id,election_id,election_center_id), ADD CONSTRAINT fk_submissions_position FOREIGN KEY(position_id) REFERENCES election.positions(position_id), ADD CONSTRAINT fk_submissions_user FOREIGN KEY(tenant_id,submitted_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id);
                ALTER TABLE results.details ADD CONSTRAINT ck_details_votes CHECK(votes>=0), ADD CONSTRAINT fk_details_submission FOREIGN KEY(tenant_id,submission_id) REFERENCES results.submissions(tenant_id,submission_id) ON DELETE CASCADE, ADD CONSTRAINT fk_details_candidate FOREIGN KEY(tenant_id,candidate_election_id) REFERENCES election.candidate_elections(tenant_id,candidate_election_id);
                ALTER TABLE results.verifications ADD CONSTRAINT ck_verifier_separation CHECK("SubmitterUserId"<>"VerifierUserId");
                ALTER TABLE results.official_results ADD CONSTRAINT ck_official_votes CHECK(votes>=0), ADD CONSTRAINT fk_official_candidate FOREIGN KEY(tenant_id,candidate_election_id) REFERENCES election.candidate_elections(tenant_id,candidate_election_id);
                DO $rls$ DECLARE n text;BEGIN FOREACH n IN ARRAY ARRAY['submissions','details','documents','verifications','disputes','official_results'] LOOP EXECUTE format('ALTER TABLE results.%I ENABLE ROW LEVEL SECURITY',n);EXECUTE format('ALTER TABLE results.%I FORCE ROW LEVEL SECURITY',n);EXECUTE format('CREATE POLICY tenant_isolation_%I ON results.%I USING(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK(tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',n,n);END LOOP;END $rls$;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "details",
                schema: "results");

            migrationBuilder.DropTable(
                name: "disputes",
                schema: "results");

            migrationBuilder.DropTable(
                name: "documents",
                schema: "results");

            migrationBuilder.DropTable(
                name: "official_results",
                schema: "results");

            migrationBuilder.DropTable(
                name: "submissions",
                schema: "results");

            migrationBuilder.DropTable(
                name: "verifications",
                schema: "results");

            migrationBuilder.DropTable(
                name: "submission_states",
                schema: "results");
        }
    }
}
