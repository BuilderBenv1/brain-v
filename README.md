# Brain-V (VoynichMind)

An autonomous cognitive architecture attempting to decipher the Voynich Manuscript through statistical analysis, hypothesis generation, and iterative testing.

**Every hypothesis is tested. Every failure is published. Nothing is hidden.**

## What is this?

Brain-V is a fork of [Project Brain](https://github.com/your-repo/project-brain), a persistent cognitive architecture originally built for tracking AI research trends. It runs the same perceive-predict-score loop, now retargeted at the Voynich Manuscript (Beinecke MS 408, c. 1404-1438).

The manuscript has resisted 600 years of human analysis. Brain-V doesn't claim to solve it. It runs a systematic, transparent process — generating testable hypotheses, running statistical tests against the corpus, eliminating what fails, promoting what passes, and publishing everything.

## Current Status

| Metric | Value |
|---|---|
| Corpus | 38,053 words, 8,261 unique, 226 folios |
| Glyph entropy | 3.86 bits (natural language range) |
| Zipf exponent | 0.89 (R²=0.91) |
| Active hypotheses | Check the dashboard |
| Eliminated | 13+ (including historical failed attempts) |
| Failed approaches catalogued | 20 (1921-2025) |

## How it works

```
perceive.py  →  Parse EVA transliteration, compute statistical profile
     ↓
predict.py   →  Generate testable hypotheses via LLM
     ↓
score.py     →  Run statistical tests against corpus
     ↓
loop.py      →  Update beliefs, eliminate failures, repeat
```

Each cycle:
1. **Perceive** — Parse the Zandbergen (ZL3b) EVA transliteration. Compute glyph frequencies, Shannon entropy, Zipf fit, positional constraints, Currier A/B statistics.
2. **Predict** — Generate 3-5 testable hypotheses about cipher, language, or structure. Each must specify the exact statistical test.
3. **Score** — Run each test. Update confidence. Eliminate what fails.
4. **Learn** — Update beliefs. Generate new hypotheses. Repeat.

Brain-V cycles 5 times daily (Mon-Fri). The corpus is static — hypotheses are the moving part.

## Contributing

**Submit a hypothesis** via [GitHub Issues](../../issues/new?template=hypothesis.md). Brain-V will test it and publish the results.

The most valuable hypotheses are those that **narrow the solution space** — precise, testable claims where either outcome teaches us something.

## Failed Approaches

Brain-V pre-loads 20 documented failed decipherment attempts (1921-2025) as eliminated hypotheses. It will never waste cycles rediscovering what Friedman's NSA team ruled out in the 1940s or what Cheshire got debunked for in 2019. See the [Failed Approaches](dashboard) page on the dashboard.

## Infrastructure

- **6 agents** on SKALE via [AgentProof](https://agentproof.sh) (#471-#477)
- **Inference**: llama3.1:8b via local Ollama
- **State sync**: AgentOS + IPFS (every cycle anchored on-chain)
- **Corpus**: Zandbergen ZL3b EVA transliteration from [voynich.nu](https://voynich.nu)
- **Dashboard**: Next.js on Vercel

## Running locally

```bash
# Prerequisites: Python 3.10+, Ollama with llama3.1:8b

# Parse the corpus
python scripts/perceive.py --report

# Generate hypotheses
python scripts/predict.py

# Test hypotheses
python scripts/score.py

# Full cycle
python scripts/loop.py full

# Auto: 10 consecutive cycles
python scripts/loop.py auto --cycles 10

# Check status
python scripts/loop.py status
```

## Acknowledgements

- Rene Zandbergen ([voynich.nu](https://voynich.nu)) for the EVA transliteration
- Prescott Currier for the A/B language classification
- Jorge Stolfi for foundational statistical analysis
- The communities at [voynich.ninja](https://voynich.ninja) and [voynich.net](https://voynich.net)
- D'Imperio, Kennedy & Churchill, and all researchers whose failed attempts form our knowledge base

## License

MIT
