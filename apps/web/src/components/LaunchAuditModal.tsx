import { Project } from '../types';
import { apiUrl } from '../lib/api';
import { X, Play, ShieldAlert, Sparkles } from 'lucide-react';

interface Props {
  project: Project;
  isOpen: boolean;
  onClose: () => void;
  onLaunched: (auditId: string) => void;
}

export const LaunchAuditModal: React.FC<Props> = ({ project, isOpen, onClose, onLaunched }) => {
  const [crawlMode, setCrawlMode] = useState<'quick' | 'standard' | 'deep'>('quick');
  const [maxUrls, setMaxUrls] = useState<number>(50);
  const [respectRobots, setRespectRobots] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch(apiUrl(`/api/v1/projects/${project.id}/audits`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crawl_mode: crawlMode,
          max_urls: maxUrls,
          respect_robots: respectRobots,
        }),
      });
      const data = await res.json();
      if (data.data?.audit_id) {
        onLaunched(data.data.audit_id);
        onClose();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Launch SearchSignal Audit</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 text-sm text-slate-300">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Target Project & Root URL
            </label>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-white font-mono text-xs">
              {project.name} ({project.root_url})
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Crawl Mode
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'quick', label: 'Quick Audit', urls: 50, desc: 'Homepage + key links' },
                { id: 'standard', label: 'Standard Audit', urls: 200, desc: 'Sitemap sample crawl' },
                { id: 'deep', label: 'Deep Audit', urls: 500, desc: 'Exhaustive BFS analysis' },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => {
                    setCrawlMode(m.id as any);
                    setMaxUrls(m.urls);
                  }}
                  className={`p-3 rounded-xl border text-left transition ${
                    crawlMode === m.id
                      ? 'bg-cyan-950/60 border-cyan-500 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <span className="font-bold block text-xs mb-0.5">{m.label}</span>
                  <span className="text-[11px] opacity-70 block">{m.urls} URLs</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Maximum Crawl URL Cap
            </label>
            <input
              type="number"
              value={maxUrls}
              onChange={(e) => setMaxUrls(parseInt(e.target.value) || 10)}
              min={5}
              max={1000}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="pt-2 border-t border-slate-800">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <span className="text-xs font-bold text-white block">Respect robots.txt</span>
                <span className="text-[11px] text-slate-400">Enforce RFC 9309 crawler exclusion rules</span>
              </div>
              <input
                type="checkbox"
                checked={respectRobots}
                onChange={(e) => setRespectRobots(e.target.checked)}
                className="w-4 h-4 rounded text-cyan-500 bg-slate-950 border-slate-700 focus:ring-cyan-500"
              />
            </label>
            {!respectRobots && (
              <div className="mt-2 p-2 bg-amber-950/40 border border-amber-900/60 rounded text-[11px] text-amber-300 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Robots exclusion rules are being ignored for this audit.</span>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800 bg-slate-950/70">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
          >
            Cancel
          </button>
          <button
            onClick={handleLaunch}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 rounded-xl font-bold text-xs tracking-wide transition shadow-lg shadow-cyan-500/20"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {loading ? 'Starting...' : 'Start Audit'}
          </button>
        </div>
      </div>
    </div>
  );
};
