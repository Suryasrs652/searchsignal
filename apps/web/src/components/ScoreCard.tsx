import React from 'react';
import { ScoreItem } from '../types';
import { EvidenceBadge } from './EvidenceBadge';
import { AlertCircle, CheckCircle2, HelpCircle } from 'lucide-react';

interface Props {
  score: ScoreItem;
}

export const ScoreCard: React.FC<Props> = ({ score }) => {
  const val = Math.round(score.score);
  const isHeuristic = score.evidence_class === 'HEURISTIC';

  // Color gradient based on score
  const getScoreColor = (s: number) => {
    if (s >= 85) return 'text-emerald-400 border-emerald-500/30';
    if (s >= 70) return 'text-cyan-400 border-cyan-500/30';
    if (s >= 55) return 'text-amber-400 border-amber-500/30';
    return 'text-rose-400 border-rose-500/30';
  };

  const getProgressColor = (s: number) => {
    if (s >= 85) return 'bg-emerald-500';
    if (s >= 70) return 'bg-cyan-500';
    if (s >= 55) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className={`relative flex flex-col justify-between p-5 rounded-xl bg-slate-900/90 border border-slate-800/80 shadow-lg hover:border-slate-700 transition duration-150`}>
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-medium text-slate-300 tracking-tight">{score.dimension}</h3>
        <EvidenceBadge evidenceClass={score.evidence_class} />
      </div>

      <div className="my-4 flex items-baseline justify-between">
        <div className="flex items-baseline gap-1">
          <span className={`text-4xl font-extrabold tracking-tight ${getScoreColor(val).split(' ')[0]}`}>
            {val}
          </span>
          <span className="text-xs text-slate-500 font-medium">/100</span>
        </div>
        <span className="text-xs text-slate-400">
          Confidence: <span className="text-slate-200 font-semibold">{Math.round(score.confidence * 100)}%</span>
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-800/80 h-1.5 rounded-full overflow-hidden mb-2">
        <div
          className={`h-full rounded-full ${getProgressColor(val)} transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(5, val))}%` }}
        />
      </div>

      {/* Explicit Heuristic or Provenance Notice */}
      {isHeuristic ? (
        <div className="mt-2 text-[11px] leading-tight text-amber-300/90 bg-amber-950/40 border border-amber-900/60 rounded px-2 py-1 flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5 shrink-0 text-amber-400" />
          <span>HEURISTIC — not an official search-engine metric</span>
        </div>
      ) : (
        <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Model: {score.methodology_version}</span>
          <span className="text-slate-500 font-mono">100% auditable</span>
        </div>
      )}
    </div>
  );
};
