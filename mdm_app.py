import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
import io
import time
import re
import json
from collections import defaultdict

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

/* ── Steward review ── */
.review-card {
    background:#fff;border:2px solid #fde68a;
    border-radius:12px;padding:16px 20px;margin-bottom:14px;
}
.review-card.approved { border-color:#bbf7d0;background:#f0fdf4; }
.review-card.rejected { border-color:#fecaca;background:#fff5f5; }
.source-badge {
    display:inline-block;padding:2px 10px;border-radius:20px;
    font-size:0.7rem;font-weight:700;margin-right:6px;
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

def normalize_arabic(text):
    if not isinstance(text, str): return ""
    text = text.strip()
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[يى]', 'ي', text)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def read_file(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded)
    elif name.endswith((".xls", ".xlsx")):
        return pd.read_excel(uploaded)
    elif name.endswith(".json"):
        return pd.read_json(uploaded)
    else:
        return None


def compare_pair(row_a_parts, row_b_parts, col_configs):
    """Return (scores, passed) for a pair of rows across all columns in a rule."""
    scores = []
    for c_idx, cfg in enumerate(col_configs):
        a, b = row_a_parts[c_idx], row_b_parts[c_idx]
        if cfg["match_type"] == "exact":
            sc = 100 if a == b else 0
        else:
            sc = fuzz.token_sort_ratio(a, b)
        scores.append(sc)
    passed = all(scores[c_idx] >= cfg["threshold"] for c_idx, cfg in enumerate(col_configs))
    return scores, passed


def run_matching(files_dfs, rules, progress_bar=None):
    """
    files_dfs: list of (label, df)
    rules: list of {name, cols_per_file: [{file_idx, col, match_type, threshold}], logic:"AND"}
    Returns list of match records.
    """
    results = []
    total_steps = 0
    pairs = []

    # Build all file-pair combos (within same file and across files)
    for i in range(len(files_dfs)):
        for j in range(i, len(files_dfs)):
            pairs.append((i, j))
    total_steps = sum(
        len(files_dfs[i][1]) * (len(files_dfs[j][1]) if i != j else len(files_dfs[j][1]))
        for i, j in pairs
    ) or 1

    done = 0
    for rule in rules:
        rule_results = []
        for fi, fj in pairs:
            label_i, df_i = files_dfs[fi]
            label_j, df_j = files_dfs[fj]

            # Gather col configs for each file in this rule
            cfgs_i = [c for c in rule["columns"] if c["file_idx"] == fi]
            cfgs_j = [c for c in rule["columns"] if c["file_idx"] == fj]
            if not cfgs_i or not cfgs_j:
                continue  # rule doesn't cover this file pair

            keys_i = []
            for row_idx in range(len(df_i)):
                parts = []
                for cfg in cfgs_i:
                    val = str(df_i[cfg["col"]].iloc[row_idx]) if cfg["col"] in df_i.columns else ""
                    parts.append(normalize_arabic(val))
                keys_i.append(parts)

            keys_j = []
            for row_idx in range(len(df_j)):
                parts = []
                for cfg in cfgs_j:
                    val = str(df_j[cfg["col"]].iloc[row_idx]) if cfg["col"] in df_j.columns else ""
                    parts.append(normalize_arabic(val))
                keys_j.append(parts)

            range_j_start = 0
            same_file = (fi == fj)

            for i_idx in range(len(df_i)):
                if progress_bar and done % 200 == 0:
                    progress_bar.progress(min(done / total_steps, 0.99))
                done += 1
                if not any(keys_i[i_idx]): continue
                j_start = i_idx + 1 if same_file else 0
                for j_idx in range(j_start, len(df_j)):
                    if not any(keys_j[j_idx]): continue
                    # Build unified col configs for comparison
                    scores = []
                    passed_all = True
                    for k, (cfg_i, cfg_j) in enumerate(zip(cfgs_i, cfgs_j)):
                        a = keys_i[i_idx][k]
                        b = keys_j[j_idx][k]
                        if cfg_i["match_type"] == "exact":
                            sc = 100 if a == b else 0
                        else:
                            sc = fuzz.token_sort_ratio(a, b)
                        scores.append(sc)
                        if sc < cfg_i["threshold"]:
                            passed_all = False
                            break
                    if not passed_all:
                        continue
                    avg_sc = round(sum(scores) / len(scores))
                    rec = {
                        "Rule": rule["name"],
                        "File A": label_i,
                        "Row A": i_idx + 2,
                        "File B": label_j,
                        "Row B": j_idx + 2,
                        "Avg Score": avg_sc,
                        "Status": "Exact Match" if avg_sc == 100 else "Similar",
                        "_row_i": i_idx,
                        "_row_j": j_idx,
                        "_fi": fi,
                        "_fj": fj,
                    }
                    for k, cfg_i in enumerate(cfgs_i):
                        rec[f"A: {cfg_i['col']}"] = str(df_i[cfg_i["col"]].iloc[i_idx]) if cfg_i["col"] in df_i.columns else ""
                    for k, cfg_j in enumerate(cfgs_j):
                        rec[f"B: {cfg_j['col']}"] = str(df_j[cfg_j["col"]].iloc[j_idx]) if cfg_j["col"] in df_j.columns else ""
                    rule_results.append(rec)
        results.extend(rule_results)

    if progress_bar: progress_bar.progress(1.0)
    return pd.DataFrame(results) if results else pd.DataFrame()


def build_clusters(results_df, files_dfs):
    """Build union-find clusters from match pairs. Each node = (file_idx, row_idx)."""
    if results_df is None or len(results_df) == 0:
        return []
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        if parent[x] != x: parent[x] = find(parent[x])
        return parent[x]
    def union(x, y): parent[find(x)] = find(y)

    scores_map = {}
    for _, row in results_df.iterrows():
        a = (int(row["_fi"]), int(row["_row_i"]))
        b = (int(row["_fj"]), int(row["_row_j"]))
        union(a, b)
        key = tuple(sorted([a, b]))
        scores_map[key] = max(scores_map.get(key, 0), int(row["Avg Score"]))

    groups = defaultdict(set)
    for node in parent:
        groups[find(node)].add(node)

    clusters = []
    for _, members in groups.items():
        members = sorted(members)
        max_sc = 0
        for ii, a in enumerate(members):
            for b in members[ii+1:]:
                key = tuple(sorted([a, b]))
                max_sc = max(max_sc, scores_map.get(key, 0))

        # Build display rows for the cluster
        records = []
        for fi, ri in members:
            label, df = files_dfs[fi]
            row_data = df.iloc[ri].to_dict() if ri < len(df) else {}
            records.append({
                "source_label": label,
                "file_idx": fi,
                "row_idx": ri,
                "data": row_data
            })
        clusters.append({"members": members, "max_score": max_sc, "records": records})
    clusters.sort(key=lambda x: -x["max_score"])
    return clusters


def pick_golden_auto(records, trust_scores):
    """Pick golden record based on column trust scores per source."""
    # trust_scores: {col: {source_label: score}}
    if not records:
        return records[0]["data"] if records else {}

    all_cols = set()
    for r in records: all_cols.update(r["data"].keys())

    golden = {}
    for col in all_cols:
        best_val = None
        best_trust = -1
        for r in records:
            val = r["data"].get(col, "")
            src = r["source_label"]
            trust = trust_scores.get(col, {}).get(src, 50)
            # Prefer non-empty values
            if str(val).strip() in ("", "nan", "None"):
                trust = trust - 200  # heavy penalty for empty
            if trust > best_trust:
                best_trust = trust
                best_val = val
        golden[col] = best_val
    return golden


def mini_bar(value, color="#2563eb", width=100):
    pct = min(value, 100)
    return (f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="width:{width}px;height:8px;background:#e2e8f0;border-radius:5px;overflow:hidden">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:5px"></div></div>'
            f'<span style="font-size:0.76rem;font-weight:700;color:{color}">{value:.1f}%</span></div>')


def source_badge(label, palette=None):
    colors = ["#2563eb","#7c3aed","#0d9488","#d97706","#dc2626","#16a34a"]
    idx = hash(label) % len(colors)
    c = colors[idx]
    return f'<span class="source-badge" style="background:{c}20;color:{c};border:1px solid {c}40">{label}</span>'


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
defaults = {
    "step": 1,
    "files_dfs": [],          # list of (label, df)
    "rules": [],              # list of rule configs
    "results_df": None,
    "clusters": None,
    "merge_mode": "auto",
    "trust_scores": {},       # {col: {source_label: int 0-100}}
    "golden_records": {},     # {cluster_idx: {col: val}}
    "steward_decisions": {},  # {cluster_idx: "approve"|"reject"|"pending"}
    "steward_overrides": {},  # {cluster_idx: {col: val}}
    "final_df": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
total_records = sum(len(df) for _, df in st.session_state.files_dfs)

st.markdown(f"""
<div class="hero">
    <div class="hero-icon">🏅</div>
    <div class="hero-text">
        <h1>Golden Data MDM</h1>
        <p class="sub">Master Data Management · Multi-File Deduplication · Golden Record Engine</p>
        <p class="tagline">✦ Let's Master your Data ✦</p>
    </div>
    {"" if total_records == 0 else f'<div class="hero-badge"><span class="hb-val">{total_records:,}</span>Records Loaded</div>'}
</div>
""", unsafe_allow_html=True)

step = st.session_state.step

def sc(n): return "done" if n < step else ("active" if n == step else "pending")
def cc(n): return "done" if n < step else ""

STEPS = ["Upload Files", "Match Rules", "Run Matching", "Merge Config", "Steward Review", "Export"]

st.markdown(f"""
<div class="stepper">
    {''.join(
        f'<div class="step"><div class="step-circle {sc(i+1)}">{"✓" if step > i+1 else i+1}</div>'
        f'<span class="step-label {"active" if step == i+1 else "pending"}">{s}</span></div>'
        + (f'<div class="step-connector {cc(i+1)}"></div>' if i < len(STEPS)-1 else '')
        for i, s in enumerate(STEPS)
    )}
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — UPLOAD MULTIPLE FILES
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    col_main, col_side = st.columns([2, 1], gap="large")

    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📂 Upload Data Sources</div>', unsafe_allow_html=True)
        st.info("Upload 1 or more files (CSV, Excel, JSON). Each file becomes a named data source.")

        num_files = st.number_input("How many files to upload?", min_value=1, max_value=10, value=2, step=1)

        new_files = []
        for i in range(int(num_files)):
            st.markdown(f"**Source {i+1}:**")
            c1, c2 = st.columns([2, 1])
            with c1:
                uploaded = st.file_uploader(f"File {i+1}", type=["csv","xlsx","xls","json"], key=f"up_{i}")
            with c2:
                default_label = f"Source_{i+1}"
                label = st.text_input(f"Label:", value=default_label, key=f"lbl_{i}")
            if uploaded is not None:
                df = read_file(uploaded)
                if df is not None:
                    new_files.append((label, df))
                    st.success(f"✅ {label}: {len(df):,} rows, {len(df.columns)} columns")
                else:
                    st.error(f"Could not read file {i+1}")
            st.markdown("<hr style='border-color:#e2e8f0;margin:6px 0'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Continue to Match Rules →", use_container_width=True):
            if not new_files:
                st.error("Please upload at least one file.")
            else:
                st.session_state.files_dfs = new_files
                st.session_state.rules = []
                st.session_state.results_df = None
                st.session_state.clusters = None
                st.session_state.golden_records = {}
                st.session_state.steward_decisions = {}
                st.session_state.final_df = None
                st.session_state.step = 2
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-title">📋 What is MDM?</div>
            <p style="font-size:0.84rem;color:#475569;line-height:2;margin:0">
                <b>Master Data Management</b> helps you:<br>
                🔗 Integrate data from multiple sources<br>
                🔍 Match records using configurable rules<br>
                🏅 Create golden (authoritative) records<br>
                👤 Review merges as a Data Steward<br>
                ⬇️ Export clean, unified master data
            </p>
        </div>
        <div class="card">
            <div class="card-title">📁 Supported Formats</div>
            <p style="font-size:0.84rem;color:#475569;line-height:2;margin:0">
                CSV · Excel (.xlsx / .xls) · JSON
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — CONFIGURE MATCHING RULES
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    files_dfs = st.session_state.files_dfs
    if not files_dfs:
        st.warning("Please upload files first.")
        if st.button("← Back"): st.session_state.step = 1; st.rerun()
        st.stop()

    file_labels = [lbl for lbl, _ in files_dfs]
    all_cols_by_file = {lbl: list(df.columns) for lbl, df in files_dfs}

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Matching Rules</div>', unsafe_allow_html=True)
    st.info("Define one or more matching rules. Each rule can match on multiple columns across your files. A cluster forms when ANY rule fires.")

    num_rules = st.number_input("Number of matching rules:", min_value=1, max_value=8, value=max(1, len(st.session_state.rules)), step=1)

    rules = []
    for r_idx in range(int(num_rules)):
        with st.expander(f"📌 Rule {r_idx+1}", expanded=(r_idx == 0)):
            rule_name = st.text_input("Rule name:", value=f"Rule_{r_idx+1}", key=f"rname_{r_idx}")

            st.markdown("**How many columns does this rule match on?**")
            num_cols_in_rule = st.number_input("Columns per rule:", min_value=1, max_value=6, value=1, step=1, key=f"nrc_{r_idx}")

            rule_cols = []
            for c_idx in range(int(num_cols_in_rule)):
                st.markdown(f"*Column {c_idx+1} — one entry per file:*")
                col_entries = []
                for f_idx, (lbl, df) in enumerate(files_dfs):
                    cx1, cx2, cx3, cx4 = st.columns([1.5, 2, 1.2, 1])
                    with cx1:
                        st.markdown(f"<span style='font-size:0.8rem;font-weight:700'>{source_badge(lbl)}</span>", unsafe_allow_html=True)
                    with cx2:
                        cols_for_file = list(df.columns)
                        sel = st.selectbox("Column:", cols_for_file, key=f"rcol_{r_idx}_{c_idx}_{f_idx}")
                    with cx3:
                        mtype = st.selectbox("Method:", ["Fuzzy","Exact"], key=f"rmt_{r_idx}_{c_idx}_{f_idx}")
                    with cx4:
                        if mtype == "Fuzzy":
                            thr = st.slider("Threshold:", 50, 100, 80, 5, key=f"rthr_{r_idx}_{c_idx}_{f_idx}")
                        else:
                            thr = 100
                            st.markdown("<br><span style='color:#16a34a;font-weight:700;font-size:0.82rem'>100%</span>", unsafe_allow_html=True)
                    col_entries.append({
                        "file_idx": f_idx,
                        "col": sel,
                        "match_type": mtype.lower(),
                        "threshold": thr,
                    })
                rule_cols.extend(col_entries)
                if c_idx < int(num_cols_in_rule) - 1:
                    st.markdown("<hr style='border-color:#e2e8f0;margin:4px 0'>", unsafe_allow_html=True)

            rules.append({"name": rule_name, "columns": rule_cols})

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1; st.rerun()
    with b2:
        if st.button("🚀 Run Matching →", use_container_width=True):
            st.session_state.rules = rules
            st.session_state.results_df = None
            st.session_state.clusters = None
            st.session_state.step = 3
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — RUN MATCHING + SHOW RESULTS
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    files_dfs = st.session_state.files_dfs
    rules = st.session_state.rules

    if not files_dfs or not rules:
        st.warning("Please go back and configure files and rules.")
        if st.button("← Back"): st.session_state.step = 2; st.rerun()
        st.stop()

    if st.session_state.results_df is None:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⏳ Running Matching Engine...")
        prog = st.progress(0)
        status = st.empty()
        status.text("🔄 Preparing data...")
        time.sleep(0.2)
        try:
            status.text("🔍 Matching across rules and files...")
            results = run_matching(files_dfs, rules, prog)
            st.session_state.results_df = results
            status.text("🧩 Building clusters...")
            st.session_state.clusters = build_clusters(results, files_dfs)
            status.text("✅ Complete!")
            time.sleep(0.3)
        except Exception as e:
            st.error(f"❌ Error: {e}"); st.stop()
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()

    results = st.session_state.results_df
    clusters = st.session_state.clusters or []
    total_matches = len(results)
    exact_matches = int((results["Status"] == "Exact Match").sum()) if total_matches else 0
    similar_matches = total_matches - exact_matches
    avg_score = round(results["Avg Score"].mean(), 1) if total_matches else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="val">{total_matches:,}</div><div class="lbl">Total Pairs Found</div></div>
        <div class="metric-card"><div class="val" style="color:#dc2626">{exact_matches:,}</div><div class="lbl">Exact Matches</div></div>
        <div class="metric-card"><div class="val" style="color:#d97706">{similar_matches:,}</div><div class="lbl">Similar Records</div></div>
        <div class="metric-card"><div class="val">{len(clusters):,}</div><div class="lbl">Clusters</div></div>
    </div>
    """, unsafe_allow_html=True)

    tab_pairs, tab_clusters = st.tabs(["🔗 Matched Pairs", "🧩 Clusters"])

    with tab_pairs:
        if total_matches > 0:
            display_cols = [c for c in results.columns if not c.startswith("_")]
            st.dataframe(results[display_cols].head(200), use_container_width=True)
        else:
            st.info("No matches found. Try lowering thresholds or adjusting rules.")

    with tab_clusters:
        if clusters:
            for i, cl in enumerate(clusters[:30]):
                sc_class = "score-high" if cl["max_score"] >= 90 else "score-medium" if cl["max_score"] >= 70 else "score-low"
                st.markdown(f"""
                <div class="group-card">
                    <div class="group-header">
                        <span class="group-id">GRP-{i+1:03d}</span>
                        <span style="font-size:0.82rem;color:var(--muted)">{len(cl["records"])} records</span>
                        <span class="score-pill {sc_class}">{cl["max_score"]}%</span>
                    </div>
                """, unsafe_allow_html=True)
                for rec in cl["records"]:
                    first_col_val = list(rec["data"].values())[0] if rec["data"] else "—"
                    st.markdown(f"""
                    <div class="name-row">
                        {source_badge(rec["source_label"])}
                        <span>Row {rec["row_idx"]+2}: <b>{first_col_val}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No clusters to display.")

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Rules", use_container_width=True):
            st.session_state.step = 2; st.rerun()
    with b2:
        if st.button("▶ Configure Merge →", use_container_width=True):
            st.session_state.step = 4; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — MERGE CONFIGURATION (Auto vs Manual + Trust Scores)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    files_dfs = st.session_state.files_dfs
    clusters = st.session_state.clusters or []

    if not files_dfs or not clusters:
        st.warning("Please run matching first.")
        if st.button("← Back"): st.session_state.step = 3; st.rerun()
        st.stop()

    file_labels = [lbl for lbl, _ in files_dfs]

    # Collect all columns across all files
    all_cols = []
    seen = set()
    for _, df in files_dfs:
        for c in df.columns:
            if c not in seen:
                all_cols.append(c)
                seen.add(c)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔀 Merge Configuration</div>', unsafe_allow_html=True)

    merge_mode = st.radio(
        "**Merge Mode:**",
        ["🤖 Auto Merge (trust score determines golden record)", "👤 Manual Merge (data steward reviews each cluster)"],
        horizontal=False, key="merge_mode_radio"
    )
    is_auto = "Auto" in merge_mode
    st.session_state.merge_mode = "auto" if is_auto else "manual"

    st.markdown("<br>", unsafe_allow_html=True)

    if is_auto:
        st.markdown("""
        <div style="background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:12px;padding:14px 18px;margin-bottom:16px">
            <b style="color:#15803d">🤖 Auto Merge</b>: For each column, assign a trust score (0–100) per source file.
            The source with the highest trust score for that column contributes the value to the golden record.
            Empty values are penalized automatically.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🎯 Column Trust Scores per Source")

        trust_scores = {}
        for col in all_cols:
            st.markdown(f"**`{col}`**")
            col_trust = {}
            tcols = st.columns(len(file_labels))
            for f_idx, lbl in enumerate(file_labels):
                with tcols[f_idx]:
                    ts = st.slider(f"{lbl}:", 0, 100, 70, 5, key=f"ts_{col}_{f_idx}")
                    col_trust[lbl] = ts
            trust_scores[col] = col_trust
            st.markdown("<hr style='border-color:#e2e8f0;margin:4px 0'>", unsafe_allow_html=True)

        st.session_state.trust_scores = trust_scores

    else:
        st.markdown("""
        <div style="background:#fef3c7;border:1.5px solid #fde68a;border-radius:12px;padding:14px 18px;margin-bottom:16px">
            <b style="color:#92400e">👤 Manual Merge</b>: In the next step, a Data Steward will review each cluster,
            compare candidate records, select or override the golden record field by field, then approve or reject the merge.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Results", use_container_width=True):
            st.session_state.step = 3; st.rerun()
    with b2:
        btn_label = "⚡ Auto-Generate Golden Records →" if is_auto else "👤 Go to Steward Review →"
        if st.button(btn_label, use_container_width=True):
            if is_auto:
                # Generate all golden records automatically
                golden_records = {}
                for i, cl in enumerate(clusters):
                    golden_records[i] = pick_golden_auto(cl["records"], st.session_state.trust_scores)
                st.session_state.golden_records = golden_records
                st.session_state.step = 6  # Skip steward review
            else:
                # Initialize steward decisions
                st.session_state.steward_decisions = {i: "pending" for i in range(len(clusters))}
                st.session_state.steward_overrides = {}
                st.session_state.step = 5
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — STEWARD REVIEW (Manual Merge)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 5:
    clusters = st.session_state.clusters or []
    decisions = st.session_state.steward_decisions
    overrides = st.session_state.steward_overrides

    if not clusters:
        st.warning("No clusters to review.")
        if st.button("← Back"): st.session_state.step = 4; st.rerun()
        st.stop()

    all_cols = []
    seen = set()
    for _, df in st.session_state.files_dfs:
        for c in df.columns:
            if c not in seen:
                all_cols.append(c)
                seen.add(c)

    approved = sum(1 for v in decisions.values() if v == "approve")
    rejected = sum(1 for v in decisions.values() if v == "reject")
    pending = sum(1 for v in decisions.values() if v == "pending")

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="val">{len(clusters)}</div><div class="lbl">Total Clusters</div></div>
        <div class="metric-card"><div class="val" style="color:#16a34a">{approved}</div><div class="lbl">Approved</div></div>
        <div class="metric-card"><div class="val" style="color:#dc2626">{rejected}</div><div class="lbl">Rejected</div></div>
        <div class="metric-card"><div class="val" style="color:#d97706">{pending}</div><div class="lbl">Pending</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👤 Data Steward Review</div>', unsafe_allow_html=True)
    st.info("Review each cluster. For each column, select which source value should become the golden record — or type a custom value. Then approve or reject the merge.")

    filter_opt = st.radio("Show:", ["All", "Pending only", "Approved", "Rejected"], horizontal=True)

    for i, cl in enumerate(clusters):
        d = decisions.get(i, "pending")
        if filter_opt == "Pending only" and d != "pending": continue
        if filter_opt == "Approved" and d != "approve": continue
        if filter_opt == "Rejected" and d != "reject": continue

        card_class = "review-card approved" if d == "approve" else "review-card rejected" if d == "reject" else "review-card"
        status_icon = "✅" if d == "approve" else "❌" if d == "reject" else "⏳"

        with st.expander(f"{status_icon} Cluster GRP-{i+1:03d} — {len(cl['records'])} records | Score: {cl['max_score']}%", expanded=(d == "pending")):
            # Show all candidate records side by side
            rec_cols = st.columns(len(cl["records"]))
            for r_idx, rec in enumerate(cl["records"]):
                with rec_cols[r_idx]:
                    st.markdown(f"**{source_badge(rec['source_label'])}** Row {rec['row_idx']+2}", unsafe_allow_html=True)
                    for col in all_cols:
                        val = rec["data"].get(col, "")
                        color = "#64748b" if str(val).strip() in ("","nan","None") else "#0f172a"
                        st.markdown(f"<span style='font-size:0.78rem;color:#94a3b8'>{col}:</span> <span style='color:{color};font-size:0.85rem'>{val}</span>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**🏅 Build Golden Record — select value per column:**")

            override_vals = overrides.get(i, {})
            new_override = {}
            for col in all_cols:
                st.markdown(f"*{col}:*")
                options = {}
                for rec in cl["records"]:
                    val = str(rec["data"].get(col, ""))
                    if val.strip() not in ("","nan","None"):
                        options[f"{rec['source_label']} → {val}"] = val
                options["Custom value..."] = "__custom__"

                current_key = list(options.keys())[0] if options else "Custom value..."
                if col in override_vals:
                    for k, v in options.items():
                        if v == override_vals[col]:
                            current_key = k
                            break

                ov1, ov2 = st.columns([3, 1])
                with ov1:
                    sel = st.selectbox("", list(options.keys()), key=f"ov_sel_{i}_{col}", index=list(options.keys()).index(current_key) if current_key in options else 0)
                with ov2:
                    if options.get(sel) == "__custom__":
                        custom = st.text_input("Value:", value=override_vals.get(col, ""), key=f"ov_cust_{i}_{col}")
                        new_override[col] = custom
                    else:
                        new_override[col] = options.get(sel, "")
                        st.markdown(f"<span style='font-size:0.8rem;color:#16a34a;font-weight:700'>✓</span>", unsafe_allow_html=True)

            overrides[i] = new_override

            st.markdown("<br>", unsafe_allow_html=True)
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if st.button(f"✅ Approve GRP-{i+1:03d}", key=f"approve_{i}", use_container_width=True):
                    decisions[i] = "approve"
                    overrides[i] = new_override
                    st.session_state.steward_decisions = decisions
                    st.session_state.steward_overrides = overrides
                    st.rerun()
            with ac2:
                if st.button(f"❌ Reject GRP-{i+1:03d}", key=f"reject_{i}", use_container_width=True):
                    decisions[i] = "reject"
                    st.session_state.steward_decisions = decisions
                    st.rerun()
            with ac3:
                if d != "pending":
                    if st.button(f"🔄 Reset", key=f"reset_{i}", use_container_width=True):
                        decisions[i] = "pending"
                        st.session_state.steward_decisions = decisions
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("← Back to Merge Config", use_container_width=True):
            st.session_state.step = 4; st.rerun()
    with b2:
        if st.button("⚡ Approve All Remaining", use_container_width=True):
            for i in range(len(clusters)):
                if decisions.get(i, "pending") == "pending":
                    decisions[i] = "approve"
            st.session_state.steward_decisions = decisions
            st.rerun()
    with b3:
        if st.button("▶ Finalize & Export →", use_container_width=True):
            # Build golden records from steward decisions
            golden_records = {}
            for i, cl in enumerate(clusters):
                if decisions.get(i) == "approve":
                    golden_records[i] = overrides.get(i, {rec["data"] for rec in cl["records"]} and cl["records"][0]["data"])
            st.session_state.golden_records = golden_records
            st.session_state.step = 6
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — EXPORT (was step 4 auto or after steward)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 6:
    files_dfs = st.session_state.files_dfs
    clusters = st.session_state.clusters or []
    golden_records = st.session_state.golden_records
    merge_mode = st.session_state.merge_mode
    decisions = st.session_state.steward_decisions

    if not clusters or not golden_records:
        st.warning("No golden records generated. Please go back.")
        if st.button("← Back"): st.session_state.step = 4; st.rerun()
        st.stop()

    # Build final dataset
    # Collect all rows NOT in any approved cluster + golden records for approved clusters
    all_cluster_members = set()
    for i, cl in enumerate(clusters):
        if merge_mode == "auto" or decisions.get(i) == "approve":
            for fi, ri in cl["members"]:
                all_cluster_members.add((fi, ri))

    all_cols = []
    seen = set()
    for _, df in files_dfs:
        for c in df.columns:
            if c not in seen:
                all_cols.append(c)
                seen.add(c)
    all_cols_with_meta = ["_source", "_row"] + all_cols

    final_rows = []
    # Add golden records
    for i, cl in enumerate(clusters):
        if merge_mode == "auto" or decisions.get(i) == "approve":
            gr = golden_records.get(i, {})
            row = {"_source": "GOLDEN", "_row": f"GRP-{i+1:03d}"}
            for col in all_cols:
                row[col] = gr.get(col, "")
            final_rows.append(row)

    # Add non-clustered rows from all files
    for fi, (lbl, df) in enumerate(files_dfs):
        for ri in range(len(df)):
            if (fi, ri) not in all_cluster_members:
                row = {"_source": lbl, "_row": ri + 2}
                for col in all_cols:
                    row[col] = df[col].iloc[ri] if col in df.columns else ""
                final_rows.append(row)

    final_df = pd.DataFrame(final_rows, columns=all_cols_with_meta)
    st.session_state.final_df = final_df

    # Stats
    total_input = sum(len(df) for _, df in files_dfs)
    golden_count = len([r for r in final_rows if r["_source"] == "GOLDEN"])
    non_clustered = len([r for r in final_rows if r["_source"] != "GOLDEN"])
    dedup_saved = total_input - len(final_rows)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1.5px solid #bbf7d0;
        border-radius:16px;padding:20px 26px;margin-bottom:20px">
        <h3 style="margin:0 0 8px 0;color:#15803d">🏅 Golden Records Generated</h3>
        <p style="margin:0;color:#166534;font-size:0.9rem">Your master dataset is ready for export.</p>
    </div>
    <div class="metric-row">
        <div class="metric-card"><div class="val">{total_input:,}</div><div class="lbl">Total Input Records</div></div>
        <div class="metric-card"><div class="val" style="color:#d97706">{golden_count:,}</div><div class="lbl">Golden Records</div></div>
        <div class="metric-card"><div class="val" style="color:#2563eb">{non_clustered:,}</div><div class="lbl">Unique (Unmatched)</div></div>
        <div class="metric-card"><div class="val" style="color:#16a34a">{max(0,dedup_saved):,}</div><div class="lbl">Duplicates Resolved</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Preview
    st.markdown("#### 🔍 Preview — Final Master Dataset")
    st.dataframe(final_df.head(50), use_container_width=True)

    # Show cluster map
    st.markdown("#### 🗺️ Cluster Merge Map")
    merge_map_rows = []
    for i, cl in enumerate(clusters):
        status = "Auto-Merged" if merge_mode == "auto" else decisions.get(i, "pending").title()
        for rec in cl["records"]:
            merge_map_rows.append({
                "Group": f"GRP-{i+1:03d}",
                "Source": rec["source_label"],
                "Row": rec["row_idx"] + 2,
                "Status": status,
                "Max Score": cl["max_score"],
            })
    if merge_map_rows:
        st.dataframe(pd.DataFrame(merge_map_rows), use_container_width=True)

    # Download
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        final_df.to_excel(writer, sheet_name='Master Golden Records', index=False)
        if merge_map_rows:
            pd.DataFrame(merge_map_rows).to_excel(writer, sheet_name='Cluster Merge Map', index=False)
        # Per-source sheets
        for lbl, df in files_dfs:
            df.to_excel(writer, sheet_name=f'Source - {lbl[:20]}', index=False)
    out.seek(0)

    st.download_button(
        "⬇️ Download Master Dataset (Excel)",
        data=out,
        file_name="golden_master_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        back_step = 5 if merge_mode == "manual" else 4
        if st.button("← Back", use_container_width=True):
            st.session_state.step = back_step; st.rerun()
    with b2:
        if st.button("🔄 Start New Session", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
