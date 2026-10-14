import React from 'react';

interface ConfusionMatrixProps {
  matrix: [[number, number], [number, number]]; // [[TN, FP], [FN, TP]]
  modelName: string;
}

export const ConfusionMatrix: React.FC<ConfusionMatrixProps> = ({ matrix, modelName }) => {
  const [tn, fp] = matrix[0];
  const [fn, tp] = matrix[1];
  const total = tn + fp + fn + tp;

  const tnPct = ((tn / total) * 100).toFixed(1);
  const fpPct = ((fp / total) * 100).toFixed(1);
  const fnPct = ((fn / total) * 100).toFixed(1);
  const tpPct = ((tp / total) * 100).toFixed(1);

  return (
    <div className="space-y-3 font-sans">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-800">
          Confusion Matrix ({modelName})
        </span>
        <span className="font-mono text-slate-500 text-[11px]">
          Held-Out N = {total} cases
        </span>
      </div>

      <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-2xs">
        {/* Header grid */}
        <div className="grid grid-cols-3 bg-slate-50 border-b border-slate-200 text-center text-xs font-semibold text-slate-700 py-2.5">
          <div className="text-left pl-4 text-slate-400 font-medium">Actual / Predicted</div>
          <div>Predicted Normal</div>
          <div>Predicted Bust</div>
        </div>

        {/* Row 1: Actual Normal */}
        <div className="grid grid-cols-3 border-b border-slate-100 items-stretch">
          <div className="p-3 bg-slate-50/70 border-r border-slate-200 text-xs font-semibold text-slate-700 flex flex-col justify-center">
            <span>Actual Normal</span>
            <span className="text-[10px] text-slate-400 font-normal">Non-bust cases</span>
          </div>

          {/* True Negative */}
          <div className="p-4 bg-emerald-50/50 border-r border-slate-100 text-center flex flex-col items-center justify-center">
            <span className="text-xl font-bold font-mono text-emerald-800">{tn}</span>
            <span className="text-[10px] font-semibold text-emerald-700 uppercase tracking-wider mt-0.5">
              True Negative ({tnPct}%)
            </span>
          </div>

          {/* False Positive */}
          <div className="p-4 bg-amber-50/40 text-center flex flex-col items-center justify-center">
            <span className="text-xl font-bold font-mono text-amber-800">{fp}</span>
            <span className="text-[10px] font-semibold text-amber-700 uppercase tracking-wider mt-0.5">
              False Alarm ({fpPct}%)
            </span>
          </div>
        </div>

        {/* Row 2: Actual Bust */}
        <div className="grid grid-cols-3 items-stretch">
          <div className="p-3 bg-slate-50/70 border-r border-slate-200 text-xs font-semibold text-slate-700 flex flex-col justify-center">
            <span>Actual Bust</span>
            <span className="text-[10px] text-slate-400 font-normal">Upper 90th percentile</span>
          </div>

          {/* False Negative */}
          <div className="p-4 bg-rose-50/40 border-r border-slate-100 text-center flex flex-col items-center justify-center">
            <span className="text-xl font-bold font-mono text-rose-800">{fn}</span>
            <span className="text-[10px] font-semibold text-rose-700 uppercase tracking-wider mt-0.5">
              Missed Bust ({fnPct}%)
            </span>
          </div>

          {/* True Positive */}
          <div className="p-4 bg-emerald-50/80 text-center flex flex-col items-center justify-center">
            <span className="text-xl font-bold font-mono text-emerald-900">{tp}</span>
            <span className="text-[10px] font-semibold text-emerald-700 uppercase tracking-wider mt-0.5">
              Detected Bust ({tpPct}%)
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
        <span>Bust Definition: Error &gt; 90th percentile of training absolute error.</span>
        <span>Decision Threshold: 0.50</span>
      </div>
    </div>
  );
};
