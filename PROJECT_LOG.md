# Project log

**Project:** Disease Pathway GraphRAG

**Last updated:** 9 November 2026

This log records completed work and confirmed project decisions. Entries are added as work is completed.

## 1 Project scope established

- Established scientific papers and their supporting materials as the starting sources for the knowledge base.
- Defined broad coverage of diseases, symptoms, biomarkers and contributing factors. Biological, genetic, environmental, behavioral, psychological and medical factors were included in the agreed scope when supported by evidence.
- Confirmed that stress and depression were illustrative examples rather than a required focus.
- Defined three exploration modes:
  - **Backward:** start from a disease and explore possible contributing factors and earlier conditions.
  - **Forward:** start from a disease or factor and explore reported subsequent conditions or outcomes.
  - **Both:** explore incoming and outgoing relationships around the selected concept.
- Agreed that a branching answer should explain each supported connection and provide its scientific source.
- Distinguished associations, temporal sequences, risk factors and supported causal findings. Graph connectivity alone was not accepted as evidence of causation in an individual patient.

## 2 Original papers reviewed

Reviewed the five PDFs initially supplied for the project:

| Source ID | Paper |
|---|---|
| S001 | Disease Trajectories from Healthcare Data: Methodologies, Key Results, and Future Perspectives |
| S002 | Trajectories network analysis of chronic diseases among middle-aged and older adults: evidence from CHARLS |
| S003 | Analysing disease trajectories in a cohort of 71,849 Patients: A visual analytics and statistical approach |
| S004 | Temporal trajectories of important diseases in the life course and premature mortality in the UK Biobank |
| S005 | Visualising disease trajectories from population-wide data |

Identified their contributions to trajectory methods, cohort analysis, diagnosis normalization, temporal relationships, visualization and interpretation of findings. Distinguished the disease counts reported for study datasets from the number of evidence records actually available for extraction.

## 3 Requirements specification and architecture documented

- Created an English Project Requirements Specification and revised it as the scope became clearer:
  - **Version 0.1, dated 2 November 2026:** initial project specification.
  - **Version 0.2, dated 4 November 2026:** scientific papers, knowledge base and disease trajectory architecture.
  - **Version 0.3, dated 8 November 2026:** broad disease coverage, backward and forward exploration, current corpus, evidence requirements, evaluation and development milestones.
- Saved the current specification at `docs/Project_Specification_v0_3_EN.docx`.
- Added a horizontal architecture diagram to Version 0.3.
- Documented Neo4j as the intended graph store and GraphRAG as the proposed approach for retrieving graph context and source passages for cited explanations.
- Recorded the proposed Python-based processing and lightweight interface approach, with implementation choices still subject to supervisor review.
- Documented the current scope in `docs/project_scope.md`.

## 4 PubMed exploration completed

- Used references from the original papers and targeted searches to select 12 additional PubMed-indexed papers.
- Checked identifiers and bibliographic metadata against NCBI PubMed records.
- Recorded each paper's connection to the original corpus, intended contribution and screening status.
- Created a reading shortlist, reference-manager citations and metadata records.
- Selected papers covering broad trajectory networks, age-dependent branching, cardiometabolic patterns, cancer, biomarkers, COPD, fatty liver disease, stroke and dementia, obesity, and cardiovascular intervention evidence.

The reading shortlist is saved at `docs/PubMed_Expansion_Shortlist.md`; the reference-manager file is `docs/PubMed_Expansion_References.ris`.

## 5 Additional PDFs downloaded and checked

- Downloaded 10 of the 12 shortlisted papers from publishers and publicly accessible repositories.
- Checked that the downloaded files were readable PDFs and matched the expected article title or DOI.
- Recorded download sources, page counts and file checksums.
- Organized the local corpus as 15 available PDFs: the five original papers and ten additional downloads.
- Recorded two shortlisted papers as pending full-text access:
  - [Hu et al., Precancer disease routes, PMID 30591553](https://pubmed.ncbi.nlm.nih.gov/30591553/).
  - [Yang et al., Dementia after stroke and transient ischemic attack, PMID 24603162](https://pubmed.ncbi.nlm.nih.gov/24603162/).

## 6 Jensen supplementary tables obtained

Followed the original papers' references to [Jensen et al., 2014, PMID 24959948](https://pubmed.ncbi.nlm.nih.gov/24959948/), then downloaded its supplementary files through Europe PMC. These tables were obtained during the literature expansion; they were not separate attachments in the five original PDFs.

| Material | Records | Content |
|---|---|---|
| Supplementary Data 1 | 4,014 | Directional diagnosis pairs with codes, names, patient counts, relative risks and significance statistics |
| Supplementary Data 2 | 1,171 | Four-diagnosis trajectories with patient counts and timing information |

- Inspected the workbook structure and verified the record counts after the source header section. The first data record is at Excel row 6 in each workbook.
- Preserved the original publisher filenames, `ncomms5022-s2.zip` and `ncomms5022-s3.zip`.
- Confirmed that these ZIP containers use the Excel workbook format.
- Created byte-identical `.xlsx` copies, preserving both originals:
  - `ressources/supplements/ncomms5022-s2.xlsx`
  - `ressources/supplements/ncomms5022-s3.xlsx`
- Selected these structured tables as the starting material for the first graph-building milestone.

## 7 Local project folder prepared

Created the Desktop project folder named **PFA Disease Knowledge Graph** and organized its materials. The existing, separately populated Desktop folder named **PFA** was left unchanged.

- Created folders for source materials, extracted data, reviewed evidence, extraction code, graph code, retrieval code, the interface, tests and documentation.
- Copied research materials without changing their original contents and verified file checksums.
- Created a source register with stable IDs and availability states for 17 papers.
- Added project documentation and a starter README.
- Organized papers under `ressources/` and supplementary tables under `ressources/supplements/`.
- Preserved earlier local copies under `data/papers/` and `data/supplements/`.

## 8 Git repository initialized and first version published

Repository: [YoussefElGharbaouiDevs/disease-pathway-graphrag](https://github.com/YoussefElGharbaouiDevs/disease-pathway-graphrag).

- Initialized Git in the local project folder and connected the `origin` remote.
- Added `.gitignore` and `.gitattributes` files.
- Added a repository README, source register, attribution document, research references, current requirements specification and starter folders.
- Committed and pushed the initial version to `main`.
- Initial commit: [`7af3362`](https://github.com/YoussefElGharbaouiDevs/disease-pathway-graphrag/commit/7af3362), **Set up project structure and scientific ressources**, dated 9 November 2026.
- Verified the remote contents: 33 files, including 14 PDFs and two original supplementary workbooks.
- Included publication attribution and license notices. The personal-use-only NEJM canakinumab PDF was retained locally and represented by a source link in the public repository.
- Kept local duplicate materials, generated-data locations and the restricted PDF outside version control.

The `.xlsx` convenience copies and this project log were created locally after the initial push and have not been committed or pushed as of this entry.

## 9 Jensen workbooks exported without changing the sources

Completed on **9 November 2026**:

- Added `src/extraction/extract_jensen.py`, a reusable Python 3.10+ script using only the standard library.
- Read the two `.xlsx` copies without modifying them or the original publisher `.zip` workbooks. Verified byte identity between each original and its `.xlsx` copy, and verified all four source SHA-256 checksums before and after extraction.
- Generated local files under `data/extracted/`:
  - `jensen_diagnosis_pairs.csv`: all **4,014** pair records.
  - `jensen_trajectories.csv`: all **1,171** trajectory records.
  - `jensen_extraction_manifest.json`: extraction timestamp, source/output checksums, original headers, column mappings and record counts.
- Flattened the stacked headers into descriptive CSV field names and cleaned whitespace. Preserved diagnosis codes, labels, source numeric precision, zero values, scientific notation and less-than p-value bounds. No records were filtered, deduplicated or merged.
- Attached the source ID `S006`, DOI, workbook path, sheet name and original Excel row number to every exported record.
- Preserved the ambiguous trajectory column P label (`1->...->3`, positioned after diagnosis 4) in the manifest and exported its values as `count_final_reported`, without silently correcting the source.
- Added `docs/jensen_extraction.md` with rerun instructions, field explanations, integrity checks and extraction limits. Updated the repository README to reflect the implemented extraction step.
- Checked required values, expected headers, numeric validity and exact row counts. Verified CSV read-back against the prepared records.
- Independently reconciled all **60,047 source data cells** against the exported fields using a separate read-only Excel parser (`openpyxl`). Verified provenance fields for every record.
- Ran the script again and confirmed that both CSVs were byte-identical between runs. Verified that invalid values and a changed source copy were rejected; the changed-copy check used temporary files rather than modifying the project sources.

The generated files remain local under the existing Git ignore rules. This extraction work, the `.xlsx` convenience copies and the project log have not been committed or pushed as of this entry.

## 10 Diagnosis and relationship tables prepared

Completed on **9 November 2026**:

- Added `src/extraction/prepare_jensen_graph_tables.py`, a standard-library Python script that reads the verified pair CSV and checks it against the first extraction manifest and source workbook checksums.
- Generated `data/extracted/diagnoses.csv` with **681 distinct diagnosis-code records**, including the study-reported name, ICD-10 coding system, three-character category level, source-qualified ID, source references and every original row mentioning the code. These are diagnosis categories, not necessarily 681 separate diseases.
- Used source-qualified IDs such as `S006:ICD10:E11` to avoid implicitly merging different studies or coding editions. Marked the exact coding version as `not_specified_in_table`; no current terminology mapping was claimed.
- Generated `data/extracted/relationships.csv` with all **4,014** directed pair-evidence records. Labelled each relationship `TEMPORALLY_ASSOCIATED_WITH` and retained patient counts, relative risk, significance statistics and complete workbook/row provenance without recalculation or aggregation.
- Assigned stable relationship IDs from the study, table and original row, such as `S006:SD1:22`.
- Generated `data/extracted/jensen_graph_tables_manifest.json` with input/output checksums, field lists, counts, validation results and interpretation limits.
- Confirmed there were no conflicting names for a code, no repeated directed pairs and no missing diagnosis endpoints in the actual pair table.
- Independently reconciled every relationship's statistics and source references against the input CSV, all diagnosis names against their original pair endpoints, and every diagnosis's source-row list against all its occurrences.
- Verified that both original workbook pairs, the extracted pair CSV, the trajectory CSV and the first extraction manifest remained unchanged.
- Added five focused tests covering reverse and repeated pair evidence, conflicting names, repeated source rows, unexpected code formats, source preservation, repeatable outputs and rejection of a modified input CSV. All five passed. Output writes and modified-input checks in the tests used temporary project copies.
- Updated `docs/jensen_extraction.md` with the new schemas, example, rerun instructions and test command, and updated the README to describe the completed step.

All diagnosis and relationship records remain `not_reviewed_for_graph`. The trajectory table was not converted into extra pair evidence. The new generated tables remain local under the existing Git ignore rules; no commit or push was performed for this step.

## 11 Complete trajectories preserved separately

Completed on **9 November 2026**:

- Added `src/extraction/prepare_jensen_trajectories.py`, a standard-library Python script that prepares complete sequences from the verified second-workbook export and references the existing diagnosis table.
- Generated `data/extracted/trajectories.csv` with all **1,171 four-diagnosis sequences**, preserving every original field: sequence identifier, cluster, starting age, ordered diagnosis codes/names, reported counts/timing, study ID, DOI, workbook, sheet and Excel row.
- Added stable source-row record IDs such as `S006:SD2:6`, four ordered diagnosis references, the evidence type `OBSERVED_DIAGNOSIS_TRAJECTORY` and review status `not_reviewed_for_graph`. Kept the original trajectory identifiers unchanged.
- Confirmed that all **140 diagnosis codes** appearing in the trajectories resolve to the existing diagnosis table, with matching names at all **4,684 diagnosis positions**.
- Preserved the literal cluster label `None`, source numeric precision and the neutral `count_final_reported` field for the ambiguous final source count column. Did not calculate new intervals, aggregate counts or infer probabilities.
- Generated `data/extracted/jensen_trajectories_manifest.json` with input/output checksums, field names, validation results, cluster counts and evidence limits.
- Independently compared all **25,762 original CSV field values** against the prepared trajectory records and verified every ordered diagnosis reference and source-row identity.
- Verified that the source workbooks, earlier extracted CSVs, diagnosis and relationship tables, and earlier manifests were unchanged. Kept the initial `jensen_trajectories.csv` export alongside the prepared `trajectories.csv` table.
- Added five trajectory tests covering complete-path and value retention, repeated sequences in distinct rows, source-row uniqueness, ordered identifiers, missing diagnosis references, conflicting labels, repeatable outputs and rejection of a modified trajectory CSV. All **10 implemented tests** passed, including the five existing pair-table tests. Tests used temporary copies for generated outputs and modified-input checks.
- Updated the extraction documentation and README to describe the completed trajectory step and its rerun command.

Trajectories remain separate from pairwise relationship evidence. Both tables retain study ID `S006`; no independent confirmation or additional pair evidence was counted from the trajectories. No database import, commit or push was performed. Generated files remain local under the existing Git ignore rules.

## 12 Extraction checked and first Neo4j graph imported

Completed on **9 November 2026**:

- Added `src/graph/review_jensen.py` and pinned its independent reader, `openpyxl==3.1.5`, in `requirements.txt`. Recompared all **60,047 original workbook data cells** with the exports and reconciled every prepared diagnosis, directed association and full trajectory.
- Prepared and inspected **20 side-by-side source/export examples**: ten diagnosis pairs spread across the first workbook and ten full trajectories spanning all six source cluster labels. Checked names, codes, direction/order, counts, relative risks, significance values and timing. All matched. Display differences in floating-point precision were distinguished from value changes.
- Recorded the comparison sheet, validation results and a clearly attributed **Codex assistant extraction spot-check**, including matching input hashes, under `data/reviewed/`. This was not human supervisor approval or clinical validation. Preserved the unresolved source column-P label under `count_final_reported`.
- Located the existing Java 21 runtime and downloaded **Neo4j Community 5.26.33** from its official distribution. Verified the archive against the publisher's SHA-256 checksum and extracted it under the project's ignored `.local/` folder.
- Configured project-local database storage, local-only HTTP/Bolt connectors, bounded memory and a generated password in the ignored `.env` file. No system-wide Neo4j installation or Windows service was created.
- Added a local setup/start/status helper, isolated local HTTP client, reviewed-data import gate, full import/read-back verification, bounded exploration CLI and five Browser example queries under `src/graph/`.
- Imported **681 Diagnosis nodes**, **4,014 TEMPORALLY_ASSOCIATED_WITH relationships**, **1,171 Trajectory nodes** and **one Study node**. Added **4,684 ordered trajectory-position connections** and **1,852 study-reference connections**. The complete local graph contains **1,853 nodes and 10,550 relationships**; structural links are not additional disease associations.
- Retained original CSV records exactly in `source_record_json`, original statistics/provenance, typed numeric values for queries, ordered trajectory positions and explicit extraction/clinical review states. Did not add trajectory counts to pair counts or claim independent evidence from the same study.
- Read back and verified every imported record property, all association directions, all four positions in every trajectory and study references. Saved the local import report.
- Repeated the import using stable IDs, uniqueness constraints and `MERGE`. Verified **zero additional nodes and zero additional relationships** were created.
- Tested backward and forward exploration around `N18`, recovered the known `E11 -> N18` pair with its original statistics, and retrieved `E11 -> A46 -> L97 -> E86` in its original four-position order. Saved the search examples locally. Confirmed all five Browser queries executed successfully.
- Added three import tests for exact numeric evidence retention, rejection of changed reviewed inputs and detection of Cypher errors inside HTTP-success responses. All **13 implemented tests** passed. Also verified the running database version and that Neo4j Browser returned HTTP 200.
- Added `docs/neo4j_setup.md`, `.env.example` and access/rerun/search instructions; updated the README and extraction documentation. Verified that credentials, runtime files and generated review reports are Git-ignored.

Neo4j Browser was available at `http://127.0.0.1:7474/browser/` at completion. Login credentials remain in the local `.env` and were not published. This step changed no source workbooks or extracted CSVs. No commit or push was performed.

## 13 Readable relationship captions added

Completed on **9 November 2026**:

- Adopted the user-facing caption **Associated with a later diagnosis of** for observed temporal associations.
- Added the caption as `display_label` on all **4,014** existing association relationships and in the importer so that it persists on future imports. Preserved the technical relationship type `TEMPORALLY_ASSOCIATED_WITH`, stable IDs, directions and source statistics.
- Read back and verified the full graph after the update; record properties, counts, trajectory positions and study references still matched the source tables.
- Set the open Neo4j Browser's relationship caption to `display_label` and visually verified the readable arrow text in the backward-search example.
- Added the reusable Browser style rule at `src/graph/browser_style.grass` and documented the display property and Browser configuration in `docs/neo4j_setup.md`.
- Reran the three focused import checks after the caption change; all passed.

The change affects wording and display metadata. Source CSVs, source workbooks and the evidence interpretation remain unchanged. No application was created and no commit or push was performed.

## 14 Guided Neo4j Browser walkthrough completed

Completed on **9 November 2026**:

- Opened the local Neo4j Browser and confirmed the user's successful connection to the project database.
- Displayed the single `E11 -> N18` relationship as a two-diagnosis example and explained diagnosis circles and the direction of the observed association.
- Demonstrated a forward search from `E11`, limited to five outgoing connections, and a backward search around `N18`, limited to five incoming connections. Connected the backward view to the project's `FINAL` search concept.
- Demonstrated selecting a diagnosis and reading its code, full name and source information in the details panel.
- Used fullscreen, graph fitting and the details-panel toggle to keep the examples readable. Left the guided graph tab open for the user.
- Clarified the difference between Neo4j's database workbench and the planned project interface, and between an observed temporal association and an established individual cause.
- Saved screenshots of the guided backward view and the updated readable relationship captions in the chat workspace's `outputs/neo4j_walkthrough/` folder.

The walkthrough used read-only graph queries. It did not add or remove evidence records.

## 15 Current completed-work status

The project now has a running local Neo4j research graph with checked source-to-extraction accuracy, preserved pair and full-trajectory evidence, complete source references, repeatable import, bounded backward/forward exploration and readable association captions. A guided Browser walkthrough has been completed. Clinical review remains pending; observed temporal paths are not established individual causes. A project application and GraphRAG explanation service have not yet been implemented.
