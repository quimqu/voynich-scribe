# Còpia literal de les funcions del notebook pm-cipher.ipynb (Kaggle, set. 2025): cel·les 4, 6, 7, 8, 9, 11 i 13, només les definicions.
# Les variables globals que el notebook feia servir (voynich_words, LATIN_ALPHABET, RNG, voy_H) les posa set_globals().
import os, re, math, random, copy
from collections import Counter, defaultdict
import numpy as np
from scipy.spatial.distance import jensenshannon
RNG = random.Random(42)
LATIN_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
voynich_words = []
voy_H = [float("nan")] * 5
def set_globals(vw, seed=42):
    global voynich_words, voy_H, RNG
    voynich_words = vw; RNG = random.Random(seed); np.random.seed(seed)
    voy_H = entropy_curve(vw, max_n=5)

def encode_chars(words):
    """
    Map characters to integer indices and encode each word as a list of indices.
    Returns:
        - char_to_idx: dict mapping character -> int index
        - idx_to_char: dict mapping int index -> character
        - encoded_words: list of lists (one list of indices per word)
        - flat_seq: single flattened list of all indices (concatenation of words)
    Notes:
        - The vocabulary is derived from the set of characters present in `words`.
        - Empty strings are ignored when encoding.
    """
    vocab = sorted(set("".join(words)))
    char_to_idx = {ch: i for i, ch in enumerate(vocab)}
    idx_to_char = {i: ch for ch, i in char_to_idx.items()}
    encoded_words = [[char_to_idx[ch] for ch in w] for w in words if w]
    flat_seq = [idx for w in encoded_words for idx in w]
    return char_to_idx, idx_to_char, encoded_words, flat_seq

def entropy_word_reset(words, n):
    """
    Compute n-gram entropy (in bits) with word resets (contexts do not cross word boundaries).

    Method:
        - Build conditional distributions P(x_t | context) for contexts of length n-1 inside words.
        - Evaluate the negative log2 probability of each observed n-gram under these conditionals.
        - Average over all observed positions.

    Fallback:
        - If a (context, target) pair is unseen, use a uniform fallback over the vocabulary (1/V),
          which is a conservative choice that avoids over-penalizing rare events.
    """
    char_to_idx, idx_to_char, encoded_words, _ = encode_chars(words)
    V = len(char_to_idx)
    if V == 0:
        return float("nan")

    # Count occurrences per context
    ngram_counts = defaultdict(Counter)
    context_counts = Counter()

    for w in encoded_words:
        if len(w) < n:
            continue
        for i in range(len(w) - n + 1):
            context = tuple(w[i:i + n - 1]) if n > 1 else tuple()
            target = w[i + n - 1]
            ngram_counts[context][target] += 1
            context_counts[context] += 1

    total_log_prob = 0.0
    total_positions = 0
    fallback_prob = 1.0 / V  # uniform fallback over symbols

    for w in encoded_words:
        if len(w) < n:
            continue
        for i in range(len(w) - n + 1):
            context = tuple(w[i:i + n - 1]) if n > 1 else tuple()
            target = w[i + n - 1]
            context_total = context_counts.get(context, 0)
            target_count = ngram_counts[context].get(target, 0)
            prob = (target_count / context_total) if (context_total > 0 and target_count > 0) else fallback_prob
            total_log_prob += -math.log2(prob)
            total_positions += 1

    if total_positions == 0:
        return float("nan")
    return total_log_prob / total_positions

def entropy_curve(words, max_n=5):
    """
    Compute entropies for n = 1..max_n using word resets.
    Returns a list [H1, H2, ..., H_max_n].
    """
    return [entropy_word_reset(words, n) for n in range(1, max_n + 1)]

def bigram_matrix(words):
    """
    Compute a bigram matrix with word resets (no cross-word bigrams).
    Returns:
        - M: (V x V) numpy array with normalized probabilities P(next | current) * P(current)
             flattened normalization (i.e., M / M.sum()) to compare distributions globally.
        - vocab: list of characters in the order used by M indices.
    """
    vocab = sorted(set("".join(words)))
    idx = {ch: i for i, ch in enumerate(vocab)}
    M = np.zeros((len(vocab), len(vocab)), dtype=float)

    for w in words:
        for a, b in zip(w, w[1:]):
            M[idx[a], idx[b]] += 1.0

    # Normalize to a probability distribution over all bigrams (avoid division by zero)
    total = M.sum()
    if total > 0:
        M = M / total
    return M, vocab

def js_divergence(P, Q):
    """
    Jensen–Shannon divergence between two (possibly multidimensional) distributions.
    Inputs:
        - P, Q: numpy arrays; they will be flattened and normalized to sum to 1.
    Output:
        - JS divergence (not distance), i.e., jensenshannon(...) ** 2
    """
    eps = 1e-12
    p = P.flatten().astype(float) + eps
    q = Q.flatten().astype(float) + eps
    p = p / p.sum()
    q = q / q.sum()
    # scipy.spatial.distance.jensenshannon returns the JS distance; square it to get divergence
    return jensenshannon(p, q) ** 2

def position_profile(words):
    """
    Build positional character profiles.

    Returns:
        - counts: dict[int -> Counter], where counts[i][ch] is the count of character `ch`
          appearing at 0-based position i within words.
        - probs: dict[int -> dict], where probs[i][ch] is the normalized probability of `ch`
          at position i (row-wise normalization of `counts`).

    Notes:
        - Positions are 0-based within each word.
        - Empty words (if any) are safely ignored.
    """
    counts = defaultdict(Counter)
    for w in words:
        if not w:
            continue
        for i, ch in enumerate(w):
            counts[i][ch] += 1

    probs = {}
    for i, cnt in counts.items():
        total = sum(cnt.values())
        probs[i] = {ch: c / total for ch, c in cnt.items()} if total else {}

    return counts, probs

class PMCipher:
    """
    Positional Mimic Cipher.

    Overview
    --------
    - Maintains per-position maps: token -> glyph (positional_map) and the reverse (reverse_map).
    - Tokens can be single letters (default) and, optionally, selected n-grams from the plaintext.
    - Residuals resolve one-to-many mappings (several tokens mapped to the same glyph at a position).

    Parameters
    ----------
    latin_alphabet : iterable of str
        Allowed plaintext symbols (e.g., lowercase Latin letters).
    voynich_words : list of str
        Voynich wordlist used to derive positional glyph distributions.
    target_collision : int, default=3
        Approximate number of tokens that should share a glyph at a position (controls K).
    strategy : str, default="greedy"
        Placeholder for alternative assignment strategies (currently only greedy fill is implemented).
    use_ngrams : bool, default=False
        If True, select frequent plaintext n-grams as tokens in addition to single letters.
    ngram_ns : tuple, default=(2, 3)
        N-gram sizes to consider if `use_ngrams` is True.
    top_k_per_n : int, default=100
        Maximum number of top n-grams to include per n.
    min_freq : int, default=50
        Minimum frequency threshold for including an n-gram token.

    Notes
    -----
    - Random choices use the module-level RNG (seeded earlier) to keep runs reproducible.
    """

    def __init__(
        self,
        latin_alphabet,
        voynich_words,
        target_collision=3,
        strategy="greedy",
        use_ngrams=False,      # keep False for letter-by-letter trials
        ngram_ns=(2, 3),
        top_k_per_n=100,
        min_freq=50,
    ):
        self.latin = list(latin_alphabet)
        self.voy_words = voynich_words
        self.target_collision = max(1, int(target_collision))
        self.strategy = strategy
        self.use_ngrams = use_ngrams
        self.ngram_ns = tuple(sorted(set(ngram_ns)))
        self.top_k_per_n = int(top_k_per_n)
        self.min_freq = int(min_freq)

        # Voynich positional profiles
        self.voy_prof_cnt, self.voy_prof = position_profile(self.voy_words)

        # Available Voynich glyphs per position (fallback to global vocab if missing)
        self.voy_chars_by_pos = {i: sorted(self.voy_prof_cnt[i].keys())
                                 for i in self.voy_prof_cnt.keys()}
        self.max_pos = max(self.voy_chars_by_pos.keys()) if self.voy_chars_by_pos else 0

        self.positional_map = {}
        self.reverse_map = {}
        self.residual_bases = {}
        self.tokens = list(self.latin)

    @staticmethod
    def _count_ngrams(words, n):
        """Count contiguous character n-grams within words (no cross-word n-grams)."""
        c = Counter()
        for w in words:
            if len(w) < n:
                continue
            for i in range(len(w) - n + 1):
                c[w[i:i + n]] += 1
        return c

    def _select_ngrams(self, plaintext_words):
        """
        Select frequent n-grams from plaintext according to thresholds.
        Returns a set of n-gram tokens limited to characters in self.latin.
        """
        if not self.use_ngrams:
            return set()
        selected = set()
        for n in self.ngram_ns:
            cnt = self._count_ngrams(plaintext_words, n)
            items = [(tok, f) for tok, f in cnt.items() if f >= self.min_freq]
            items.sort(key=lambda x: x[1], reverse=True)
            top = [tok for tok, _ in items[:self.top_k_per_n]]
            selected.update(top)
        # Keep only tokens made of allowed Latin characters
        selected = {t for t in selected if all(ch in self.latin for ch in t)}
        return selected

    def _greedy_tokenize(self, word, ngram_set):
        """
        Greedy longest-match tokenization using the n-gram set.
        Non-Latin characters are passed through as literal 1-char tokens (marked with residual -1 at encryption).
        Returns a list of (position_in_word, token).
        """
        i = 0
        out = []
        max_n = max([1] + [len(t) for t in ngram_set]) if ngram_set else 1
        while i < len(word):
            if word[i] not in self.latin:
                out.append((i, word[i]))
                i += 1
                continue
            matched = None
            for L in range(min(max_n, len(word) - i), 1, -1):
                cand = word[i:i + L]
                if cand in ngram_set:
                    matched = cand
                    break
            if matched is None:
                matched = word[i]
            out.append((i, matched))
            i += len(matched)
        return out

    def fit(self, plaintext_words):
        """
        Build per-position token -> glyph assignments to mimic Voynich positional distributions.

        Steps:
        1) (Optional) select frequent plaintext n-grams to augment the token set.
        2) Count per-position token demand via greedy tokenization of plaintext.
        3) For each position:
           - Choose a limited set of glyphs (K) according to Voynich positional frequencies
             and the `target_collision` (tokens per glyph) heuristic.
           - Allocate capacity per glyph proportional to Voynich positional probabilities.
           - Fill glyph “buckets” with tokens by descending plaintext frequency.
           - Assign any remaining rare tokens by random fill into chosen glyphs.
        4) Build reverse maps for deterministic decoding via “residuals”.

        Returns:
            self
        """
        # 1) Token set: letters + optional n-grams
        ngram_set = self._select_ngrams(plaintext_words)
        self.tokens = sorted(set(self.latin) | ngram_set, key=lambda t: (len(t), t))

        # 2) Demand per position from plaintext
        demand_by_pos = defaultdict(Counter)
        for w in plaintext_words:
            for pos, tok in self._greedy_tokenize(w, ngram_set):
                demand_by_pos[pos][tok] += 1

        voynich_vocab = sorted(set("".join(self.voy_words)))

        positional_map = {}
        reverse_map = {}
        residual_bases = {}

        all_positions = sorted(set(list(self.voy_prof.keys()) + list(demand_by_pos.keys())))
        max_pos = max(all_positions) if all_positions else 0

        for pos in range(max_pos + 1):
            demand = demand_by_pos.get(pos, Counter())

            # If no demand at this position, still assign a default mapping so encryption won't fail
            if not demand:
                pmap = {}
                rmap = defaultdict(list)
                chosen_glyphs = self.voy_chars_by_pos.get(pos, voynich_vocab)
                for tok in self.tokens:
                    g = RNG.choice(chosen_glyphs) if chosen_glyphs else RNG.choice(voynich_vocab)
                    pmap[tok] = g
                    rmap[g].append(tok)
                positional_map[pos] = pmap
                reverse_map[pos] = rmap
                residual_bases[pos] = max(1, max(len(v) for v in rmap.values()))
                continue

            tokens_by_freq = [t for t, _ in demand.most_common()]

            # Voynich positional distribution for this position (fallback to global distribution)
            voy_pos_dist = self.voy_prof.get(pos, {})
            if not voy_pos_dist:
                global_cnt = Counter("".join(self.voy_words))
                total = sum(global_cnt.values())
                voy_pos_dist = {c: (global_cnt[c] / total) for c in global_cnt}

            sorted_glyphs = [g for g, _ in sorted(voy_pos_dist.items(), key=lambda x: x[1], reverse=True)]
            if not sorted_glyphs:
                sorted_glyphs = voynich_vocab[:]

            # Determine K = number of glyphs to use at this position (capped)
            L = len(tokens_by_freq)
            K = max(1, int(round(L / max(1, self.target_collision))))
            max_K = 12
            K = min(K, len(sorted_glyphs), max_K)
            chosen_glyphs = sorted_glyphs[:K]

            # Per-glyph capacities proportional to Voynich positional probabilities
            p = np.array([voy_pos_dist[g] for g in chosen_glyphs], dtype=float)
            p = p / p.sum() if p.sum() > 0 else np.ones(len(chosen_glyphs)) / len(chosen_glyphs)
            caps = np.maximum(1, np.round(p * L).astype(int))

            # Adjust rounding so total capacity equals number of tokens to place
            while caps.sum() < L:
                caps[int(np.argmax(p))] += 1
            while caps.sum() > L:
                j = int(np.argmax(caps))
                if caps[j] > 1:
                    caps[j] -= 1
                else:
                    break

            # Fill buckets with tokens by descending frequency
            buckets_map = {g: [] for g in chosen_glyphs}
            cursor = 0
            for g, cap in zip(chosen_glyphs, caps):
                for _ in range(int(cap)):
                    if cursor < L:
                        buckets_map[g].append(tokens_by_freq[cursor])
                        cursor += 1

            # Build forward and reverse maps
            pmap = {}
            rmap = defaultdict(list)
            for g, toks in buckets_map.items():
                for t in toks:
                    pmap[t] = g
                rmap[g] = list(toks)

            # Assign any tokens not covered (very rare ones) to random chosen glyphs
            for t in self.tokens:
                if t not in pmap:
                    g = RNG.choice(chosen_glyphs)
                    pmap[t] = g
                    rmap[g].append(t)

            positional_map[pos] = pmap
            reverse_map[pos] = rmap
            residual_bases[pos] = max(1, max((len(v) for v in rmap.values()), default=1))

        self.positional_map = positional_map
        self.reverse_map = reverse_map
        self.residual_bases = residual_bases
        return self

    def encrypt_word(self, word):
        """
        Encrypt a single plaintext word.
        Returns:
            - cipher (str): concatenated glyphs
            - residuals (list[int]): index within reverse_map bucket per position; -1 for passthrough chars
        """
        cipher = []
        residuals = []
        ngram_set = {t for t in self.tokens if len(t) > 1}
        for pos, tok in self._greedy_tokenize(word, ngram_set):
            # Passthrough for non-Latin tokens (kept literal, flagged with residual -1)
            if any(ch not in self.latin for ch in tok):
                cipher.append(tok)
                residuals.append(-1)
                continue

            pmap = self.positional_map.get(pos, {})
            rmap = self.reverse_map.get(pos, {})
            glyph = pmap.get(tok)
            if glyph is None:
                # Fallback: choose any glyph available at this position (deterministic RNG)
                glyph = RNG.choice(self.voy_chars_by_pos.get(pos, sorted(set("".join(self.voy_words)))))

            cipher.append(glyph)

            # Residual index is the position of the token within the glyph's candidate list
            letters = rmap.get(glyph, [tok])
            idx = letters.index(tok) if tok in letters else 0
            residuals.append(idx)
        return "".join(cipher), residuals

    def decrypt_word(self, cipher, residuals):
        """
        Decrypt a single cipher word using residuals to disambiguate one-to-many mappings.
        - residual == -1 → passthrough literal token (non-Latin during encryption).
        """
        out, pos = [], 0
        for g, r in zip(cipher, residuals):
            if r == -1:
                out.append(g)
                pos += 1
                continue
            cand_list = self.reverse_map.get(pos, {}).get(g, [])
            if not cand_list:
                out.append("?")
                pos += 1
            else:
                tok = cand_list[min(r, len(cand_list) - 1)]
                out.append(tok)
                pos += len(tok)
        return "".join(out)

    def encrypt_words(self, words):
        """Encrypt a list of words -> (list of cipher words, list of residual lists)."""
        ciphers, residuals = [], []
        for w in words:
            c, r = self.encrypt_word(w)
            ciphers.append(c)
            residuals.append(r)
        return ciphers, residuals

    def table_as_dataframe(self, max_pos=None):
        """
        Export the positional mapping as a pandas DataFrame:
            index = tokens, columns = pos_0 .. pos_k, values = glyph at that position.
        """
        if max_pos is None:
            max_pos = max(self.positional_map.keys()) if self.positional_map else 0
        data = {}
        for pos in range(max_pos + 1):
            col = []
            for tok in self.tokens:
                g = self.positional_map.get(pos, {}).get(tok, "")
                col.append(g)
            data[f"pos_{pos}"] = col
        df_table = pd.DataFrame(data, index=self.tokens)
        df_table.index.name = "token"
        return df_table

def evaluate_cipher(cipher_words, reference_words, max_n=5, smooth=1.0):
    """
    Evaluate a cipher against a reference corpus.

    Metrics:
        - Entropy curve H(n) for n = 1..max_n (word-reset model).
        - Jensen–Shannon divergence between global bigram distributions.

    Smoothing:
        - Applies Laplace/Dirichlet smoothing ('smooth') to bigram counts
          before normalizing to a probability distribution.

    Returns:
        H     : list[float]       -- entropies for n = 1..max_n
        jsd   : float             -- JS divergence between bigram matrices
        Mc    : np.ndarray (VxV)  -- cipher bigram probability matrix
        Mr    : np.ndarray (VxV)  -- reference bigram probability matrix
        common: list[str]         -- unified character vocabulary used for Mc/Mr
    """
    H = entropy_curve(cipher_words, max_n=max_n)

    # Unified glyph alphabet to compare bigram matrices on the same index space
    chars_c = sorted(set("".join(cipher_words)))
    chars_r = sorted(set("".join(reference_words)))
    common = sorted(set(chars_c) | set(chars_r))
    idx = {ch: i for i, ch in enumerate(common)}
    n = len(common)

    def bigram_matrix_over(words):
        M = np.zeros((n, n), dtype=float)
        for w in words:
            if len(w) < 2:
                continue
            for a, b in zip(w, w[1:]):
                M[idx[a], idx[b]] += 1.0
        # Laplace/Dirichlet smoothing then global normalization
        M += smooth
        M /= M.sum()
        return M

    Mc = bigram_matrix_over(cipher_words)
    Mr = bigram_matrix_over(reference_words)
    jsd = js_divergence(Mc, Mr)
    return H, jsd, Mc, Mr, common

def objective(H2, jsd, target_H2=2.3, w_H=1.0, w_jsd=1.0):
    """
    Scalar objective to minimize when tuning parameters.

    Args:
        H2        : float  -- entropy at n=2 for the candidate cipher
        jsd       : float  -- JS divergence of bigram distributions vs reference
        target_H2 : float  -- desired H2 target (adjust per corpus/normalization)
        w_H       : float  -- weight for |H2 - target_H2|
        w_jsd     : float  -- weight for jsd

    Returns:
        float: weighted sum of deviations.
    """
    return w_H * abs(H2 - target_H2) + w_jsd * jsd

def search_parameters_extended(
    plaintext_words,
    target_collision_grid=range(1, 11),
    trials_per=5,
    target_H2=2.1,
    w_H=1.0,
    w_jsd=1.0,
    use_ngrams_options=(False, True),
    ngram_ns_options=((2, 3), (3, 4)),
):
    """
    Exhaustive/stochastic search over PMCipher hyperparameters.

    Explores:
        - target_collision (controls tokens-per-glyph at each position)
        - use_ngrams (whether to augment tokens with frequent n-grams)
        - ngram_ns (which n-gram sizes to consider when use_ngrams=True)
        - trials_per (repeated runs to sample RNG variation in assignments)

    Objective:
        Minimize a weighted sum of |H2 - target_H2| and JS divergence (bigrams) vs. Voynich.

    Returns:
        dict with the best configuration and artifacts:
            {
              "C": int,
              "use_ngrams": bool,
              "ngram_ns": tuple,
              "H": list[float],          # entropies for n=1..5
              "jsd": float,              # JS divergence on bigrams
              "score": float,
              "cipher": PMCipher,        # fitted instance
              "cipher_words": list[str], # encrypted words
              "residuals": list[list[int]]
            }
    """
    if not plaintext_words:
        raise ValueError("plaintext_words is empty; cannot search parameters.")

    best = None
    for C in target_collision_grid:
        for use_ngrams in use_ngrams_options:
            for ngram_ns in ngram_ns_options:
                for _ in range(trials_per):
                    cipher = PMCipher(
                        LATIN_ALPHABET,
                        voynich_words,
                        target_collision=C,
                        strategy="greedy",
                        use_ngrams=use_ngrams,
                        ngram_ns=ngram_ns,
                    ).fit(plaintext_words)

                    cipher_words, residuals = cipher.encrypt_words(plaintext_words)
                    H, jsd, _, _, _ = evaluate_cipher(cipher_words, voynich_words, max_n=5)

                    score = objective(
                        H2=H[1],
                        jsd=jsd,
                        target_H2=target_H2,
                        w_H=w_H,
                        w_jsd=w_jsd,
                    )

                    cand = {
                        "C": C,
                        "use_ngrams": use_ngrams,
                        "ngram_ns": ngram_ns,
                        "H": H,
                        "jsd": jsd,
                        "score": score,
                        "cipher": cipher,
                        "cipher_words": cipher_words,
                        "residuals": residuals,  # keep residuals for deterministic decoding
                    }

                    if (best is None) or (score < best["score"]):
                        best = cand

                    print(
                        f"[C={C}, ngrams={use_ngrams}, ns={ngram_ns}] "
                        f"H2={H[1]:.3f}, JSD={jsd:.4f}, score={score:.4f}"
                    )
    return best

try:
    from scipy.optimize import linear_sum_assignment
    HAVE_HUNGARIAN = True   # downstream code will use Hungarian when this is True
except Exception:
    HAVE_HUNGARIAN = False

EPS = 1e-12

def _tokenize_words_with_cipher_tokens(words, cipher):
    """
    Tokenize plaintext words using the cipher's current token set (letters + optional n-grams).
    Returns a list of token lists per word (no positions, only the token sequence).
    """
    ngram_set = {t for t in cipher.tokens if len(t) > 1}
    out = []
    for w in words:
        toks = []
        for _, tok in cipher._greedy_tokenize(w, ngram_set):
            toks.append(tok)
        out.append(toks)
    return out

from collections import defaultdict, Counter

def _positional_token_bigrams(words_tok):
    """
    Count token bigrams by 0-based position (within tokenized words).
    Returns: dict[pos][token_prev][token_curr] -> count
    """
    tb = defaultdict(lambda: defaultdict(Counter))
    for toks in words_tok:
        for i in range(len(toks) - 1):
            a, b = toks[i], toks[i + 1]
            tb[i][a][b] += 1
    return tb

def _positional_glyph_bigrams(voy_words):
    """
    Count glyph bigrams by 0-based position in Voynich words.
    Returns: dict[pos][glyph_prev][glyph_curr] -> count
    """
    gb = defaultdict(lambda: defaultdict(Counter))
    for w in voy_words:
        for i in range(len(w) - 1):
            a, b = w[i], w[i + 1]
            gb[i][a][b] += 1
    return gb

def _glyph_positional_unigrams(words):
    """
    Count glyph unigrams by 0-based position.
    Returns: dict[pos][glyph] -> count
    """
    C = defaultdict(Counter)
    for w in words:
        for i, g in enumerate(w):
            C[i][g] += 1
    return C

def _normalize_counter_to_dist(cdict, support):
    """
    Convert counts over a fixed support into a smoothed probability distribution.
    """
    arr = np.array([cdict.get(x, 0.0) for x in support], dtype=float)
    arr = arr + EPS
    arr = arr / arr.sum()
    return arr

def _cond_dist_prev_for_token(t, pos, token_bi, map_prev, glyph_support_prev):
    """
    For a given token t at position pos, induce a distribution over previous glyphs:
    P(g_prev | token at pos == t) using the previous-position token→glyph map.
    """
    counts = Counter()
    for t_prev, nxts in token_bi.get(pos - 1, {}).items():
        c = nxts.get(t, 0)
        if c:
            g_prev = map_prev.get(t_prev)
            if g_prev is not None:
                counts[g_prev] += c
    return _normalize_counter_to_dist(counts, glyph_support_prev)

def _js(p, q):
    """
    Jensen–Shannon divergence for two discrete distributions (vectors that sum to 1).
    """
    m = 0.5 * (p + q)
    return 0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m))

def bigram_prev_only_freqaware_with_stability(
    cipher,
    plain_words,
    voynich_words,
    gamma_uni=1.0,
    tau_move=0.3,
    seed=42,
):
    """
    Re-assign tokens to glyphs at each position using a 'previous-glyph' bigram objective,
    while preserving per-glyph capacities at that position.

    Components of the cost:
      - Previous-bigram fit: JS( induced_prev(token), Voynich_prev_cond(glyph) )
      - Unigram bias: gamma_uni * f_token * (-log P_voynich(glyph_at_pos))
        (frequent tokens avoid unlikely glyphs at that position)
      - Stability penalty: tau_move * f_token * 1{ new_glyph != old_glyph }
        (discourages moving tokens away from their original assignment)

    Args:
      cipher        : PMCipher (will be deep-copied)
      plain_words   : list[str]  plaintext words
      voynich_words : list[str]  Voynich words
      gamma_uni     : float      weight of unigram penalty
      tau_move      : float      weight of movement/stability penalty
      seed          : int        RNG seed (kept for future stochastic variants)

    Returns:
      PMCipher with updated positional_map / reverse_map.
    """
    c = copy.deepcopy(cipher)

    # Token bigrams from plaintext under current tokenization
    words_tok = _tokenize_words_with_cipher_tokens(plain_words, c)
    token_bi = _positional_token_bigrams(words_tok)

    # Token frequencies per position (to weight penalties)
    token_freq_by_pos = defaultdict(Counter)
    for toks in words_tok:
        for i, t in enumerate(toks):
            token_freq_by_pos[i][t] += 1

    # Voynich bigrams (glyph) and unigrams (by position)
    glyph_bi = _positional_glyph_bigrams(voynich_words)
    voy_uni = _glyph_positional_unigrams(voynich_words)

    # Original mapping (for stability penalty)
    pos_map0 = c.positional_map
    rev_map = c.reverse_map
    positions = sorted(rev_map.keys())

    # Glyph supports by position (incl. fallbacks from cipher)
    glyphs_by_pos = {
        pos: sorted(set(glyph_bi.get(pos, {}).keys()) | set(c.voy_chars_by_pos.get(pos, [])))
        for pos in set(list(glyph_bi.keys()) + list(c.voy_chars_by_pos.keys()))
    }
    for pos in positions:
        glyphs_by_pos.setdefault(pos - 1, sorted(c.voy_chars_by_pos.get(pos - 1, [])))
        glyphs_by_pos.setdefault(pos,     sorted(c.voy_chars_by_pos.get(pos, [])))

    for pos in positions:
        rmap = rev_map[pos]
        if not rmap:
            continue

        glyphs = list(rmap.keys())
        caps = [len(rmap[g]) for g in glyphs]
        if sum(caps) == 0:
            continue

        # Current tokens (flatten buckets, preserving multiplicities)
        tokens = []
        for g in glyphs:
            tokens.extend(rmap[g])

        # Need a non-empty previous-glyph support to compare previous bigrams
        g_support_prev = glyphs_by_pos.get(pos - 1, [])
        if not g_support_prev:
            continue

        # Voynich conditional: P(g_prev | g_at_pos)
        voy_prev_cond = {}
        for g in set(glyphs):
            counts_prev = Counter()
            for g_prev, nxts in glyph_bi.get(pos - 1, {}).items():
                ccount = nxts.get(g, 0)
                if ccount:
                    counts_prev[g_prev] += ccount
            voy_prev_cond[g] = _normalize_counter_to_dist(counts_prev, g_support_prev)

        # Target unigram distribution at this position (for the unigram penalty)
        total_pos = sum(voy_uni.get(pos, {}).values()) + EPS
        p_g_target = {g: (voy_uni.get(pos, {}).get(g, 0) + EPS) / total_pos for g in glyphs}

        # Map at previous position (token -> glyph) to induce previous-glyph distributions
        map_prev = pos_map0.get(pos - 1, {})

        # Expand capacity slots for assignment (each slot belongs to a glyph)
        slots, slot_glyph = [], []
        for g, cap in zip(glyphs, caps):
            for _ in range(cap):
                slots.append((g, _))
                slot_glyph.append(g)
        assert len(slots) == len(tokens)

        # Cost matrix: rows=tokens, cols=slots
        T, S = len(tokens), len(slots)
        Cmat = np.zeros((T, S), dtype=float)

        # Token frequency weights (normalized) at this position
        total_tok = sum(token_freq_by_pos[pos][t] for t in tokens) + EPS
        f_norm = {t: token_freq_by_pos[pos][t] / total_tok for t in tokens}

        # Induced distributions over previous glyphs for each token
        induced_prev = {
            t: _cond_dist_prev_for_token(t, pos, token_bi, map_prev, g_support_prev) for t in tokens
        }

        for i, t in enumerate(tokens):
            q_prev = induced_prev[t]
            f_t = f_norm[t]
            g_old = pos_map0.get(pos, {}).get(t)  # original glyph of this token at pos
            for j, g in enumerate(slot_glyph):
                p_prev = voy_prev_cond[g]
                cost_prev = _js(q_prev, p_prev)
                cost_uni = gamma_uni * f_t * (-np.log(p_g_target.get(g, EPS)))
                cost_move = tau_move * f_t * (0.0 if (g_old == g) else 1.0)
                Cmat[i, j] = cost_prev + cost_uni + cost_move

        # Solve assignment
        if HAVE_HUNGARIAN:
            row_ind, col_ind = linear_sum_assignment(Cmat)
        else:
            # Greedy fallback (not guaranteed optimal, but deterministic)
            taken = set()
            row_ind, col_ind = [], []
            order = np.argsort(Cmat.min(axis=1))
            for i in order:
                j = int(np.argmin([Cmat[i, k] if k not in taken else np.inf for k in range(S)]))
                row_ind.append(i)
                col_ind.append(j)
                taken.add(j)

        # Rebuild reverse/forward maps
        new_rmap = {g: [] for g in glyphs}
        for i, j in zip(row_ind, col_ind):
            g = slot_glyph[j]
            new_rmap[g].append(tokens[i])

        new_pmap = {}
        for g, toks in new_rmap.items():
            for t in toks:
                new_pmap[t] = g

        c.reverse_map[pos] = new_rmap
        c.positional_map[pos] = new_pmap

    return c

def run_gamma_sweep(
    best,
    plain_words,
    voynich_words,
    gamma_grid=(0.8, 1.0, 1.5, 2.0, 2.5, 3.0),
    tau_grid=(0.0, 0.2, 0.5, 1.0),
    h2_target=2.1,
    h2_tol=0.25,
    seed=123,
):
    """
    Sweep (gamma_uni, tau_move), re-fitting the prev-bigram-aware assignment.
    Keeps candidates whose H2 is within [h2_target ± h2_tol], then selects the one with
    the lowest bigram JS divergence. If that improves the current 'best', update it.
    """
    results = []
    for gamma in gamma_grid:
        for tau in tau_grid:
            c_try = bigram_prev_only_freqaware_with_stability(
                best["cipher"], plain_words, voynich_words,
                gamma_uni=gamma, tau_move=tau, seed=seed
            )
            w_try, r_try = c_try.encrypt_words(plain_words)
            H_try, jsd_try, _, _, _ = evaluate_cipher(w_try, voynich_words, max_n=5)
            h2 = H_try[1]
            ok = (abs(h2 - h2_target) <= (h2_tol + 1e-9))
            results.append((gamma, tau, jsd_try, h2, ok, c_try, w_try, r_try, H_try))
            print(f"gamma={gamma:.2f}, tau={tau:.2f} -> JSD={jsd_try:.6f}, H2={h2:.3f}  [{'OK' if ok else 'X'}]")

    # Choose the best OK by JSD
    ok_results = [r for r in results if r[4]]
    if ok_results:
        best_ok = min(ok_results, key=lambda x: x[2])
        gamma, tau, jsd_try, h2, ok, c_try, w_try, r_try, H_try = best_ok
        print(f"\nSelected: gamma={gamma}, tau={tau} -> JSD={jsd_try:.6f}, H2={h2:.3f}")
        # Update 'best' if improved
        if jsd_try < best["jsd"]:
            best = {**best, "cipher": c_try, "cipher_words": w_try,
                    "residuals": r_try, "jsd": jsd_try, "H": H_try}
            print("-> Updated 'best'.")
        else:
            print("-> No update (JSD not improved over previous best).")
    else:
        print("\nNo combination met the H2 window. Try larger gamma and/or tau, or widen h2_tol.")

    return best

def run_gamma_sweep_until_convergence(
    best,
    plain_words,
    voynich_words,
    gamma_grid=(3.0, 4.0, 5.0, 6.0, 7.0),
    tau_grid=(0.2, 0.5, 1.0),
    h2_target=None,          # if None, use current Voynich H2
    h2_tol=0.20,
    max_rounds=10,           # hard cap to avoid infinite loops
    min_delta=1e-4,          # minimum JSD improvement to count as "better"
    patience=1,              # stop after this many consecutive non-improving rounds
    base_seed=123,           # base RNG seed; we vary it slightly each round
    verbose=True,
):
    """
    Iteratively call `run_gamma_sweep` until JSD stops improving.

    Strategy:
      - In each round, run a full sweep over (gamma, tau).
      - Accept the new mapping only if its JSD improves by at least `min_delta`.
      - If no improvement for `patience` consecutive rounds, stop early.

    Returns:
      Updated `best` dict (possibly unchanged if no improvement is found).
    """
    if h2_target is None:
        # Fall back to previously computed Voynich H2 if available
        try:
            h2_target = float(voy_H[1])
            if verbose:
                print(f"[Convergence] Using h2_target={h2_target:.3f} from voy_H[1].")
        except Exception:
            h2_target = 2.1
            if verbose:
                print(f"[Convergence] Could not infer Voynich H2; defaulting to {h2_target:.3f}.")

    best_jsd = best.get("jsd", float("inf"))
    no_improve_rounds = 0

    for round_idx in range(1, max_rounds + 1):
        if verbose:
            print(f"\n=== Sweep round {round_idx} | current best JSD={best_jsd:.6f}, H2={best['H'][1]:.3f} ===")

        # Vary seed slightly per round to shake tie-breaks (even with Hungarian, upstream steps or ordering can differ)
        seed = base_seed + round_idx

        new_best = run_gamma_sweep(
            best,
            plain_words,
            voynich_words,
            gamma_grid=gamma_grid,
            tau_grid=tau_grid,
            h2_target=h2_target,
            h2_tol=h2_tol,
            seed=seed,
        )

        new_jsd = new_best.get("jsd", float("inf"))
        jsd_gain = best_jsd - new_jsd

        if new_jsd < best_jsd - min_delta:
            if verbose:
                print(f"[Convergence] Improvement found: JSD {best_jsd:.6f} → {new_jsd:.6f} (Δ={jsd_gain:.6f})")
            best = new_best
            best_jsd = new_jsd
            no_improve_rounds = 0
        else:
            no_improve_rounds += 1
            if verbose:
                print(f"[Convergence] No meaningful improvement (Δ={jsd_gain:.6f} <= {min_delta}). "
                      f"Patience {no_improve_rounds}/{patience}.")
            if no_improve_rounds > patience:
                if verbose:
                    print("[Convergence] Early stopping: no further improvements.")
                break

    if verbose:
        print(f"\nFinal best: JSD={best['jsd']:.6f}, H2={best['H'][1]:.3f}")
    return best
