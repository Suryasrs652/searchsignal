import React, { useState, useEffect } from 'react';
import { ScoreCard } from './components/ScoreCard';
import { EvidenceBadge } from './components/EvidenceBadge';
import { EvidenceModal } from './components/EvidenceModal';
import { RoadmapView } from './components/RoadmapView';
import { ComparisonDiff } from './components/ComparisonDiff';
import { ExecutiveReportView } from './components/ExecutiveReportView';
import { generateWebsiteAudit, AuditAnalysisReport } from './lib/auditEngine';
import { Finding, Audit } from './types';
import {
  Search,
  Compass,
  Download,
  Printer,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  Zap,
  Globe,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

export const App: React.FC = () => {
  const [inputUrl, setInputUrl] = useState<string>('https://example.com');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [scanStep, setScanStep] = useState<string>('');
  const [report, setReport] = useState<AuditAnalysisReport>(() => generateWebsiteAudit('https://example.com'));

  // Active Main Tab: 'executive' (Strengths & Weaknesses), 'roadmap' (Growth Strategy), 'findings' (Technical Explorer), 'comparison'
  const [activeTab, setActiveTab] = useState<'executive' | 'roadmap' | 'findings' | 'comparison'>('executive');
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  // Filters for findings tab
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [evidenceFilter, setEvidenceFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // History of audits for comparison
  const [auditHistory, setAuditHistory] = useState<Audit[]>([
    {
      id: 'audit-prev-benchmark',
      project_id: 'proj-1',
      status: 'completed',
      crawl_mode: 'quick',
      started_at: '2026-08-28T10:00:00Z',
      completed_at: '2026-08-28T10:02:15Z',
      progress_pages: 42,
      engine_version: '4.1.0',
    },
    {
      id: 'audit-current',
      project_id: 'proj-1',
      status: 'completed',
      crawl_mode: 'quick',
      started_at: '2026-09-06T15:40:00Z',
      completed_at: '2026-09-06T15:42:10Z',
      progress_pages: 48,
      engine_version: '4.2.0',
    },
  ]);

  const handleAnalyze = (targetUrlToScan?: string) => {
    const urlToUse = targetUrlToScan || inputUrl;
    if (!urlToUse.trim()) return;

    setIsAnalyzing(true);
    const steps = [
      'Validating SSL security & DNS baseline...',
      'Crawling DOM & evaluating Technical SEO rules...',
      'Measuring Time to First Byte (TTFB) & Page Speed...',
      'Analyzing AEO direct question coverage & answer candidate passages...',
      'Evaluating GEO Generative AI source quality & factual density...',
      'Synthesizing Strengths, Weaknesses, and Perfect Growth Strategy...',
    ];

    let currentStepIdx = 0;
    setScanStep(steps[0]);

    const stepInterval = setInterval(() => {
      currentStepIdx++;
      if (currentStepIdx < steps.length) {
        setScanStep(steps[currentStepIdx]);
      } else {
        clearInterval(stepInterval);
        const newReport = generateWebsiteAudit(urlToUse);
        setReport(newReport);
        setIsAnalyzing(false);

        // Add to comparison history
        const newAuditRecord: Audit = {
          id: `audit-${Date.now().toString().slice(-6)}`,
          project_id: 'proj-1',
          status: 'completed',
          crawl_mode: 'quick',
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          progress_pages: 48,
          engine_version: '4.2.0',
        };
        setAuditHistory((prev) => [newAuditRecord, ...prev]);
      }
    }, 280);
  };

  // Filtered findings
  const filteredFindings = report.findings.filter((f) => {
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false;
    if (evidenceFilter !== 'all' && f.evidence_class !== evidenceFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        f.rule_id.toLowerCase().includes(q) ||
        f.url.toLowerCase().includes(q) ||
        JSON.stringify(f.evidence).toLowerCase().includes(q)
      );
    }
    return true;
  });

  const exportJsonReport = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(report, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute('href', dataStr);
    dlAnchorElem.setAttribute('download', `searchsignal_audit_${report.domain}.json`);
    dlAnchorElem.click();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Compass className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-lg font-extrabold tracking-tight text-white block leading-none">SearchSignal</span>
              <span className="text-[10px] text-slate-400 font-mono">SEO • AEO • GEO Growth Platform</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={exportJsonReport}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-lg text-xs font-medium text-slate-300 flex items-center gap-1.5 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              Export JSON
            </button>
            <button
              onClick={() => window.print()}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-lg text-xs font-medium text-slate-300 flex items-center gap-1.5 transition"
            >
              <Printer className="w-3.5 h-3.5 text-slate-400" />
              Print Report
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-1 space-y-8">
        {/* HERO ANALYZER INPUT BAR (User's primary action) */}
        <div className="relative p-6 sm:p-8 bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800/80 rounded-2xl shadow-2xl overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="max-w-3xl space-y-2 mb-6">
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Website Audit & Growth Intelligence
            </h1>
            <p className="text-sm text-slate-400">
              Paste your website link below to immediately audit, score, and uncover your site's <strong>Strengths</strong>, <strong>Weaknesses</strong>, and <strong>Perfect Growth Strategy</strong> across SEO, AEO, GEO, Page Speed, and Backlinks.
            </p>
          </div>

          {/* URL Input Bar Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAnalyze();
            }}
            className="flex flex-col sm:flex-row gap-3 max-w-4xl"
          >
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <Globe className="w-5 h-5 text-cyan-400" />
              </div>
              <input
                type="text"
                value={inputUrl}
                onChange={(e) => setInputUrl(e.target.value)}
                placeholder="Paste website link (e.g. https://yourwebsite.com or domain.com)"
                className="w-full pl-11 pr-4 py-3.5 bg-slate-950/90 border-2 border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono transition shadow-inner"
              />
            </div>
            <button
              type="submit"
              disabled={isAnalyzing}
              className="px-8 py-3.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-slate-950 font-black text-sm rounded-xl shadow-lg shadow-cyan-500/25 transition flex items-center justify-center gap-2 whitespace-nowrap"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 fill-current" />
                  Analyze Website
                </>
              )}
            </button>
          </form>

          {/* Quick Preset Samples */}
          <div className="flex flex-wrap items-center gap-2 mt-4 text-xs text-slate-400">
            <span className="font-semibold text-slate-500">Try quick demo:</span>
            {['https://example.com', 'https://shopify.com', 'https://github.com', 'https://wikipedia.org'].map((sample) => (
              <button
                key={sample}
                type="button"
                onClick={() => {
                  setInputUrl(sample);
                  handleAnalyze(sample);
                }}
                className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-lg text-slate-300 font-mono transition"
              >
                {sample.replace('https://', '')}
              </button>
            ))}
          </div>

          {/* Scanning Progress Overlay */}
          {isAnalyzing && (
            <div className="mt-6 p-4 bg-cyan-950/40 border border-cyan-800/60 rounded-xl flex items-center gap-3 text-cyan-300 text-xs font-semibold animate-pulse">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
              <span>{scanStep}</span>
            </div>
          )}
        </div>

        {/* CURRENT AUDITED DOMAIN HEADER */}
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <div>
              <span className="text-xs text-slate-500 block uppercase font-bold tracking-wider">Active Analysis Target</span>
              <a
                href={report.url}
                target="_blank"
                rel="noreferrer"
                className="text-base font-bold text-white hover:text-cyan-400 transition flex items-center gap-1.5"
              >
                {report.domain}
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-400">
            <div>
              <span className="text-slate-500 block">Overall Health:</span>
              <span className="text-lg font-black text-cyan-400">{report.scores.overall.score}/100</span>
            </div>
            <div>
              <span className="text-slate-500 block">Audited At:</span>
              <span className="text-slate-200 font-medium">{new Date(report.analyzedAt).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        {/* 5 CORE PILLAR SCORE CARDS (SEO, AEO, GEO, Page Speed, Backlinks) */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              Core Intelligence & Readiness Scores
            </h2>
            <span className="text-xs text-slate-400 hidden sm:inline">
              Principle: <strong className="text-slate-200">Never present a heuristic as an observed fact.</strong>
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <ScoreCard score={report.scores.seo} />
            <ScoreCard score={report.scores.aeo} />
            <ScoreCard score={report.scores.geo} />
            <ScoreCard score={report.scores.pageSpeed} />
            <ScoreCard score={report.scores.backlinks} />
          </div>
        </div>

        {/* DASHBOARD NAVIGATION TABS */}
        <div className="space-y-6">
          <div className="flex border-b border-slate-800 gap-6">
            <button
              onClick={() => setActiveTab('executive')}
              className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition ${
                activeTab === 'executive'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Strengths & Weaknesses Report ({report.strengths.length + report.weaknesses.length})
            </button>
            <button
              onClick={() => setActiveTab('roadmap')}
              className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition ${
                activeTab === 'roadmap'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Perfect Growth Strategy ({report.recommendations.length})
            </button>
            <button
              onClick={() => setActiveTab('findings')}
              className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition ${
                activeTab === 'findings'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Technical Findings Explorer ({report.findings.length})
            </button>
            <button
              onClick={() => setActiveTab('comparison')}
              className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition ${
                activeTab === 'comparison'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Audit Comparison Diff
            </button>
          </div>

          {/* TAB 1: EXECUTIVE REPORT (Strengths & Weaknesses) */}
          {activeTab === 'executive' && (
            <ExecutiveReportView report={report} onOpenRoadmap={() => setActiveTab('roadmap')} />
          )}

          {/* TAB 2: PERFECT GROWTH STRATEGY */}
          {activeTab === 'roadmap' && <RoadmapView recommendations={report.recommendations} />}

          {/* TAB 3: TECHNICAL FINDINGS EXPLORER */}
          {activeTab === 'findings' && (
            <div className="space-y-4">
              {/* Search & Filter Bar */}
              <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-2 flex-1 max-w-md">
                  <Search className="w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search by rule ID or finding evidence..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-transparent border-none text-xs text-white placeholder-slate-500 focus:outline-none w-full"
                  />
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-1.5 text-xs">
                    <span className="text-slate-500 font-semibold">Severity:</span>
                    <select
                      value={severityFilter}
                      onChange={(e) => setSeverityFilter(e.target.value)}
                      className="bg-slate-950 border border-slate-800 text-slate-300 rounded px-2.5 py-1 text-xs focus:outline-none"
                    >
                      <option value="all">All Severities</option>
                      <option value="blocker">Blocker</option>
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs">
                    <span className="text-slate-500 font-semibold">Evidence Class:</span>
                    <select
                      value={evidenceFilter}
                      onChange={(e) => setEvidenceFilter(e.target.value)}
                      className="bg-slate-950 border border-slate-800 text-slate-300 rounded px-2.5 py-1 text-xs focus:outline-none"
                    >
                      <option value="all">All Classes</option>
                      <option value="EXACT">EXACT</option>
                      <option value="DERIVED">DERIVED</option>
                      <option value="VALIDATED">VALIDATED</option>
                      <option value="OBSERVED">OBSERVED</option>
                      <option value="HEURISTIC">HEURISTIC</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Findings Table */}
              <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-xl">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-bold">
                    <tr>
                      <th className="py-3.5 px-4">Rule ID</th>
                      <th className="py-3.5 px-4">Evidence Class</th>
                      <th className="py-3.5 px-4">Severity</th>
                      <th className="py-3.5 px-4">Observed Evidence Snippet</th>
                      <th className="py-3.5 px-4 text-right">Inspection</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {filteredFindings.map((f) => (
                      <tr key={f.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3.5 px-4 font-mono font-bold text-white">{f.rule_id}</td>
                        <td className="py-3.5 px-4">
                          <EvidenceBadge evidenceClass={f.evidence_class} />
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                              f.severity === 'critical' || f.severity === 'blocker'
                                ? 'bg-rose-950/80 text-rose-400'
                                : f.severity === 'high'
                                ? 'bg-amber-950/80 text-amber-400'
                                : 'bg-slate-800 text-slate-300'
                            }`}
                          >
                            {f.severity}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 max-w-sm truncate text-slate-400 font-mono text-[11px]">
                          {JSON.stringify(f.evidence)}
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <button
                            onClick={() => setSelectedFinding(f)}
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 font-semibold rounded text-xs transition"
                          >
                            Inspect Evidence
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: AUDIT COMPARISON */}
          {activeTab === 'comparison' && (
            <ComparisonDiff currentAuditId={auditHistory[0].id} audits={auditHistory} />
          )}
        </div>
      </main>

      {/* Evidence Modal */}
      {selectedFinding && (
        <EvidenceModal
          auditId="audit-active"
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
        />
      )}
    </div>
  );
};

export default App;
