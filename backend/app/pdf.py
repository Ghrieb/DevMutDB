"""PDF report generation using WeasyPrint."""

from weasyprint import HTML, CSS
from io import BytesIO
from typing import Dict, Any


async def generate_report(result: Dict[str, Any]) -> BytesIO:
    """Generate PDF report from DevScore result."""
    
    html_content = f"""
    <html>
    <head>
        <title>DevScore Report - {result['gene']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2cm; }}
            h1 {{ color: #333; }}
            .score {{ font-size: 48px; color: #7F77DD; font-weight: bold; }}
            .section {{ margin-top: 2cm; }}
        </style>
    </head>
    <body>
        <h1>DevScore Report</h1>
        <p>Gene: <strong>{result['gene']}</strong></p>
        <p>Variant: <strong>{result['variant']}</strong></p>
        <div class="score">{result['score']:.1f}</div>
        <div class="section">
            <h2>Interpretation</h2>
            <p>{result['interpretation']}</p>
        </div>
        <div class="section">
            <h3>Components</h3>
            <ul>
                <li>V (Variant Severity): {result['V']:.4f}</li>
                <li>E_peak (Expression): {result['E_peak']:.4f}</li>
                <li>C_stage (Stage Criticality): {result['C_stage']:.4f}</li>
                <li>D_domain (Domain): {result['D_domain']:.4f}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    return BytesIO(pdf_bytes)
