import { Audit, AuditComparison } from '../types';
import { EvidenceBadge } from './EvidenceBadge';
import { apiUrl } from '../lib/api';
import { ArrowUpRight, ArrowDownRight, Minus, CheckCircle, AlertOctagon, GitCompare } from 'lucide-react';

interface Props {
  currentAuditId: string;
  audits: Audit[];
}

export const ComparisonDiff: React.FC<Props> = ({ currentAuditId, audits }) => {
  const otherAudits = audits.filter((a) => a.id !== currentAuditId);
  const [selectedOtherId, setSelectedOtherId] = useState<string>(
    otherAudits.length > 0 ? otherAudits[0].id : ''
  );
  const [diff, setDiff] = useState<AuditComparison | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedOtherId) return;
    setLoading(true);
    fetch(apiUrl(`/api/v1/audits/${selectedOtherId}/compare/${currentAuditId}`))
      .then((res) => res.json())
      .then((data) => {
        if (data.data) {
          setDiff(data.data);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [currentAuditId, selectedOtherId]);

  if (otherAudits.length === 0) {
    return (
      <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl">
        <GitCompare className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-1">No Previous Audit Available</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Run at least two audits for this project to inspect resolved issues, new regressions, and score movement over time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Comparison Selector */}
      <div className="flex items-center justify-between p-4 bg-slate-900 border border-slate-800 rounded-xl">
        <div className="flex items-center gap-3">
          <GitCompare className="w-5 h-5 text-cyan-400" />
          <span className="text-sm font-semibold text-white">Compare Current Audit Against:</span>
        </div>
        <select
          value={selectedOtherId}
          onChange={(e) => setSelectedOtherId(e.target.value)}
          className="bg-slate-950 border border-slate-700 text-sm rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
        >
          {otherAudits.map((a) => (
            <option key={a.id} value={a.id}>
              Audit {a.id.slice(0, 8)} ({a.started_at ? new Date(a.started_at).toLocaleDateString() : 'Draft'}) - {a.crawl_mode}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading audit diff analysis...</div>
      ) : diff ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 bg-emerald-950/40 border border-emerald-800/60 rounded-xl">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 block mb-1">
                Resolved Issues
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-emerald-400">+{diff.resolved_issues_count}</span>
                <span className="text-xs text-slate-400">fixed since previous audit</span>
              </div>
            </div>

            <div className="p-5 bg-rose-950/40 border border-rose-800/60 rounded-xl">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-400 block mb-1">
                New Regressions
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-rose-400">-{diff.new_issues_count}</span>
                <span className="text-xs text-slate-400">new issues detected</span>
              </div>
            </div>

            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                Persisting Fingerprints
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-300">{diff.persisting_issues_count}</span>
                <span className="text-xs text-slate-400">unchanged across audits</span>
              </div>
            </div>
          </div>

          {/* Score Deltas */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Score Movement</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(diff.score_deltas).map(([dimension, values]) => {
                const delta = values.delta;
                const isPositive = delta > 0;
                const isNeutral = delta === 0;

                return (
                  <div key={dimension} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
                    <span className="text-xs text-slate-400 block truncate">{dimension}</span>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-lg font-bold text-white">{values.current}</span>
                      <span
                        className={`text-xs font-semibold flex items-center ${
                          isPositive
                            ? 'text-emerald-400'
                            : isNeutral
                            ? 'text-slate-500'
                            : 'text-rose-400'
                        }`}
                      >
                        {isPositive && <ArrowUpRight className="w-3.5 h-3.5" />}
                        {!isPositive && !isNeutral && <ArrowDownRight className="w-3.5 h-3.5" />}
                        {isNeutral && <Minus className="w-3.5 h-3.5" />}
                        {delta > 0 ? `+${delta}` : delta}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
