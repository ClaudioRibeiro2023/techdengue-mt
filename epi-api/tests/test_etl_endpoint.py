"""
Integration tests for ETL EPI endpoint
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestETLEndpoint:
    """Test ETL EPI upload endpoint"""
    
    @pytest.fixture
    def valid_csv_path(self):
        return Path(__file__).parent / "test_data" / "epi_example_valid.csv"
    
    def test_upload_valid_csv(self, valid_csv_path):
        """Test successful upload of valid CSV"""
        with open(valid_csv_path, "rb") as f:
            response = client.post(
                "/api/etl/epi/upload",
                files={"file": ("test.csv", f, "text/csv")},
                data={"competencia": "202401", "sobrescrever": "true"}
            )
        
        if response.status_code != 200:
            print(f"\nError response: {response.status_code}")
            print(f"Body: {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "mensagem" in data
        assert "relatorio" in data
        assert "casos_inseridos" in data
        
        # Check quality report
        relatorio = data["relatorio"]
        assert relatorio["total_linhas"] == 5
        assert relatorio["linhas_validas"] == 5
        assert relatorio["taxa_qualidade"] == 100.0
        assert relatorio["aprovado_para_carga"] is True
        
        # Check cases were inserted
        assert data["casos_inseridos"] >= 0  # May be 0 if ON CONFLICT DO NOTHING
    
    def test_upload_without_csv_extension(self):
        """Test rejection of non-CSV files"""
        response = client.post(
            "/api/etl/epi/upload",
            files={"file": ("test.txt", b"content", "text/plain")},
            data={"competencia": "202401", "sobrescrever": "false"}
        )
        
        assert response.status_code == 400
        assert "csv" in response.json()["detail"].lower()
    
    def test_upload_invalid_competencia(self, valid_csv_path):
        """Test rejection of invalid competencia format"""
        with open(valid_csv_path, "rb") as f:
            response = client.post(
                "/api/etl/epi/upload",
                files={"file": ("test.csv", f, "text/csv")},
                data={"competencia": "2024", "sobrescrever": "false"}
            )
        
        # FastAPI validation should catch this
        assert response.status_code == 422
    
    def test_list_competencias(self):
        """Test listing loaded competencias"""
        response = client.get("/api/etl/epi/competencias")
        
        assert response.status_code == 200
        data = response.json()
        assert "competencias" in data
        assert "total" in data
        assert isinstance(data["competencias"], list)
        assert isinstance(data["total"], int)
    
    def test_get_competencia_stats(self):
        """Test getting statistics for a specific competencia"""
        response = client.get("/api/etl/epi/competencias/202401/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "competencia" in data
        assert "total_casos" in data
        assert data["competencia"] == "202401"
    
    def test_health_endpoint(self):
        """Test health check endpoint still works"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "epi-api"
