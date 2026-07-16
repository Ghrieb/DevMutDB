from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_hgvs_hello():
    """'Hello' has no HGVS prefix -> 422"""
    response = client.post("/score", json={"gene": "SOX2", "hgvs": "Hello"})
    assert response.status_code == 422


def test_invalid_hgvs_c_hello():
    """'c.Hello' has valid prefix but invalid body -> 422"""
    response = client.post("/score", json={"gene": "SOX2", "hgvs": "c.Hello"})
    assert response.status_code == 422


def test_invalid_nucleotide_x_y():
    """'c.70X>Y' uses non-nucleotide bases -> 422"""
    response = client.post("/score", json={"gene": "SOX2", "hgvs": "c.70X>Y"})
    assert response.status_code == 422


def test_invalid_gene_returns_404():
    """Unknown gene -> 404 from Ensembl lookup"""
    response = client.post(
        "/score", json={"gene": "INVALID_GENE_123", "hgvs": "c.70C>T"}
    )
    assert response.status_code == 404


def test_out_of_bounds_cds():
    """CDS position beyond transcript length -> 404"""
    response = client.post("/score", json={"gene": "CFTR", "hgvs": "c.99999C>T"})
    assert response.status_code == 404


def test_valid_hgvs_not_broken():
    """Valid inputs still return 200"""
    response = client.post("/score", json={"gene": "SOX2", "hgvs": "c.70C>T"})
    assert response.status_code == 200
