"""Tests for DevScore engine."""

import pytest
from app.devscore.engine import calculate_devscore


def test_critical_impact():
    """Test critical impact score."""
    result = calculate_devscore({
        "gene": "SOX2",
        "variant": "c.70C>T",
        "vep": {"cadd_phred": 35.0},
        "clinvar": {"classification": "Pathogenic"},
        "expression": {"gastrulation": 3000},
        "domains": {"domain_class": "DNA_BINDING"},
    })
    assert result.score >= 50


def test_limited_impact():
    """Test limited impact score."""
    result = calculate_devscore({
        "gene": "BRCA1",
        "variant": "c.50G>A",
        "vep": {"cadd_phred": 5.0},
        "clinvar": {"classification": "Benign"},
        "expression": {"adult": 400},
        "domains": {"domain_class": "DISORDERED"},
    })
    assert result.score < 50
