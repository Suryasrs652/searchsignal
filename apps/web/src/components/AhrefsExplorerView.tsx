import React, { useState } from 'react';
import { AhrefsIntelligenceData } from '../types';
import { Link2, Globe, TrendingUp, Key, Anchor, ExternalLink, ShieldCheck, ArrowUpRight, Filter, DollarSign } from 'lucide-react';

interface Props {
  ahrefs: AhrefsIntelligenceData;
  domain: string;
}

export const AhrefsExplorerView: React.FC<Props> = ({ ahrefs, domain }) => {
  const [activeTab, setActiveTab] = useState<'backlinks' | 'keywords' | 'anchors'>('backlinks');
  const [keywordFilter, setKeywordFilter] = useState('');
  const [linkFilter, setLinkFilter] = useState<'all' | 'dofollow' | 'nofollow'>('all');

  const filteredBacklinks = ahrefs.backlinks.filter((bl) => {
    if (linkFilter !== 'all' && bl.linkType !== linkFilter) return false;
    return true;
  });

  const filteredKeywords = ahrefs.keywords.filter((kw) =>
    kw.keyword.toLowerCase().includes(keywordFilter.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Ahrefs Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-900/90 border border-slate-800 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
            <Link2 className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">Ahrefs Domain & Backlink Intelligence</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800">
                Site Explorer 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">Deep link equity, anchor distribution, and ranking keywords for {domain}</p>
          </div>
        </div>

        {/* Sub-view switcher */}
        <div className="flex gap-1.5 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('backlinks')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'backlinks' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Backlinks ({ahrefs.backlinks.length})
          </button>
          <button
            onClick={() => setActiveTab('keywords')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'keywords' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Organic Keywords ({ahrefs.keywords.length})
          </button>
          <button
            onClick={() => setActiveTab('anchors')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'anchors' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Anchor Text Profile
          </button>
        </div>
      </div>

      {/* Ahrefs 5 Domain Overview Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Domain Rating (DR) */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider">Domain Rating</span>
            <ShieldCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-amber-400 font-mono">DR {ahrefs.domainRating}</div>
          <div className="mt-2 text-[11px] text-slate-500">Logarithmic authority 0-100</div>
        </div>

        {/* URL Rating (UR) */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider">URL Rating</span>
            <Globe className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-black text-cyan-400 font-mono">UR {ahrefs.urlRating}</div>
          <div className="mt-2 text-[11px] text-slate-500">Root page link strength</div>
        </div>

        {/* Referring Domains */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider">Ref. Domains</span>
            <Link2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-black text-white font-mono">{ahrefs.referringDomains.toLocaleString()}</div>
          <div className="mt-2 text-[11px] text-emerald-400 font-medium">
            {ahrefs.dofollowPercent}% dofollow
          </div>
        </div>

        {/* Total Backlinks */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider">Total Backlinks</span>
            <ExternalLink className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-black text-purple-400 font-mono">{ahrefs.totalBacklinks.toLocaleString()}</div>
          <div className="mt-2 text-[11px] text-slate-500">Indexed inbound links</div>
        </div>

        {/* Organic Traffic Value */}
        <div className="p-5 bg-slate-900/80 border border-slate-800 rounded-2xl">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider">Traffic Value</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-black text-emerald-400 font-mono">
            ${(ahrefs.trafficValueUsd).toLocaleString()}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">~{ahrefs.organicTrafficMonthly.toLocaleString()} visits/mo</div>
        </div>
      </div>

      {/* Rank Positions Distribution Bar */}
      <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl space-y-3">
        <div className="flex items-center justify-between text-xs font-bold text-slate-300">
          <span className="uppercase tracking-wider">SERP Positions Distribution</span>
          <span className="text-slate-500 font-mono">Top 100 Keyword Rankings</span>
        </div>
        <div className="grid grid-cols-4 gap-3 text-center">
          <div className="p-3 bg-slate-950/80 rounded-xl border border-emerald-900/40">
            <span className="text-[10px] text-slate-400 block font-semibold">Positions 1 - 3</span>
            <span className="text-xl font-bold text-emerald-400 font-mono">{ahrefs.rankDistribution.top3}</span>
          </div>
          <div className="p-3 bg-slate-950/80 rounded-xl border border-blue-900/40">
            <span className="text-[10px] text-slate-400 block font-semibold">Positions 4 - 10</span>
            <span className="text-xl font-bold text-blue-400 font-mono">{ahrefs.rankDistribution.top10}</span>
          </div>
          <div className="p-3 bg-slate-950/80 rounded-xl border border-amber-900/40">
            <span className="text-[10px] text-slate-400 block font-semibold">Positions 11 - 50</span>
            <span className="text-xl font-bold text-amber-400 font-mono">{ahrefs.rankDistribution.top50}</span>
          </div>
          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 block font-semibold">Positions 51 - 100</span>
            <span className="text-xl font-bold text-slate-300 font-mono">{ahrefs.rankDistribution.top100}</span>
          </div>
        </div>
      </div>

      {/* TAB 1: BACKLINKS EXPLORER */}
      {activeTab === 'backlinks' && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 font-semibold">Filter by Link Type:</span>
              {(['all', 'dofollow', 'nofollow'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setLinkFilter(type)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                    linkFilter === type ? 'bg-amber-500 text-slate-950' : 'bg-slate-900 text-slate-400 border border-slate-800'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
            <span className="text-xs text-slate-400">Showing {filteredBacklinks.length} discovered backlinks</span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-800">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Referring Page</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-center">DR</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Anchor & Target URL</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-center">Type</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">First Seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40 font-mono">
                {filteredBacklinks.map((bl) => (
                  <tr key={bl.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-4 max-w-xs truncate">
                      <div className="font-sans font-bold text-white flex items-center gap-1.5">
                        <Globe className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        {bl.sourceDomain}
                      </div>
                      <a
                        href={bl.sourceUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-slate-400 hover:text-amber-400 transition truncate block"
                      >
                        {bl.sourceUrl}
                      </a>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-900 text-amber-400 border border-slate-800">
                        {bl.sourceDr}
                      </span>
                    </td>
                    <td className="py-3 px-4 max-w-sm">
                      <div className="font-sans font-semibold text-slate-200 flex items-center gap-1">
                        <Anchor className="w-3 h-3 text-amber-400 shrink-0" />
                        "{bl.anchor}"
                      </div>
                      <span className="text-[10px] text-slate-500 block truncate">{bl.targetUrl}</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-sans font-bold uppercase ${
                          bl.linkType === 'dofollow'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {bl.linkType}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-slate-400">{bl.firstSeen}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: ORGANIC KEYWORDS EXPLORER */}
      {activeTab === 'keywords' && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="relative w-full max-w-sm">
              <Key className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter organic keywords..."
                value={keywordFilter}
                onChange={(e) => setKeywordFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
            <span className="text-xs text-slate-400">Showing {filteredKeywords.length} ranking keywords</span>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-800">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Keyword</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-center">SERP Pos.</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-center">KD</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Volume</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">CPC</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Est. Traffic</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40 font-mono">
                {filteredKeywords.map((kw, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 px-4 text-slate-200 font-sans font-medium">
                      {kw.keyword}
                      <span className="text-[10px] text-slate-500 block truncate font-mono">{kw.url}</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded font-bold ${
                          kw.position <= 3
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : kw.position <= 10
                            ? 'bg-blue-950 text-blue-400 border border-blue-800'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        #{kw.position}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                          kw.kd <= 30
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                            : kw.kd <= 60
                            ? 'bg-amber-950/80 text-amber-400 border border-amber-800'
                            : 'bg-rose-950/80 text-rose-400 border border-rose-800'
                        }`}
                      >
                        {kw.kd}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-slate-200">{kw.volume.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right text-emerald-400">${kw.cpc.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-bold text-white">{kw.traffic.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: ANCHOR TEXT PROFILE */}
      {activeTab === 'anchors' && (
        <div className="p-6 bg-slate-900/70 border border-slate-800 rounded-2xl space-y-6">
          <div>
            <h4 className="font-bold text-white text-sm mb-1">Anchor Text Profile & Dispersion</h4>
            <p className="text-xs text-slate-400">
              Natural anchor distributions protect from Google Penguin algorithmic penalties by balancing brand and exact match phrases.
            </p>
          </div>

          {/* Anchor percentages visual bar */}
          <div className="space-y-3">
            {ahrefs.anchors.map((anc, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-200 font-semibold font-mono">"{anc.anchor}"</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">
                      {anc.type}
                    </span>
                    <span className="font-bold text-amber-400">{anc.percentage}%</span>
                    <span className="text-slate-500 text-[11px]">({anc.count} ref. domains)</span>
                  </div>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    style={{ width: `${anc.percentage}%` }}
                    className={`h-full rounded-full ${
                      anc.type === 'brand'
                        ? 'bg-emerald-500'
                        : anc.type === 'exact'
                        ? 'bg-amber-500'
                        : anc.type === 'url'
                        ? 'bg-cyan-500'
                        : 'bg-slate-500'
                    }`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
