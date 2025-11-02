"""
Tests for Mapa (Map) endpoints
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMapaEndpoint:
    """Test mapa endpoints"""
    
    def test_get_camadas_incidencia(self):
        """Test getting incidence map layer"""
        response = client.get(
            "/api/mapa/camadas",
            params={
                "tipo_camada": "incidencia",
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "cluster": False,
                "max_features": 100
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "tipo_camada" in data
        assert data["tipo_camada"] == "incidencia"
        assert "competencia_inicio" in data
        assert "competencia_fim" in data
        assert "total_municipios" in data
        assert "total_casos" in data
        assert "total_obitos" in data
        assert "incidencia_media" in data
        assert "data" in data
        assert "metadata" in data
        
        # Check GeoJSON structure
        geojson = data["data"]
        assert geojson["type"] == "FeatureCollection"
        assert "features" in geojson
        assert isinstance(geojson["features"], list)
    
    def test_get_camadas_invalid_periodo(self):
        """Test rejection of invalid period"""
        response = client.get(
            "/api/mapa/camadas",
            params={
                "tipo_camada": "incidencia",
                "competencia_inicio": "202402",
                "competencia_fim": "202401",  # End before start
            }
        )
        
        assert response.status_code == 400
        assert "competencia_inicio" in response.json()["detail"].lower()
    
    def test_get_camadas_invalid_municipio(self):
        """Test rejection of invalid IBGE code"""
        response = client.get(
            "/api/mapa/camadas",
            params={
                "tipo_camada": "incidencia",
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "municipios": "123"  # Invalid: not 7 digits
            }
        )
        
        assert response.status_code == 400
        assert "ibge" in response.json()["detail"].lower()
    
    def test_get_camadas_tipo_nao_implementado(self):
        """Test error for non-implemented layer types"""
        response = client.get(
            "/api/mapa/camadas",
            params={
                "tipo_camada": "ipo",  # Not yet implemented
                "competencia_inicio": "202401",
                "competencia_fim": "202401"
            }
        )
        
        # Accept either 500 or 501 for not implemented features
        assert response.status_code in (500, 501)
        detail = response.json()["detail"].lower()
        assert "implementado" in detail or "erro" in detail
    
    def test_get_camadas_with_clustering(self):
        """Test clustering parameter"""
        response = client.get(
            "/api/mapa/camadas",
            params={
                "tipo_camada": "incidencia",
                "competencia_inicio": "202401",
                "competencia_fim": "202401",
                "cluster": True,
                "max_features": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check clustering metadata
        if data["total_municipios"] > 5:
            assert data["metadata"].get("clustering_applied") is True
    
    def test_list_municipios(self):
        """Test listing available municipalities"""
        response = client.get("/api/mapa/municipios")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "municipios" in data
        assert "total" in data
        assert isinstance(data["municipios"], list)
        assert data["total"] > 0
        
        # Check municipality structure
        if data["municipios"]:
            mun = data["municipios"][0]
            assert "cod_ibge" in mun
            assert "nome" in mun
            assert "populacao" in mun
            assert "centroid" in mun
            assert "lat" in mun["centroid"]
            assert "lon" in mun["centroid"]
