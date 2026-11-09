"""Preserve full Jensen trajectories separately from pairwise relationship evidence.

Run extract_jensen.py and prepare_jensen_graph_tables.py first. Python 3.10+.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from extract_jensen import DOI, PROVENANCE, SOURCE_ID, TRAJECTORY_COLUMNS, clean_value, sha256
from prepare_jensen_graph_tables import STATUS, write_csv


INPUT_FIELDS = [field for _, field, _, _ in TRAJECTORY_COLUMNS] + PROVENANCE
OUTPUT_FIELDS = ["trajectory_record_id"] + INPUT_FIELDS + [
    f"diagnosis_{position}_id" for position in range(1, 5)
] + ["evidence_type", "review_status"]


def build_records(rows: list[dict[str, str]], diagnoses: list[dict[str, str]]) -> tuple[list[dict], dict]:
    nodes = {}
    for node in diagnoses:
        if node["code"] in nodes:
            raise ValueError("Duplicate code in the diagnosis table")
        if node["diagnosis_id"] != f"{SOURCE_ID}:ICD10:{node['code']}":
            raise ValueError("Unexpected diagnosis ID namespace")
        nodes[node["code"]] = node
    records = []
    seen_rows = set()
    used_codes = set()
    sequences = Counter()
    for row in rows:
        if set(row) != set(INPUT_FIELDS):
            raise ValueError("Unexpected trajectory record fields")
        for _, field, _, kind in TRAJECTORY_COLUMNS:
            if clean_value(row[field], kind) != row[field]:
                raise ValueError(f"Unclean input field: {field}")
        if (row["source_id"], row["source_doi"], row["source_file"], row["source_sheet"]) != (
            SOURCE_ID, DOI, "ressources/supplements/ncomms5022-s3.xlsx", "S4 - Trajectories"
        ):
            raise ValueError("Unexpected trajectory source provenance")
        if not re.fullmatch(r"[1-9][0-9]*", row["source_row"]) or int(row["source_row"]) < 6:
            raise ValueError("Invalid trajectory source row")
        if row["source_row"] in seen_rows:
            raise ValueError("Repeated trajectory source row")
        seen_rows.add(row["source_row"])
        codes = [row[f"diagnosis_{position}_code"] for position in range(1, 5)]
        if row["trajectory_id"] != "_".join(codes):
            raise ValueError("Trajectory identifier does not match the ordered diagnosis codes")
        ids = {}
        for position, code in enumerate(codes, start=1):
            if code not in nodes:
                raise ValueError(f"Trajectory code missing from diagnoses: {code}")
            if row[f"diagnosis_{position}_name"] != nodes[code]["name"]:
                raise ValueError(f"Trajectory/diagnosis label conflict for {code}")
            ids[f"diagnosis_{position}_id"] = nodes[code]["diagnosis_id"]
            used_codes.add(code)
        records.append({
            "trajectory_record_id": f"{SOURCE_ID}:SD2:{row['source_row']}",
            **row, **ids,
            "evidence_type": "OBSERVED_DIAGNOSIS_TRAJECTORY", "review_status": STATUS,
        })
        sequences[tuple(codes)] += 1
    if not records:
        raise ValueError("No trajectory records found")
    return records, {
        "trajectory_record_count": len(records), "unique_ordered_sequence_count": len(sequences),
        "repeated_sequence_record_count": sum(count - 1 for count in sequences.values()),
        "diagnosis_codes_in_trajectories": len(used_codes),
        "missing_diagnosis_references": 0, "diagnosis_name_conflicts": 0,
        "cluster_counts": dict(sorted(Counter(row["cluster"] for row in rows).items())),
    }


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def prepare(root: Path) -> dict:
    directory = root / "data/extracted"
    input_path = directory / "jensen_trajectories.csv"
    extraction_path = directory / "jensen_extraction_manifest.json"
    node_path = directory / "diagnoses.csv"
    node_manifest_path = directory / "jensen_graph_tables_manifest.json"
    workbook = root / "ressources/supplements/ncomms5022-s3.xlsx"
    original = root / "ressources/supplements/ncomms5022-s3.zip"
    inputs = (input_path, extraction_path, node_path, node_manifest_path, workbook, original)
    before = {path: sha256(path) for path in inputs}
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    node_manifest = json.loads(node_manifest_path.read_text(encoding="utf-8"))
    if extraction.get("source_id") != SOURCE_ID or extraction.get("source_doi") != DOI:
        raise ValueError("Unexpected extraction study")
    table = next(item for item in extraction["tables"]
                 if item["output_file"] == "data/extracted/jensen_trajectories.csv")
    if (table["input_file"] != workbook.relative_to(root).as_posix()
            or table["publisher_original"] != original.relative_to(root).as_posix()
            or table["sheet"] != "S4 - Trajectories"):
        raise ValueError("Unexpected source workbook in extraction manifest")
    if before[input_path] != table["output_sha256"]:
        raise ValueError("Trajectory CSV checksum mismatch; rerun extraction")
    if (before[workbook] != table["input_sha256"] or before[original] != table["publisher_sha256"]
            or before[workbook] != before[original]):
        raise ValueError("Source workbook checksum mismatch")
    node_output = next(item for item in node_manifest["outputs"]
                       if item["file"] == "data/extracted/diagnoses.csv")
    if before[node_path] != node_output["sha256"]:
        raise ValueError("Diagnosis CSV checksum mismatch; rerun diagnosis preparation")
    fields, rows = read_csv(input_path)
    _, diagnoses = read_csv(node_path)
    if fields != INPUT_FIELDS:
        raise ValueError("Unexpected trajectory CSV header")
    if len(rows) != 1171 or len(rows) != table["record_count"]:
        raise ValueError("Trajectory record count does not match the published extraction")
    if len(diagnoses) != node_output["record_count"]:
        raise ValueError("Diagnosis count does not match its manifest")
    records, checks = build_records(rows, diagnoses)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("An input changed during preparation; no output was written")
    output_path = directory / "trajectories.csv"
    write_csv(output_path, OUTPUT_FIELDS, records)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("An input changed during preparation; check sources and rerun")
    report = {
        "schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": STATUS, "source_id": SOURCE_ID, "source_doi": DOI,
        "inputs_unchanged": True,
        "inputs": [{"file": path.relative_to(root).as_posix(), "sha256": digest}
                   for path, digest in before.items()],
        "output": {"file": output_path.relative_to(root).as_posix(), "record_count": len(records),
                   "sha256": sha256(output_path), "fields": OUTPUT_FIELDS},
        "validation": checks,
        "notes": [
            "Each record retains a complete ordered four-diagnosis sequence and all original fields.",
            "Source trajectory_id is preserved; trajectory_record_id uniquely identifies the source row.",
            "Cluster label 'None' is preserved as literal source text, not converted to a missing value.",
            "count_final_reported preserves the ambiguous source column-P header '1->...->3'.",
            "Counts and timing are not aggregated, reinterpreted, or converted to probabilities or intervals.",
            "No pair relationships are created or updated. Both supplements belong to study S006; "
            "the trajectory table is not independent confirmation of the pair table.",
        ],
    }
    (directory / "jensen_trajectories_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    result = prepare(parser.parse_args().project_root.resolve())
    print(f"{result['output']['file']}: {result['output']['record_count']:,} complete trajectories")
    print("All four diagnosis positions resolved. Sources unchanged; pair evidence not modified.")
