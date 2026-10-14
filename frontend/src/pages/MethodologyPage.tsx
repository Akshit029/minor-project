import React, { useState } from 'react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';
import { APP_CONFIG } from '../data/config';
import { 
  ArrowDown, 
  Database, 
  Filter, 
  CheckCircle2, 
  Layers, 
  Calculator, 
  Cpu, 
  Bell, 
  BookOpen, 
  ShieldCheck, 
  Clock, 
  AlertTriangle,
  GitBranch
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  const [activeWeek, setActiveWeek] = useState<'all' | 'w12' | 'w3' | 'w4' | 'w5'>('all');

  const pipelineStages = [
    {
      id: 'step-1',
      title: 'NOAA GFS Operational (AWS S3 / NOMADS)',
      desc: '0.25° Gaussian grid (~27 km), forecast hours 000–168, cycles 00/06/12/18 UTC',
      category: 'Ingestion',
      icon: Database,
    },
    {
      id: 'step-2',
      title: 'Data Acquisition & Byte-Range Slicing',
      desc: 'Index (.idx) parsing with HTTP byte-range slicing for target variables without downloading full multi-GB files',
      category: 'Data Pipeline',
      icon: Filter,
    },
    {
      id: 'step-3',
      title: 'Preprocessing & Spatial Nearest-Grid Point Extraction',
      desc: 'Unit standardization (K to °C, m to mm) and nearest coordinate extraction for Srinagar, Jammu, Anantnag, Baramulla',
      category: 'Preprocessing',
      icon: Layers,
    },
    {
      id: 'step-4',
      title: 'ECMWF ERA5 Reanalysis Co-Registration',
      desc: 'Continuous atmospheric reanalysis hourly reference fields (0.25° grid) matched at valid time = init_time + lead_hours',
      category: 'Verification Reference',
      icon: GitBranch,
    },
    {
      id: 'step-5',
      title: 'Forecast Verification & Anomaly Screening (Weeks 1–2)',
      desc: 'Physical bound checks, rolling 24h/7d temporal features, standard Z-score (|Z| ≥ 3.0) and Robust MAD (|Z_mad| ≥ 3.5)',
      category: 'Quality Assurance',
      icon: ShieldCheck,
    },
    {
      id: 'step-6',
      title: 'Error & Bias Analysis (Week 3)',
      desc: 'Signed error = GFS - ERA5. MAE, RMSE, Bias computed across lead days 1–10. Leakage-safe historical mean bias correction',
      category: 'Error Metrics',
      icon: Calculator,
    },
    {
      id: 'step-7',
      title: 'Empirical Spatiotemporal Reliability Scoring (Week 4)',
      desc: 'R = R_error × C, where R_error = exp(-normalized_error) and sample confidence factor C = n / (n + k)',
      category: 'Reliability Scoring',
      icon: Calculator,
    },
    {
      id: 'step-8',
      title: 'Machine-Learning Forecast-Bust Classifier (Week 5)',
      desc: 'Empirical 90th percentile error threshold; strictly leakage-free features; chronological 70/15/15 split; LR & Random Forest',
      category: 'ML Inference',
      icon: Cpu,
    },
    {
      id: 'step-9',
      title: 'Dashboard Visualization & Real-Time Alerts',
      desc: 'Interactive Leaflet spatiotemporal map, multi-lead day heatmaps, PR curves, and configurable alert monitoring',
      category: 'Presentation',
      icon: Bell,
    },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-6 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="blue" size="xs">
                End-to-End System Architecture
              </Badge>
              <Badge variant="slate" size="xs">
                Weeks 1 through 5 Research Syllabus
              </Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Scientific Pipeline &amp; Methodology
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Complete theoretical formulation, mathematical derivations, verification protocols, and data flow from numerical weather prediction to real-time risk alerts.
            </p>
          </div>

          <Badge variant="emerald" size="sm">
            Research Verified
          </Badge>
        </div>

        <ScientificDisclaimer type="reference" />
      </div>

      {/* Visual Pipeline Flowchart */}
      <Card
        title="Visual End-to-End Scientific Architecture"
        subtitle="Chronological data transformation pipeline from NOAA GFS / ECMWF ERA5 ingestion to operational alerts"
        icon={<GitBranch className="w-5 h-5 text-indigo-600" />}
      >
        <div className="max-w-2xl mx-auto py-4 space-y-2">
          {pipelineStages.map((stage, idx) => {
            const Icon = stage.icon;
            const isLast = idx === pipelineStages.length - 1;

            return (
              <React.Fragment key={stage.id}>
                <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-all flex items-start gap-4 shadow-2xs">
                  <div className="p-2.5 rounded-lg bg-slate-100 text-slate-800 shrink-0 mt-0.5">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-xs text-slate-900">
                        {stage.title}
                      </span>
                      <Badge variant="slate" size="xs">
                        {stage.category}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {stage.desc}
                    </p>
                  </div>
                </div>

                {!isLast && (
                  <div className="flex justify-center py-1">
                    <div className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400">
                      <ArrowDown className="w-3.5 h-3.5" />
                    </div>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </Card>

      {/* Week-by-Week Implementation Deep-Dive */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-indigo-600" />
          <span>Detailed Research Phase Specifications (Weeks 1 to 5)</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Weeks 1 & 2 */}
          <Card
            title="Weeks 1 & 2: Ingestion, Quality Checks & Anomaly Screening"
            subtitle="Data curation, nearest grid point mapping, and temporal feature engineering"
          >
            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              <ul className="space-y-2 list-disc list-inside">
                <li>
                  <strong className="text-slate-800">Operational Ingestion:</strong> GFS GRIB2 retrieved from AWS S3 using index byte-range slicing; ERA5 hourly NetCDF ingested from Copernicus CDS API.
                </li>
                <li>
                  <strong className="text-slate-800">Spatial Extraction:</strong> Nearest grid point localization for Srinagar (34.08°N, 74.80°E), Jammu (32.73°N, 74.86°E), Anantnag (33.73°N, 75.15°E), and Baramulla (34.21°N, 74.34°E).
                </li>
                <li>
                  <strong className="text-slate-800">Quality Checks:</strong> Strict physical bound filters (Temperature: -40°C to +55°C, Precipitation: 0 to 500 mm).
                </li>
                <li>
                  <strong className="text-slate-800">Dual-Method Anomaly Detection:</strong> Standard Z-Score (|Z| ≥ 3.0) and Robust Z-Score via Median Absolute Deviation (|Robust Z| ≥ 3.5).
                </li>
              </ul>
            </div>
          </Card>

          {/* Week 3 */}
          <Card
            title="Week 3: Matched Error Analysis & Leakage-Safe Bias Correction"
            subtitle="Lead day verification 1–10 and historical mean-bias correction"
          >
            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              <ul className="space-y-2 list-disc list-inside">
                <li>
                  <strong className="text-slate-800">Strict Timestamp Matching:</strong> Verification strictly on (district, valid_time) where <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">valid_time = init_time + lead_hours</code>.
                </li>
                <li>
                  <strong className="text-slate-800">Sign Convention:</strong> Error = GFS - ERA5. Positive bias denotes systematic model overestimation over mountainous terrain.
                </li>
                <li>
                  <strong className="text-slate-800">Baseline Error Metrics:</strong> MAE, RMSE, Signed Bias, and Error Dispersion across lead days 1 through 10.
                </li>
                <li>
                  <strong className="text-slate-800">Hierarchical Bias Correction:</strong> Learned strictly from training split (earliest 70%) with fallback hierarchy: District × Lead Day → Regional Lead Day → Global Regional.
                </li>
              </ul>
            </div>
          </Card>

          {/* Week 4 */}
          <Card
            title="Week 4: Spatiotemporal Reliability Scoring Formula"
            subtitle="Mathematical formulation of empirical reliability index R in [0, 1]"
          >
            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1 font-mono text-[11px]">
                <div className="font-bold text-slate-900">R = R_error × C</div>
                <div className="text-indigo-700">R_error = exp(-MAE / S_error)</div>
                <div className="text-emerald-700">C = n / (n + k)</div>
              </div>
              <ul className="space-y-2 list-disc list-inside">
                <li>
                  <strong className="text-slate-800">Error Component (R_error):</strong> Standardized by engineering tolerance scale <code className="font-mono bg-slate-100 px-1">S_error = 2.0 °C</code>.
                </li>
                <li>
                  <strong className="text-slate-800">Confidence Factor (C):</strong> Smoothing parameter <code className="font-mono bg-slate-100 px-1">k = 10.0</code> and independent verification sample count <code className="font-mono bg-slate-100 px-1">n</code>.
                </li>
                <li>
                  <strong className="text-slate-800">Scientific Distinction:</strong> R is an empirical performance index based on verification history, not a Bayesian probability.
                </li>
              </ul>
            </div>
          </Card>

          {/* Week 5 */}
          <Card
            title="Week 5: Forecast-Bust Classifier & ML Evaluation"
            subtitle="Predicting extreme forecast breakdown using leakage-free issuance features"
          >
            <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
              <ul className="space-y-2 list-disc list-inside">
                <li>
                  <strong className="text-slate-800">Empirical Label Definition:</strong> Absolute error exceeding the upper 90th percentile threshold derived strictly from training data.
                </li>
                <li>
                  <strong className="text-slate-800">Strictly Leakage-Free Features:</strong> Only issuance parameters available at runtime: <code className="font-mono bg-slate-100 px-1">lead_hours, lead_day, forecast_value, init_hour, valid_hour, valid_month, district</code>.
                </li>
                <li>
                  <strong className="text-slate-800">Chronological Split:</strong> Earliest 70% for Training, next 15% for Validation, final 15% for Testing.
                </li>
                <li>
                  <strong className="text-slate-800">Production Inference API:</strong> Reusable <code className="font-mono bg-slate-100 px-1">ForecastBustPredictor</code> class loading serialized <code className="font-mono bg-slate-100 px-1">.joblib</code> models.
                </li>
              </ul>
            </div>
          </Card>
        </div>
      </div>

      {/* Operational Constraints & Scientific Assumptions */}
      <Card
        title="Scientific Assumptions & Operational Boundaries"
        subtitle="Documented limitations in complex high-altitude mountain meteorology"
        icon={<AlertTriangle className="w-5 h-5 text-amber-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <span className="font-bold text-slate-800 block text-xs">
              Precipitation Accumulation Alignment Guard
            </span>
            <p className="leading-relaxed">
              NOAA GFS total precipitation (APCP) represents step accumulations over 3–6 hour forecast windows, whereas ECMWF ERA5 records hourly depth. Unaligned instantaneous subtraction generates artificial discrepancies; precipitation bias correction is strictly safeguarded until window accumulation alignment is completed.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1.5">
            <span className="font-bold text-slate-800 block text-xs">
              Reanalysis as Reference vs Ground Truth
            </span>
            <p className="leading-relaxed">
              ERA5 is a state-of-the-art atmospheric reanalysis combining model physics with satellite and in-situ observations. However, in rugged Himalayan terrain (such as Pir Panjal and Kazinag), reanalysis topography smooths extreme peaks and deep valleys. Therefore, ERA5 is designated as a <em>reanalysis reference</em>, not immutable ground truth.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
