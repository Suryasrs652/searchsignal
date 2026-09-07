import React from 'react';
import { AuditAnalysisReport } from '../lib/auditEngine';
import {
  CheckCircle2,
  AlertTriangle,
  Zap,
  Shield,
  FileText,
  Link2,
  Globe,
  Lock,
  Clock,
  Printer,
  TrendingUp,
} from 'lucide-react';

interface Props {
  report: AuditAnalysisReport;
  onOpenRoadmap: () => void;
}

export const ExecutiveReportView: React.FC<Props> = ({ report, onOpenRoadmap }) => {
  return (
    <div className="space-y-8">
      {/* Quick Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Server TTFB</span>
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span className="text-lg font-extrabold text-white">{report.metrics.ttfbMs}ms</span>
          </div>
        </div>

        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Page Load Time</span>
          <div className="flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="text-lg font-extrabold text-white">{(report.metrics.loadTimeMs / 1000).toFixed(2)}s</span>
          </div>
        </div>

        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Content Words</span>
          <div className="flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span className="text-lg font-extrabold text-white">{report.metrics.wordCount}</span>
          </div>
        </div>

        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Internal Links</span>
          <div className="flex items-center gap-1.5">
            <Link2 className="w-4 h-4 text-emerald-400" />
            <span className="text-lg font-extrabold text-white">{report.metrics.internalLinksCount}</span>
          </div>
        </div>

        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">External Links</span>
          <div className="flex items-center gap-1.5">
            <Globe className="w-4 h-4 text-purple-400" />
            <span className="text-lg font-extrabold text-white">{report.metrics.externalLinksCount}</span>
          </div>
        </div>

        <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Security / SSL</span>
          <div className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span className="text-lg font-extrabold text-emerald-400">{report.metrics.hasSsl ? 'HTTPS Active' : 'No SSL'}</span>
          </div>
        </div>
      </div>

      {/* Production Evidence: Exact Observed HTML & Metadata Card */}
      {report.pageMetadata && (
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${report.isLiveAnalysis ? 'bg-emerald-400 animate-pulse' : 'bg-cyan-400'}`} />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                {report.isLiveAnalysis ? 'Live Target DOM Extraction' : 'Target Document Architecture'}
              </span>
            </div>
            <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
              {report.pageMetadata.headingsCount} Headings • {report.pageMetadata.imagesCount} Images • {report.pageMetadata.schemaCount} Schemas
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5 font-mono">
              <div>
                <span className="text-slate-500 font-sans">Observed &lt;title&gt;:</span>{' '}
                <span className="text-white font-medium">{report.pageMetadata.title || '<Not Declared>'}</span>
              </div>
              <div>
                <span className="text-slate-500 font-sans">Meta Description:</span>{' '}
                <span className="text-slate-300">{report.pageMetadata.description || '<Not Declared>'}</span>
              </div>
              <div>
                <span className="text-slate-500 font-sans">Canonical Tag:</span>{' '}
                <span className="text-cyan-400">{report.pageMetadata.canonical || '<Not Declared>'}</span>
              </div>
            </div>

            <div className="space-y-1.5 font-mono">
              <div>
                <span className="text-slate-500 font-sans">Primary &lt;h1&gt;:</span>{' '}
                <span className="text-white font-medium">
                  {report.pageMetadata.h1Tags.length > 0 ? report.pageMetadata.h1Tags[0] : '<No H1 Tag>'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 font-sans">Schema.org Types:</span>{' '}
                <span className="text-amber-400">
                  {report.pageMetadata.schemaTypesFound.length > 0
                    ? report.pageMetadata.schemaTypesFound.join(', ')
                    : '<Zero Schema Detected>'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 font-sans">OpenGraph / Twitter Cards:</span>{' '}
                <span className={report.pageMetadata.hasOgTags ? 'text-emerald-400' : 'text-slate-500'}>
                  {report.pageMetadata.hasOgTags ? 'OG Ready' : 'Missing OG'} / {report.pageMetadata.hasTwitterTags ? 'Twitter Ready' : 'Missing Twitter'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Two-Column Breakdown: Strengths vs Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* STRENGTHS */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800 text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">Website Strengths</h3>
                <p className="text-xs text-slate-400">Foundational elements meeting or exceeding search standards</p>
              </div>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
              {report.strengths.length} Detected
            </span>
          </div>

          <div className="space-y-3">
            {report.strengths.map((s, idx) => (
              <div
                key={idx}
                className="p-4 bg-slate-900/80 border border-emerald-900/40 rounded-xl hover:border-emerald-700/60 transition shadow-sm"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <h4 className="text-sm font-bold text-emerald-300 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    {s.title}
                  </h4>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800 shrink-0">
                    {s.impact}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed pl-6">{s.description}</p>
                <span className="inline-block mt-2 pl-6 text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
                  Category: {s.category}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* WEAKNESSES */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-400">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">Website Weaknesses & Bottlenecks</h3>
                <p className="text-xs text-slate-400">Critical gaps hindering ranking, crawlability, or AI extraction</p>
              </div>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800">
              {report.weaknesses.length} Issues
            </span>
          </div>

          <div className="space-y-3">
            {report.weaknesses.map((w, idx) => (
              <div
                key={idx}
                className="p-4 bg-slate-900/80 border border-rose-900/40 rounded-xl hover:border-rose-700/60 transition shadow-sm"
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <h4 className="text-sm font-bold text-rose-300 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                    {w.title}
                  </h4>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded shrink-0 ${
                      w.severity === 'critical'
                        ? 'bg-rose-950 text-rose-400 border border-rose-800'
                        : 'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}
                  >
                    {w.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed pl-6 mb-2">{w.description}</p>
                <div className="ml-6 p-2.5 bg-slate-950 rounded-lg border border-slate-800 text-[11px] space-y-1">
                  <div>
                    <strong className="text-slate-400">Observed Evidence: </strong>
                    <span className="font-mono text-slate-300">{w.evidence}</span>
                  </div>
                  <div>
                    <strong className="text-cyan-400">Remediation: </strong>
                    <span className="text-slate-300">{w.remediation}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Call to Action: Growth Strategy */}
      <div className="p-6 bg-gradient-to-r from-slate-900 via-cyan-950/40 to-slate-900 border border-cyan-700/50 rounded-2xl shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h4 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            Ready to execute the Perfect Growth Strategy?
          </h4>
          <p className="text-xs text-slate-400 max-w-xl">
            We have generated a prioritized action roadmap categorized into <strong>Now</strong>, <strong>Next</strong>, <strong>Later</strong>, and <strong>Experiments</strong>, complete with Opportunity Scores, Pros & Cons, and exact Validation Tests.
          </p>
        </div>
        <button
          onClick={onOpenRoadmap}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-cyan-500/20 transition whitespace-nowrap"
        >
          View Growth Strategy Roadmap →
        </button>
      </div>
    </div>
  );
};
