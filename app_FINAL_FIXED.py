import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
import io
import time
import re
import json

# ─── Safe Slider Helper ───────────────────────────────────────────────
def safe_slider(label, max_val, default=20, key=None):
    if max_val <= 1:
        return max_val
    return st.slider(
        label,
        min_value=1,
        max_value=min(100, max_val),
        value=min(default, max_val),
        key=key
    )


# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="الريكوردات الذهبية | MDM",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;900&family=IBM+Plex+Mono:wght@500&display=swap');

:root {
    --blue:       #1d4ed8;
    --blue-mid:   #2563eb;
    --blue-light: #3b82f6;
    --blue-pale:  #eff6ff;
    --blue-border:#bfdbfe;
    --gold:       #d97706;
    --gold-light: #fef3c7;
    --gold-border:#fde68a;
    --bg:         #f0f4ff;
    --card:       #ffffff;
    --border:     #dbeafe;
    --text:       #0f172a;
    --muted:      #64748b;
    --danger:     #dc2626;
    --success:    #16a34a;
    --warn:       #d97706;
}

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
.stApp { background-color: var(--bg); }

.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 60%, #2563eb 100%);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:'';position:absolute;top:-40px;right:-40px;
    width:200px;height:200px;border-radius:50%;
    background:rgba(255,255,255,0.05);
}
.hero-icon {
    width:72px;height:72px;
    background:rgba(255,255,255,0.15);
    border:2px solid rgba(255,255,255,0.25);
    border-radius:18px;
    display:flex;align-items:center;justify-content:center;
    font-size:32px;flex-shrink:0;
}
.hero-text h1 { font-size:2rem;font-weight:900;margin:0 0 4px 0;color:#fff; }
.hero-text .sub { font-size:0.95rem;color:rgba(255,255,255,0.75);margin:0 0 6px 0; }
.hero-text .tagline { font-size:0.82rem;color:#fde68a;font-weight:600;letter-spacing:0.08em; }
.hero-badge {
    margin-right:auto;
    background:rgba(255,255,255,0.12);
    border:1px solid rgba(255,255,255,0.2);
    border-radius:10px;padding:10px 18px;
    text-align:center;color:white;font-size:0.78rem;
}
.hero-badge .hb-val { font-size:1.5rem;font-weight:900;color:#fde68a; }

.stepper {
    display:flex;align-items:center;
    margin-bottom:28px;
    background:var(--card);
    border:1.5px solid var(--border);
    border-radius:14px;
    padding:16px 28px;
}
.step { display:flex;align-items:center;gap:10px;flex:1; }
.step-circle {
    width:34px;height:34px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-weight:700;font-size:0.88rem;flex-shrink:0;
}
.step-circle.active  { background:var(--blue);color:#fff; }
.step-circle.done    { background:var(--blue-pale);color:var(--blue);border:2px solid var(--blue-light); }
.step-circle.pending { background:#f1f5f9;color:var(--muted); }
.step-label { font-size:0.83rem;font-weight:700; }
.step-label.active  { color:var(--blue); }
.step-label.pending { color:var(--muted); }
.step-connector { flex:1;height:2px;background:#e2e8f0;margin:0 8px;max-width:80px; }
.step-connector.done { background:var(--blue-light); }

.card {
    background:var(--card);
    border:1.5px solid var(--border);
    border-radius:14px;
    padding:24px 28px;
    margin-bottom:20px;
}
.card-title {
    font-size:0.72rem;font-weight:700;
    letter-spacing:0.12em;text-transform:uppercase;
    color:var(--muted);margin-bottom:16px;
}

.metric-row { display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px; }
.metric-card {
    background:var(--card);border:1.5px solid var(--border);
    border-radius:12px;padding:16px 20px;text-align:center;
}
.metric-card .val { font-size:1.8rem;font-weight:900;color:var(--blue-mid); }
.metric-card .lbl { font-size:0.78rem;color:var(--muted);margin-top:2px; }

.group-card {
    background:var(--blue-pale);border:1.5px solid var(--blue-border);
    border-radius:12px;padding:16px 20px;margin-bottom:14px;
}
.group-header { display:flex;align-items:center;gap:10px;margin-bottom:12px; }
.group-id {
    background:var(--blue-mid);color:#fff;
    border-radius:20px;padding:2px 12px;
    font-size:0.75rem;font-weight:700;
}
.name-row {
    display:flex;align-items:center;gap:8px;padding:7px 12px;
    border-radius:8px;margin-bottom:6px;
    background:var(--card);border:1px solid var(--blue-border);
    font-size:0.88rem;
}
.name-row.golden { background:var(--gold-light);border-color:var(--gold-border);font-weight:700; }
.golden-badge {
    background:var(--gold);color:#fff;border-radius:20px;
    padding:1px 10px;font-size:0.7rem;font-weight:700;flex-shrink:0;
}
.score-pill { margin-right:auto;border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:700; }
.score-high   { background:#dcfce7;color:#15803d; }
.score-medium { background:#fef9c3;color:#a16207; }
.score-low    { background:#fee2e2;color:#dc2626; }

.stButton > button {
    background:var(--blue-mid) !important;color:white !important;
    border:none !important;border-radius:10px !important;
    font-family:'Cairo',sans-serif !important;font-weight:700 !important;
    font-size:0.95rem !important;padding:10px 24px !important;
    transition:all 0.2s !important;
}
.stButton > button:hover {
    background:#1e40af !important;transform:translateY(-1px);
    box-shadow:0 4px 12px rgba(37,99,235,0.3) !important;
}
[data-testid="stFileUploader"] {
    border:2px dashed var(--blue-border) !important;
    border-radius:12px !important;background:var(--blue-pale) !important;
    padding:12px !important;
}
.stTabs [data-baseweb="tab-list"] { background:transparent !important;border-bottom:2px solid var(--border) !important;gap:4px; }
.stTabs [data-baseweb="tab"] { font-family:'Cairo',sans-serif !important;font-weight:600 !important;color:var(--muted) !important; }
.stTabs [aria-selected="true"] { color:var(--blue-mid) !important;border-bottom:2px solid var(--blue-mid) !important; }
.stProgress > div > div { background-color:var(--blue-mid) !important;border-radius:4px; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:2rem;padding-bottom:3rem; }
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


def find_duplicates_within(df, col, threshold, progress_bar=None):
    names = df[col].fillna("").tolist()
    normalized = [normalize_arabic(n) for n in names]
    results = []
    total = len(names)
    for i in range(total):
        if i % 100 == 0 and progress_bar:
            progress_bar.progress(min(i / total, 0.99))
        if not normalized[i]: continue
        for j in range(i + 1, total):
            if not normalized[j]: continue
            score = fuzz.token_sort_ratio(normalized[i], normalized[j])
            if score >= threshold:
                results.append({
                    "الصف الأول": i + 2, "الاسم الأول": names[i],
                    "الصف الثاني": j + 2, "الاسم الثاني": names[j],
                    "نسبة التشابه": score,
                    "الحالة": "تطابق تام" if score == 100 else "متشابه"
                })
    if progress_bar: progress_bar.progress(1.0)
    return pd.DataFrame(results)


def find_duplicates_across(df1, col1, df2, col2, threshold, progress_bar=None):
    names1 = df1[col1].fillna("").tolist()
    names2 = df2[col2].fillna("").tolist()
    norm1 = [normalize_arabic(n) for n in names1]
    norm2 = [normalize_arabic(n) for n in names2]
    results = []
    total = len(norm1)
    for i, (name1, n1) in enumerate(zip(names1, norm1)):
        if i % 100 == 0 and progress_bar:
            progress_bar.progress(min(i / total, 0.99))
        if not n1: continue
        matches = process.extract(n1, norm2, scorer=fuzz.token_sort_ratio, limit=3, score_cutoff=threshold)
        for _, score, idx in matches:
            results.append({
                "صف الملف الأول": i + 2, "اسم الملف الأول": name1,
                "صف الملف الثاني": idx + 2, "اسم الملف الثاني": names2[idx],
                "نسبة التشابه": score,
                "الحالة": "تطابق تام" if score == 100 else "متشابه"
            })
    if progress_bar: progress_bar.progress(1.0)
    return pd.DataFrame(results)


def build_clusters(results_df, mode="within"):
    from collections import defaultdict
    col_a = "الاسم الأول" if mode == "within" else "اسم الملف الأول"
    col_b = "الاسم الثاني" if mode == "within" else "اسم الملف الثاني"
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
        scores[key] = max(scores.get(key, 0), int(row["نسبة التشابه"]))
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
        if pd.api.types.is_numeric_dtype(series): col_type = "رقمي"
        elif pd.api.types.is_datetime64_any_dtype(series): col_type = "تاريخ"
        else: col_type = "نص عربي" if arabic_chars > len(sample) * 0.2 else "نص"
        p = {
            "col": col, "dtype": dtype, "col_type": col_type,
            "total": total_rows, "non_null": total_rows - null_count,
            "null_count": null_count,
            "null_pct": round(null_count / total_rows * 100, 1) if total_rows else 0,
            "unique_count": unique_count,
            "unique_pct": round(unique_count / total_rows * 100, 1) if total_rows else 0,
            "completeness": round((1 - null_count / total_rows) * 100, 1) if total_rows else 100,
        }
        if col_type == "رقمي" and len(non_null):
            p.update({"min": round(float(non_null.min()), 2), "max": round(float(non_null.max()), 2),
                       "mean": round(float(non_null.mean()), 2), "median": round(float(non_null.median()), 2),
                       "std": round(float(non_null.std()), 2), "zeros": int((non_null == 0).sum()),
                       "negatives": int((non_null < 0).sum())})
        else:
            p.update({"min": None, "max": None, "mean": None, "median": None,
                       "std": None, "zeros": 0, "negatives": 0})
        if col_type in ["نص", "نص عربي"] and len(non_null):
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


def mini_bar(value, color="#2563eb", width=110):
    pct = min(value, 100)
    return (f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="width:{width}px;height:9px;background:#e2e8f0;border-radius:5px;overflow:hidden">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:5px"></div></div>'
            f'<span style="font-size:0.78rem;font-weight:700;color:{color}">{value:.1f}%</span></div>')


def render_profile_section(df):
    profiles = profile_dataframe(df)
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    total_nulls = int(df.isna().sum().sum())
    completeness = round((1 - total_nulls / total_cells) * 100, 1) if total_cells else 100
    dup_rows = int(df.duplicated().sum())

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px">
        <div class="metric-card"><div class="val">{total_rows:,}</div><div class="lbl">إجمالي الصفوف</div></div>
        <div class="metric-card"><div class="val">{total_cols}</div><div class="lbl">عدد الأعمدة</div></div>
        <div class="metric-card">
            <div class="val" style="color:{'#16a34a' if completeness>=90 else '#d97706' if completeness>=70 else '#dc2626'}">{completeness}%</div>
            <div class="lbl">اكتمال البيانات</div>
        </div>
        <div class="metric-card">
            <div class="val" style="color:{'#dc2626' if dup_rows>0 else '#16a34a'}">{dup_rows:,}</div>
            <div class="lbl">صفوف مكررة</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_col = st.selectbox("🔍 اختر عمود للتفاصيل:", [p["col"] for p in profiles], key=f"prof_sel_{id(df)}")

    rows_html = ""
    for p in profiles:
        hl = "background:#eff6ff;" if p["col"] == selected_col else ""
        comp_color = "#16a34a" if p["completeness"] >= 90 else "#d97706" if p["completeness"] >= 70 else "#dc2626"
        rows_html += f"""
        <tr style="border-bottom:1px solid #dbeafe;{hl}">
            <td style="padding:10px 12px;font-weight:{'700' if p['col']==selected_col else '400'}">{p['col']}</td>
            <td style="padding:10px 12px"><span style="background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:20px;font-size:0.73rem;font-weight:700">{p['col_type']}</span></td>
            <td style="padding:10px 12px">{mini_bar(p['completeness'], comp_color)}</td>
            <td style="padding:10px 12px;font-size:0.85rem;color:#64748b">{p['null_count']:,} فارغ</td>
            <td style="padding:10px 12px">{mini_bar(p['unique_pct'], '#6366f1')}</td>
            <td style="padding:10px 12px;font-size:0.85rem;color:#64748b">{p['unique_count']:,} فريد</td>
        </tr>"""

    st.markdown(f"""
    <div class="card" style="padding:0;overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-family:'Cairo',sans-serif">
            <thead><tr style="background:#f8faff;border-bottom:2px solid #dbeafe">
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">العمود</th>
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">النوع</th>
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">الاكتمال</th>
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">فارغ</th>
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">التفرد</th>
                <th style="padding:12px;text-align:right;font-size:0.75rem;color:#64748b">قيم فريدة</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    p = next((x for x in profiles if x["col"] == selected_col), None)
    if not p: return

    st.markdown(f"#### 🔬 تفاصيل: `{selected_col}`")
    col_a, col_b = st.columns(2, gap="large")
    hc = "#16a34a" if p["completeness"] >= 90 else "#d97706" if p["completeness"] >= 70 else "#dc2626"
    hl = "ممتاز ✅" if p["completeness"] >= 90 else "متوسط ⚠️" if p["completeness"] >= 70 else "يحتاج مراجعة ❌"

    with col_a:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏥 صحة العمود</div>
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
                <div style="width:68px;height:68px;border-radius:50%;border:4px solid {hc};
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.1rem;font-weight:900;color:{hc}">{p['completeness']:.0f}%</div>
                <div><div style="font-weight:700;color:{hc}">{hl}</div>
                    <div style="font-size:0.8rem;color:#64748b">اكتمال البيانات</div></div>
            </div>
            <div style="font-size:0.87rem;line-height:2.2">
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">النوع</span><span style="font-weight:700">{p['col_type']} ({p['dtype']})</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">إجمالي</span><span style="font-weight:700">{p['total']:,}</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">مكتمل</span><span style="font-weight:700;color:#16a34a">{p['non_null']:,}</span></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                    <span style="color:#64748b">فارغ</span>
                    <span style="font-weight:700;color:{'#dc2626' if p['null_count']>0 else '#16a34a'}">{p['null_count']:,} ({p['null_pct']}%)</span></div>
                <div style="display:flex;justify-content:space-between;padding:2px 0">
                    <span style="color:#64748b">فريد</span><span style="font-weight:700;color:#6366f1">{p['unique_count']:,} ({p['unique_pct']}%)</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    with col_b:
        if p["col_type"] == "رقمي" and p["mean"] is not None:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📈 إحصائيات رقمية</div>
                <div style="font-size:0.87rem;line-height:2.2">
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Min</span><span style="font-weight:700">{p['min']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Max</span><span style="font-weight:700">{p['max']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Mean</span><span style="font-weight:700;color:#2563eb">{p['mean']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Median</span><span style="font-weight:700">{p['median']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">Std</span><span style="font-weight:700">{p['std']:,}</span></div>
                    <div style="display:flex;justify-content:space-between;padding:2px 0">
                        <span style="color:#64748b">أصفار / سالب</span>
                        <span style="font-weight:700">{p['zeros']:,} / {p['negatives']:,}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📝 إحصائيات نصية</div>
                <div style="font-size:0.87rem;line-height:2.5">
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">متوسط الطول</span><span style="font-weight:700">{p.get('avg_len','—')} حرف</span></div>
                    <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:2px 0">
                        <span style="color:#64748b">أقصر</span><span style="font-weight:700">{p.get('min_len','—')} حرف</span></div>
                    <div style="display:flex;justify-content:space-between;padding:2px 0">
                        <span style="color:#64748b">أطول</span><span style="font-weight:700">{p.get('max_len','—')} حرف</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

    if p.get("top_values"):
        st.markdown("##### 🏆 أكثر القيم تكراراً")
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
                    <span style="font-size:0.84rem;font-weight:600;max-width:65%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{val}</span>
                    <span style="font-size:0.8rem;color:#64748b">{cnt:,} <span style="color:{colors[i]}">({pct:.1f}%)</span></span>
                </div>
                <div style="height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden">
                    <div style="width:{bw}%;height:100%;background:{colors[i]};border-radius:4px"></div>
                </div>
            </div>"""
        st.markdown(f'<div class="card">{bars}</div>', unsafe_allow_html=True)

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        rows = []
        for p2 in profiles:
            r = {"العمود": p2["col"], "النوع": p2["col_type"], "نوع البيانات": p2["dtype"],
                 "إجمالي": p2["total"], "مكتمل": p2["non_null"], "فارغ": p2["null_count"],
                 "% فارغ": p2["null_pct"], "فريد": p2["unique_count"],
                 "% فريد": p2["unique_pct"], "% اكتمال": p2["completeness"]}
            if p2["mean"] is not None:
                r.update({"Min": p2["min"], "Max": p2["max"], "Mean": p2["mean"],
                           "Median": p2["median"], "Std": p2["std"]})
            rows.append(r)
        pd.DataFrame(rows).to_excel(writer, sheet_name="Data Profile", index=False)
    out.seek(0)
    st.download_button("⬇️ تحميل تقرير الـ Profile", data=out,
                        file_name="data_profile.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_prof_{id(df)}")


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [("step", 1), ("results_df", None), ("mode", "within"),
              ("df1", None), ("df2", None), ("clusters", None), ("merged_df", None)]:
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
        <h1>الريكوردات الذهبية</h1>
        <p class="sub">Master Data Management · Arabic Name Deduplication & Merge</p>
        <p class="tagline">✦ Let's Master your Data ✦</p>
    </div>
    {"" if total_records == 0 else f'<div class="hero-badge"><div class="hb-val">{total_records:,}</div><div>سجل محمّل</div></div>'}
</div>
""", unsafe_allow_html=True)

step = st.session_state.step

def sc(n): return "done" if n < step else ("active" if n == step else "pending")
def cc(n): return "done" if n < step else ""

st.markdown(f"""
<div class="stepper">
    <div class="step">
        <div class="step-circle {sc(1)}">{'✓' if step>1 else '1'}</div>
        <span class="step-label {'active' if step==1 else 'pending'}">رفع البيانات</span>
    </div>
    <div class="step-connector {cc(1)}"></div>
    <div class="step">
        <div class="step-circle {sc(2)}">{'✓' if step>2 else '2'}</div>
        <span class="step-label {'active' if step==2 else 'pending'}">الإعدادات</span>
    </div>
    <div class="step-connector {cc(2)}"></div>
    <div class="step">
        <div class="step-circle {sc(3)}">{'✓' if step>3 else '3'}</div>
        <span class="step-label {'active' if step==3 else 'pending'}">المطابقة والمجموعات</span>
    </div>
    <div class="step-connector {cc(3)}"></div>
    <div class="step">
        <div class="step-circle {sc(4)}">4</div>
        <span class="step-label {'active' if step==4 else 'pending'}">الريكورد الذهبي</span>
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
        mode = st.radio("**نوع المطابقة:**",
                         ["داخل نفس الملف (كشف التكرار)", "بين ملفين مختلفين (مقارنة)"],
                         horizontal=True)
        st.session_state.mode = "within" if "داخل" in mode else "across"
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.mode == "within":
            st.markdown('<div class="card-title">📁 ارفع ملف Excel / CSV</div>', unsafe_allow_html=True)
            file1 = st.file_uploader("رفع الملف", type=["xlsx", "xls", "csv"], key="f1", label_visibility="collapsed")
            st.caption("`.xlsx` · `.csv` · حتى 200MB")
            if file1:
                df1 = pd.read_csv(file1) if file1.name.endswith(".csv") else pd.read_excel(file1)
                st.session_state.df1 = df1
                st.session_state.df2 = None
                st.success(f"✅ **{file1.name}** — {len(df1):,} سجل · {len(df1.columns)} عمود")
                prev_tab, prof_tab = st.tabs(["👁️ معاينة", "📊 Data Profile"])
                with prev_tab:
                    st.dataframe(df1.head(10), width='stretch')
                with prof_tab:
                    render_profile_section(df1)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("التالي ← الإعدادات", width='stretch'):
                    st.session_state.step = 2; st.rerun()
        else:
            st.markdown('<div class="card-title">📁 الملف الأول</div>', unsafe_allow_html=True)
            file1 = st.file_uploader("رفع الملف", type=["xlsx", "xls", "csv"], key="f1", label_visibility="collapsed")
            st.markdown('<div class="card-title" style="margin-top:14px">📁 الملف الثاني</div>', unsafe_allow_html=True)
            file2 = st.file_uploader("رفع الملف", type=["xlsx", "xls", "csv"], key="f2", label_visibility="collapsed")
            if file1 and file2:
                df1 = pd.read_csv(file1) if file1.name.endswith(".csv") else pd.read_excel(file1)
                df2 = pd.read_csv(file2) if file2.name.endswith(".csv") else pd.read_excel(file2)
                st.session_state.df1 = df1; st.session_state.df2 = df2
                c1, c2 = st.columns(2)
                c1.success(f"✅ **{file1.name}** — {len(df1):,} سجل")
                c2.success(f"✅ **{file2.name}** — {len(df2):,} سجل")
                t1, t2 = st.tabs([f"📊 Profile: {file1.name}", f"📊 Profile: {file2.name}"])
                with t1: render_profile_section(df1)
                with t2: render_profile_section(df2)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("التالي ← الإعدادات", width='stretch'):
                    st.session_state.step = 2; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-title">ℹ️ ما هو MDM؟</div>
            <p style="font-size:0.87rem;color:#475569;line-height:1.9;margin:0">
                <b>Master Data Management</b> هو عملية تنظيف وتوحيد البيانات الرئيسية في المؤسسة.<br><br>
                🏅 <b>الريكورد الذهبي</b> هو النسخة الموثوقة الوحيدة لكل كيان بعد دمج التكرارات.<br><br>
                🔹 تحديد الأسماء المتشابهة<br>
                🔹 تجميعها في مجموعات<br>
                🔹 اختيار الريكورد الذهبي<br>
                🔹 دمج البيانات وتصدير ملف نظيف
            </p>
        </div>
        <div class="card">
            <div class="card-title">💡 تطبيع الأسماء العربية</div>
            <p style="font-size:0.85rem;color:#475569;line-height:2;margin:0">
                أ / إ / آ / ا → <b>ا</b><br>
                ة → <b>ه</b><br>
                ي / ى → <b>ي</b><br>
                التشكيل → <b>يُحذف</b><br>
                مسافات زائدة → <b>تُزال</b>
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — CONFIGURE
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    df1 = st.session_state.get("df1")
    df2 = st.session_state.get("df2")
    if df1 is None:
        st.warning("ارجع للخطوة الأولى وارفع الملف.")
        if st.button("← رجوع"): st.session_state.step = 1; st.rerun()
        st.stop()

    col_main, col_side = st.columns([2, 1], gap="large")
    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚙️ إعدادات المطابقة</div>', unsafe_allow_html=True)
        cols = list(df1.columns)
        if st.session_state.mode == "within":
            name_col1 = st.selectbox("اختر عمود الأسماء:", cols, key="col1")
            name_col2 = None
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**الملف الأول:**")
                name_col1 = st.selectbox("عمود الأسماء:", cols, key="col1")
            with c2:
                st.markdown("**الملف الثاني:**")
                cols2 = list(df2.columns) if df2 is not None else []
                name_col2 = st.selectbox("عمود الأسماء:", cols2, key="col2")

        st.markdown("<br>", unsafe_allow_html=True)
        threshold = st.slider("🎯 حد التشابه الأدنى:", min_value=50, max_value=100, value=80, step=5)
        st.markdown(f"""
        <div style="background:var(--blue-pale);border:1px solid var(--blue-border);
            border-radius:10px;padding:12px 16px;margin:12px 0">
            سيظهر أي اسمين نسبة تشابههم ≥ <b style="color:var(--blue-mid)">{threshold}%</b>
        </div>
        """, unsafe_allow_html=True)
        st.checkbox("✅ تطبيع الأسماء العربية (موصى به)", value=True, key="normalize_cb")
        st.session_state.threshold = threshold
        st.session_state.name_col1 = name_col1
        st.session_state.name_col2 = name_col2

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("← رجوع", width='stretch'):
                st.session_state.step = 1; st.rerun()
        with b2:
            if st.button("🚀 ابدأ المطابقة", width='stretch'):
                st.session_state.step = 3
                st.session_state.results_df = None
                st.session_state.clusters = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📊 معلومات الملف</div>
            <p style="font-size:0.9rem;margin:0;line-height:2.2">
                🗂 سجلات: <b>{len(df1):,}</b><br>
                📋 أعمدة: <b>{len(df1.columns)}</b>
                {"<br>🗂 الملف الثاني: <b>" + str(len(df2)) + " سجل</b>" if df2 is not None else ""}
            </p>
        </div>
        <div class="card">
            <div class="card-title">💡 نصائح الـ Threshold</div>
            <p style="font-size:0.84rem;color:#475569;line-height:2;margin:0">
                <b style="color:#16a34a">90–100%</b> → دقة عالية جداً<br>
                <b style="color:#2563eb">80–89%</b> → موصى بها<br>
                <b style="color:#d97706">65–79%</b> → بحث واسع<br>
                <b style="color:#dc2626">50–64%</b> → نتائج كثيرة
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — RESULTS + CLUSTERS
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    df1 = st.session_state.get("df1")
    df2 = st.session_state.get("df2")
    threshold = st.session_state.get("threshold", 80)
    name_col1 = st.session_state.get("name_col1")
    name_col2 = st.session_state.get("name_col2")
    mode = st.session_state.mode

    if df1 is None or name_col1 is None:
        st.warning("ارجع وأعد الإعداد.")
        if st.button("← رجوع"): st.session_state.step = 1; st.rerun()
        st.stop()

    if st.session_state.results_df is None:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⏳ جاري المطابقة...")
        prog = st.progress(0)
        status = st.empty()
        status.text("🔄 تحضير البيانات...")
        time.sleep(0.3)
        try:
            if mode == "within":
                status.text("🔍 البحث عن الأسماء المتشابهة...")
                results = find_duplicates_within(df1, name_col1, threshold, prog)
            else:
                status.text("🔍 المقارنة بين الملفين...")
                results = find_duplicates_across(df1, name_col1, df2, name_col2, threshold, prog)
            st.session_state.results_df = results
            status.text("🧩 تجميع المجموعات...")
            st.session_state.clusters = build_clusters(results, mode)
            status.text("✅ اكتمل!")
            time.sleep(0.4)
        except Exception as e:
            st.error(f"❌ خطأ: {e}"); st.stop()
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()

    results  = st.session_state.results_df
    clusters = st.session_state.clusters or []
    total_matches = len(results)
    exact_matches = int((results["الحالة"] == "تطابق تام").sum()) if total_matches else 0
    similar_matches = total_matches - exact_matches
    avg_score = round(results["نسبة التشابه"].mean(), 1) if total_matches else 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="val">{total_matches:,}</div><div class="lbl">إجمالي الأزواج</div></div>
        <div class="metric-card"><div class="val" style="color:#dc2626">{exact_matches:,}</div><div class="lbl">تطابق تام 100%</div></div>
        <div class="metric-card"><div class="val" style="color:#d97706">{similar_matches:,}</div><div class="lbl">أسماء متشابهة</div></div>
        <div class="metric-card"><div class="val">{len(clusters):,}</div><div class="lbl">مجموعات (Clusters)</div></div>
    </div>
    """, unsafe_allow_html=True)

    if total_matches == 0:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px">
            <div style="font-size:3rem">🎉</div>
            <h3>لا توجد تكرارات!</h3>
            <p style="color:#64748b">لم يُعثر على أسماء مكررة بالـ Threshold المحدد.</p>
        </div>""", unsafe_allow_html=True)
    else:
        tab_raw, tab_clusters, tab_chart = st.tabs([
            "📋 نتائج المطابقة", "🧩 المجموعات والكود (GRP)", "📊 توزيع التشابه"
        ])

        
        with tab_raw:
            cf1, cf2 = st.columns([1, 2])
            with cf1: filt = st.selectbox("فلتر:", ["الكل", "تطابق تام", "متشابه"])
            with cf2: search = st.text_input("🔍 بحث:", placeholder="اكتب اسم...")
            disp = results.copy()
            if filt != "الكل": disp = disp[disp["الحالة"] == filt]
            if search: disp = disp[disp.apply(lambda r: search in str(r.values), axis=1)]
            def hl(val):
                if val >= 85: return "background:#dcfce7;color:#15803d;font-weight:700"
                if val >= 70: return "background:#fef9c3;color:#a16207;font-weight:700"
                return "background:#fee2e2;color:#dc2626;font-weight:700"
                styled = disp.style.map(hl, subset=["نسبة التشابه"])
                st.dataframe(styled, use_container_width=True, height=400)
                st.caption(f"عرض {len(disp):,} من {total_matches:,}")

        with tab_clusters:
            st.markdown("""
            <div style="background:var(--blue-pale);border:1px solid var(--blue-border);
                border-radius:10px;padding:12px 16px;margin-bottom:16px;font-size:0.87rem;color:#1e40af">
                كل مجموعة تضم أسماء متشابهة.
                🏅 <b>الريكورد الذهبي</b> = الاسم الأكثر اكتمالاً.
                الكود <code>GRP-001</code> يُستخدم في الدمج.
            </div>
            """, unsafe_allow_html=True)
            show_limit = safe_slider("عدد المجموعات المعروضة:", len(clusters), key="cl_limit")
            for i, cluster in enumerate(clusters[:show_limit]):
                golden = pick_golden_record(cluster["names"])
                sc_val = cluster["max_score"]
                sc_class = "score-high" if sc_val >= 85 else ("score-medium" if sc_val >= 70 else "score-low")
                rows_html = "".join(f"""
                <div class="name-row {'golden' if n==golden else ''}">
                    {'<span class="golden-badge">🏅 ذهبي</span>' if n==golden else '<span style="width:58px;display:inline-block"></span>'}
                    <span>{n}</span>
                </div>""" for n in cluster["names"])
                st.markdown(f"""
                <div class="group-card">
                    <div class="group-header">
                        <span class="group-id">GRP-{i+1:03d}</span>
                        <span style="font-size:0.78rem;color:#64748b">{len(cluster['names'])} أسماء</span>
                        <span class="score-pill {sc_class}">{sc_val}%</span>
                    </div>
                    {rows_html}
                </div>""", unsafe_allow_html=True)
            if len(clusters) > show_limit:
                st.caption(f"يتم عرض {show_limit} من {len(clusters)} مجموعة.")

        with tab_chart:
            bins = [50,60,70,80,90,100]
            labels = ["50-60%","60-70%","70-80%","80-90%","90-100%","100%"]
            scores = results["نسبة التشابه"].tolist()
            hist = [sum(1 for s in scores if bins[i]<=s<bins[i+1]) for i in range(5)]
            hist.append(sum(1 for s in scores if s==100))
            cd = json.dumps([{"l":labels[i],"c":hist[i]} for i in range(6)])
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📊 توزيع نسب التشابه</div>
                <div id="mdm-chart" style="display:flex;align-items:flex-end;gap:14px;height:180px;padding:16px 0"></div>
            </div>
            <script>(function(){{
                const d={cd};const mx=Math.max(...d.map(x=>x.c));
                const el=document.getElementById('mdm-chart');if(!el)return;
                const cs=['#1d4ed8','#2563eb','#3b82f6','#60a5fa','#93c5fd','#bfdbfe'];
                d.forEach((item,i)=>{{
                    const div=document.createElement('div');
                    div.style.cssText='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px';
                    const h=mx>0?Math.round((item.c/mx)*150):0;
                    div.innerHTML=`<span style="font-size:0.8rem;font-weight:700;color:${{cs[i]}}">${{item.c}}</span>
                        <div style="width:100%;height:${{h}}px;background:${{cs[i]}};border-radius:6px 6px 0 0;min-height:4px"></div>
                        <span style="font-size:0.73rem;color:#64748b">${{item.l}}</span>`;
                    el.appendChild(div);
                }});
            }})();</script>
            """, unsafe_allow_html=True)

        # Downloads
        st.markdown("<br>", unsafe_allow_html=True)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            results.to_excel(writer, sheet_name='نتائج المطابقة', index=False)
            cl_rows = []
            for i, cl in enumerate(clusters):
                g = pick_golden_record(cl["names"])
                for name in cl["names"]:
                    cl_rows.append({"كود المجموعة": f"GRP-{i+1:03d}", "الاسم": name,
                                     "الريكورد الذهبي": g,
                                     "هو الريكورد الذهبي": "نعم" if name==g else "لا",
                                     "أقصى تشابه": cl["max_score"]})
            pd.DataFrame(cl_rows).to_excel(writer, sheet_name='المجموعات والكود', index=False)
            pd.DataFrame({"المقياس":["إجمالي الأزواج","تطابق تام","متشابه","مجموعات","متوسط التشابه"],
                           "القيمة":[total_matches,exact_matches,similar_matches,len(clusters),f"{avg_score}%"]}
                          ).to_excel(writer, sheet_name='ملخص', index=False)
        out.seek(0)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("⬇️ تحميل النتائج (Excel)", data=out,
                                file_name="golden_records_results.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                width='stretch')
        with d2:
            csv_data = results.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("⬇️ تحميل النتائج (CSV)",
                                data=csv_data.encode("utf-8-sig"),
                                file_name="golden_records_results.csv",
                                mime="text/csv", width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("← تعديل الإعدادات", width='stretch'):
            st.session_state.results_df = None
            st.session_state.clusters = None
            st.session_state.step = 2; st.rerun()
    with nav2:
        if total_matches > 0:
            if st.button("🏅 الانتقال للدمج — Golden Record Merge", width='stretch'):
                st.session_state.step = 4; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — GOLDEN RECORD MERGE
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    df1       = st.session_state.get("df1")
    clusters  = st.session_state.get("clusters", [])
    name_col1 = st.session_state.get("name_col1")

    if df1 is None or not clusters:
        st.warning("ارجع للخطوة السابقة أولاً.")
        if st.button("← رجوع"): st.session_state.step = 3; st.rerun()
        st.stop()

    st.markdown("""
    <div style="background:var(--gold-light);border:1.5px solid var(--gold-border);
        border-radius:14px;padding:18px 24px;margin-bottom:20px">
        <h3 style="margin:0 0 6px 0;color:#92400e">🏅 Golden Record Merge</h3>
        <p style="margin:0;color:#78350f;font-size:0.9rem">
            راجع الريكوردات الذهبية المقترحة، عدّل أي منها يدوياً،
            ثم اضغط <b>تطبيق الدمج</b> لتصدير بياناتك النظيفة.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "golden_overrides" not in st.session_state:
        st.session_state.golden_overrides = {}

    show_n = safe_slider("عدد المجموعات:", len(clusters), key="merge_limit")

    for i, cluster in enumerate(clusters[:show_n]):
        auto_golden = pick_golden_record(cluster["names"])
        ok  = f"golden_{i}"
        cur = st.session_state.golden_overrides.get(ok, auto_golden)
        sc_val = cluster["max_score"]
        sc_class = "score-high" if sc_val >= 85 else ("score-medium" if sc_val >= 70 else "score-low")

        with st.expander(f"GRP-{i+1:03d}  ·  {len(cluster['names'])} أسماء  ·  {sc_val}% تشابه", expanded=(i<5)):
            c_names, c_golden = st.columns([1,1], gap="large")
            with c_names:
                st.markdown("**الأسماء في المجموعة:**")
                for name in cluster["names"]:
                    is_g = name == cur
                    st.markdown(f"""
                    <div style="padding:7px 12px;border-radius:8px;margin-bottom:6px;
                        background:{'#fef3c7' if is_g else '#f8faff'};
                        border:1px solid {'#fde68a' if is_g else '#dbeafe'};
                        font-size:0.88rem;font-weight:{'700' if is_g else '400'}">
                        {'🏅 ' if is_g else '• '}{name}
                    </div>""", unsafe_allow_html=True)

            with c_golden:
                st.markdown("**اختر الريكورد الذهبي:**")
                chosen = st.selectbox("",
                    options=cluster["names"],
                    index=cluster["names"].index(cur) if cur in cluster["names"] else 0,
                    key=f"sel_{i}", label_visibility="collapsed")
                st.session_state.golden_overrides[ok] = chosen
                st.markdown(f"""
                <div style="margin-top:12px;background:#fef3c7;border:1px solid #fde68a;
                    border-radius:10px;padding:10px 14px;text-align:center">
                    <div style="font-size:0.72rem;color:#92400e;font-weight:700;margin-bottom:4px">🏅 الريكورد الذهبي</div>
                    <div style="font-size:1rem;font-weight:900;color:#78350f">{chosen}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:var(--blue-pale);border:1px solid var(--blue-border);
        border-radius:10px;padding:12px 16px;margin-bottom:16px;font-size:0.87rem;color:#1e40af">
        بعد الضغط على <b>تطبيق الدمج</b>، كل الأسماء في كل مجموعة هتتبدل بالريكورد الذهبي المختار
        في ملف Excel نظيف جاهز للتحميل.
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ تطبيق الدمج وتصدير الملف النظيف", width='stretch'):
        merged = df1.copy()
        for i, cluster in enumerate(clusters):
            golden = st.session_state.golden_overrides.get(f"golden_{i}", pick_golden_record(cluster["names"]))
            for name in cluster["names"]:
                if name != golden:
                    merged.loc[merged[name_col1] == name, name_col1] = golden
        st.session_state.merged_df = merged
        original_unique = df1[name_col1].nunique()
        merged_unique = merged[name_col1].nunique()
        st.success(f"✅ تم الدمج! — {len(merged):,} سجل")
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0">
            <div class="metric-card"><div class="val">{original_unique:,}</div><div class="lbl">قيم فريدة قبل</div></div>
            <div class="metric-card"><div class="val" style="color:#16a34a">{merged_unique:,}</div><div class="lbl">قيم فريدة بعد</div></div>
            <div class="metric-card"><div class="val" style="color:#2563eb">{original_unique-merged_unique:,}</div><div class="lbl">تم توحيده</div></div>
        </div>""", unsafe_allow_html=True)
        st.dataframe(merged.head(10), width='stretch')

    if st.session_state.get("merged_df") is not None:
        merged = st.session_state.merged_df
        out_m = io.BytesIO()
        with pd.ExcelWriter(out_m, engine='openpyxl') as writer:
            merged.to_excel(writer, sheet_name='البيانات النظيفة', index=False)
            cl_rows = []
            for i, cl in enumerate(clusters):
                g = st.session_state.golden_overrides.get(f"golden_{i}", pick_golden_record(cl["names"]))
                for name in cl["names"]:
                    cl_rows.append({"كود المجموعة": f"GRP-{i+1:03d}",
                                     "الاسم الأصلي": name, "الريكورد الذهبي": g})
            pd.DataFrame(cl_rows).to_excel(writer, sheet_name='خريطة الدمج', index=False)
        out_m.seek(0)
        st.download_button("⬇️ تحميل الملف النظيف (Excel)", data=out_m,
                            file_name="golden_records_clean.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← رجوع للنتائج", width='stretch'):
            st.session_state.step = 3; st.rerun()
    with b2:
        if st.button("🔄 تحليل جديد", width='stretch'):
            for k in ["results_df","clusters","df1","df2","merged_df","golden_overrides"]:
                st.session_state[k] = None
            st.session_state.step = 1; st.rerun()
