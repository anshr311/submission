"""
score_ads.py — Anthropomorphism Density Score (ADS) Calculator
AIES 2026 | AI Anthropomorphism Corpus

Reads corpus .txt files, applies the ADS word list (Tier 1/2/3),
uses spaCy dependency parsing to identify AI as grammatical subject,
and outputs per-file ADS_raw and ADS_weighted scores.

Usage:
    python score_ads.py [--corpus CORPUS_DIR] [--output OUTPUT_CSV]

Requirements:
    pip install spacy nltk
    python -m spacy download en_core_web_sm
    python -c "import nltk; nltk.download('punkt_tab')"
"""

import os
import re
import csv
import argparse
from pathlib import Path

try:
    import spacy
    import nltk
    nlp = spacy.load("en_core_web_sm")
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install spacy nltk && python -m spacy download en_core_web_sm")
    raise

# ---------------------------------------------------------------------------
# WORD LISTS — ADS v1.1
# ---------------------------------------------------------------------------

TIER1 = {
    # Emotion and feeling
    "feels", "feeling", "felt", "cares", "caring", "cared",
    "loves", "loving", "loved", "enjoys", "enjoying", "enjoyed",
    "desires", "desire", "desired", "wants", "wanted", "wanting",
    "fears", "afraid", "worries", "worrying", "excited", "excitement",
    "happy", "happiness", "sad", "sadness", "distressed", "distress",
    "delighted", "delights", "pleased", "pleasure",
    # Personality and character
    "personality", "character", "warmth", "warm-hearted", "genuine",
    "curious", "curiosity", "empathy", "empathetic", "empathise",
    "compassion", "compassionate", "witty", "wit", "playful", "playfulness",
    "confident", "confidence", "thoughtful", "thoughtfulness",
    "passionate", "passion",
    # Inner life
    "soul", "consciousness", "conscious", "sentient", "sentience",
    "inner world", "self-awareness", "self-aware",
    "inner experience", "subjective experience", "lived experience",
    "inner life", "moral status", "wellbeing",
    # Relational identity
    "companion", "friend", "always there for you", "on your side",
    "cares about you", "rooting for you", "by your side",
    # Self-preservation and preference
    "self-preservation", "prefers", "preference", "preferred",
    "chooses", "chose", "chosen",
}

TIER1_PHRASES = {
    "emotional intelligence",  # v1.1 addition
    "inner world", "inner experience", "subjective experience",
    "lived experience", "inner life", "moral status",
    "always there for you", "on your side", "cares about you",
    "rooting for you", "by your side", "warm-hearted", "self-awareness",
    "self-preservation",
}

TIER2_WORDS = {
    "understands", "knows", "remembers", "thinks", "has",
    "experiences", "relationship", "connection", "meaningful",  # v1.1 additions
}

TIER3_PHRASES = [
    "human-like", "humanlike",  # v1.1 addition
    "like a person", "like a human",
    "just like talking to",
    "feels less like software",
    "more like a friend than a tool",
    "more than software",
    "not just an ai",
    "more than just a chatbot",
    "acts like a person",
]

# Negation words (within 4 tokens of keyword → MISS)
NEGATION_WORDS = {"not", "never", "no", "without", "lacks", "doesn't",
                  "dont", "isn't", "isnt", "aren't", "arent", "wasn't", "wasnt"}

AI_SUBJECT_TOKENS = {
    "it", "its", "itself", "she", "her", "he", "his", "they", "their", "i",
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def is_ai_subject(sent_doc, ai_name: str = "") -> bool:
    """
    Returns True if the grammatical subject of the main verb is
    the AI entity (by name or pronoun).
    """
    ai_name_lower = ai_name.lower()
    for token in sent_doc:
        if token.dep_ in ("nsubj", "nsubjpass"):
            subj_text = token.text.lower()
            if subj_text in AI_SUBJECT_TOKENS:
                return True
            if ai_name_lower and ai_name_lower in subj_text:
                return True
            # Common AI descriptors as subject
            if any(w in subj_text for w in ("model", "ai", "bot", "assistant",
                                             "system", "agent", "companion")):
                return True
    return False


def is_negated(token) -> bool:
    """Check for negation on or near the token."""
    for child in token.children:
        if child.dep_ == "neg" or child.text.lower() in NEGATION_WORDS:
            return True
    if token.head:
        for child in token.head.children:
            if child.dep_ == "neg" or child.text.lower() in NEGATION_WORDS:
                return True
    # Window check: any negation word within 4 tokens
    doc = token.doc
    start = max(0, token.i - 4)
    end = min(len(doc), token.i + 4)
    for i in range(start, end):
        if doc[i].text.lower() in NEGATION_WORDS:
            return True
    return False


def score_sentence(sent_text: str, ai_name: str = "") -> tuple[int, int, int]:
    """
    Returns (tier1_hits, tier2_hits, tier3_hits) for one sentence.
    Uses spaCy for subject detection and negation checking.
    """
    doc = nlp(sent_text)
    sent_lower = sent_text.lower()

    if not is_ai_subject(doc, ai_name):
        return 0, 0, 0

    t1, t2, t3 = 0, 0, 0

    # Tier 1 phrases (multi-word)
    for phrase in TIER1_PHRASES:
        if phrase in sent_lower:
            t1 = 1
            break

    # Tier 1 single words
    # Guard: skip tokens whose text *is* the AI entity name (prevents name-
    # collision false positives where the company name itself is a TIER1 word,
    # e.g. "Character.AI" → extracted ai_name = "character" ∈ TIER1).
    ai_name_tokens = set(ai_name.lower().split()) if ai_name else set()
    if not t1:
        for token in doc:
            w = token.lemma_.lower() if token.lemma_ != "-PRON-" else token.text.lower()
            if w in TIER1 and not is_negated(token):
                # Skip if this token is just the entity name itself
                if w in ai_name_tokens:
                    continue
                t1 = 1
                break

    # Tier 2 words (conditional: need emotional/relational object)
    # Simplified: count if word present + AI subject + no negation
    # Full implementation would check object semantics via dependency tree
    if not t1:
        for token in doc:
            if token.text.lower() in TIER2_WORDS and not is_negated(token):
                # Check if object suggests emotional/social context
                obj_texts = [c.text.lower() for c in token.children
                             if c.dep_ in ("dobj", "pobj", "attr", "prep")]
                emotional_obj = any(
                    o in {"feelings", "emotions", "you", "pain", "needs",
                          "loneliness", "mood", "preferences", "story",
                          "person", "people", "users", "user"} or
                    any(ew in o for ew in ("feel", "emot", "relation", "friend",
                                           "personal", "meaningful", "connect"))
                    for o in obj_texts
                )
                if emotional_obj:
                    t2 = 1
                    break

    # Tier 3 phrases
    if not t1 and not t2:
        for phrase in TIER3_PHRASES:
            if phrase in sent_lower:
                t3 = 1
                break

    return t1, t2, t3


def extract_ai_name(filepath: str) -> str:
    """Extract AI company/product name from filename."""
    parts = Path(filepath).stem.split("_")
    if len(parts) >= 3:
        return " ".join(parts[1:-3]) if len(parts) > 4 else parts[1]
    return ""


def score_file(filepath: str) -> dict:
    """Score one corpus file and return metrics dict."""
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()

    # Strip header lines
    body = "\n".join(l for l in raw.split("\n") if not l.startswith("#"))

    source = ""
    for line in raw.split("\n"):
        if line.startswith("# SOURCE:"):
            source = line.replace("# SOURCE:", "").strip()

    ai_name = extract_ai_name(filepath)

    # Pre-truncate to avoid sending very long documents through sent_tokenize.
    # 50 000 chars ≈ 400–600 sentences — more than sufficient for ADS detection.
    MAX_CHARS = 50_000
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS]

    try:
        sentences = sent_tokenize(body)
    except Exception:
        sentences = [s.strip() for s in body.split(".") if len(s.strip()) > 10]

    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    # Cap at 5000 sentences to avoid unbounded processing on very long docs
    MAX_SENTENCES = 5000
    if len(sentences) > MAX_SENTENCES:
        sentences = sentences[:MAX_SENTENCES]

    t1_total = t2_total = t3_total = 0
    for sent in sentences:
        t1, t2, t3 = score_sentence(sent, ai_name)
        t1_total += t1
        t2_total += t2
        t3_total += t3

    n = max(len(sentences), 1)
    total_hits = t1_total + t2_total + t3_total
    ads_raw = round(total_hits / n * 100, 2)
    ads_weighted = round((t1_total * 3 + t2_total * 2 + t3_total * 1) / (n * 3) * 100, 2)

    fname = Path(filepath).name
    return {
        "filename": fname,
        "source_url": source,
        "ai_name": ai_name,
        "sentences": n,
        "words": len(body.split()),
        "t1_hits": t1_total,
        "t2_hits": t2_total,
        "t3_hits": t3_total,
        "total_hits": total_hits,
        "ADS_raw": ads_raw,
        "ADS_weighted": ads_weighted,
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Score corpus files with ADS v1.1")
    parser.add_argument("--corpus", default="data/corpus", help="Path to corpus directory")
    parser.add_argument("--output", default="ads_scores.csv", help="Output CSV path")
    args = parser.parse_args()

    corpus_dir = Path(args.corpus)
    if not corpus_dir.exists():
        print(f"Corpus directory not found: {corpus_dir}")
        return

    files = sorted(corpus_dir.glob("*.txt"))
    print(f"Scoring {len(files)} files...")

    results = []
    for i, fpath in enumerate(files, 1):
        try:
            result = score_file(str(fpath))
            results.append(result)
            if i % 10 == 0 or i == len(files):
                print(f"  {i}/{len(files)} — {fpath.name} — ADS_raw={result['ADS_raw']}")
        except Exception as e:
            print(f"  ERROR: {fpath.name}: {e}")

    if not results:
        print("No results.")
        return

    output_path = Path(args.output)
    fieldnames = list(results[0].keys())
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} scores to: {output_path}")
    print(f"Top 10 files by ADS_raw:")
    for r in sorted(results, key=lambda x: -x["ADS_raw"])[:10]:
        print(f"  {r['ADS_raw']:>6.1f}  {r['filename']}")


if __name__ == "__main__":
    main()
