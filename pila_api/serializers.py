# pila_api/serializers.py
from rest_framework import serializers


class EmpresaSerializer(serializers.Serializer):
    id_interno = serializers.IntegerField()
    nit = serializers.CharField(max_length=20)
    dv = serializers.CharField(max_length=1, required=False, allow_blank=True)  # Dígito de verificación
    razon_social = serializers.CharField(max_length=255)
    sucursal = serializers.CharField(max_length=5, allow_blank=True)
    tipo_documento_aportante = serializers.CharField(max_length=2, required=False, default="NI")
    tipo_aportante = serializers.CharField(max_length=2)
    clase_aportante = serializers.CharField(max_length=1, required=False, default="A")
    tipo_presentacion_planilla = serializers.CharField(max_length=1, required=False, default="U")  # U=única, S=sucursal
    codigo_arl = serializers.CharField(max_length=10, required=False, allow_blank=True)  # Código ARL del aportante
    flags = serializers.DictField(required=False, default=dict)

class PlanillaSerializer(serializers.Serializer):
    tipo_planilla = serializers.CharField(max_length=2)
    numero_interno = serializers.CharField(max_length=50)
    fecha_generacion = serializers.DateField(required=False, allow_null=True)


class EntidadesEmpleadoSerializer(serializers.Serializer):
    eps = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)
    afp = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)
    arl = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)
    caja = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)


class DiasEmpleadoSerializer(serializers.Serializer):
    salud = serializers.IntegerField()
    pension = serializers.IntegerField()
    arl = serializers.IntegerField()
    caja = serializers.IntegerField()


class IbcEmpleadoSerializer(serializers.Serializer):
    salud = serializers.DecimalField(max_digits=14, decimal_places=2)
    pension = serializers.DecimalField(max_digits=14, decimal_places=2)
    arl = serializers.DecimalField(max_digits=14, decimal_places=2)
    parafiscales = serializers.DecimalField(max_digits=14, decimal_places=2)


class TarifasEmpleadoSerializer(serializers.Serializer):
    arl = serializers.DecimalField(max_digits=8, decimal_places=6, required=False, allow_null=True)


class NovedadSerializer(serializers.Serializer):
    codigo = serializers.CharField(max_length=5)
    fecha_desde = serializers.DateField(required=False, allow_null=True)
    fecha_hasta = serializers.DateField(required=False, allow_null=True)
    dias = serializers.IntegerField(required=False, allow_null=True)
    salario_anterior = serializers.IntegerField(required=False, allow_null=True)
    salario_nuevo = serializers.IntegerField(required=False, allow_null=True)
    diferencia = serializers.IntegerField(required=False, allow_null=True)
    tipo_salario = serializers.IntegerField(required=False, allow_null=True)


class RegistroEmpleadoSerializer(serializers.Serializer):
    """Serializer para cada registro (línea tipo 02) de un empleado"""
    tipo_linea = serializers.CharField(max_length=20)
    dias = DiasEmpleadoSerializer()
    ibc = IbcEmpleadoSerializer()
    novedades = NovedadSerializer(many=True, required=False, default=list)


class EmpleadoSerializer(serializers.Serializer):
    id_empleado = serializers.IntegerField()
    tipo_doc = serializers.CharField(max_length=3)
    num_doc = serializers.CharField(max_length=30)
    primer_apellido = serializers.CharField(max_length=20, required=False, allow_blank=True)
    segundo_apellido = serializers.CharField(max_length=30, required=False, allow_blank=True)
    primer_nombre = serializers.CharField(max_length=20, required=False, allow_blank=True)
    segundo_nombre = serializers.CharField(max_length=30, required=False, allow_blank=True)
    cod_departamento = serializers.CharField(max_length=2, required=False, allow_blank=True)
    cod_municipio = serializers.CharField(max_length=3, required=False, allow_blank=True)
    tipo_cotizante = serializers.CharField(max_length=2)
    subtipo_cotizante = serializers.CharField(max_length=2)

    salario_basico = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    flags = serializers.DictField(required=False, default=dict)
    entidades = EntidadesEmpleadoSerializer()
    
    # Campos opcionales para retrocompatibilidad (formato antiguo)
    dias = DiasEmpleadoSerializer(required=False)
    ibc = IbcEmpleadoSerializer(required=False)
    
    tarifas = TarifasEmpleadoSerializer(required=False)
    novedades = NovedadSerializer(many=True, required=False, default=list)
    
    # Clase de riesgo ARL (campo 78 TXT, pos 513): "1"-"5" según tarifa 0.522→1, 1.044→2, 2.436→3, 4.350→4, 6.960→5
    clase_riesgo = serializers.CharField(max_length=1, required=False, allow_blank=True)
    # Código centro de trabajo (campo 62 TXT, pos 390-398)
    codigo_centro_trabajo = serializers.IntegerField(required=False, allow_null=True)
    
    # Nuevo campo para múltiples registros por empleado
    registros = RegistroEmpleadoSerializer(many=True, required=False, default=list)


class MetaSerializer(serializers.Serializer):
    origen = serializers.CharField(max_length=50, required=False)
    version_payload = serializers.CharField(max_length=20, required=False)
    usuario = serializers.CharField(max_length=150, required=False)


class PayloadPlanillaSerializer(serializers.Serializer):
    empresa = EmpresaSerializer()
    periodo = serializers.RegexField(regex=r"^\d{4}-\d{2}$")
    planilla = PlanillaSerializer()
    empleados = EmpleadoSerializer(many=True)
    meta = MetaSerializer(required=False)

    def validate(self, attrs):
        # Validación mínima: empleados no vacío
        if not attrs.get("empleados"):
            raise serializers.ValidationError("empleados no puede estar vacío")
        return attrs