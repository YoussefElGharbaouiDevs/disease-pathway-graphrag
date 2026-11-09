// Run one query at a time in Neo4j Browser.

// Forward: observed subsequent diagnoses.
MATCH (d:Diagnosis {diagnosis_id: 'S006:ICD10:E11'})
      -[r:TEMPORALLY_ASSOCIATED_WITH]->(later:Diagnosis)
RETURN d, r, later LIMIT 25;

// Backward: observed preceding diagnoses, keeping the original arrow direction.
MATCH (earlier:Diagnosis)-[r:TEMPORALLY_ASSOCIATED_WITH]->
      (d:Diagnosis {diagnosis_id: 'S006:ICD10:N18'})
RETURN earlier, r, d LIMIT 25;

// A bounded graph path; not necessarily a same-patient observed trajectory.
MATCH p=(:Diagnosis {diagnosis_id: 'S006:ICD10:E11'})
         -[:TEMPORALLY_ASSOCIATED_WITH*1..2]->(:Diagnosis)
RETURN p LIMIT 20;

// A complete published trajectory, with its ordered diagnosis positions.
MATCH (t:Trajectory {trajectory_record_id: 'S006:SD2:6'})
      -[position:INCLUDES_DIAGNOSIS]->(d:Diagnosis)
RETURN t, position, d ORDER BY position.position;

// Show source values and the publication for one known pair.
MATCH (a:Diagnosis)-[r:TEMPORALLY_ASSOCIATED_WITH {relationship_id:'S006:SD1:22'}]->(b:Diagnosis)
MATCH (a)-[:REPORTED_IN]->(s:Study)
RETURN a.code, b.code, r.n_patients, r.relative_risk_reported,
       r.source_file, r.source_sheet, r.source_row, s.title, s.doi;
