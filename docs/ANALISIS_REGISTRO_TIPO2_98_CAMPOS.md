## Análisis Registro Tipo 2 – 98 campos

**Contexto:** Registro tipo 2 del **Archivo Tipo 2** PILA (liquidación detallada de aportes), 693 caracteres, según `LAYOUT_REGISTRO_02.md` (Anexo Técnico 2 versión 29, 06-01-2026).  
Este documento resume qué campos ya se están llenando, cuáles se dejan en blanco por norma / operador y cuáles dependen de futuros cambios (principalmente en Nomiweb).

---

### 1. Campos 1–8 – Identificación del registro y del cotizante

- **Campo 1 (1–2, tipo registro)**  
  - **Origen**: constante `"02"` en `Registro02Renderer`.  
  - **Estado**: OK.

- **Campo 2 (3–7, secuencia)**  
  - **Origen**: contador secuencial en `generar_txt.genera_txt_planilla` (`00001`, `00002`, …).  
  - **Estado**: OK.

- **Campos 3–6 (8–21, tipo doc, número doc, tipo y subtipo cotizante)**  
  - **Origen**: `PilaPlanillaDetalle` (`tipo_doc`, `numero_doc`, `tipo_cotizante`, `subtipo_cotizante`), alimentado inicialmente desde el payload de Nomiweb.  
  - **Estado**: OK.

- **Campos 7–8 (22–23, extranjero no obligado a pensiones / colombiano en el exterior)**  
  - **Origen**: hoy no se modela explícitamente este escenario en Nomiweb ni en PILA.  
  - **Estado**: se dejan en blanco.  
  - **Pendiente**: si en el futuro se soporta formalmente cotizantes en exterior, Nomiweb debe marcar este caso y el microservicio ajustará estos indicadores y el campo 97 (fecha radicación exterior).

---

### 2. Campos 9–14 – Ubicación laboral y nombres

- **Campo 9 (32–33, código departamento)**  
  - **Origen**: `empleado.cod_departamento` del payload (Nomiweb), que a su vez viene de `ciudades.codciudad` (históricamente usado como departamento).  
  - **Implementación**:  
    - `payload_builder._get_ficha_contratos` arma `cod_departamento`/`cod_municipio`.  
    - `generar_txt` pasa `cod_departamento` a `data_02`.  
    - `Registro02Renderer` escribe posiciones 32–33 con `cod_departamento`.  
  - **Estado (4-mar-2026)**: OK, ajustado hoy al layout.

- **Campo 10 (34–36, código municipio)**  
  - **Origen**: `empleado.cod_municipio` del payload (Nomiweb), que a su vez viene de `ciudades.coddepartamento` (históricamente usado como ciudad).  
  - **Implementación**:  
    - `generar_txt` pasa `cod_municipio` a `data_02`.  
    - `Registro02Renderer` escribe posiciones 34–36 con `cod_municipio`.  
  - **Estado (4-mar-2026)**: OK, ajustado hoy al layout.

- **Campos 11–14 (37–136, primer/segundo apellido, primer/segundo nombre)**  
  - **Origen**: payload Nomiweb (`primer_apellido`, `segundo_apellido`, `primer_nombre`, `segundo_nombre`), con fallback desde `PilaPlanillaDetalle`.  
  - **Implementación**: se escriben con las longitudes correctas (20, 30, 20, 30).  
  - **Estado**: OK.

---

### 3. Campos 15–31 – Novedades y entidades pensión/salud/CCF

- **Novedades de 1 carácter (ING, RET, VSP, VST, SLN, IGE, LMA, VAC-LR, IRL-días)**  
  - **Origen principal**: modelo `PilaNovedad` en PILA (no del payload).  
  - **Implementación**:  
    - `generar_txt` recorre `detalle.novedades` y arma flags `nov_ing`, `nov_ret`, `nov_vsp`, `nov_vst`, `nov_sln`, `nov_ige`, `nov_lma`, `nov_vac`, `irl_dias` más sus fechas asociadas.  
    - `Registro02Renderer` los escribe en las posiciones 137–149 y 152–153 según layout.  
  - **Estado**: OK para las novedades que usamos hoy (ING, RET, VSP, VST, SLN, IGE, LMA, VAC, IRL).

- **Campos de traslados TDE, TAE, TDP, TAP (posiciones 139–142)**  
  - **Origen**: no se generan hoy desde Nomiweb ni se modelan en PILA.  
  - **Estado**: se dejan en blanco.  
  - **Pendiente**: si se implementan escenarios de traslados en Nomiweb, deberán llegar en el payload y mapearse a `PilaNovedad`/`data_02`.

- **Campo 28 – AVP (aporte voluntario pensiones, 150)**  
  - **Origen esperado**: debe provenir de la lógica de nómina en Nomiweb (marcando cuándo el cotizante tiene AVP).  
  - **Estado actual**: se deja en blanco; no se expone aún en el payload ni se usa en `generar_txt`.  
  - **Pendiente**: **desarrollar en Nomiweb** y luego extender payload + mapping a `data_02` y al renderer.

- **Campo 29 – VCT (variación centros de trabajo, 151)**  
  - **Uso funcional**: novedad cuando cambia el centro de trabajo.  
  - **Origen esperado**: Nomiweb debe detectar cambio de `centrotrabajo` y enviar novedad VCT para el periodo.  
  - **Estado actual**: se deja en blanco; hoy no se genera VCT en Nomiweb ni se modela en PILA.  
  - **Pendiente**: **Nomiweb** debe implementar detección de VCT y pasarlo a PILA; luego se mapea a este campo y a las fechas 91–92 (inicio/fin VCT).

- **Campo 31 – Código AFP (154–159)**  
  - **Origen**: `empleado.entidades.afp` desde el payload (6 caracteres), con reglas especiales para no obligados a pensión.  
  - **Estado**: OK.

- **Campo 33 – Código EPS (166–171)** y **Campo 35 – Código CCF (178–183)**  
  - **Origen**: `empleado.entidades.eps` y `empleado.entidades.caja` desde el payload.  
  - **Estado**: OK (con reglas para tipo 23 que no aporta salud/CCF).

---

### 4. Campos 36–56 – Días, salarios, IBC y aportes pensión/salud/FSP/UPC

- **Campos 36–39 (184–191, días por subsistema)**  
  - **Origen**: `detalle.dias_salud`, `dias_pension`, `dias_arl`, `dias_caja` calculados en PILA.  
  - **Estado**: OK.

- **Campo 40 (192–200, salario básico)**  
  - **Origen**: `empleado.salario_basico` desde payload Nomiweb.  
  - **Estado**: OK.

- **Campo 41 (201, tipo salario X/F/V)**  
  - **Origen**: `flags.salario_integral` (payload) y tipo de cotizante (`detalle.tipo_cotizante`).  
  - **Estado**: OK (con lógica especial para tipo 23, sin F/X/V).

- **Campos 42–45 (202–237, IBC pensión/salud/ARL/CCF)**  
  - **Origen**: JSON `aportes` calculado en PILA (`calcular_planilla`), no directamente del payload.  
  - **Estado**: OK.

- **Campos 46–52 (238–298, tarifa pensión, cotización y fondos solidaridad/subsistencia)**  
  - **Origen**: lógica interna de PILA (`calcular_planilla` + reglas de aplica/no aplica pensión).  
  - **Estado**: OK (incluye manejo de pensionados, subtipo, FSP solidaridad/subsistencia).

- **Campos 53–56 (299–332, valor no retenido, tarifa salud, cotización salud, UPC adicional)**  
  - **Origen**: aportes de salud calculados en PILA y parámetros SMMLV; el payload aporta banderas de exoneración y tarifas cuando aplica.  
  - **Estado**: OK (con reglas para integrales y IBC > 10 SMMLV).

---

### 5. Campos 57–69 – Incapacidades/LMA, ARL y parafiscales

- **Campos 57–60 (333–380, números de autorización y valores IGE/LMA)**  
  - **Norma**: en la mayoría de casos se dejan en blanco o en cero; el operador puede usarlos según procesos internos.  
  - **Estado**: se dejan en blanco/0; PILA no trae número de autorización ni valor entidad en estos campos (los valores de ausentismo se reflejan en IBC y cotizaciones regulares).  
  - **Pendiente**: sólo si se requiere modelar autorizaciones/facturas explícitas, habría que extender payload y modelo de PILA.

- **Campo 61 (381–389, tarifa ARL)**  
  - **Origen**: `tarifas.arl` en payload Nomiweb, con fallback por `clase_riesgo`, formateado por `_format_tarifa_arl` (porcentaje → decimal PILA con 7 decimales).  
  - **Estado**: OK, incluye manejo especial para ausentismo (tarifa 0 cuando hay IRL/VAC/IGE/LMA/SLN).

- **Campo 62 (390–398, centro de trabajo)**  
  - **Origen**: `codigo_centro_trabajo` en payload Nomiweb, mapeado por tarifa ARL (0,1,3,5).  
  - **Estado**: OK.

- **Campo 63 (399–407, cotización ARL)**  
  - **Origen**: aportes ARL calculados en PILA, con reglas para ausentismo (cotización 0).  
  - **Estado**: OK.

- **Campos 64–69 (408–455, tarifas y valores CCF/SENA/ICBF)**  
  - **Origen**: IBC caja calculado en PILA + reglas de exoneración; tarifas 4/2/3% expresadas en formato decimal PILA; valores redondeados según Decreto 1990.  
  - **Estado**: OK.

---

### 6. Campos 70–79 – ESAP, MEN, cotizante 40, exonerado, ARL y tarifa especial pensiones

- **Campos 70–73 (456–487, ESAP y MEN)**  
  - **Origen teórico**: aportes ESAP/MEN para ciertas entidades públicas.  
  - **Estado actual**: se dejan en blanco/cero; no se calcula ni se expone en el payload.  
  - **Pendiente**: si en el futuro se soporta este tipo de aportes, Nomiweb debe proveerlos y PILA debe calcular/mapping.

- **Campos 74–75 (488–505, documento cotizante principal, sólo tipo 40)**  
  - **Origen esperado**: Nomiweb (caso cotizante 40 – beneficiario con cotizante principal).  
  - **Estado actual**: se dejan en blanco; hoy no se modela tipo 40 en este flujo.  
  - **Pendiente**: implementar lógica para tipo 40 en Nomiweb y extender payload + mapping.

- **Campo 76 (506, exonerado salud/SENA/ICBF)**  
  - **Origen**: flags de exoneración en payload (`empresa_exonerada`, exoneración empleador) y lógica de PILA.  
  - **Estado**: OK.

- **Campo 77 (507–512, código ARL)**  
  - **Origen**: `entidades.arl` del payload.  
  - **Estado**: OK.

- **Campo 78 (513, clase de riesgo 1–5)**  
  - **Origen**: `clase_riesgo` en payload Nomiweb (calculada a partir de tarifa ARL).  
  - **Estado**: OK.

- **Campo 79 (514, indicador tarifa especial pensiones)**  
  - **Origen esperado**: Nomiweb debería indicar actividades de alto riesgo para marcar este campo.  
  - **Estado actual**: se deja en blanco; aún no se modela explícitamente tarifa especial pensiones.  
  - **Pendiente**: definir en Nomiweb qué contratos son de alto riesgo y enviar indicador en el payload.

---

### 7. Campos 80–94 – Fechas de novedades

- **Campos 80–88 (515–604, fechas ING, RET, VSP, SLN, IGE, LMA)**  
  - **Origen**: `PilaNovedad` (tabla de novedades en PILA).  
  - **Estado**: OK para las novedades que usamos:  
    - ING (80), RET (81), VSP (82), SLN (83–84), IGE (85–86), LMA (87–88).

- **Campos 89–90 (605–624, fechas inicio/fin VAC-LR)**  
  - **Origen**: novedades de vacaciones en PILA (VAC) recortadas al mes PILA.  
  - **Estado**: OK.

- **Campos 91–92 (625–644, fechas inicio/fin VCT)**  
  - **Uso funcional**: fechas de variación de centro de trabajo (novedad VCT).  
  - **Estado actual**: se dejan en blanco porque hoy no se genera VCT ni en Nomiweb ni en PILA.  
  - **Pendiente**: cuando Nomiweb implemente VCT, se deben crear `PilaNovedad` VCT y mapear estas fechas.

- **Campos 93–94 (645–664, fechas inicio/fin IRL)**  
  - **Origen**: novedades IRL en PILA (incapacidad riesgo laboral), ya implementado.  
  - **Estado**: OK.

---

### 8. Campos 95–98 – IBC otros parafiscales, horas, exterior y actividad económica

- **Campo 95 (665–673, IBC otros parafiscales)**  
  - **Origen**: IBC caja calculado en PILA (`ibc_caja`), usado cuando hay aporte SENA/ICBF.  
  - **Estado**: OK, con reglas para error 816 (no puede ser 0 cuando hay aporte y 30 días).

- **Campo 96 (674–676, número de horas laboradas)**  
  - **Origen**: derivado de `dias_caja` (multiplicado por 8 horas/día).  
  - **Estado**: OK.

- **Campo 97 (677–686, fecha radicación exterior)**  
  - **Uso funcional**: obligatorio si el campo 8 (colombiano en el exterior) es X.  
  - **Estado actual**: se deja en blanco, ya que hoy no modelamos cotizantes en exterior.  
  - **Pendiente**: ligado a la implementación futura de campos 7–8.

- **Campo 98 (687–693, actividad económica ARL)**  
  - **Origen**: `actividad_economica_arl` del payload Nomiweb (viene desde `centrotrabajo` en la BD).  
  - **Estado**: OK.

---

### 9. Resumen de pendientes (a marzo 2026)

- **Dependen de cambios en Nomiweb (payload):**
  - Campo 28 (AVP – aporte voluntario pensiones).  
  - Campo 29 (VCT – variación centros de trabajo) + campos 91–92 (fechas VCT).  
  - Campos 70–73 (aportes ESAP y MEN) – sólo si se requiere para entidades públicas.  
  - Campos 74–75 (documento cotizante principal, tipo 40).  
  - Campo 79 (indicador tarifa especial pensiones).  
  - Campos 7–8 y 97 (colombiano en el exterior / fecha radicación exterior).

- **Se dejan en blanco/cero por norma o porque el operador los calcula:**
  - Traslados TDE/TAE/TDP/TAP.  
  - Campos 57–60 (número autorización y valores específicos IGE/LMA, no requeridos en este flujo).  
  - ESAP/MEN mientras no se modele.  
  - Documento cotizante principal (tipo 40) mientras no se necesite en clientes actuales.

- **Ajustes realizados hoy (4-mar-2026):**
  - Campos **9 y 10** del layout (departamento y municipio) se alinean al layout 32–33 / 34–36:  
    - `generar_txt` ya no concatena municipio; ahora pasa `cod_departamento` y `cod_municipio` por separado a `data_02`.  
    - `Registro02Renderer` escribe 32–33 con `cod_departamento` y 34–36 con `cod_municipio`.  
    - Se respeta el comportamiento histórico de la tabla `ciudades` (campo `codciudad` utilizado como departamento y `coddepartamento` como ciudad) a nivel de payload, sin modificar la BD.

