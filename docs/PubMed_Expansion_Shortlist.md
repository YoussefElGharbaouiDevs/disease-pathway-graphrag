# PubMed expansion shortlist for the PFA project

Screening date: 8 November 2026. Twelve additional PubMed-indexed papers, selected using references from the five supplied PDFs and targeted searches for connected factor and disease evidence. This is a first targeted screening pass, not a systematic review or a validated knowledge base.

The first extraction priorities are Jensen 2014, the trajectory browser, the biomarker study, the COPD study and the MAFLD study. Priority labels are project recommendations. They do not grade clinical evidence strength.

## Main discovery for database construction

The original Jensen paper provides downloadable aggregate relationship tables. The retrieved supplementary files have four header rows followed by 4,014 diagnosis-pair records and 1,171 trajectory records, respectively. The pairs include source and target codes and names, patient counts, relative risks and significance statistics. This offers a practical seed for a graph; the records still require interpretation and validation. They are not individual patient histories. [Source paper](https://pubmed.ncbi.nlm.nih.gov/24959948/) and [full text with supplement descriptions](https://pmc.ncbi.nlm.nih.gov/articles/PMC4090719/).

The research pack preserves the publisher filenames ncomms5022-s2.zip and ncomms5022-s3.zip. Although their extension is ZIP, their contents use the Excel workbook format. They can be opened as copies with the .xlsx extension. Original bytes have not been changed. Supplementary files were obtained from the [Europe PMC supplementary-files service](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4090719/supplementaryFiles).

## Selected papers

| Priority | Paper | Intended contribution | Free PMC link in PubMed record |
|---|---|---|---|
| 1 | [Jensen AB et al., 2014](https://pubmed.ncbi.nlm.nih.gov/24959948/) | Graph foundation | Yes |
| 1 | [Siggaard T et al., 2020](https://pubmed.ncbi.nlm.nih.gov/33009368/) | Graph exploration and export | Yes |
| 2 | [Dervić E et al., 2024](https://pubmed.ncbi.nlm.nih.gov/38454004/) | Age-dependent branching | Yes |
| 2 | [Haug N et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32151252/) | Cardiometabolic combinations | Yes |
| 2 | [Hu JX et al., 2019](https://pubmed.ncbi.nlm.nih.gov/30591553/) | Backward cancer pathways | No |
| 1 | [Yang H et al., 2022](https://pubmed.ncbi.nlm.nih.gov/35578620/) | Biomarker to disease links | Yes |
| 1 | [Hagmann M et al., 2023](https://pubmed.ncbi.nlm.nih.gov/37418429/) | Backward respiratory pathways | Yes |
| 1 | [Jia Y et al., 2023](https://pubmed.ncbi.nlm.nih.gov/37864216/) | Forward multisystem pathways | Yes |
| 2 | [Yang J et al., 2015](https://pubmed.ncbi.nlm.nih.gov/24603162/) | Stroke to dementia context | No |
| 2 | [Kivimäki M et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28626830/) | Modifiable factor evidence | Yes |
| 3 | [Ridker PM et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28845751/) | Experimental pathway evidence | No |
| 3 | [Blood Pressure Lowering Treatment Trialists' Collaboration et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33933205/) | Intervention outcome evidence | Yes |

### 1 Temporal disease trajectories condensed from population-wide registry data covering 6.2 million patients

Jensen AB et al. Nature communications. 2014. PMID 24959948. DOI 10.1038/ncomms5022.

- **Connection to the base corpus:** Annual Review [16]; also cited in the Spanish, UK Biobank, and Frontiers papers.
- **What it adds:** Reports 4,014 directional diagnosis pairs and 1,171 four-diagnosis trajectories. Retrieved supplementary files contain codes, names and relationship statistics.
- **Proposed extraction:** Extract candidate temporal edges and their statistics. Keep associations distinct from causal claims.
- **Screening status:** PubMed abstract and relevant full-text sections screened; both supplementary workbooks retrieved and structurally checked.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24959948/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4090719/).

### 2 Disease trajectory browser for exploring temporal, population-wide disease progression patterns in 7.2 million Danish patients

Siggaard T et al. Nature communications. 2020. PMID 33009368. DOI 10.1038/s41467-020-18682-4.

- **Connection to the base corpus:** Annual Review [63]; cited in the Spanish, UK Biobank, CHARLS and Frontiers papers.
- **What it adds:** Describes disease-agnostic exploration of a 7.2-million-patient register and exports in formats including CSV and JSON.
- **Proposed extraction:** Use as a design and potential aggregate-data source. Current browser functionality and export access have not been tested.
- **Screening status:** PubMed abstract screened; PMC full-text link identified.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/33009368/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7532164/).

### 3 Unraveling cradle-to-grave disease trajectories from multilayer comorbidity networks

Dervić E et al. NPJ digital medicine. 2024. PMID 38454004. DOI 10.1038/s41746-024-01015-w.

- **Connection to the base corpus:** Annual Review [60].
- **What it adds:** Reports 1,260 trajectories and 70 pairs of diverging trajectories in Austrian inpatient data, with age groups represented as layers.
- **Proposed extraction:** Preserve age and sex context in graph paths. The underlying individual patient data are restricted.
- **Screening status:** PubMed abstract and relevant full-text methods, results and availability sections screened.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/38454004/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10920888/).

### 4 High-risk multimorbidity patterns on the road to cardiovascular mortality

Haug N et al. BMC medicine. 2020. PMID 32151252. DOI 10.1186/s12916-020-1508-1.

- **Connection to the base corpus:** Annual Review [52].
- **What it adds:** Identifies 132 multimorbidity patterns and their transitions in Austrian hospital records.
- **Proposed extraction:** Represent joint disease patterns and subgroup-specific transitions; 132 is a pattern count, not a disease count.
- **Screening status:** PubMed abstract screened; PMC full-text link identified.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/32151252/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7063814/).

### 5 A Large-Cohort, Longitudinal Study Determines Precancer Disease Routes across Different Cancer Types

Hu JX et al. Cancer research. 2019. PMID 30591553. DOI 10.1158/0008-5472.CAN-18-1677.

- **Connection to the base corpus:** Discussed in the supplied Annual Review and Frontiers visualization paper.
- **What it adds:** Examines 17 cancer types and reports 168 ordered trajectories for seven cancer types.
- **Proposed extraction:** Add upstream diagnoses for cancer queries. Treat them as precancer associations rather than established explanations of individual cancer causation.
- **Screening status:** PubMed abstract screened; publisher full-text link identified; no PMC identifier in the PubMed record.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/30591553/); [Publisher](https://doi.org/10.1158/0008-5472.CAN-18-1677).

### 6 Biomarkers and Disease Trajectories Influencing Women's Health: Results from the UK Biobank Cohort

Yang H et al. Phenomics (Cham, Switzerland). 2022. PMID 35578620. DOI 10.1007/s43657-022-00054-1.

- **Connection to the base corpus:** Annual Review [38].
- **What it adds:** Examines 301 diseases and connects physical measurements and biomarkers with disease trajectories in women.
- **Proposed extraction:** Add factor and biomarker nodes alongside disease nodes, preserving the sex-specific study population.
- **Screening status:** PubMed abstract screened; PMC full-text link identified.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/35578620/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9096057/).

### 7 Gender-specific disease trajectories prior to the onset of COPD allow individualized screening and early intervention

Hagmann M et al. PloS one. 2023. PMID 37418429. DOI 10.1371/journal.pone.0288237.

- **Connection to the base corpus:** Annual Review [56].
- **What it adds:** Reports 62 diagnoses over-represented before COPD diagnosis, with sex-specific analyses and independent-cohort validation.
- **Proposed extraction:** Supply a concrete backward-search example around COPD. Preceding diagnoses are not automatically causes.
- **Screening status:** PubMed abstract and relevant full-text results and validation sections screened.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/37418429/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10328310/).

### 8 Multi-system diseases and death trajectory of metabolic dysfunction-associated fatty liver disease: findings from the UK Biobank

Jia Y et al. BMC medicine. 2023. PMID 37864216. DOI 10.1186/s12916-023-03080-6.

- **Connection to the base corpus:** Annual Review [62].
- **What it adds:** Examines 490 conditions and reports higher risks for 113 conditions among people meeting the study definition of MAFLD.
- **Proposed extraction:** Connect a liver/metabolic starting condition to multisystem outcomes. Review supplementary Tables S1 and S2 for associations and temporal pairs; preserve the original MAFLD definition.
- **Screening status:** PubMed abstract and relevant full-text supplement descriptions screened; tables located but not yet downloaded or curated.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/37864216/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10590000/).

### 9 Risk factors for incident dementia after stroke and transient ischemic attack

Yang J et al. Alzheimer's & dementia : the journal of the Alzheimer's Association. 2015. PMID 24603162. DOI 10.1016/j.jalz.2014.01.003.

- **Connection to the base corpus:** Spanish trajectory paper [23].
- **What it adds:** Investigates clinical and imaging features associated with incident dementia after stroke or transient ischemic attack.
- **Proposed extraction:** Add context for a stroke-to-dementia branch, including age, diabetes history and brain imaging findings. Keep these as study associations.
- **Screening status:** PubMed abstract screened through the NCBI record; publisher full text remains to be obtained.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/24603162/); [Publisher](https://doi.org/10.1016/j.jalz.2014.01.003).

### 10 Overweight, obesity, and risk of cardiometabolic multimorbidity: pooled analysis of individual-level data for 120 813 adults from 16 cohort studies from the USA and Europe

Kivimäki M et al. The Lancet. Public health. 2017. PMID 28626830. DOI 10.1016/S2468-2667(17)30074-9.

- **Connection to the base corpus:** Expansion of the cardiometabolic branch identified in the base papers.
- **What it adds:** Pools 120,813 adults from 16 cohorts to study BMI and later combinations of diabetes, coronary heart disease and stroke.
- **Proposed extraction:** Add BMI or obesity exposure records and links to defined cardiometabolic outcomes. Preserve the observational design.
- **Screening status:** PubMed abstract screened; PMC full-text link identified.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28626830/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5463032/).

### 11 Antiinflammatory Therapy with Canakinumab for Atherosclerotic Disease

Ridker PM et al. The New England journal of medicine. 2017. PMID 28845751. DOI 10.1056/NEJMoa1707914.

- **Connection to the base corpus:** Targeted expansion of cardiovascular and inflammatory explanations.
- **What it adds:** Randomized canakinumab trial in 10,061 people with previous myocardial infarction and elevated inflammatory markers.
- **Proposed extraction:** Add carefully scoped experimental evidence for an inflammatory intervention pathway. It is neither a general treatment recommendation nor a universal cause-of-disease claim.
- **Screening status:** PubMed abstract screened; publisher full-text link identified; no PMC identifier in the PubMed record.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/28845751/); [Publisher](https://doi.org/10.1056/NEJMoa1707914).

### 12 Pharmacological blood pressure lowering for primary and secondary prevention of cardiovascular disease across different levels of blood pressure: an individual participant-level data meta-analysis

Blood Pressure Lowering Treatment Trialists' Collaboration et al. Lancet (London, England). 2021. PMID 33933205. DOI 10.1016/S0140-6736(21)00590-0.

- **Connection to the base corpus:** UK Biobank premature mortality paper [35].
- **What it adds:** Individual-participant meta-analysis of 48 randomized trials covering 344,716 participants and cardiovascular outcomes.
- **Proposed extraction:** Distinguish intervention-to-outcome evidence from observational disease transitions. Preserve trial populations and composite outcome definitions.
- **Screening status:** PubMed abstract screened; PMC full-text link identified.
- **Links:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/33933205/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8102467/).

## Proposed extraction sequence

1. Interpret the Jensen supplementary headers and coding level, then map source and target diagnoses to normalized nodes. Retain the source PMID and table identifiers on every edge.
2. Verify a small sample against the paper before importing the complete relationship table. Store temporality and statistical association separately from any causal interpretation.
3. Add biomarker, COPD and MAFLD evidence to introduce factor nodes and richer incoming and outgoing branches. Inspect the supplementary tables rather than relying only on abstracts.
4. Use cancer, stroke and multimorbidity studies to extend the same connected regions. Account for overlapping cohorts and avoid treating repeated publications as independent evidence.
5. Add source-supported explanations and stronger experimental evidence where appropriate. A discussion mechanism is a hypothesis unless the cited supporting study establishes more.
6. Test backward, forward and combined queries. Every displayed edge must resolve to a study-specific evidence record; absence of evidence should remain visible.

## Queries to continue the exploration

Broad trajectory search:
```text
("disease trajectory"[Title/Abstract] OR "disease trajectories"[Title/Abstract]) AND (network*[Title/Abstract] OR longitudinal[Title/Abstract])
```

Fill a specific graph connection:
```text
("disease A"[Title/Abstract]) AND ("disease B"[Title/Abstract]) AND (cohort[Title/Abstract] OR longitudinal[Title/Abstract] OR mechanism*[Title/Abstract])
```

Replace the disease names with normalized terms and relevant synonyms. Expand searches with PubMed MeSH terms after inspecting relevant records. These are reusable next-search templates, not a claim that every matching paper has been screened.

## Files and provenance

- `PubMed_Expansion_Shortlist_2026-11-08.md`: this reading guide.
- `PubMed_Expansion_References.ris`: twelve bibliographic records for a reference manager.
- `PubMed_Expansion_Metadata.json`: identifiers, links and screening notes; no full abstracts.
- `ncomms5022-s2.zip`: original Jensen Supplementary Data 1.
- `ncomms5022-s3.zip`: original Jensen Supplementary Data 2.

Metadata were checked against the NCBI PubMed records. Nine records link to PMC full text; a PMC link does not mean the entire article has been reviewed. Review depth is stated for each paper. No new disease relationships have yet been accepted into a project database.
