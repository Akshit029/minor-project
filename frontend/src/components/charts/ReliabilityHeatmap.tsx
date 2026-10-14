import React, { useState } from 'react';
import type { DistrictName } from '../../types/weather';
import { HEATMAP_DATA, HeatmapCell } from '../../data/mockReliability';

interface ReliabilityHeatmapProps {
  selectedDistrict?: DistrictName | null;
  onSelectDistrict?: (name: DistrictName) => void;
  selectedLeadDay?: number;
  onSelectLeadDay?: (day: number) => void;
}

export const ReliabilityHeatmap: React.FC<ReliabilityHeatmapProps> = ({
  selectedDistrict,
  onSelectDistrict,
  selectedLeadDay,
  onSelectLeadDay,
}) => {
  const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);

  const districts: DistrictName[] = ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla'];
  const leadDays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  // Helper for cell color styling based on reliability score R
  const getCellColor = (score: number) => {
    if (score >= 0.85) return 'bg-emerald-600 text-white hover:ring-2 hover:ring-emerald-400';
    if (score >= 0.70) return 'bg-emerald-500 text-white hover:ring-2 hover:ring-emerald-300';
    if (score >= 0.60) return 'bg-amber-400 text-slate-900 hover:ring-2 hover:ring-amber-200';
    if (score >= 0.50) return 'bg-amber-500 text-white hover:ring-2 hover:ring-amber-300';
    if (score >= 0.35) return 'bg-orange-500 text-white hover:ring-2 hover:ring-orange-300';
    return 'bg-rose-600 text-white hover:ring-2 hover:ring-rose-400';
  };

  return (
    <div className="space-y-4 font-sans">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-slate-500">
        <span>
          Spatiotemporal decay across forecast lead horizon (1–10 days). Click any cell or column header to filter.
        </span>
        <div className="flex items-center gap-2 text-[10px]">
          <span>Optimal (1.0)</span>
          <div className="flex h-2.5 w-24 rounded overflow-hidden">
            <span className="flex-1 bg-emerald-600" />
            <span className="flex-1 bg-emerald-500" />
            <span className="flex-1 bg-amber-400" />
            <span className="flex-1 bg-amber-500" />
            <span className="flex-1 bg-orange-500" />
            <span className="flex-1 bg-rose-600" />
          </div>
          <span>Uncertain (0.0)</span>
        </div>
      </div>

      {/* Heatmap Grid Container */}
      <div className="overflow-x-auto border border-slate-200 rounded-xl bg-white shadow-2xs">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600">
              <th className="py-3 px-4 text-left font-semibold text-slate-800 w-32 border-r border-slate-200">
                District / Day
              </th>
              {leadDays.map((day) => {
                const isSelected = selectedLeadDay === day;
                return (
                  <th
                    key={`th-${day}`}
                    onClick={() => onSelectLeadDay && onSelectLeadDay(day)}
                    className={`py-2 px-1 text-center font-semibold cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-slate-900 text-white font-bold'
                        : 'hover:bg-slate-200/60'
                    }`}
                  >
                    <div className="text-[11px]">D{day}</div>
                    <div className="text-[9px] opacity-75 font-mono">{day * 24}h</div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {districts.map((dist) => {
              const isDistrictSelected = selectedDistrict === dist;
              return (
                <tr
                  key={`tr-${dist}`}
                  className={`border-b border-slate-100 last:border-b-0 ${
                    isDistrictSelected ? 'bg-slate-50/90' : 'hover:bg-slate-50/40'
                  }`}
                >
                  <td
                    onClick={() => onSelectDistrict && onSelectDistrict(dist)}
                    className="py-3 px-4 font-semibold text-slate-900 border-r border-slate-200 cursor-pointer flex items-center justify-between"
                  >
                    <span>{dist}</span>
                    {isDistrictSelected && (
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                    )}
                  </td>

                  {leadDays.map((day) => {
                    const cell = HEATMAP_DATA.find(
                      (item) => item.district === dist && item.leadDay === day
                    );
                    const score = cell ? cell.score : 0.5;
                    const isCellHighlighted =
                      (selectedLeadDay === day && selectedDistrict === dist) ||
                      selectedLeadDay === day ||
                      selectedDistrict === dist;

                    return (
                      <td
                        key={`cell-${dist}-${day}`}
                        className="p-1 text-center relative"
                        onMouseEnter={() => cell && setHoveredCell(cell)}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        <button
                          onClick={() => {
                            if (onSelectDistrict) onSelectDistrict(dist);
                            if (onSelectLeadDay) onSelectLeadDay(day);
                          }}
                          className={`w-full py-2.5 px-1 rounded-md font-mono text-xs font-semibold transition-all cursor-pointer ${getCellColor(
                            score
                          )} ${
                            isCellHighlighted
                              ? 'ring-2 ring-slate-900 shadow-xs scale-102 z-10'
                              : ''
                          }`}
                        >
                          {score.toFixed(2)}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Cell Hover Details Bar */}
      <div className="p-3 bg-slate-50 border border-slate-200/90 rounded-lg text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        {hoveredCell ? (
          <>
            <div className="flex items-center gap-3">
              <span className="font-bold text-slate-900">
                {hoveredCell.district} • Lead Day {hoveredCell.leadDay} ({hoveredCell.leadDay * 24} Hours)
              </span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-700">
                Reliability Score: <strong className="font-mono text-slate-900">{hoveredCell.score.toFixed(2)}</strong>
              </span>
              <span className="text-slate-700">
                MAE: <strong className="font-mono text-slate-900">{hoveredCell.mae.toFixed(2)} °C</strong>
              </span>
            </div>
            <div className="text-[11px] font-mono text-slate-500">
              Provenance: <span className="text-slate-700">{hoveredCell.provenance}</span>
            </div>
          </>
        ) : (
          <span className="text-slate-500 italic">
            Hover over any score cell to view localized MAE error and estimation provenance (district-level vs regional fallback).
          </span>
        )}
      </div>
    </div>
  );
};
