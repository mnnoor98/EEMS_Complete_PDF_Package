using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Identity.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class IdentityTenantIsolation : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                ALTER TABLE iam.roles
                    ADD CONSTRAINT uq_roles_tenant_role UNIQUE (tenant_id, role_id),
                    ADD CONSTRAINT fk_roles_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT;

                ALTER TABLE iam.tenant_users
                    ADD CONSTRAINT fk_tenant_users_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT;

                ALTER TABLE iam.role_permissions
                    ADD CONSTRAINT fk_role_permissions_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_role_permissions_tenant_role FOREIGN KEY (tenant_id, role_id)
                        REFERENCES iam.roles (tenant_id, role_id) ON DELETE CASCADE;

                ALTER TABLE iam.user_roles
                    ADD CONSTRAINT fk_user_roles_tenant FOREIGN KEY (tenant_id)
                        REFERENCES core.tenants (tenant_id) ON DELETE RESTRICT,
                    ADD CONSTRAINT fk_user_roles_tenant_role FOREIGN KEY (tenant_id, role_id)
                        REFERENCES iam.roles (tenant_id, role_id) ON DELETE CASCADE;

                ALTER TABLE iam.roles ENABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.roles FORCE ROW LEVEL SECURITY;
                ALTER TABLE iam.tenant_users ENABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.tenant_users FORCE ROW LEVEL SECURITY;
                ALTER TABLE iam.role_permissions ENABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.role_permissions FORCE ROW LEVEL SECURITY;
                ALTER TABLE iam.user_roles ENABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.user_roles FORCE ROW LEVEL SECURITY;

                CREATE POLICY roles_tenant_policy ON iam.roles
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                CREATE POLICY tenant_users_tenant_policy ON iam.tenant_users
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                CREATE POLICY role_permissions_tenant_policy ON iam.role_permissions
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                CREATE POLICY user_roles_tenant_policy ON iam.user_roles
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
                    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("""
                DROP POLICY IF EXISTS user_roles_tenant_policy ON iam.user_roles;
                DROP POLICY IF EXISTS role_permissions_tenant_policy ON iam.role_permissions;
                DROP POLICY IF EXISTS tenant_users_tenant_policy ON iam.tenant_users;
                DROP POLICY IF EXISTS roles_tenant_policy ON iam.roles;

                ALTER TABLE iam.user_roles DISABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.role_permissions DISABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.tenant_users DISABLE ROW LEVEL SECURITY;
                ALTER TABLE iam.roles DISABLE ROW LEVEL SECURITY;

                ALTER TABLE iam.user_roles
                    DROP CONSTRAINT IF EXISTS fk_user_roles_tenant_role,
                    DROP CONSTRAINT IF EXISTS fk_user_roles_tenant;
                ALTER TABLE iam.role_permissions
                    DROP CONSTRAINT IF EXISTS fk_role_permissions_tenant_role,
                    DROP CONSTRAINT IF EXISTS fk_role_permissions_tenant;
                ALTER TABLE iam.tenant_users DROP CONSTRAINT IF EXISTS fk_tenant_users_tenant;
                ALTER TABLE iam.roles
                    DROP CONSTRAINT IF EXISTS fk_roles_tenant,
                    DROP CONSTRAINT IF EXISTS uq_roles_tenant_role;
                """);
        }
    }
}
