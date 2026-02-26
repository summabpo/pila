# Layout Registro Tipo 2 – Archivo Tipo 2 PILA (Liquidación detallada de aportes)

Referencia: **Anexo Técnico 2**, Resolución 2388 de 2016 y modificatorias (versión 29, 06-01-2026).  
Páginas 83-98. **Longitud total del registro: 693 caracteres.**

Convención: posiciones **1-based** (inicial y final inclusive). N = numérico (derecha, relleno ceros). A = alfanumérico (izquierda, relleno espacios).

---

## Campos 1-8 (inicio del registro)

*Definidos en páginas anteriores al 83; se mantiene lo implementado en código.*

| Campo | Long | Inicial | Final | Tipo | Descripción |
|-------|------|---------|-------|------|-------------|
| 1 | 2 | 1 | 2 | N | Tipo de registro (01/02/…) |
| 2 | 5 | 3 | 7 | N | Secuencia |
| 3 | 2 | 8 | 9 | A | Tipo documento del cotizante |
| 4 | 8 | 10 | 17 | A | Número documento del cotizante |
| 5 | 2 | 18 | 19 | A | Tipo de cotizante |
| 6 | 2 | 20 | 21 | A | Subtipo de cotizante |
| 7 | 1 | 22 | 22 | A | Extranjero no obligado a cotizar pensiones |
| 8 | 1 | 23 | 23 | A | Colombiano en el exterior (X cuando aplica) |

*(Posiciones 24-31: según Anexo corresponden a otros campos previos al código DANE; verificar en PDF completo.)*

---

## Campos 9-11 – Ubicación y primer apellido (p.83)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 9 | 2 | 32 | 33 | A | Código del departamento de la ubicación laboral | DIVIPOLA DANE. Blanco si colombiano en exterior (salvo CCF voluntaria) o cotizante 40. |
| 10 | 3 | 34 | 36 | A | Código del municipio de ubicación laboral | DIVIPOLA DANE. Mismas excepciones que campo 9. |
| 11 | 20 | 37 | 56 | A | Primer apellido | Obligatorio. Lo suministra el aportante. |

---

## Campos 12-14 – Segundo apellido y nombres (p.84)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 12 | 30 | 57 | 86 | A | Segundo apellido | Lo suministra el aportante. |
| 13 | 20 | 87 | 106 | A | Primer nombre | Obligatorio. Lo suministra el aportante. |
| 14 | 30 | 107 | 136 | A | Segundo nombre | Lo suministra el aportante. |

---

## Campos 15-27 – Novedades (marcas 1 carácter) (p.84-85)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 15 | 1 | 137 | 137 | A | ING – Ingreso | Blanco, R, X o C. Aportante. |
| 16 | 1 | 138 | 138 | A | RET – Retiro | Blanco, P, R, X, C o T. Aportante. |
| 17 | 1 | 139 | 139 | A | TDE – Traslado desde otra EPS/EOC | En blanco. |
| 18 | 1 | 140 | 140 | A | TAE – Traslado a otra EPS/EOC | En blanco. |
| 19 | 1 | 141 | 141 | A | TDP – Traslado desde otra AFP | En blanco. |
| 20 | 1 | 142 | 142 | A | TAP – Traslado a otra AFP | En blanco. |
| 21 | 1 | 143 | 143 | A | VSP – Variación permanente de salario | Blanco o X. Aportante. |
| 22 | 1 | 144 | 144 | A | Correcciones | Blanco, A o C. Aportante. |
| 23 | 1 | 145 | 145 | A | VST – Variación transitoria del salario | Blanco o X. Aportante. |
| 24 | 1 | 146 | 146 | A | SLN – Suspensión temporal / licencia no remunerada | Blanco, X o C. Aportante. |
| 25 | 1 | 147 | 147 | A | IGE – Incapacidad enfermedad general / licencia niñez | Blanco, X o L. Aportante. |
| 26 | 1 | 148 | 148 | A | LMA – Licencia maternidad/paternidad | Blanco, X o P. Aportante. |
| 27 | 1 | 149 | 149 | A | VAC-LR – Vacaciones / Licencia remunerada | X vacaciones, L licencia remunerada. Aportante. |

---

## Campos 28-31 – AVP, VCT, IRL, Administradora pensiones (p.85)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 28 | 1 | 150 | 150 | A | AVP – Aporte voluntario | Solo si cotizante en S en archivo afiliación pensiones. Blanco o X. Aportante. |
| 29 | 1 | 151 | 151 | A | VCT – Variación centros de trabajo | Blanco o X. Aportante. |
| 30 | 2 | 152 | 153 | N | IRL – Días incapacidad accidente trabajo / enfermedad laboral | 00 o 01-30. Aportante. |
| 31 | 6 | 154 | 159 | A | Código administradora de pensiones (o ACCAI) | Obligatorio salvo si no obligado a pensiones. Código válido. Operador/Aportante. |

---

## Campos 32-35 – Traslados y códigos EPS/CCF (p.86)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 32 | 6 | 160 | 165 | A | Código AFP a la cual se traslada | En blanco. |
| 33 | 6 | 166 | 171 | A | Código EPS o EOC del afiliado | Obligatorio salvo si no obligado a salud. Código válido. Aportante. |
| 34 | 6 | 172 | 177 | A | Código EPS o EOC a la cual se traslada | En blanco. |
| 35 | 6 | 178 | 183 | A | Código CCF del afiliado | Obligatorio salvo si no obligado a CCF. Aportante. |

---

## Campos 36-39 – Días cotizados por subsistema (p.87)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 36 | 2 | 184 | 185 | N | Días cotizados a pensión | 00-30. 0 solo si no obligado. Si &lt;30 debe haber novedad ING/RET. Aportante. |
| 37 | 2 | 186 | 187 | N | Días cotizados a salud | 00-30. Si &lt;30 debe haber novedad. Si UPC adicional &gt;0 debe ser 30. Aportante. |
| 38 | 2 | 188 | 189 | N | Días cotizados a riesgos laborales | 00-30. 0 solo si no obligado. Relación con IGE/LMA/IRL. Aportante. |
| 39 | 2 | 190 | 191 | N | Días cotizados a CCF | 00-30. 0 solo si no obligado. Aportante. |

---

## Campos 40-46 – Salario, tipo salario, IBC, tarifa pensiones (p.88)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 40 | 9 | 192 | 200 | N | Salario básico | Obligatorio, sin decimales, ≥0. Puede &lt;1 SMMLV. Aportante. |
| 41 | 1 | 201 | 201 | A | Tipo de salario | X integral, F fijo, V variable. Obligatorio para tipos cotizante 1,2,20,22,32,58. Aportante. |
| 42 | 9 | 202 | 210 | N | IBC pensión | Obligatorio. Aportante. |
| 43 | 9 | 211 | 219 | N | IBC salud | Obligatorio. Aportante. |
| 44 | 9 | 220 | 228 | N | IBC riesgos laborales | Obligatorio. Aportante. |
| 45 | 9 | 229 | 237 | N | IBC CCF | Obligatorio para tipos 1,2,18,22,30,51,55. Aportante. |
| 46 | 7 | 238 | 244 | N | Tarifa aportes pensiones | Aportante; operador valida según tarifas vigentes. |

---

## Campos 47-52 – Aportes pensiones y fondo solidaridad (p.89)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 47 | 9 | 245 | 253 | N | Cotización obligatoria pensiones | Tarifas vigentes. Obligatorio. Aportante. |
| 48 | 9 | 254 | 262 | N | Aporte voluntario afiliado pensiones | Solo régimen ahorro individual; campo 5 archivo afiliación = S. Aportante. |
| 49 | 9 | 263 | 271 | N | Aporte voluntario aportante pensiones | Igual que 48. Aportante. |
| 50 | 9 | 272 | 280 | N | Total cotización pensiones | Calculado: 47+48+49. Sistema. |
| 51 | 9 | 281 | 289 | N | Aportes fondo solidaridad – subcuenta solidaridad | Operador liquida según normativa. |
| 52 | 9 | 290 | 298 | N | Aportes fondo solidaridad – subcuenta subsistencia | Operador liquida según normativa. |

---

## Campos 53-56 – Valor no retenido, tarifa salud, cotización salud, UPC (p.90)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 53 | 9 | 299 | 307 | N | Valor no retenido por aportes voluntarios | Aportante. |
| 54 | 7 | 308 | 314 | N | Tarifa aportes salud | Aportante; operador valida tarifas vigentes. |
| 55 | 9 | 315 | 323 | N | Cotización obligatoria salud | Obligatorio. Aportante. |
| 56 | 9 | 324 | 332 | N | Valor UPC adicional / contribución solidaria | Según tipo cotizante (40, 69) y archivos BDUA/contribución solidaria. |

---

## Campos 57-62 – Incapacidad/IGE, LMA, ARL, CT (p.90-91)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 57 | 15 | 333 | 347 | A | N° autorización incapacidad enfermedad general | En blanco. |
| 58 | 9 | 348 | 356 | N | Valor incapacidad enfermedad general | En cero. |
| 59 | 15 | 357 | 371 | A | N° autorización licencia maternidad/paternidad | En blanco. |
| 60 | 9 | 372 | 380 | N | Valor licencia maternidad | En cero. |
| 61 | 9 | 381 | 389 | N | Tarifa aportes riesgos laborales | Aportante; operador valida. |
| 62 | 9 | 390 | 398 | N | Centro de trabajo (CT) | Aportante. |

---

## Campos 63-69 – Cotización ARL, CCF, SENA, ICBF (p.91)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 63 | 9 | 399 | 407 | N | Cotización obligatoria riesgos laborales | Aportante. |
| 64 | 7 | 408 | 414 | N | Tarifa aportes CCF | Aportante; operador valida. |
| 65 | 9 | 415 | 423 | N | Valor aporte CCF | Aportante. |
| 66 | 7 | 424 | 430 | N | Tarifa aportes SENA | Aportante. |
| 67 | 9 | 431 | 439 | N | Valor aportes SENA | Aportante. |
| 68 | 7 | 440 | 446 | N | Tarifa aportes ICBF | Aportante. |
| 69 | 9 | 447 | 455 | N | Valor aporte ICBF | Aportante. |

---

## Campos 70-76 – ESAP, MEN, cotizante 40, exonerado (p.91-92)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 70 | 7 | 456 | 462 | N | Tarifa aportes ESAP | Aportante. |
| 71 | 9 | 463 | 471 | N | Valor aporte ESAP | Aportante. |
| 72 | 7 | 472 | 478 | N | Tarifa aportes MEN | Aportante. |
| 73 | 9 | 479 | 487 | N | Valor aporte MEN | Aportante. |
| 74 | 2 | 488 | 489 | A | Tipo documento cotizante principal | Solo cuando cotizante 40. Aportante. |
| 75 | 16 | 490 | 505 | A | Número identificación cotizante principal | Solo cuando cotizante 40. Aportante. |
| 76 | 1 | 506 | 506 | A | Cotizante exonerado salud, SENA e ICBF | S/N. Obligatorio. Si IBC salud ≥10 SMMLV debe N. Aportante. |

---

## Campos 77-79 – ARL, clase de riesgo, tarifa especial pensiones (p.93)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 77 | 6 | 507 | 512 | A | Código administradora riesgos laborales | Campo 14 registro tipo 1, o ARL por cotizante 59/57. Blanco si no obligado. Aportante. |
| 78 | 1 | 513 | 513 | A | Clase de riesgo (1-5) | I a V. Tipo 57: tabla ocupaciones Decreto 1563/2016. Tipo 70: siempre 1. Blanco si no obligado. Aportante. |
| 79 | 1 | 514 | 514 | A | Indicador tarifa especial pensiones | Blanco normal, 1 actividades alto riesgo. Aportante. |

---

## Campos 80-88 – Fechas novedades ING, RET, VSP, SLN, IGE, LMA (p.94-95)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 80 | 10 | 515 | 524 | A | Fecha ingreso (AAAA-MM-DD) | Opcional si novedad ING. Fecha válida en periodo. Aportante. |
| 81 | 10 | 525 | 534 | A | Fecha retiro (AAAA-MM-DD) | Opcional si novedad RET. Aportante. |
| 82 | 10 | 535 | 544 | A | Fecha inicio VSP (AAAA-MM-DD) | Opcional si novedad VSP. Aportante. |
| 83 | 10 | 545 | 554 | A | Fecha inicio SLN (AAAA-MM-DD) | Opcional si novedad SLN. Aportante. |
| 84 | 10 | 555 | 564 | A | Fecha fin SLN (AAAA-MM-DD) | Opcional si novedad SLN. Aportante. |
| 85 | 10 | 565 | 574 | A | Fecha inicio IGE (AAAA-MM-DD) | Opcional si novedad IGE. Aportante. |
| 86 | 10 | 575 | 584 | A | Fecha fin IGE (AAAA-MM-DD) | Opcional si novedad IGE. Aportante. |
| 87 | 10 | 585 | 594 | A | Fecha inicio LMA (AAAA-MM-DD) | Opcional si novedad LMA. Aportante. |
| 88 | 10 | 595 | 604 | A | Fecha fin LMA (AAAA-MM-DD) | Opcional si novedad LMA. Aportante. |

---

## Campos 89-94 – Fechas VAC-LR, VCT, IRL (p.96)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 89 | 10 | 605 | 614 | A | Fecha inicio VAC-LR (AAAA-MM-DD) | Opcional si novedad VAC-LR. Aportante. |
| 90 | 10 | 615 | 624 | A | Fecha fin VAC-LR (AAAA-MM-DD) | Opcional si novedad VAC-LR. Aportante. |
| 91 | 10 | 625 | 634 | A | Fecha inicio VCT (AAAA-MM-DD) | Opcional si novedad VCT. Aportante. |
| 92 | 10 | 635 | 644 | A | Fecha fin VCT (AAAA-MM-DD) | Opcional si novedad VCT. Aportante. |
| 93 | 10 | 645 | 654 | A | Fecha inicio IRL (AAAA-MM-DD) | Opcional si novedad IRL. Aportante. |
| 94 | 10 | 655 | 664 | A | Fecha fin IRL (AAAA-MM-DD) | Opcional si novedad IRL. Aportante. |

---

## Campos 95-98 – IBC parafiscales, horas, exterior, actividad económica (p.97)

| Campo | Long | Inicial | Final | Tipo | Descripción | Validación / origen |
|-------|------|---------|-------|------|-------------|----------------------|
| 95 | 9 | 665 | 673 | N | IBC otros parafiscales (no CCF) | Obligatorio tipos 1,18,20,22,30,31,55. Aportante. |
| 96 | 3 | 674 | 676 | N | Número de horas laboradas | Opcional tipos 1,2,18,22,30,51,55. Tipo 31 ver excepción. Aportante. |
| 97 | 10 | 677 | 686 | A | Fecha radicación en exterior (AAAA-MM-DD) | Opcional; obligatorio si campo 8 = X. Aportante. |
| 98 | 7 | 687 | 693 | N | Actividad económica riesgos laborales | Códigos Decreto 768/2022. Obligatorio quien cotice ARL (salvo 57 y 67). Desde nov 2022. Aportante. |

---

## Resumen de diferencias con el renderer actual

| Aspecto | Código actual | Anexo (este doc) | Acción sugerida |
|---------|----------------|------------------|------------------|
| Segundo nombre (Campo 14) | 107-126 (20 chars) | 107-**136** (30 chars) | Ampliar a 30 caracteres. |
| Código departamento / municipio | 32-36 como "municipio" (5) | 32-33 dep (2), 34-36 mun (3) | Separar `cod_departamento` y `cod_municipio`. |
| AFP (Campo 31) | 152-159 (8) | **154-159** (6); 152-153 = IRL (Campo 30) | AFP solo 154-159; IRL 152-153. |
| CCF (Campo 35) | 178-182 (5) | **178-183** (6) | CCF 6 caracteres (178-183). |
| Pos 145 | `flag_145` | Campo 23 **VST** (Variación transitoria salario) | Renombrar a semántica VST. |
| Bloque 333-693 | `raw_333_693` | Campos 57-98 con posiciones fijas | Ir reemplazando por campos semánticos (57-98) según tabla anterior. |

---

## Uso de múltiples registros tipo 2 por cotizante (p.98)

- **Varias novedades de ingreso/retiro en el mismo período:** una línea por cada novedad (o ingreso+retiro en la misma línea si aplica).
- **Novedades que cambian el IBC:** cada IBC diferente en una línea distinta (LMA, IGE, SLN, IRL, VAC-LR, VSP, VST).
- El aportante es responsable del cálculo de esas variaciones.

---

*Documento generado a partir del Anexo Técnico 2 (versión 29, 06-01-2026). Para validaciones detalladas y códigos válidos consultar el PDF oficial.*
