import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
import io
import time
import re
import json

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Golden Data | MDM",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=IBM+Plex+Mono:wght@500&display=swap');

:root {
    --blue:        #1d4ed8;
    --blue-mid:    #2563eb;
    --blue-light:  #3b82f6;
    --blue-pale:   #eff6ff;
    --blue-border: #bfdbfe;
    --indigo:      #4f46e5;
    --gold:        #d97706;
    --gold-light:  #fef3c7;
    --gold-border: #fde68a;
    --teal:        #0d9488;
    --teal-pale:   #f0fdfa;
    --purple:      #7c3aed;
    --purple-pale: #f5f3ff;
    --bg:          #f4f7fe;
    --card:        #ffffff;
    --border:      #e2e8f0;
    --text:        #0f172a;
    --muted:       #64748b;
    --danger:      #dc2626;
    --success:     #16a34a;
    --warn:        #d97706;
    --radius:      14px;
    --shadow:      0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(37,99,235,.06);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg);
    color: var(--text);
}
.stApp { background-color: var(--bg); }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0f2460 0%, #1d4ed8 55%, #3b82f6 100%);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(29,78,216,.28);
}
.hero::before {
    content:'';position:absolute;top:-60px;right:-60px;
    width:220px;height:220px;border-radius:50%;
    background:rgba(255,255,255,0.05);
}
.hero::after {
    content:'';position:absolute;bottom:-40px;left:30%;
    width:160px;height:160px;border-radius:50%;
    background:rgba(255,255,255,0.04);
}
.hero-icon {
    width:68px;height:68px;
    background:rgba(255,255,255,0.15);
    border:2px solid rgba(255,255,255,0.25);
    border-radius:16px;
    display:flex;align-items:center;justify-content:center;
    font-size:30px;flex-shrink:0;
}
.hero-text h1 { font-size:1.9rem;font-weight:900;margin:0 0 3px 0;color:#fff;letter-spacing:-0.02em; }
.hero-text .sub { font-size:0.88rem;color:rgba(255,255,255,0.72);margin:0 0 5px 0; }
.hero-text .tagline { font-size:0.78rem;color:#fde68a;font-weight:700;letter-spacing:0.1em;text-transform:uppercase; }
.hero-badge {
    margin-left:auto;
    background:rgba(255,255,255,0.12);
    border:1px solid rgba(255,255,255,0.2);
    border-radius:12px;padding:10px 18px;
    text-align:center;color:white;font-size:0.76rem;backdrop-filter:blur(4px);
}
.hero-badge .hb-val { font-size:1.5rem;font-weight:900;color:#fde68a;display:block; }

/* ── Stepper ── */
.stepper {
    display:flex;align-items:center;
    margin-bottom:24px;
    background:var(--card);
    border:1.5px solid var(--border);
    border-radius:var(--radius);
    padding:14px 24px;
    box-shadow:var(--shadow);
    overflow-x:auto;
    gap:4px;
}
.step { display:flex;align-items:center;gap:9px;flex:1;min-width:fit-content; }
.step-circle {
    width:32px;height:32px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:0.82rem;flex-shrink:0;
}
.step-circle.active  { background:var(--blue-mid);color:#fff;box-shadow:0 0 0 3px var(--blue-pale); }
.step-circle.done    { background:var(--blue-pale);color:var(--blue);border:2px solid var(--blue-light); }
.step-circle.pending { background:#f1f5f9;color:var(--muted); }
.step-label { font-size:0.8rem;font-weight:700;white-space:nowrap; }
.step-label.active  { color:var(--blue); }
.step-label.pending { color:var(--muted); }
.step-connector { flex:1;height:2px;background:#e2e8f0;margin:0 6px;max-width:60px;min-width:16px; }
.step-connector.done { background:var(--blue-light); }

/* ── Cards ── */
.card {
    background:var(--card);
    border:1.5px solid var(--border);
    border-radius:var(--radius);
    padding:22px 26px;
    margin-bottom:18px;
    box-shadow:var(--shadow);
}
.card-title {
    font-size:0.7rem;font-weight:700;
    letter-spacing:0.12em;text-transform:uppercase;
    color:var(--muted);margin-bottom:14px;
}

/* ── Metrics ── */
.metric-row { display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px; }
@media(max-width:640px){ .metric-row { grid-template-columns:repeat(2,1fr); } }
.metric-card {
    background:var(--card);border:1.5px solid var(--border);
    border-radius:12px;padding:16px 18px;text-align:center;
    box-shadow:var(--shadow);
}
.metric-card .val { font-size:1.75rem;font-weight:900;color:var(--blue-mid); }
.metric-card .lbl { font-size:0.74rem;color:var(--muted);margin-top:2px;font-weight:500; }

/* ── Group Cards ── */
.group-card {
    background:var(--blue-pale);border:1.5px solid var(--blue-border);
    border-radius:12px;padding:14px 18px;margin-bottom:12px;
}
.group-header { display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap; }
.group-id {
    background:var(--blue-mid);color:#fff;
    border-radius:20px;padding:2px 12px;
    font-size:0.72rem;font-weight:700;font-family:'IBM Plex Mono',monospace;
}
.name-row {
    display:flex;align-items:center;gap:8px;padding:7px 12px;
    border-radius:8px;margin-bottom:5px;
    background:var(--card);border:1px solid var(--blue-border);
    font-size:0.86rem;
}
.name-row.golden { background:var(--gold-light);border-color:var(--gold-border);font-weight:700; }
.golden-badge {
    background:var(--gold);color:#fff;border-radius:20px;
    padding:1px 10px;font-size:0.68rem;font-weight:700;flex-shrink:0;
}
.score-pill { margin-left:auto;border-radius:20px;padding:2px 10px;font-size:0.72rem;font-weight:700; }
.score-high   { background:#dcfce7;color:#15803d; }
.score-medium { background:#fef9c3;color:#a16207; }
.score-low    { background:#fee2e2;color:#dc2626; }

/* ── Buttons ── */
.stButton > button {
    background:linear-gradient(135deg,var(--blue-mid),var(--blue)) !important;
    color:white !important;border:none !important;
    border-radius:10px !important;font-family:'Inter',sans-serif !important;
    font-weight:700 !important;font-size:0.9rem !important;
    padding:10px 22px !important;transition:all 0.2s !important;
    box-shadow:0 2px 8px rgba(37,99,235,.22) !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#1e40af,#1d4ed8) !important;
    transform:translateY(-1px);
    box-shadow:0 4px 14px rgba(37,99,235,0.35) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border:2px dashed var(--blue-border) !important;
    border-radius:12px !important;background:var(--blue-pale) !important;
    padding:14px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:transparent !important;border-bottom:2px solid var(--border) !important;gap:4px; }
.stTabs [data-baseweb="tab"] { font-family:'Inter',sans-serif !important;font-weight:600 !important;color:var(--muted) !important; }
.stTabs [aria-selected="true"] { color:var(--blue-mid) !important;border-bottom:2px solid var(--blue-mid) !important; }
.stProgress > div > div { background-color:var(--blue-mid) !important;border-radius:4px; }

/* ── AI Chat bubble ── */
.ai-message {
    background:linear-gradient(135deg,var(--purple-pale),#faf5ff);
    border:1.5px solid #ddd6fe;border-radius:14px;
    padding:16px 20px;margin-bottom:12px;
    font-size:0.9rem;line-height:1.75;
    position:relative;
}
.ai-message::before {
    content:'🤖';position:absolute;top:-12px;left:16px;
    background:#fff;padding:0 6px;font-size:1.1rem;
}
.user-message {
    background:var(--blue-pale);border:1.5px solid var(--blue-border);
    border-radius:14px;padding:12px 18px;margin-bottom:10px;
    font-size:0.88rem;color:#1e40af;
}

/* ── Responsive ── */
@media(max-width:640px){
    .hero { padding:20px 18px;gap:14px; }
    .hero-text h1 { font-size:1.4rem; }
    .hero-badge { display:none; }
    .stepper { padding:12px 14px; }
    .card { padding:16px 14px; }
    .block-container { padding-left:12px !important;padding-right:12px !important; }
}

#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:1.8rem;padding-bottom:3rem; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def safe_slider(label, max_val, default=20, key=None):
    if max_val <= 1:
        return max_val
    return st.slider(label, min_value=1, max_value=min(100, max_val),
                     value=min(default, max_val), key=key)


def normalize_arabic(text):
    if not isinstance(text, str): return ""
    text = text.strip()
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[يى]', 'ي', text)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def match_columns(df1, col_configs, df2=None, col_configs2=None, mode="within", progress_bar=None):
    """
    Multi-column matching. col_configs = list of {col, match_type, threshold}
    match_type: "exact" | "fuzzy"
    Returns DataFrame of matching pairs with group_code.
    """
    if mode == "within":
        records1 = df1[col_configs[0]["col"]].fillna("").tolist()  # primary col for display
        n = len(records1)
        # Build composite key for each row
        keys = []
        for idx in range(n):
            parts = []
            for cfg in col_configs:
                val = str(df1[cfg["col"]].iloc[idx]) if idx < len(df1) else ""
                parts.append(normalize_arabic(val) if cfg.get("normalize", True) else val.strip())
            keys.append(parts)

        results = []
        total = n
        for i in range(total):
            if i % 100 == 0 and progress_bar:
                progress_bar.progress(min(i / total, 0.99))
            if not any(keys[i]): continue
            for j in range(i + 1, total):
                if not any(keys[j]): continue
                scores = []
                for c_idx, cfg in enumerate(col_configs):
                    a, b = keys[i][c_idx], keys[j][c_idx]
                    if cfg["match_type"] == "exact":
                        sc = 100 if a == b else 0
                    else:
                        sc = fuzz.token_sort_ratio(a, b)
                    scores.append(sc)
                # All columns must meet their threshold
                if all(scores[c_idx] >= cfg["threshold"] for c_idx, cfg in enumerate(col_configs)):
                    avg_sc = round(sum(scores) / len(scores))
                    row = {
                        "Row A": i + 2, "Row B": j + 2,
                        "Status": "Exact Match" if avg_sc == 100 else "Similar",
                        "Avg Score": avg_sc
                    }
                    for c_idx, cfg in enumerate(col_configs):
                        row[f"A: {cfg['col']}"] = str(df1[cfg["col"]].iloc[i])
                        row[f"B: {cfg['col']}"] = str(df1[cfg["col"]].iloc[j])
                        row[f"Score: {cfg['col']}"] = scores[c_idx]
                    results.append(row)
        if progress_bar: progress_bar.progress(1.0)
        return pd.DataFrame(results)
    else:
        # across files
        names1 = df1[col_configs[0]["col"]].fillna("").tolist()
        col2 = col_configs2[0]["col"] if col_configs2 else col_configs[0]["col"]
        names2 = df2[col2].fillna("").tolist()
        thresh = col_configs[0]["threshold"]
        norm1 = [normalize_arabic(n) for n in names1]
        norm2 = [normalize_arabic(n) for n in names2]
        results = []
        total = len(norm1)
        for i, (name1, n1) in enumerate(zip(names1, norm1)):
            if i % 100 == 0 and progress_bar:
                progress_bar.progress(min(i / total, 0.99))
            if not n1: continue
            matches = process.extract(n1, norm2, scorer=fuzz.token_sort_ratio,
                                      limit=3, score_cutoff=thresh)
            for _, score, idx in matches:
                results.append({
                    "Row (File 1)": i + 2, f"A: {col_configs[0]['col']}": name1,
                    "Row (File 2)": idx + 2, f"B: {col2}": names2[idx],
                    "Avg Score": score,
                    "Status": "Exact Match" if score == 100 else "Similar"
                })
        if progress_bar: progress_bar.progress(1.0)
        return pd.DataFrame(results)


def build_clusters(results_df):
    from collections import defaultdict
    # find col_a and col_b – first A: and B: columns
    col_a = next((c for c in results_df.columns if c.startswith("A:")), None)
    col_b = next((c for c in results_df.columns if c.startswith("B:")), None)
    if col_a is None or col_b is None:
        return []
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        if parent[x] != x: parent[x] = find(parent[x])
        return parent[x]
    def union(x, y): parent[find(x)] = find(y)
    scores = {}
    for _, row in results_df.iterrows():
        a, b = str(row[col_a]), str(row[col_b])
        union(a, b)
        key = tuple(sorted([a, b]))
        scores[key] = max(scores.get(key, 0), int(row["Avg Score"]))
    groups = defaultdict(set)
    for name in parent:
        groups[find(name)].add(name)
    clusters = []
    for _, members in groups.items():
        members = sorted(members)
        max_sc = 0
        for i, a in enumerate(members):
            for b in members[i+1:]:
                key = tuple(sorted([a, b]))
                max_sc = max(max_sc, scores.get(key, 0))
        clusters.append({"names": members, "max_score": max_sc})
    clusters.sort(key=lambda x: -x["max_score"])
    return clusters


def pick_golden_record(names):
    return max(names, key=lambda n: (len(n), n))


# ── Data Profile ──────────────────────────────────────────────────────────────

def profile_dataframe(df):
    profiles = []
    total_rows = len(df)
    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        non_null = series.dropna()
        unique_count = int(series.nunique())
        dtype = str(series.dtype)
        sample = " ".join(non_null.astype(str).head(20).tolist())
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', sample))
        if pd.api.types.is_numeric_dtype(series): col_type = "Numeric"
        elif pd.api.types.is_datetime64_any_dtype(series): col_type = "Date"
        else: col_type = "Arabic Text" if arabic_chars > len(sample) * 0.2 else "Text"
        completeness = round((1 - null_count / total_rows) * 100, 1) if total_rows else 100
        uniqueness = round(unique_count / total_rows * 100, 1) if total_rows else 0
        p = {
            "col": col, "dtype": dtype, "col_type": col_type,
            "total": total_rows, "non_null": total_rows - null_count,
            "null_count": null_count,
            "null_pct": round(null_count / total_rows * 100, 1) if total_rows else 0,
            "unique_count": unique_count,
            "unique_pct": uniqueness,
            "completeness": completeness,
            "uniqueness": uniqueness,
        }
        if col_type == "Numeric" and len(non_null):
            p.update({"min": round(float(non_null.min()), 2), "max": round(float(non_null.max()), 2),
                       "mean": round(float(non_null.mean()), 2), "median": round(float(non_null.median()), 2),
                       "std": round(float(non_null.std()), 2), "zeros": int((non_null == 0).sum()),
                       "negatives": int((non_null < 0).sum())})
        else:
            p.update({"min": None, "max": None, "mean": None, "median": None,
                       "std": None, "zeros": 0, "negatives": 0})
        if col_type in ["Text", "Arabic Text"] and len(non_null):
            lengths = non_null.astype(str).str.len()
            p["avg_len"] = round(float(lengths.mean()), 1)
            p["min_len"] = int(lengths.min())
            p["max_len"] = int(lengths.max())
        else:
            p["avg_len"] = p["min_len"] = p["max_len"] = None
        top_vals = series.value_counts().head(5)
        p["top_values"] = [(str(k), int(v)) for k, v in top_vals.items()]
        profiles.append(p)
    return profiles


def mini_bar(value, color="#2563eb", width=100):
    pct = min(value, 100)
    return (f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="width:{width}px;height:8px;background:#e2e8f0;border-radius:5px;overflow:hidden">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:5px"></div></div>'
            f'<span style="font-size:0.76rem;font-weight:700;color:{color}">{value:.1f}%</span></div>')


def render_profile_section(df):
    profiles = profile_dataframe(df)
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    total_nulls = int(df.isna().sum().sum())
    completeness = round((1 - total_nulls / total_cells) * 100, 1) if total_cells else 100
    uniqueness_overall = round(df.drop_duplicates().shape[0] / total_rows * 100, 1) if total_rows else 100
    dup_rows = int(df.duplicated().sum())
    dq_score = round((completeness * 0.6 + uniqueness_overall * 0.4), 1)

    comp_color = "#16a34a" if completeness >= 90 else "#d97706" if completeness >= 70 else "#dc2626"
    uniq_color = "#16a34a" if uniqueness_overall >= 90 else "#d97706" if uniqueness_overall >= 70 else "#dc2626"

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px">
        <div class="metric-card"><div class="val">{total_rows:,}</div><div class="lbl">Total Rows</div></div>
        <div class="metric-card"><div class="val">{total_cols}</div><div class="lbl">Columns</div></div>
        <div class="metric-card">
            <div class="val" style="color:{comp_color}">{completeness}%</div>
            <div class="lbl">Completeness</div>
        </div>
        <div class="metric-card">
            <div class="val" style="color:{uniq_color}">{uniqueness_overall}%</div>
            <div class="lbl">Uniqueness</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Completeness & Uniqueness Gauge Charts
    g1, g2, g3 = st.columns(3)
    def gauge_svg(value, label, color, icon):
        angle = value / 100 * 180
        rad = (180 - angle) * 3.14159 / 180
        cx, cy, r = 80, 75, 55
        x = cx + r * (-1 if angle <= 90 else 1) * abs(0 if angle == 0 else (1 - 2*(angle/180)))
        import math
        x2 = cx + r * math.cos(math.radians(180 - angle))
        y2 = cy - r * math.sin(math.radians(180 - angle))
        fill_color = color
        bg_color = "#e2e8f0"
        return f"""
        <div style="text-align:center;background:var(--card);border:1.5px solid var(--border);
            border-radius:12px;padding:16px 10px;box-shadow:var(--shadow)">
            <svg width="160" height="90" viewBox="0 0 160 90">
              <path d="M20,75 A60,60 0 0,1 140,75" fill="none" stroke="{bg_color}" stroke-width="12" stroke-linecap="round"/>
              <path d="M20,75 A60,60 0 0,1 140,75" fill="none" stroke="{fill_color}" stroke-width="12"
                stroke-linecap="round" stroke-dasharray="{value * 1.885} 188.5" />
              <text x="80" y="68" text-anchor="middle" font-size="18" font-weight="900" fill="{fill_color}"
                font-family="Inter,sans-serif">{value:.0f}%</text>
            </svg>
            <div style="font-size:0.76rem;font-weight:700;color:var(--muted);margin-top:-4px">{icon} {label}</div>
        </div>"""

    import math
    with g1:
        st.markdown(gauge_svg(completeness, "Completeness", comp_color, "✅"), unsafe_allow_html=True)
    with g2:
        st.markdown(gauge_svg(uniqueness_overall, "Uniqueness", uniq_color, "🔷"), unsafe_allow_html=True)
    with g3:
        dq_color = "#16a34a" if dq_score >= 85 else "#d97706" if dq_score >= 65 else "#dc2626"
        st.markdown(gauge_svg(dq_score, "Data Quality Score", dq_color, "🏅"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    selected_col = st.selectbox("🔍 Select column for details:", [p["col"] for p in profiles], key=f"prof_sel_{id(df)}")

    # Table of all columns
    rows_html = ""
    for p in profiles:
        hl = "background:#eff6ff;" if p["col"] == selected_col else ""
        comp_c = "#16a34a" if p["completeness"] >= 90 else "#d97706" if p["completeness"] >= 70 else "#dc2626"
        uniq_c = "#16a34a" if p["uniqueness"] >= 90 else "#d97706" if p["uniqueness"] >= 70 else "#6366f1"
        rows_html += f"""
        <tr style="border-bottom:1px solid #dbeafe;{hl}">
            <td style="padding:9px 12px;font-weight:{'700' if p['col']==selected_col else '400'}">{p['col']}</td>
            <td style="padding:9px 12px"><span style="background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:20px;font-size:0.7rem;font-weight:700">{p['col_type']}</span></td>
            <td style="padding:9px 12px">{mini_bar(p['completeness'], comp_c)}</td>
            <td style="padding:9px 12px;font-size:0.82rem;color:#64748b">{p['null_count']:,} empty</td>
            <td style="padding:9px 12px">{mini_bar(p['uniqueness'], uniq_c)}</td>
            <td style="padding:9px 12px;font-size:0.82rem;color:#64748b">{p['unique_count']:,} unique</td>
        </tr>"""

    st.markdown(f"""
    <div class="card" style="padding:0;overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif">
            <thead><tr style="background:#f8faff;border-bottom:2px solid #dbeafe">
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">COLUMN</th>
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">TYPE</th>
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">COMPLETENESS</th>
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">EMPTY</th>
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">UNIQUENESS</th>
                <th style="padding:11px;text-align:left;font-size:0.72rem;color:#64748b;font-weight:700">UNIQUE VALUES</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    p = next((x for x in profiles if x["col"] == selected_col), None)
    if not p: return

    st.markdown(f"#### 🔬 Column Detail: `{selected_col}`")
    col_a, col_b = st.columns(2, gap="large")
    hc = "#16a34a" if p["completeness"] >= 90 else "#d97706" if p["completeness"] >= 70 else "#dc2626"
    hl_label = "Excellent ✅" if p["completeness"] >= 90 else "Moderate ⚠️" if p["completeness"] >= 70 else "Needs Review ❌"
    uc = "#16a34a" if p["uniqueness"] >= 90 else "#d97706" if p["uniqueness"] >= 70 else "#6366f1"
    ul_label = "High Uniqueness ✅" if p["uniqueness"] >= 90 else "Moderate 🔷" if p["uniqueness"] >= 70 else "Low Uniqueness ⚠️"

    with col_a:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏥 Column Health</div>
            <div style="display:flex;gap:14px;margin-bottom:14px;flex-wrap:wrap">
                <div style="text-align:center">
                    <div style="width:62px;height:62px;border-radius:50%;border:4px solid {hc};
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;font-weight:900;color:{hc};margin:0 auto">{p['completeness']:.0f}%</div>
                    <div style="font-size:0.7rem;color:#64748b;margin-top:4px">Completeness</div>
                </div>
                <div style="text-align:center">
                    <div style="width:62px;height:62px;border-radius:50%;border:4px solid {uc};
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;font-weight:900;color:{uc};margin:0 auto">{p['uniqueness']:.0f}%</div>
                    <div style="font-size:0.7rem;color:#64748b;margin-top:4px">Uniqueness</div>
                </div>
            </div>
            <div style="font-size:0.84rem;line-height:2.2">
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">Type</span><span style="font-weight:700">{p['col_type']} ({p['dtype']})</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">Total</span><span style="font-weight:700">{p['total']:,}</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">Non-Empty</span><span style="font-weight:700;color:#16a34a">{p['non_null']:,}</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">Empty</span>
                    <span style="font-weight:700;color:{'#dc2626' if p['null_count']>0 else '#16a34a'}">{p['null_count']:,} ({p['null_pct']}%)</span></div>
                <div style="display:flex;justify-content:space-between;padding:2px 0">
                    <span style="color:#64748b">Unique</span><span style="font-weight:700;color:#6366f1">{p['unique_count']:,} ({p['unique_pct']}%)</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    with col_b:
        if p["col_type"] == "Numeric" and p["mean"] is not None:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📈 Numeric Statistics</div>
                <div style="font-size:0.84rem;line-height:2.2">
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Min</span><span style="font-weight:700">{p['min']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Max</span><span style="font-weight:700">{p['max']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Mean</span><span style="font-weight:700;color:#2563eb">{p['mean']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Median</span><span style="font-weight:700">{p['median']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Std Dev</span><span style="font-weight:700">{p['std']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;padding:2px 0">
                        <span style="color:#64748b">Zeros / Negatives</span>
                        <span style="font-weight:700">{p['zeros']:,} / {p['negatives']:,}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📝 Text Statistics</div>
                <div style="font-size:0.84rem;line-height:2.5">
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Avg Length</span><span style="font-weight:700">{p.get('avg_len','—')} chars</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Shortest</span><span style="font-weight:700">{p.get('min_len','—')} chars</span></div>
                    <div style="display:flex;justify-content:space-between;padding:2px 0">
                        <span style="color:#64748b">Longest</span><span style="font-weight:700">{p.get('max_len','—')} chars</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Top values bar chart
    if p.get("top_values"):
        st.markdown("##### 🏆 Top Recurring Values")
        top = p["top_values"]
        max_c = top[0][1] if top else 1
        colors = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
        bars = ""
        for i, (val, cnt) in enumerate(top):
            pct = cnt / len(df) * 100
            bw = int(cnt / max_c * 100)
            bars += f"""
            <div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="font-size:0.82rem;font-weight:600;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{val}</span>
                    <span style="font-size:0.78rem;color:#64748b">{cnt:,} <span style="color:{colors[i]}">({pct:.1f}%)</span></span>
                </div>
                <div style="height:7px;background:#e2e8f0;border-radius:4px;overflow:hidden">
                    <div style="width:{bw}%;height:100%;background:{colors[i]};border-radius:4px"></div>
                </div>
            </div>"""
        st.markdown(f'<div class="card">{bars}</div>', unsafe_allow_html=True)

    # Column completeness sparkline chart for all columns
    st.markdown("##### 📊 Completeness & Uniqueness — All Columns")
    chart_data = json.dumps([{"col": p2["col"][:14], "comp": p2["completeness"], "uniq": p2["uniqueness"]} for p2 in profiles])
    st.markdown(f"""
    <div class="card">
        <div id="prof-chart" style="overflow-x:auto;padding:8px 0"></div>
    </div>
    <script>(function(){{
        const d={chart_data};
        const el=document.getElementById('prof-chart');if(!el)return;
        const W=Math.max(d.length*70,300);
        let svg=`<svg width="${{W}}" height="160" viewBox="0 0 ${{W}} 160" xmlns="http://www.w3.org/2000/svg">`;
        d.forEach((item,i)=>{{
            const x=i*70+10;
            const ch=Math.round(item.comp/100*110);
            const uh=Math.round(item.uniq/100*110);
            svg+=`<rect x="${{x}}" y="${{140-ch}}" width="22" height="${{ch}}" rx="4" fill="#2563eb" opacity="0.85"/>`;
            svg+=`<rect x="${{x+24}}" y="${{140-uh}}" width="22" height="${{uh}}" rx="4" fill="#6366f1" opacity="0.85"/>`;
            svg+=`<text x="${{x+11}}" y="156" text-anchor="middle" font-size="9" fill="#64748b" font-family="Inter,sans-serif">${{item.col}}</text>`;
        }});
        svg+=`<line x1="0" y1="140" x2="${{W}}" y2="140" stroke="#e2e8f0" stroke-width="1"/>`;
        svg+=`</svg>`;
        el.innerHTML=svg+`<div style="display:flex;gap:16px;margin-top:8px;font-size:0.72rem;color:#64748b">
            <span><span style="display:inline-block;width:10px;height:10px;background:#2563eb;border-radius:2px;margin-right:4px"></span>Completeness</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#6366f1;border-radius:2px;margin-right:4px"></span>Uniqueness</span>
        </div>`;
    }})();</script>
    """, unsafe_allow_html=True)

    # Export
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        rows = []
        for p2 in profiles:
            r = {"Column": p2["col"], "Type": p2["col_type"], "Data Type": p2["dtype"],
                 "Total Rows": p2["total"], "Non-Empty": p2["non_null"],
                 "Empty Count": p2["null_count"], "Empty %": p2["null_pct"],
                 "Unique Count": p2["unique_count"],
                 "Uniqueness %": p2["unique_pct"],
                 "Completeness %": p2["completeness"]}
            if p2["mean"] is not None:
                r.update({"Min": p2["min"], "Max": p2["max"], "Mean": p2["mean"],
                           "Median": p2["median"], "Std Dev": p2["std"]})
            rows.append(r)
        pd.DataFrame(rows).to_excel(writer, sheet_name="Data Profile", index=False)
    out.seek(0)
    st.download_button("⬇️ Download Profile Report (Excel)", data=out,
                        file_name="data_profile.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_prof_{id(df)}")


# ══════════════════════════════════════════════════════════════════════════════
# AI ANALYSIS SECTION
# ══════════════════════════════════════════════════════════════════════════════

def render_ai_analysis(df, context="uploaded data"):
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border:1.5px solid #ddd6fe;
        border-radius:14px;padding:16px 20px;margin-bottom:16px">
        <h4 style="margin:0 0 6px 0;color:#5b21b6">🤖 AI Data Analyst</h4>
        <p style="margin:0;color:#6d28d9;font-size:0.87rem">
            Ask questions about your data in plain English. Powered by Claude AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Build data summary for AI
    profiles = profile_dataframe(df)
    total_rows = len(df)
    total_cols = len(df.columns)
    total_nulls = int(df.isna().sum().sum())
    dup_rows = int(df.duplicated().sum())
    completeness = round((1 - total_nulls / (total_rows * total_cols)) * 100, 1) if total_rows * total_cols else 100

    col_summaries = []
    for p in profiles:
        s = f"Column '{p['col']}' (type:{p['col_type']}, completeness:{p['completeness']}%, uniqueness:{p['uniqueness']}%"
        if p["col_type"] == "Numeric" and p["mean"] is not None:
            s += f", min:{p['min']}, max:{p['max']}, mean:{p['mean']}"
        if p.get("top_values"):
            top_str = ", ".join([f"'{v}'({c})" for v, c in p["top_values"][:3]])
            s += f", top values: {top_str}"
        s += ")"
        col_summaries.append(s)

    data_summary = f"""Dataset: {total_rows:,} rows, {total_cols} columns.
Overall completeness: {completeness}%, duplicate rows: {dup_rows:,}.
Columns: {'; '.join(col_summaries)}
Sample data (first 3 rows): {df.head(3).to_dict(orient='records')}"""

    # Chat history
    chat_key = f"ai_chat_{id(df)}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    # Quick prompt buttons
    st.markdown("**💡 Quick Analysis Prompts:**")
    qp_cols = st.columns(3)
    quick_prompts = [
        "Summarize the overall data quality and key issues",
        "What columns need the most attention and why?",
        "Identify any patterns or anomalies in this data",
        "What data cleaning steps would you recommend?",
        "Which columns have the best and worst quality?",
        "Give me a data governance risk assessment"
    ]
    for i, qp in enumerate(quick_prompts[:6]):
        with qp_cols[i % 3]:
            if st.button(f"💬 {qp[:35]}...", key=f"qp_{id(df)}_{i}"):
                st.session_state[chat_key].append({"role": "user", "content": qp})
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat display
    for msg in st.session_state[chat_key]:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message">{msg["content"]}</div>', unsafe_allow_html=True)

    # Process pending user message
    if st.session_state[chat_key] and st.session_state[chat_key][-1]["role"] == "user":
        user_q = st.session_state[chat_key][-1]["content"]
        with st.spinner("🤖 Analyzing your data..."):
            try:
                import requests
                messages_payload = []
                # Add conversation history
                for msg in st.session_state[chat_key]:
                    messages_payload.append({"role": msg["role"], "content": msg["content"]})

                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1000,
                        "system": f"""You are an expert Data Quality Analyst specializing in Master Data Management (MDM).
You are analyzing a dataset and must provide clear, actionable insights.
Always be specific, mention column names, percentages, and concrete recommendations.
Format your response in a readable way using bullet points where appropriate.
Keep responses focused and practical (max 300 words).

Dataset context:
{data_summary}""",
                        "messages": messages_payload
                    }
                )
                data = response.json()
                ai_text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        ai_text += block["text"]
                if not ai_text:
                    ai_text = "Sorry, I couldn't generate an analysis at this time. Please try again."
                st.session_state[chat_key].append({"role": "assistant", "content": ai_text})
                st.rerun()
            except Exception as e:
                st.session_state[chat_key].append({"role": "assistant",
                    "content": f"⚠️ Analysis error: {str(e)[:100]}. Please check your connection."})
                st.rerun()

    # Input
    user_input = st.text_input("💬 Ask AI about your data...",
                                placeholder="e.g., What are the main data quality issues?",
                                key=f"ai_input_{id(df)}")
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Send →", key=f"ai_send_{id(df)}"):
            if user_input.strip():
                st.session_state[chat_key].append({"role": "user", "content": user_input.strip()})
                st.rerun()
    with c1:
        if st.button("🗑️ Clear Chat", key=f"ai_clear_{id(df)}"):
            st.session_state[chat_key] = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [("step", 1), ("results_df", None), ("mode", "within"),
              ("df1", None), ("df2", None), ("clusters", None), ("merged_df", None),
              ("col_configs", None)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
df1_loaded = st.session_state.get("df1")
total_records = len(df1_loaded) if df1_loaded is not None else 0

st.markdown(f"""
<div class="hero">
    <div class="hero-icon">🏅</div>
    <div class="hero-text">
        <h1>Golden Data</h1>
        <p class="sub">Master Data Management · Deduplication · AI Analytics</p>
        <p class="tagline">✦ Let's Master your Data ✦</p>
    </div>
    {"" if total_records == 0 else f'<div class="hero-badge"><span class="hb-val">{total_records:,}</span>Records Loaded</div>'}
</div>
""", unsafe_allow_html=True)

step = st.session_state.step

def sc(n): return "done" if n < step else ("active" if n == step else "pending")
def cc(n): return "done" if n < step else ""

st.markdown(f"""
<div class="stepper">
    <div class="step">
        <div class="step-circle {sc(1)}">{'✓' if step>1 else '1'}</div>
        <span class="step-label {'active' if step==1 else 'pending'}">Upload Data</span>
    </div>
    <div class="step-connector {cc(1)}"></div>
    <div class="step">
        <div class="step-circle {sc(2)}">{'✓' if step>2 else '2'}</div>
        <span class="step-label {'active' if step==2 else 'pending'}">Configure</span>
    </div>
    <div class="step-connector {cc(2)}"></div>
    <div class="step">
        <div class="step-circle {sc(3)}">{'✓' if step>3 else '3'}</div>
        <span class="step-label {'active' if step==3 else 'pending'}">Match & Clusters</span>
    </div>
    <div class="step-connector {cc(3)}"></div>
    <div class="step">
        <div class="step-circle {sc(4)}">{'✓' if step>4 else '4'}</div>
        <span class="step-label {'active' if step==4 else 'pending'}">Golden Record</span>
    </div>
    <div class="step-connector {cc(4)}"></div>
    <div class="step">
        <div class="step-circle {sc(5)}">5</div>
        <span class="step-label {'active' if step==5 else 'pending'}">AI Analysis</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    col_main, col_side = st.columns([2, 1], gap="large")

    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        mode = st.radio("**Match Mode:**",
                         ["Within a single file (deduplication)", "Across two files (cross-match)"],
                         horizontal=True)
        st.session_state.mode = "within" if "single" in mode else "across"
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.mode == "within":
            st.markdown('<div class="card-title">📁 Upload Excel / CSV File</div>', unsafe_allow_html=True)
            file1 = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"], key="f1", label_visibility="collapsed")
            st.caption("Supports `.xlsx` · `.csv` · up to 200MB")
            if file1:
                df1 = pd.read_csv(file1) if file1.name.endswith(".csv") else pd.read_excel(file1)
                st.session_state.df1 = df1
                st.session_state.df2 = None
                st.success(f"✅ **{file1.name}** — {len(df1):,} records · {len(df1.columns)} columns")
                prev_tab, prof_tab, ai_tab = st.tabs(["👁️ Preview", "📊 Data Profile", "🤖 AI Analysis"])
                with prev_tab:
                    st.dataframe(df1.head(10), use_container_width=True)
                with prof_tab:
                    render_profile_section(df1)
                with ai_tab:
                    render_ai_analysis(df1)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Next → Configure Matching", use_container_width=True):
                    st.session_state.step = 2; st.rerun()
        else:
            st.markdown('<div class="card-title">📁 File 1</div>', unsafe_allow_html=True)
            file1 = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"], key="f1", label_visibility="collapsed")
            st.markdown('<div class="card-title" style="margin-top:14px">📁 File 2</div>', unsafe_allow_html=True)
            file2 = st.file_uploader("Upload file", type=["xlsx", "xls", "csv"], key="f2", label_visibility="collapsed")
            if file1 and file2:
                df1 = pd.read_csv(file1) if file1.name.endswith(".csv") else pd.read_excel(file1)
                df2 = pd.read_csv(file2) if file2.name.endswith(".csv") else pd.read_excel(file2)
                st.session_state.df1 = df1; st.session_state.df2 = df2
                c1, c2 = st.columns(2)
                c1.success(f"✅ **{file1.name}** — {len(df1):,} records")
                c2.success(f"✅ **{file2.name}** — {len(df2):,} records")
                t1, t2, t3 = st.tabs([f"📊 Profile: {file1.name}", f"📊 Profile: {file2.name}", "🤖 AI Analysis"])
                with t1: render_profile_section(df1)
                with t2: render_profile_section(df2)
                with t3: render_ai_analysis(df1, context=f"File 1: {file1.name}")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Next → Configure Matching", use_container_width=True):
                    st.session_state.step = 2; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-title">ℹ️ What is MDM?</div>
            <p style="font-size:0.85rem;color:#475569;line-height:1.9;margin:0">
                <b>Master Data Management</b> is the process of cleaning and unifying master data across your organization.<br><br>
                🏅 <b>The Golden Record</b> is the single trusted version of each entity after merging duplicates.<br><br>
                🔹 Identify similar or duplicate records<br>
                🔹 Group them into clusters<br>
                🔹 Pick the golden record<br>
                🔹 Export a clean, unified dataset
            </p>
        </div>
        <div class="card">
            <div class="card-title">🤖 AI Features</div>
            <p style="font-size:0.84rem;color:#475569;line-height:2;margin:0">
                ✨ Ask questions about your data<br>
                📊 Get data quality insights<br>
                🔍 Identify anomalies & patterns<br>
                💡 Receive cleaning recommendations<br>
                📋 Data governance risk alerts
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — CONFIGURE (Multi-Column Matching)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    df1 = st.session_state.get("df1")
    df2 = st.session_state.get("df2")
    if df1 is None:
        st.warning("Please go back and upload a file first.")
        if st.button("← Back"): st.session_state.step = 1; st.rerun()
        st.stop()

    col_main, col_side = st.columns([2, 1], gap="large")
    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚙️ Match Configuration</div>', unsafe_allow_html=True)

        cols = list(df1.columns)

        if st.session_state.mode == "within":
            st.markdown("#### 🔗 Select Columns to Match On")
            st.info("💡 You can match on multiple columns. Each column can use Exact or Fuzzy matching with its own threshold.")

            num_cols = st.number_input("Number of matching columns:", min_value=1, max_value=min(6, len(cols)),
                                        value=1, step=1, key="num_match_cols")

            col_configs = []
            for idx in range(int(num_cols)):
                st.markdown(f"**Column {idx+1}:**")
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    sel_col = st.selectbox(f"Column:", cols, key=f"match_col_{idx}")
                with c2:
                    match_type = st.selectbox(f"Method:", ["Fuzzy", "Exact"], key=f"match_type_{idx}")
                with c3:
                    if match_type == "Fuzzy":
                        thresh = st.slider(f"Threshold:", 50, 100, 80, 5, key=f"match_thresh_{idx}")
                    else:
                        thresh = 100
                        st.markdown(f"<br><span style='color:#16a34a;font-weight:700;font-size:0.85rem'>100% — Exact</span>", unsafe_allow_html=True)

                col_configs.append({
                    "col": sel_col,
                    "match_type": match_type.lower(),
                    "threshold": thresh,
                    "normalize": True
                })
                if idx < int(num_cols) - 1:
                    st.markdown("<hr style='border-color:#e2e8f0;margin:8px 0'>", unsafe_allow_html=True)

            st.session_state.col_configs = col_configs
            name_col1 = col_configs[0]["col"]
            name_col2 = None

        else:
            st.markdown("**File 1 — Primary Column:**")
            name_col1 = st.selectbox("Column (File 1):", cols, key="col1")
            match_type1 = st.selectbox("Match Method:", ["Fuzzy", "Exact"], key="mt1")
            thresh1 = st.slider("Threshold:", 50, 100, 80, 5, key="thr1") if match_type1 == "Fuzzy" else 100
            col_configs = [{"col": name_col1, "match_type": match_type1.lower(), "threshold": thresh1, "normalize": True}]

            st.markdown("<br>**File 2 — Match Column:**")
            cols2 = list(df2.columns) if df2 is not None else []
            name_col2 = st.selectbox("Column (File 2):", cols2, key="col2")
            col_configs2 = [{"col": name_col2, "match_type": match_type1.lower(), "threshold": thresh1, "normalize": True}]
            st.session_state.col_configs = col_configs
            st.session_state.col_configs2 = col_configs2

        st.markdown("<br>", unsafe_allow_html=True)
        st.checkbox("✅ Normalize Arabic names (recommended)", value=True, key="normalize_cb")
        st.session_state.name_col1 = name_col1
        st.session_state.name_col2 = name_col2

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = 1; st.rerun()
        with b2:
            if st.button("🚀 Start Matching", use_container_width=True):
                st.session_state.step = 3
                st.session_state.results_df = None
                st.session_state.clusters = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        config_info = ""
        if st.session_state.get("col_configs"):
            for i, cfg in enumerate(st.session_state.col_configs):
                color = "#16a34a" if cfg["match_type"] == "exact" else "#2563eb"
                config_info += f"""<div style="padding:8px 0;border-bottom:1px solid #f1f5f9">
                    <b>{cfg['col']}</b><br>
                    <span style="color:{color};font-size:0.8rem">{'🎯 Exact' if cfg['match_type']=='exact' else f'🔍 Fuzzy ≥{cfg["threshold"]}%'}</span>
                </div>"""

        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Current Configuration</div>
            {config_info or '<p style="color:var(--muted);font-size:0.84rem">Configure columns on the left.</p>'}
        </div>
        <div class="card">
            <div class="card-title">💡 Threshold Guide</div>
            <p style="font-size:0.82rem;color:#475569;line-height:2;margin:0">
                <b style="color:#16a34a">90–100%</b> → Very high precision<br>
                <b style="color:#2563eb">80–89%</b> → Recommended<br>
                <b style="color:#d97706">65–79%</b> → Broad search<br>
                <b style="color:#dc2626">50–64%</b> → Many results
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — RESULTS + CLUSTERS
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    df1 = st.session_state.get("df1")
    df2 = st.session_state.get("df2")
    col_configs = st.session_state.get("col_configs", [])
    col_configs2 = st.session_state.get("col_configs2", None)
    name_col1 = st.session_state.get("name_col1")
    mode = st.session_state.mode

    if df1 is None or not col_configs:
        st.warning("Please go back and configure matching first.")
        if st.button("← Back"): st.session_state.step = 1; st.rerun()
        st.stop()

    if st.session_state.results_df is None:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⏳ Running Matching Engine...")
        prog = st.progress(0)
        status = st.empty()
        status.text("🔄 Preparing data...")
        time.sleep(0.3)
        try:
            status.text("🔍 Finding matches across columns...")
            results = match_columns(df1, col_configs, df2, col_configs2, mode, prog)
            st.session_state.results_df = results
            status.text("🧩 Building clusters...")
            st.session_state.clusters = build_clusters(results)
            status.text("✅ Complete!")
            time.sleep(0.4)
        except Exception as e:
            st.error(f"❌ Error: {e}"); st.stop()
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()

    results  = st.session_state.results_df
    clusters = st.session_state.clusters or []
    total_matches = len(results)
    exact_matches = int((results["Status"] == "Exact Match").sum()) if total_matches else 0
    similar_matches = total_matches - exact_matches
    avg_score = round(results["Avg Score"].mean(), 1) if total_matches else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="val">{total_matches:,}</div><div class="lbl">Total Pairs Found</div></div>
        <div class="metric-card"><div class="val" style="color:#dc2626">{exact_matches:,}</div><div class="lbl">Exact Matches (100%)</div></div>
        <div class="metric-card"><div class="val" style="color:#d97706">{similar_matches:,}</div><div class="lbl">Similar Records</div></div>
        <div class="metric-card"><div class="val">{len(clusters):,}</div><div class="lbl">Clusters</div></div>
    </div>
    """, unsafe_allow_html=True)

    if total_matches == 0:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px">
            <div style="font-size:3rem">🎉</div>
            <h3>No Duplicates Found!</h3>
            <p style="color:#64748b">No matching records found at the configured threshold.</p>
        </div>""", unsafe_allow_html=True)
    else:
        tab_raw, tab_clusters, tab_chart = st.tabs([
            "📋 Match Results", "🧩 Clusters & Group Codes", "📊 Score Distribution"
        ])

        with tab_raw:
            cf1, cf2 = st.columns([1, 2])
            with cf1: filt = st.selectbox("Filter:", ["All", "Exact Match", "Similar"])
            with cf2: search = st.text_input("🔍 Search:", placeholder="Type a name...")
            disp = results.copy()
            if filt != "All": disp = disp[disp["Status"] == filt]
            if search: disp = disp[disp.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)]
            st.dataframe(disp, use_container_width=True, height=400)
            st.caption(f"Showing {len(disp):,} of {total_matches:,} pairs")

        with tab_clusters:
            st.markdown("""
            <div style="background:var(--blue-pale);border:1px solid var(--blue-border);
                border-radius:10px;padding:12px 16px;margin-bottom:14px;font-size:0.86rem;color:#1e40af">
                Each cluster groups similar records.
                🏅 <b>Golden Record</b> = most complete name.
                Use <code>GRP-001</code> codes in the merge step.
            </div>
            """, unsafe_allow_html=True)
            show_limit = safe_slider("Clusters to display:", len(clusters), key="cl_limit")
            for i, cluster in enumerate(clusters[:show_limit]):
                golden = pick_golden_record(cluster["names"])
                sc_val = cluster["max_score"]
                sc_class = "score-high" if sc_val >= 85 else ("score-medium" if sc_val >= 70 else "score-low")
                rows_html = "".join(f"""
                <div class="name-row {'golden' if n==golden else ''}">
                    {'<span class="golden-badge">🏅 Golden</span>' if n==golden else '<span style="width:62px;display:inline-block"></span>'}
                    <span>{n}</span>
                </div>""" for n in cluster["names"])
                st.markdown(f"""
                <div class="group-card">
                    <div class="group-header">
                        <span class="group-id">GRP-{i+1:03d}</span>
                        <span style="font-size:0.76rem;color:#64748b">{len(cluster['names'])} records</span>
                        <span class="score-pill {sc_class}">{sc_val}%</span>
                    </div>
                    {rows_html}
                </div>""", unsafe_allow_html=True)
            if len(clusters) > show_limit:
                st.caption(f"Showing {show_limit} of {len(clusters)} clusters.")

        with tab_chart:
            bins = [50,60,70,80,90,100]
            labels = ["50–60%","60–70%","70–80%","80–90%","90–100%","100%"]
            scores = results["Avg Score"].tolist()
            hist = [sum(1 for s in scores if bins[i]<=s<bins[i+1]) for i in range(5)]
            hist.append(sum(1 for s in scores if s==100))
            cd = json.dumps([{"l":labels[i],"c":hist[i]} for i in range(6)])
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📊 Similarity Score Distribution</div>
                <div id="mdm-chart" style="display:flex;align-items:flex-end;gap:14px;height:200px;padding:16px 0"></div>
                <div style="font-size:0.74rem;color:#64748b;margin-top:4px">Average score: <b>{avg_score}%</b></div>
            </div>
            <script>(function(){{
                const d={cd};const mx=Math.max(...d.map(x=>x.c),1);
                const el=document.getElementById('mdm-chart');if(!el)return;
                const cs=['#1d4ed8','#2563eb','#3b82f6','#60a5fa','#16a34a','#dc2626'];
                d.forEach((item,i)=>{{
                    const div=document.createElement('div');
                    div.style.cssText='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px';
                    const h=Math.round((item.c/mx)*160);
                    div.innerHTML=`<span style="font-size:0.8rem;font-weight:700;color:${{cs[i]}}">${{item.c}}</span>
                        <div style="width:100%;height:${{h}}px;background:${{cs[i]}};border-radius:6px 6px 0 0;min-height:4px"></div>
                        <span style="font-size:0.72rem;color:#64748b">${{item.l}}</span>`;
                    el.appendChild(div);
                }});
            }})();</script>
            """, unsafe_allow_html=True)

        # Downloads
        st.markdown("<br>", unsafe_allow_html=True)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            results.to_excel(writer, sheet_name='Match Results', index=False)
            cl_rows = []
            for i, cl in enumerate(clusters):
                g = pick_golden_record(cl["names"])
                for name in cl["names"]:
                    cl_rows.append({
                        "Group Code": f"GRP-{i+1:03d}",
                        "Record": name,
                        "Golden Record": g,
                        "Is Golden": "Yes" if name == g else "No",
                        "Max Similarity": cl["max_score"]
                    })
            pd.DataFrame(cl_rows).to_excel(writer, sheet_name='Clusters & Group Codes', index=False)
            pd.DataFrame({
                "Metric": ["Total Pairs","Exact Matches","Similar Records","Clusters","Avg Score"],
                "Value": [total_matches, exact_matches, similar_matches, len(clusters), f"{avg_score}%"]
            }).to_excel(writer, sheet_name='Summary', index=False)
        out.seek(0)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("⬇️ Download Results (Excel)", data=out,
                                file_name="golden_records_results.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True)
        with d2:
            csv_data = results.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("⬇️ Download Results (CSV)",
                                data=csv_data.encode("utf-8-sig"),
                                file_name="golden_records_results.csv",
                                mime="text/csv", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("← Edit Settings", use_container_width=True):
            st.session_state.results_df = None
            st.session_state.clusters = None
            st.session_state.step = 2; st.rerun()
    with nav2:
        if total_matches > 0:
            if st.button("🏅 Golden Record Merge →", use_container_width=True):
                st.session_state.step = 4; st.rerun()
    with nav3:
        if st.button("🤖 AI Analysis →", use_container_width=True):
            st.session_state.step = 5; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — GOLDEN RECORD MERGE
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    df1       = st.session_state.get("df1")
    clusters  = st.session_state.get("clusters", [])
    name_col1 = st.session_state.get("name_col1")

    if df1 is None or not clusters:
        st.warning("Please go back and run matching first.")
        if st.button("← Back"): st.session_state.step = 3; st.rerun()
        st.stop()

    st.markdown("""
    <div style="background:var(--gold-light);border:1.5px solid var(--gold-border);
        border-radius:14px;padding:16px 22px;margin-bottom:18px">
        <h3 style="margin:0 0 6px 0;color:#92400e">🏅 Golden Record Merge</h3>
        <p style="margin:0;color:#78350f;font-size:0.88rem">
            Review and optionally override the suggested golden records, then click
            <b>Apply Merge</b> to export your clean, unified dataset.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "golden_overrides" not in st.session_state:
        st.session_state["golden_overrides"] = {}

    show_n = safe_slider("Clusters to review:", len(clusters), key="merge_limit")
    golden_overrides = st.session_state.get("golden_overrides", {})

    for i, cluster in enumerate(clusters[:show_n]):
        auto_golden = pick_golden_record(cluster["names"])
        ok  = f"golden_{i}"
        cur = golden_overrides.get(ok, auto_golden)
        sc_val = cluster["max_score"]
        sc_class = "score-high" if sc_val >= 85 else ("score-medium" if sc_val >= 70 else "score-low")

        with st.expander(f"GRP-{i+1:03d}  ·  {len(cluster['names'])} records  ·  {sc_val}% similarity", expanded=(i<5)):
            c_names, c_golden = st.columns([1,1], gap="large")
            with c_names:
                st.markdown("**Records in this cluster:**")
                for name in cluster["names"]:
                    is_g = name == cur
                    st.markdown(f"""
                    <div style="padding:7px 12px;border-radius:8px;margin-bottom:5px;
                        background:{'#fef3c7' if is_g else '#f8faff'};
                        border:1px solid {'#fde68a' if is_g else '#dbeafe'};
                        font-size:0.86rem;font-weight:{'700' if is_g else '400'}">
                        {'🏅 ' if is_g else '• '}{name}
                    </div>""", unsafe_allow_html=True)

            with c_golden:
                st.markdown("**Choose Golden Record:**")
                chosen = st.selectbox("",
                    options=cluster["names"],
                    index=cluster["names"].index(cur) if cur in cluster["names"] else 0,
                    key=f"sel_{i}", label_visibility="collapsed")
                st.session_state.golden_overrides[ok] = chosen
                st.markdown(f"""
                <div style="margin-top:12px;background:#fef3c7;border:1px solid #fde68a;
                    border-radius:10px;padding:10px 14px;text-align:center">
                    <div style="font-size:0.7rem;color:#92400e;font-weight:700;margin-bottom:4px">🏅 GOLDEN RECORD</div>
                    <div style="font-size:1rem;font-weight:900;color:#78350f">{chosen}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:var(--blue-pale);border:1px solid var(--blue-border);
        border-radius:10px;padding:12px 16px;margin-bottom:14px;font-size:0.86rem;color:#1e40af">
        After clicking <b>Apply Merge</b>, all records in each cluster will be replaced by the selected
        golden record in a clean Excel file ready for download.
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ Apply Merge & Export Clean File", use_container_width=True):
        merged = df1.copy()
        for i, cluster in enumerate(clusters):
            golden = st.session_state.golden_overrides.get(f"golden_{i}", pick_golden_record(cluster["names"]))
            for name in cluster["names"]:
                if name != golden:
                    merged.loc[merged[name_col1] == name, name_col1] = golden
        st.session_state.merged_df = merged
        original_unique = df1[name_col1].nunique()
        merged_unique = merged[name_col1].nunique()
        st.success(f"✅ Merge complete! — {len(merged):,} records")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0">
            <div class="metric-card"><div class="val">{original_unique:,}</div><div class="lbl">Unique Values Before</div></div>
            <div class="metric-card"><div class="val" style="color:#16a34a">{merged_unique:,}</div><div class="lbl">Unique Values After</div></div>
            <div class="metric-card"><div class="val" style="color:#2563eb">{original_unique-merged_unique:,}</div><div class="lbl">Records Unified</div></div>
        </div>""", unsafe_allow_html=True)
        st.dataframe(merged.head(10), use_container_width=True)

    if st.session_state.get("merged_df") is not None:
        merged = st.session_state.merged_df
        out_m = io.BytesIO()
        with pd.ExcelWriter(out_m, engine='openpyxl') as writer:
            merged.to_excel(writer, sheet_name='Clean Data', index=False)
            cl_rows = []
            for i, cl in enumerate(clusters):
                g = st.session_state.golden_overrides.get(f"golden_{i}", pick_golden_record(cl["names"]))
                for name in cl["names"]:
                    cl_rows.append({
                        "Group Code": f"GRP-{i+1:03d}",
                        "Original Record": name,
                        "Golden Record": g
                    })
            pd.DataFrame(cl_rows).to_excel(writer, sheet_name='Merge Map', index=False)
        out_m.seek(0)
        st.download_button("⬇️ Download Clean File (Excel)", data=out_m,
                            file_name="golden_records_clean.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("← Back to Results", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with b2:
        if st.button("🤖 AI Analysis →", use_container_width=True):
            st.session_state.step = 5; st.rerun()
    with b3:
        if st.button("🔄 New Analysis", use_container_width=True):
            for k in ["results_df","clusters","df1","df2","merged_df","golden_overrides","col_configs","col_configs2"]:
                st.session_state[k] = None
            st.session_state.step = 1; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — AI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif step == 5:
    df1 = st.session_state.get("df1")
    results = st.session_state.get("results_df")
    clusters = st.session_state.get("clusters", [])

    if df1 is None:
        st.warning("Please upload data first.")
        if st.button("← Back to Upload"): st.session_state.step = 1; st.rerun()
        st.stop()

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e1b4b,#4f46e5);
        border-radius:16px;padding:22px 28px;margin-bottom:20px;color:white">
        <h3 style="margin:0 0 8px 0;font-size:1.4rem">🤖 AI Data Intelligence</h3>
        <p style="margin:0;opacity:0.85;font-size:0.9rem">
            Claude AI analyzes your data, match results, and clusters to provide
            expert data quality insights, anomaly detection, and actionable recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Summary panel
    if results is not None and len(results) > 0:
        total_matches = len(results)
        exact_matches = int((results["Status"] == "Exact Match").sum())
        avg_score = round(results["Avg Score"].mean(), 1)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px">
            <div class="metric-card"><div class="val">{len(df1):,}</div><div class="lbl">Total Records</div></div>
            <div class="metric-card"><div class="val" style="color:#dc2626">{total_matches:,}</div><div class="lbl">Matches Found</div></div>
            <div class="metric-card"><div class="val" style="color:#d97706">{len(clusters):,}</div><div class="lbl">Clusters</div></div>
            <div class="metric-card"><div class="val">{avg_score}%</div><div class="lbl">Avg Similarity</div></div>
        </div>""", unsafe_allow_html=True)

    tab_data, tab_matches = st.tabs(["📊 Data Quality Analysis", "🔍 Match & Cluster Analysis"])

    with tab_data:
        render_ai_analysis(df1, context="main dataset")

    with tab_matches:
        if results is not None and len(results) > 0:
            # AI analysis of matching results
            st.markdown("""
            <div style="background:linear-gradient(135deg,var(--teal-pale),#ecfdf5);
                border:1.5px solid #99f6e4;border-radius:14px;padding:14px 18px;margin-bottom:14px">
                <h4 style="margin:0 0 4px 0;color:#0f766e">🔍 Match Results AI Analysis</h4>
                <p style="margin:0;color:#0d9488;font-size:0.84rem">AI interpretation of your deduplication results.</p>
            </div>
            """, unsafe_allow_html=True)

            match_chat_key = "match_ai_chat"
            if match_chat_key not in st.session_state:
                st.session_state[match_chat_key] = []

            profiles_match = profile_dataframe(df1)
            match_summary = f"""Matching results: {len(results)} pairs found.
Exact matches (100%): {exact_matches}.
Similar matches: {len(results) - exact_matches}.
Number of clusters: {len(clusters)}.
Average similarity score: {avg_score}%.
Largest cluster size: {max((len(c['names']) for c in clusters), default=0)} records.
Score distribution: {dict(results['Avg Score'].value_counts().head(5).items())}
Sample cluster (first 3): {[{'code': f'GRP-{i+1:03d}', 'size': len(c['names']), 'score': c['max_score']} for i, c in enumerate(clusters[:3])]}"""

            # Quick prompts for match analysis
            st.markdown("**💡 Quick Match Analysis Prompts:**")
            qp_cols2 = st.columns(2)
            match_prompts = [
                "Summarize the duplicate/similarity findings",
                "How severe is the data duplication problem?",
                "What do these clusters tell us about data entry patterns?",
                "What's the business impact of these duplicates?"
            ]
            for i, qp in enumerate(match_prompts):
                with qp_cols2[i % 2]:
                    if st.button(f"💬 {qp}", key=f"mqp_{i}"):
                        st.session_state[match_chat_key].append({"role": "user", "content": qp})
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            for msg in st.session_state[match_chat_key]:
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-message">{msg["content"]}</div>', unsafe_allow_html=True)

            if st.session_state[match_chat_key] and st.session_state[match_chat_key][-1]["role"] == "user":
                user_q = st.session_state[match_chat_key][-1]["content"]
                with st.spinner("🤖 Analyzing match results..."):
                    try:
                        import requests
                        msg_payload = [{"role": m["role"], "content": m["content"]}
                                       for m in st.session_state[match_chat_key]]
                        response = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers={"Content-Type": "application/json"},
                            json={
                                "model": "claude-sonnet-4-20250514",
                                "max_tokens": 1000,
                                "system": f"""You are an expert MDM (Master Data Management) consultant.
Analyze the deduplication/matching results and provide clear, actionable insights.
Be specific with numbers and percentages. Max 300 words.

Matching context:
{match_summary}""",
                                "messages": msg_payload
                            }
                        )
                        data = response.json()
                        ai_text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
                        st.session_state[match_chat_key].append({"role": "assistant", "content": ai_text or "Unable to generate analysis."})
                        st.rerun()
                    except Exception as e:
                        st.session_state[match_chat_key].append({"role": "assistant", "content": f"⚠️ Error: {str(e)[:100]}"})
                        st.rerun()

            user_input2 = st.text_input("💬 Ask about match results...", key="match_ai_input",
                                         placeholder="e.g., What's causing these duplicates?")
            mc1, mc2 = st.columns([3, 1])
            with mc2:
                if st.button("Send →", key="match_ai_send"):
                    if user_input2.strip():
                        st.session_state[match_chat_key].append({"role": "user", "content": user_input2.strip()})
                        st.rerun()
            with mc1:
                if st.button("🗑️ Clear", key="match_ai_clear"):
                    st.session_state[match_chat_key] = []
                    st.rerun()
        else:
            st.info("Run matching first (Step 2–3) to get AI analysis of match results.")

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Results", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with b2:
        if st.button("🔄 New Analysis", use_container_width=True):
            for k in ["results_df","clusters","df1","df2","merged_df","golden_overrides","col_configs"]:
                st.session_state[k] = None
            st.session_state.step = 1; st.rerun()
