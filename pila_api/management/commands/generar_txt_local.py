# pila_api/management/commands/generar_txt_local.py
"""
Genera el TXT PILA localmente (sin API) y lo guarda.
Útil cuando el microservicio no está actualizado o para pruebas.

Uso:
  python manage.py generar_txt_local --planilla-id 1 --tipo-planilla E
  python manage.py generar_txt_local --planilla-id 1 --output ../nomiweb/nomiweb/apps/pila/archivos/PILA_E.txt
"""

from django.core.management.base import BaseCommand
from pila_api.services.generar_txt import generar_txt_planilla


class Command(BaseCommand):
    help = "Genera el TXT PILA localmente (sin llamar al API)"

    def add_arguments(self, parser):
        parser.add_argument("--planilla-id", type=int, required=True)
        parser.add_argument("--tipo-planilla", type=str, choices=["K", "E"], default=None)
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Ruta de salida. Por defecto: pila_api/scripts/generado_planilla_<id>.txt",
        )

    def handle(self, *args, **options):
        planilla_id = options["planilla_id"]
        tipo = options["tipo_planilla"]
        output = options["output"]

        self.stdout.write(f"Generando TXT para planilla {planilla_id}...")
        contenido = generar_txt_planilla(planilla_id, filtro_tipo_planilla=tipo)

        if not output:
            output = f"pila_api/scripts/generado_planilla_{planilla_id}.txt"
            if tipo:
                output = output.replace(".txt", f"_{tipo}.txt")

        with open(output, "w", encoding="iso-8859-1") as f:
            f.write(contenido)

        lineas = len(contenido.split("\n"))
        self.stdout.write(self.style.SUCCESS(f"✓ Guardado: {output} ({lineas} líneas)"))
