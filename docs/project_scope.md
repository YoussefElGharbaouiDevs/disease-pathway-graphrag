# Current project scope

## Objective

Build a scientific knowledge base linking diseases, symptoms, contributing factors, biomarkers and health outcomes. Use it to explore evidence-supported pathways and explain their connections with citations.

## Main workflows

- Backward: begin with a disease and retrieve possible contributing factors and earlier conditions.
- Forward: begin with a disease or factor and retrieve possible later conditions or outcomes.
- Both: show the selected concept within its incoming and outgoing network.

## Evidence requirements

Preserve each study-specific finding independently, including its population, relationship type, reported statistics, source passage or table, location and review status. A temporal predecessor is not automatically a cause. Generic associations should not acquire a temporal direction without evidence. Paths assembled across studies should be identifiable as composed paths.

Scientific explanations must be retrieved from supporting texts rather than invented from graph connectivity. The graph and evidence retrieval supply the context for later GraphRAG explanations.

## First prototype

A disease search with direction and depth controls, a visible graph and inspectable evidence behind each connection. Start from published aggregate relationships. Patient-specific probabilities and clinical deployment would require separate data and evaluation.

## Decisions still open

Final evidence schema, normalization rules, approved relation types, extraction review procedure, evaluation targets, model provider, implementation details and academic schedule.
