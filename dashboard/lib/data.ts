import fs from "fs";
import path from "path";

const BRAIN_ROOT = path.resolve(process.cwd(), "..");

export interface Hypothesis {
  id: string;
  claim: string;
  type: string;
  confidence: number;
  evidence_for: string[];
  evidence_against: string[];
  test: string;
  test_metric: string;
  test_threshold: string;
  tests_run: TestResult[];
  tests_remaining: string[];
  status: string;
  parent: string | null;
  created: string;
  last_tested: string | null;
  reasoning: string;
}

export interface TestResult {
  date: string;
  test: string;
  score: number;
  passed: boolean | null;
  details: string;
  confidence_change: string;
}

export interface Belief {
  belief: string;
  confidence: number | string;
  source: string;
  date: string;
  evidence?: string;
  last_scored?: string;
}

export interface ScoreRecord {
  date: string;
  hypotheses_scored: number;
  progress: {
    total_hypotheses: number;
    active: number;
    eliminated: number;
    high_confidence: number;
    high_confidence_ids: string[];
    eliminated_this_cycle: number;
    surprise: number;
    progress_summary: string;
  };
  scored_hypotheses: {
    id: string;
    claim: string;
    confidence: number;
    status: string;
    test_result: TestResult | null;
  }[];
  belief_count_before: number;
  belief_count_after: number;
}

export interface Stats {
  computed_at: string;
  source: string;
  summary: {
    total_folios: number;
    total_words: number;
    unique_words: number;
    total_glyphs: number;
    unique_glyphs: number;
    avg_word_length: number;
    hapax_legomena: number;
    dis_legomena: number;
    hapax_ratio: number;
  };
  entropy: {
    glyph_entropy_overall: number;
    word_entropy_overall: number;
    by_section: Record<string, { glyph_entropy: number; word_entropy: number; word_count: number; unique_words: number }>;
    by_language: Record<string, { glyph_entropy: number; word_entropy: number; word_count: number; unique_words: number }>;
  };
  zipf: {
    exponent: number;
    r_squared: number;
    interpretation: string;
  };
  word_frequency: {
    top_50: Record<string, number>;
    length_distribution: Record<string, number>;
  };
  glyph_frequency: {
    overall: Record<string, number>;
    positional: Record<string, Record<string, number>>;
  };
  ngrams: {
    top_30_bigrams: Record<string, number>;
    top_30_trigrams: Record<string, number>;
  };
  sections: Record<string, { folio_count: number; word_count: number; unique_words: number; avg_word_length: number }>;
  languages: Record<string, { folio_count: number; word_count: number; unique_words: number }>;
}

function readJson<T>(filePath: string): T | null {
  const full = path.join(BRAIN_ROOT, filePath);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf-8")) as T;
}

function readJsonDir<T>(dirPath: string): T[] {
  const full = path.join(BRAIN_ROOT, dirPath);
  if (!fs.existsSync(full)) return [];
  return fs
    .readdirSync(full)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => JSON.parse(fs.readFileSync(path.join(full, f), "utf-8")) as T);
}

export function getHypotheses(): Hypothesis[] {
  return readJsonDir<Hypothesis>("hypotheses");
}

export function getBeliefs(): Belief[] {
  return readJson<Belief[]>("scripts/beliefs.json") ?? [];
}

export function getScores(): ScoreRecord[] {
  return readJsonDir<ScoreRecord>("outputs/scores");
}

export function getStats(): Stats | null {
  return readJson<Stats>("raw/perception/voynich-stats.json");
}

export function getFailedApproaches(): Hypothesis[] {
  return readJsonDir<Hypothesis>("hypotheses").filter(
    (h) => h.status === "eliminated"
  );
}

export function getActiveHypotheses(): Hypothesis[] {
  return readJsonDir<Hypothesis>("hypotheses")
    .filter((h) => h.status === "active")
    .sort((a, b) => b.confidence - a.confidence);
}

export function getLogContent(): string {
  const full = path.join(BRAIN_ROOT, "wiki/LOG.md");
  if (!fs.existsSync(full)) return "";
  return fs.readFileSync(full, "utf-8");
}
