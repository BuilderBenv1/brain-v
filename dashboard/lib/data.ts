import fs from "fs";
import path from "path";

// data/ is synced from the parent brain-v directory before each build.
// In dev: run `node scripts/sync-data.js` first, or it falls back to parent dir.
const DATA_DIR = path.resolve(process.cwd(), "data");
const PARENT_DIR = path.resolve(process.cwd(), "..");
const ROOT = fs.existsSync(path.join(DATA_DIR, "beliefs.json"))
  ? DATA_DIR
  : PARENT_DIR;

// Path mappings: data/ has a flat structure, parent dir has nested paths
const HYPOTHESES_DIR = fs.existsSync(path.join(DATA_DIR, "hypotheses"))
  ? path.join(DATA_DIR, "hypotheses")
  : path.join(PARENT_DIR, "hypotheses");

const BELIEFS_PATH = fs.existsSync(path.join(DATA_DIR, "beliefs.json"))
  ? path.join(DATA_DIR, "beliefs.json")
  : path.join(PARENT_DIR, "scripts/beliefs.json");

const STATS_PATH = fs.existsSync(path.join(DATA_DIR, "voynich-stats.json"))
  ? path.join(DATA_DIR, "voynich-stats.json")
  : path.join(PARENT_DIR, "raw/perception/voynich-stats.json");

const SCORES_DIR = fs.existsSync(path.join(DATA_DIR, "scores"))
  ? path.join(DATA_DIR, "scores")
  : path.join(PARENT_DIR, "outputs/scores");

const FAILED_PATH = fs.existsSync(path.join(DATA_DIR, "failed-approaches.json"))
  ? path.join(DATA_DIR, "failed-approaches.json")
  : path.join(PARENT_DIR, "raw/corpus/failed-approaches.json");

const LEXICON_TESTS_PATH = path.join(DATA_DIR, "lexicon-tests.json");

export interface LexiconTestData {
  generated: string;
  description: string;
  lexicons: Array<{
    name: string;
    source: string;
    entries: number;
    coverage: number;
    reported_full_coverage?: number;
    reported_z?: number;
    permutation_z?: number;
    shuffle_in_order_vs_shuffled: {
      match?: number | null;
      conn_content?: number | null;
      both_matched?: number | null;
      conn_frac?: number | null;
      notes?: string;
    };
  }>;
  currier_ab_gap: {
    description: string;
    schechter_latin: number;
    brady_syriac_proxy: number;
    hebrew_medieval: number;
  };
  brady_gallows_confirmed: {
    description: string;
    p_enrichment: number;
    p_predicted: number;
    t_enrichment: number;
    t_predicted: number;
    cth_enrichment: number;
    ckh_enrichment: number;
    cph_enrichment: number;
  };
  verdict: string;
  null_lexicon?: {
    headline: string;
    method: string;
    trials: number;
    lexicon_size: number;
    coverage_mean: number;
    coverage_stdev: number;
    coverage_min: number;
    coverage_max: number;
    comparison: Array<{
      system: string;
      coverage: number;
      delta_vs_null: number;
      is_null?: boolean;
    }>;
    implication: string;
  };
  vowel_holdout?: {
    headline: string;
    method: string;
    heldout_folios: string[];
    heldout_tokens: number;
    pharmaceutical: {
      prevalence: number;
      always_predict_f1: number;
      rule_precision: number;
      rule_recall: number;
      rule_f1: number;
      nb_precision: number;
      nb_recall: number;
      nb_f1: number;
      verdict_signal_survives: boolean;
    };
    biological: {
      prevalence: number;
      always_predict_f1: number;
      rule_precision: number;
      rule_recall: number;
      rule_f1: number;
      nb_precision: number;
      nb_recall: number;
      nb_f1: number;
      verdict_signal_survives: boolean;
    };
    multiclass: {
      nb_accuracy: number;
      majority_baseline: number;
      rule_accuracy_on_covered: number;
      rule_coverage: number;
    };
    per_folio: Array<{
      folio: string;
      true: string;
      n: number;
      nb_hit_rate: number;
    }>;
    interpretation: string;
    strategic_note: string;
  };
  vowel_layer?: {
    headline: string;
    method: string;
    skeletons_tested: number;
    significant_at_p01: number;
    significant_fraction: number;
    headline_case: {
      skeleton: string;
      description: string;
      chi2: number;
      df: number;
      critical_p01: number;
      over_threshold: number;
      variants: Array<{
        word: string;
        total: number;
        biological: number;
        recipes: number;
        herbal: number;
        zodiac: number;
      }>;
    };
    top_coupled_skeletons: Array<{
      skeleton: string;
      variants_preview: string;
      chi2: number;
      df: number;
      over_threshold: number;
    }>;
    implication: string;
  };
}

export function getLexiconTests(): LexiconTestData | null {
  if (!fs.existsSync(LEXICON_TESTS_PATH)) return null;
  return JSON.parse(fs.readFileSync(LEXICON_TESTS_PATH, "utf-8")) as LexiconTestData;
}

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
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
}

function readJsonDir<T>(dirPath: string): T[] {
  if (!fs.existsSync(dirPath)) return [];
  return fs
    .readdirSync(dirPath)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => JSON.parse(fs.readFileSync(path.join(dirPath, f), "utf-8")) as T);
}

export function getHypotheses(): Hypothesis[] {
  return readJsonDir<Hypothesis>(HYPOTHESES_DIR);
}

export function getBeliefs(): Belief[] {
  return readJson<Belief[]>(BELIEFS_PATH) ?? [];
}

export function getScores(): ScoreRecord[] {
  return readJsonDir<ScoreRecord>(SCORES_DIR);
}

export function getStats(): Stats | null {
  return readJson<Stats>(STATS_PATH);
}

export function getFailedApproaches(): Hypothesis[] {
  return readJsonDir<Hypothesis>(HYPOTHESES_DIR).filter(
    (h) => h.status === "eliminated"
  );
}

export function getActiveHypotheses(): Hypothesis[] {
  return readJsonDir<Hypothesis>(HYPOTHESES_DIR)
    .filter((h) => h.status === "active")
    .sort((a, b) => b.confidence - a.confidence);
}

export function getLogContent(): string {
  const logPath = path.join(PARENT_DIR, "wiki/LOG.md");
  if (!fs.existsSync(logPath)) return "";
  return fs.readFileSync(logPath, "utf-8");
}
