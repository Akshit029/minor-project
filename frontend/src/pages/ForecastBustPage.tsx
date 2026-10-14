import React, { useEffect, useState } from 'react';
import { WeatherApi } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';
import type { 
  ForecastBustPredictionResult, 
  DistrictName, 
  BustRiskLevel, 
  ModelMetricsData 
} from '../types/weather';
import { APP_CONFIG } from '../data/config';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { 
  AlertOctagon, 
  Cpu, 
  ShieldAlert, 
  Sliders, 
  Sparkles, 
  CheckCircle, 
  Send,
  Database,
  Info
} from 'lucide-react';

export const ForecastBustPage: React.FC = () => {
  const [predictions, setPredictions] = useState<ForecastBustPredictionResult[]>([]);
  const [models, setModels] = useState<Record<'logisticRegression' | 'randomForest', ModelMetricsData> | null>(null);
  const [loading, setLoading] = useState(true);

  // Live inference interactive widget state
  const [simDistrict, setSimDistrict] = useState<DistrictName>('Anantnag');
  const [simLeadDay, setSimLeadDay] = useState<number>(6);
  const [simForecastValue, setSimForecastValue] = useState<number>(27.5);
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<ForecastBustPredictionResult | null>(null);

  useEffect(() => {
    Promise.all([WeatherApi.getBustPredictions(), WeatherApi.getModelPerformance()]).then(
      ([preds, perf]) => {
        setPredictions(preds);
        setModels(perf.models);
        setLoading(false);
      }
    );
  }, []);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    try {
      const res = await WeatherApi.predictBust({
        district: simDistrict,
        leadDay: simLeadDay,
        forecastValue: simForecastValue,
        initHour: 0,
        validHour: 12,
        validMonth: 10,
      });
      setSimResult(res);
    } finally {
      setSimulating(false);
    }
  };

  const getRiskBadgeVariant = (risk: BustRiskLevel) => {
    switch (risk) {
      case 'HIGH RISK':
        return 'rose';
      case 'MEDIUM RISK':
        return 'amber';
      case 'LOW RISK':
      default:
        return 'emerald';
    }
  };

  if (loading || !models) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-white rounded-xl border border-slate-200 animate-pulse" />
        <div className="h-64 bg-white rounded-xl border border-slate-200 animate-pulse" />
      </div>
    );
  }

  // Model comparison bar chart data
  const modelCompData = [
    {
      metric: 'Precision',
      'Logistic Regression': Number(models.logisticRegression.precision.toFixed(3)),
      'Random Forest': Number(models.randomForest.precision.toFixed(3)),
    },
    {
      metric: 'Recall',
      'Logistic Regression': Number(models.logisticRegression.recall.toFixed(3)),
      'Random Forest': Number(models.randomForest.recall.toFixed(3)),
    },
    {
      metric: 'F1 Score',
      'Logistic Regression': Number(models.logisticRegression.f1Score.toFixed(3)),
      'Random Forest': Number(models.randomForest.f1Score.toFixed(3)),
    },
    {
      metric: 'Average Precision',
      'Logistic Regression': Number(models.logisticRegression.averagePrecision.toFixed(3)),
      'Random Forest': Number(models.randomForest.averagePrecision.toFixed(3)),
    },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="rose" size="xs">
                Week 5 ML Classifier
              </Badge>
              <Badge variant="slate" size="xs">
                90th Percentile Training Threshold
              </Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Forecast Bust Prediction
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Detecting severe forecast breakdowns using strictly issuance-time features. Predicts whether absolute verification error will exceed the empirical 90th percentile threshold.
            </p>
          </div>

          <Badge variant="amber" size="sm" dot>
            Demo Data (Week 5 Prototype)
          </Badge>
        </div>

        <ScientificDisclaimer type="demo" />
      </div>

      {/* Model Performance Overview Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Specs Card */}
        <Card
          title="Trained Classifier Pipelines (Week 5)"
          subtitle="Evaluated on chronologically held-out test splits"
          icon={<Cpu className="w-5 h-5 text-indigo-600" />}
        >
          <div className="space-y-4 text-xs">
            {/* Logistic Regression Card */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 text-sm">
                  1. Logistic Regression (Class-Weighted)
                </span>
                <Badge variant="indigo" size="xs">
                  Linear Baseline
                </Badge>
              </div>
              <p className="text-slate-600 text-[11px]">
                Interpretable baseline utilizing balanced class weighting to handle the 90:10 imbalance ratio without synthetic oversampling.
              </p>
              <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-200 text-center font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Precision</span>
                  <span className="font-bold text-slate-800">{(models.logisticRegression.precision * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Recall</span>
                  <span className="font-bold text-slate-800">{(models.logisticRegression.recall * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">F1 Score</span>
                  <span className="font-bold text-slate-800">{models.logisticRegression.f1Score.toFixed(3)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Avg Prec (AP)</span>
                  <span className="font-bold text-indigo-700">{models.logisticRegression.averagePrecision.toFixed(3)}</span>
                </div>
              </div>
            </div>

            {/* Random Forest Card */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 text-sm">
                  2. Random Forest Classifier (100 Trees)
                </span>
                <Badge variant="emerald" size="xs">
                  Top Nonlinear
                </Badge>
              </div>
              <p className="text-slate-600 text-[11px]">
                Nonlinear ensemble capturing complex interactions between lead hours, issuance cycle, and mountainous elevation regimes.
              </p>
              <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-200 text-center font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Precision</span>
                  <span className="font-bold text-slate-800">{(models.randomForest.precision * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Recall</span>
                  <span className="font-bold text-slate-800">{(models.randomForest.recall * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">F1 Score</span>
                  <span className="font-bold text-slate-800">{models.randomForest.f1Score.toFixed(3)}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block font-sans">Avg Prec (AP)</span>
                  <span className="font-bold text-emerald-700">{models.randomForest.averagePrecision.toFixed(3)}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Model Metric Comparison Chart */}
        <Card
          title="Model Metric Comparison"
          subtitle="Precision, Recall, F1 Score, and Average Precision benchmark"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={modelCompData}
                margin={{ top: 10, right: 15, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                  dataKey="metric"
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis
                  domain={[0, 1]}
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar
                  dataKey="Logistic Regression"
                  fill="#6366f1"
                  radius={[4, 4, 0, 0]}
                  barSize={24}
                />
                <Bar
                  dataKey="Random Forest"
                  fill="#059669"
                  radius={[4, 4, 0, 0]}
                  barSize={24}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[11px] text-slate-500 pt-2 text-center">
            Both models were fit on the earliest 70% chronological split and evaluated on held-out test data.
          </div>
        </Card>
      </div>

      {/* Forecast Bust Prediction Table */}
      <Card
        title="Operational Forecast-Bust Predictions"
        subtitle="Evaluated cases across Jammu & Kashmir study grid"
        action={
          <Badge variant="slate" size="xs">
            {predictions.length} Active Forecast Cases
          </Badge>
        }
      >
        <div className="overflow-x-auto border border-slate-200 rounded-xl bg-white shadow-2xs">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50/80 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">District</th>
                <th className="py-3 px-4">Lead Day</th>
                <th className="py-3 px-4">GFS Forecast</th>
                <th className="py-3 px-4">Bust Probability</th>
                <th className="py-3 px-4">Predicted Class</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Inference Model</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {predictions.map((p, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    {p.district}
                  </td>
                  <td className="py-3 px-4 font-mono font-medium text-slate-700">
                    Day {p.leadDay} ({p.leadHours}h)
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">
                    {p.forecastValue.toFixed(1)} °C
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-900">
                    <span
                      className={
                        p.bustProbability >= 70
                          ? 'text-rose-600'
                          : p.bustProbability >= 35
                          ? 'text-amber-600'
                          : 'text-emerald-600'
                      }
                    >
                      {p.bustProbability}%
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono">
                    <span className={p.predictedClass === 'BUST' ? 'font-bold text-rose-700' : 'text-slate-600'}>
                      {p.predictedClass}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={getRiskBadgeVariant(p.riskLevel)} size="xs" dot>
                      {p.riskLevel}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                    {p.modelUsed}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Live Interactive Predictor Simulator Widget */}
      <Card
        title="Interactive Forecast-Bust Inference Simulator"
        subtitle="Simulate real-time prediction using the production inference pipeline API logic"
        icon={<Sparkles className="w-5 h-5 text-indigo-600" />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <form onSubmit={handleSimulate} className="lg:col-span-7 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* District */}
              <div>
                <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                  Target District
                </label>
                <select
                  value={simDistrict}
                  onChange={(e) => setSimDistrict(e.target.value as DistrictName)}
                  className="w-full bg-white border border-slate-300 text-slate-900 text-xs font-semibold rounded-lg px-3 py-2 shadow-2xs focus:ring-2 focus:ring-slate-900"
                >
                  {APP_CONFIG.studyDistricts.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              {/* Lead Day */}
              <div>
                <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                  Forecast Lead Day (1–10)
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={simLeadDay}
                  onChange={(e) => setSimLeadDay(Number(e.target.value))}
                  className="w-full bg-white border border-slate-300 text-slate-900 text-xs font-mono font-semibold rounded-lg px-3 py-2 shadow-2xs focus:ring-2 focus:ring-slate-900"
                />
              </div>

              {/* Forecast Value */}
              <div>
                <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                  Forecast Temp (°C)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={simForecastValue}
                  onChange={(e) => setSimForecastValue(Number(e.target.value))}
                  className="w-full bg-white border border-slate-300 text-slate-900 text-xs font-mono font-semibold rounded-lg px-3 py-2 shadow-2xs focus:ring-2 focus:ring-slate-900"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="text-[11px] text-slate-500">
                Inputs are verified against strict schema: <code className="font-mono text-slate-700">lead_hours, district, forecast_value</code>
              </span>
              <button
                type="submit"
                disabled={simulating}
                className="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{simulating ? 'Inferring...' : 'Run Predictor'}</span>
              </button>
            </div>
          </form>

          {/* Simulator Result Output Display */}
          <div className="lg:col-span-5 p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-200">
              <span className="font-semibold text-slate-700 uppercase tracking-wider text-[10px]">
                Inference Result
              </span>
              {simResult && (
                <Badge variant={getRiskBadgeVariant(simResult.riskLevel)} size="xs" dot>
                  {simResult.riskLevel}
                </Badge>
              )}
            </div>

            {simResult ? (
              <div className="space-y-2 text-xs">
                <div className="flex items-baseline justify-between">
                  <span className="text-slate-500">Bust Probability:</span>
                  <span className="text-2xl font-bold font-mono text-slate-900">
                    {simResult.bustProbability}%
                  </span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Predicted Class:</span>
                  <span className="font-mono font-bold text-slate-900">{simResult.predictedClass}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Lookahead:</span>
                  <span className="font-mono text-slate-700">Day {simResult.leadDay} ({simResult.leadHours}h)</span>
                </div>
                <div className="text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-200 flex justify-between">
                  <span>Inference Time:</span>
                  <span>{simResult.computedTimestamp}</span>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-xs text-slate-400 italic">
                Select parameters and click "Run Predictor" to test the model API.
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};
