"""
Integration tests for EVD01 reports
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestEVD01Endpoints:
    """Test EVD01 report generation"""
    
    @pytest.fixture
    def atividade_with_evidencias(self):
        """Create activity with evidences"""
        # Create activity
        ativ_response = client.post("/api/atividades", json={
            "tipo": "VISTORIA",
            "municipio_cod_ibge": "5103403",
            "descricao": "Atividade para teste EVD01"
        })
        assert ativ_response.status_code == 201
        atividade_id = ativ_response.json()["id"]
        
        # Create 3 evidences
        for i in range(3):
            # Get presigned URL
            presigned = client.post(
                f"/api/atividades/{atividade_id}/evidencias/presigned-url",
                json={
                    "filename": f"test_{i}.jpg",
                    "content_type": "image/jpeg",
                    "tamanho_bytes": 1024 * (i + 1)
                }
            )
            upload_id = presigned.json()["upload_id"]
            object_key = presigned.json()["fields"]["key"]
            
            # Create evidence
            client.post(
                f"/api/atividades/{atividade_id}/evidencias",
                json={
                    "atividade_id": atividade_id,
                    "tipo": "FOTO",
                    "upload_id": upload_id,
                    "hash_sha256": f"{'a' * 63}{i}",
                    "tamanho_bytes": 1024 * (i + 1),
                    "url_s3": object_key
                }
            )
        
        return atividade_id
    
    def test_generate_evd01_success(self, atividade_with_evidencias):
        """Test successful EVD01 generation"""
        response = client.get(
            f"/api/relatorios/evd01?atividade_id={atividade_with_evidencias}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "metadata" in data
        assert "arquivo" in data
        assert "tamanho_bytes" in data
        assert "url_download" in data
        assert "merkle_tree" in data
        
        # Check metadata
        metadata = data["metadata"]
        assert metadata["atividade_id"] == atividade_with_evidencias
        assert metadata["total_evidencias"] == 3
        assert "merkle_root_hash" in metadata
        assert len(metadata["merkle_root_hash"]) == 64  # SHA-256
        
        # Check merkle tree
        merkle = data["merkle_tree"]
        assert merkle["leaf_count"] == 3
        assert merkle["tree_depth"] >= 2
        assert len(merkle["leaves"]) == 3
        
        # Check filename
        assert data["arquivo"].startswith("EVD01_Atividade_")
        assert data["arquivo"].endswith(".pdf")
    
    def test_generate_evd01_a1_landscape(self, atividade_with_evidencias):
        """Test EVD01 with A1 landscape format"""
        response = client.get(
            f"/api/relatorios/evd01?atividade_id={atividade_with_evidencias}"
            "&tamanho_pagina=A1&orientacao=landscape"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        metadata = data["metadata"]
        assert metadata["tamanho_pagina"] == "A1"
        assert metadata["orientacao"] == "landscape"
    
    def test_generate_evd01_atividade_not_found(self):
        """Test EVD01 for non-existent activity"""
        response = client.get("/api/relatorios/evd01?atividade_id=999999")
        
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]
    
    def test_generate_evd01_no_evidencias(self):
        """Test EVD01 for activity without evidences"""
        # Create activity without evidences
        ativ_response = client.post("/api/atividades", json={
            "tipo": "VISTORIA",
            "municipio_cod_ibge": "5103403"
        })
        atividade_id = ativ_response.json()["id"]
        
        response = client.get(f"/api/relatorios/evd01?atividade_id={atividade_id}")
        
        assert response.status_code == 400
        assert "não possui evidências" in response.json()["detail"]
    
    def test_download_report_not_found(self):
        """Test downloading non-existent report"""
        response = client.get("/api/relatorios/download/EVD01_NotFound.pdf")
        
        assert response.status_code == 404
    
    def test_download_report_invalid_filename(self):
        """Test downloading with invalid filename"""
        response = client.get("/api/relatorios/download/../../etc/passwd")
        
        # After sanitization, becomes just "passwd" which is not found
        assert response.status_code == 404
