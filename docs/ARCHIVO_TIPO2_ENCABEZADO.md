# ARCHIVO TIPO 2 – Encabezado (Registro tipo 1 del archivo tipo 2)

Referencia: **Anexo Técnico 2**, Resolución 2388 de 2016 y modificatorias (versión 29, 06-01-2026).  
**Archivo tipo 2: Información planilla integrada.**  
**Longitud del encabezado: 359 caracteres.**

---

## 1. Archivo tipo 1 vs Archivo tipo 2

| Concepto | Descripción |
|----------|-------------|
| **ARCHIVO TIPO 1 – Datos generales del aportante** | Registro de 567 caracteres con todos los datos del aportante (razón social, NIT, sucursal, naturaleza jurídica, tipo persona, representante legal, dirección, CIIU, email, etc.). El operador puede exigirlo en otro proceso o como dato maestro; **no es el archivo que se sube como planilla**. Varios campos del encabezado del archivo tipo 2 indican “El registrado en el campo X del **archivo tipo 1**”, es decir, el archivo tipo 1 es la **fuente de datos** del aportante. En este proyecto esos datos se obtienen de la BD (Empresa) y se usan para armar el encabezado del archivo tipo 2. |
| **ARCHIVO TIPO 2 – Información planilla integrada** | Es el archivo que **se sube al operador** (Aportes en Línea). Contiene una línea de encabezado (Registro tipo 1 del archivo tipo 2) y N líneas de liquidación (Registro tipo 2 del archivo tipo 2). |

En este desarrollo **solo se genera el ARCHIVO TIPO 2** (encabezado 359 + detalle 693).

---

## 2. Estructura del archivo tipo 2 (lo que se sube)

| Línea | Tipo de registro | Longitud | Descripción |
|-------|------------------|----------|-------------|
| 1 | Registro tipo 1 del archivo tipo 2 – **Encabezado** | **359 caracteres** | Una sola línea por archivo. Identificación del aportante (desde archivo tipo 1/BD), tipo planilla, periodo, total cotizantes, valor total nómina, etc. |
| 2..N | Registro tipo 2 del archivo tipo 2 – **Liquidación detallada** | **693 caracteres** | Una línea por cada cotizante/detalle. Ver `LAYOUT_REGISTRO_02.md`. |

---

## 3. Registro tipo 1 del archivo tipo 2 – Encabezado (359 caracteres)

Convención: posiciones **1-based**. N = numérico (derecha, relleno ceros). A = alfanumérico (izquierda, relleno espacios).

### Campos 1–3 (págs. 24–25 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 1 | 2 | 1 | 2 | N | Tipo de registro | Obligatorio. Valor fijo **01**. |
| 2 | 1 | 3 | 3 | N | Modalidad de la planilla | Obligatorio. Generado por el operador. 1 = Electrónica, 2 = Asistida. |
| 3 | 4 | 4 | 7 | N | Secuencia | Obligatorio. Por cada aportante inicia en 0001. Lo genera el sistema o lo reporta el aportante si sube archivo plano. |

### Campos 4–8 (pág. 25 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 4 | 200 | 8 | 207 | A | Nombre o razón social del aportante | El registrado en el **campo 1 del archivo tipo 1**. |
| 5 | 2 | 208 | 209 | A | Tipo documento del aportante | El registrado en el **campo 2 del archivo tipo 1** (NI, CC, etc.). |
| 6 | 16 | 210 | 225 | A | Número de identificación del aportante | El registrado en el **campo 3 del archivo tipo 1**. |
| 7 | 1 | 226 | 226 | N | Dígito de verificación aportante | El registrado en el **campo 4 del archivo tipo 1**. |
| 8 | 1 | 227 | 227 | A | Tipo de planilla | Obligatorio. E = Empleados, K = Estudiantes, A = Ingreso, I = Independientes, S = Servicio doméstico, M = Mora, N = Correcciones, H = Madres sustitutas, T = SGP, F = Pago patronal faltante SGP, J = Sentencia judicial, X = Empresa liquidada, U = UGPP terceros, entre otros. |

### Campo 9 (pág. 26 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 9 | 9 | 228 | 237 | N | Número de la planilla asociada a esta planilla | En blanco cuando tipo planilla sea E, A, I, M, S, Y, H, T, X, K, Q o B. Se diligencia cuando tipo sea N, F, U, J u O según reglas del Anexo. |

### Campos 10–13 (pág. 27 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 10 | 10 | 238 | 247 | A | Fecha de pago planilla asociada (AAAA-MM-DD) | Reglas según tipo de planilla (Z, E, A, I, M, S, Y, T, X, K, H, Q, B, N, F, U, J, O). |
| 11 | 1 | 248 | 248 | A | Forma de presentación | El registrado en el **campo 10 del archivo tipo 1** (U = Única, S = Sucursal). |
| 12 | 10 | 249 | 258 | A | Código de la sucursal del aportante | El registrado en el **campo 5 del archivo tipo 1**. En blanco si forma presentación U. |
| 13 | 40 | 259 | 298 | A | Nombre de la sucursal | El registrado en el **campo 6 del archivo tipo 1**. |

### Campos 14–19 (pág. 28 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 14 | 6 | 299 | 304 | A | Código de la ARL a la cual el aportante está afiliado | Lo suministra el aportante. |
| 15 | 7 | 305 | 311 | A | Período de pago (sistemas distintos a salud) | Obligatorio. Formato aaaa-mm. Lo calcula el operador o lo suministra el aportante. |
| 16 | 7 | 312 | 318 | A | Período de pago sistema de salud | Obligatorio. Formato aaaa-mm. Lo suministra el aportante. |
| 17 | 10 | 319 | 328 | N | Número de radicación o de la Planilla Integrada de Liquidación de Aportes | Asignado por el sistema. Único por operador. |
| 18 | 10 | 329 | 338 | A | Fecha de pago (aaaa-mm-dd) | Asignada por el sistema según fecha efectiva de pago. |
| 19 | 5 | 339 | 343 | N | Número total de cotizantes reportados en esta planilla | Obligatorio. Debe ser igual al número de cotizantes únicos en el detalle (Registro tipo 2), excluyendo tipo cotizante 40. |

### Campos 20–22 (pág. 29 Anexo)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 20 | 12 | 344 | 355 | N | Valor total de la nómina | Obligatorio. Suma del campo 45 (IBC CCF) de todos los registros tipo 2. Para aportantes no obligados a CCF, cero. |
| 21 | 2 | 356 | 357 | N | Tipo de aportante | Obligatorio. El registrado en el **campo 30 del archivo tipo 1** (01 = Empleador, 02 = Independiente, etc.). |
| 22 | 2 | 358 | 359 | N | Código del operador de información | Asignado por el sistema del operador. |

---

## 4. Total

**Longitud total del registro tipo 1 del archivo tipo 2 (encabezado): 359 caracteres.**

---

## 5. Registro tipo 2 del archivo tipo 2 (liquidación detallada)

La liquidación detallada (693 caracteres por cotizante) se documenta en **`LAYOUT_REGISTRO_02.md`**. Es lo que implementa `registro_02.py`. Las tablas de este documento se basan en el Anexo Técnico 2 versión 29 (páginas 24-29).

---

*Documento generado a partir del Anexo Técnico 2 (versión 29). Para reglas detalladas de cada campo consultar el PDF oficial.*
