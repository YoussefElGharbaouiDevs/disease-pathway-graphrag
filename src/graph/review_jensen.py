"""Independently check workbook values and prepare a 20-record extraction review.

Requires openpyxl 3.1.5. Does not edit any source or prepared CSV.
"""

from __future__ import annotations

import csv
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extraction"))
from extract_jensen import PAIR_COLUMNS, TRAJECTORY_COLUMNS, sha256


ROOT = Path(__file__).resolve().parents[2]


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def review(root=ROOT):
    from openpyxl import load_workbook

    directory = root / "data/extracted"
    protected = [directory / name for name in [
        "jensen_diagnosis_pairs.csv", "jensen_trajectories.csv", "diagnoses.csv",
        "relationships.csv", "trajectories.csv", "jensen_extraction_manifest.json",
        "jensen_graph_tables_manifest.json", "jensen_trajectories_manifest.json",
    ]] + [root / "ressources/supplements" / (stem + extension)
          for stem in ("ncomms5022-s2", "ncomms5022-s3") for extension in (".xlsx", ".zip")]
    before = {path: sha256(path) for path in protected}
    extraction = json.loads((directory / "jensen_extraction_manifest.json").read_text())
    for table in extraction["tables"]:
        check(sha256(root / table["output_file"]) == table["output_sha256"], "Stale extraction CSV")
        check(sha256(root / table["input_file"]) == table["input_sha256"], "Changed workbook")
        check(sha256(root / table["publisher_original"]) == table["input_sha256"], "Changed publisher original")
    graph_manifest = json.loads((directory / "jensen_graph_tables_manifest.json").read_text())
    trajectory_manifest = json.loads((directory / "jensen_trajectories_manifest.json").read_text())
    for output in graph_manifest["outputs"]:
        check(sha256(root / output["file"]) == output["sha256"], "Changed graph table")
    check(sha256(root / trajectory_manifest["output"]["file"]) == trajectory_manifest["output"]["sha256"],
          "Changed prepared trajectory table")

    pairs = csv_rows(directory / "jensen_diagnosis_pairs.csv")
    raw_trajectories = csv_rows(directory / "jensen_trajectories.csv")
    nodes = csv_rows(directory / "diagnoses.csv")
    links = csv_rows(directory / "relationships.csv")
    trajectories = csv_rows(directory / "trajectories.csv")
    check((len(nodes), len(links), len(trajectories)) == (681, 4014, 1171), "Unexpected graph record counts")
    node_by_id = {node["diagnosis_id"]: node for node in nodes}
    check(len(node_by_id) == len(nodes), "Duplicate diagnosis IDs")
    check(len({link["relationship_id"] for link in links}) == len(links), "Duplicate relationship IDs")
    check(len({row["trajectory_record_id"] for row in trajectories}) == len(trajectories), "Duplicate trajectory IDs")
    node_references = {key: set() for key in node_by_id}
    check(len(pairs) == len(links) and len(raw_trajectories) == len(trajectories), "Record loss")
    for raw, link in zip(pairs, links):
        for key in [field for _, field, _, _ in PAIR_COLUMNS[4:]] + [
            "source_id", "source_doi", "source_file", "source_sheet", "source_row"
        ]:
            check(raw[key] == link[key], f"Changed pair value: row {raw['source_row']}, {key}")
        for role, position in (("source", 1), ("target", 2)):
            node = node_by_id[link[f"{role}_diagnosis_id"]]
            check(node["code"] == raw[f"diagnosis_{position}_code"], "Changed pair direction/code")
            check(node["name"] == raw[f"diagnosis_{position}_name"], "Changed diagnosis name")
            node_references[node["diagnosis_id"]].add(int(raw["source_row"]))
        check(link["relationship_type"] == "TEMPORALLY_ASSOCIATED_WITH", "Incorrect relationship meaning")
    for key, node in node_by_id.items():
        check(json.loads(node["source_rows_json"]) == sorted(node_references[key]), "Changed diagnosis provenance")
    for raw, row in zip(raw_trajectories, trajectories):
        check(all(row[key] == value for key, value in raw.items()), "Changed trajectory source values")
        check(row["trajectory_id"] == "_".join(row[f"diagnosis_{p}_code"] for p in range(1, 5)), "Changed sequence order")
        for p in range(1, 5):
            node = node_by_id[row[f"diagnosis_{p}_id"]]
            check((node["code"], node["name"]) == (row[f"diagnosis_{p}_code"], row[f"diagnosis_{p}_name"]),
                  "Changed trajectory diagnosis reference")

    # Ten spread-out pairs and ten trajectories spanning every reported cluster.
    pair_samples = {6, 22, 250, 638, 1000, 1500, 2000, 2500, 3500, 4019}
    groups = {}
    for row in raw_trajectories:
        groups.setdefault(row["cluster"], []).append(int(row["source_row"]))
    trajectory_samples = {values[0] for values in groups.values()}
    trajectory_samples.update(values[-1] for key, values in list(groups.items())[:4])
    check(len(trajectory_samples) == 10, "Expected ten trajectory samples")
    samples = []
    checked_cells = 0
    for stem, sheet_name, rows, columns, selected in [
        ("ncomms5022-s2", "Supplementary Data 1", pairs, PAIR_COLUMNS, pair_samples),
        ("ncomms5022-s3", "S4 - Trajectories", raw_trajectories, TRAJECTORY_COLUMNS, trajectory_samples),
    ]:
        path = root / "ressources/supplements" / (stem + ".xlsx")
        # The workbook is opened read-only and is never saved. Its extension metadata is irrelevant here.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Unknown extension is not supported.*")
            workbook = load_workbook(path, read_only=True, data_only=False)
            sheet = workbook[sheet_name]
            source_rows = list(sheet.iter_rows(min_row=6, values_only=True))
        check(len(source_rows) == len(rows), "Workbook/CSV row count mismatch")
        for index, (source_cells, row) in enumerate(zip(source_rows, rows), start=6):
            check(int(row["source_row"]) == index, "Original Excel row mismatch")
            source_values = {}
            for letter, field, _, kind in columns:
                source = source_cells[ord(letter) - ord("A")]
                exported = row[field]
                if isinstance(source, (int, float)):
                    matches = float(exported) == source
                else:
                    source = " ".join(str(source).split()) if kind == "text" else str(source).strip()
                    matches = source == exported
                check(matches, f"Workbook mismatch: {stem}!{letter}{index}, {source!r} vs {exported!r}")
                source_values[field] = source
                checked_cells += 1
            if index in selected:
                samples.append({"kind": "pair" if stem.endswith("s2") else "trajectory",
                                "workbook": path.relative_to(root).as_posix(), "sheet": sheet_name,
                                "source_row": index, "excel_values": source_values,
                                "exported_values": {field: row[field] for _, field, _, _ in columns}})
        workbook.close()
    check(len(samples) == 20, "Expected twenty review samples")
    check(all(sha256(path) == digest for path, digest in before.items()), "Input changed during review")
    lines = ["# Jensen extraction spot-check", "",
             "20 source-to-extraction examples: ten pairs and ten full trajectories, including every cluster.",
             "Original Excel values and exports are shown separately below. Numeric display precision may differ; "
             "the full export retains the source XML numeric text. This is extraction review, not clinical validation.",
             "", "The original trajectory column P reads `1->...->3` after diagnosis 4. Its meaning remains flagged "
             "under `count_final_reported`; it has not been silently repaired.", ""]
    for number, sample in enumerate(samples, start=1):
        lines += [f"## {number}. {sample['kind']} — Excel row {sample['source_row']}", "",
                  f"Workbook: `{sample['workbook']}`; sheet: `{sample['sheet']}`.", "",
                  "| Field | Original Excel value | Exported value |", "|---|---|---|"]
        for key, source in sample["excel_values"].items():
            value = sample["exported_values"][key]
            lines.append(f"| {key} | {str(source).replace('|', '/')} | {value.replace('|', '/')} |")
        lines += ["", "Automated comparison: PASS. Assistant spot-check is recorded separately.", ""]
    destination = root / "data/reviewed"
    destination.mkdir(exist_ok=True)
    sheet_path = destination / "jensen_spotcheck.md"
    sheet_path.write_text("\n".join(lines), encoding="utf-8")
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "source_comparison_passed", "clinical_review_status": "not_reviewed",
        "independent_reader": "openpyxl 3.1.5 (read-only)", "source_cells_checked": checked_cells,
        "diagnosis_count": len(nodes), "relationship_count": len(links), "trajectory_count": len(trajectories),
        "sample_count": len(samples), "samples": samples,
        "review_sheet": sheet_path.relative_to(root).as_posix(), "review_sheet_sha256": sha256(sheet_path),
        "inputs": {path.relative_to(root).as_posix(): digest for path, digest in before.items()},
    }
    (destination / "jensen_validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked {checked_cells:,} original workbook cells and all prepared graph records.")
    for sample in samples:
        fields = sample["exported_values"]
        codes = " -> ".join(fields[f"diagnosis_{p}_code"] for p in range(1, 3 if sample["kind"] == "pair" else 5))
        if sample["kind"] == "pair":
            values = f"patients={fields['n_patients']}; RR={fields['relative_risk']}"
        else:
            values = f"counts={fields['count_1_to_2']}/{fields['count_1_to_2_to_3']}/{fields['count_final_reported']}; "
            values += f"months={fields['time_to_2_months_reported']}/{fields['time_to_3_months_reported']}/{fields['time_to_4_months_reported']}"
        print(f"{sample['kind']} row {sample['source_row']}: {codes}; {values}; PASS")


if __name__ == "__main__":
    review()
