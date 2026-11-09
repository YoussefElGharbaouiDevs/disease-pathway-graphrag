"""Import the extraction-checked Jensen dataset, retaining its clinical-review limits."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from neo4j_client import ASSOCIATION_DISPLAY_LABEL, Client, PROJECT_ID, ROOT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gate(root):
    review = json.loads((root / "data/reviewed/jensen_validation.json").read_text())
    signoff = json.loads((root / "data/reviewed/jensen_spotcheck_signoff.json").read_text())
    if review["status"] != "source_comparison_passed" or signoff["status"] != "passed":
        raise ValueError("Extraction review has not passed")
    if (review["sample_count"] != 20 or signoff["sample_count"] != 20
            or review["review_sheet_sha256"] != signoff["review_sheet_sha256"]
            or sha(root / review["review_sheet"]) != review["review_sheet_sha256"]
            or review["inputs"] != signoff["inputs"]):
        raise ValueError("Spot-check signoff does not match the reviewed dataset")
    if any(sha(root / name) != digest for name, digest in review["inputs"].items()):
        raise ValueError("Reviewed inputs changed; repeat extraction review before import")
    rows = {}
    for name in ("diagnoses", "relationships", "trajectories"):
        with (root / f"data/extracted/{name}.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows[name] = list(csv.DictReader(stream))
    return rows, review


def properties(row, kind):
    result = dict(row)
    # Exact original values remain available even when Neo4j stores typed numbers.
    result.update(source_record_json=json.dumps(row, sort_keys=True, ensure_ascii=False),
                  project_id=PROJECT_ID, extraction_review_status="passed", clinical_review_status="not_reviewed")
    if "source_row" in result:
        result["source_row"] = int(result["source_row"])
    if kind == "diagnosis":
        result["source_rows"] = json.loads(result["source_rows_json"])
    elif kind == "relationship":
        result["display_label"] = ASSOCIATION_DISPLAY_LABEL
        result["n_patients"] = int(result["n_patients"])
        result["n_samples"] = int(result["n_samples"])
        result["relative_risk_reported"] = result["relative_risk"]
        result["relative_risk"] = float(result["relative_risk"])
    elif kind == "trajectory":
        for field in ("count_1_to_2", "count_1_to_2_to_3"):
            result[field] = int(result[field])
        result["median_start_age_years_reported"] = result["median_start_age_years"]
        result["median_start_age_years"] = float(result["median_start_age_years"])
        for position in (2, 3, 4):
            result[f"time_to_{position}_months"] = float(result[f"time_to_{position}_months_reported"])
    return result


CONSTRAINTS = [
    "CREATE CONSTRAINT pfa_diagnosis_id IF NOT EXISTS FOR (n:Diagnosis) REQUIRE n.diagnosis_id IS UNIQUE",
    "CREATE CONSTRAINT pfa_trajectory_id IF NOT EXISTS FOR (n:Trajectory) REQUIRE n.trajectory_record_id IS UNIQUE",
    "CREATE CONSTRAINT pfa_study_id IF NOT EXISTS FOR (n:Study) REQUIRE n.source_id IS UNIQUE",
    "CREATE CONSTRAINT pfa_association_id IF NOT EXISTS FOR ()-[r:TEMPORALLY_ASSOCIATED_WITH]-() REQUIRE r.relationship_id IS UNIQUE",
]


def verify(client, rows):
    counts = {}
    for table, label, key, kind in [
        ("diagnoses", "Diagnosis", "diagnosis_id", "diagnosis"),
        ("trajectories", "Trajectory", "trajectory_record_id", "trajectory"),
    ]:
        actual = client.query(f"MATCH (n:{label} {{project_id:$project}}) RETURN properties(n) AS props",
                              {"project": PROJECT_ID})
        by_id = {item["props"][key]: item["props"] for item in actual}
        if len(by_id) != len(actual) or len(actual) != len(rows[table]):
            raise ValueError(f"Imported {table} count mismatch")
        for row in rows[table]:
            expected = properties(row, kind)
            if any(by_id.get(row[key], {}).get(field) != value for field, value in expected.items()):
                raise ValueError(f"Imported {table} property mismatch: {row[key]}")
        counts[table] = len(actual)
    actual = client.query("MATCH (a:Diagnosis)-[r:TEMPORALLY_ASSOCIATED_WITH {project_id:$project}]->(b:Diagnosis) "
                          "RETURN a.diagnosis_id AS start, b.diagnosis_id AS end, properties(r) AS props",
                          {"project": PROJECT_ID})
    by_id = {item["props"]["relationship_id"]: item for item in actual}
    if len(actual) != len(rows["relationships"]) or len(by_id) != len(actual):
        raise ValueError("Association count mismatch")
    for row in rows["relationships"]:
        item = by_id[row["relationship_id"]]
        if (item["start"], item["end"]) != (row["source_diagnosis_id"], row["target_diagnosis_id"]):
            raise ValueError("Imported association direction mismatch")
        if any(item["props"].get(field) != value for field, value in properties(row, "relationship").items()):
            raise ValueError("Imported association property mismatch")
    counts["temporal_associations"] = len(actual)
    steps = client.query("MATCH (t:Trajectory {project_id:$project})-[r:INCLUDES_DIAGNOSIS]->(d:Diagnosis) "
                         "RETURN t.trajectory_record_id AS id, r.position AS position, d.diagnosis_id AS diagnosis",
                         {"project": PROJECT_ID})
    actual_steps = sorted((r["id"], r["position"], r["diagnosis"]) for r in steps)
    expected_steps = sorted((row["trajectory_record_id"], p, row[f"diagnosis_{p}_id"])
                            for row in rows["trajectories"] for p in range(1, 5))
    if actual_steps != expected_steps:
        raise ValueError("Imported trajectory positions mismatch")
    counts["trajectory_positions"] = len(steps)
    study = client.query("MATCH (s:Study {source_id:'S006',project_id:$project}) "
                         "OPTIONAL MATCH (n {project_id:$project})-[:REPORTED_IN]->(s) "
                         "RETURN count(DISTINCT s) AS studies, count(n) AS references", {"project": PROJECT_ID})[0]
    if study != {"studies": 1, "references": len(rows["diagnoses"]) + len(rows["trajectories"])}:
        raise ValueError("Study provenance reference mismatch")
    counts.update(study)
    return counts


def run(root=ROOT):
    rows, review = load_gate(root)
    client = Client(root)
    foreign = client.query("MATCH (n) WHERE n.project_id IS NULL OR n.project_id <> $project RETURN count(n) AS n",
                           {"project": PROJECT_ID})[0]["n"]
    if foreign:
        raise ValueError("Target contains unrelated nodes; use the dedicated project Neo4j instance")
    client.commit([{"statement": query} for query in CONSTRAINTS])
    source = next(item for item in json.loads((root / "ressources/sources.json").read_text())["sources"]
                  if item["source_id"] == "S006")
    study = {field: source[field] for field in ("source_id", "title", "doi", "pmid", "pmcid", "pubmed_url")}
    study.update(project_id=PROJECT_ID, evidence_scope="population-level temporal associations",
                 extraction_review_status="passed", clinical_review_status="not_reviewed")
    nodes = [properties(row, "diagnosis") for row in rows["diagnoses"]]
    links = [properties(row, "relationship") for row in rows["relationships"]]
    trajectories = [properties(row, "trajectory") for row in rows["trajectories"]]
    statements = [
        ("MERGE (s:Study {source_id:$study.source_id}) SET s += $study", {"study": study}),
        ("UNWIND $rows AS row MERGE (d:Diagnosis {diagnosis_id:row.diagnosis_id}) SET d += row "
         "WITH d MATCH (s:Study {source_id:'S006'}) MERGE (d)-[:REPORTED_IN]->(s)", {"rows": nodes}),
        ("UNWIND $rows AS row MATCH (a:Diagnosis {diagnosis_id:row.source_diagnosis_id}) "
         "MATCH (b:Diagnosis {diagnosis_id:row.target_diagnosis_id}) "
         "MERGE (a)-[r:TEMPORALLY_ASSOCIATED_WITH {relationship_id:row.relationship_id}]->(b) SET r += row",
         {"rows": links}),
        ("UNWIND $rows AS row MERGE (t:Trajectory {trajectory_record_id:row.trajectory_record_id}) SET t += row "
         "WITH t MATCH (s:Study {source_id:'S006'}) MERGE (t)-[:REPORTED_IN]->(s)", {"rows": trajectories}),
        ("UNWIND $rows AS row MATCH (t:Trajectory {trajectory_record_id:row.trajectory_record_id}) "
         "UNWIND [1,2,3,4] AS position "
         "WITH t,row,position,[row.diagnosis_1_id,row.diagnosis_2_id,row.diagnosis_3_id,row.diagnosis_4_id][position-1] AS id "
         "MATCH (d:Diagnosis {diagnosis_id:id}) MERGE (t)-[:INCLUDES_DIAGNOSIS {position:position}]->(d)",
         {"rows": trajectories}),
    ]
    result = client.commit([{"statement": query, "parameters": parameters, "includeStats": True}
                            for query, parameters in statements])
    counts = verify(client, rows)
    report = {"imported_at_utc": datetime.now(timezone.utc).isoformat(), "status": "imported_and_verified",
              "project_id": PROJECT_ID, "counts": counts,
              "clinical_review_status": "not_reviewed", "spotcheck_reviewer": "Codex (assistant)",
              "reviewed_inputs": review["inputs"], "transaction_stats": [item["stats"] for item in result]}
    (root / "data/reviewed/neo4j_import_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(counts, indent=2))
    print("Imported and verified every record and property. Clinical review remains pending.")
    return report


if __name__ == "__main__":
    run()
