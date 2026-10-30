import os, re, numpy as np, pandas as pd
coma_is_space = True
# Còpia literal del parser del notebook pm-cipher.ipynb (Kaggle, set. 2025) per diagnosticar-ne els errors.
# ==== CELL 1 code
# =========================
# Config and mappings
# =========================
I_MAP = {
    "A": "Astronomical", "B": "Biological (balneological)", "C": "Cosmological",
    "H": "Herbal", "P": "Pharmaceutical", "S": "Marginal stars only",
    "T": "Text-only", "Z": "Zodiac",
}
X_MAP = {
    "C": "Colour annotation", "M": "Month name", "O": "Other extraneous writing",
    "S": "Sequence of characters or numbers", "V": "Various (combination; deprecated)",
}
FIELD_MAP = {  # short key -> output column name
    "Q": "quire",
    "P": "page",
    "F": "folio",
    "B": "bifolio",
    "I": "section",
    "L": "language",
    "H": "writing_hand",
    "C": "currier_hand",
    "X": "annotations",
}

# =========================
# Regex
# =========================
# Line starting with <tag> followed by the rest
FIRST_TOKEN_RE = re.compile(r'^\s*<([^>]+)>\s*(.*)$')

# Header if the first token does NOT contain a dot
def is_header_token(token: str) -> bool:
    return '.' not in token

# Key–value pairs $K=V inside <! ... >
KV_RE = re.compile(r'\$([A-Z])=([^\s>]+)')

# Extract tag + line from text lines:
# - f86v5.2,+P0  -> tag=f86v, line=5
# - f1r.1,@P0    -> tag=f1r, line=1
# - fRos.142,@Pb -> tag=fRos, line=None
TAG_LINE_RE = re.compile(
    r'^(?P<tag>f(?:Ros|[0-9]+[rv]))'            # base tag
    r'(?:(?P<lineno1>\d+)|\.(?P<lineno2>\d+))?' # A: immediate digits; B: .digits
    r'(?:[.,].*)?$',                             # remainder (.,@,+, etc.)
    re.IGNORECASE
)

# Text cleaning
BRACKET_ALT_RE = re.compile(r'\[([^\[\]]+)\]')        # [a:b:c]
NUM_TAG_RE = re.compile(r'<!\d{1,3}[^>]*>')
# 1) <!@7>, <! @12 ;>, <!@123;>
ANGLE_PUA_RE = re.compile(r'<\!\s*@\s*(\d{1,3})\s*;?\s*>')
# 2) @7;   @12   @123;   (bare tokens)
BARE_PUA_RE  = re.compile(r'@\s*(\d{1,3})\s*;?')

# Helper to build the match expected by _replace_high_ascii (group(0)='@ddd;')
_AT_TOKEN = re.compile(r'@(\d{1,3});')

# =========================
# Helpers
# =========================
def parse_tag_and_line(inner: str):
    m = TAG_LINE_RE.match(inner)
    if not m:
        # Fallback: tag until the first dot; line=None
        tag = inner.split('.', 1)[0]
        return tag, None
    tag = m.group('tag')
    # Force line=None for fRos*
    if tag.lower().startswith('fros'):
        return tag, None
    ln = m.group('lineno1') or m.group('lineno2')
    return tag, (int(ln) if ln is not None else None)

def apply_maps(k: str, v: str):
    """Map I and X codes to labels; leave other fields unchanged."""
    if k == "I":
        return I_MAP.get(v.upper(), v)
    if k == "X":
        return X_MAP.get(v.upper(), v)
    return v

def _replace_bracket_alternatives(s: str) -> str:
    """Keep only the first value inside [a:b:c] -> 'a'."""
    def repl(m):
        inner = m.group(1)
        first = inner.split(':', 1)[0]
        return first
    return BRACKET_ALT_RE.sub(repl, s)

def _pua_from_digits(digits: str) -> str:
    # Requires a helper `_replace_high_ascii('@ddd;') -> PUA char` defined elsewhere
    fake = _AT_TOKEN.match(f'@{digits};')   # group(0) will be '@ddd;'
    return _replace_high_ascii(fake)        # returns PUA U+E000..F8FF (non-ASCII)

def clean_text(raw_text: str) -> str:
    s = raw_text
    # [a:b:c] -> 'a'
    s = _replace_bracket_alternatives(s)

    # <!@ddd;?> -> PUA
    def _repl_angle(m):
        ch = _pua_from_digits(m.group(1))
        return ch
    s, n1 = ANGLE_PUA_RE.subn(_repl_angle, s)

    # @ddd;? (bare) -> PUA
    def _repl_bare(m):
        ch = _pua_from_digits(m.group(1))
        return ch
    s, n2 = BARE_PUA_RE.subn(_repl_bare, s)

    # Remove paragraph markers if desired
    s = s.replace('<%>', '').replace('<$>', '')
    return s

# --- Mapeig PUA per @ddd; ---
special_to_unicode = {}
unicode_to_special = {}
_next_codepoint = 0xE000

def _replace_high_ascii(m):
    """Converteix @ddd; en un caràcter PUA únic i el memoritza als mapes."""
    global _next_codepoint
    token = m.group(0)               # p. ex. '@173;'
    ch = special_to_unicode.get(token)
    if ch is None:
        if _next_codepoint > 0xF8FF:
            raise ValueError("Private Use Area BMP exhaurida (E000..F8FF)!")
        ch = chr(_next_codepoint)
        special_to_unicode[token] = ch
        unicode_to_special[ch] = token
        _next_codepoint += 1
    return ch

def detect_line_type(raw_text: str) -> int:
    """
    Line type codes (detect on raw_text, before cleaning):
      0 = normal
      1 = paragraph start (<%>)
      2 = inside paragraph (between 1 and 3)
      3 = paragraph end (<$>)
      4 = numeric tag (<!NNN>)
    """
    if '<%>' in raw_text:
        return 1
    if '<$>' in raw_text:
        return 3
    if NUM_TAG_RE.search(raw_text):
        return 4
    return 0

# =========================
# Main parser
# =========================
def parse_voynich_file(path: str) -> pd.DataFrame:
    rows = []
    current_header = {col: None for col in FIELD_MAP.values()}  # header state propagated to rows

    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")

            # Skip empty and comment lines
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            m = FIRST_TOKEN_RE.match(line)
            if not m:
                continue  # unexpected line

            first_token = m.group(1)
            remainder = m.group(2)

            # Header line if the first token has no dot
            if is_header_token(first_token):
                # Look for the <! ... > block
                m_meta = re.search(r'<\!(.*?)>', remainder)
                if m_meta:
                    payload = m_meta.group(1)
                    for k, v in KV_RE.findall(payload):
                        col = FIELD_MAP.get(k)
                        if not col:
                            continue
                        current_header[col] = apply_maps(k, v)
                # Headers do not generate a data row
                continue

            # Text line
            tag, lineno = parse_tag_and_line(first_token)
            raw_text = remainder.strip()
            text = clean_text(raw_text)
            lt = detect_line_type(raw_text)

            rows.append({
                "tag": tag,
                "line": lineno if lineno is not None else np.nan,
                "text": text,
                "line_type": lt,
                **current_header,
            })

    df = pd.DataFrame(rows)

    # Post-process: mark 2 (inside paragraph) between 1 (<%>) and 3 (<$>) without overwriting 1/3/4
    inside_para = False
    for i in range(len(df)):
        t = df.at[i, 'line_type']
        if t == 1:
            inside_para = True
        elif t == 3:
            inside_para = False
        else:
            if inside_para and t == 0:
                df.at[i, 'line_type'] = 2

    return df


# =========================
# Usage
# =========================
path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ZL3b-n.txt")
df = parse_voynich_file(path)

# Precompiled regex
RE_PCT = re.compile(r'<%>')
RE_DOLLAR = re.compile(r'<\$>')
RE_NUM_BANG = re.compile(r'<!\d{1,3}[^>]*>')
RE_AT_BLOCK = re.compile(r'<@[^>]*>')        # <@...>
RE_CURLY = re.compile(r'\{([^{}]*)\}')       # {content} -> content

def step1_remove_tokens(s: str) -> str:
    """Strip common markup blocks and keep content inside {...}."""
    if not isinstance(s, str):
        return s
    # remove <%> and <$>
    s = RE_PCT.sub('', s)
    s = RE_DOLLAR.sub('', s)
    # remove <!N> (short numeric)
    s = RE_NUM_BANG.sub('', s)
    # remove <@...> blocks
    s = RE_AT_BLOCK.sub('', s)
    # remove { and } while keeping inner content (repeat a couple of times just in case)
    for _ in range(2):
        s, n = RE_CURLY.subn(r'\1', s)
        if n == 0:
            break
    return s

df['text'] = df['text'].astype(str).map(step1_remove_tokens)

# 3) AFTER marking special lines, remove ANY remaining <...> blocks
RE_ANY_BLOCK = re.compile(r'<[^>]*>')
df['text'] = df['text'].map(lambda s: RE_ANY_BLOCK.sub('', s))

# 4) Replace "." with " "
df['text'] = df['text'].str.replace('.', ' ', regex=False)

# 5) Replace "," with " " — first, count commas and percentage relative to words
num_commas = df['text'].str.count(',').sum()
num_words = df['text'].str.split().str.len().sum()
percent_commas = (num_commas / num_words * 100) if num_words > 0 else 0

print(f"Number of commas: {num_commas}")
print(f"Total number of words: {num_words}")
print(f"Percentage of commas relative to words: {percent_commas:.2f}%")

if coma_is_space:
    # Now perform the replacement coma for space
    df['text'] = df['text'].str.replace(',', ' ', regex=False)
else:
    # Remove the coma
    df['text'] = df['text'].str.replace(',', '', regex=False)

# (Optional) clean multiple spaces and trim
df['text'] = df['text'].str.replace(r'\s+', ' ', regex=True).str.strip()

# --- Show ASCII vs non-ASCII character sets ---
all_text = ''.join(df['text'].dropna().tolist())
ascii_chars = sorted({ch for ch in all_text if ord(ch) < 128})
non_ascii_chars = sorted({ch for ch in all_text if ord(ch) >= 128})

print("ASCII chars (set):", set(ascii_chars))
print("Non-ASCII chars (set):", set(non_ascii_chars))
print("""LINE TYPES:
0: normal
1: paragraph start
2: paragraph middle
3: paragraph end
4: tag
5: special line""")

# Generic output (current folder)
# (fi del codi copiat del notebook pm-cipher.ipynb, cel·la 1; l'única canvi és la ruta del fitxer)
