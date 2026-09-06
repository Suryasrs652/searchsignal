import React, { useState } from 'react';
import { Recommendation } from '../types';
import { EvidenceBadge } from './EvidenceBadge';
import { CheckCircle2, TrendingUp, AlertTriangle, Lightbulb, Clock, CheckSquare, ChevronRight } from 'lucide-react';

interface Props {
  recommendations: Recommendation[];
}

export const RoadmapView: React.FC<Props> = ({ recommendations }) => {
  const [activeGroup, setActiveGroup] = useState<'all' | 'now' | 'next' | 'later' | 'experiments'>('all');

  const filtered = activeGroup === 'all'
    ? recommendations
    : recommendations.filter((r) => r.priority_group === activeGroup);

  const groupBadges = {
    now: { label: 'Now (Blockers)', color: 'bg-rose-950/60 text-rose-400 border-rose-800' },
    next: { label: 'Next (High Impact)', color: 'bg-cyan-950/60 text-cyan-400 border-cyan-800' },
    later: { label: 'Later (Strategic)', color: 'bg-indigo-950/60 text-indigo-400 border-indigo-800' },
    experiments: { label: 'Experiments (GEO/AEO)', color: 'bg-amber-950/60 text-amber-400 border-amber-800' },
  };

  return (
    <div className="space-y-6">
      {/* Group Switcher */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-slate-900/90 border border-slate-800 rounded-xl max-w-fit">
        {(['all', 'now', 'next', 'later', 'experiments'] as const).map((grp) => {
          const count = grp === 'all'
            ? recommendations.length
            : recommendations.filter((r) => r.priority_group === grp).length;
          return (
            <button
              key={grp}
              onClick={() => setActiveGroup(grp)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                activeGroup === grp
                  ? 'bg-cyan-500 text-slate-950 shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {grp} <span className="ml-1 opacity-70">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Opportunity List */}
      <div className="space-y-4">
        {filtered.map((rec) => (
          <div
            key={rec.id}
            className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-2xl shadow-lg hover:border-slate-700 transition"
          >
            <div className="flex flex-wrap items-start justify-between gap-4 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${
                      groupBadges[rec.priority_group]?.color || 'bg-slate-800'
                    }`}
                  >
                    {groupBadges[rec.priority_group]?.label || rec.priority_group}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">Effort: {rec.estimated_effort}</span>
                  {rec.evidence?.evidence_class && (
                    <EvidenceBadge evidenceClass={rec.evidence.evidence_class} />
                  )}
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">{rec.title}</h3>
              </div>

              {/* Opportunity Score Pill (Spec Section 39) */}
              <div className="text-right">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-cyan-950/70 border border-cyan-700/60 rounded-xl text-cyan-400 font-extrabold text-sm">
                  <TrendingUp className="w-4 h-4" />
                  Opportunity: {rec.opportunity_score}/100
                </div>
                <span className="block text-[11px] text-slate-500 mt-1">Impact × Reach / Effort</span>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed mb-4">{rec.description}</p>

            {/* Pros & Cons Engine (Spec Section 37) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
              {rec.pros && rec.pros.length > 0 && (
                <div className="p-3 bg-emerald-950/30 border border-emerald-900/50 rounded-xl text-xs">
                  <span className="text-emerald-400 font-bold uppercase tracking-wider block mb-1.5">
                    Pros & Expected Outcomes:
                  </span>
                  <ul className="space-y-1 text-slate-300">
                    {rec.pros.map((pro, idx) => (
                      <li key={idx} className="flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {rec.cons && rec.cons.length > 0 && (
                <div className="p-3 bg-rose-950/30 border border-rose-900/50 rounded-xl text-xs">
                  <span className="text-rose-400 font-bold uppercase tracking-wider block mb-1.5">
                    Cons & Tradeoffs / Risks:
                  </span>
                  <ul className="space-y-1 text-slate-300">
                    {rec.cons.map((con, idx) => (
                      <li key={idx} className="flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                        <span>{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Validation Method (Spec Section 65) */}
            {rec.validation_method && (
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-xs flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-300">
                  <CheckSquare className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span className="font-semibold text-slate-200">Validation Test:</span>
                  <span className="font-mono text-slate-400">{rec.validation_method}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
