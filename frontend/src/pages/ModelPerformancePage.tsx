import React, { useEffect, useState } from 'react';
import { WeatherApi, ModelPerformanceApiResponse } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import { ConfusionMatrix } from '../components/charts/ConfusionMatrix';
import { PrecisionRecallChart } from '../components/charts/PrecisionRecallChart';
import { FeatureImportanceChart } from '../components/charts/FeatureImportanceChart';
import { 
  Cpu, 
  Layers, 
  GitCommit, 
  ShieldCheck, 
  BarChart3, 
  Sliders, 
  CheckCircle,
  Database,
  ArrowRight
} from 'lucide-react';

export const ModelPerformancePage: React.FC = () => {
  const [data, setData] = useState<ModelPerformanceApiResponse | null>(null);
  const [selectedModelKey, setSelectedModelKey] = useState<'randomForest' | 'logisticRegression'>('randomForest');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    WeatherApi.getModelPerformance().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-white rounded-xl border border-slate-200 animate-pulse" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 bg-white rounded-xl border border-slate-200 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const { models, featureImportance, prCurve } = data;
  const currentModel = models[selectedModelKey];

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="indigo" size="xs">
                Scientific ML Evaluation (Week 5)
              </Badge>
              <Badge variant="slate" size="xs">
                Temporal Chronological Split
              </Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Machine Learning Model Performance
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Evaluating forecast-bust detection classifiers on held-out verification records. Features strictly respect temporal causality and prevent data leakage.
            </p>
          </div>

          {/* Model Switcher Buttons */}
          <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setSelectedModelKey('randomForest')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                selectedModelKey === 'randomForest'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Random Forest
            </button>
            <button
              onClick={() => setSelectedModelKey('logisticRegression')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                selectedModelKey === 'logisticRegression'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Logistic Regression
            </button>
          </div>
        </div>
      </div>

      {/* Primary Classification Metric KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Precision */}
        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Precision
          </span>
          <div className="text-3xl font-bold font-mono text-slate-900 mt-1">
            {(currentModel.precision * 100).toFixed(1)}%
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Positive predictive value
          </span>
        </Card>

        {/* Recall */}
        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Recall (Sensitivity)
          </span>
          <div className="text-3xl font-bold font-mono text-indigo-700 mt-1">
            {(currentModel.recall * 100).toFixed(1)}%
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Bust event capture rate
          </span>
        </Card>

        {/* F1 Score */}
        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            F1 Score
          </span>
          <div className="text-3xl font-bold font-mono text-emerald-700 mt-1">
            {currentModel.f1Score.toFixed(3)}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Harmonic mean of P &amp; R
          </span>
        </Card>

        {/* Average Precision */}
        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Average Precision (AP)
          </span>
          <div className="text-3xl font-bold font-mono text-amber-700 mt-1">
            {currentModel.averagePrecision.toFixed(3)}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Area under PR curve
          </span>
        </Card>
      </div>

      {/* Row: Confusion Matrix & Precision-Recall Curve */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix */}
        <Card
          title="Confusion Matrix Visualization"
          subtitle={`Held-out evaluation distribution for ${currentModel.modelName}`}
          action={
            <Badge variant="slate" size="xs">
              Threshold = 0.50
            </Badge>
          }
        >
          <ConfusionMatrix
            matrix={currentModel.confusionMatrix}
            modelName={currentModel.modelName}
          />
        </Card>

        {/* Precision-Recall Curve */}
        <Card
          title="Precision-Recall Curve"
          subtitle="Direct comparison between Random Forest and Logistic Regression"
          action={
            <Badge variant="emerald" size="xs">
              PR AUC Benchmark
            </Badge>
          }
        >
          <PrecisionRecallChart data={prCurve} />
        </Card>
      </div>

      {/* Feature Importance Section */}
      <Card
        title="Feature Importance (Random Forest)"
        subtitle="Ranked Gini importance of strictly leakage-free parameters available at forecast issuance"
        action={
          <Badge variant="slate" size="xs">
            7 Engineered Features
          </Badge>
        }
      >
        <FeatureImportanceChart data={featureImportance} />
      </Card>

      {/* Methodological Integrity Card */}
      <Card
        title="Experimental Validation Protocol (Chronological Split)"
        subtitle="How data leakage is strictly prevented during training and evaluation"
        icon={<ShieldCheck className="w-5 h-5 text-indigo-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <span className="font-bold text-slate-900 block text-xs">
              1. Chronological Partitioning
            </span>
            <div className="flex items-center justify-between font-mono text-[11px] text-slate-700">
              <span>Train (70%)</span>
              <span>Val (15%)</span>
              <span>Test (15%)</span>
            </div>
            <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden flex">
              <div className="h-full bg-slate-800 w-[70%]" />
              <div className="h-full bg-indigo-500 w-[15%]" />
              <div className="h-full bg-emerald-500 w-[15%]" />
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed pt-1">
              Time series ordering is strictly preserved. Future forecast cycles are never shuffled into past training cases.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <span className="font-bold text-slate-900 block text-xs">
              2. Leakage-Free Feature Space
            </span>
            <div className="p-2 rounded bg-white border border-slate-200 text-[11px] font-mono text-slate-700">
              ✓ lead_hours, cycle, district, forecast
            </div>
            <div className="p-2 rounded bg-rose-50 border border-rose-200 text-[11px] font-mono text-rose-700">
              ✗ No reference observations or errors
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Models have zero access to ERA5 reference observations or computed errors during feature extraction.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <span className="font-bold text-slate-900 block text-xs">
              3. Independent Label Threshold
            </span>
            <div className="p-2 rounded bg-white border border-slate-200 text-[11px] text-slate-700 font-mono">
              threshold = quantile(train_error, 0.90)
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              The 90th percentile bust threshold is computed strictly from training split errors and frozen before scoring validation or test splits.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
