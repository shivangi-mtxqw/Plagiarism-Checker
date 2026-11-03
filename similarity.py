"""Plagiarism similarity logic built on KMP and Rabin-Karp."""
import re
import time

from kmp import kmp_search
from rabin_karp import rabin_karp_search


def normalize(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """Split raw text into sentences (on . ! ? and newlines)."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _search(algorithm, text, pattern):
    """Run the chosen algorithm. Returns (found, comparisons, spurious)."""
    if algorithm == "KMP":
        idx, comps = kmp_search(text, pattern)
        return bool(idx), comps, 0
    idx, comps, spur = rabin_karp_search(text, pattern)
    return bool(idx), comps, spur


def analyze(doc_a, doc_b, algorithm="KMP", min_words=4):
    """Check each sentence of doc_a for an exact (normalized) match in doc_b.

    Similarity % = words in matched sentences / total words in doc_a * 100.
    Sentences shorter than `min_words` are skipped to avoid trivial matches.
    """
    padded_b = " " + normalize(doc_b) + " "  # padding => whole-word matches only
    results, total_words, matched_words = [], 0, 0
    comparisons = spurious = 0

    start = time.perf_counter()
    for sentence in split_sentences(doc_a):
        norm = normalize(sentence)
        words = len(norm.split())
        if words < min_words:
            results.append({"sentence": sentence, "matched": False, "skipped": True})
            continue
        total_words += words
        found, c, s = _search(algorithm, padded_b, " " + norm + " ")
        comparisons += c
        spurious += s
        if found:
            matched_words += words
        results.append({"sentence": sentence, "matched": found, "skipped": False})
    elapsed = time.perf_counter() - start

    pct = (matched_words / total_words * 100) if total_words else 0.0
    return {
        "algorithm": algorithm,
        "similarity": round(pct, 2),
        "matched_sentences": sum(r["matched"] for r in results),
        "checked_sentences": sum(not r["skipped"] for r in results),
        "time_ms": elapsed * 1000,
        "comparisons": comparisons,
        "spurious_hits": spurious,
        "results": results,
    }


def compare_algorithms(doc_a, doc_b, min_words=4, repeats=5):
    """Run both algorithms; average the timing over several repeats."""
    out = {}
    for algo in ("KMP", "Rabin-Karp"):
        runs = [analyze(doc_a, doc_b, algo, min_words) for _ in range(repeats)]
        best = runs[0]
        best["time_ms"] = sum(r["time_ms"] for r in runs) / repeats
        out[algo] = best
    return out


def verdict(pct):
    if pct < 20:
        return "Low similarity - likely original"
    if pct < 50:
        return "Moderate similarity - review recommended"
    return "High similarity - possible plagiarism"