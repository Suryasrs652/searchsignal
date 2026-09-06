import { Finding, FindingDetail } from '../types';
import { EvidenceBadge } from './EvidenceBadge';
import { apiUrl } from '../lib/api';
import { X, ExternalLink, Code2, Server, FileText, Check, Copy } from 'lucide-react';

interface Props {
  auditId: string;
  finding: Finding | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<Props> = ({ auditId, finding, onClose }) => {
  const [detail, setDetail] = useState<FindingDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'evidence' | 'headers' | 'html'>('evidence');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!finding) return;
    setLoading(true);
    fetch(apiUrl(`/api/v1/audits/${auditId}/findings/${finding.id}`))
      .then((res) => res.json())
      .then((data) => {
        if (data.data) {
          setDetail(data.data);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [auditId, finding]);

  if (!finding) return null;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs px-2.5 py-1 bg-slate-800 text-slate-300 rounded font-semibold">
              {finding.rule_id}
            </span>
            <EvidenceBadge evidenceClass={finding.evidence_class} />
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                finding.severity === 'blocker' || finding.severity === 'critical'
                  ? 'bg-rose-950 text-rose-400 border border-rose-800'
                  : finding.severity === 'high'
                  ? 'bg-amber-950 text-amber-400 border border-amber-800'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {finding.severity}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Evidence & Remediation Inspector</h2>
            <div className="flex items-center gap-2 text-sm text-slate-400 font-mono break-all">
              <span className="text-slate-500 font-sans">URL:</span>
              <a
                href={finding.url}
                target="_blank"
                rel="noreferrer"
                className="text-cyan-400 hover:underline flex items-center gap-1"
              >
                {finding.url}
                <ExternalLink className="w-3.5 h-3.5 inline" />
              </a>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 gap-6">
            <button
              onClick={() => setActiveTab('evidence')}
              className={`pb-2.5 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'evidence'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code2 className="w-4 h-4" />
              Exact Evidence Observation
            </button>
            <button
              onClick={() => setActiveTab('headers')}
              className={`pb-2.5 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'headers'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Server className="w-4 h-4" />
              HTTP Response Headers
            </button>
            <button
              onClick={() => setActiveTab('html')}
              className={`pb-2.5 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
                activeTab === 'html'
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText className="w-4 h-4" />
              HTML Snapshot
            </button>
          </div>

          {/* Tab Panes */}
          <div className="relative">
            {activeTab === 'evidence' && (
              <div className="space-y-4">
                <div className="relative bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto">
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(finding.evidence, null, 2))}
                    className="absolute top-3 right-3 p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition flex items-center gap-1 text-[11px]"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copied ? 'Copied' : 'Copy'}
                  </button>
                  <pre>{JSON.stringify(finding.evidence, null, 2)}</pre>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
                    <span className="text-slate-400 block mb-1 font-semibold">Evidence Confidence:</span>
                    <span className="text-emerald-400 font-mono text-sm font-bold">
                      {Math.round(finding.confidence * 100)}%
                    </span>
                  </div>
                  <div className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg">
                    <span className="text-slate-400 block mb-1 font-semibold">Fingerprint Hash:</span>
                    <span className="text-slate-300 font-mono text-xs">{finding.fingerprint}</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'headers' && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto">
                {detail?.headers ? (
                  <pre>{JSON.stringify(detail.headers, null, 2)}</pre>
                ) : (
                  <p className="text-slate-500 italic">No headers captured for this entity.</p>
                )}
              </div>
            )}

            {activeTab === 'html' && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-emerald-300 overflow-x-auto max-h-96">
                {detail?.html_snapshot ? (
                  <pre>{detail.html_snapshot}</pre>
                ) : (
                  <p className="text-slate-500 italic">HTML snapshot not stored or not available.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/80 flex justify-between items-center text-xs text-slate-400">
          <span>Observed: {new Date(finding.created_at).toLocaleString()}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
