"""Check evidence preservation and rejection of ambiguous/stale inputs."""

import copy
import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/extraction"))
from prepare_jensen_graph_tables import build_records, prepare, sha256


def example(row="6", code_1="E11", code_2="N18"):
    return {
        "diagnosis_1_code": code_1, "diagnosis_1_name": "Diagnosis " + code_1,
        "diagnosis_2_code": code_2, "diagnosis_2_name": "Diagnosis " + code_2,
        "n_patients": "8515", "relative_risk": "2.442088",
        "rr_p_value_estimated": "0", "rr_p_value_sampled": "< 1.214E-08",
        "n_samples": "82360600", "direction_p_value": "0",
        "source_id": "S006", "source_doi": "10.1038/ncomms5022",
        "source_file": "ressources/supplements/ncomms5022-s2.xlsx",
        "source_sheet": "Supplementary Data 1", "source_row": row,
    }


class EvidenceTests(unittest.TestCase):
    def test_reverse_and_repeat_pairs_retain_separate_evidence(self):
        rows = [example(), example("7", "N18", "E11"), example("8")]
        diagnoses, relationships, checks = build_records(rows)
        self.assertEqual(len(diagnoses), 2)
        self.assertEqual(len(relationships), 3)
        self.assertEqual(checks["repeated_pair_evidence_count"], 1)
        self.assertEqual(relationships[0]["source_diagnosis_id"], relationships[1]["target_diagnosis_id"])
        self.assertNotEqual(relationships[0]["relationship_id"], relationships[2]["relationship_id"])
        self.assertEqual(relationships[0]["rr_p_value_sampled"], "< 1.214E-08")
        self.assertEqual(relationships[0]["rr_p_value_estimated"], "0")
        self.assertTrue(all(r["relationship_type"] == "TEMPORALLY_ASSOCIATED_WITH" for r in relationships))
        self.assertTrue(all(r["review_status"] == "not_reviewed_for_graph" for r in relationships))
        self.assertEqual(json.loads(diagnoses[0]["source_rows_json"]), [6, 7, 8])

    def test_conflicting_names_require_review(self):
        first = example()
        second = example("7")
        second["diagnosis_1_name"] = "Different source label"
        with self.assertRaisesRegex(ValueError, "Conflicting names"):
            build_records([first, second])

    def test_repeated_source_location_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Repeated source row"):
            build_records([example(), copy.deepcopy(example())])

    def test_unexpected_codes_are_not_silently_fixed(self):
        with self.assertRaisesRegex(ValueError, "three-character"):
            build_records([example(code_1="E11.9")])

    def test_real_inputs_preserved_and_modified_csv_rejected(self):
        # Test all output writes in an isolated temporary project.
        with tempfile.TemporaryDirectory(prefix="jensen-graph-test-") as folder:
            root = Path(folder)
            paths = [
                "data/extracted/jensen_diagnosis_pairs.csv",
                "data/extracted/jensen_extraction_manifest.json",
                "ressources/supplements/ncomms5022-s2.xlsx",
                "ressources/supplements/ncomms5022-s2.zip",
            ]
            for name in paths:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, root / name)
            before = {name: sha256(root / name) for name in paths}
            report = prepare(root)
            self.assertEqual(report["validation"]["relationship_count"], 4014)
            self.assertEqual(report["validation"]["diagnosis_count"], 681)
            self.assertEqual(before, {name: sha256(root / name) for name in paths})
            outputs = {item["file"]: sha256(root / item["file"]) for item in report["outputs"]}
            prepare(root)
            self.assertEqual(outputs, {name: sha256(root / name) for name in outputs})
            with (root / "data/extracted/relationships.csv").open(encoding="utf-8-sig", newline="") as stream:
                links = list(csv.DictReader(stream))
            row_22 = next(link for link in links if link["source_row"] == "22")
            self.assertEqual(row_22["source_diagnosis_id"], "S006:ICD10:E11")
            self.assertEqual(row_22["target_diagnosis_id"], "S006:ICD10:N18")
            self.assertEqual(row_22["relative_risk"], "2.442088")
            changed = root / paths[0]
            changed.write_bytes(changed.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                prepare(root)
            self.assertEqual(outputs, {name: sha256(root / name) for name in outputs})


if __name__ == "__main__":
    unittest.main()
