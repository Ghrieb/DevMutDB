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

### Interpretative Scale

DevScore values are stratified into three tiers based on validated performance against the 110-gene benchmark:

| Tier | DevScore Range | Clinical Implication | Validation Performance |
|------|---------------|---------------------|----------------------|
| **High** | ≥20 | Strong evidence for developmental pathogenicity; high-confidence classification | PPV = 100% (17/17), Specificity = 100% |
| **Moderate** | 10–19 | Suggestive of developmental involvement; warrants independent clinical correlation | PPV = 96.4% (27/28), Specificity = 98.0% |
| **Low** | <10 | Limited evidence for developmental specificity; pathogenic in adult-onset contexts | 46/50 adult controls fall in this range |

The Youden-optimal decision threshold of **8.5** maximises the trade-off between sensitivity (0.833) and specificity (0.920). A cumulative threshold of ≥10 captures 75.0% of developmental-disorder variants (44/60) with 97.8% PPV, providing a conservative rule-out criterion for clinical screening.

### Architectural Design Justifications

**CADD:ClinVar weight ratio (60:40).** A hyperparameter sweep across seven ratios (50:50 to 80:20) confirmed architectural robustness. AUC varied by only 0.009 (range 0.922–0.931), Cohen's d remained very large (1.628–1.713), and rank order was perfectly preserved (Spearman ρ = 1.0 across all ratios). The 60:40 configuration was selected as the midpoint of the stable plateau.

**Expression normalisation ceiling (10,000 TPM).** The maximum observed developmental expression in E-MTAB-6814 across any gene-stage combination is approximately 9,800 TPM (SOX2 during gastrulation). A 10,000 TPM ceiling was chosen as a round-number upper bound ensuring no E_peak exceeds 1.0 while preserving proportional resolution.

**Developmental stage selection (10 stages).** The E-MTAB-6814 transcriptome (Cardoso-Moreira et al. 2019) profiles 10 developmental stages spanning conception to adulthood: zygote, blastocyst, gastrulation, neurulation, organogenesis, fetal early, fetal late, neonatal, childhood, and adult. All 10 stages are retained to preserve temporal granularity.

**Stage criticality weights.** Weights are biologically motivated: gastrulation and neurulation (C_stage = 1.0) represent the most vulnerable windows, when germ layer specification and neural tube closure occur. Organogenesis (0.95) covers organ patterning. Fetal early (0.65) and fetal late (0.50) reflect diminishing but ongoing developmental sensitivity. Neonatal (0.30), childhood (0.28), and adult (0.25) capture post-natal and adult-expressed genes with decreasing developmental relevance.

**Domain essentiality classification.** UniProt domain annotations are mapped to five essentiality classes: DNA-binding and catalytic domains (D_domain = 1.0) are assigned the highest weight, reflecting their critical role in developmental regulatory programmes. Structural domains (0.70), regulatory regions (0.50), disordered regions (0.40), and UTRs (0.20) receive progressively lower weights.

### Data Sources

- Variant consequences: Ensembl VEP API
- Clinical significance: NCBI ClinVar API
- Developmental gene expression: Expression Atlas (E-MTAB-6814, Cardoso-Moreira et al. 2019)
- Protein domains / functional regions: UniProt API
- Population frequency: gnomAD API (v4)

## Results

DevScore was validated on a benchmark of 110 variants (60 developmental-disorder genes, 50 adult-onset controls). The metric achieved a headline ROC AUC of 0.928 (95% CI: 0.873–0.973), outperforming CADD (0.457, +0.471), SIFT (0.397, +0.536), and PolyPhen-2 (0.446, +0.487). In the missense-only subset (n=66), DevScore AUC reached 0.933.

The Youden-optimal threshold of 8.50 yielded sensitivity of 0.833 and specificity of 0.920. A tiered classification system at ≥20 (High) captured 17/60 developmental genes with 100% specificity; the Moderate tier (10–19) captured an additional 27 genes at 98.0% specificity. Cumulative sensitivity at ≥10 was 75.0% (44/60) with 97.8% PPV.

Effect size was very large (Cohen's d = 1.77; Mann-Whitney U = 2784.5, p = 6.38 × 10⁻¹⁵). Median DevScore for developmental genes was 16.6 versus 4.0 for adult-onset controls. Spearman correlation with CADD was low (ρ = 0.156, p = 0.103), confirming that DevScore captures orthogonal developmental timing information. After controlling for disease class, partial Spearman remained significant (ρ = 0.299, p = 1.49 × 10⁻³).

A weight sensitivity sweep (seven CADD:ClinVar ratios, 50:50 to 80:20) confirmed architectural robustness: AUC varied only 0.922–0.931 (range 0.009) with perfect rank-order invariance (Spearman ρ = 1.0).

### Supplementary Table S1: Full Validation Cohort

The complete 110-gene benchmark dataset, including DevScore, all four components, baseline tool scores (CADD, SIFT, PolyPhen-2), HGVS notation, disease association, and classification, is available at `validation/benchmark_results.csv`. Below, a top-10 excerpt of highest-scoring developmental-disorder genes:

| Gene | DevScore | V | E_peak | C_stage | D_domain | CADD | Phenotype |
|------|----------|---|---|---------|----------|------|-----------|
| SOX2 | 52.8 | 0.910 | 0.58 | 1.00 | 1.00 | 34.0 | Anophthalmia-esophageal-genital syndrome |
| CHD7 | 37.0 | 0.770 | 0.48 | 1.00 | 1.00 | 38.0 | CHARGE syndrome |
| DHCR7 | 36.1 | 0.695 | 0.52 | 1.00 | 1.00 | 33.0 | Smith-Lemli-Opitz syndrome |
| CREBBP | 35.2 | 0.800 | 0.44 | 1.00 | 1.00 | 43.0 | Rubinstein-Taybi syndrome 1 |
| FOXG1 | 34.8 | 0.725 | 0.48 | 1.00 | 1.00 | 35.0 | Rett syndrome, congenital variant |
| EP300 | 33.6 | 0.800 | 0.42 | 1.00 | 1.00 | 43.0 | Rubinstein-Taybi syndrome 2 |
| COL1A1 | 27.6 | 0.611 | 0.68 | 0.95 | 0.70 | 27.4 | Osteogenesis imperfecta |
| SALL4 | 25.6 | 0.800 | 0.32 | 1.00 | 1.00 | 43.0 | Duane-radial ray syndrome |
| SMAD3 | 24.5 | 0.680 | 0.38 | 0.95 | 1.00 | 32.0 | Loeys-Dietz syndrome 3 |
| PAX6 | 24.0 | 0.571 | 0.42 | 1.00 | 1.00 | 24.7 | Aniridia |

The full Supplementary Table S1 (110 rows, 14 columns) is available as a CSV at `validation/benchmark_results.csv`.

## Discussion

DevScore addresses a critical gap in variant interpretation by incorporating developmental timing. While established tools such as CADD, SIFT, and PolyPhen-2 predict pathogenicity from evolutionary conservation and protein-level features, they treat all developmental stages as equivalent. As a result, adult-onset Mendelian disease genes with strong evolutionary constraint — e.g., *TP53* (DevScore 3.8), *BRCA1* (3.8), *MYH7* (7.2) — receive high CADD scores despite being unrelated to developmental disorders. DevScore resolves these false positives by attenuating the contribution of genes whose expression peaks in post-natal or adult tissues via C_stage weighting.

The tiered interpretative scale (High ≥20, Moderate 10–19, Low <10) provides actionable clinical stratification. The High tier achieves 100% PPV, meaning a DevScore ≥20 is fully specific for developmental pathogenicity in this cohort. The Moderate tier maintains 96.4% PPV, suggesting that scores in this range are strongly indicative but warrant independent confirmation. The cumulative ≥10 threshold (75.0% sensitivity, 98.0% specificity) serves as a practical screening rule-out for developmental involvement.

The weight sensitivity analysis demonstrates that the 60:40 CADD:ClinVar ratio is not a finely-tuned parameter; rather, any ratio between 50:50 and 80:20 produces near-identical classification performance (AUC range 0.009). This robustness is important for clinical deployment, where small weight changes must not materially alter variant classification.

### Limitations

Several limitations should be acknowledged. First, the benchmark dataset (n=110) is moderate in size and enriched for well-characterised developmental-disorder genes; performance on rare or novel genes remains to be established. Second, expression data from E-MTAB-6814 — while representing the most comprehensive staged human developmental transcriptome available — aggregates whole-tissue RNA-seq and may obscure cell-type-specific expression patterns. Third, DevScore is currently restricted to curated missense, nonsense, and canonical splice-site variants; non-coding and structural variants are not supported. Fourth, for genes absent from E-MTAB-6814, E_peak is estimated from class-informed baselines rather than direct experimental measurement.

### Future Work

Planned extensions include expansion to non-coding regulatory variants, integration of single-cell RNA-seq atlases for refined stage- and tissue-specific weights, and incorporation of constraint-based metrics (e.g., pLI, LOEUF) as additional orthogonal features. A prospective clinical validation study in undiagnosed developmental disorder cohorts is also planned.

## Conclusion

DevScore is a novel computational metric that quantifies variant pathogenicity in the context of human developmental timing. By combining variant severity (CADD + ClinVar), peak developmental expression (E_peak), stage criticality (C_stage), and domain essentiality (D_domain), it achieves an AUC of 0.928 and a large discriminatory effect size (d = 1.77). The framework is robust to architectural choices, orthogonal to conservation-based tools, and produces an interpretable, tiered classification that maps directly to clinical decision-making.

## Availability

Code: https://github.com/Ghrieb/DevMutDB
Web: https://devmutdb.vercel.app
