# Layout Registro Tipo 1 – Archivo Tipo 1 PILA (Datos generales del aportante)

Referencia: **Anexo Técnico 2**, Resolución 2388 de 2016 y modificatorias (versión 29, 06-01-2026).  
Páginas 9-16. **Longitud total del registro: 567 caracteres.**

Convención: posiciones **1-based** (inicial y final inclusive). N = numérico (derecha, relleno ceros). A = alfanumérico (izquierda, relleno espacios).

---

## Campos 1-10 – Identificación del aportante y forma de presentación (p.9-11)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 1 | 200 | 1 | 200 | A | Nombre o razón social del aportante | Obligatorio. Lo suministra el aportante. Valores válidos: NIT, CC, CE, PA, SC, CD, PE, PT |
| 2 | 2 | 201 | 202 | A | Tipo de documento del aportante | NI = Número de identificación. CC = Cédula de ciudadanía. TI = Tarjeta de identidad. PA = Pasaporte. CD = Carné diplomático. SC = Salvoconducto de permanencia. PE = Permiso Especial de Permanencia. No puede ser utilizada para los periodos de cotización de agosto a septiembre de 2023 en adelante. PT = Permiso por Protección Temporal |
| 3 | 16 | 203 | 218 | A | Número de identificación del aportante | El operador de información validará que este campo, esté compuesto por letras de la A a la Z y los caracteres numéricos del Cero (0) al nueve (9). Solo es permitido el número de identificación alfanumérico para los siguientes tipos de documentos de identidad: CD: Carné diplomático. Para el resto los aportantes tipo de documento deben ser dígitos numéricos. |
| 4 | 1 | 219 | 219 | N | Dígito de verificación | Este deber ser validado por el operador de información, según la norma que lo haya definido en DIAN. Lo suministra el aportante. |
| 5 | 10 | 220 | 229 | A | Código sucursal o de la dependencia | Este campo debe ir en blanco cuando la forma de presentación sea U: Único |
| 6 | 40 | 230 | 269 | A | Nombre de la sucursal o de la dependencia | Si la sucursal no tiene nombre, colocar su código. Obligatorio. Lo suministra el aportante. A: Aportantes con 200 o más cotizantes. Aportantes con menos de 200 cotizantes. |
| 7 | 1 | 270 | 270 | A | Clase de aportante | A: Aportantes con 200 o más cotizantes. Para lo cual se deben tener en cuenta todos los cotizantes de todas las sucursales o dependencias, si las hubiera. B: Aportante con menos de 200 cotizantes. Para lo cual se deben tener en cuenta todos los cotizantes de todas las sucursales o dependencias, si las hubiera. C: Aportante Mipyme que se acoge a Ley 590 de 2000. D: Aportante beneficiario del artículo 5º de la Ley 1429 de 2010 |
| 8 | 1 | 271 | 271 | N | Naturaleza jurídica | Obligatorio. Lo suministra el aportante. 1: Pública. 2: Privada. 3: Mixta. 4: Organismos multilaterales. 5: Entidades de derecho público internacional de la legislación colombiana. Obligatorio. Lo suministra el aportante. N: Natural. J: Jurídica |
| 9 | 1 | 272 | 272 | A | Tipo persona | Cuando el tipo de persona sea N. NI: Número de identificación. CC: Cédula de ciudadanía. CE: Cédula de extranjería. TI: Tarjeta de identidad. PA: Pasaporte. CD: Carné diplomático. PE: Permiso Especial de Permanencia. SC: Salvoconducto de permanencia. PT: Permiso por Protección Temporal |
| 10 | 1 | 273 | 273 | A | Forma de presentación | Obligatorio. Lo suministra el aportante. U: Única. S: Sucursal |

---

## Campos 11-17 – Ubicación y contacto (p.12-13)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 11 | 40 | 274 | 313 | A | Dirección de correspondencia | Obligatorio. Lo suministra el aportante. El operador de información deberá validar que campo no exceda los 40 caracteres de longitud. |
| 12 | 3 | 314 | 316 | A | Código ciudad o municipio | Obligatorio. Lo suministra el aportante. El operador de información deberá validar que este código esté en relación de la División Política y Administrativa – DIVIPOLA. Cuando marque el campo colombiano en el exterior se debe diligenciar en blanco. |
| 13 | 2 | 317 | 318 | A | Código departamento | Obligatorio. Lo suministra el aportante. El operador de información deberá validar que este código esté en relación de la División Política y Administrativa – DIVIPOLA, expedida por el DANE. Cuando marque el campo colombiano en el exterior se debe diligenciar en blanco. |
| 14 | 4 | 319 | 322 | N | Código DANE de la actividad económica | Obligatorio. Lo suministra el aportante. El código debe estar adaptada para Colombia especificada por el DANE mediante decreto que la modificó o sustituya. Obligatorio. Lo suministra el aportante. |
| 15 | 10 | 323 | 332 | N | Teléfono | Lo suministra el aportante. |
| 16 | 10 | 333 | 342 | N | Fax | Lo suministra el aportante. Los nombres de usuario pueden contener letras (a,z), números (0-9) y ciertos caracteres especiales ():;' y puntos (.). El Símbolo indicador debe ser el arroba (@). El nombre del dominio debe estar formado por letras (a-z), y números (0-9) que sea válido (-), pero no podrá estar situado como último ni como el primer carácter del nombre. |
| 17 | 60 | 343 | 402 | A | Dirección de correo electrónico (E-mail) | El nombre del dominio debe estar formado por letras (a-z), y números (0-9) que sea válido (-), pero no podrá estar situado como último ni como el primer carácter del nombre. |

---

## Campos 18-24 – Representante legal (p.13)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 18 | 15 | 403 | 418 | A | Número de identificación del representante legal | Obligatorio cuando el campo 9 de este archivo esté reportando como tipo de persona N = Natural. El operador de información validará que este campo, esté compuesto por letras de la A a la Z y los caracteres numéricos del Cero (0) al nueve (9). Solo es permitido el número de identificación alfanumérico para los siguientes tipos de documentos de identidad: CD: Carné diplomático. CE: Cédula de Extranjería deben ser dígitos numéricos. |
| 19 | 1 | 419 | 419 | N | Dígito de verificación del representante legal | Este campo se deberá reportar en cero. Obligatorio cuando en el campo 7 tipo de Persona sea J. El diligenciamiento es opcional cuando el tipo de persona N |
| 20 | 2 | 420 | 421 | A | Tipo identificación representante legal | Obligatorio. Lo suministra el aportante. Los valores válidos son: CC: Cédula de ciudadanía. CE: Cédula de extranjería. PA: Pasaporte |
| 21 | 20 | 422 | 441 | A | Primer apellido del representante legal | Obligatorio cuando en el campo 7 tipo de persona sea J. Jurídica. |
| 22 | 30 | 442 | 471 | A | Segundo apellido del representante legal | Lo suministra el aportante. |
| 23 | 20 | 472 | 491 | A | Primer nombre del representante legal | Obligatorio cuando en el campo 7 tipo de Persona sea J. Jurídica. |
| 24 | 30 | 492 | 521 | A | Segundo nombre del representante legal | Lo suministra el aportante. |

---

## Campos 25-27 – Información de liquidación (p.14)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 25 | 10 | 522 | 531 | A | Fecha de inicio del concesionario, liquidación o cese de actividades | Opcional. Cuando no hay pago de nómina o pagos. Formato AAAA-MM-DD. El operador de información deberá revisar la diferencia información en el campo 26 de este archivo. 0: No aplica. 1: Concordato. 2: Concesión. 3: Liquidación. 4: Cese de actividades |
| 26 | 1 | 532 | 532 | N | Tipo de acción | Opcional. Se debe diligenciar cuando haya reportado información en el campo 25 de este registro. A: Se debe reportar a partir de la cual el concesionario u otro quedó en la obligación a efectuar aportes. Formato AAAA-MM-DD. |
| 27 | 10 | 533 | 542 | A | Fecha en que terminó el pago | Opcional. Se debe diligenciar cuando haya reportado información en esta registro. |

---

## Campos 28-30 – Operador, periodo y tipo de aportante (p.14)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 28 | 2 | 543 | 544 | N | Código del operador | Asignado por el sistema. Asignado por AM-IM. Cuando se utilice la planilla Z en este campo se deberá diligenciar 00, por lo que no es procesada por la herramienta tecnológica www.aportesenlinea.com.co |
| 29 | 7 | 545 | 551 | N | Periodo de pago | Lo suministra el aportante. 1: Empleador. 2: Independiente. 3: Estudiantes o universidades o instituciones de régimen especial y de excepción. 4: Organizaciones, asociaciones, fundaciones y organizaciones no gubernamentales que cumplen con la legislación colombiana. 5: Operadores Programa de Hogares de Bienestar. 6: Cotizantes del Programa de Hogares de Bienestar |
| 30 | 2 | 552 | 553 | N | Tipo de aportante | 8: Pagador de aportes de los concejales, municipales, ediles, contralores y demás juntas y administradoras de locales. 9: Pagador de aportes contrato sindical. 10:Pagador programa de reincorporación. 11:Pagador de aportes participantes del Magisterio. 12:Pagador de prestación voluntaria. 13:Afiliados al Sistema Nacional de Voluntarios en Primera Respuesta. 14:Trabajador de pago aporte saliente pensión. 15:Contratante. 16:Cotizante al Promotor del Servicio Social para la Paz. Obligatorio para el aportante que realice el pago de Formalización y Generación de Empleo (Ley 1429 de 2010). Corresponder a la fecha base en el documento de matrícula mercantil. Es decir corresponde a su sede principal. |

---

## Campos 31-34 – Fechas y exoneraciones (p.15-16)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 31 | 10 | 554 | 563 | A | Fecha de matrícula mercantil (aaaa-mm-dd) | Lo suministra el aportante. Se permite fechas desde el 28 de diciembre de 2010 hasta el 31 de diciembre de 2014. Obligatorio para el aportante beneficiario de la Ley 1429 (Empleo Ley 1429 de 2010). |
| 32 | 2 | 564 | 565 | A | Código del departamento | Lo suministra el aportante y no el código del departamento donde está principal. Debe corresponder con la dirección de correspondencia. |
| 33 | 1 | 566 | 566 | A | Aportante exonerado de aportes parafiscales SENA e ICBF | Obligatorio. Lo suministra el aportante. S: Si. N: No |
| 34 | 1 | 567 | 567 | A | Aportante que se acoge al artículo 5º de la Ley 1429 de 2010 con beneficio de aportes a SENA e ICBF para las cajas de compensación familiar | Obligatorio. Lo suministra el aportante. S: Si. N: No |

---

## Total

**Longitud total del registro tipo 1: 567 caracteres.**

---

## Notas importantes

1. **Forma de presentación (Campo 10)**:
   - **U (Única)**: Cuando el aportante reporta todos sus cotizantes en un solo archivo, sin diferenciar por sucursales. En este caso, los campos 5 (código sucursal) y 6 (nombre sucursal) deben ir **en blanco**.
   - **S (Sucursal)**: Cuando el aportante reporta por sucursales separadas.

2. **Clase de aportante (Campo 7)**:
   - Determina si el aportante tiene más o menos de 200 cotizantes, o si aplica a regímenes especiales (Mipyme, Ley 1429).

3. **Tipo de aportante (Campo 30)**:
   - Define la naturaleza del aportante según la normativa (Empleador, Independiente, etc.).

4. **Validaciones del operador**:
   - El operador de información (Aportes en Línea) valida que los códigos DANE, DIVIPOLA y otros cumplan con los estándares oficiales.

---

*Documento generado a partir del Anexo Técnico 2 (versión 29, 06-01-2026). Para validaciones detalladas y códigos válidos consultar el PDF oficial.*
