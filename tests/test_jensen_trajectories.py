"""Check full-path retention, separate evidence identity, and source integrity."""

import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/extraction"))
from prepare_jensen_trajectories import build_records, prepare, read_csv, sha256


def fixtures():
    _, rows = read_csv(ROOT / "data/extracted/jensen_trajectories.csv")
    _, diagnoses = read_csv(ROOT / "data/extracted/diagnoses.csv")
    return rows[0].copy(), diagnoses


class TrajectoryTests(unittest.TestCase):
    def test_full_path_and_all_reported_values_survive(self):
        row, diagnoses = fixtures()
        second = dict(row, source_row="7", cluster="None")
        records, checks = build_records([row, second], diagnoses)
        self.assertEqual(len(records), 2)  # Identical sequences in separate source rows stay separate.
        self.assertEqual(checks["repeated_sequence_record_count"], 1)
        self.assertNotEqual(records[0]["trajectory_record_id"], records[1]["trajectory_record_id"])
        for field, value in row.items():
            self.assertEqual(records[0][field], value)
        self.assertEqual(records[1]["cluster"], "None")
        self.assertEqual(records[0]["diagnosis_4_id"], "S006:ICD10:E86")
        self.assertEqual(records[0]["count_final_reported"], "50")
        self.assertEqual(records[0]["time_to_4_months_reported"], "93.09")
        self.assertEqual(records[0]["evidence_type"], "OBSERVED_DIAGNOSIS_TRAJECTORY")
        self.assertEqual(records[0]["review_status"], "not_reviewed_for_graph")

    def test_order_and_source_row_identity_checked(self):
        row, diagnoses = fixtures()
        with self.assertRaisesRegex(ValueError, "Repeated trajectory source row"):
            build_records([row, row.copy()], diagnoses)
        row["trajectory_id"] = "E86_L97_A46_E11"
        with self.assertRaisesRegex(ValueError, "ordered diagnosis codes"):
            build_records([row], diagnoses)

    def test_missing_diagnosis_reference_is_rejected(self):
        row, diagnoses = fixtures()
        diagnoses = [node for node in diagnoses if node["code"] != "E86"]
        with self.assertRaisesRegex(ValueError, "missing from diagnoses"):
            build_records([row], diagnoses)

    def test_label_conflict_is_rejected(self):
        row, diagnoses = fixtures()
        row["diagnosis_1_name"] = "Unreviewed alternate label"
        with self.assertRaisesRegex(ValueError, "label conflict"):
            build_records([row], diagnoses)

    def test_real_inputs_repeatable_and_modified_csv_rejected(self):
        paths = [
            "data/extracted/jensen_trajectories.csv", "data/extracted/jensen_extraction_manifest.json",
            "data/extracted/diagnoses.csv", "data/extracted/jensen_graph_tables_manifest.json",
            "ressources/supplements/ncomms5022-s3.xlsx", "ressources/supplements/ncomms5022-s3.zip",
        ]
        with tempfile.TemporaryDirectory(prefix="jensen-trajectory-test-") as folder:
            root = Path(folder)
            for name in paths:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, root / name)
            before = {name: sha256(root / name) for name in paths}
            report = prepare(root)
            self.assertEqual(report["validation"]["trajectory_record_count"], 1171)
            self.assertEqual(report["validation"]["diagnosis_codes_in_trajectories"], 140)
            self.assertEqual(before, {name: sha256(root / name) for name in paths})
            output = root / "data/extracted/trajectories.csv"
            expected = sha256(output)
            prepare(root)
            self.assertEqual(sha256(output), expected)
            _, source = read_csv(root / paths[0])
            _, records = read_csv(output)
            for raw, record in zip(source, records):
                self.assertTrue(all(record[field] == value for field, value in raw.items()))
            changed = root / paths[0]
            changed.write_bytes(changed.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                prepare(root)
            self.assertEqual(sha256(output), expected)


if __name__ == "__main__":
    unittest.main()
