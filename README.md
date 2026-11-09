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
  extracted/         Future extracted passages and table records
  reviewed/          Future validated evidence records
src/
  extraction/        Future source processing and extraction
  graph/             Future Neo4j import and graph traversal
  retrieval/         Future graph and passage retrieval
app/                 Future demonstration interface
tests/               Future tests and evaluation cases
docs/                Project requirements, scope and reading list
```

## Research corpus

The source register contains 17 papers: five original project references and twelve PubMed additions. This public repository includes 14 open-licensed PDFs, one additional source as a link, and two papers awaiting full-text access. See [ressources](ressources/README.md) and [attribution](ressources/ATTRIBUTION.md).

Two Jensen supplementary workbooks provide 4,014 published directional diagnosis pairs and 1,171 four-diagnosis trajectories. These are candidate research inputs; a project graph has not yet been imported or validated.

## First development milestone

1. Define the concept and study-specific evidence schema.
2. Manually verify a small sample from the Jensen tables.
3. Import verified relationships with source references into Neo4j.
4. Demonstrate bounded backward, forward and combined searches.
5. Retrieve supporting passages and add cited GraphRAG explanations.

## Documentation

- [Current scope](docs/project_scope.md)
- [Project Requirements Specification v0.3](docs/Project_Specification_v0_3_EN.docx)
- [PubMed reading shortlist](docs/PubMed_Expansion_Shortlist.md)
- [Reference manager citations](docs/PubMed_Expansion_References.ris)

## Development status

The repository currently contains source materials, documentation and an initial folder structure. The proposed stack is Python, Neo4j and a lightweight interface. Application code, database configuration and dependency installation will follow. Credentials and generated data belong outside version control.
