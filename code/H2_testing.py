# Clean tests for H2, H2a, H2b with binary Financial_Stability
import pandas as pd
import numpy as np
from scipy import stats
import re

PATH = "/Users/gaby/Desktop/THESIS/excel_data/data_survey_for_python.xlsx"

# Exclusivity items
COL_EXCL_NO_BNPL  = "Not offering BNPL makes me think the brand is targeting customers who value exclusivity and personal service."
COL_LUX_WITHOUT   = "I would expect luxury products (e.g., Lamborghini, high-end Rolex, mansion) to be sold without BNPL options."
COL_LUX_LESS_EXCL = "Offering BNPL for luxury products would make them feel less exclusive."
EXCL_COLS = [COL_EXCL_NO_BNPL, COL_LUX_WITHOUT, COL_LUX_LESS_EXCL]

# Financial stability binary
COL_FIN_STABLE = "Financial_Stability"

def clean_numeric(series):
    s = series.astype(str).str.replace("\xa0", " ", regex=False)
    s = s.str.replace(r"[^0-9\.-]", "", regex=True)
    return pd.to_numeric(s, errors="coerce")

def cohens_d_ind(x1, x0):
    n1, n0 = len(x1), len(x0)
    if n1 < 2 or n0 < 2:
        return np.nan
    s1, s0 = np.var(x1, ddof=1), np.var(x0, ddof=1)
    sp = np.sqrt(((n1-1)*s1 + (n0-1)*s0) / (n1+n0-2))
    return (np.mean(x1) - np.mean(x0)) / sp if sp > 0 else np.nan

# ---------- load ----------
df = pd.read_excel(PATH, sheet_name="Sheet1", dtype=str)

# normalize column names to strip weird spaces/quotes
df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]

# find the "high status" column automatically
status_candidates = [c for c in df.columns if "high status" in c.lower()]
if not status_candidates:
    raise ValueError("Could not find a column mentioning 'high status'")
COL_HIGH_STATUS = status_candidates[0]

# clean numerics
for c in EXCL_COLS + [COL_HIGH_STATUS, COL_FIN_STABLE]:
    df[c] = clean_numeric(df[c])

# ---------- exclusivity index ----------
df["excl_index"] = df[EXCL_COLS].mean(axis=1, skipna=True)
valid_excl = df[EXCL_COLS].notna().sum(axis=1) >= 2
df.loc[~valid_excl, "excl_index"] = np.nan
excl_nonnull = df["excl_index"].dropna()

# ---------- H2/H2a ----------
if len(excl_nonnull) >= 5:
    t_excl, p_excl = stats.ttest_1samp(excl_nonnull, popmean=3.0, alternative="greater")
    print("H2/H2a: One-sample t-test on exclusivity index vs neutral=3 (greater means more exclusive):")
    print(f"  n={len(excl_nonnull)}, mean={excl_nonnull.mean():.3f}, sd={excl_nonnull.std(ddof=1):.3f}")
    print(f"  t={t_excl:.3f}, p={p_excl:.4f}")

# ---------- H2b: Welch t-test ----------
fin = df[COL_FIN_STABLE]
status_score = df[COL_HIGH_STATUS]
tmp = pd.DataFrame({"fin": fin, "status_score": status_score}).dropna()

g0 = tmp.loc[tmp["fin"] == 0, "status_score"]
g1 = tmp.loc[tmp["fin"] == 1, "status_score"]

print("\nH2b (Welch test): Do financially stable shoppers differ in belief BNPL attracts high-status shoppers?")
print(f"  n0={len(g0)}, n1={len(g1)}, means: {g0.mean():.2f} vs {g1.mean():.2f}")
if len(g0) >= 5 and len(g1) >= 5:
    t, p = stats.ttest_ind(g1, g0, equal_var=False)
    d = cohens_d_ind(g1.to_numpy(), g0.to_numpy())
    print(f"  Welch t={t:.3f}, p={p:.4f}, Cohen's d={d:.2f}")

# ---------- H2b: Chi-square ----------
agree_bin = np.where(status_score >= 4, 1, 0)
tmp2 = pd.DataFrame({"fin": fin, "agree": agree_bin}).dropna()
cont = pd.crosstab(tmp2["fin"], tmp2["agree"])
print("\nH2b (Chi-square, optional): Financial stability × agreement that BNPL attracts high-status shoppers (≥4)")
print(cont)
if cont.shape == (2, 2):
    chi2, p_chi, dof, exp = stats.chi2_contingency(cont)
    n = cont.values.sum()
    phi = np.sqrt(chi2 / n) if n > 0 else np.nan
    min_expected = exp.min()
    print(f"  Chi-square: chi2={chi2:.3f}, dof={dof}, p={p_chi:.4f}, phi={phi:.3f}, min expected={min_expected:.2f}")
    if min_expected < 5:
        oddsratio, p_fisher = stats.fisher_exact(cont.values)
        print(f"  Fisher’s exact (small counts): odds ratio={oddsratio:.3f}, p={p_fisher:.4f}")

# This code was generated with the assistance of ChatGPT (OpenAI, 2025)
