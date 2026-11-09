"""Export the two Jensen supplementary workbooks without modifying their bytes.

Run with Python 3.10+; uses only the standard library. No Excel installation needed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DOCUMENT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SOURCE_ID = "S006"
DOI = "10.1038/ncomms5022"

# Source letter, exported name, expected row-5 label, validation type.
PAIR_COLUMNS = [
    ("A", "diagnosis_1_code", "Code", "text"),
    ("B", "diagnosis_1_name", "Text", "text"),
    ("C", "diagnosis_2_code", "Code", "text"),
    ("D", "diagnosis_2_name", "Text", "text"),
    ("E", "n_patients", "N patients", "count"),
    ("F", "relative_risk", "RR", "number"),
    ("G", "rr_p_value_estimated", "estimated", "p_value"),
    ("H", "rr_p_value_sampled", "sampled", "p_value"),
    ("I", "n_samples", "N samples", "count"),
    ("J", "direction_p_value", "p-value", "p_value"),
]
TRAJECTORY_COLUMNS = [
    ("A", "cluster", "Cluster", "text"),
    ("B", "trajectory_id", "Trajectory id", "text"),
    ("C", "median_start_age_years", "start (years)", "number"),
    ("D", "diagnosis_1_code", "Diagnose 1", "text"),
    ("E", "diagnosis_1_name", "", "text"),
    ("F", "diagnosis_2_code", "Diagnose 2", "text"),
    ("G", "diagnosis_2_name", "", "text"),
    ("H", "count_1_to_2", "1->2", "count"),
    ("I", "time_to_2_months_reported", "(months)", "number"),
    ("J", "diagnosis_3_code", "Diagnose 3", "text"),
    ("K", "diagnosis_3_name", "", "text"),
    ("L", "count_1_to_2_to_3", "1->2->3", "count"),
    ("M", "time_to_3_months_reported", "(months)", "number"),
    ("N", "diagnosis_4_code", "Diagnose 4", "text"),
    ("O", "diagnosis_4_name", "", "text"),
    # Keep this neutral: the published fourth-step count header reads 1->...->3.
    ("P", "count_final_reported", "1->...->3", "count"),
    ("Q", "time_to_4_months_reported", "(months)", "number"),
]
TABLES = [
    ("ncomms5022-s2", "Supplementary Data 1", "jensen_diagnosis_pairs.csv", 4014, PAIR_COLUMNS),
    ("ncomms5022-s3", "S4 - Trajectories", "jensen_trajectories.csv", 1171, TRAJECTORY_COLUMNS),
]
PROVENANCE = ["source_id", "source_doi", "source_file", "source_sheet", "source_row"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_sheet(path: Path, sheet_name: str) -> dict[int, dict[str, str]]:
    """Read stored cell values directly from OOXML; never open a file for writing."""
    with ZipFile(path, "r") as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [
                "".join(node.text or "" for node in item.findall(".//s:t", NS))
                for item in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", NS)
            ]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = {sheet.attrib["name"]: sheet for sheet in workbook.findall("s:sheets/s:sheet", NS)}
        if sheet_name not in sheets:
            raise ValueError(f"{path.name}: expected sheet {sheet_name!r}")
        rel_id = sheets[sheet_name].attrib[f"{{{DOCUMENT_REL}}}id"]
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship = next(item for item in relationships if item.attrib["Id"] == rel_id)
        if relationship.get("TargetMode") == "External":
            raise ValueError("External worksheet targets are not supported")
        target = relationship.attrib["Target"]
        sheet_path = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        worksheet = ET.fromstring(archive.read(sheet_path))
        rows = {}
        for row in worksheet.findall("s:sheetData/s:row", NS):
            row_number = int(row.attrib["r"])
            values = {}
            for cell in row.findall("s:c", NS):
                address = cell.attrib["r"]
                if cell.find("s:f", NS) is not None or cell.get("t") == "e":
                    raise ValueError(f"{path.name}!{address}: formula or Excel error requires review")
                value = cell.findtext("s:v", default="", namespaces=NS)
                if cell.get("t") == "s":
                    value = strings[int(value)]
                elif cell.get("t") == "inlineStr":
                    value = "".join(node.text or "" for node in cell.findall("s:is//s:t", NS))
                values[re.sub(r"\d", "", address)] = value
            if row_number in rows:
                raise ValueError(f"Duplicate Excel row {row_number}")
            rows[row_number] = values
        return rows


def clean_value(raw: str, kind: str) -> str:
    """Validate numbers without float conversion, rounding, or changing inequalities."""
    value = raw.strip()
    if not value:
        raise ValueError("Missing required value")
    if kind == "text":
        return " ".join(value.split())
    number_text = value[1:].strip() if kind == "p_value" and value.startswith("<") else value
    try:
        number = Decimal(number_text)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {kind}: {value!r}") from exc
    if not number.is_finite() or number < 0:
        raise ValueError(f"Invalid {kind}: {value!r}")
    if kind == "count" and number != number.to_integral_value():
        raise ValueError(f"Non-integer count: {value!r}")
    if kind == "p_value" and number > 1:
        raise ValueError(f"P-value outside [0, 1]: {value!r}")
    return value


def extract(root: Path) -> dict:
    register = json.loads((root / "ressources/sources.json").read_text(encoding="utf-8"))
    if not any(source.get("source_id") == SOURCE_ID and source.get("doi") == DOI
               for source in register["sources"]):
        raise ValueError("Jensen source ID/DOI does not match the source register")

    source_dir = root / "ressources/supplements"
    inputs = [source_dir / (stem + extension) for stem, *_ in TABLES for extension in (".zip", ".xlsx")]
    before = {path: sha256(path) for path in inputs}
    prepared = []
    for stem, sheet, output_name, expected_count, columns in TABLES:
        workbook = source_dir / (stem + ".xlsx")
        original = source_dir / (stem + ".zip")
        if before[workbook] != before[original]:
            raise ValueError(f"{workbook.name} is no longer byte-identical to the publisher original")
        rows = read_sheet(workbook, sheet)
        for letter, _, expected_header, _ in columns:
            if rows.get(5, {}).get(letter, "").strip() != expected_header:
                raise ValueError(f"{workbook.name}: unexpected header in {letter}5")
        records = []
        source_path = workbook.relative_to(root).as_posix()
        for row_number, cells in sorted(rows.items()):
            if row_number < 6 or not any(value.strip() for value in cells.values()):
                continue
            allowed = {letter for letter, *_ in columns}
            if any(value.strip() for letter, value in cells.items() if letter not in allowed):
                raise ValueError(f"{workbook.name}: unexpected data columns in row {row_number}")
            record = {}
            for letter, field, _, kind in columns:
                try:
                    record[field] = clean_value(cells.get(letter, ""), kind)
                except ValueError as exc:
                    raise ValueError(f"{workbook.name}!{letter}{row_number}: {exc}") from exc
            record.update(source_id=SOURCE_ID, source_doi=DOI, source_file=source_path,
                          source_sheet=sheet, source_row=str(row_number))
            records.append(record)
        if len(records) != expected_count:
            raise ValueError(f"{workbook.name}: expected {expected_count} records, got {len(records)}")
        metadata = {
            "input_file": source_path,
            "publisher_original": original.relative_to(root).as_posix(),
            "input_sha256": before[workbook],
            "publisher_sha256": before[original],
            "sheet": sheet,
            "source_header_rows": {str(n): cells for n, cells in rows.items() if n < 6},
            "source_first_data_row": int(records[0]["source_row"]),
            "source_last_data_row": int(records[-1]["source_row"]),
            "record_count": len(records),
            "columns": [{"source_column": letter, "output_field": field,
                         "source_row_5_label": label, "validation_type": kind}
                        for letter, field, label, kind in columns],
        }
        prepared.append((output_name, columns, records, metadata))

    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("A source file changed during extraction; no outputs were written")

    output_dir = root / "data/extracted"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "source_doi": DOI,
        "status": "extracted_not_reviewed_for_graph",
        "source_files_unchanged": True,
        "cleaning": ["Flattened headers", "Trimmed outer whitespace",
                     "Collapsed whitespace in text fields only",
                     "Preserved numeric strings, zeros, inequalities and scientific notation",
                     "No filtering, deduplication, rounding, merging or causal inference"],
        "notes": [
            "Both tables originate from one study; do not treat them as independent evidence.",
            "Trajectory column P has the published label '1->...->3' despite following diagnosis 4; "
            "exported as count_final_reported without silently correcting the label.",
            "Timing values are exported as reported; no intervals or probabilities are calculated.",
        ],
        "tables": [],
    }
    for output_name, columns, records, metadata in prepared:
        path = output_dir / output_name
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=[field for _, field, _, _ in columns] + PROVENANCE)
            writer.writeheader()
            writer.writerows(records)
        with path.open(encoding="utf-8-sig", newline="") as stream:
            if list(csv.DictReader(stream)) != records:
                raise RuntimeError(f"CSV round-trip verification failed: {output_name}")
        metadata.update(output_file=path.relative_to(root).as_posix(), output_sha256=sha256(path))
        manifest["tables"].append(metadata)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("A source file changed during extraction; rerun after checking the sources")
    (output_dir / "jensen_extraction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = extract(args.project_root.resolve())
    for table in result["tables"]:
        print(f"{table['output_file']}: {table['record_count']:,} records")
    print("Verified all four source files unchanged. Extraction manifest saved.")
