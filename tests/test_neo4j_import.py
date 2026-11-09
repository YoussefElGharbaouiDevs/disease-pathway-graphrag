"""Check import gates, exact evidence retention and server-error handling."""

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/graph"))
from import_jensen import load_gate, properties
from neo4j_client import Client


class ImportTests(unittest.TestCase):
    def test_original_numeric_evidence_survives_typed_properties(self):
        row = {"relative_risk": "3.0971929999999999", "n_patients": "2889", "n_samples": "82360600",
               "source_row": "6", "rr_p_value_estimated": "0", "rr_p_value_sampled": "< 1.214E-08"}
        stored = properties(row, "relationship")
        self.assertEqual(json.loads(stored["source_record_json"]), row)
        self.assertEqual(stored["relative_risk_reported"], row["relative_risk"])
        self.assertEqual(stored["n_patients"], 2889)
        self.assertEqual(stored["rr_p_value_estimated"], "0")
        self.assertEqual(stored["rr_p_value_sampled"], "< 1.214E-08")
        self.assertEqual(stored["clinical_review_status"], "not_reviewed")

    def test_changed_reviewed_dataset_is_rejected(self):
        report = json.loads((ROOT / "data/reviewed/jensen_validation.json").read_text())
        names = list(report["inputs"]) + [
            "data/reviewed/jensen_validation.json", "data/reviewed/jensen_spotcheck_signoff.json",
            report["review_sheet"],
        ]
        with tempfile.TemporaryDirectory(prefix="pfa-import-test-") as directory:
            root = Path(directory)
            for name in names:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, root / name)
            rows, _ = load_gate(root)
            self.assertEqual(len(rows["relationships"]), 4014)
            changed = root / "data/extracted/relationships.csv"
            changed.write_bytes(changed.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "Reviewed inputs changed"):
                load_gate(root)

    def test_http_200_with_cypher_errors_is_not_success(self):
        client = object.__new__(Client)
        client.url = "http://127.0.0.1:7474"
        client.headers = {}
        response = io.BytesIO(json.dumps({"results": [], "errors": [
            {"code": "Neo.ClientError.Statement.SyntaxError", "message": "invalid query"}
        ]}).encode())
        with patch("neo4j_client.urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "Neo4j transaction failed"):
                client.commit([{"statement": "invalid query"}])


if __name__ == "__main__":
    unittest.main()
