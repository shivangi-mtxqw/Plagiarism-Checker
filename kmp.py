"""Knuth-Morris-Pratt (KMP) string matching. Time: O(n + m), Space: O(m)."""


def compute_lps(pattern):
    """Build the Longest Proper Prefix which is also Suffix (LPS) table."""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]  # fall back, do not advance i
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text, pattern):
    """Return (list of start indices of pattern in text, comparison count)."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return [], 0

    lps = compute_lps(pattern)
    matches, comparisons = [], 0
    i = j = 0
    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                matches.append(i - j)
                j = lps[j - 1]
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1
    return matches, comparisons