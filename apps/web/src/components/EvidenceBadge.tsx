import React from 'react';
import { EvidenceClass } from '../types';

interface Props {
  evidenceClass: EvidenceClass;
  showTooltip?: boolean;
}

const BADGE_CONFIG: Record<
  EvidenceClass,
  { bg: string; text: string; border: string; label: string; desc: string }
> = {
  EXACT: {
    bg: 'bg-emerald-950/60',
    text: 'text-emerald-400',
    border: 'border-emerald-700/60',
    label: 'EXACT',
    desc: 'Directly measured from HTTP, HTML, DOM or DNS',
  },
  DERIVED: {
    bg: 'bg-cyan-950/60',
    text: 'text-cyan-400',
    border: 'border-cyan-700/60',
    label: 'DERIVED',
    desc: 'Deterministically calculated from exact observations',
  },
  VALIDATED: {
    bg: 'bg-blue-950/60',
    text: 'text-blue-400',
    border: 'border-blue-700/60',
    label: 'VALIDATED',
    desc: 'Tested against Schema.org or XML sitemap specification',
  },
  OBSERVED: {
    bg: 'bg-purple-950/60',
    text: 'text-purple-400',
    border: 'border-purple-700/60',
    label: 'OBSERVED',
    desc: 'Obtained from external source or real user metrics',
  },
  HEURISTIC: {
    bg: 'bg-amber-950/60',
    text: 'text-amber-400',
    border: 'border-amber-700/70',
    label: 'HEURISTIC',
    desc: 'Model/rule-based estimate — not an official search-engine metric',
  },
  PREDICTIVE: {
    bg: 'bg-indigo-950/60',
    text: 'text-indigo-400',
    border: 'border-indigo-700/60',
    label: 'PREDICTIVE',
    desc: 'Model-generated forecast or prioritization estimate',
  },
  UNKNOWN: {
    bg: 'bg-slate-900',
    text: 'text-slate-400',
    border: 'border-slate-700',
    label: 'UNKNOWN',
    desc: 'Cannot be established with available evidence',
  },
};

export const EvidenceBadge: React.FC<Props> = ({ evidenceClass }) => {
  const config = BADGE_CONFIG[evidenceClass] || BADGE_CONFIG.UNKNOWN;

  return (
    <span
      title={config.desc}
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide border ${config.bg} ${config.text} ${config.border} shadow-sm`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80 animate-pulse" />
      {config.label}
    </span>
  );
};
