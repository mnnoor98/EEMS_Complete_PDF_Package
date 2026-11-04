using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Identity.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddPasswordSecurity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "failed_login_count",
                schema: "iam",
                table: "password_credentials",
                type: "integer",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "lockout_end",
                schema: "iam",
                table: "password_credentials",
                type: "timestamp with time zone",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "must_change_password",
                schema: "iam",
                table: "password_credentials",
                type: "boolean",
                nullable: false,
                defaultValue: true);

            migrationBuilder.Sql("""
                ALTER TABLE iam.password_credentials
                    ADD CONSTRAINT ck_password_credentials_failed_login_count
                    CHECK (failed_login_count >= 0);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "failed_login_count",
                schema: "iam",
                table: "password_credentials");

            migrationBuilder.DropColumn(
                name: "lockout_end",
                schema: "iam",
                table: "password_credentials");

            migrationBuilder.DropColumn(
                name: "must_change_password",
                schema: "iam",
                table: "password_credentials");
        }
    }
}
