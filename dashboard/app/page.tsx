import Link from "next/link";
import {
  getActiveHypotheses,
  getBeliefs,
  getHypotheses,
  getLexiconTests,
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
  const lexTests = getLexiconTests();

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

      {/* Null lexicon headline — Brain-V's strongest contribution */}
      {lexTests?.null_lexicon && (
        <div className="border-2 border-danger/60 bg-danger/5 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded bg-danger/20 text-danger font-bold uppercase tracking-wide">
              Headline finding
            </span>
            <span className="text-xs text-muted">{lexTests.generated}</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">
            {lexTests.null_lexicon.headline}
          </h2>
          <p className="text-sm text-muted mb-4">
            {lexTests.null_lexicon.method}
          </p>

          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted text-xs uppercase tracking-wide border-b border-border">
                  <th className="py-2 pr-4">System</th>
                  <th className="py-2 pr-4 text-right">Coverage</th>
                  <th className="py-2 pr-4 text-right">Δ vs null floor</th>
                </tr>
              </thead>
              <tbody>
                {lexTests.null_lexicon.comparison.map((row) => (
                  <tr
                    key={row.system}
                    className={`border-b border-border/40 ${
                      row.is_null ? "bg-danger/10 font-bold" : ""
                    }`}
                  >
                    <td className="py-2 pr-4">{row.system}</td>
                    <td className="py-2 pr-4 text-right font-mono">
                      {(row.coverage * 100).toFixed(2)}%
                    </td>
                    <td
                      className={`py-2 pr-4 text-right font-mono ${
                        row.is_null
                          ? "text-muted"
                          : row.delta_vs_null > 0.05
                            ? "text-success"
                            : row.delta_vs_null > 0
                              ? "text-warning"
                              : "text-danger"
                      }`}
                    >
                      {row.is_null
                        ? "—"
                        : (row.delta_vs_null >= 0 ? "+" : "") +
                          (row.delta_vs_null * 100).toFixed(2) +
                          "pp"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid md:grid-cols-3 gap-3 mb-4 text-sm">
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">Null size</div>
              <div className="font-mono text-xl">
                {lexTests.null_lexicon.lexicon_size.toLocaleString()}
              </div>
            </div>
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">Null coverage</div>
              <div className="font-mono text-xl">
                {(lexTests.null_lexicon.coverage_mean * 100).toFixed(2)}% ± {(lexTests.null_lexicon.coverage_stdev * 100).toFixed(2)}pp
              </div>
            </div>
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">Trials</div>
              <div className="font-mono text-xl">
                {lexTests.null_lexicon.trials}
              </div>
            </div>
          </div>

          <p className="text-sm bg-surface rounded p-4 border-l-2 border-danger">
            <strong>Implication.</strong> {lexTests.null_lexicon.implication}
          </p>
        </div>
      )}

      {/* Vowel holdout — published negative result */}
      {lexTests?.vowel_holdout && (
        <div className="border-2 border-warning/60 bg-warning/5 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded bg-warning/20 text-warning font-bold uppercase tracking-wide">
              Negative result (published)
            </span>
            <span className="text-xs text-muted">{lexTests.generated}</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">
            {lexTests.vowel_holdout.headline}
          </h2>
          <p className="text-sm text-muted mb-4">
            {lexTests.vowel_holdout.method}
          </p>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            {(["pharmaceutical", "biological"] as const).map((target) => {
              const r = lexTests.vowel_holdout![target];
              return (
                <div key={target} className="bg-surface rounded p-4">
                  <h3 className="text-sm font-bold mb-2 capitalize">
                    Target: {target}{" "}
                    <span className="text-xs text-muted font-normal">
                      (prevalence {(r.prevalence * 100).toFixed(1)}%)
                    </span>
                  </h3>
                  <table className="w-full text-xs font-mono">
                    <thead>
                      <tr className="text-muted border-b border-border">
                        <th className="py-1 text-left">method</th>
                        <th className="py-1 text-right">prec</th>
                        <th className="py-1 text-right">rec</th>
                        <th className="py-1 text-right">F1</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border/40">
                        <td className="py-1">always-predict</td>
                        <td className="py-1 text-right">{r.prevalence.toFixed(3)}</td>
                        <td className="py-1 text-right">1.000</td>
                        <td className="py-1 text-right text-success font-bold">
                          {r.always_predict_f1.toFixed(3)}
                        </td>
                      </tr>
                      <tr className="border-b border-border/40">
                        <td className="py-1">rule table</td>
                        <td className="py-1 text-right text-success">
                          {r.rule_precision.toFixed(3)}
                        </td>
                        <td className="py-1 text-right">{r.rule_recall.toFixed(3)}</td>
                        <td className="py-1 text-right">{r.rule_f1.toFixed(3)}</td>
                      </tr>
                      <tr>
                        <td className="py-1">naive Bayes</td>
                        <td className="py-1 text-right">{r.nb_precision.toFixed(3)}</td>
                        <td className="py-1 text-right">{r.nb_recall.toFixed(3)}</td>
                        <td className="py-1 text-right">{r.nb_f1.toFixed(3)}</td>
                      </tr>
                    </tbody>
                  </table>
                  <p className="text-xs text-danger mt-2">
                    Signal does not survive: best F1 below always-predict baseline.
                  </p>
                </div>
              );
            })}
          </div>

          <div className="bg-surface rounded p-4 mb-4">
            <h3 className="text-sm font-bold mb-2">Per-folio NB hit rate</h3>
            <div className="space-y-1 text-xs font-mono">
              {lexTests.vowel_holdout.per_folio.map((f) => (
                <div key={f.folio} className="flex items-center justify-between">
                  <span>
                    <span className="text-accent">{f.folio}</span>{" "}
                    <span className="text-muted">
                      (true: {f.true}, n={f.n})
                    </span>
                  </span>
                  <span
                    className={
                      f.nb_hit_rate >= 0.5 ? "text-warning" : "text-danger"
                    }
                  >
                    {(f.nb_hit_rate * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted mt-2">
              Held-out pharmaceutical folios mis-classified as biological at ~75%+
              rate. Multi-class NB accuracy{" "}
              {(lexTests.vowel_holdout.multiclass.nb_accuracy * 100).toFixed(1)}%
              vs majority baseline{" "}
              {(lexTests.vowel_holdout.multiclass.majority_baseline * 100).toFixed(1)}
              %.
            </p>
          </div>

          <p className="text-sm bg-surface rounded p-4 border-l-2 border-warning mb-2">
            <strong>Interpretation.</strong> {lexTests.vowel_holdout.interpretation}
          </p>
          <p className="text-sm bg-surface rounded p-4 border-l-2 border-accent">
            <strong>Why this is published.</strong>{" "}
            {lexTests.vowel_holdout.strategic_note}
          </p>
        </div>
      )}

      {/* Vowel-layer finding */}
      {lexTests?.vowel_layer && (
        <div className="border-2 border-success/60 bg-success/5 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded bg-success/20 text-success font-bold uppercase tracking-wide">
              Positive finding
            </span>
            <span className="text-xs text-muted">{lexTests.generated}</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">
            {lexTests.vowel_layer.headline}
          </h2>
          <p className="text-sm text-muted mb-4">
            {lexTests.vowel_layer.method}
          </p>

          <div className="grid md:grid-cols-3 gap-3 mb-4 text-sm">
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">Skeletons tested</div>
              <div className="font-mono text-xl">
                {lexTests.vowel_layer.skeletons_tested}
              </div>
            </div>
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">
                Significant at p&lt;0.01
              </div>
              <div className="font-mono text-xl text-success">
                {lexTests.vowel_layer.significant_at_p01} /{" "}
                {lexTests.vowel_layer.skeletons_tested} (
                {(lexTests.vowel_layer.significant_fraction * 100).toFixed(1)}%)
              </div>
            </div>
            <div className="bg-surface rounded p-3">
              <div className="text-muted text-xs uppercase">
                Headline skeleton &apos;{lexTests.vowel_layer.headline_case.skeleton}&apos; vs chance
              </div>
              <div className="font-mono text-xl text-success">
                {lexTests.vowel_layer.headline_case.over_threshold.toFixed(2)}× over p=0.01
              </div>
            </div>
          </div>

          <div className="bg-surface rounded p-4 mb-4">
            <h3 className="text-sm font-bold mb-2">
              Case: skeleton &apos;{lexTests.vowel_layer.headline_case.skeleton}&apos; — {lexTests.vowel_layer.headline_case.description}
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="text-muted border-b border-border">
                    <th className="py-1 pr-3 text-left">variant</th>
                    <th className="py-1 pr-3 text-right">total</th>
                    <th className="py-1 pr-3 text-right">biological</th>
                    <th className="py-1 pr-3 text-right">recipes</th>
                    <th className="py-1 pr-3 text-right">herbal</th>
                    <th className="py-1 pr-3 text-right">zodiac</th>
                  </tr>
                </thead>
                <tbody>
                  {lexTests.vowel_layer.headline_case.variants.map((v) => (
                    <tr key={v.word} className="border-b border-border/40">
                      <td className="py-1 pr-3">{v.word}</td>
                      <td className="py-1 pr-3 text-right">{v.total}</td>
                      <td className="py-1 pr-3 text-right">{v.biological}</td>
                      <td className="py-1 pr-3 text-right">{v.recipes}</td>
                      <td className="py-1 pr-3 text-right">{v.herbal}</td>
                      <td className="py-1 pr-3 text-right">{v.zodiac}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-muted mt-2">
              chi² = {lexTests.vowel_layer.headline_case.chi2.toFixed(1)}, df ={" "}
              {lexTests.vowel_layer.headline_case.df}, critical at p&lt;0.01 ={" "}
              {lexTests.vowel_layer.headline_case.critical_p01.toFixed(1)} →{" "}
              <strong className="text-success">
                {lexTests.vowel_layer.headline_case.over_threshold.toFixed(2)}× over threshold
              </strong>
            </p>
          </div>

          <div className="bg-surface rounded p-4 mb-4">
            <h3 className="text-sm font-bold mb-2">
              Top-5 skeletons by vowel-section coupling strength
            </h3>
            <div className="space-y-1 text-xs font-mono">
              {lexTests.vowel_layer.top_coupled_skeletons.map((s) => (
                <div key={s.skeleton} className="flex justify-between">
                  <span>
                    <span className="text-accent">{s.skeleton}</span>{" "}
                    <span className="text-muted">[{s.variants_preview}]</span>
                  </span>
                  <span className="text-success">
                    {s.over_threshold.toFixed(2)}× over p=0.01
                  </span>
                </div>
              ))}
            </div>
          </div>

          <p className="text-sm bg-surface rounded p-4 border-l-2 border-success">
            <strong>Implication.</strong> {lexTests.vowel_layer.implication}
          </p>
        </div>
      )}

      {/* Three-lexicon comparison — new finding */}
      {lexTests && (
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-lg font-bold">
              Three-Lexicon Comparison
              <span className="ml-2 text-xs px-2 py-0.5 rounded bg-accent/20 text-accent align-middle">
                new
              </span>
            </h2>
            <span className="text-xs text-muted">{lexTests.generated}</span>
          </div>
          <p className="text-sm text-muted mb-4">
            Three independent decipherment lexicons (Latin, Syriac, Hebrew) run
            through Brain-V&apos;s honest pipeline against the full EVA corpus.
            {" "}
            <strong className="text-foreground">
              All three fail the shuffle test on word-order syntax.
            </strong>
          </p>

          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted text-xs uppercase tracking-wide border-b border-border">
                  <th className="py-2 pr-4">Lexicon</th>
                  <th className="py-2 pr-4 text-right">Entries</th>
                  <th className="py-2 pr-4 text-right">Coverage</th>
                  <th className="py-2 pr-4 text-right">conn→content Δ</th>
                  <th className="py-2 pr-4 text-right">both-matched Δ</th>
                </tr>
              </thead>
              <tbody>
                {lexTests.lexicons.map((l) => {
                  const cc = l.shuffle_in_order_vs_shuffled.conn_content;
                  const bm = l.shuffle_in_order_vs_shuffled.both_matched;
                  return (
                    <tr key={l.name} className="border-b border-border/40">
                      <td className="py-2 pr-4">{l.name}</td>
                      <td className="py-2 pr-4 text-right font-mono">
                        {l.entries.toLocaleString()}
                      </td>
                      <td className="py-2 pr-4 text-right font-mono text-accent">
                        {(l.coverage * 100).toFixed(1)}%
                      </td>
                      <td
                        className={`py-2 pr-4 text-right font-mono ${
                          cc == null
                            ? "text-muted"
                            : cc < 0
                              ? "text-danger"
                              : "text-success"
                        }`}
                      >
                        {cc == null ? "—" : (cc >= 0 ? "+" : "") + cc.toFixed(4)}
                      </td>
                      <td
                        className={`py-2 pr-4 text-right font-mono ${
                          bm == null
                            ? "text-muted"
                            : bm > 0.01
                              ? "text-success"
                              : "text-muted"
                        }`}
                      >
                        {bm == null ? "—" : (bm >= 0 ? "+" : "") + bm.toFixed(4)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Currier A/B convergence */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-surface-2 rounded p-4">
              <h3 className="text-sm font-bold text-accent mb-2">
                Currier B &gt; A across all three lexicons
              </h3>
              <div className="space-y-1 text-sm font-mono">
                <div className="flex justify-between">
                  <span>Schechter Latin</span>
                  <span className="text-success">
                    +{(lexTests.currier_ab_gap.schechter_latin * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Brady Syriac (proxy)</span>
                  <span className="text-success">
                    +{(lexTests.currier_ab_gap.brady_syriac_proxy * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Hebrew medieval</span>
                  <span className="text-success">
                    +{(lexTests.currier_ab_gap.hebrew_medieval * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
              <p className="text-xs text-muted mt-2">
                Three independent methodologies, same direction. Currier A
                structurally resists lexical matching.
              </p>
            </div>

            <div className="bg-surface-2 rounded p-4">
              <h3 className="text-sm font-bold text-accent mb-2">
                H-BRADY-02 confirmed: gallows are paragraph markers
              </h3>
              <div className="space-y-1 text-sm font-mono">
                <div className="flex justify-between">
                  <span>EVA &apos;p&apos; line-initial</span>
                  <span className="text-success">
                    {lexTests.brady_gallows_confirmed.p_enrichment.toFixed(1)}× (pred{" "}
                    {lexTests.brady_gallows_confirmed.p_predicted.toFixed(1)}×)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>EVA &apos;t&apos; line-initial</span>
                  <span className="text-success">
                    {lexTests.brady_gallows_confirmed.t_enrichment.toFixed(1)}× (pred{" "}
                    {lexTests.brady_gallows_confirmed.t_predicted.toFixed(1)}×)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>bench gallows cth/ckh/cph</span>
                  <span className="text-muted">&lt; 0.5×</span>
                </div>
              </div>
              <p className="text-xs text-muted mt-2">
                Brain-V&apos;s first independent verification of an external
                Voynich structural claim.
              </p>
            </div>
          </div>

          <p className="text-xs text-muted mt-4 italic border-t border-border pt-3">
            <strong className="text-foreground not-italic">Verdict:</strong>{" "}
            {lexTests.verdict}
          </p>
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
