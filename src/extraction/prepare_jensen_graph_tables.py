"""Prepare candidate diagnosis nodes and temporal links from Jensen pair records.

Run extract_jensen.py first. Python 3.10+; standard library only. No Neo4j writes.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from extract_jensen import DOI, PAIR_COLUMNS, PROVENANCE, SOURCE_ID, clean_value, sha256


RELATIONSHIP_TYPE = "TEMPORALLY_ASSOCIATED_WITH"
STATUS = "not_reviewed_for_graph"
INPUT_FIELDS = [field for _, field, _, _ in PAIR_COLUMNS] + PROVENANCE
STAT_FIELDS = [field for _, field, _, _ in PAIR_COLUMNS[4:]]
DIAGNOSIS_FIELDS = [
    "diagnosis_id", "code", "name", "coding_system", "code_level", "coding_version",
    "source_id", "source_doi", "source_file", "source_sheet", "source_rows_json", "review_status",
]
RELATIONSHIP_FIELDS = [
    "relationship_id", "source_diagnosis_id", "target_diagnosis_id", "relationship_type",
] + STAT_FIELDS + PROVENANCE + ["review_status"]


def build_records(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict], dict]:
    """Keep one node per source/code and one evidence link per source row."""
    concepts = {}
    references = defaultdict(set)
    relationships = []
    evidence_ids = set()
    pairs = Counter()
    for row in rows:
        if set(row) != set(INPUT_FIELDS):
            raise ValueError("Pair record fields do not match the extraction schema")
        for _, field, _, kind in PAIR_COLUMNS:
            if clean_value(row[field], kind) != row[field]:
                raise ValueError(f"Unclean input field: {field}")
        if (row["source_id"], row["source_doi"], row["source_file"], row["source_sheet"]) != (
            SOURCE_ID, DOI, "ressources/supplements/ncomms5022-s2.xlsx", "Supplementary Data 1"
        ):
            raise ValueError("Unexpected study or workbook provenance")
        if not re.fullmatch(r"[1-9][0-9]*", row["source_row"]) or int(row["source_row"]) < 6:
            raise ValueError("Invalid source Excel row")

        endpoints = []
        for position in (1, 2):
            code = row[f"diagnosis_{position}_code"]
            name = row[f"diagnosis_{position}_name"]
            if not re.fullmatch(r"[A-Z][0-9]{2}", code):
                raise ValueError(f"Unexpected three-character diagnosis code: {code!r}")
            # Source-qualified IDs avoid merging different studies/editions implicitly.
            diagnosis_id = f"{SOURCE_ID}:ICD10:{code}"
            if diagnosis_id in concepts and concepts[diagnosis_id]["name"] != name:
                raise ValueError(f"Conflicting names for {code}; manual review required")
            if diagnosis_id not in concepts:
                concepts[diagnosis_id] = {
                    "diagnosis_id": diagnosis_id, "code": code, "name": name,
                    "coding_system": "ICD-10", "code_level": "three-character category",
                    "coding_version": "not_specified_in_table",
                    **{field: row[field] for field in PROVENANCE if field != "source_row"},
                    "review_status": STATUS,
                }
            references[diagnosis_id].add(int(row["source_row"]))
            endpoints.append(diagnosis_id)

        relationship_id = f"{SOURCE_ID}:SD1:{row['source_row']}"
        if relationship_id in evidence_ids:
            raise ValueError(f"Repeated source row: {relationship_id}")
        evidence_ids.add(relationship_id)
        relationships.append({
            "relationship_id": relationship_id,
            "source_diagnosis_id": endpoints[0], "target_diagnosis_id": endpoints[1],
            "relationship_type": RELATIONSHIP_TYPE,
            **{field: row[field] for field in STAT_FIELDS + PROVENANCE},
            "review_status": STATUS,
        })
        pairs[tuple(endpoints)] += 1

    diagnoses = []
    for key, record in sorted(concepts.items()):
        record["source_rows_json"] = json.dumps(sorted(references[key]), separators=(",", ":"))
        diagnoses.append(record)
    if not diagnoses or not relationships:
        raise ValueError("No diagnosis or relationship records found")
    if not all(r[field] in concepts for r in relationships
               for field in ("source_diagnosis_id", "target_diagnosis_id")):
        raise ValueError("A relationship endpoint has no diagnosis record")
    diagnostics = {
        "diagnosis_count": len(diagnoses), "relationship_count": len(relationships),
        "distinct_directed_pair_count": len(pairs),
        "repeated_pair_evidence_count": sum(count - 1 for count in pairs.values()),
        "conflicting_diagnosis_names": 0, "dangling_relationship_endpoints": 0,
    }
    return diagnoses, relationships, diagnostics


def write_csv(path: Path, fields: list[str], records: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if list(csv.DictReader(stream)) != records:
            raise RuntimeError(f"CSV read-back failed: {path.name}")


def prepare(root: Path) -> dict:
    output_dir = root / "data/extracted"
    manifest_path = output_dir / "jensen_extraction_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_id") != SOURCE_ID or manifest.get("source_doi") != DOI:
        raise ValueError("Unexpected extraction manifest study")
    table = next(item for item in manifest["tables"]
                 if item["output_file"] == "data/extracted/jensen_diagnosis_pairs.csv")
    input_path = output_dir / "jensen_diagnosis_pairs.csv"
    workbook = root / "ressources/supplements/ncomms5022-s2.xlsx"
    original = root / "ressources/supplements/ncomms5022-s2.zip"
    if (table["input_file"] != workbook.relative_to(root).as_posix()
            or table["publisher_original"] != original.relative_to(root).as_posix()
            or table["sheet"] != "Supplementary Data 1"):
        raise ValueError("Unexpected extraction manifest source")
    before = {path: sha256(path) for path in (input_path, manifest_path, workbook, original)}
    if before[input_path] != table["output_sha256"]:
        raise ValueError("Pair CSV checksum mismatch; rerun extract_jensen.py before preparing graph tables")
    if before[workbook] != table["input_sha256"] or before[original] != table["publisher_sha256"]:
        raise ValueError("Source workbook checksum mismatch")
    if before[workbook] != before[original]:
        raise ValueError("Source workbook differs from publisher original")
    with input_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != INPUT_FIELDS:
            raise ValueError("Unexpected pair CSV header")
        rows = list(reader)
    if len(rows) != 4014 or len(rows) != table["record_count"]:
        raise ValueError("Pair record count does not match the published extraction")
    diagnoses, relationships, checks = build_records(rows)
    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("An input changed during processing; no outputs were written")

    output_tables = []
    for name, fields, records in [
        ("diagnoses.csv", DIAGNOSIS_FIELDS, diagnoses),
        ("relationships.csv", RELATIONSHIP_FIELDS, relationships),
    ]:
        path = output_dir / name
        write_csv(path, fields, records)
        output_tables.append({"file": path.relative_to(root).as_posix(),
                              "record_count": len(records), "sha256": sha256(path), "fields": fields})
    if any(sha256(path) != digest for path, digest in before.items()):
        raise RuntimeError("An input changed during processing; check sources and rerun")
    report = {
        "schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": STATUS, "relationship_type": RELATIONSHIP_TYPE,
        "inputs_unchanged": True,
        "inputs": [{"file": path.relative_to(root).as_posix(), "sha256": digest}
                   for path, digest in before.items()],
        "validation": checks, "outputs": output_tables,
        "notes": [
            "Diagnosis labels are study-reported names, not current terminology mappings.",
            "ICD-10 edition/national-version mapping has not been resolved.",
            "Relationships are population-level temporal associations, not proven causes or individual probabilities.",
            "No patient counts, relative risks or p-values are aggregated or recalculated.",
            "The trajectory table is not used to generate additional pair evidence in this step.",
        ],
    }
    (output_dir / "jensen_graph_tables_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = prepare(args.project_root.resolve())
    for output in result["outputs"]:
        print(f"{output['file']}: {output['record_count']:,} records")
    print("All endpoints resolved. Source checksums unchanged. Records remain unreviewed.")
