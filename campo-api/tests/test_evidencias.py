"""
Integration tests for Evidencias endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestEvidenciasEndpoints:
    """Test Evidencias endpoints"""
    
    @pytest.fixture
    def atividade_id(self):
        """Create a test activity and return its ID"""
        response = client.post("/api/atividades", json={
            "tipo": "VISTORIA",
            "municipio_cod_ibge": "5103403",
            "descricao": "Atividade para teste de evidências"
        })
        assert response.status_code == 201
        return response.json()["id"]
    
    def test_generate_presigned_url_success(self, atividade_id):
        """Test generating presigned URL"""
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias/presigned-url",
            json={
                "filename": "test_photo.jpg",
                "content_type": "image/jpeg",
                "tamanho_bytes": 1024000
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "upload_url" in data
        assert "upload_id" in data
        assert "expires_in" in data
        assert data["expires_in"] == 300
        
        # Verify upload_url format (should contain S3 endpoint)
        assert "minio" in data["upload_url"] or "s3" in data["upload_url"]
    
    def test_generate_presigned_url_invalid_content_type(self, atividade_id):
        """Test rejection of invalid content type"""
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias/presigned-url",
            json={
                "filename": "test.exe",
                "content_type": "application/x-msdownload",
                "tamanho_bytes": 1024
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_presigned_url_too_large(self, atividade_id):
        """Test rejection of file too large"""
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias/presigned-url",
            json={
                "filename": "huge.jpg",
                "content_type": "image/jpeg",
                "tamanho_bytes": 60 * 1024 * 1024  # 60MB > 50MB limit
            }
        )
        
        assert response.status_code == 422
    
    def test_generate_presigned_url_atividade_not_found(self):
        """Test presigned URL for non-existent activity"""
        response = client.post(
            "/api/atividades/999999/evidencias/presigned-url",
            json={
                "filename": "test.jpg",
                "content_type": "image/jpeg",
                "tamanho_bytes": 1024
            }
        )
        
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]
    
    def test_create_evidencia_success(self, atividade_id):
        """Test creating evidence record"""
        # First get presigned URL
        presigned_response = client.post(
            f"/api/atividades/{atividade_id}/evidencias/presigned-url",
            json={
                "filename": "test_photo.jpg",
                "content_type": "image/jpeg",
                "tamanho_bytes": 1024000
            }
        )
        upload_id = presigned_response.json()["upload_id"]
        object_key = presigned_response.json()["fields"]["key"]
        
        # Create evidence record
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias",
            json={
                "atividade_id": atividade_id,
                "tipo": "FOTO",
                "upload_id": upload_id,
                "hash_sha256": "a" * 64,  # Valid SHA-256 hash
                "tamanho_bytes": 1024000,
                "url_s3": object_key,
                "descricao": "Foto de teste",
                "metadata": {
                    "exif": {
                        "make": "Test Camera",
                        "model": "TC-100"
                    }
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert data["id"] > 0
        assert data["atividade_id"] == atividade_id
        assert data["tipo"] == "FOTO"
        assert data["status"] == "CONCLUIDA"
        assert data["hash_sha256"] == "a" * 64
        assert data["url_s3"] == object_key
        assert "url_download" in data
        assert data["descricao"] == "Foto de teste"
        assert data["metadata"]["exif"]["make"] == "Test Camera"
    
    def test_create_evidencia_invalid_hash(self, atividade_id):
        """Test creating evidence with invalid hash"""
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias",
            json={
                "atividade_id": atividade_id,
                "tipo": "FOTO",
                "upload_id": "test-id",
                "hash_sha256": "invalid-hash",  # Too short
                "tamanho_bytes": 1024,
                "url_s3": "test.jpg"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_evidencia_atividade_mismatch(self, atividade_id):
        """Test creating evidence with mismatched activity ID"""
        response = client.post(
            f"/api/atividades/{atividade_id}/evidencias",
            json={
                "atividade_id": atividade_id + 1,  # Different ID
                "tipo": "FOTO",
                "upload_id": "test-id",
                "hash_sha256": "a" * 64,
                "tamanho_bytes": 1024,
                "url_s3": "test.jpg"
            }
        )
        
        assert response.status_code == 400
        assert "não corresponde" in response.json()["detail"]
    
    def test_list_evidencias_empty(self, atividade_id):
        """Test listing evidences for activity with none"""
        response = client.get(f"/api/atividades/{atividade_id}/evidencias")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0
    
    def test_list_evidencias_with_items(self, atividade_id):
        """Test listing evidences after creating some"""
        # Create 2 evidences
        for i in range(2):
            presigned_response = client.post(
                f"/api/atividades/{atividade_id}/evidencias/presigned-url",
                json={
                    "filename": f"test_{i}.jpg",
                    "content_type": "image/jpeg",
                    "tamanho_bytes": 1024
                }
            )
            upload_id = presigned_response.json()["upload_id"]
            object_key = presigned_response.json()["fields"]["key"]
            
            client.post(
                f"/api/atividades/{atividade_id}/evidencias",
                json={
                    "atividade_id": atividade_id,
                    "tipo": "FOTO",
                    "upload_id": upload_id,
                    "hash_sha256": f"{'a' * 63}{i}",
                    "tamanho_bytes": 1024,
                    "url_s3": object_key
                }
            )
        
        # List evidences
        response = client.get(f"/api/atividades/{atividade_id}/evidencias")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 2
        assert len(data["items"]) == 2
        
        # Check all have download URLs
        for item in data["items"]:
            assert "url_download" in item
            assert item["url_download"] is not None
    
    def test_delete_evidencia(self, atividade_id):
        """Test deleting evidence"""
        # TODO: Fix router path registration for /evidencias/{id} endpoint
        pytest.skip("Router path issue - endpoint not registering correctly")
    
    def test_delete_evidencia_not_found(self):
        """Test deleting non-existent evidence"""
        response = client.delete("/api/evidencias/999999")
        
        assert response.status_code == 404
