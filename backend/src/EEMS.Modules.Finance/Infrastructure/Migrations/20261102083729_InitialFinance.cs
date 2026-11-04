using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Finance.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialFinance : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "finance");

            migrationBuilder.CreateTable(
                name: "adjustments",
                schema: "finance",
                columns: table => new
                {
                    adjustment_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    expense_id = table.Column<Guid>(type: "uuid", nullable: false),
                    created_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    amount = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    reason = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_adjustments", x => x.adjustment_id);
                });

            migrationBuilder.CreateTable(
                name: "budget_lines",
                schema: "finance",
                columns: table => new
                {
                    budget_line_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    budget_id = table.Column<Guid>(type: "uuid", nullable: false),
                    category = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    allocated_amount = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_budget_lines", x => x.budget_line_id);
                });

            migrationBuilder.CreateTable(
                name: "budgets",
                schema: "finance",
                columns: table => new
                {
                    budget_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    name = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    currency = table.Column<string>(type: "character varying(3)", maxLength: 3, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_budgets", x => x.budget_id);
                });

            migrationBuilder.CreateTable(
                name: "expense_states",
                schema: "finance",
                columns: table => new
                {
                    expense_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_approved = table.Column<bool>(type: "boolean", nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_expense_states", x => x.expense_state_id);
                });

            migrationBuilder.CreateTable(
                name: "payments",
                schema: "finance",
                columns: table => new
                {
                    payment_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    expense_id = table.Column<Guid>(type: "uuid", nullable: false),
                    paid_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    amount = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    reference = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    paid_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_payments", x => x.payment_id);
                });

            migrationBuilder.CreateTable(
                name: "vendors",
                schema: "finance",
                columns: table => new
                {
                    vendor_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    name = table.Column<string>(type: "character varying(180)", maxLength: 180, nullable: false),
                    registration_number = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_vendors", x => x.vendor_id);
                });

            migrationBuilder.CreateTable(
                name: "approvals",
                schema: "finance",
                columns: table => new
                {
                    approval_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    expense_id = table.Column<Guid>(type: "uuid", nullable: false),
                    maker_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    checker_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    resulting_state_id = table.Column<short>(type: "smallint", nullable: false),
                    note = table.Column<string>(type: "character varying(1000)", maxLength: 1000, nullable: false),
                    decided_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_approvals", x => x.approval_id);
                    table.ForeignKey(
                        name: "FK_approvals_expense_states_resulting_state_id",
                        column: x => x.resulting_state_id,
                        principalSchema: "finance",
                        principalTable: "expense_states",
                        principalColumn: "expense_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "expenses",
                schema: "finance",
                columns: table => new
                {
                    expense_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    budget_line_id = table.Column<Guid>(type: "uuid", nullable: false),
                    vendor_id = table.Column<Guid>(type: "uuid", nullable: true),
                    submitted_by_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    expense_state_id = table.Column<short>(type: "smallint", nullable: false),
                    invoice_number = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    amount = table.Column<decimal>(type: "numeric(18,2)", precision: 18, scale: 2, nullable: false),
                    expense_date = table.Column<DateOnly>(type: "date", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    version = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_expenses", x => x.expense_id);
                    table.ForeignKey(
                        name: "FK_expenses_expense_states_expense_state_id",
                        column: x => x.expense_state_id,
                        principalSchema: "finance",
                        principalTable: "expense_states",
                        principalColumn: "expense_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_approvals_resulting_state_id",
                schema: "finance",
                table: "approvals",
                column: "resulting_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_budget_lines_tenant_id_budget_id_category",
                schema: "finance",
                table: "budget_lines",
                columns: new[] { "tenant_id", "budget_id", "category" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_budget_lines_tenant_id_budget_line_id",
                schema: "finance",
                table: "budget_lines",
                columns: new[] { "tenant_id", "budget_line_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_budgets_tenant_id_budget_id",
                schema: "finance",
                table: "budgets",
                columns: new[] { "tenant_id", "budget_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_budgets_tenant_id_election_id_name",
                schema: "finance",
                table: "budgets",
                columns: new[] { "tenant_id", "election_id", "name" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_expense_states_code",
                schema: "finance",
                table: "expense_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_expenses_expense_state_id",
                schema: "finance",
                table: "expenses",
                column: "expense_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_expenses_tenant_id_expense_id",
                schema: "finance",
                table: "expenses",
                columns: new[] { "tenant_id", "expense_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_expenses_tenant_id_vendor_id_invoice_number",
                schema: "finance",
                table: "expenses",
                columns: new[] { "tenant_id", "vendor_id", "invoice_number" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_payments_tenant_id_reference",
                schema: "finance",
                table: "payments",
                columns: new[] { "tenant_id", "reference" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_vendors_tenant_id_registration_number",
                schema: "finance",
                table: "vendors",
                columns: new[] { "tenant_id", "registration_number" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_vendors_tenant_id_vendor_id",
                schema: "finance",
                table: "vendors",
                columns: new[] { "tenant_id", "vendor_id" },
                unique: true);

            migrationBuilder.Sql(
                """
                ALTER TABLE finance.budgets ADD CONSTRAINT fk_budgets_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_budgets_election FOREIGN KEY (tenant_id,election_id) REFERENCES election.elections(tenant_id,election_id) ON DELETE RESTRICT;
                ALTER TABLE finance.budget_lines ADD CONSTRAINT ck_budget_lines_amount CHECK (allocated_amount > 0), ADD CONSTRAINT fk_budget_lines_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_budget_lines_budget FOREIGN KEY (tenant_id,budget_id) REFERENCES finance.budgets(tenant_id,budget_id) ON DELETE CASCADE;
                ALTER TABLE finance.vendors ADD CONSTRAINT fk_vendors_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT;
                ALTER TABLE finance.expenses ADD CONSTRAINT ck_expenses_amount CHECK (amount > 0), ADD CONSTRAINT fk_expenses_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_expenses_budget_line FOREIGN KEY (tenant_id,budget_line_id) REFERENCES finance.budget_lines(tenant_id,budget_line_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_expenses_vendor FOREIGN KEY (tenant_id,vendor_id) REFERENCES finance.vendors(tenant_id,vendor_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_expenses_submitter FOREIGN KEY (tenant_id,submitted_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE finance.approvals ADD CONSTRAINT ck_approvals_maker_checker CHECK (maker_user_id <> checker_user_id), ADD CONSTRAINT fk_approvals_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_approvals_expense FOREIGN KEY (tenant_id,expense_id) REFERENCES finance.expenses(tenant_id,expense_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_approvals_maker FOREIGN KEY (tenant_id,maker_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_approvals_checker FOREIGN KEY (tenant_id,checker_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE finance.payments ADD CONSTRAINT ck_payments_amount CHECK (amount > 0), ADD CONSTRAINT fk_payments_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_payments_expense FOREIGN KEY (tenant_id,expense_id) REFERENCES finance.expenses(tenant_id,expense_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_payments_user FOREIGN KEY (tenant_id,paid_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE finance.adjustments ADD CONSTRAINT ck_adjustments_nonzero CHECK (amount <> 0), ADD CONSTRAINT fk_adjustments_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_adjustments_expense FOREIGN KEY (tenant_id,expense_id) REFERENCES finance.expenses(tenant_id,expense_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_adjustments_user FOREIGN KEY (tenant_id,created_by_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;

                DO $rls$ DECLARE table_name text; BEGIN
                  FOREACH table_name IN ARRAY ARRAY['budgets','budget_lines','vendors','expenses','approvals','payments','adjustments'] LOOP
                    EXECUTE format('ALTER TABLE finance.%I ENABLE ROW LEVEL SECURITY',table_name);
                    EXECUTE format('ALTER TABLE finance.%I FORCE ROW LEVEL SECURITY',table_name);
                    EXECUTE format('CREATE POLICY tenant_isolation_%I ON finance.%I USING (tenant_id = NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',table_name,table_name);
                  END LOOP;
                END $rls$;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                """
                ALTER TABLE finance.adjustments DROP CONSTRAINT IF EXISTS fk_adjustments_expense;
                ALTER TABLE finance.approvals DROP CONSTRAINT IF EXISTS fk_approvals_expense;
                ALTER TABLE finance.payments DROP CONSTRAINT IF EXISTS fk_payments_expense;
                ALTER TABLE finance.expenses DROP CONSTRAINT IF EXISTS fk_expenses_budget_line, DROP CONSTRAINT IF EXISTS fk_expenses_vendor;
                ALTER TABLE finance.budget_lines DROP CONSTRAINT IF EXISTS fk_budget_lines_budget;
                """);

            migrationBuilder.DropTable(
                name: "adjustments",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "approvals",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "budget_lines",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "budgets",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "expenses",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "payments",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "vendors",
                schema: "finance");

            migrationBuilder.DropTable(
                name: "expense_states",
                schema: "finance");
        }
    }
}
