import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "/Users/franciscodelacorte/.codex/.chatgpt-projects/g-p-6a88402d58cc8191b03a665302b9e7f5";
const outDir = `${root}/outputs/01a03d6c-06a1-7f50-bf47-10ed54760d3c`;
const rows = JSON.parse(await fs.readFile(`${outDir}/diccionario_trabajo_ESdE2023.json`, "utf8"));
const inspection = JSON.parse(await fs.readFile(`${outDir}/inspection_summary.json`, "utf8"));

const wb = Workbook.create();
const readme = wb.worksheets.add("README");
const dict = wb.worksheets.add("Diccionario");
const inspect = wb.worksheets.add("Inspección CSV");
const sources = wb.worksheets.add("Fuentes y versiones");

const navy = "#17324D", blue = "#246B8E", pale = "#EAF3F7", gold = "#D7A64A", ink = "#1E293B", muted = "#64748B";

for (const s of [readme, dict, inspect, sources]) { s.showGridLines = false; }

readme.getRange("A1:H1").merge();
readme.getRange("A1").values = [["ESdE 2023 · Diccionario de trabajo"]];
readme.getRange("A1:H1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 18 }, rowHeight: 34, verticalAlignment: "center" };
readme.getRange("A3:B8").values = [
  ["Proyecto", "Desigualdades socioeconómicas y determinantes de la salud en España"],
  ["Unidad principal", "Persona adulta seleccionada, 15 años o más"],
  ["Microdatos adulto", `${inspection.adult_rows.toLocaleString("es-ES")} filas × ${inspection.adult_columns} columnas`],
  ["Selección de trabajo", `${inspection.selected_variables} variables`],
  ["Vinculación hogar", `${inspection.join_income_non_null.toLocaleString("es-ES")} de ${inspection.join_rows.toLocaleString("es-ES")} adultos con INGRESOS mediante IDENTHOGAR + NORDENa=NORDEN`],
  ["Criterio de versión", "Adulto revisado por IMC (aviso 01/09/2025); hogar actualizado por ingresos (aviso 16/04/2026)"],
];
readme.getRange("A3:A8").format = { fill: pale, font: { bold: true, color: navy }, verticalAlignment: "top" };
readme.getRange("B3:B8").format = { font: { color: ink }, wrapText: true, verticalAlignment: "top" };
readme.getRange("A10:H10").merge();
readme.getRange("A10").values = [["Recomendación inicial"]];
readme.getRange("A10:H10").format = { fill: blue, font: { bold: true, color: "#FFFFFF" }, rowHeight: 25 };
readme.getRange("A11:H13").merge();
readme.getRange("A11").values = [["Pregunta: ¿Existe un gradiente socioeconómico en la mala salud autopercibida en España, y cuánto cambia tras ajustar por edad, sexo, origen y comunidad autónoma? Hipótesis primaria: a menor nivel educativo, clase social e intervalo de ingresos, mayor prevalencia de salud regular/mala/muy mala. Hipótesis secundaria: actividad física y apoyo social atenúan parcialmente la asociación. Empezar con C1 como resultado por su interpretación clara y cobertura completa; dejar IMC y depresión como análisis secundarios por sus restricciones y construcción derivada."]];
readme.getRange("A11:H13").format = { fill: "#FFF8E8", font: { color: ink }, wrapText: true, verticalAlignment: "top", rowHeight: 32 };
readme.getRange("A15:H15").merge();
readme.getRange("A15").values = [["Notas de uso"]];
readme.getRange("A15:H15").format = { fill: navy, font: { bold: true, color: "#FFFFFF" } };
readme.getRange("A16:H20").merge();
readme.getRange("A16").values = [["• Los códigos y etiquetas proceden del diseño de registro oficial incluido en los ZIP.\n• Los blancos del CSV suelen corresponder a saltos de cuestionario/no aplicable; no deben confundirse automáticamente con no respuesta.\n• Aplicar FACTORADULTO en estimaciones descriptivas e inferenciales apropiadas para encuesta.\n• INGRESOS y A11 proceden del fichero hogar; la unión exacta es uno-a-uno por IDENTHOGAR y número de orden.\n• Para IMC, usar la versión revisada y restringir la interpretación de categorías adultas a población de 18+ años."]];
readme.getRange("A16:H20").format = { wrapText: true, verticalAlignment: "top", font: { color: ink } };
readme.getRange("A1:H20").format.font.name = "Aptos";
readme.getRange("A1:H20").format.columnWidth = 16;
readme.getRange("A1:A20").format.columnWidth = 24;
readme.getRange("B1:B20").format.columnWidth = 62;

const headers = Object.keys(rows[0]);
const values = rows.map(r => headers.map(h => r[h] ?? ""));
dict.getRangeByIndexes(0, 0, 1, headers.length).values = [headers];
dict.getRangeByIndexes(1, 0, values.length, headers.length).values = values;
dict.getRangeByIndexes(0, 0, 1, headers.length).format = { fill: navy, font: { bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center", rowHeight: 42 };
dict.getRangeByIndexes(1, 0, values.length, headers.length).format = { font: { color: ink, size: 10 }, wrapText: true, verticalAlignment: "top" };
dict.freezePanes.freezeRows(1); dict.freezePanes.freezeColumns(2);
const dtable = dict.tables.add(`A1:P${rows.length + 1}`, true, "DiccionarioESdE");
dtable.style = "TableStyleMedium2";
const widths = [12,17,48,16,10,68,44,23,20,55,42,16,16,16,48,18];
widths.forEach((w,i)=>dict.getRangeByIndexes(0,i,rows.length+1,1).format.columnWidth=w);
dict.getRange(`L2:N${rows.length+1}`).format.numberFormat = "#,##0";

inspect.getRange("A1:F1").merge(); inspect.getRange("A1").values = [["Inspección real de los microdatos"]];
inspect.getRange("A1:F1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 16 }, rowHeight: 32 };
inspect.getRange("A3:B12").values = [
  ["Métrica", "Valor"], ["Filas adulto", inspection.adult_rows], ["Columnas adulto", inspection.adult_columns],
  ["Columnas enteras inferidas", inspection.adult_int_columns], ["Columnas decimales/nullable inferidas", inspection.adult_float_columns],
  ["Filas fichero hogar (miembros)", inspection.household_member_rows], ["Columnas hogar", inspection.household_columns],
  ["Adultos enlazados 1:1", inspection.join_rows], ["INGRESOS no nulo tras unión", inspection.join_income_non_null],
  ["A11 no nulo tras unión", inspection.join_work_status_non_null]
];
inspect.getRange("A3:B3").format = { fill: blue, font: { bold: true, color: "#FFFFFF" } };
inspect.getRange("A4:A12").format = { fill: pale, font: { bold: true, color: navy } };
inspect.getRange("B4:B12").format.numberFormat = "#,##0";
inspect.getRange("D3:F3").values = [["Control", "Resultado", "Interpretación"]];
inspect.getRange("D4:F7").values = [
  ["Dimensión adulto", `${inspection.adult_rows} × ${inspection.adult_columns}`, "Coincide con 21.032 entrevistas adultas publicadas."],
  ["Tipos CSV", `${inspection.adult_int_columns} int / ${inspection.adult_float_columns} float`, "Los float reflejan decimales y columnas con blancos; el tipo analítico debe seguir el diseño oficial."],
  ["Clave de enlace", "IDENTHOGAR + NORDEN", "NORDENa del adulto se iguala a NORDEN del miembro del hogar."],
  ["Cobertura enlace", "100%", "21.032 uniones uno-a-uno; ingresos y situación laboral disponibles para todos los adultos seleccionados."],
];
inspect.getRange("D3:F3").format = { fill: blue, font: { bold: true, color: "#FFFFFF" } };
inspect.getRange("D4:F7").format = { wrapText: true, verticalAlignment: "top" };
inspect.getRange("A14:F14").merge(); inspect.getRange("A14").values = [["El CSV se distribuye con extensión .tab y separador de tabulación. Tiene encabezados exactos y 432 variables; no es un CSV separado por comas pese al nombre genérico del formato en la web."]];
inspect.getRange("A14:F14").format = { fill: "#FFF8E8", font: { color: ink }, wrapText: true, rowHeight: 38 };
inspect.getRange("A:F").format.columnWidth = 24; inspect.getRange("A:A").format.columnWidth = 34; inspect.getRange("F:F").format.columnWidth = 55; inspect.getRange("D:D").format.columnWidth = 24;

sources.getRange("A1:F1").merge(); sources.getRange("A1").values = [["Fuentes oficiales, versiones y trazabilidad"]];
sources.getRange("A1:F1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 16 }, rowHeight: 32 };
sources.getRange("A3:F9").values = [
  ["Elemento", "Archivo local", "Versión/fecha verificada", "SHA-256", "URL oficial", "Uso"],
  ["Microdatos adulto", "data/raw/ESdEadulto_2023.zip", "Contenido fechado 2025-08-26; aviso de revisión IMC 2025-09-01", "3fea61e77297a1b154ea151e09fc4455cbab54d879223b7fffb467ba1673b99e", "https://www.sanidad.gob.es/estadEstudios/estadisticas/microdatos/EncSalEsp/ESdEadulto_2023.zip", "CSV y diseño de registro"],
  ["Microdatos hogar", "data/raw/ESdEhogar_2023.zip", "Contenido de datos fechado 2026-04-13; aviso de actualización ingresos 2026-04-16", "1ec200c11d56f17944f3cba65dc732309b3e401873ae5a1e670a69300c44272c", "https://www.sanidad.gob.es/estadEstudios/estadisticas/microdatos/EncSalEsp/ESdEhogar_2023.zip", "INGRESOS y A11 vinculables"],
  ["Cuestionario adulto", "docs/official/ESdE23_ADULTO.pdf", "Descargado 2026-08-26", "fc224215e7f13d28bc2a03f20cb258f1ba7c891f675f21c5c8ec9527808566c1", "https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/ESdE2023/ESdE23_ADULTO.pdf", "Enunciados, flujos y categorías"],
  ["Metodología", "docs/official/ESdE23_Metodologia.pdf", "Descargado 2026-08-26", "655e9147b1f5bcdb0d43d09153a2b6f3509a95cdbf1055e811b33cd51a2c2720", "https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/ESdE2023/ESdE23_Metodologia.pdf", "Diseño muestral y definiciones"],
  ["Página ESdE 2023", "—", "Consultada 2026-08-26", "—", "https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/", "Avisos oficiales de correcciones"],
  ["Banco de microdatos", "—", "Consultado 2026-08-26", "—", "https://www.sanidad.gob.es/estadisticas/microdatos.do", "Localización de ZIP vigentes"],
];
sources.getRange("A3:F3").format = { fill: blue, font: { bold: true, color: "#FFFFFF" }, wrapText: true };
sources.getRange("A4:F9").format = { wrapText: true, verticalAlignment: "top", font: { color: ink, size: 10 } };
sources.getRange("A4:A9").format.font.bold = true;
[20,36,32,68,72,30].forEach((w,i)=>sources.getRangeByIndexes(0,i,9,1).format.columnWidth=w);
sources.freezePanes.freezeRows(3);

for (const s of [readme, dict, inspect, sources]) {
  const used = s.getUsedRange();
  used.format.font.name = "Aptos";
}

const check1 = await wb.inspect({kind:"table", range:"README!A1:H20", include:"values,formulas", tableMaxRows:20, tableMaxCols:8, maxChars:5000});
console.log(check1.ndjson);
const check2 = await wb.inspect({kind:"table", range:`Diccionario!A1:P${rows.length+1}`, include:"values,formulas", tableMaxRows:6, tableMaxCols:16, maxChars:8000});
console.log(check2.ndjson);
const errors = await wb.inspect({kind:"match", searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options:{useRegex:true,maxResults:100}, summary:"final formula error scan"});
console.log(errors.ndjson);
for (const [sheetName, range, name] of [["README","A1:H20","preview_readme.png"],["Diccionario","A1:P8","preview_diccionario.png"],["Inspección CSV","A1:F14","preview_inspeccion.png"],["Fuentes y versiones","A1:F9","preview_fuentes.png"]]) {
  const png = await wb.render({sheetName, range, scale:1.2, format:"png"});
  await fs.writeFile(`${outDir}/${name}`, new Uint8Array(await png.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(`${outDir}/diccionario_trabajo_ESdE2023.xlsx`);
console.log(`${outDir}/diccionario_trabajo_ESdE2023.xlsx`);
