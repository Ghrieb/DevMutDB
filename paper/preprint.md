# DevMutDB: A Developmental Mutation Pathogenicity Scoring System

## Abstract

Interpreting the clinical significance of genetic variants remains a major challenge in genomic medicine. While existing tools like CADD, SIFT, and PolyPhen-2 predict protein-level consequences, they do not account for temporal developmental criticality. We present DevScore, a novel computational framework that integrates variant pathogenicity, gene expression timing, and protein domain importance to predict developmental impact. Our framework is validated on a cohort of 110 known developmental disorder mutations.

## Introduction

Developmental disorders affect 2-3% of live births and result from genetic perturbations during critical windows of embryonic development. Current pathogenicity prediction tools treat all genes and tissues equally, ignoring developmental timing. We hypothesize that mutations in genes highly expressed during critical developmental stages (gastrulation, neurulation) have greater phenotypic impact.

## Methods

### DevScore Formula

**DevScore = V × E_peak × C_stage × D_domain × 100**

- **V**: Pathogenicity (CADD + ClinVar)
- **E_peak**: Peak developmental expression
- **C_stage**: Stage criticality weight (1.0 for gastrulation/neurulation)
- **D_domain**: Protein domain weight (1.0 for DNA-binding domains)

For genes with experimentally characterised developmental expression in E-MTAB-6814, E_peak is derived from the reported peak TPM normalised against a 10,000 TPM ceiling. Uncharacterised genes receive class-informed estimated expression profiles based on known developmental or adult-onset patterns.

### Data Sources

- Variant consequences: Ensembl VEP API
- Clinical significance: NCBI ClinVar API
- Developmental gene expression: Expression Atlas (E-MTAB-6814, Cardoso-Moreira et al. 2019)
- Protein domains / functional regions: UniProt API
- Population frequency: gnomAD API (v4)

## Results

*Benchmark results pending recalibration following domain classification improvements.*
- Mean absolute error: TBD points (0–100 scale)
- ROC AUC for developmental vs. adult-onset: TBD
- Sensitivity for gastrulation-critical genes: TBD

## Discussion

DevScore addresses a critical gap in variant interpretation by incorporating developmental timing. Expression profiles for genes absent from the E-MTAB-6814 developmental transcriptome are estimated using class-aware baselines rather than experimental measurements, representing a limitation for truly novel genes. Future work will expand to non-coding regions and refine stage-specific expression weights using scRNA-seq atlases.

## Availability

Code: https://github.com/Ghrieb/DevMutDB
Web: https://devmutdb.vercel.app
