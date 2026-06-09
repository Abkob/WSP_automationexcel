import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = path.resolve(".");
const inputPath = path.join(projectRoot, "data", "incoming_excel", "WSP_dummy_semantic_20260604.xlsx");
const outputPath = path.join(projectRoot, "data", "incoming_excel", "WSP_dummy_semantic_rerun_20260607.xlsx");
const previewPath = path.join(projectRoot, "data", "incoming_excel", "WSP_dummy_semantic_rerun_20260607_preview.png");

const input = await FileBlob.load(inputPath);
const sourceWorkbook = await SpreadsheetFile.importXlsx(input);
const sourceSheet = sourceWorkbook.worksheets.getItem("Sheet1");
const sourceValues = sourceSheet.getUsedRange().values;

const headers = sourceValues[0].map((value) => String(value));
const headerIndex = Object.fromEntries(headers.map((header, index) => [header, index]));
const rows = sourceValues.slice(1).filter((row) => row[headerIndex.STUD_ID] !== null && row[headerIndex.STUD_ID] !== undefined);

const removedRows = rows.slice(0, 3);
const keptRows = rows.slice(3).map((row) => [...row]);
const updatedRows = keptRows.slice(0, 7);

for (const [index, row] of updatedRows.entries()) {
  const gpaIndex = headerIndex.CUM_GPA;
  const skillsIndex = headerIndex.WSP_TECHNICAL_SKILLS;
  const preferredIndex = headerIndex.WSP_PREFERRED_TYPE_OF_WORK;
  const previousIndex = headerIndex.WSP_PREV_WORK;
  const probationIndex = headerIndex.PROBATION;

  const currentGpa = Number(row[gpaIndex] ?? 3.1);
  row[gpaIndex] = Math.min(4, Math.round((currentGpa + 0.08 + index * 0.01) * 100) / 100);
  row[skillsIndex] = `${row[skillsIndex]}; Excel quality checks; dashboard cleanup`;
  row[preferredIndex] = "Spreadsheet reporting, data cleanup, dashboard preparation, and careful student record review.";
  row[previousIndex] = `${row[previousIndex]} During spring rerun testing, helped review spreadsheet rows and flag mismatched entries.`;
  if (index % 3 === 0) {
    row[probationIndex] = !Boolean(row[probationIndex]);
  }
}

const newRows = [
  makeNewRow("260201", "Maya Rerun", "Information Technology", "Junior", 3.72, "Excel, SQL, spreadsheet QA, dashboard notes", "Data entry, spreadsheet reporting, and checking import errors."),
  makeNewRow("260202", "Omar Rerun", "Business Administration", "Senior", 3.41, "Excel budgets, invoice tracking, PowerPoint", "Office assistant work with budgets, forms, and careful follow-up."),
  makeNewRow("260203", "Nadine Rerun", "Computer Science", "Sophomore", 3.88, "Python, SQL, Excel pivot tables, data cleaning", "Research assistant work using cleaned datasets and short summaries."),
  makeNewRow("260204", "Karim Rerun", "Graphic Design", "Freshman", 2.96, "Canva, social media scheduling, Excel trackers", "Design support, event posters, and registration desk coordination."),
  makeNewRow("260205", "Leila Rerun", "Biology", "Senior", 3.33, "Lab logs, Excel inventory sheets, sample labels", "Laboratory assistant work with safety logs and organized preparation."),
];

const outputRows = [headers, ...keptRows, ...newRows];
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Sheet1");
sheet.getRangeByIndexes(0, 0, outputRows.length, headers.length).values = outputRows;
sheet.freezePanes.freezeRows(1);
sheet.getRangeByIndexes(0, 0, 1, headers.length).format = {
  fill: "#1f6f8b",
  font: { bold: true, color: "#FFFFFF" },
};
sheet.getUsedRange().format.wrapText = true;

const notes = workbook.worksheets.add("Rerun Notes");
notes.getRange("A1:B8").values = [
  ["Item", "Value"],
  ["Source workbook", path.basename(inputPath)],
  ["Rerun workbook", path.basename(outputPath)],
  ["Rows removed to test missing detection", removedRows.length],
  ["Rows updated to test history", updatedRows.length],
  ["Rows added to test new inserts", newRows.length],
  ["Expected import result", "5 new, 7 updated, many unchanged, 3 newly missing"],
  ["Semantic smoke query", "spreadsheet reporting with careful data entry"],
];
notes.getRange("A1:B1").format = {
  fill: "#2f7d57",
  font: { bold: true, color: "#FFFFFF" },
};
notes.getUsedRange().format.wrapText = true;

const preview = await workbook.render({ sheetName: "Sheet1", range: "A1:J18", scale: 1, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

console.log(JSON.stringify({
  outputPath,
  previewPath,
  sourceRows: rows.length,
  outputRows: outputRows.length - 1,
  removed: removedRows.length,
  updated: updatedRows.length,
  added: newRows.length,
}, null, 2));

function makeNewRow(studentId, name, major, classDesc, gpa, skills, preferredWork) {
  const row = Array(headers.length).fill(null);
  row[headerIndex.STUD_ID] = studentId;
  row[headerIndex.STUD_NAME] = name;
  row[headerIndex.MAJR_DESC] = major;
  row[headerIndex.CLAS_DESC] = classDesc;
  row[headerIndex.STUD_EMAIL] = `${name.toLowerCase().replace(/\s+/g, ".")}@example.test`;
  row[headerIndex.WSP_WRITTEN_LANGUAGES] = "English, Arabic";
  row[headerIndex.WSP_SPOKEN_LANGUAGES] = "English, Arabic, French";
  row[headerIndex.WSP_ORGANIZATIONAL_SKILLS] = "keeps task lists updated; checks details before submitting forms";
  row[headerIndex.WSP_TECHNICAL_SKILLS] = skills;
  row[headerIndex.WSP_INTERPERSONAL_SKILLS] = "patient with students; clear communicator";
  row[headerIndex.WSP_ADDITIONAL_SKILLS] = "available for morning shifts; comfortable with repeated data checks";
  row[headerIndex.WSP_PREV_WORK] = "Helped with campus office tasks, spreadsheet cleanup, and student form review.";
  row[headerIndex.WSP_PREVIOUS_TYPE_OF_WORK] = "Office support and spreadsheet cleanup";
  row[headerIndex.WSP_PREFERRED_TYPE_OF_WORK] = preferredWork;
  row[headerIndex.DEANS_WARNING] = false;
  row[headerIndex.ENRL_TERM] = "202610";
  row[headerIndex.DEAN_WARN] = false;
  row[headerIndex.MOBILE_NBR] = `700${studentId.slice(-5)}`;
  row[headerIndex.PROBATION] = false;
  row[headerIndex.APPLICATION_DATE] = "2026-06-07";
  row[headerIndex.CUM_GPA] = gpa;
  row[headerIndex.STST_DESC] = "Active";
  row[headerIndex.STYP_CODE] = "REG";
  row[headerIndex.STYP_DESC] = "Regular";
  row[headerIndex.ENROLLED_IND] = true;
  row[headerIndex.REGISTERED_IND] = true;
  row[headerIndex.LEVL_CODE] = "UG";
  row[headerIndex.COLL_CODE] = "AS";
  row[headerIndex.TOTAL_CREDIT_HOURS] = 72;
  row[headerIndex.ASTD_TERM] = "202610";
  row[headerIndex.ATSD_CODE_END_OF_TERM] = "GOOD";
  row[headerIndex.ASTD_DESC] = "Good Standing";
  row[headerIndex.ASTD_DATE_END_OF_TERM] = "2026-06-07";
  row[headerIndex.USAID] = false;
  row[headerIndex.MASTER_CARD] = false;
  row[headerIndex.UPP_MEPI] = false;
  row[headerIndex.GAS] = false;
  row[headerIndex.FINANCIAL_AID] = true;
  row[headerIndex.DORMS] = false;
  return row;
}
