import { getStats } from "@/lib/data";

export default function StatsPage() {
  const stats = getStats();

  if (!stats) {
    return (
      <div>
        <h1 className="text-3xl font-bold">Corpus Statistics</h1>
        <p className="text-muted mt-4">
          No statistics computed yet. Run perceive.py first.
        </p>
      </div>
    );
  }

  const s = stats.summary;
  const e = stats.entropy;
  const z = stats.zipf;

  const topWords = Object.entries(stats.word_frequency.top_50)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 30);

  const topGlyphs = Object.entries(stats.glyph_frequency.overall)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 25);

  const topBigrams = Object.entries(stats.ngrams.top_30_bigrams)
    .sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Corpus Statistics</h1>
        <p className="text-muted mt-2">
          Statistical profile of the Voynich Manuscript, computed from the
          Zandbergen (ZL3b) EVA transliteration.
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          ["Total words", s.total_words.toLocaleString()],
          ["Unique words", s.unique_words.toLocaleString()],
          ["Total glyphs", s.total_glyphs.toLocaleString()],
          ["Unique glyphs", String(s.unique_glyphs)],
          ["Avg word length", String(s.avg_word_length)],
          ["Hapax legomena", `${s.hapax_legomena.toLocaleString()} (${(s.hapax_ratio * 100).toFixed(1)}%)`],
          ["Dis legomena", s.dis_legomena.toLocaleString()],
          ["Total folios", String(s.total_folios)],
        ].map(([label, value]) => (
          <div
            key={label}
            className="bg-surface border border-border rounded-lg p-3"
          >
            <div className="text-xs text-muted uppercase">{label}</div>
            <div className="font-mono font-bold mt-1">{value}</div>
          </div>
        ))}
      </div>

      {/* Entropy table */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-4">Entropy Analysis</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted border-b border-border">
                <th className="pb-2 pr-4">Scope</th>
                <th className="pb-2 pr-4 font-mono">Glyph entropy</th>
                <th className="pb-2 pr-4 font-mono">Word entropy</th>
                <th className="pb-2 font-mono">Words</th>
              </tr>
            </thead>
            <tbody className="font-mono text-xs">
              <tr className="border-b border-border/50 font-bold">
                <td className="py-2 pr-4">Overall</td>
                <td className="py-2 pr-4">{e.glyph_entropy_overall} bits</td>
                <td className="py-2 pr-4">{e.word_entropy_overall} bits</td>
                <td className="py-2">{s.total_words.toLocaleString()}</td>
              </tr>
              {Object.entries(e.by_section)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([section, data]) => (
                  <tr key={section} className="border-b border-border/30">
                    <td className="py-2 pr-4 capitalize">{section}</td>
                    <td className="py-2 pr-4">{data.glyph_entropy} bits</td>
                    <td className="py-2 pr-4">{data.word_entropy} bits</td>
                    <td className="py-2">{data.word_count.toLocaleString()}</td>
                  </tr>
                ))}
              <tr className="border-t border-border">
                <td className="py-2 pr-4 text-muted" colSpan={4}>
                  Currier Languages
                </td>
              </tr>
              {Object.entries(e.by_language)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([lang, data]) => (
                  <tr key={lang} className="border-b border-border/30">
                    <td className="py-2 pr-4">Language {lang}</td>
                    <td className="py-2 pr-4">{data.glyph_entropy} bits</td>
                    <td className="py-2 pr-4">{data.word_entropy} bits</td>
                    <td className="py-2">{data.word_count.toLocaleString()}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted mt-3">
          Natural language comparison: English ~4.11 bits/char, Latin ~4.0
          bits/char, Italian ~3.95 bits/char. The Voynich&apos;s 3.86 bits is
          within the natural language range.
        </p>
      </div>

      {/* Zipf's Law */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-4">Zipf&apos;s Law</h2>
        <div className="grid grid-cols-3 gap-4 font-mono text-sm">
          <div>
            <span className="text-muted text-xs block">Exponent</span>
            <span className="text-xl font-bold">{z.exponent}</span>
          </div>
          <div>
            <span className="text-muted text-xs block">R²</span>
            <span className="text-xl font-bold">{z.r_squared}</span>
          </div>
          <div>
            <span className="text-muted text-xs block">Fit</span>
            <span className="text-xl font-bold text-accent">
              {z.interpretation}
            </span>
          </div>
        </div>
        <p className="text-xs text-muted mt-3">
          Natural language: exponent ~1.0, R² &gt; 0.95. The Voynich shows
          moderate fit — consistent with meaningful text but not a perfect
          match.
        </p>
      </div>

      {/* Top words */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4">Top 30 Words</h2>
          <div className="space-y-1 font-mono text-xs">
            {topWords.map(([word, count], i) => (
              <div key={word} className="flex items-center gap-2">
                <span className="text-muted w-6 text-right">{i + 1}.</span>
                <span className="w-20">{word}</span>
                <div className="flex-1 h-3 bg-surface-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent/40 rounded-full"
                    style={{
                      width: `${(count / topWords[0][1]) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-muted w-12 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <h2 className="text-lg font-bold mb-4">Glyph Frequency</h2>
          <div className="space-y-1 font-mono text-xs">
            {topGlyphs.map(([glyph, count]) => (
              <div key={glyph} className="flex items-center gap-2">
                <span className="w-6 text-center text-accent font-bold text-sm">
                  {glyph}
                </span>
                <div className="flex-1 h-3 bg-surface-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent/40 rounded-full"
                    style={{
                      width: `${(count / topGlyphs[0][1]) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-muted w-16 text-right">
                  {count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bigrams */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-4">Top Glyph Bigrams</h2>
        <div className="flex flex-wrap gap-2">
          {topBigrams.map(([bigram, count]) => (
            <span
              key={bigram}
              className="font-mono text-xs px-2 py-1 rounded bg-surface-2 border border-border"
            >
              <span className="text-accent">{bigram}</span>
              <span className="text-muted ml-1">{count}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Sections */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <h2 className="text-lg font-bold mb-4">Section Breakdown</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="text-left text-muted border-b border-border">
                <th className="pb-2 pr-4">Section</th>
                <th className="pb-2 pr-4">Folios</th>
                <th className="pb-2 pr-4">Words</th>
                <th className="pb-2 pr-4">Unique</th>
                <th className="pb-2">Avg length</th>
              </tr>
            </thead>
            <tbody className="text-xs">
              {Object.entries(stats.sections)
                .sort(([, a], [, b]) => b.word_count - a.word_count)
                .map(([section, data]) => (
                  <tr key={section} className="border-b border-border/30">
                    <td className="py-2 pr-4 capitalize">{section}</td>
                    <td className="py-2 pr-4">{data.folio_count}</td>
                    <td className="py-2 pr-4">
                      {data.word_count.toLocaleString()}
                    </td>
                    <td className="py-2 pr-4">
                      {data.unique_words.toLocaleString()}
                    </td>
                    <td className="py-2">{data.avg_word_length}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
