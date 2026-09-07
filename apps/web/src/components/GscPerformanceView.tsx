import React, { useState } from 'react';
import { GscPerformanceData } from '../types';
import { Search, MousePointerClick, Eye, TrendingUp, BarChart2, CheckCircle2, AlertTriangle, XCircle, FileText, ArrowUpDown } from 'lucide-react';

interface Props {
  gsc: GscPerformanceData;
  domain: string;
}

export const GscPerformanceView: React.FC<Props> = ({ gsc, domain }) => {
  const [queryFilter, setQueryFilter] = useState('');
  const [activeTab, setActiveTab] = useState<'queries' | 'coverage' | 'vitals'>('queries');

  const filteredQueries = gsc.queries.filter((q) =>
    q.query.toLowerCase().includes(queryFilter.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* GSC Brand Header & 4 Key Cards */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-900/90 border border-slate-800 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
            <Search className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">Google Search Console Performance</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950 text-blue-400 border border-blue-800">
                Web Search • Last 28 Days
              </span>
            </div>
            <p className="text-xs text-slate-400">Deterministic clicks, impressions, CTR, and SERP positions for {domain}</p>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex gap-1.5 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('queries')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'queries' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Queries ({gsc.queries.length})
          </button>
          <button
            onClick={() => setActiveTab('coverage')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'coverage' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Pages & Indexing
          </button>
          <button
            onClick={() => setActiveTab('vitals')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'vitals' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Core Web Vitals
          </button>
        </div>
      </div>

      {/* 4 GSC Core Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/70 border border-slate-800/80 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Total Clicks</span>
            <MousePointerClick className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-black text-white">{gsc.totalClicks.toLocaleString()}</div>
          <div className="mt-2 text-[11px] text-emerald-400 font-medium flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> +12.4% vs prev 28 days
          </div>
        </div>

        <div className="p-5 bg-slate-900/70 border border-slate-800/80 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Total Impressions</span>
            <Eye className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-black text-white">{gsc.totalImpressions.toLocaleString()}</div>
          <div className="mt-2 text-[11px] text-emerald-400 font-medium flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> +8.1% vs prev 28 days
          </div>
        </div>

        <div className="p-5 bg-slate-900/70 border border-slate-800/80 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Average CTR</span>
            <BarChart2 className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-black text-white">{gsc.avgCtr}%</div>
          <div className="mt-2 text-[11px] text-slate-400">
            Industry avg for top 10: 2.8% - 4.5%
          </div>
        </div>

        <div className="p-5 bg-slate-900/70 border border-slate-800/80 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold uppercase tracking-wider">Average Position</span>
            <ArrowUpDown className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-amber-400">{gsc.avgPosition}</div>
          <div className="mt-2 text-[11px] text-slate-400">
            Across all active search impressions
          </div>
        </div>
      </div>

      {/* 28-Day Mini Chart / Sparkline Bar */}
      <div className="p-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Daily Clicks Velocity (Past 28 Days)
          </span>
          <span className="text-[11px] text-slate-500 font-mono">Normalized Clicks Trend</span>
        </div>
        <div className="flex items-end gap-1.5 h-20 pt-4 border-b border-slate-800">
          {gsc.trend.map((t, idx) => {
            const maxClicks = Math.max(...gsc.trend.map((x) => x.clicks));
            const pct = Math.max(12, Math.round((t.clicks / maxClicks) * 100));
            return (
              <div key={idx} className="flex-1 flex flex-col items-center group relative">
                <div
                  style={{ height: `${pct}%` }}
                  className="w-full bg-blue-500/60 group-hover:bg-blue-400 rounded-t transition-all duration-150"
                />
                <div className="hidden group-hover:block absolute bottom-full mb-2 z-20 px-2 py-1 bg-slate-950 border border-slate-700 rounded text-[10px] text-white whitespace-nowrap shadow-xl">
                  <div className="font-bold">{t.date}</div>
                  <div>{t.clicks} clicks • {t.impressions} impr.</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* TAB 1: TOP QUERIES TABLE */}
      {activeTab === 'queries' && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="relative w-full max-w-sm">
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter search queries..."
                value={queryFilter}
                onChange={(e) => setQueryFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <span className="text-xs text-slate-400">
              Showing {filteredQueries.length} top organic queries
            </span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-800">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Search Query</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Search Intent</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Clicks</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Impressions</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">CTR</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Position</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40 font-mono">
                {filteredQueries.map((q, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium">{q.query}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold ${
                          q.intent === 'Navigational'
                            ? 'bg-blue-950 text-blue-300 border border-blue-800'
                            : q.intent === 'Commercial'
                            ? 'bg-purple-950 text-purple-300 border border-purple-800'
                            : q.intent === 'Transactional'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : 'bg-slate-800 text-slate-300 border border-slate-700'
                        }`}
                      >
                        {q.intent}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-white font-bold">{q.clicks.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-slate-300">{q.impressions.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-cyan-400 font-semibold">{q.ctr}%</td>
                    <td className="py-3 px-4 text-right">
                      <span
                        className={`px-2 py-0.5 rounded font-bold ${
                          q.position <= 3
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                            : q.position <= 10
                            ? 'bg-blue-950/80 text-blue-400 border border-blue-800'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        #{q.position}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: PAGE INDEXING & SITEMAP COVERAGE */}
      {activeTab === 'coverage' && (
        <div className="space-y-6">
          {/* Index summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h4 className="font-bold text-white text-sm">Indexed & Serving on Google</h4>
              </div>
              <div className="text-4xl font-black text-emerald-400 font-mono mb-2">
                {gsc.coverage.validIndexed}
              </div>
              <p className="text-xs text-slate-400">
                These URLs are in Google’s index and can appear in Search results.
              </p>
            </div>

            <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-5 h-5 text-blue-400" />
                <h4 className="font-bold text-white text-sm">Primary XML Sitemap Status</h4>
              </div>
              <div className="text-xs space-y-1.5 text-slate-300 font-mono">
                <div><span className="text-slate-500">Sitemap URL:</span> {gsc.coverage.sitemapStatus.url}</div>
                <div><span className="text-slate-500">Submitted URLs:</span> {gsc.coverage.sitemapStatus.submitted}</div>
                <div><span className="text-slate-500">Discovered & Indexed:</span> {gsc.coverage.sitemapStatus.indexed}</div>
                <div><span className="text-slate-500">Last Read by Googlebot:</span> {new Date(gsc.coverage.sitemapStatus.lastRead).toLocaleString()}</div>
                <div className="mt-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    Status: {gsc.coverage.sitemapStatus.status}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Excluded Reasons Table */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl space-y-4">
            <h4 className="font-bold text-white text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Why Pages Aren't Indexed (Googlebot Crawl Reasons)
            </h4>
            <div className="overflow-x-auto rounded-xl border border-slate-800">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-800 text-slate-400">
                    <th className="py-3 px-4 font-semibold">Reason</th>
                    <th className="py-3 px-4 font-semibold text-center">Impact Severity</th>
                    <th className="py-3 px-4 font-semibold text-right">Affected Pages</th>
                    <th className="py-3 px-4 font-semibold">Sample URL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {gsc.coverage.excludedReasons.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/30">
                      <td className="py-3 px-4 font-sans font-medium text-slate-200">{item.reason}</td>
                      <td className="py-3 px-4 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-sans font-bold uppercase ${
                            item.severity === 'high'
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : item.severity === 'medium'
                              ? 'bg-amber-950 text-amber-400 border border-amber-800'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {item.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-white">{item.count}</td>
                      <td className="py-3 px-4 text-slate-400 truncate max-w-xs">{item.sampleUrl || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: CORE WEB VITALS */}
      {activeTab === 'vitals' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
            <span className="text-xs font-semibold text-slate-400 block mb-1">Largest Contentful Paint (LCP)</span>
            <div className="text-3xl font-black text-white font-mono my-2">{gsc.coreWebVitals.lcp.value}</div>
            <span
              className={`px-2.5 py-1 rounded text-xs font-bold ${
                gsc.coreWebVitals.lcp.status === 'good'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              Status: {gsc.coreWebVitals.lcp.status.toUpperCase()}
            </span>
            <p className="mt-3 text-xs text-slate-400">Target: &lt; 2.5s for fast user experience</p>
          </div>

          <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
            <span className="text-xs font-semibold text-slate-400 block mb-1">Interaction to Next Paint (INP)</span>
            <div className="text-3xl font-black text-white font-mono my-2">{gsc.coreWebVitals.inp.value}</div>
            <span
              className={`px-2.5 py-1 rounded text-xs font-bold ${
                gsc.coreWebVitals.inp.status === 'good'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              Status: {gsc.coreWebVitals.inp.status.toUpperCase()}
            </span>
            <p className="mt-3 text-xs text-slate-400">Target: &lt; 200ms responsive input handling</p>
          </div>

          <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl">
            <span className="text-xs font-semibold text-slate-400 block mb-1">Cumulative Layout Shift (CLS)</span>
            <div className="text-3xl font-black text-white font-mono my-2">{gsc.coreWebVitals.cls.value}</div>
            <span
              className={`px-2.5 py-1 rounded text-xs font-bold ${
                gsc.coreWebVitals.cls.status === 'good'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              Status: {gsc.coreWebVitals.cls.status.toUpperCase()}
            </span>
            <p className="mt-3 text-xs text-slate-400">Target: &lt; 0.1 visual stability score</p>
          </div>
        </div>
      )}
    </div>
  );
};
