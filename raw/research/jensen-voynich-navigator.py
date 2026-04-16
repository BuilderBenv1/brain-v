"""
VOYNICH NAVIGATOR
=================
Semantic attractor analysis for the Voynich Manuscript.
Built on semantic_navigator_optimized.py

Key differences from standard pipeline:
1. EVA transcription parser - handles Voynich-specific format
2. Dual embedding strategy:
   - Character n-gram embeddings (structure-sensitive, language-agnostic)
   - Standard sentence embeddings (for comparison baseline)
3. Section-aware analysis (herbal, astronomical, biological, etc.)
4. Language-structure detection metrics
5. Comparison mode against known languages

The central question: does this text have the SHAPE of language?

EVA transcription source:
  https://www.voynich.nu/transcr.html (Zandbergen-Landini transcription)
  Download: interln16e6.txt or similar

Usage:
  python voynich_navigator.py --input interln16e6.txt
  python voynich_navigator.py --input interln16e6.txt --compare revelation.txt
  python voynich_navigator.py --input interln16e6.txt --section herbal
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from tqdm import tqdm
from collections import Counter, defaultdict
import argparse
import hashlib
import pickle
import re
from itertools import combinations

# ML/NLP imports
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import torch

import warnings
warnings.filterwarnings('ignore')

# ======================
# CONFIGURATION
# ======================

class Config:
    # Standard embedding model (for baseline comparison)
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

    # Clustering — tuned for Voynich word-token space
    DBSCAN_EPS = 0.5
    DBSCAN_MIN_SAMPLES = 2

    # N-gram settings — word-level for Voynich (not char-level)
    NGRAM_MIN = 1
    NGRAM_MAX = 2

    # Visualization
    FIGURE_SIZE = (20, 16)
    DPI = 300

    # Output
    OUTPUT_DIR = "voynich_analysis"
    CACHE_DIR = ".voynich_cache"
    USE_CACHE = True
    USE_GPU = torch.cuda.is_available()

# ======================
# VOYNICH SECTION MAP
# ======================

# Known sections of the Voynich manuscript by folio range
# Based on standard Voynich scholarship
SECTION_MAP = {
    'herbal_a':      (1,   66),   # Herbal A - botanical illustrations
    'astronomical':  (67,  73),   # Astronomical / zodiac
    'biological':    (74,  84),   # Biological / bathing figures  
    'cosmological':  (85,  86),   # Cosmological rosettes
    'herbal_b':      (87,  102),  # Herbal B - more botanical
    'pharmaceutical':(103, 116),  # Pharmaceutical / jars
    'recipes':       (117, 120),  # Stars / recipes / continuous text
}

SECTION_COLORS = {
    'herbal_a':       '#2d8a4e',
    'astronomical':   '#4a90d9',
    'biological':     '#e87c3e',
    'cosmological':   '#9b59b6',
    'herbal_b':       '#27ae60',
    'pharmaceutical': '#e74c3c',
    'recipes':        '#f39c12',
    'unknown':        '#95a5a6',
}

# ======================
# CACHING
# ======================

def get_cache_path(content_hash, suffix, cache_dir=Config.CACHE_DIR):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"voynich_{content_hash}_{suffix}.pkl"

def try_load_cache(path):
    if Config.USE_CACHE and path.exists():
        print(f"🎯 Cache hit: {path.name}")
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None

def save_cache(data, path):
    if Config.USE_CACHE:
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Cached: {path.name}")

# ======================
# STEP 1: EVA PARSER
# ======================

def parse_eva_transcription(filepath):
    """
    Parse EVA (European Voynich Alphabet) transcription file.
    
    EVA format looks like:
    <f1r.P1.1;H>   fachys.ykal.ar.ataiin.shol.shory.cth...
    <f1r.P1.2;H>   sory.ched.y.kor.sheody...
    
    Returns:
        lines: list of transcribed text strings (one per line)
        metadata: list of dicts with folio, section info per line
        sections: dict mapping section name to line indices
    """
    print(f"📖 Parsing EVA transcription: {filepath}")

    lines = []
    metadata = []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.readlines()

    for raw_line in raw:
        raw_line = raw_line.strip()

        # Skip empty lines and pure comment lines
        if not raw_line or raw_line.startswith('#'):
            continue

        # Try to parse structured EVA format: <folio.paragraph.line;scribe> text
        match = re.match(r'<([^>]+)>\s*(.*)', raw_line)

        if match:
            tag = match.group(1)
            text = match.group(2).strip()
        else:
            # Unstructured - treat whole line as text
            tag = 'unknown'
            text = raw_line

        # Clean EVA/Currier text
        # Remove inline comments {like this}
        text = re.sub(r'\{[^}]*\}', '', text)
        # Remove special markers !, ?, *, %
        text = re.sub(r'[!?*%]', '', text)
        # Remove plant/illustration markers
        text = re.sub(r'<[^>]*>', '', text)
        # Replace . word separators with spaces (critical for Currier notation)
        text = text.replace('.', ' ')
        # Remove line continuation and paragraph markers
        text = text.replace('-', '').replace('=', '')
        # Normalize whitespace
        text = ' '.join(text.split())

        if not text:
            continue

        # Extract folio number — handle both <f1r.P1.1> and <1r.1> formats
        folio_num = None
        folio_match = re.match(r'f?(\d+)', tag)
        if folio_match:
            folio_num = int(folio_match.group(1))

        # Determine section
        section = 'unknown'
        if folio_num is not None:
            for sec_name, (start, end) in SECTION_MAP.items():
                if start <= folio_num <= end:
                    section = sec_name
                    break

        lines.append(text)
        metadata.append({
            'tag': tag,
            'folio': folio_num,
            'section': section,
            'original': text,
        })

    # If file didn't match EVA format, try plain text parsing
    if len(lines) < 10:
        print("⚠️  EVA format not detected, trying plain text parsing...")
        lines, metadata = parse_plain_voynich(filepath)

    print(f"✅ Parsed {len(lines)} lines from {len(set(m['folio'] for m in metadata if m['folio']))} folios")

    # Build section index
    sections = defaultdict(list)
    for i, meta in enumerate(metadata):
        sections[meta['section']].append(i)

    section_summary = {k: len(v) for k, v in sections.items()}
    print(f"📚 Sections: {section_summary}")

    return lines, metadata, dict(sections)


def parse_plain_voynich(filepath):
    """Fallback parser for plain text Voynich transcriptions."""
    lines = []
    metadata = []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
                metadata.append({
                    'tag': f'line_{i}',
                    'folio': None,
                    'section': 'unknown',
                    'original': line,
                })

    return lines, metadata

# ======================
# STEP 2: DUAL EMBEDDING
# ======================

def embed_ngrams(lines, ngram_min=Config.NGRAM_MIN, ngram_max=Config.NGRAM_MAX):
    """
    Word-level TF-IDF embeddings for Voynich.

    CRITICAL: Voynich uses numeric/symbolic tokens as atomic units
    (e.g. '8am', '1oe', '9hoe'). Character n-grams destroy this
    structure. We treat each dot-separated token as a whole word.

    This finds lines that share similar vocabularies and token patterns —
    which is exactly what we want for section detection.
    """
    print(f"🔤 Building word-level TF-IDF embeddings...")

    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(ngram_min, ngram_max),
        min_df=2,
        max_features=10000,
        sublinear_tf=True,
        token_pattern=r'\S+',  # Any non-whitespace = one token
    )

    try:
        embeddings = vectorizer.fit_transform(lines).toarray().astype(np.float32)
        # L2 normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings = embeddings / norms
        print(f"✅ Word embeddings: {embeddings.shape} ({embeddings.shape[1]} features)")
        print(f"   Top tokens: {vectorizer.get_feature_names_out()[:20].tolist()}")
        return embeddings, vectorizer
    except Exception as e:
        print(f"⚠️  Word embedding failed: {e}")
        return None, None


def embed_semantic(lines, model_name=Config.EMBEDDING_MODEL):
    """
    Standard semantic embeddings for comparison baseline.
    Will capture English-like patterns if the text has them.
    """
    content_hash = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]
    cache_path = get_cache_path(content_hash, 'semantic')
    cached = try_load_cache(cache_path)
    if cached is not None:
        return cached

    print(f"🧠 Building semantic embeddings...")
    device = 'cuda' if Config.USE_GPU else 'cpu'
    model = SentenceTransformer(model_name, device=device)

    embeddings = []
    batch_size = 32
    for i in tqdm(range(0, len(lines), batch_size), desc="Semantic embed"):
        batch = model.encode(
            lines[i:i+batch_size],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        embeddings.append(batch)

    embeddings = np.vstack(embeddings)
    save_cache(embeddings, cache_path)
    print(f"✅ Semantic embeddings: {embeddings.shape}")
    return embeddings

# ======================
# STEP 3: STRUCTURE METRICS
# ======================

def compute_structure_metrics(lines, metadata, embeddings_ngram, embeddings_semantic):
    """
    Compute metrics that indicate whether this text has language-like structure.
    
    Returns a dict of metrics with interpretation.
    """
    print("📊 Computing structure metrics...")
    metrics = {}

    # --- 1. Vocabulary statistics ---
    all_words = []
    for line in lines:
        # Words are already space-separated after preprocessing
        words = line.split()
        all_words.extend(words)

    word_counts = Counter(all_words)
    vocab_size = len(word_counts)
    total_tokens = len(all_words)

    metrics['vocab_size'] = vocab_size
    metrics['total_tokens'] = total_tokens
    metrics['type_token_ratio'] = vocab_size / total_tokens if total_tokens > 0 else 0

    # Hapax legomena (words appearing exactly once) - high in real languages
    hapax = sum(1 for c in word_counts.values() if c == 1)
    metrics['hapax_ratio'] = hapax / vocab_size if vocab_size > 0 else 0

    # --- 2. Zipf's law fit ---
    # Real languages follow Zipf's law: rank * frequency ≈ constant
    # Hoaxes and random text deviate significantly
    freqs = sorted(word_counts.values(), reverse=True)
    if len(freqs) > 10:
        ranks = np.arange(1, len(freqs) + 1)
        log_ranks = np.log(ranks)
        log_freqs = np.log(np.array(freqs, dtype=float))

        # Linear fit in log-log space
        coeffs = np.polyfit(log_ranks, log_freqs, 1)
        zipf_slope = coeffs[0]  # Should be ~-1 for real language
        zipf_r2 = np.corrcoef(log_ranks, log_freqs)[0, 1] ** 2

        metrics['zipf_slope'] = round(zipf_slope, 3)
        metrics['zipf_r2'] = round(zipf_r2, 3)
        metrics['zipf_interpretation'] = interpret_zipf(zipf_slope, zipf_r2)

    # --- 3. Entropy metrics ---
    # Real language has intermediate entropy - not too random, not too repetitive
    from collections import Counter as C

    # Word entropy
    total = sum(word_counts.values())
    probs = np.array([c / total for c in word_counts.values()])
    word_entropy = -np.sum(probs * np.log2(probs + 1e-10))
    metrics['word_entropy'] = round(word_entropy, 3)

    # Character entropy
    all_chars = ''.join(lines)
    char_counts = Counter(all_chars)
    total_chars = len(all_chars)
    char_probs = np.array([c / total_chars for c in char_counts.values()])
    char_entropy = -np.sum(char_probs * np.log2(char_probs + 1e-10))
    metrics['char_entropy'] = round(char_entropy, 3)

    # --- 4. Embedding coherence ---
    if embeddings_ngram is not None and len(embeddings_ngram) > 10:
        # Sample similarity to avoid memory issues
        sample_size = min(200, len(embeddings_ngram))
        idx = np.random.choice(len(embeddings_ngram), sample_size, replace=False)
        sample = embeddings_ngram[idx]
        sim_matrix = cosine_similarity(sample)
        np.fill_diagonal(sim_matrix, 0)
        mean_sim = sim_matrix.mean()
        metrics['mean_ngram_similarity'] = round(float(mean_sim), 4)

    print("✅ Structure metrics computed")
    return metrics


def interpret_zipf(slope, r2):
    """Interpret Zipf's law fit."""
    if r2 < 0.7:
        return "Poor fit - unusual for natural language"
    if -1.3 <= slope <= -0.7:
        return "Excellent - consistent with natural language"
    elif -1.6 <= slope <= -0.4:
        return "Good - plausible natural language"
    elif slope > -0.4:
        return "Flat - possibly random or highly repetitive"
    else:
        return "Steep - possibly highly structured/artificial"

# ======================
# STEP 4: CLUSTERING
# ======================

def find_attractors(embeddings, eps=Config.DBSCAN_EPS, min_samples=Config.DBSCAN_MIN_SAMPLES):
    """Find semantic attractors via DBSCAN."""
    print(f"🌀 Finding attractors (eps={eps}, min_samples={min_samples})...")
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeddings)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"✅ Found {n_clusters} attractors + {n_noise} noise points")
    return labels


def summarize_clusters(labels, lines, metadata, top_n=5):
    """Summarize attractors with Voynich-aware context."""
    cluster_map = defaultdict(list)
    for i, label in enumerate(labels):
        cluster_map[label].append((i, lines[i], metadata[i]))

    summaries = {}
    for cluster_id, items in cluster_map.items():
        # Word frequency within cluster
        all_words = []
        for _, text, _ in items:
            all_words.extend(text.replace('.', ' ').split())

        word_counts = Counter(all_words)
        keywords = [w for w, _ in word_counts.most_common(top_n) if len(w) > 1]

        # Section distribution
        section_dist = Counter(meta['section'] for _, _, meta in items)

        summaries[cluster_id] = {
            'size': len(items),
            'keywords': keywords,
            'section_distribution': dict(section_dist),
            'dominant_section': section_dist.most_common(1)[0][0] if section_dist else 'unknown',
            'indices': [i for i, _, _ in items],
            'sample_lines': [text[:80] for _, text, _ in items[:3]],
        }

    return summaries

# ======================
# STEP 5: VISUALIZATION
# ======================

def create_voynich_visualization(
    embeddings_ngram,
    embeddings_semantic,
    labels_ngram,
    labels_semantic,
    metadata,
    sections,
    metrics,
    output_dir
):
    """Create comprehensive Voynich visualization."""
    print("🎨 Creating visualizations...")
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    section_list = [m['section'] for m in metadata]
    section_color_list = [SECTION_COLORS.get(s, SECTION_COLORS['unknown']) for s in section_list]

    fig, axes = plt.subplots(3, 3, figsize=Config.FIGURE_SIZE)
    fig.suptitle('Voynich Manuscript — Semantic Attractor Analysis', fontsize=16, fontweight='bold')

    # --- Plot 1: N-gram trajectory with attractors ---
    ax1 = axes[0, 0]
    if embeddings_ngram is not None:
        coords = _reduce_2d(embeddings_ngram)
        ax1.scatter(coords[:, 0], coords[:, 1],
                   c=labels_ngram, cmap='tab20', s=30, alpha=0.6)
        ax1.set_title('N-gram Attractors')
        ax1.set_xlabel('Dim 1')
        ax1.set_ylabel('Dim 2')
        ax1.grid(True, alpha=0.3)

    # --- Plot 2: Section map (n-gram space) ---
    ax2 = axes[0, 1]
    if embeddings_ngram is not None:
        coords = _reduce_2d(embeddings_ngram)
        ax2.scatter(coords[:, 0], coords[:, 1],
                   c=section_color_list, s=30, alpha=0.6)
        ax2.set_title('Manuscript Sections in N-gram Space')
        ax2.set_xlabel('Dim 1')
        ax2.set_ylabel('Dim 2')
        ax2.grid(True, alpha=0.3)
        # Legend
        patches = [mpatches.Patch(color=v, label=k) for k, v in SECTION_COLORS.items()
                   if k in set(section_list)]
        ax2.legend(handles=patches, fontsize=6, loc='upper right')

    # --- Plot 3: Semantic trajectory ---
    ax3 = axes[0, 2]
    if embeddings_semantic is not None:
        coords_sem = _reduce_2d(embeddings_semantic)
        ax3.scatter(coords_sem[:, 0], coords_sem[:, 1],
                   c=labels_semantic, cmap='tab20', s=30, alpha=0.6)
        ax3.set_title('Semantic Attractors (English model)')
        ax3.set_xlabel('Dim 1')
        ax3.set_ylabel('Dim 2')
        ax3.grid(True, alpha=0.3)

    # --- Plot 4: Attractor sequence over time (n-gram) ---
    ax4 = axes[1, 0]
    if embeddings_ngram is not None:
        t = np.arange(len(labels_ngram))
        ax4.scatter(t, labels_ngram, c=labels_ngram, cmap='tab20', s=20, alpha=0.6)
        ax4.set_title('N-gram Attractor Sequence')
        ax4.set_xlabel('Line Index')
        ax4.set_ylabel('Attractor ID')
        ax4.grid(True, alpha=0.3)

    # --- Plot 5: Section sequence over time ---
    ax5 = axes[1, 1]
    section_ids = [list(SECTION_COLORS.keys()).index(s)
                   if s in SECTION_COLORS else len(SECTION_COLORS)
                   for s in section_list]
    ax5.scatter(np.arange(len(section_ids)), section_ids,
               c=section_color_list, s=20, alpha=0.7)
    ax5.set_title('Section Sequence Over Time')
    ax5.set_xlabel('Line Index')
    ax5.set_ylabel('Section')
    ax5.set_yticks(range(len(SECTION_COLORS)))
    ax5.set_yticklabels(list(SECTION_COLORS.keys()), fontsize=7)
    ax5.grid(True, alpha=0.3)

    # --- Plot 6: N-gram recurrence matrix ---
    ax6 = axes[1, 2]
    if embeddings_ngram is not None:
        _plot_recurrence(embeddings_ngram, ax6, 'N-gram Recurrence Matrix')

    # --- Plot 7: Semantic recurrence matrix ---
    ax7 = axes[2, 0]
    if embeddings_semantic is not None:
        _plot_recurrence(embeddings_semantic, ax7, 'Semantic Recurrence Matrix')

    # --- Plot 8: Zipf's law ---
    ax8 = axes[2, 1]
    all_words = []
    for line in [m['original'] for m in metadata]:
        # Use preprocessed space-separated tokens
        words = line.replace('.', ' ').replace('-', '').replace('=', '').split()
        all_words.extend(words)
    word_counts = Counter(all_words)
    freqs = sorted(word_counts.values(), reverse=True)[:500]
    ranks = np.arange(1, len(freqs) + 1)
    ax8.loglog(ranks, freqs, 'b.', alpha=0.5, markersize=3, label='Voynich')
    # Ideal Zipf reference line
    ideal = freqs[0] / ranks
    ax8.loglog(ranks, ideal, 'r--', alpha=0.7, label="Ideal Zipf (slope=-1)")
    ax8.set_title("Zipf's Law Distribution")
    ax8.set_xlabel('Rank (log)')
    ax8.set_ylabel('Frequency (log)')
    ax8.legend(fontsize=8)
    ax8.grid(True, alpha=0.3)

    # --- Plot 9: Structure metrics summary ---
    ax9 = axes[2, 2]
    ax9.axis('off')
    metric_text = "STRUCTURE METRICS\n" + "─" * 30 + "\n"
    display_metrics = [
        ('Vocabulary size', 'vocab_size', ''),
        ('Total tokens', 'total_tokens', ''),
        ('Type/token ratio', 'type_token_ratio', '.3f'),
        ('Hapax ratio', 'hapax_ratio', '.3f'),
        ('Zipf slope', 'zipf_slope', ''),
        ('Zipf R²', 'zipf_r2', ''),
        ('Word entropy', 'word_entropy', ''),
        ('Char entropy', 'char_entropy', ''),
    ]
    for label, key, fmt in display_metrics:
        val = metrics.get(key, 'N/A')
        if fmt and isinstance(val, float):
            metric_text += f"{label}: {val:{fmt}}\n"
        else:
            metric_text += f"{label}: {val}\n"

    if 'zipf_interpretation' in metrics:
        metric_text += f"\nZipf: {metrics['zipf_interpretation']}"

    ax9.text(0.05, 0.95, metric_text, transform=ax9.transAxes,
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    viz_path = output_path / 'voynich_trajectory.png'
    plt.savefig(viz_path, dpi=Config.DPI, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved visualization: {viz_path}")


def _reduce_2d(embeddings):
    """Reduce to 2D via PCA → TSNE."""
    n_components = min(50, embeddings.shape[1], len(embeddings) - 1)
    if n_components < 2:
        return embeddings[:, :2]
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(embeddings)
    perplexity = min(30, len(embeddings) - 1)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    return tsne.fit_transform(reduced)


def _plot_recurrence(embeddings, ax, title):
    """Plot recurrence matrix, subsampled for large corpora."""
    max_points = 400
    if len(embeddings) > max_points:
        idx = np.linspace(0, len(embeddings) - 1, max_points).astype(int)
        sample = embeddings[idx]
    else:
        sample = embeddings

    sim = cosine_similarity(sample)
    im = ax.imshow(sim, cmap='viridis', aspect='auto')
    ax.set_title(title)
    ax.set_xlabel('Line Index')
    ax.set_ylabel('Line Index')
    plt.colorbar(im, ax=ax, label='Cosine Similarity')

# ======================
# STEP 6: REPORT
# ======================

def create_report(summaries_ngram, labels_ngram, lines, metadata, metrics, output_dir):
    """Create attractor report."""
    print("📝 Creating report...")
    output_path = Path(output_dir)

    report = []
    report.append("=" * 80)
    report.append("VOYNICH MANUSCRIPT — SEMANTIC ATTRACTOR ANALYSIS")
    report.append("=" * 80)
    report.append("")

    # Structure assessment
    report.append("📊 LANGUAGE STRUCTURE ASSESSMENT")
    report.append("-" * 40)
    for k, v in metrics.items():
        report.append(f"  {k}: {v}")
    report.append("")

    # Attractor summary
    report.append("🌀 N-GRAM ATTRACTORS")
    report.append("-" * 40)
    sorted_clusters = sorted(summaries_ngram.items(), key=lambda x: x[1]['size'], reverse=True)

    for cluster_id, info in sorted_clusters[:20]:  # Top 20
        if cluster_id == -1:
            report.append(f"🕳  NOISE ({info['size']} lines)")
        else:
            report.append(f"🌀 ATTRACTOR {cluster_id} ({info['size']} lines)")
        report.append(f"   Keywords: {', '.join(info['keywords'])}")
        report.append(f"   Dominant section: {info['dominant_section']}")
        report.append(f"   Section distribution: {info['section_distribution']}")
        for line in info['sample_lines']:
            report.append(f"   • {line}...")
        report.append("")

    # Statistics
    report.append("=" * 80)
    report.append("STATISTICS")
    report.append("=" * 80)
    report.append(f"Total lines: {len(lines)}")
    n_attractors = len([c for c in summaries_ngram if c != -1])
    report.append(f"N-gram attractors: {n_attractors}")
    noise = summaries_ngram.get(-1, {}).get('size', 0)
    report.append(f"Noise points: {noise} ({100*noise/len(lines):.1f}%)")
    transitions = sum(1 for i in range(1, len(labels_ngram)) if labels_ngram[i] != labels_ngram[i-1])
    report.append(f"Attractor transitions: {transitions}")

    report_text = "\n".join(report)
    report_path = output_path / 'voynich_attractor_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"✅ Saved report: {report_path}")
    print("\n" + report_text[:2000])  # Preview

# ======================
# MAIN PIPELINE
# ======================

def analyze_voynich(input_file, output_dir=Config.OUTPUT_DIR, section_filter=None):
    """Full Voynich analysis pipeline."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print("\n" + "=" * 80)
    print("🔮 VOYNICH NAVIGATOR")
    print("=" * 80 + "\n")

    if Config.USE_GPU:
        print("⚡ GPU acceleration: ENABLED")
    print()

    # Parse
    lines, metadata, sections = parse_eva_transcription(input_file)

    # Optional section filter
    if section_filter and section_filter in sections:
        idx = sections[section_filter]
        lines = [lines[i] for i in idx]
        metadata = [metadata[i] for i in idx]
        print(f"🔍 Filtered to section '{section_filter}': {len(lines)} lines")

    if len(lines) < 10:
        print("❌ Too few lines to analyze. Check input file format.")
        return

    # Dual embedding
    embeddings_ngram, vectorizer = embed_ngrams(lines)
    embeddings_semantic = embed_semantic(lines)

    # Structure metrics
    metrics = compute_structure_metrics(lines, metadata, embeddings_ngram, embeddings_semantic)

    # Clustering
    labels_ngram = find_attractors(embeddings_ngram) if embeddings_ngram is not None else np.full(len(lines), -1)
    labels_semantic = find_attractors(embeddings_semantic) if embeddings_semantic is not None else np.full(len(lines), -1)

    # Summarize
    summaries_ngram = summarize_clusters(labels_ngram, lines, metadata)

    # Visualize
    create_voynich_visualization(
        embeddings_ngram, embeddings_semantic,
        labels_ngram, labels_semantic,
        metadata, sections, metrics, output_dir
    )

    # Report
    create_report(summaries_ngram, labels_ngram, lines, metadata, metrics, output_dir)

    print("\n" + "=" * 80)
    print("✅ VOYNICH ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {output_path.absolute()}")

# ======================
# CLI
# ======================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Voynich Manuscript semantic attractor analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis
  python voynich_navigator.py --input interln16e6.txt

  # Single section
  python voynich_navigator.py --input interln16e6.txt --section herbal_a

  # Custom output dir
  python voynich_navigator.py --input interln16e6.txt --output my_analysis

Available sections:
  herbal_a, astronomical, biological, cosmological,
  herbal_b, pharmaceutical, recipes
        """
    )
    parser.add_argument('--input', '-i', required=True,
                       help='EVA transcription file (e.g. interln16e6.txt)')
    parser.add_argument('--output', '-o', default=Config.OUTPUT_DIR,
                       help='Output directory')
    parser.add_argument('--section', '-s', default=None,
                       help='Analyze specific section only')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable embedding cache')
    parser.add_argument('--no-gpu', action='store_true',
                       help='Disable GPU')

    args = parser.parse_args()

    if args.no_cache:
        Config.USE_CACHE = False
    if args.no_gpu:
        Config.USE_GPU = False

    analyze_voynich(args.input, args.output, args.section)
