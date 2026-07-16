# DevMutDB — DevScore

**A developmental-context variant pathogenicity scoring method.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/doi-10.1101/2025.xx.xx-blue)](https://doi.org/10.1101/2025.xx.xx)
[![Live demo](https://img.shields.io/badge/demo-devmutdb.vercel.app-6B5CE7?logo=vercel)](https://devmutdb.vercel.app)

---

DevScore is a novel metric that weights variant pathogenicity by **spatiotemporal gene expression across human developmental stages**. Unlike CADD, SIFT, or PolyPhen-2 — which assess evolutionary conservation or protein-level impact alone — DevScore explicitly incorporates *when* and *where* a gene is expressed during development, and the *criticality* of that developmental window.

<p align="center">
  <img src="validation/figures/fig1_roc_curves.png" alt="ROC curves" width="600"/>
</p>

---

## DevScore formula

```
DevScore = V × E_peak × C_stage × D_domain × 100
```

| Component | Range | Source | What it captures |
|-----------|-------|--------|------------------|
| **V** — variant severity | 0–1 | CADD PHRED + ClinVar | Combined pathogenicity from conservation, protein impact, and clinical annotation |
| **E_peak** — peak expression | 0–1 | Expression Atlas (E-MTAB-6814) | Maximum developmental TPM across 10 stages, normalised to 10,000 TPM ceiling |
| **C_stage** — stage criticality | 0.25–1.0 | Curated developmental biology | Gastrulation & neurulation = 1.0, organogenesis = 0.85, fetal = 0.65, adult = 0.25 |
| **D_domain** — domain essentiality | 0.2–1.0 | UniProt | DNA-binding domains = 1.0, ligand-binding = 0.7, UTR = 0.2 |

The product is scaled to a **0–100** interpretable range. A DevScore > 7.6 (Youden threshold) indicates likely developmental pathogenicity.

---

## Validation

Benchmarked on **110 variants** across developmental-disorder and adult-onset genes:

| Comparison | DevScore | Alternative | Improvement |
|------------|----------|-------------|-------------|
| **All variants** (AUC) | **0.931** | — | — |
| vs CADD (paired, n=110) | **0.931** | 0.457 | **+0.474** |
| vs SIFT (missense-only, n=66) | **0.930** | 0.397 | **+0.533** |
| vs PolyPhen-2 (missense-only, n=66) | **0.930** | 0.446 | **+0.484** |

- **Mann-Whitney U**: U = 2794.5, p = 3.97 × 10⁻¹⁵
- **Cohen's d**: 1.65 (large effect)
- **Median DevScore**: developmental genes = 12.3, adult-onset genes = 3.0
- **DevScore vs CADD**: Spearman ρ = 0.154 (p = 0.11), confirming DevScore measures orthogonal information not captured by conservation-based scores

Conventional evolutionary-conservation tools (SIFT, PolyPhen-2) systematically over-predict pathogenicity for adult-onset genes (TP53, BRCA1, etc.) because protein constraint alone cannot distinguish developmental timing. DevScore resolves this gap through spatiotemporal criticality weighting (C_stage).

### Figures

| Figure | Description |
|--------|-------------|
| [ROC curves](validation/figures/fig1_roc_curves.png) | DevScore (AUC 0.931) vs CADD, SIFT, PolyPhen-2 |
| [Score distributions](validation/figures/fig2_distributions.png) | Developmental vs adult-onset variant scores |
| [Case studies](validation/figures/fig3_case_studies.png) | SOX2, PPARG, BRCA1 component breakdowns |
| [Component breakdown](validation/figures/fig4_component_breakdown.png) | V, E_peak, C_stage, D_domain contributions |
| [Stage distribution](validation/figures/fig5_stage_distribution.png) | Peak developmental stage across benchmark genes |
| [DevScore vs CADD](validation/figures/fig6_scatter_devscore_vs_cadd.png) | Scatter: orthogonal signal |
| [AUC summary](validation/figures/fig7_auc_summary.png) | All pairwise comparisons |

---

## Quick start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload    # → http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                      # → http://localhost:5173
```

### Try it

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"gene": "SOX2", "hgvs": "c.70C>T", "position": 24}'
```

Response:

```json
{
  "gene": "SOX2",
  "variant": "c.70C>T",
  "score": 77.5,
  "V": 0.78,
  "E_peak": 1.0,
  "C_stage": 1.0,
  "D_domain": 1.0,
  "peak_stage": "gastrulation",
  "interpretation": "High developmental impact — mutation in a gene with peak expression during gastrulation...",
  "component_explanation": {
    "V": "ClinVar: pathogenic, CADD PHRED: 27.3",
    "E_peak": "SOX2 peaks at 9800 TPM during gastrulation",
    "C_stage": "Gastrulation (C_stage = 1.0) is the most critical developmental window",
    "D_domain": "HMG-box DNA-binding domain (D_domain = 1.0)"
  }
}
```

---

## Web app

Try the live demo at **[devmutdb.vercel.app](https://devmutdb.vercel.app)**.

1. **Enter a gene symbol** — autocomplete searches 120+ curated genes
2. **Type an HGVS variant** (e.g. `c.70C>T`), or click *Pick variant* to browse pre-loaded ClinVar entries
3. **View results** — score ring, component breakdown, stage timeline, and comparison table vs CADD / SIFT / PolyPhen-2
4. **Export PDF** — citable variant summary report (coming soon)

---

## Data sources

| Source | Data | Endpoint |
|--------|------|----------|
| Ensembl VEP | Variant consequences, SIFT, PolyPhen-2 | REST API |
| NCBI ClinVar | Clinical significance | REST API |
| Expression Atlas (E-MTAB-6814) | Developmental transcriptome (Cardoso-Moreira et al. 2019, Nature) | REST API |
| UniProt | Protein domains, essential regions | REST API |
| gnomAD v4 | Population allele frequencies | REST API |
| CADD | Combined Annotation Dependent Depletion | Scaling API |

Genes absent from the developmental transcriptome receive class-informed expression estimates based on known developmental or adult-onset patterns.

---

## Project structure

```
DevMutDB/
├── backend/                 # FastAPI server + DevScore engine
│   ├── app/
│   │   ├── main.py          # API routes (/score, /genes, /health)
│   │   ├── devscore/        # Core formula, stage index, domain weights
│   │   └── clients/         # Ensembl, ClinVar, gnomAD, Expression Atlas, UniProt
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind CSS
│   └── src/
│       ├── pages/           # Search, Results, Methodology, API Docs
│       └── components/      # ScoreRing, StageTimeline, ComparisonTable
├── validation/              # Benchmark dataset + scoring pipeline
│   ├── run_validation.py    # Batch scoring script
│   └── figures/             # ROC curves, distributions, case studies
└── paper/                   # Preprint manuscript (draft)
```

---

## Citation

```bibtex
@software{ghrieb2026devmutdb,
  author = {Abdelkarim Hani Ghrieb},
  title = {{DevMutDB}: A Developmental Mutation Pathogenicity Scoring System},
  year = {2026},
  doi = {10.1101/2025.xx.xx},
  url = {https://github.com/DevMutDB/DevMutDB}
}
```

---

## License

- **Code** (backend, frontend, validation pipeline): GNU Affero General Public License v3.0 — see [`LICENSE`](LICENSE)
- **Manuscript and figures**: Creative Commons Attribution 4.0 International (CC BY 4.0)

*Research prototype — not intended for clinical diagnosis without independent validation.*
