export type RiskLevel = "고위험" | "중위험" | "저위험";

export interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  salary?: string;
  url?: string;
  posted_date?: string;
  source_site: string;
  crawled_at: string;
}

export interface KeywordMatch {
  id: number;
  job_id: number;
  keyword: string;
  tier: number;
  category: string;
  weight: number;
  positions?: string;
}

export interface PatternMatch {
  id: number;
  job_id: number;
  pattern_name: string;
  keywords: string;
  score: number;
}

export interface RiskAnalysis {
  id: number;
  job_id: number;
  base_score: number;
  combo_multiplier: number;
  final_score: number;
  risk_level: RiskLevel;
  risk_factors?: string;
  recommendations?: string;
  analysis_summary?: string;
}

export interface JobDetail extends Job {
  keyword_matches: KeywordMatch[];
  pattern_matches: PatternMatch[];
  risk_analysis: RiskAnalysis;
}
