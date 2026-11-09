# Local Neo4j graph

The Jensen dataset is imported into a project-local Neo4j Community 5.26.33 instance. Database files, runtime files and logs are under `.local/`; connection settings and the generated password are in `.env`. Both locations are Git-ignored. No Windows service or system-wide Neo4j installation was created. Java 21 already available on this computer is used.

## Open the graph

Open [Neo4j Browser](http://127.0.0.1:7474/browser/).

- Connection: `bolt://127.0.0.1:7687`.
- Username: `neo4j`.
- Password: the `NEO4J_PASSWORD` value in the project's local `.env` file.

The instance listens on the local computer only. Credentials are not included in project documentation or generated review reports.

## Imported contents

| Graph element | Count | Purpose |
|---|---:|---|
| `Diagnosis` nodes | 681 | Study-specific diagnosis codes and names |
| `TEMPORALLY_ASSOCIATED_WITH` connections | 4,014 | Observed directional pairs and their statistics |
| `Trajectory` nodes | 1,171 | Complete observed four-diagnosis sequences, counts and timing |
| `INCLUDES_DIAGNOSIS` connections | 4,684 | Four ordered positions per trajectory |
| `Study` nodes | 1 | Jensen publication identity and bibliographic metadata |
| `REPORTED_IN` connections | 1,852 | Diagnosis and trajectory links to their study |

There are 1,853 nodes and 10,550 connections overall. Trajectory-position and study-reference connections are structural supporting information, not additional disease associations.

Relationship direction follows diagnosis 1 to diagnosis 2. Patient counts and relative risks belong to that study-specific connection. Full trajectories remain separate; their counts have not been added to pair counts or counted as independent replication.

The user-facing relationship caption is **Associated with a later diagnosis of**, stored in `display_label`. The technical type remains `TEMPORALLY_ASSOCIATED_WITH` so existing queries keep working. The importer preserves this display label on subsequent imports. In Neo4j Browser, select the relationship type in the graph details panel and choose `display_label` as its caption. A reusable GraSS rule is saved at `src/graph/browser_style.grass`. Browser captions are display settings; the project application has not yet been built.

Every imported CSV record is retained exactly in `source_record_json`, alongside useful typed properties. Relative risks also retain `relative_risk_reported`, and timing retains the original reported text alongside numeric fields. Less-than p-values and reported zeros remain intact. The ambiguous trajectory column P remains `count_final_reported`.

`extraction_review_status=passed` records a source-to-extraction accuracy check. `clinical_review_status=not_reviewed` remains explicit. The original CSV review status is preserved. Importing these observations does not validate a causal explanation or an individual patient's probability.

## Review performed

An independent, read-only `openpyxl` comparison checked all 60,047 original workbook data cells. The check also reconciled every prepared diagnosis, association and complete trajectory with the first-stage exports.

Codex inspected twenty side-by-side examples: ten pairs spread through the first workbook and ten complete trajectories spanning all six reported cluster labels in the second. The comparison covered diagnosis codes/names, order, counts, relative risks, statistics and timing. Numeric display precision differences were checked without rounding away the source text. The source column-P ambiguity remains flagged rather than corrected.

This was assistant extraction review, not human supervisor or clinical signoff. Local evidence is saved under `data/reviewed/`:

- `jensen_spotcheck.md`: the twenty source/export comparisons.
- `jensen_validation.json`: full reconciliation results, source hashes and selected examples.
- `jensen_spotcheck_signoff.json`: assistant reviewer identity, review scope and matching input hashes.
- `neo4j_import_report.json`: imported counts, verification and repeat-import results.
- `neo4j_search_examples.json`: tested backward/forward searches and an ordered full trajectory.

## Commands

Run these from the project folder with Python 3.10+. On this computer, the commands were executed with the bundled Python runtime. Only the independent workbook review needs an extra package (`openpyxl`, pinned in `requirements.txt`). The local Neo4j client and import scripts use the standard library.

```powershell
python -m pip install -r requirements.txt
python src/graph/local_neo4j.py status
```

After a reboot, start the existing project instance:

```powershell
python src/graph/local_neo4j.py start
```

For a new local setup, `python src/graph/local_neo4j.py setup` downloads the pinned Windows archive, checks its SHA-256 checksum, configures local-only connectors and initializes a generated password. It does not reset credentials for an existing database. Runtime data is not recreated by `start`.

To repeat the source comparison:

```powershell
python src/graph/review_jensen.py
```

The import gate requires a passing comparison and a spot-check signoff matching the review sheet and input hashes. A changed dataset requires another twenty-example inspection and a new accurately attributed signoff. The review script does not claim that a person inspected the examples or create an assistant signoff automatically.

To import or repeat the import of the reviewed dataset:

```powershell
python src/graph/import_jensen.py
```

The importer uses uniqueness constraints and `MERGE`, makes no deletions, and rejects a target containing unrelated nodes. Data writes are submitted in one transaction. Afterward it reads back and compares every record property, association direction, trajectory position and study reference. Re-import was tested and created zero additional nodes or connections.

Bounded exploration by diagnosis code:

```powershell
python src/graph/explore.py E11 --direction forward --depth 1 --limit 10
python src/graph/explore.py N18 --direction backward --depth 1 --limit 10
python src/graph/explore.py N18 --direction both --depth 2 --limit 10
```

CLI result lists start at the queried diagnosis. In backward mode, the list then visits its predecessors; stored relationship arrows still point from the earlier diagnosis to the later one. Depth is bounded to 1–3 hops. A path assembled by traversing pair connections is not automatically a full sequence observed in the same patients. Use the separate trajectory records for that question.

Browser queries are in `src/graph/example_queries.cypher`. The Browser is a database exploration interface; a project application and GraphRAG explanation service have not yet been implemented.

## Technical references

- [Neo4j Windows installation](https://neo4j.com/docs/operations-manual/current/installation/windows/).
- [Official deployment center](https://neo4j.com/deployment-center/) and [pinned download checksum](https://dist.neo4j.org/neo4j-community-5.26.33-windows.zip.sha256).
- [Connector configuration](https://neo4j.com/docs/operations-manual/5/configuration/connectors/).
- [Cypher MERGE and constraints](https://neo4j.com/docs/cypher-manual/5/clauses/merge/).
- [Transactional HTTP API](https://neo4j.com/docs/http-api/current/query/) and [error handling](https://neo4j.com/docs/http-api/current/error-handling/). This endpoint is supported in the pinned 5.26 prototype but deprecated there; the transport is isolated in `neo4j_client.py` for a later move to the Bolt driver or Query API.
