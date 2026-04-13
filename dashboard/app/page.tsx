import Link from "next/link";
import {
  getActiveHypotheses,
  getBeliefs,
  getHypotheses,
  getScores,
  getStats,
} from "@/lib/data";

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="text-muted text-xs uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-mono font-bold mt-1 text-accent">
        {value}
      </div>
      {sub && <div className="text-muted text-xs mt-1">{sub}</div>}
    </div>
  );
}

export default function Home() {
  const stats = getStats();
  const hypotheses = getHypotheses();
  const active = getActiveHypotheses();
  const beliefs = getBeliefs();
  const scores = getScores();

  const eliminated = hypotheses.filter((h) => h.status === "eliminated");
  const parked = hypotheses.filter((h) => h.status === "parked");
  const highConf = active.filter((h) => h.confidence > 0.8);
  const latestScore = scores[scores.length - 1];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Brain-V Dashboard</h1>
        <p className="text-muted mt-2 max-w-2xl">
          An autonomous cognitive architecture attempting to decipher the Voynich
          Manuscript (Beinecke MS 408, c. 1404-1438) through statistical
          analysis, hypothesis generation, and iterative testing.
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <StatCard
          label="Active Hypotheses"
          value={active.length}
          sub={`${highConf.length} above 0.8`}
        />
        <StatCard
          label="Eliminated"
          value={eliminated.length}
          sub="won't retest"
        />
        <StatCard label="Parked" value={parked.length} sub="need more data" />
        <StatCard label="Beliefs" value={beliefs.length} />
        <StatCard label="Cycles Run" value={scores.length} />
        <StatCard
          label="Latest Surprise"
          value={latestScore?.progress?.surprise?.toFixed(4) ?? "—"}
          sub={latestScore?.date ?? "no cycles yet"}
        />
      </div>

      {/* Corpus overview */}
      {stats && (
        <div className="bg-surface border border-border rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4">Corpus Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-muted">Words:</span>{" "}
              <span className="font-mono">
                {stats.summary.total_words.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-muted">Unique:</span>{" "}
              <span className="font-mono">
                {stats.summary.unique_words.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-muted">Glyphs:</span>{" "}
              <span className="font-mono">{stats.summary.unique_glyphs}</span>
            </div>
            <div>
              <span className="text-muted">Folios:</span>{" "}
              <span className="font-mono">{stats.summary.total_folios}</span>
            </div>
            <div>
              <span className="text-muted">Glyph entropy:</span>{" "}
              <span className="font-mono">
                {stats.entropy.glyph_entropy_overall} bits
              </span>
            </div>
            <div>
              <span className="text-muted">Zipf exponent:</span>{" "}
              <span className="font-mono">{stats.zipf.exponent}</span>
            </div>
            <div>
              <span className="text-muted">Zipf R²:</span>{" "}
              <span className="font-mono">{stats.zipf.r_squared}</span>
            </div>
            <div>
              <span className="text-muted">Hapax ratio:</span>{" "}
              <span className="font-mono">
                {(stats.summary.hapax_ratio * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Top hypotheses */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">Leading Hypotheses</h2>
          <Link
            href="/hypotheses"
            className="text-accent text-sm hover:underline"
          >
            View all
          </Link>
        </div>
        {active.length === 0 ? (
          <p className="text-muted">No active hypotheses yet.</p>
        ) : (
          <div className="space-y-3">
            {active.slice(0, 5).map((h) => (
              <div
                key={h.id}
                className="flex items-start gap-3 p-3 rounded bg-surface-2"
              >
                <div className="flex-shrink-0">
                  <span className="font-mono text-xs text-muted">{h.id}</span>
                  <div
                    className={`text-lg font-bold font-mono ${
                      h.confidence > 0.7
                        ? "text-success"
                        : h.confidence > 0.4
                          ? "text-warning"
                          : "text-danger"
                    }`}
                  >
                    {h.confidence.toFixed(2)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm">{h.claim}</p>
                  <div className="flex gap-2 mt-1">
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-dim/30 text-accent">
                      {h.type}
                    </span>
                    {h.tests_run.length > 0 && (
                      <span className="text-xs text-muted">
                        {h.tests_run.length} test
                        {h.tests_run.length !== 1 ? "s" : ""} run
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Current beliefs */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">Current Beliefs</h2>
          <Link
            href="/beliefs"
            className="text-accent text-sm hover:underline"
          >
            View all
          </Link>
        </div>
        <div className="space-y-2">
          {beliefs.slice(0, 6).map((b, i) => {
            const conf =
              typeof b.confidence === "number"
                ? b.confidence
                : parseFloat(String(b.confidence)) || 0;
            return (
              <div key={i} className="flex items-center gap-3 text-sm">
                <span
                  className={`font-mono font-bold w-12 text-right ${
                    conf > 0.7
                      ? "text-success"
                      : conf > 0.4
                        ? "text-warning"
                        : "text-danger"
                  }`}
                >
                  {conf.toFixed(2)}
                </span>
                <span className="text-foreground">{b.belief}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Methodology */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-3">How Brain-V Works</h2>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <h3 className="font-bold text-accent mb-1">Perceive</h3>
            <p className="text-muted">
              Parse the EVA transliteration (Zandbergen ZL3b). Compute glyph
              frequencies, entropy, Zipf fit, positional constraints, Currier
              A/B statistics across all 226 folios.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-accent mb-1">Predict</h3>
            <p className="text-muted">
              Generate testable hypotheses about the manuscript&apos;s cipher,
              language, and structure. Each hypothesis specifies the exact
              statistical test that would confirm or deny it.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-accent mb-1">Score</h3>
            <p className="text-muted">
              Run each test against the corpus. Update confidence scores.
              Eliminate hypotheses that fail. Promote those that pass. Log
              everything on-chain via AgentProof.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
