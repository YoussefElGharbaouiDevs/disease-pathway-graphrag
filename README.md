# Disease Pathway GraphRAG

An academic PFA project for exploring disease relationships through a scientific knowledge graph and evidence-grounded explanations.

Users will search for a disease, condition or factor and explore its connections:

- **Backward**: possible contributors, risk factors and earlier conditions.
- **Forward**: reported subsequent conditions, complications and outcomes.
- **Both**: the incoming and outgoing network around the selected concept.

Every displayed connection should retain its supporting publication and evidence location. Associations, temporal sequences and reviewed causal findings are represented distinctly.

## Project structure

```text
ressources/          Scientific papers, attribution and source register
  supplements/       Original published relationship tables
data/
  extracted/         Jensen CSVs, candidate graph tables and manifests (local)
  reviewed/          Extraction review and Neo4j verification reports (local)
src/
  extraction/        Jensen extraction, graph-table and full-trajectory scripts
  graph/             Source review, local Neo4j setup, import and bounded searches
  retrieval/         Future graph and passage retrieval
app/                 Future demonstration interface
tests/               Evidence-preservation and input-integrity checks
docs/                Project requirements, scope and reading list
```

## Research corpus

The source register contains 17 papers: five original project references and twelve PubMed additions. This public repository includes 14 open-licensed PDFs, one additional source as a link, and two papers awaiting full-text access. See [ressources](ressources/README.md) and [attribution](ressources/ATTRIBUTION.md).

Two Jensen supplementary workbooks provide 4,014 published directional diagnosis pairs and 1,171 four-diagnosis trajectories. They have been checked against the sources and imported into the local prototype graph. Extraction accuracy has been reviewed; clinical and causal interpretations remain unreviewed.

## Prototype progress

1. Defined study-specific diagnosis, pair-evidence and full-trajectory records.
2. Checked source values, inspected twenty examples and recorded assistant extraction review.
3. Imported the dataset and source references into a local Neo4j instance.
4. Tested bounded backward, forward and combined searches.
5. Supporting-passage retrieval and cited GraphRAG explanations remain to be implemented.

## Documentation

- [Current scope](docs/project_scope.md)
- [Project Requirements Specification v0.3](docs/Project_Specification_v0_3_EN.docx)
- [PubMed reading shortlist](docs/PubMed_Expansion_Shortlist.md)
- [Reference manager citations](docs/PubMed_Expansion_References.ris)
- [Jensen extraction and rerun instructions](docs/jensen_extraction.md)
- [Local Neo4j setup, review and search instructions](docs/neo4j_setup.md)
- [Completed project work](PROJECT_LOG.md)

## Development status

The local prototype graph is running in Neo4j Community 5.26.33 with 681 diagnosis nodes, 4,014 temporal associations and 1,171 complete trajectories. Source-to-extraction checks and a twenty-example assistant spot-check passed. Full database read-back, repeat-import checks and bounded backward/forward searches passed. Trajectories remain separate from pair evidence, and original statistics and references are preserved. Clinical review, an application and GraphRAG explanations have not yet been implemented. See the Neo4j instructions above for access and commands. Credentials, runtime files and generated data remain outside version control.
