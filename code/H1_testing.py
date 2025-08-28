# H1, H1a, H1b — fast and robust: Spearman correlations + fallback Welch tests
# pip install pandas scipy numpy openpyxl
import re
import numpy as np
import pandas as pd
from scipy import stats

PATH  = "/Users/gaby/Desktop/THESIS/excel_data/data_survey_for_python.xlsx"
SHEET = "Sheet1"

# ---------- helpers ----------
def norm_header(s: str) -> str:
    s = (s or "")
    s = s.replace("\u00A0", " ")
    s = re.sub(r"[\u2018\u2019\u201C\u201D]", '"', s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def clean_numeric(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace("\u00A0", " ", regex=False)
    s = s.str.replace(r"[^0-9\.-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")

def match_col(df: pd.DataFrame, must_all=(), any_of=()):
    for c in df.columns:
        h = norm_header(str(c)).lower()
        if all(k.lower() in h for k in must_all) and (not any_of or any(p.lower() in h for p in any_of)):
            return c
    if any_of:
        for c in df.columns:
            h = norm_header(str(c)).lower()
            if any(p.lower() in h for p in any_of):
                return c
    return None

def pick_outcome_cols(df, keywords, exclude_cols=()):
    out, ex = [], set(exclude_cols)
    for c in df.columns:
        if c in ex: 
            continue
        h = norm_header(str(c)).lower()
        if any(k in h for k in keywords):
            out.append(c)
    return out

def spearman_one_sided(x, y, direction="+"):
    rho, p_two = stats.spearmanr(x, y, nan_policy="omit")
    if np.isnan(rho) or np.isnan(p_two):
        return rho, np.nan
    if direction == "+":
        p_one = p_two / 2 if rho >= 0 else 1 - p_two / 2
    else:
        p_one = p_two / 2 if rho <= 0 else 1 - p_two / 2
    return rho, p_one

def cohens_d_ind(x1, x0):
    n1, n0 = len(x1), len(x0)
    if n1 < 2 or n0 < 2: 
        return np.nan
    s1, s0 = np.var(x1, ddof=1), np.var(x0, ddof=1)
    sp = np.sqrt(((n1-1)*s1 + (n0-1)*s0) / (n1+n0-2))
    return (np.mean(x1) - np.mean(x0)) / sp if sp > 0 else np.nan

# ---------- load ----------
df = pd.read_excel(PATH, sheet_name=SHEET, dtype=str)

# ---------- age filter (your exact labels) ----------
age_col = None
for c in df.columns:
    if norm_header(str(c)).lower() == "age":
        age_col = c; break
if age_col is not None:
    before = len(df)
    df = df[df[age_col].isin(["18 -28", "29 - 44"])].copy()
    print(f"Rows before age filter: {before}, after: {len(df)}")
else:
    print("Warning: no Age column found. Proceeding without age filter.")

# ---------- predictor: belief that internal/invoice is more secure ----------
belief_col = match_col(
    df,
    must_all=["payment", "internal", "secure"],
    any_of=["external bnpl", "amazonpay", "store", "brand"]
)
if belief_col is None:
    raise ValueError("Could not find the belief item about internal vs external security.")

raw = df[belief_col].astype(str).str.replace("\u00A0"," ", regex=False).str.strip()
low = raw.str.lower()

# try numeric Likert; otherwise map common text to an ordinal
belief = pd.to_numeric(low.str.extract(r"(-?\d+(?:\.\d+)?)", expand=False), errors="coerce")

map_ordered = {
    "strongly disagree": 1, "disagree": 2, "neutral": 3, "agree": 4, "strongly agree": 5,
    "no": 2, "nein": 2, "yes": 4, "ja": 4
}
fill = low.map(lambda v: next((val for key, val in map_ordered.items() if key in v), np.nan))
belief = belief.fillna(fill)
print(f"Belief variable non-missing: {int(belief.notna().sum())}")

# ---------- outcomes ----------
exclude_cols = {belief_col}

trust_cols   = pick_outcome_cols(df, ["trust","reliable","reliab"], exclude_cols)
quality_cols = pick_outcome_cols(df, ["quality"], exclude_cols)
service_cols = pick_outcome_cols(df, ["customer service","service quality","support"], exclude_cols)

def build_index(cols, name):
    if not cols:
        print(f"No columns detected for {name}.")
        return pd.Series([np.nan]*len(df))
    tmp = df[cols].apply(clean_numeric, axis=0)
    idx = tmp.mean(axis=1, skipna=True)
    print(f"{name} items used ({len(cols)}): {cols}")
    print(f"{name} non-missing: {int(idx.notna().sum())}")
    return idx

trust_idx   = build_index(trust_cols,   "Trust")
quality_idx = build_index(quality_cols, "Quality")
service_idx = build_index(service_cols, "Service")

# ---------- primary tests: Spearman (directional, expect positive) ----------
def run_spearman(label, y):
    dat = pd.DataFrame({"b": belief, "y": y}).dropna()
    print(f"\n{label} — Spearman directional test (rho > 0):")
    print(f"  n={len(dat)}")
    if len(dat) < 10:
        print("  Too few paired cases for a stable correlation.")
        return
    rho, p_one = spearman_one_sided(dat["b"], dat["y"], direction="+")
    print(f"  rho={rho:.3f}, one-sided p={p_one:.4f}")

run_spearman("H1 (trust ~ belief internal>external)",   trust_idx)
run_spearman("H1a (quality ~ belief internal>external)", quality_idx)
run_spearman("H1b (service ~ belief internal>external)", service_idx)

# ---------- secondary check: two-group Welch tests if both sides exist ----------
# Define groups: agree (belief >=4) vs disagree (belief <=2); drop neutrals
g = pd.Series(pd.NA, index=df.index, dtype="Int64")
g.loc[belief >= 4] = 1
g.loc[belief <= 2] = 0

def run_welch(label, y):
    dat = pd.DataFrame({"y": y, "g": g}).dropna()
    g1 = dat.loc[dat["g"] == 1, "y"]
    g0 = dat.loc[dat["g"] == 0, "y"]
    print(f"\n{label} — Welch t test (agree internal > disagree):")
    print(f"  n1(agree)={len(g1)}, n0(disagree)={len(g0)}")
    if len(g1) >= 5 and len(g0) >= 5:
        t, p = stats.ttest_ind(g1, g0, equal_var=False, alternative="greater")
        d = cohens_d_ind(g1.to_numpy(), g0.to_numpy())
        print(f"  means: {g1.mean():.2f} vs {g0.mean():.2f}")
        print(f"  Welch t={t:.2f}, p={p:.4f}, d={d:.2f}")
    else:
        print("  Not enough per group; skipping.")

run_welch("H1",   trust_idx)
run_welch("H1a", quality_idx)
run_welch("H1b", service_idx)

# This code was generated with the assistance of ChatGPT (OpenAI, 2025)
