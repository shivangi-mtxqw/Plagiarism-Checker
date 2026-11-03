"""Rabin-Karp string matching using a rolling hash.
Average: O(n + m), Worst case: O(n * m) when many spurious hits occur."""


def rabin_karp_search(text, pattern, d=256, q=1_000_003):
    """Return (list of start indices, comparison count, spurious hit count).

    d: alphabet size, q: prime modulus. comparisons counts hash comparisons
    plus character comparisons made when verifying a hash match.
    """
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return [], 0, 0

    h = pow(d, m - 1, q)          # weight of the leading character
    p_hash = t_hash = 0
    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % q
        t_hash = (d * t_hash + ord(text[i])) % q

    matches, comparisons, spurious = [], 0, 0
    for i in range(n - m + 1):
        comparisons += 1                      # hash comparison
        if p_hash == t_hash:
            comparisons += m                  # verify character by character
            if text[i:i + m] == pattern:
                matches.append(i)
            else:
                spurious += 1
        if i < n - m:                         # roll the hash forward
            t_hash = (d * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % q
    return matches, comparisons, spurious