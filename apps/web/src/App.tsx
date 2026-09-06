import React, { useState, useEffect } from 'react';
import { Project, Audit, ScoreItem, Finding, Recommendation } from './types';
import { ScoreCard } from './components/ScoreCard';
import { EvidenceBadge } from './components/EvidenceBadge';
import { EvidenceModal } from './components/EvidenceModal';
import { RoadmapView } from './components/RoadmapView';
import { ComparisonDiff } from './components/ComparisonDiff';
import { LaunchAuditModal } from './components/LaunchAuditModal';
import { apiUrl } from './lib/api';
import {
  Search,
  SlidersHorizontal,
  RefreshCw,
  Download,
  Plus,
  Compass,
  FileSpreadsheet,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Activity,
} from 'lucide-react';

export const App: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [audits, setAudits] = useState<Audit[]>([]);
  const [currentAudit, setCurrentAudit] = useState<Audit | null>(null);
  const [scores, setScores] = useState<ScoreItem[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [pages, setPages] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState<'findings' | 'roadmap' | 'comparison' | 'pages'>('findings');
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [isLaunchModalOpen, setIsLaunchModalOpen] = useState(false);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [evidenceFilter, setEvidenceFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // 1. Fetch Projects on mount
  useEffect(() => {
    fetch(apiUrl('/api/v1/projects'))
      .then((res) => res.json())
      .then((data) => {
        if (data.data && data.data.length > 0) {
          setProjects(data.data);
          setSelectedProject(data.data[0]);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  // 2. Fetch Audits when project changes
  useEffect(() => {
    if (!selectedProject) return;
    fetch(apiUrl(`/api/v1/projects/${selectedProject.id}/audits`))
      .then((res) => res.json())
      .then((data) => {
        if (data.data && data.data.length > 0) {
          setAudits(data.data);
          setCurrentAudit(data.data[0]);
        } else {
          setAudits([]);
          setCurrentAudit(null);
          setScores([]);
          setFindings([]);
          setRecommendations([]);
        }
      })
      .catch((err) => console.error(err));
  }, [selectedProject]);

  // 3. Fetch Audit Details (Scores, Findings, Recommendations, Pages)
  const refreshAuditData = (auditId: string) => {
    // Scores
    fetch(apiUrl(`/api/v1/audits/${auditId}/scores`))
      .then((res) => res.json())
      .then((data) => data.data && setScores(data.data));

    // Findings
    fetch(apiUrl(`/api/v1/audits/${auditId}/findings`))
      .then((res) => res.json())
      .then((data) => data.data && setFindings(data.data));

    // Recommendations
    fetch(apiUrl(`/api/v1/audits/${auditId}/recommendations`))
      .then((res) => res.json())
      .then((data) => data.data && setRecommendations(data.data));

    // Pages
    fetch(apiUrl(`/api/v1/audits/${auditId}/pages`))
      .then((res) => res.json())
      .then((data) => data.data && setPages(data.data));
  };

  useEffect(() => {
    if (!currentAudit) return;
    refreshAuditData(currentAudit.id);

    // Auto-poll if audit is currently in progress
    if (['queued', 'crawling', 'validating', 'scoring', 'strategizing'].includes(currentAudit.status)) {
      const interval = setInterval(() => {
        fetch(apiUrl(`/api/v1/audits/${currentAudit.id}`))
          .then((res) => res.json())
          .then((data) => {
            if (data.data) {
              setCurrentAudit(data.data);
              if (data.data.status === 'completed') {
                refreshAuditData(data.data.id);
              }
            }
          });
      }, 2500);
      return () => clearInterval(interval);
    }
  }, [currentAudit?.id, currentAudit?.status]);

  // Filtered Findings
  const filteredFindings = findings.filter((f) => {
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20">
                <Compass className="w-5 h-5 text-slate-950 stroke-[2.5]" />
              </div>
              <span className="text-lg font-extrabold tracking-tight text-white">SearchSignal</span>
            </div>
            <span className="text-slate-600">/</span>

            {/* Project Switcher */}
            {projects.length > 0 && (
              <select
                value={selectedProject?.id}
                onChange={(e) => {
                  const p = projects.find((proj) => proj.id === e.target.value);
                  if (p) setSelectedProject(p);
                }}
                className="bg-slate-900 border border-slate-700/80 text-xs font-semibold rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.root_url})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="flex items-center gap-3">
            {currentAudit && (
              <div className="hidden md:flex items-center gap-2">
                <a
                  href={apiUrl(`/api/v1/audits/${currentAudit.id}/report/json`)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-lg text-xs font-medium text-slate-300 flex items-center gap-1.5 transition"
                >
                  <Download className="w-3.5 h-3.5 text-slate-400" />
                  JSON Report
                </a>
                <a
                  href={apiUrl(`/api/v1/audits/${currentAudit.id}/report/csv`)}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-lg text-xs font-medium text-slate-300 flex items-center gap-1.5 transition"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5 text-slate-400" />
                  CSV Export
                </a>
              </div>
            )}

            {selectedProject && (
              <button
                onClick={() => setIsLaunchModalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-cyan-500/20 transition"
              >
                <Plus className="w-4 h-4 stroke-[3]" />
                Launch New Audit
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-1 space-y-8">
        {/* Project & Audit Meta Header (Spec Section 4) */}
        {currentAudit ? (
          <div className="p-6 bg-slate-900/70 border border-slate-800/80 rounded-2xl shadow-xl flex flex-wrap items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-2xl font-black text-white tracking-tight">{selectedProject?.name}</h1>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                    currentAudit.status === 'completed'
                      ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800'
                      : 'bg-cyan-950/60 text-cyan-400 border border-cyan-800 animate-pulse'
                  }`}
                >
                  {currentAudit.status}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                <span>Target:</span>
                <a
                  href={selectedProject?.root_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline flex items-center gap-1 font-sans font-medium"
                >
                  {selectedProject?.root_url}
                  <ExternalLink className="w-3 h-3 inline" />
                </a>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs text-slate-300">
              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <span className="text-slate-500 block uppercase text-[10px] font-bold">Last Audit Run</span>
                <span className="font-semibold text-white">
                  {currentAudit.started_at ? new Date(currentAudit.started_at).toLocaleString() : 'Pending'}
                </span>
              </div>
              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <span className="text-slate-500 block uppercase text-[10px] font-bold">Pages Crawled</span>
                <span className="font-semibold text-white">{pages.length || currentAudit.progress_pages} URLs</span>
              </div>
              <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl">
                <span className="text-slate-500 block uppercase text-[10px] font-bold">Audit Engine</span>
                <span className="font-semibold text-cyan-400 font-mono">v{currentAudit.engine_version}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
            <Activity className="w-12 h-12 text-cyan-500 mx-auto mb-3" />
            <h2 className="text-xl font-bold text-white mb-1">No Audit Completed Yet</h2>
            <p className="text-sm text-slate-400 max-w-md mx-auto mb-6">
              Launch a Quick Audit to crawl and evaluate your website against deterministic SEO rules and transparent GEO & AEO readiness heuristics.
            </p>
            {selectedProject && (
              <button
                onClick={() => setIsLaunchModalOpen(true)}
                className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs uppercase tracking-wider transition"
              >
                Launch First Audit
              </button>
            )}
          </div>
        )}

        {/* 7 Score Cards Grid (Spec Section 4 & 33) */}
        {scores.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                Intelligence & Readiness Score Cards
              </h2>
              <span className="text-xs text-slate-400">
                Central Principle: <strong className="text-slate-200">Never present a heuristic as an observed fact.</strong>
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {scores.map((sc) => (
                <ScoreCard key={sc.dimension} score={sc} />
              ))}
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        {currentAudit && (
          <div className="space-y-6">
            <div className="flex border-b border-slate-800 gap-6">
              {[
                { id: 'findings', label: `Technical Findings (${findings.length})` },
                { id: 'roadmap', label: `Growth Roadmap (${recommendations.length})` },
                { id: 'comparison', label: 'Audit Comparison Diff' },
                { id: 'pages', label: `Crawled URLs Graph (${pages.length})` },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id as any)}
                  className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition ${
                    activeTab === t.id
                      ? 'border-cyan-400 text-cyan-400'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* TAB 1: FINDINGS EXPLORER */}
            {activeTab === 'findings' && (
              <div className="space-y-4">
                {/* Search & Filter Bar */}
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-2 flex-1 max-w-md">
                    <Search className="w-4 h-4 text-slate-500" />
                    <input
                      type="text"
                      placeholder="Search by rule ID, affected URL, or finding evidence..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="bg-transparent border-none text-xs text-white placeholder-slate-500 focus:outline-none w-full"
                    />
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    {/* Severity Filter */}
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
                        <option value="info">Info</option>
                      </select>
                    </div>

                    {/* Evidence Class Filter */}
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className="text-slate-500 font-semibold">Evidence Class:</span>
                      <select
                        value={evidenceFilter}
                        onChange={(e) => setEvidenceFilter(e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-slate-300 rounded px-2.5 py-1 text-xs focus:outline-none"
                      >
                        <option value="all">All Evidence Classes</option>
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
                        <th className="py-3.5 px-4">Affected URL</th>
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
                                f.severity === 'blocker' || f.severity === 'critical'
                                  ? 'bg-rose-950/80 text-rose-400'
                                  : f.severity === 'high'
                                  ? 'bg-amber-950/80 text-amber-400'
                                  : 'bg-slate-800 text-slate-300'
                              }`}
                            >
                              {f.severity}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 max-w-xs truncate font-mono text-slate-300" title={f.url}>
                            {f.url}
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

            {/* TAB 2: ROADMAP */}
            {activeTab === 'roadmap' && <RoadmapView recommendations={recommendations} />}

            {/* TAB 3: COMPARISON */}
            {activeTab === 'comparison' && (
              <ComparisonDiff currentAuditId={currentAudit.id} audits={audits} />
            )}

            {/* TAB 4: PAGES */}
            {activeTab === 'pages' && (
              <div className="overflow-x-auto bg-slate-900 border border-slate-800 rounded-xl">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-bold">
                    <tr>
                      <th className="py-3.5 px-4">Status</th>
                      <th className="py-3.5 px-4">URL</th>
                      <th className="py-3.5 px-4">Title</th>
                      <th className="py-3.5 px-4">Words</th>
                      <th className="py-3.5 px-4">Depth</th>
                      <th className="py-3.5 px-4">Response Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {pages.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3.5 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                              p.http_status === 200
                                ? 'bg-emerald-950/80 text-emerald-400'
                                : 'bg-rose-950/80 text-rose-400'
                            }`}
                          >
                            {p.http_status || 'ERR'}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 max-w-sm truncate text-white">{p.url}</td>
                        <td className="py-3.5 px-4 max-w-xs truncate text-slate-400 font-sans">{p.title || '—'}</td>
                        <td className="py-3.5 px-4">{p.word_count}</td>
                        <td className="py-3.5 px-4">{p.depth}</td>
                        <td className="py-3.5 px-4">{p.response_time_ms}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Modals */}
      {selectedFinding && currentAudit && (
        <EvidenceModal
          auditId={currentAudit.id}
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
        />
      )}

      {selectedProject && (
        <LaunchAuditModal
          project={selectedProject}
          isOpen={isLaunchModalOpen}
          onClose={() => setIsLaunchModalOpen(false)}
          onLaunched={(auditId) => {
            fetch(apiUrl(`/api/v1/audits/${auditId}`))
              .then((res) => res.json())
              .then((data) => {
                if (data.data) {
                  setAudits((prev) => [data.data, ...prev]);
                  setCurrentAudit(data.data);
                }
              });
          }}
        />
      )}
    </div>
  );
};
export default App;
