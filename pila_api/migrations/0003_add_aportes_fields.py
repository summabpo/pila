from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("pila_api", "0002_pilaplanilladetalle_pilanovedad"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE pila.pila_planilla_detalle
              ADD COLUMN IF NOT EXISTS aportes jsonb NOT NULL DEFAULT '{}'::jsonb;
            ALTER TABLE pila.pila_planilla_detalle
              ADD COLUMN IF NOT EXISTS aportes_empleado jsonb NOT NULL DEFAULT '{}'::jsonb;
            ALTER TABLE pila.pila_planilla_detalle
              ADD COLUMN IF NOT EXISTS aportes_empleador jsonb NOT NULL DEFAULT '{}'::jsonb;
            """,
            reverse_sql="""
            ALTER TABLE pila.pila_planilla_detalle
              DROP COLUMN IF EXISTS aportes;
            ALTER TABLE pila.pila_planilla_detalle
              DROP COLUMN IF EXISTS aportes_empleado;
            ALTER TABLE pila.pila_planilla_detalle
              DROP COLUMN IF EXISTS aportes_empleador;
            """,
        ),
    ]