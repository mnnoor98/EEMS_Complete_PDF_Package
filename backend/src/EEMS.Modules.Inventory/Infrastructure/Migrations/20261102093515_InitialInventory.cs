using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Inventory.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialInventory : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "inventory");

            migrationBuilder.CreateTable(
                name: "allocation_states",
                schema: "inventory",
                columns: table => new
                {
                    allocation_state_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    is_terminal = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_allocation_states", x => x.allocation_state_id);
                });

            migrationBuilder.CreateTable(
                name: "items",
                schema: "inventory",
                columns: table => new
                {
                    item_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    sku = table.Column<string>(type: "character varying(80)", maxLength: 80, nullable: false),
                    name = table.Column<string>(type: "character varying(180)", maxLength: 180, nullable: false),
                    unit = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_items", x => x.item_id);
                });

            migrationBuilder.CreateTable(
                name: "movement_types",
                schema: "inventory",
                columns: table => new
                {
                    movement_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    requires_source = table.Column<bool>(type: "boolean", nullable: false),
                    requires_destination = table.Column<bool>(type: "boolean", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_movement_types", x => x.movement_type_id);
                });

            migrationBuilder.CreateTable(
                name: "warehouses",
                schema: "inventory",
                columns: table => new
                {
                    warehouse_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    name = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_warehouses", x => x.warehouse_id);
                });

            migrationBuilder.CreateTable(
                name: "allocations",
                schema: "inventory",
                columns: table => new
                {
                    allocation_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    election_id = table.Column<Guid>(type: "uuid", nullable: false),
                    item_id = table.Column<Guid>(type: "uuid", nullable: false),
                    source_warehouse_id = table.Column<Guid>(type: "uuid", nullable: false),
                    team_id = table.Column<Guid>(type: "uuid", nullable: true),
                    polling_center_id = table.Column<Guid>(type: "uuid", nullable: true),
                    recipient_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    allocation_state_id = table.Column<short>(type: "smallint", nullable: false),
                    quantity = table.Column<decimal>(type: "numeric(18,3)", precision: 18, scale: 3, nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    acknowledged_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_allocations", x => x.allocation_id);
                    table.ForeignKey(
                        name: "FK_allocations_allocation_states_allocation_state_id",
                        column: x => x.allocation_state_id,
                        principalSchema: "inventory",
                        principalTable: "allocation_states",
                        principalColumn: "allocation_state_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "stock_movements",
                schema: "inventory",
                columns: table => new
                {
                    movement_id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    item_id = table.Column<Guid>(type: "uuid", nullable: false),
                    movement_type_id = table.Column<short>(type: "smallint", nullable: false),
                    source_warehouse_id = table.Column<Guid>(type: "uuid", nullable: true),
                    destination_warehouse_id = table.Column<Guid>(type: "uuid", nullable: true),
                    actor_user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    quantity = table.Column<decimal>(type: "numeric(18,3)", precision: 18, scale: 3, nullable: false),
                    reference = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    occurred_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_stock_movements", x => x.movement_id);
                    table.ForeignKey(
                        name: "FK_stock_movements_movement_types_movement_type_id",
                        column: x => x.movement_type_id,
                        principalSchema: "inventory",
                        principalTable: "movement_types",
                        principalColumn: "movement_type_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_allocation_states_code",
                schema: "inventory",
                table: "allocation_states",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_allocations_allocation_state_id",
                schema: "inventory",
                table: "allocations",
                column: "allocation_state_id");

            migrationBuilder.CreateIndex(
                name: "IX_allocations_tenant_id_election_id_allocation_state_id",
                schema: "inventory",
                table: "allocations",
                columns: new[] { "tenant_id", "election_id", "allocation_state_id" });

            migrationBuilder.CreateIndex(
                name: "IX_items_tenant_id_item_id",
                schema: "inventory",
                table: "items",
                columns: new[] { "tenant_id", "item_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_items_tenant_id_sku",
                schema: "inventory",
                table: "items",
                columns: new[] { "tenant_id", "sku" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_movement_types_code",
                schema: "inventory",
                table: "movement_types",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_stock_movements_movement_type_id",
                schema: "inventory",
                table: "stock_movements",
                column: "movement_type_id");

            migrationBuilder.CreateIndex(
                name: "IX_stock_movements_tenant_id_item_id_occurred_at",
                schema: "inventory",
                table: "stock_movements",
                columns: new[] { "tenant_id", "item_id", "occurred_at" });

            migrationBuilder.CreateIndex(
                name: "IX_stock_movements_tenant_id_reference",
                schema: "inventory",
                table: "stock_movements",
                columns: new[] { "tenant_id", "reference" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_warehouses_tenant_id_area_id_name",
                schema: "inventory",
                table: "warehouses",
                columns: new[] { "tenant_id", "area_id", "name" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_warehouses_tenant_id_warehouse_id",
                schema: "inventory",
                table: "warehouses",
                columns: new[] { "tenant_id", "warehouse_id" },
                unique: true);

            migrationBuilder.Sql(
                """
                CREATE UNIQUE INDEX ux_polling_election_centers_tenant_election_center
                    ON polling.election_centers (tenant_id,election_id,election_center_id);
                ALTER TABLE inventory.items ADD CONSTRAINT fk_items_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT;
                ALTER TABLE inventory.warehouses ADD CONSTRAINT fk_warehouses_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_warehouses_area FOREIGN KEY (area_id) REFERENCES geo.areas(area_id) ON DELETE RESTRICT;
                ALTER TABLE inventory.stock_movements ADD CONSTRAINT ck_movements_quantity CHECK (quantity>0), ADD CONSTRAINT ck_movements_endpoints CHECK ((source_warehouse_id IS NOT NULL OR destination_warehouse_id IS NOT NULL) AND source_warehouse_id IS DISTINCT FROM destination_warehouse_id), ADD CONSTRAINT fk_movements_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_movements_item FOREIGN KEY (tenant_id,item_id) REFERENCES inventory.items(tenant_id,item_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_movements_source FOREIGN KEY (tenant_id,source_warehouse_id) REFERENCES inventory.warehouses(tenant_id,warehouse_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_movements_destination FOREIGN KEY (tenant_id,destination_warehouse_id) REFERENCES inventory.warehouses(tenant_id,warehouse_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_movements_actor FOREIGN KEY (tenant_id,actor_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;
                ALTER TABLE inventory.allocations ADD CONSTRAINT ck_allocations_quantity CHECK (quantity>0), ADD CONSTRAINT ck_allocations_destination CHECK (team_id IS NOT NULL OR polling_center_id IS NOT NULL), ADD CONSTRAINT fk_allocations_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_election FOREIGN KEY (tenant_id,election_id) REFERENCES election.elections(tenant_id,election_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_item FOREIGN KEY (tenant_id,item_id) REFERENCES inventory.items(tenant_id,item_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_warehouse FOREIGN KEY (tenant_id,source_warehouse_id) REFERENCES inventory.warehouses(tenant_id,warehouse_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_team FOREIGN KEY (tenant_id,team_id) REFERENCES team.teams(tenant_id,team_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_center FOREIGN KEY (tenant_id,election_id,polling_center_id) REFERENCES polling.election_centers(tenant_id,election_id,election_center_id) ON DELETE RESTRICT, ADD CONSTRAINT fk_allocations_recipient FOREIGN KEY (tenant_id,recipient_user_id) REFERENCES iam.tenant_users(tenant_id,user_id) ON DELETE RESTRICT;

                CREATE FUNCTION inventory.validate_stock_movement() RETURNS trigger LANGUAGE plpgsql AS $fn$
                DECLARE movement inventory.movement_types; balance numeric(18,3);
                BEGIN
                  SELECT * INTO movement FROM inventory.movement_types WHERE movement_type_id=NEW.movement_type_id;
                  IF movement.requires_source AND NEW.source_warehouse_id IS NULL THEN RAISE EXCEPTION 'Source warehouse is required'; END IF;
                  IF movement.requires_destination AND NEW.destination_warehouse_id IS NULL THEN RAISE EXCEPTION 'Destination warehouse is required'; END IF;
                  IF NEW.source_warehouse_id IS NOT NULL THEN
                    SELECT COALESCE(SUM(CASE WHEN destination_warehouse_id=NEW.source_warehouse_id THEN quantity ELSE 0 END)-SUM(CASE WHEN source_warehouse_id=NEW.source_warehouse_id THEN quantity ELSE 0 END),0) INTO balance FROM inventory.stock_movements WHERE tenant_id=NEW.tenant_id AND item_id=NEW.item_id;
                    IF balance < NEW.quantity THEN RAISE EXCEPTION 'Insufficient stock'; END IF;
                  END IF;
                  RETURN NEW;
                END $fn$;
                CREATE TRIGGER trg_validate_stock_movement BEFORE INSERT ON inventory.stock_movements FOR EACH ROW EXECUTE FUNCTION inventory.validate_stock_movement();

                DO $rls$ DECLARE n text; BEGIN FOREACH n IN ARRAY ARRAY['items','warehouses','stock_movements','allocations'] LOOP EXECUTE format('ALTER TABLE inventory.%I ENABLE ROW LEVEL SECURITY',n);EXECUTE format('ALTER TABLE inventory.%I FORCE ROW LEVEL SECURITY',n);EXECUTE format('CREATE POLICY tenant_isolation_%I ON inventory.%I USING (tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid) WITH CHECK (tenant_id=NULLIF(current_setting(''app.tenant_id'',true),'''')::uuid)',n,n);END LOOP;END $rls$;
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                """
                DROP TRIGGER IF EXISTS trg_validate_stock_movement ON inventory.stock_movements;
                DROP FUNCTION IF EXISTS inventory.validate_stock_movement();
                ALTER TABLE inventory.allocations DROP CONSTRAINT IF EXISTS fk_allocations_item, DROP CONSTRAINT IF EXISTS fk_allocations_warehouse, DROP CONSTRAINT IF EXISTS fk_allocations_team, DROP CONSTRAINT IF EXISTS fk_allocations_center;
                ALTER TABLE inventory.stock_movements DROP CONSTRAINT IF EXISTS fk_movements_item, DROP CONSTRAINT IF EXISTS fk_movements_source, DROP CONSTRAINT IF EXISTS fk_movements_destination;
                DROP INDEX IF EXISTS polling.ux_polling_election_centers_tenant_election_center;
                """);

            migrationBuilder.DropTable(
                name: "allocations",
                schema: "inventory");

            migrationBuilder.DropTable(
                name: "items",
                schema: "inventory");

            migrationBuilder.DropTable(
                name: "stock_movements",
                schema: "inventory");

            migrationBuilder.DropTable(
                name: "warehouses",
                schema: "inventory");

            migrationBuilder.DropTable(
                name: "allocation_states",
                schema: "inventory");

            migrationBuilder.DropTable(
                name: "movement_types",
                schema: "inventory");
        }
    }
}
