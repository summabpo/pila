# PILA – Microservicio de Planilla Integrada de Liquidación de Aportes

Microservicio Django que recibe un payload JSON (p.ej. desde Nomiweb), persiste la planilla y sus detalles, calcula aportes (salud, pensión, ARL, caja) y genera el archivo TXT PILA de ancho fijo para subir a [Aportes en Línea](https://aportesenlinea.com).

---

## Stack

- **Django** 5.2
- **Django REST Framework**
- **PostgreSQL** (configurado vía `.env`)
- **Python** 3.11

---

## Estructura del proyecto

```
pila/
├── manage.py
├── requirements.txt
├── .env                    # DB_*, PILA_SERVICE_TOKEN
├── pila_service/           # Proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── pila_api/               # App principal
    ├── models.py           # PilaPlanilla, PilaPlanillaDetalle, PilaNovedad
    ├── views.py            # Endpoints REST
    ├── serializers.py      # Validación del payload
    ├── dto.py              # Transformación a respuesta
    ├── admin.py
    ├── renderers/
    │   └── fixed_width/    # Generación TXT PILA
    │       ├── base.py     # FixedWidthLine
    │       ├── registro_01.py
    │       └── registro_02.py
    ├── services/
    │   └── calcular_planilla.py
    └── scripts/            # Validación y debugging
        ├── diff_reg02.py
        ├── test_reg02_clone.py
        ├── inspect_fw_02_windows.py
        └── ATI_COL28736 (2).TXT   # Golden sample
```

---

## API

Base: `/api/v1/`. Autenticación: `Authorization: Bearer <PILA_SERVICE_TOKEN>`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST   | `/api/v1/pila/planillas/`                | Crear o actualizar planilla |
| GET    | `/api/v1/pila/planillas/<id>/`           | Consultar planilla |
| GET    | `/api/v1/pila/planillas/<id>/detalles/`  | Listar detalles por empleado |
| POST   | `/api/v1/pila/planillas/<id>/calcular/`  | Recalcular aportes |

*(El endpoint de descarga de archivo está comentado en `urls.py`.)*

---

## Modelos

### PilaPlanilla

- `numero_interno`, `periodo` (YYYY-MM), `empresa_nit`, `empresa_sucursal`
- `estado`: EN_PROCESO | COMPLETADA | CON_ERRORES
- `payload_inicial` (JSON), `totales`, `resumen`, `errores`
- `tiene_archivo`

### PilaPlanillaDetalle

- Por empleado: `tipo_doc`, `numero_doc`, `primer_nombre`, `primer_apellido`
- `tipo_cotizante`, `subtipo_cotizante`
- `dias_cotizados`, `dias_salud`, `dias_pension`, `dias_arl`, `dias_caja`
- `ibc`, `ibc_salud`, `ibc_pension`, `ibc_arl`
- `riesgo_arl`, `caja_compensacion`
- `aportes` (JSON), `aportes_empleado`, `aportes_empleador`

### PilaNovedad

- Por detalle: `tipo_novedad` (VAC, INC, LIC, RET, ING, VAR)
- `fecha_inicio`, `fecha_fin`, `dias`, `valor`, `metadata`

---

## Payload esperado

```json
{
  "empresa": {
    "id_interno": 1,
    "nit": "...",
    "razon_social": "...",
    "sucursal": "001",
    "tipo_aportante": "01",
    "clase_riesgo_arl": "1",
    "flags": {}
  },
  "periodo": "2025-12",
  "planilla": {
    "tipo_planilla": "E",
    "numero_interno": "...",
    "fecha_generacion": "2025-12-15"
  },
  "empleados": [
    {
      "id_empleado": 1,
      "tipo_doc": "CC",
      "num_doc": "12345678",
      "nombre_completo": "Nombre Apellido",
      "tipo_cotizante": "01",
      "subtipo_cotizante": "00",
      "entidades": { "eps": "...", "afp": "...", "arl": "...", "caja": "..." },
      "dias": { "salud": 30, "pension": 30, "arl": 30, "caja": 30 },
      "ibc": { "salud": 0, "pension": 0, "arl": 0, "parafiscales": 0 },
      "novedades": []
    }
  ],
  "parametros": {
    "smmlv": 1400000,
    "tope_ibc_smmlv": 25,
    "dias_base": 30
  }
}
```

Ver `pila_api/serializers.py` para el formato exacto.

---

## Renderers de ancho fijo

### FixedWidthLine (`base.py`)

- Buffer de longitud fija, posiciones **1-indexadas** (como PILA).
- `set(start, end, value, align, pad)`
- `set_num(start, end, value)` – numérico, right, pad "0"
- `set_alpha(start, end, value)` – texto, left, pad " "
- `set_raw(start, end, raw)` – literal exacto (para clonar tail)
- `render()` – valida longitud final

### Registro01Renderer

- Encabezado PILA. Longitud: 359 caracteres.
- Campos: tipo registro, razón social, NIT, periodo cotización/pago, etc.

### Registro02Renderer

- Detalle cotizante. Longitud: 693 caracteres.
- Segmentos:
  - 1–182: identificadores, entidades (CCF/EPS/AFP), nombres, municipio
  - 184–332: días por subsistema, IBCs y valores (`v_192_200`, `v_237_245`, etc.)
  - 333–693: tail clonado (raw) hasta completar semántica

---

## Servicio de cálculo

`calcular_planilla(planilla_id)` en `services/calcular_planilla.py`:

- Tasas: salud (4% emp / 8.5% empl), pensión (4% / 12%), ARL por riesgo, caja 4%
- Exoneración (empresa exonerada, salario < 10 SMMLV, no integral)
- Flags por empleado: aplica_salud, aplica_pension, aplica_arl, aplica_caja
- IBC mínimos proporcionales, topes por SMMLV
- Actualiza detalles y totales de la planilla

---

## Scripts de validación

| Script | Uso |
|--------|-----|
| `diff_reg02.py` | Compara línea 02 generada vs golden sample; muestra primera diferencia y ventana |
| `test_reg02_clone.py` | Compara por rangos (1–182, 184–332, 333–693) |
| `inspect_fw_02_windows.py` | Inspección de ventanas del registro 02 |

**Golden sample:** `pila_api/scripts/ATI_COL28736 (2).TXT`

Ejecutar desde la raíz del proyecto:

```bash
python -m pila_api.scripts.diff_reg02
python -m pila_api.scripts.test_reg02_clone
```

---

## Variables de entorno

```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
DB_SSLMODE=require
PILA_SERVICE_TOKEN=
```

---

## Ejecución

```bash
cd pila
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Integración con Nomiweb

- **Nomiweb** (`apps.pila`): `payload_builder`, `pila_cliente`, comando `probar_pila_payload`
- Este microservicio recibe el payload, calcula aportes y prepara el TXT PILA
- Estado del proyecto conjunto: `nomiweb/documentation/PILA_ESTADO_PROYECTO.md`
