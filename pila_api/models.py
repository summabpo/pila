from django.db import models


class PilaPlanilla(models.Model):
    ESTADOS = (
        ("EN_PROCESO", "EN_PROCESO"),
        ("COMPLETADA", "COMPLETADA"),
        ("CON_ERRORES", "CON_ERRORES"),
    )

    planilla_id = models.AutoField(primary_key=True)
    numero_interno = models.CharField(max_length=50, unique=True)

    periodo = models.CharField(max_length=7)  # YYYY-MM
    empresa_nit = models.CharField(max_length=20)
    empresa_sucursal = models.CharField(max_length=5)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="EN_PROCESO")

    payload_inicial = models.JSONField(null=True, blank=True)

    totales = models.JSONField(null=True, blank=True)
    resumen = models.JSONField(null=True, blank=True)
    errores = models.JSONField(default=list, blank=True)
    tiene_archivo = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pila"."pila_planilla'


class PilaPlanillaDetalle(models.Model):
    ESTADOS = (
        ("OK", "OK"),
        ("CON_ERROR", "CON_ERROR"),
    )

    id = models.AutoField(primary_key=True)

    planilla = models.ForeignKey(
        PilaPlanilla,
        on_delete=models.CASCADE,
        related_name="detalles",
    )

    tipo_doc = models.CharField(max_length=3)
    numero_doc = models.CharField(max_length=20)

    primer_nombre = models.CharField(max_length=50)
    primer_apellido = models.CharField(max_length=50)

    tipo_cotizante = models.CharField(max_length=2)
    subtipo_cotizante = models.CharField(max_length=2, null=True, blank=True)

    dias_cotizados = models.PositiveSmallIntegerField()
    
    dias_salud = models.PositiveSmallIntegerField(default=0)
    dias_pension = models.PositiveSmallIntegerField(default=0)
    dias_arl = models.PositiveSmallIntegerField(default=0)
    dias_caja = models.PositiveSmallIntegerField(default=0)

    ibc = models.DecimalField(max_digits=12, decimal_places=2)
    ibc_salud = models.DecimalField(max_digits=12, decimal_places=2)
    ibc_pension = models.DecimalField(max_digits=12, decimal_places=2)
    ibc_arl = models.DecimalField(max_digits=12, decimal_places=2)

    riesgo_arl = models.CharField(max_length=1)
    caja_compensacion = models.BooleanField(default=True)

    estado = models.CharField(max_length=10, choices=ESTADOS, default="OK")
    errores = models.JSONField(default=list, blank=True)

    aportes = models.JSONField(default=dict, blank=True)
    aportes_empleador = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    aportes_empleado = models.DecimalField(max_digits=14, decimal_places=2, default=0)


    class Meta:
        db_table = 'pila"."pila_planilla_detalle'
        # NOTA: Se eliminó la restricción UNIQUE para permitir múltiples registros por empleado
        # (necesario para generar múltiples líneas tipo 02 cuando hay novedades como VAC, IGE, etc)


class PilaNovedad(models.Model):
    TIPOS_NOVEDAD = (
        ("VAC", "Vacaciones"),
        ("INC", "Incapacidad"),
        ("LIC", "Licencia"),
        ("RET", "Retiro"),
        ("ING", "Ingreso"),
        ("VAR", "Variable salarial"),
    )

    id = models.AutoField(primary_key=True)

    detalle = models.ForeignKey(
        PilaPlanillaDetalle,
        on_delete=models.CASCADE,
        related_name="novedades",
    )

    tipo_novedad = models.CharField(max_length=3, choices=TIPOS_NOVEDAD)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    dias = models.PositiveSmallIntegerField(null=True, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'pila"."pila_novedad'