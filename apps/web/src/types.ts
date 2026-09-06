export type EvidenceClass =
  | 'EXACT'
  | 'DERIVED'
  | 'VALIDATED'
  | 'OBSERVED'
  | 'HEURISTIC'
  | 'PREDICTIVE'
  | 'UNKNOWN';

export type Severity = 'blocker' | 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  root_url: string;
  status: string;
  crawl_config: Record<string, any>;
  created_at: string;
}

export interface Audit {
  id: string;
  project_id: string;
  project_name?: string;
  root_url?: string;
  status: string; // queued, discovering, crawling, validating, scoring, completed, failed
  crawl_mode: string;
  started_at: string | null;
  completed_at: string | null;
  progress_pages: number;
  engine_version: string;
  config?: Record<string, any>;
}

export interface ScoreItem {
  dimension: string;
  score: number;
  confidence: number;
  evidence_class: EvidenceClass;
  methodology_version: string;
  inputs?: Record<string, any>;
}

export interface Finding {
  id: string;
  rule_id: string;
  url: string;
  severity: Severity;
  evidence_class: EvidenceClass;
  status: string;
  confidence: number;
  fingerprint: string;
  evidence: Record<string, any>;
  created_at: string;
}

export interface FindingDetail extends Finding {
  finding_id: string;
  headers?: {
    headers: Record<string, string>;
    url: string;
  };
  html_snapshot?: string;
  observed_at: string;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: string;
  priority_group: 'now' | 'next' | 'later' | 'experiments';
  priority: number;
  opportunity_score: number;
  estimated_effort: string;
  pros: string[];
  cons: string[];
  validation_method: string;
  evidence: {
    rule_id: string;
    affected_urls_count: number;
    sample_urls: string[];
    evidence_class: EvidenceClass;
    severity: Severity;
    confidence: number;
  };
}

export interface AuditComparison {
  audit_a_id: string;
  audit_b_id: string;
  new_issues_count: number;
  resolved_issues_count: number;
  persisting_issues_count: number;
  new_issues: Array<{ rule_id: string; severity: Severity; evidence_class: EvidenceClass; evidence: any }>;
  resolved_issues: Array<{ rule_id: string; severity: Severity; evidence_class: EvidenceClass; evidence: any }>;
  score_deltas: Record<string, { before: number; current: number; delta: number }>;
  pages_count_delta: number;
}
