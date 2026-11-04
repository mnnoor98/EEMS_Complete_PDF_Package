using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Identity.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddLocalAuthentication : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "password_credentials",
                schema: "iam",
                columns: table => new
                {
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    password_hash = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_password_credentials", x => x.user_id);
                    table.ForeignKey(
                        name: "FK_password_credentials_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "iam",
                        principalTable: "users",
                        principalColumn: "user_id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "refresh_tokens",
                schema: "iam",
                columns: table => new
                {
                    refresh_token_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    token_hash = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    expires_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    revoked_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    replaced_by_token_id = table.Column<Guid>(type: "uuid", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_refresh_tokens", x => x.refresh_token_id);
                    table.ForeignKey(
                        name: "FK_refresh_tokens_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "iam",
                        principalTable: "users",
                        principalColumn: "user_id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_refresh_tokens_tenant_id_token_hash",
                schema: "iam",
                table: "refresh_tokens",
                columns: new[] { "tenant_id", "token_hash" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_refresh_tokens_user_id",
                schema: "iam",
                table: "refresh_tokens",
                column: "user_id");

            migrationBuilder.Sql("""
                ALTER TABLE iam.refresh_tokens
                    ADD CONSTRAINT fk_refresh_tokens_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_refresh_tokens_tenant_user FOREIGN KEY (tenant_id, user_id)
                        REFERENCES iam.tenant_users (tenant_id, user_id) ON DELETE CASCADE,
                    ADD CONSTRAINT fk_refresh_tokens_replacement FOREIGN KEY (replaced_by_token_id)
                        REFERENCES iam.refresh_tokens (refresh_token_id) ON DELETE SET NULL,
                    ADD CONSTRAINT ck_refresh_tokens_expiry CHECK (expires_at > created_at),
                    ADD CONSTRAINT ck_refresh_tokens_revocation CHECK (revoked_at IS NULL OR revoked_at >= created_at);

                ALTER TABLE iam.refresh_tokens ENABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.refresh_tokens FORCE ROW LEVEL SECURITY;
                CREATE POLICY refresh_tokens_tenant_policy ON iam.refresh_tokens
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "password_credentials",
                schema: "iam");

            migrationBuilder.DropTable(
                name: "refresh_tokens",
                schema: "iam");
        }
    }
}
