from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0"}

def test_list_demo_genes():
    response = client.get("/genes")
    assert response.status_code == 200
    data = response.json()
    assert "genes" in data
    assert len(data["genes"]) > 0
    # Ensure SOX2 is in the list
    genes = [g["gene"] for g in data["genes"]]
    assert "SOX2" in genes

def test_score_demo_gene():
    response = client.post("/score", json={"gene": "SOX2", "hgvs": "c.70C>T"})
    assert response.status_code == 200
    data = response.json()
    assert data["gene"] == "SOX2"
    assert data["variant"] == "c.70C>T"
    assert "score" in data
    assert data["source"] == "demo_curated"
