import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Circle } from 'react-leaflet';
import L, { LatLngExpression, PathOptions } from 'leaflet';
import type { Feature, FeatureCollection, Geometry, Point } from 'geojson';
import axios from 'axios';
import { getAuthHeader } from '../services/authService';
import { Layers, Filter, Download } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import { useFilters, FilterDrawer } from '@/design-system/filters';
import { webmapFilterConfig } from '@/modules/webmap/filters/config';
import { webmapHeatmapParams, webmapCamadasParams } from '@/modules/webmap/filters/adapter';

const API_BASE = '/api';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

// Centro de MT (Cuiabá)
const MT_CENTER: LatLngExpression = [-15.6014, -56.0979];

interface HeatmapPoint {
  lat: number;
  lng: number;
  intensity: number;
}

// Filtros são gerenciados pelo Design System (useFilters)

// Propriedades esperadas nos polígonos de municípios
interface MunicipioProps {
  municipio_cod_ibge: string;
  municipio_nome: string;
  populacao: number;
  casos: number;
  incidencia: number;
  obitos: number;
  letalidade: number;
  classe_risco: 'baixo' | 'medio' | 'alto' | 'muito_alto' | string;
  cor_hex?: string;
}

const MapaVivo: React.FC = () => {
  const { filters: dsFilters, setFilter, reset } = useFilters({ config: webmapFilterConfig });

  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [choroplethData, setChoroplethData] = useState<FeatureCollection<Geometry, MunicipioProps> | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Valores derivados dos filtros (sempre consistentes)
  const computed = useMemo(() => {
    const getNum = (v: unknown) => (v == null || v === '' ? undefined : Number(v));
    const ano = getNum(dsFilters['ano']) ?? new Date().getFullYear();
    const semanaInicio = getNum(dsFilters['semanaInicio']);
    const semanaFim = getNum(dsFilters['semanaFim']);
    const doenca = (dsFilters['doenca'] as string) || undefined;
    const tipoCamada = String(dsFilters['tipoCamada'] ?? 'INCIDENCIA');
    return { ano, semanaInicio, semanaFim, doenca, tipoCamada };
  }, [dsFilters]);

  // Fetch heatmap
  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        setLoading(true);
        if (DEMO_MODE) {
          setHeatmapData([
            { lat: -15.6014, lng: -56.0979, intensity: 8 },
            { lat: -16.4672, lng: -54.6356, intensity: 5 },
            { lat: -10.1841, lng: -59.4560, intensity: 3 },
          ]);
          return;
        }

        const headers = await getAuthHeader();
        const params = webmapHeatmapParams({
          ano: computed.ano,
          semanaInicio: computed.semanaInicio,
          semanaFim: computed.semanaFim,
          doenca: computed.doenca,
        })

        const response = await axios.get(`${API_BASE}/mapa/heatmap?${params}`, { headers });
        setHeatmapData(response.data.points || []);
      } catch (error) {
        console.error('Erro ao carregar heatmap:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmap();
  }, [computed]);

  // Fetch camadas (GeoJSON) - incidência por município
  useEffect(() => {
    const fetchChoropleth = async () => {
      try {
        if (DEMO_MODE) {
          const demoData: FeatureCollection<Geometry, MunicipioProps> = {
            type: 'FeatureCollection',
            features: [
              {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [-56.0979, -15.6014] },
                properties: {
                  municipio_cod_ibge: '5103403',
                  municipio_nome: 'Cuiabá',
                  populacao: 600000,
                  casos: 1200,
                  incidencia: 200.0,
                  obitos: 2,
                  letalidade: 0.17,
                  classe_risco: 'alto',
                  cor_hex: '#FF9800',
                },
              },
              {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [-56.1325, -15.6458] },
                properties: {
                  municipio_cod_ibge: '5108402',
                  municipio_nome: 'Várzea Grande',
                  populacao: 300000,
                  casos: 450,
                  incidencia: 150.0,
                  obitos: 1,
                  letalidade: 0.22,
                  classe_risco: 'medio',
                  cor_hex: '#FFC107',
                },
              },
              {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [-54.6356, -16.4672] },
                properties: {
                  municipio_cod_ibge: '5107602',
                  municipio_nome: 'Rondonópolis',
                  populacao: 240000,
                  casos: 800,
                  incidencia: 333.3,
                  obitos: 3,
                  letalidade: 0.37,
                  classe_risco: 'muito_alto',
                  cor_hex: '#F44336',
                },
              },
            ],
          };
          setChoroplethData(demoData);
          return;
        }

        const headers = await getAuthHeader();
        const params = webmapCamadasParams({
          ano: computed.ano,
          tipoCamada: computed.tipoCamada,
          doenca: computed.doenca,
        })

        const response = await axios.get(`${API_BASE}/mapa/camadas?${params}`, { headers });
        setChoroplethData(response.data?.data || null);
      } catch (error) {
        console.error('Erro ao carregar camadas:', error);
      }
    };

    fetchChoropleth();
  }, [computed]);

  const onEachFeature = (feature: Feature<Geometry, MunicipioProps>, layer: L.Layer) => {
    if (feature.properties) {
      const { municipio_nome, incidencia, classe_risco } = feature.properties;
      layer.bindPopup(`
        <div class="p-2">
          <h3 class="font-bold">${municipio_nome}</h3>
          <p>Incidência: ${typeof incidencia === 'number' ? incidencia.toFixed(2) : 'N/A'}/100k</p>
          <p>Risco: <span class="font-semibold">${classe_risco}</span></p>
        </div>
      `);
    }
  };

  const getFeatureStyle = (feature?: Feature<Geometry, MunicipioProps>): PathOptions => {
    const fillColor = feature?.properties?.cor_hex || '#2196F3';

    return {
      fillColor,
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

        {/* Drawer de Filtros (Design System) */}
        {showFilters && (
          <FilterDrawer
            open={showFilters}
            onClose={() => setShowFilters(false)}
            config={webmapFilterConfig}
            values={dsFilters}
            onChange={(field, value) => setFilter(field, value)}
            onReset={() => reset()}
          />
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
            pointToLayer={(feature: Feature<Point, MunicipioProps>, latlng) =>
              L.circleMarker(latlng, {
                radius: 6,
                color: feature.properties?.cor_hex || '#2196F3',
                fillColor: feature.properties?.cor_hex || '#2196F3',
                fillOpacity: 0.7,
                weight: 1,
              })
            }
          />
        )}

        {/* Heatmap points */}
        {heatmapData.map((point, idx) => (
          <Circle
            key={idx}
            center={[point.lat, point.lng]}
            radius={Math.max(100, point.intensity * 50)}
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
            <div className="w-6 h-6 rounded bg-[#4CAF50]"></div>
            <span className="text-sm">Baixo Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded bg-[#FFC107]"></div>
            <span className="text-sm">Médio Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded bg-[#FF9800]"></div>
            <span className="text-sm">Alto Risco</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded bg-[#F44336]"></div>
            <span className="text-sm">Muito Alto Risco</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapaVivo;
