using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace EEMS.Modules.Geography.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class InitialGeography : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.EnsureSchema(
                name: "geo");

            migrationBuilder.CreateTable(
                name: "area_types",
                schema: "geo",
                columns: table => new
                {
                    area_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    level = table.Column<short>(type: "smallint", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_area_types", x => x.area_type_id);
                });

            migrationBuilder.CreateTable(
                name: "areas",
                schema: "geo",
                columns: table => new
                {
                    area_id = table.Column<long>(type: "bigint", nullable: false),
                    parent_area_id = table.Column<long>(type: "bigint", nullable: true),
                    area_type_id = table.Column<short>(type: "smallint", nullable: false),
                    code = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    name_bn = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    name_en = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    is_active = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_areas", x => x.area_id);
                    table.ForeignKey(
                        name: "FK_areas_area_types_area_type_id",
                        column: x => x.area_type_id,
                        principalSchema: "geo",
                        principalTable: "area_types",
                        principalColumn: "area_type_id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_areas_areas_parent_area_id",
                        column: x => x.parent_area_id,
                        principalSchema: "geo",
                        principalTable: "areas",
                        principalColumn: "area_id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_area_types_code",
                schema: "geo",
                table: "area_types",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_area_types_level",
                schema: "geo",
                table: "area_types",
                column: "level",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_areas_area_type_id_code",
                schema: "geo",
                table: "areas",
                columns: new[] { "area_type_id", "code" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_areas_parent_area_id",
                schema: "geo",
                table: "areas",
                column: "parent_area_id");

            migrationBuilder.Sql("""
                CREATE OR REPLACE FUNCTION geo.prevent_area_cycle()
                RETURNS trigger LANGUAGE plpgsql AS $$
                DECLARE cycle_found boolean;
                BEGIN
                    IF NEW.parent_area_id IS NULL THEN RETURN NEW; END IF;
                    WITH RECURSIVE ancestors AS (
                        SELECT area_id, parent_area_id FROM geo.areas WHERE area_id = NEW.parent_area_id
                        UNION ALL
                        SELECT a.area_id, a.parent_area_id FROM geo.areas a
                        JOIN ancestors x ON a.area_id = x.parent_area_id
                    )
                    SELECT EXISTS (SELECT 1 FROM ancestors WHERE area_id = NEW.area_id) INTO cycle_found;
                    IF cycle_found THEN RAISE EXCEPTION 'Area hierarchy cycle is not allowed'; END IF;
                    RETURN NEW;
                END $$;
                CREATE TRIGGER trg_prevent_area_cycle
                    BEFORE INSERT OR UPDATE OF parent_area_id ON geo.areas
                    FOR EACH ROW EXECUTE FUNCTION geo.prevent_area_cycle();
                """);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("DROP TRIGGER IF EXISTS trg_prevent_area_cycle ON geo.areas; DROP FUNCTION IF EXISTS geo.prevent_area_cycle();");

            migrationBuilder.DropTable(
                name: "areas",
                schema: "geo");

            migrationBuilder.DropTable(
                name: "area_types",
                schema: "geo");
        }
    }
}
