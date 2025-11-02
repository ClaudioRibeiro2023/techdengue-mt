"""
Tests for Relatórios endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRelatoriosEndpoint:
    """Test relatórios endpoints"""
    
    def test_generate_epi01_pdf(self):
        """Test EPI01 PDF generation"""
        response = client.get(
            "/api/relatorios/epi01",
            params={
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "formato": "pdf"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "metadata" in data
        assert "arquivo" in data
        assert "tamanho_bytes" in data
        assert "url_download" in data
        
        # Check metadata
        metadata = data["metadata"]
        assert metadata["competencia_inicio"] == "202401"
        assert metadata["competencia_fim"] == "202401"
        assert "dt_geracao" in metadata
        assert "total_municipios" in metadata
        assert "total_casos" in metadata
        assert "total_obitos" in metadata
        assert "incidencia_media" in metadata
        assert "hash_sha256" in metadata
        assert len(metadata["hash_sha256"]) == 64  # SHA-256 hex length
        assert metadata["formato"] == "pdf"
        
        # Check file info
        assert data["arquivo"].endswith(".pdf")
        assert data["tamanho_bytes"] > 0
        assert "/download/" in data["url_download"]
    
    def test_generate_epi01_csv(self):
        """Test EPI01 CSV generation"""
        response = client.get(
            "/api/relatorios/epi01",
            params={
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "formato": "csv"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["arquivo"].endswith(".csv")
        assert data["metadata"]["formato"] == "csv"
    
    def test_generate_invalid_period(self):
        """Test rejection of invalid period"""
        response = client.get(
            "/api/relatorios/epi01",
            params={
                "competencia_inicio": "202402",
                "competencia_fim": "202401"  # End before start
            }
        )
        
        assert response.status_code == 400
        assert "competencia_inicio" in response.json()["detail"].lower()
    
    def test_generate_invalid_municipio(self):
        """Test rejection of invalid IBGE code"""
        response = client.get(
            "/api/relatorios/epi01",
            params={
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "municipios": "123"  # Invalid
            }
        )
        
        assert response.status_code == 400
        assert "ibge" in response.json()["detail"].lower()
    
    def test_list_relatorios(self):
        """Test listing reports"""
        response = client.get("/api/relatorios/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "relatorios" in data
        assert "total" in data
        assert isinstance(data["relatorios"], list)
    
    def test_download_invalid_filename(self):
        """Test path traversal protection"""
        response = client.get("/api/relatorios/download/../../../etc/passwd")
        
        # Accept either 400 (invalid) or 404 (not found after sanitization)
        assert response.status_code in (400, 404)
    
    def test_download_not_found(self):
        """Test 404 for non-existent file"""
        response = client.get("/api/relatorios/download/naoexiste.pdf")
        
        assert response.status_code == 404
    
    def test_health_endpoint(self):
        """Test health check"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "relatorios-api"
