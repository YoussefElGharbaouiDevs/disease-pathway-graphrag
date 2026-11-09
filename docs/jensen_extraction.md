# Jensen workbook extraction

This first processing step exports the two Jensen workbooks as flat CSV tables. The workbooks and their original publisher `.zip` copies remain unchanged. This is a format conversion with traceability, not graph validation.

## Run

From the project folder, with Python 3.10 or later:

```powershell
python src/extraction/extract_jensen.py
```

The script uses the Python standard library. No package installation or Excel session is required. It reads only the two explicitly named workbooks, ignoring Excel temporary lock files.

## Generated files

| File under `data/extracted/` | Contents |
|---|---|
| `jensen_diagnosis_pairs.csv` | All 4,014 directional diagnosis-pair records |
| `jensen_trajectories.csv` | All 1,171 four-diagnosis trajectory records |
| `jensen_extraction_manifest.json` | Source/output SHA-256 checksums, record counts, original headers and column mappings |

Each CSV record includes `source_id` (`S006`), `source_doi`, `source_file`, `source_sheet` and `source_row`. The first data row in each workbook is Excel row **6**. To check a record, open its source workbook, select the recorded sheet and go to the recorded row number.

The script replaces stacked Excel headers with one row of descriptive field names. It trims outer whitespace and collapses repeated whitespace in text fields. It preserves codes, diagnosis labels, numeric precision, zero values and p-value expressions such as `< 1.214E-08`. CSV values are textual representations; importing programs should parse count and numeric fields explicitly. The manifest identifies the validation type of each field.

No records are filtered, deduplicated, merged or relabelled as causes. Both tables belong to the same study and are not independent sources of confirmation.

## Column guide

Pair records retain `diagnosis_1_code/name`, `diagnosis_2_code/name`, `n_patients`, `relative_risk`, `rr_p_value_estimated`, `rr_p_value_sampled`, `n_samples` and `direction_p_value`.

Trajectory records retain `cluster`, `trajectory_id`, `median_start_age_years`, four diagnosis codes/names, the three count fields and three time fields in months. The identifier is a diagnosis-sequence identifier, not a patient identifier. The cluster is the study's grouping label.

The source's column P is positioned after diagnosis 4 but labelled `1->...->3`. Its value is exported under the neutral name `count_final_reported`. The original label is retained in the manifest; it has not been silently repaired. The timing fields are named `time_to_2_months_reported`, `time_to_3_months_reported` and `time_to_4_months_reported`. Their source values are preserved without calculating new intervals.

## Integrity checks

Before writing outputs, the script checks the source-register ID/DOI, sheet names, row-5 headers, record counts, required values and numeric validity. It rejects formulas and Excel errors instead of exporting potentially stale cached values. P-values are checked for a valid numeric value or a less-than bound between zero and one.

It checks that each `.xlsx` is byte-identical to its publisher `.zip` original and verifies all four source checksums before and after extraction. It also rereads each CSV to confirm a complete round trip. Running it again regenerates the same two CSVs; only the manifest's extraction timestamp changes when the inputs and code are unchanged.

Generated files remain local under the existing Git ignore rules. These exports have not been accepted into a reviewed graph, and no Neo4j import is performed by this script.

## Prepare diagnoses and relationships

After extraction, run:

```powershell
python src/extraction/prepare_jensen_graph_tables.py
```

This second script reads the pair CSV and checks it against the extraction manifest and original source checksums. It creates these additional local files under `data/extracted/`:

| File | Contents |
|---|---|
| `diagnoses.csv` | One node candidate per distinct diagnosis code in the pair table |
| `relationships.csv` | One directed evidence record per published pair row |
| `jensen_graph_tables_manifest.json` | Input/output hashes, record counts, validation results and field lists |

`diagnoses.csv` contains 681 distinct three-character ICD-10 categories, with the exact study-reported names. These are diagnosis categories, not necessarily 681 different diseases. Fields include a stable source-qualified `diagnosis_id`, `code`, `name`, `coding_system`, `code_level`, `coding_version`, study/workbook provenance, `source_rows_json` and `review_status`. The JSON field lists every original Excel row mentioning that code. The specific coding edition/national-version mapping has not been resolved and is marked `not_specified_in_table`; labels have not been replaced with modern terminology.

IDs take the form `S006:ICD10:E11`. Keeping the study ID in the identifier avoids automatically merging codes from different studies or coding editions before terminology review.

`relationships.csv` contains all 4,014 evidence records. `source_diagnosis_id` is the first diagnosis and `target_diagnosis_id` is the later diagnosis. Each link is labelled `TEMPORALLY_ASSOCIATED_WITH`. The stable relationship ID uses the study, table and source row, for example `S006:SD1:22`. Patient counts, relative risks, both relative-risk p-values, sample counts and direction p-values are copied without numerical conversion or aggregation. Original study, workbook, sheet and row provenance are retained.

Example from Excel row 22: `S006:ICD10:E11` to `S006:ICD10:N18`, with `n_patients=8515` and `relative_risk=2.442088`. Those statistics remain properties of this study-specific pair, not the diagnosis node or an individual patient's probability.

Names must agree for each code; conflicting names stop processing for manual review. Repeated source rows are rejected. Multiple distinct source rows describing the same directed pair would be retained as separate evidence, with the repetition count recorded in the manifest. Reverse-direction pairs are also distinct. Every relationship endpoint must resolve to a diagnosis record.

Both outputs remain `not_reviewed_for_graph`. No causal conclusions, trajectory-derived extra links or database import are introduced. The trajectory CSV remains unchanged for its separate processing step.

Run the focused checks from the project folder:

```powershell
python -m unittest discover -s tests -p "test_jensen_graph_tables.py" -v
```

## Preserve complete trajectories

After the first two scripts, run:

```powershell
python src/extraction/prepare_jensen_trajectories.py
```

This produces `data/extracted/trajectories.csv` and `data/extracted/jensen_trajectories_manifest.json`. The earlier `jensen_trajectories.csv` remains the unchanged first-stage export. The new table adds stable record and diagnosis references while preserving every original field. It contains 1,171 complete four-diagnosis sequences referencing 140 codes in the existing diagnosis table.

Each row retains the original `trajectory_id`, cluster, starting age, four ordered diagnosis codes and names, all reported counts and timings, and source ID, DOI, workbook, sheet and row. Added fields are:

- `trajectory_record_id`: a unique source-row identity such as `S006:SD2:6`. Original trajectory identifiers are not replaced.
- `diagnosis_1_id` through `diagnosis_4_id`: references to `diagnoses.csv` at each ordered position.
- `evidence_type`: `OBSERVED_DIAGNOSIS_TRAJECTORY`.
- `review_status`: `not_reviewed_for_graph`.

The source cluster string `None` is retained literally. The source's ambiguous final count field remains `count_final_reported`. Counts and timing retain their original precision; intervals, sums and probabilities are not calculated.

Before export, the script verifies the trajectory CSV and source workbook checksums, the diagnosis table checksum, complete source provenance, expected row count, ordered-code agreement with the original trajectory identifier, and matching diagnosis IDs/names for all four positions. All input checksums are checked again after processing. The manifest records these inputs, the output hash, validation results and cluster counts. Each source row remains a separate record, including any repeated sequence in different rows or clusters.

Full trajectories are not split into extra pair evidence. `relationships.csv` and `diagnoses.csv` are not changed. Both supplements retain the same study ID `S006`, so shared underlying observations are not treated as independent replication. No graph import or causal interpretation is performed.

Run all implemented extraction checks with:

```powershell
python -m unittest discover -s tests -v
```

## Review and database import

The source-to-extraction comparison, twenty-example assistant spot-check and first local Neo4j import are documented in [Local Neo4j graph](neo4j_setup.md). The source CSVs keep their original review flags; the graph separately records passed extraction review and pending clinical review. The preparation scripts above still perform no database writes.
