import React, { useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { JK_REGION_GEOJSON, JK_STUDY_BOUNDS } from '../../data/geojsonJK';
import { APP_CONFIG } from '../../data/config';
import type { DistrictInfo, DistrictName } from '../../types/weather';
import { Badge } from '../common/Badge';
import { Thermometer, CloudRain, ShieldAlert, Compass, Maximize2, MapPin } from 'lucide-react';

interface JKLeafletMapProps {
  districts: DistrictInfo[];
  selectedDistrict?: DistrictName | null;
  onSelectDistrict?: (name: DistrictName | null) => void;
  leadDay?: number;
}

// Helper to determine status color and state
const getReliabilityState = (reliability: number, bustProbability: number) => {
  if (bustProbability >= 70 || reliability < 0.50) {
    return {
      label: 'High Uncertainty',
      color: '#dc2626', // red-600
      bgClass: 'bg-rose-500',
      ringClass: 'ring-rose-400',
      badgeVariant: 'rose' as const,
    };
  }
  if (reliability >= 0.70) {
    return {
      label: 'High Reliability',
      color: '#059669', // emerald-600
      bgClass: 'bg-emerald-500',
      ringClass: 'ring-emerald-400',
      badgeVariant: 'emerald' as const,
    };
  }
  if (reliability >= 0.50) {
    return {
      label: 'Moderate Reliability',
      color: '#d97706', // amber-600
      bgClass: 'bg-amber-500',
      ringClass: 'ring-amber-400',
      badgeVariant: 'amber' as const,
    };
  }
  return {
    label: 'Low Reliability',
    color: '#ea580c', // orange-600
    bgClass: 'bg-orange-500',
    ringClass: 'ring-orange-400',
    badgeVariant: 'amber' as const,
  };
};

// Create a modern scientific divIcon for Leaflet
const createCustomMarker = (district: DistrictInfo, isSelected: boolean) => {
  const state = getReliabilityState(district.reliability, district.bustProbability);
  
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="
          width: ${isSelected ? '38px' : '32px'};
          height: ${isSelected ? '38px' : '32px'};
          background-color: ${state.color};
          border: 2.5px solid #ffffff;
          border-radius: 9999px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-family: ui-monospace, monospace;
          font-size: 11px;
          font-weight: 700;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          transition: transform 0.2s ease;
          ${isSelected ? 'transform: scale(1.15); box-shadow: 0 0 0 5px rgba(15, 23, 42, 0.35);' : ''}
        ">
          ${district.name.substring(0, 1)}
        </div>
        <div style="
          background: rgba(15, 23, 42, 0.92);
          color: white;
          padding: 2.5px 7px;
          border-radius: 5px;
          font-size: 10px;
          font-weight: 600;
          margin-top: 3px;
          white-space: nowrap;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
          display: flex;
          align-items: center;
          gap: 3px;
        ">
          <span>${district.name}</span>
          <span style="opacity: 0.65; font-size: 9px; font-family: monospace;">(${district.elevationMeters}m)</span>
        </div>
      </div>
    `,
    iconSize: [60, 52],
    iconAnchor: [30, 26],
    popupAnchor: [0, -26],
  });
};

// Sub-component to manage map bounds and centering
const MapViewSync: React.FC<{
  selectedDistrict?: DistrictName | null;
  districts: DistrictInfo[];
  resetTrigger: number;
}> = ({ selectedDistrict, districts, resetTrigger }) => {
  const map = useMap();

  // Fit all 4 study districts (from Jammu in the south to Baramulla in the north)
  React.useEffect(() => {
    map.fitBounds(JK_STUDY_BOUNDS, { padding: [35, 35] });
  }, [map]);

  // Respond to explicit reset trigger
  React.useEffect(() => {
    if (resetTrigger > 0) {
      map.fitBounds(JK_STUDY_BOUNDS, { padding: [35, 35], duration: 1.0 });
    }
  }, [resetTrigger, map]);

  // When a district is selected, smoothly fly to it at an informative zoom level (8.5)
  React.useEffect(() => {
    if (selectedDistrict) {
      const d = districts.find(item => item.name === selectedDistrict);
      if (d) {
        map.flyTo([d.lat, d.lon], 8.5, { duration: 1.0 });
      }
    }
  }, [selectedDistrict, districts, map]);

  return null;
};

export const JKLeafletMap: React.FC<JKLeafletMapProps> = ({
  districts,
  selectedDistrict,
  onSelectDistrict,
  leadDay = 5,
}) => {
  const [hoveredDistrict, setHoveredDistrict] = useState<DistrictName | null>(null);
  const [resetTrigger, setResetTrigger] = useState(0);

  const handleResetView = () => {
    if (onSelectDistrict) onSelectDistrict(null);
    setResetTrigger(prev => prev + 1);
  };

  // GeoJSON style handler
  const geoJsonStyle = (feature: any) => {
    const isMainRegion = feature?.id === 'JK-Region';
    if (isMainRegion) {
      return {
        fillColor: '#64748b',
        weight: 1.5,
        opacity: 0.85,
        color: '#475569',
        dashArray: '4, 4',
        fillOpacity: 0.05,
      };
    }

    // Individual district polygons
    const dName = feature?.id as DistrictName;
    const dist = districts.find(d => d.name === dName);
    const isSelected = selectedDistrict === dName;
    const isHovered = hoveredDistrict === dName;

    const state = dist 
      ? getReliabilityState(dist.reliability, dist.bustProbability)
      : { color: '#94a3b8' };

    return {
      fillColor: state.color,
      weight: isSelected ? 2.5 : isHovered ? 2 : 1.2,
      opacity: 0.9,
      color: isSelected ? '#0f172a' : state.color,
      fillOpacity: isSelected ? 0.35 : isHovered ? 0.28 : 0.18,
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    const dName = feature?.id as DistrictName;
    if (APP_CONFIG.studyDistricts.includes(dName)) {
      layer.on({
        mouseover: () => setHoveredDistrict(dName),
        mouseout: () => setHoveredDistrict(null),
        click: () => onSelectDistrict && onSelectDistrict(dName),
      });
    }
  };

  return (
    <div className="relative w-full h-[520px] rounded-xl overflow-hidden border border-slate-200/90 shadow-xs bg-slate-100">
      {/* Top Floating Control Bar */}
      <div className="absolute top-3 left-3 right-3 z-[1000] flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        {/* Left Badge: Grid Extent */}
        <div className="bg-white/95 backdrop-blur-xs px-3.5 py-2 rounded-lg border border-slate-200/90 shadow-sm flex items-center gap-2.5 pointer-events-auto">
          <Compass className="w-4 h-4 text-slate-700 shrink-0" />
          <div>
            <div className="text-xs font-bold text-slate-900 leading-none flex items-center gap-2">
              <span>Jammu &amp; Kashmir Study Grid</span>
              <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 px-1.5 py-0.2 rounded font-semibold">
                Lead Day {leadDay}
              </span>
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">
              South: Jammu (32.7°N) • North: Baramulla (34.2°N)
            </div>
          </div>
        </div>

        {/* Right Controls: Quick District Focus & Reset Extent */}
        <div className="bg-white/95 backdrop-blur-xs p-1.5 rounded-lg border border-slate-200/90 shadow-sm flex items-center gap-1.5 pointer-events-auto text-xs">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider pl-1 hidden sm:inline">
            Focus:
          </span>
          {APP_CONFIG.studyDistricts.map((dName) => {
            const isSel = selectedDistrict === dName;
            return (
              <button
                key={dName}
                onClick={() => onSelectDistrict && onSelectDistrict(dName)}
                className={`px-2 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                  isSel
                    ? 'bg-slate-900 text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {dName}
              </button>
            );
          })}

          <button
            onClick={handleResetView}
            className="px-2 py-1 rounded bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-semibold hover:bg-indigo-100 transition-colors flex items-center gap-1 cursor-pointer ml-1"
            title="Reset map view to fit all J&K districts including Jammu"
          >
            <Maximize2 className="w-3 h-3" />
            <span>Fit All</span>
          </button>
        </div>
      </div>

      {/* Map Legend Floating Overlay */}
      <div className="absolute bottom-3 right-3 z-[1000] bg-white/95 backdrop-blur-xs px-3 py-2 rounded-lg border border-slate-200/90 shadow-sm text-[11px] space-y-1.5">
        <div className="font-semibold text-slate-800 text-[10px] uppercase tracking-wider mb-1">
          Empirical Reliability
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
          <span className="text-slate-600">High Reliability (R ≥ 0.70)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span className="text-slate-600">Moderate (0.50 ≤ R &lt; 0.70)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
          <span className="text-slate-600">Low Reliability (R &lt; 0.50)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-pulse" />
          <span className="text-slate-600">High Uncertainty / Bust Risk</span>
        </div>
      </div>

      <MapContainer
        center={APP_CONFIG.region.center}
        zoom={APP_CONFIG.region.defaultZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* OpenStreetMap Standard Public TileLayer (100% Free, No API Key Required) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={18}
        />

        {/* Sync Center on Selection or Reset to show all 4 study districts */}
        <MapViewSync 
          selectedDistrict={selectedDistrict} 
          districts={districts}
          resetTrigger={resetTrigger}
        />

        {/* J&K Regional & District GeoJSON */}
        <GeoJSON
          data={JK_REGION_GEOJSON as any}
          style={geoJsonStyle}
          onEachFeature={onEachFeature}
        />

        {/* Markers for the 4 study districts */}
        {districts.map((dist) => {
          const isSelected = selectedDistrict === dist.name;
          const markerIcon = createCustomMarker(dist, isSelected);
          const state = getReliabilityState(dist.reliability, dist.bustProbability);

          return (
            <Marker
              key={dist.id}
              position={[dist.lat, dist.lon]}
              icon={markerIcon}
              eventHandlers={{
                click: () => onSelectDistrict && onSelectDistrict(dist.name),
              }}
            >
              <Popup className="custom-scientific-popup">
                <div className="p-4 w-64 space-y-3 font-sans">
                  {/* Popup Header */}
                  <div className="flex items-start justify-between border-b border-slate-100 pb-2">
                    <div>
                      <h4 className="font-bold text-sm text-slate-900 leading-tight">
                        {dist.name}
                      </h4>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        Elevation {dist.elevationMeters}m • Lead Day {leadDay}
                      </div>
                    </div>
                    <Badge variant={state.badgeVariant} size="xs" dot>
                      {state.label}
                    </Badge>
                  </div>

                  {/* Scientific Metrics Grid */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 rounded bg-slate-50 border border-slate-100">
                      <div className="text-[10px] text-slate-500 font-medium">Reliability (R)</div>
                      <div className="text-base font-bold font-mono text-slate-900">
                        {dist.reliability.toFixed(2)}
                      </div>
                    </div>
                    <div className="p-2 rounded bg-slate-50 border border-slate-100">
                      <div className="text-[10px] text-slate-500 font-medium">Bust Probability</div>
                      <div className="text-base font-bold font-mono text-rose-600">
                        {dist.bustProbability}%
                      </div>
                    </div>
                  </div>

                  {/* Weather Parameters */}
                  <div className="space-y-1.5 pt-1 border-t border-slate-100 text-xs">
                    <div className="flex items-center justify-between text-slate-600">
                      <span className="flex items-center gap-1.5">
                        <Thermometer className="w-3.5 h-3.5 text-slate-400" />
                        Temperature
                      </span>
                      <span className="font-mono font-semibold text-slate-800">
                        {dist.currentForecast.temperature} °C
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-600">
                      <span className="flex items-center gap-1.5">
                        <CloudRain className="w-3.5 h-3.5 text-slate-400" />
                        Rainfall
                      </span>
                      <span className="font-mono font-semibold text-slate-800">
                        {dist.currentForecast.rainfall} mm
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-600">
                      <span className="flex items-center gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-slate-400" />
                        Forecast MAE
                      </span>
                      <span className="font-mono font-semibold text-slate-800">
                        {dist.mae.toFixed(2)} °C
                      </span>
                    </div>
                  </div>

                  {/* Footer Action */}
                  <div className="pt-1 text-center">
                    <button
                      onClick={() => onSelectDistrict && onSelectDistrict(dist.name)}
                      className="w-full py-1.5 px-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-[11px] font-semibold transition-colors cursor-pointer"
                    >
                      View District Analysis →
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
