export default function ScientificFooter() {
  return (
    <footer className="scientific-footer">
      <div className="page-container page-wide scientific-footer-inner">
        <div>
          <div className="footer-brand">DevMutDB</div>
          <p>
            DevMutDB research prototype for DevScore, a developmental-context variant scoring method.
          </p>
          <p className="footer-small">
            Copyright &copy; 2026 Abdelkarim Hani Ghrieb.
            Code: <strong>GNU AGPL v3.0</strong> | Manuscript &amp; figures: <strong>CC BY 4.0</strong>.
            Research use only; not intended for clinical diagnosis without independent validation.
          </p>
        </div>

        <div className="footer-links">
          <a href="https://github.com/DevMutDB/DevMutDB" target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href="https://doi.org/10.1101/2025.xx.xx" target="_blank" rel="noopener noreferrer">Preprint</a>
          <a href="/methodology">Methodology</a>
          <a href="/api">API</a>
          <a href="https://github.com/DevMutDB/DevMutDB/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License</a>
        </div>

        <div className="footer-credit">
          <span>Developed by</span>
          <strong> Abdelkarim Hani Ghrieb </strong>
          <span>Public genomic APIs: Ensembl VEP, ClinVar, gnomAD, Expression Atlas (E-MTAB-6814), UniProt</span>
        </div>
      </div>
    </footer>
  );
}
