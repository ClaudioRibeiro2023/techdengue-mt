import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Circle } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import axios from 'axios';
import { getAuthHeader } from '../services/authService';
import { Layers, Filter, Download } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Centro de MT (Cuiabá)
const MT_CENTER: LatLngExpression = [-15.6014, -56.0979];

interface HeatmapPoint {
  latitude: number;
  longitude: number;
  intensidade: number;
}

interface MapFilters {
  ano: number;
  semanaInicio?: number;
  semanaFim?: number;
  doenca?: string;
  tipoCamada: string;
}

const MapaVivo: React.FC = () => {
  const [filters, setFilters] = useState<MapFilters>({
    ano: new Date().getFullYear(),
    tipoCamada: 'INCIDENCIA',
  });

  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [choroplethData, setChoroplethData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch heatmap
  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        setLoading(true);
        const headers = await getAuthHeader();
        const params = new URLSearchParams({
          ano: filters.ano.toString(),
          ...(filters.semanaInicio && { semana_epi_inicio: filters.semanaInicio.toString() }),
          ...(filters.semanaFim && { semana_epi_fim: filters.semanaFim.toString() }),
          ...(filters.doenca && { doenca_tipo: filters.doenca }),
        });

        const response = await axios.get(`${API_URL}/mapa/heatmap?${params}`, { headers });
        setHeatmapData(response.data.pontos || []);
      } catch (error) {
        console.error('Erro ao carregar heatmap:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmap();
  }, [filters]);

  // Fetch choropleth
  useEffect(() => {
    const fetchChoropleth = async () => {
      try {
        const headers = await getAuthHeader();
        const params = new URLSearchParams({
          ano: filters.ano.toString(),
          tipo_camada: filters.tipoCamada,
          ...(filters.semanaInicio && { semana_epi_inicio: filters.semanaInicio.toString() }),
          ...(filters.semanaFim && { semana_epi_fim: filters.semanaFim.toString() }),
          ...(filters.doenca && { doenca_tipo: filters.doenca }),
        });

        const response = await axios.get(`${API_URL}/mapa/camadas?${params}`, { headers });
        setChoroplethData(response.data);
      } catch (error) {
        console.error('Erro ao carregar camadas:', error);
      }
    };

    fetchChoropleth();
  }, [filters]);

  const onEachFeature = (feature: any, layer: any) => {
    if (feature.properties) {
      const { nome, valor, nivel_risco } = feature.properties;
      layer.bindPopup(`
        <div class="p-2">
          <h3 class="font-bold">${nome}</h3>
          <p>Incidência: ${valor ? valor.toFixed(2) : 'N/A'}/100k</p>
          <p>Risco: <span class="font-semibold">${nivel_risco}</span></p>
        </div>
      `);
    }
  };

  const getFeatureStyle = (feature: any) => {
    const nivel = feature.properties?.nivel_risco;
    const colors: Record<string, string> = {
      BAIXO: '#4CAF50',
      MEDIO: '#FFC107',
      ALTO: '#FF9800',
      MUITO_ALTO: '#F44336',
    };

    return {
      fillColor: colors[nivel] || '#2196F3',
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.6,
    };
  };

  return (
    <div className="relative h-screen w-full">
      {/* Header com filtros */}
      <div className="absolute top-0 left-0 right-0 z-[1000] bg-white shadow-md p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Mapa Vivo - Vigilância Epidemiológica</h1>
            <p className="text-sm text-gray-600">Dados em tempo real - Mato Grosso</p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
            >
              <Filter className="w-4 h-4" />
              <span>Filtros</span>
            </button>

            <button
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Exportar</span>
            </button>

            <button
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center space-x-2"
            >
              <Layers className="w-4 h-4" />
              <span>Camadas</span>
            </button>
          </div>
        </div>

        {/* Painel de filtros */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Ano</label>
              <select
                value={filters.ano}
                onChange={(e) => setFilters({ ...filters, ano: parseInt(e.target.value) })}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Doença</label>
              <select
                value={filters.doenca || ''}
                onChange={(e) => setFilters({ ...filters, doenca: e.target.value || undefined })}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="">Todas</option>
                <option value="DENGUE">Dengue</option>
                <option value="ZIKA">Zika</option>
                <option value="CHIKUNGUNYA">Chikungunya</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Camada</label>
              <select
                value={filters.tipoCamada}
                onChange={(e) => setFilters({ ...filters, tipoCamada: e.target.value })}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="INCIDENCIA">Incidência</option>
                <option value="IPO">IPO (Pendências)</option>
                <option value="IDO">IDO (Depósitos)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Semanas</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  min="1"
                  max="53"
                  placeholder="Início"
                  value={filters.semanaInicio || ''}
                  onChange={(e) => setFilters({ ...filters, semanaInicio: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-full border rounded-md px-3 py-2"
                />
                <input
                  type="number"
                  min="1"
                  max="53"
                  placeholder="Fim"
                  value={filters.semanaFim || ''}
                  onChange={(e) => setFilters({ ...filters, semanaFim: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Mapa */}
      <MapContainer
        center={MT_CENTER}
        zoom={7}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Choropleth (polígonos) */}
        {choroplethData && (
          <GeoJSON
            data={choroplethData}
            style={getFeatureStyle}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Heatmap points */}
        {heatmapData.map((point, idx) => (
          <Circle
            key={idx}
            center={[point.latitude, point.longitude]}
            radius={point.intensidade * 100}
            pathOptions={{
              fillColor: '#FF6B6B',
              fillOpacity: 0.4,
              color: '#FF6B6B',
              weight: 1,
            }}
          />
        ))}
      </MapContainer>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center z-[2000]">
          <div className="bg-white rounded-lg p-6">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-700">Carregando dados...</p>
          </div>
        </div>
      )}

      {/* Legenda */}
      <div className="absolute bottom-8 left-8 z-[1000] bg-white rounded-lg shadow-lg p-4">
        <h3 className="font-bold mb-2">Legenda</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded" style={{ backgroundColor: '#4CAF50' }}></div>
            <span className="text-sm">Baixo Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded" style={{ backgroundColor: '#FFC107' }}></div>
            <span className="text-sm">Médio Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded" style={{ backgroundColor: '#FF9800' }}></div>
            <span className="text-sm">Alto Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded" style={{ backgroundColor: '#F44336' }}></div>
            <span className="text-sm">Muito Alto Risco</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapaVivo;
