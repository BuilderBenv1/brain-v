export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">About Brain-V</h1>
        <p className="text-muted mt-2">
          An autonomous cognitive architecture attempting to decipher the
          Voynich Manuscript.
        </p>
      </div>

      <section className="space-y-4 text-sm leading-relaxed">
        <h2 className="text-xl font-bold">What is this?</h2>
        <p>
          Brain-V (VoynichMind) is a fork of{" "}
          <span className="text-accent">Project Brain</span>, a persistent
          cognitive architecture. It runs a continuous loop of perception,
          prediction, and scoring — the same loop that originally tracked
          AI research trends on arXiv, now retargeted at deciphering the
          Voynich Manuscript.
        </p>
        <p>
          The Voynich Manuscript (Beinecke MS 408) is a 15th-century codex
          written in an unknown script that has resisted all decipherment
          attempts for over 600 years. Its vellum has been radiocarbon dated
          to 1404-1438.
        </p>
      </section>

      <section className="space-y-4 text-sm leading-relaxed">
        <h2 className="text-xl font-bold">Methodology</h2>
        <p>
          Brain-V does not claim to solve the manuscript. It runs a
          systematic, transparent process:
        </p>
        <ol className="list-decimal list-inside space-y-2 ml-4">
          <li>
            <strong>Perceive</strong> — parse the complete EVA transliteration
            (Zandbergen ZL3b, 38,053 words across 226 folios) and compute a
            statistical profile: glyph frequencies, entropy, Zipf&apos;s law
            fit, positional constraints, Currier A/B distribution.
          </li>
          <li>
            <strong>Predict</strong> — generate testable hypotheses about the
            manuscript&apos;s cipher system, underlying language, or text
            structure. Each hypothesis must specify the exact statistical test
            that would confirm or deny it.
          </li>
          <li>
            <strong>Score</strong> — run each test against the corpus
            statistics. Update hypothesis confidence. Eliminate those that
            fail. Promote those that pass. Log every result.
          </li>
          <li>
            <strong>Learn</strong> — update the belief state based on scoring
            results. Generate new hypotheses informed by what was learned.
            Repeat.
          </li>
        </ol>
        <p>
          Every cycle is logged. Every hypothesis — including failures — is
          published. Nothing is hidden. The on-chain provenance via{" "}
          <a
            href="https://agentproof.sh"
            className="text-accent hover:underline"
          >
            AgentProof
          </a>{" "}
          means the reasoning trail is verifiable and timestamped from day
          one.
        </p>
      </section>

      <section className="space-y-4 text-sm leading-relaxed">
        <h2 className="text-xl font-bold">What Brain-V is NOT</h2>
        <ul className="list-disc list-inside space-y-1 ml-4 text-muted">
          <li>
            Not a claim to have solved the Voynich. It is a tool for
            systematic exploration.
          </li>
          <li>
            Not a replacement for domain expertise. Codicological,
            paleographic, and historical analysis are outside its scope.
          </li>
          <li>
            Not infallible. It uses a local 8B parameter LLM for hypothesis
            generation. The quality of hypotheses depends on the model.
          </li>
          <li>
            Not closed. The community can submit hypotheses and Brain-V will
            test them.
          </li>
        </ul>
      </section>

      <section className="space-y-4 text-sm leading-relaxed">
        <h2 className="text-xl font-bold">Infrastructure</h2>
        <div className="overflow-x-auto">
          <table className="text-xs font-mono">
            <tbody>
              <tr className="border-b border-border/30">
                <td className="py-2 pr-6 text-muted">Agents</td>
                <td className="py-2">
                  6 on SKALE via AgentProof (#471-#477)
                </td>
              </tr>
              <tr className="border-b border-border/30">
                <td className="py-2 pr-6 text-muted">Inference</td>
                <td className="py-2">llama3.1:8b via local Ollama</td>
              </tr>
              <tr className="border-b border-border/30">
                <td className="py-2 pr-6 text-muted">State sync</td>
                <td className="py-2">AgentOS (Railway) + IPFS</td>
              </tr>
              <tr className="border-b border-border/30">
                <td className="py-2 pr-6 text-muted">Corpus</td>
                <td className="py-2">
                  Zandbergen ZL3b EVA transliteration (voynich.nu)
                </td>
              </tr>
              <tr className="border-b border-border/30">
                <td className="py-2 pr-6 text-muted">Cycling</td>
                <td className="py-2">5 cycles daily, Mon-Fri 08:00</td>
              </tr>
              <tr>
                <td className="py-2 pr-6 text-muted">Chain</td>
                <td className="py-2">SKALE Base (zero gas)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-4 text-sm leading-relaxed">
        <h2 className="text-xl font-bold">Contributing</h2>
        <p>
          Submit a hypothesis via GitHub Issues. Use the hypothesis template.
          Brain-V will test it against the corpus statistics and publish the
          results — pass or fail.
        </p>
        <p>
          The most valuable contributions are hypotheses that would{" "}
          <strong>narrow the solution space</strong> if confirmed or denied.
          Vague theories (&quot;it might be Latin&quot;) are less useful than
          precise, testable claims (&quot;if the text is simple-substitution
          Latin, glyph entropy should be ~4.0 bits and word-final glyphs
          should match Latin suffixes&quot;).
        </p>
      </section>

      <section className="space-y-4 text-sm">
        <h2 className="text-xl font-bold">Acknowledgements</h2>
        <p className="text-muted">
          Brain-V relies on the work of the Voynich research community,
          particularly Rene Zandbergen (voynich.nu) for the EVA
          transliteration, Prescott Currier for the A/B language
          classification, and Jorge Stolfi for foundational statistical
          analysis. The failed approaches catalogue draws from D&apos;Imperio
          (1978), Kennedy &amp; Churchill (2004), and the collective work of
          voynich.ninja and voynich.net.
        </p>
      </section>
    </div>
  );
}
