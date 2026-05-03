import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
import io, time, re
from collections import defaultdict

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Golden Data | MDM", page_icon="🏅",
                   layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{
  --blue:#1d4ed8;--blue-mid:#2563eb;--blue-light:#3b82f6;
  --blue-pale:#eff6ff;--blue-border:#bfdbfe;
  --gold:#d97706;--gold-light:#fef3c7;--gold-border:#fde68a;
  --green:#16a34a;--green-pale:#f0fdf4;--green-border:#bbf7d0;
  --red:#dc2626;--red-pale:#fff5f5;--red-border:#fecaca;
  --purple:#7c3aed;--teal:#0d9488;
  --bg:#f1f5fb;--card:#ffffff;--border:#e2e8f0;
  --text:#0f172a;--muted:#64748b;--muted2:#94a3b8;
  --radius:14px;--shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(37,99,235,.07);
  --shadow-lg:0 8px 32px rgba(29,78,216,.18);
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg);color:var(--text);}
.stApp{background:var(--bg);}

/* HERO */
.hero{background:linear-gradient(135deg,#0a1628 0%,#1e3a8a 45%,#1d4ed8 78%,#2563eb 100%);
  border-radius:20px;padding:28px 36px;margin-bottom:6px;display:flex;align-items:center;gap:22px;
  position:relative;overflow:hidden;box-shadow:var(--shadow-lg);}
.hero::before{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;
  border-radius:50%;background:rgba(255,255,255,0.04);}
.hero-icon{width:62px;height:62px;background:rgba(255,255,255,0.12);border:1.5px solid rgba(255,255,255,0.2);
  border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0;}
.hero-text h1{font-size:1.65rem;font-weight:900;margin:0 0 2px 0;color:#fff;letter-spacing:-0.02em;}
.hero-text .sub{font-size:0.8rem;color:rgba(255,255,255,0.62);margin:0 0 6px 0;}
.hero-text .tag{font-size:0.7rem;color:#fde68a;font-weight:700;letter-spacing:.1em;text-transform:uppercase;}
.hero-stats{margin-left:auto;display:flex;gap:12px;flex-shrink:0;}
.hero-stat{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
  border-radius:10px;padding:10px 16px;text-align:center;color:white;font-size:0.7rem;backdrop-filter:blur(4px);}
.hero-stat .hv{font-size:1.2rem;font-weight:900;color:#fde68a;display:block;}

/* PAGE TITLE */
.page-title{font-size:1.05rem;font-weight:800;color:var(--text);margin-bottom:2px;letter-spacing:-0.01em;}
.page-sub{font-size:0.79rem;color:var(--muted);margin-bottom:18px;}

/* CARDS */
.card{background:var(--card);border:1.5px solid var(--border);border-radius:var(--radius);
  padding:20px 24px;margin-bottom:14px;box-shadow:var(--shadow);}
.card-title{font-size:0.63rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin-bottom:12px;}

/* METRICS */
.mrow{display:grid;gap:12px;margin-bottom:16px;}
.mrow-4{grid-template-columns:repeat(4,1fr);}
.mrow-3{grid-template-columns:repeat(3,1fr);}
.mrow-5{grid-template-columns:repeat(5,1fr);}
@media(max-width:700px){.mrow-4,.mrow-3,.mrow-5{grid-template-columns:repeat(2,1fr);}}
.mc{background:var(--card);border:1.5px solid var(--border);border-radius:12px;
  padding:15px 16px;text-align:center;box-shadow:var(--shadow);position:relative;overflow:hidden;}
.mc::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--blue-mid);}
.mc.g::after{background:var(--green);} .mc.r::after{background:var(--red);}
.mc.o::after{background:var(--gold);} .mc.p::after{background:var(--purple);}
.mc .val{font-size:1.55rem;font-weight:900;color:var(--blue-mid);}
.mc .lbl{font-size:0.67rem;color:var(--muted);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;}

/* BADGES */
.src-badge{display:inline-block;padding:2px 9px;border-radius:16px;font-size:0.68rem;font-weight:700;margin-right:4px;}
.token-badge{font-family:'IBM Plex Mono',monospace;background:#1e3a8a;color:#bfdbfe;
  border-radius:6px;padding:2px 8px;font-size:0.7rem;font-weight:600;}
.sp{border-radius:16px;padding:2px 9px;font-size:0.69rem;font-weight:700;}
.sp-hi{background:#dcfce7;color:#15803d;} .sp-mid{background:#fef9c3;color:#a16207;} .sp-lo{background:#fee2e2;color:#dc2626;}
.rb-auto{background:#dcfce7;color:#166534;border:1px solid #bbf7d0;border-radius:6px;padding:2px 9px;font-size:0.68rem;font-weight:700;}
.rb-man{background:#fef3c7;color:#92400e;border:1px solid #fde68a;border-radius:6px;padding:2px 9px;font-size:0.68rem;font-weight:700;}
.sb-app{background:var(--green-pale);color:var(--green);border:1px solid var(--green-border);border-radius:6px;padding:2px 9px;font-size:0.7rem;font-weight:700;}
.sb-rej{background:var(--red-pale);color:var(--red);border:1px solid var(--red-border);border-radius:6px;padding:2px 9px;font-size:0.7rem;font-weight:700;}
.sb-pnd{background:var(--gold-light);color:#92400e;border:1px solid var(--gold-border);border-radius:6px;padding:2px 9px;font-size:0.7rem;font-weight:700;}

/* CLUSTER */
.cl-card{background:var(--blue-pale);border:1.5px solid var(--blue-border);border-radius:12px;padding:14px 16px;margin-bottom:10px;}
.cl-header{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;}
.cl-id{background:var(--blue-mid);color:#fff;border-radius:14px;padding:2px 11px;font-size:0.66rem;font-weight:700;font-family:'IBM Plex Mono',monospace;}
.rec-row{display:flex;align-items:center;gap:8px;padding:7px 11px;border-radius:8px;margin-bottom:4px;background:#fff;border:1px solid var(--blue-border);font-size:0.82rem;}

/* PAIR GROUP */
.pg{background:#fff;border:1.5px solid var(--border);border-radius:10px;margin-bottom:8px;overflow:hidden;}
.pg-hdr{background:linear-gradient(90deg,#eff6ff,#f8faff);padding:8px 14px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--blue-border);}
.pg-row{padding:7px 14px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #f1f5f9;font-size:0.81rem;flex-wrap:wrap;}
.pg-row:last-child{border-bottom:none;}

/* PROFILE */
.prof-tbl{width:100%;border-collapse:collapse;font-size:0.8rem;}
.prof-tbl th{padding:9px 12px;text-align:left;background:#f8faff;border-bottom:2px solid var(--blue-border);
  font-size:0.65rem;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;}
.prof-tbl td{padding:9px 12px;border-bottom:1px solid #f1f5f9;}
.prof-tbl tr:hover td{background:#fafbff;}

/* INFO BOXES */
.ib{border-radius:12px;padding:12px 16px;margin-bottom:12px;font-size:0.83rem;line-height:1.7;}
.ib-bl{background:var(--blue-pale);border:1.5px solid var(--blue-border);color:#1e40af;}
.ib-gr{background:var(--green-pale);border:1.5px solid var(--green-border);color:#166534;}
.ib-gd{background:var(--gold-light);border:1.5px solid var(--gold-border);color:#92400e;}

/* SYSTEM SOURCE BLOCK */
.sys-block{background:#f8faff;border:1.5px solid var(--border);border-radius:10px;padding:14px 18px;margin-bottom:12px;}
.sys-block-title{font-size:0.68rem;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;}

/* GAUGE */
.gauge-wrap{text-align:center;background:var(--card);border:1.5px solid var(--border);border-radius:12px;padding:14px 8px;box-shadow:var(--shadow);}

/* BUTTONS */
.stButton>button{background:linear-gradient(135deg,#2563eb,#1d4ed8)!important;color:#fff!important;
  border:none!important;border-radius:10px!important;font-family:'Inter',sans-serif!important;
  font-weight:700!important;font-size:0.87rem!important;padding:10px 20px!important;
  transition:all .18s!important;box-shadow:0 2px 8px rgba(37,99,235,.22)!important;}
.stButton>button:hover{background:linear-gradient(135deg,#1e40af,#1d4ed8)!important;
  transform:translateY(-1px)!important;box-shadow:0 4px 14px rgba(37,99,235,.33)!important;}
[data-testid="stFileUploader"]{border:2px dashed var(--blue-border)!important;border-radius:12px!important;background:var(--blue-pale)!important;padding:10px!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:2px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Inter',sans-serif!important;font-weight:600!important;color:var(--muted)!important;}
.stTabs [aria-selected="true"]{color:var(--blue-mid)!important;border-bottom:2.5px solid var(--blue-mid)!important;}
.stProgress>div>div{background:var(--blue-mid)!important;border-radius:4px!important;}
[data-testid="stExpander"]{border:1.5px solid var(--border)!important;border-radius:12px!important;background:var(--card)!important;margin-bottom:8px!important;}
.section-div{border:none;border-top:1.5px solid var(--border);margin:14px 0;}

/* SIDEBAR */
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 14px;border-radius:10px;
  font-size:0.82rem;font-weight:600;color:var(--muted);margin-bottom:2px;transition:all .15s;}
.nav-item.nav-active{background:var(--blue-pale);color:var(--blue-mid);border-left:3px solid var(--blue-mid);}
.nav-item.nav-done{color:var(--green);}
.nav-dot{width:7px;height:7px;border-radius:50%;background:var(--muted2);flex-shrink:0;}
.nav-dot.nd-active{background:var(--blue-mid);} .nav-dot.nd-done{background:var(--green);}

#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:1.2rem!important;padding-bottom:3rem!important;}
@media(max-width:640px){.hero{padding:16px 14px;gap:12px;}.hero-text h1{font-size:1.2rem;}.hero-stats{display:none;}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def normalize_text(text):
    if not isinstance(text, str): return str(text).strip()
    t = text.strip()
    t = re.sub(r'[أإآا]','ا',t); t = re.sub(r'ة','ه',t)
    t = re.sub(r'[يى]','ي',t); t = re.sub(r'[\u0610-\u061A\u064B-\u065F]','',t)
    return re.sub(r'\s+',' ',t)

def read_file(up):
    n = up.name.lower()
    try:
        if n.endswith(".csv"):           return pd.read_csv(up)
        if n.endswith((".xls",".xlsx")): return pd.read_excel(up)
        if n.endswith(".json"):          return pd.read_json(up)
    except: pass
    return None

SRC_COLORS = ["#2563eb","#7c3aed","#0d9488","#d97706","#dc2626","#16a34a","#0891b2","#9333ea"]
def src_color(lbl): return SRC_COLORS[abs(hash(str(lbl))) % len(SRC_COLORS)]

def src_badge(lbl):
    c = src_color(lbl)
    return f'<span class="src-badge" style="background:{c}18;color:{c};border:1px solid {c}35">{lbl}</span>'

def sp(sc):
    cls = "sp-hi" if sc>=90 else "sp-mid" if sc>=70 else "sp-lo"
    return f'<span class="sp {cls}">{sc}%</span>'

def mini_bar(v, color="#2563eb", w=90):
    p = min(max(v,0),100)
    return (f'<div style="display:flex;align-items:center;gap:5px">'
            f'<div style="width:{w}px;height:6px;background:#e2e8f0;border-radius:4px;overflow:hidden">'
            f'<div style="width:{p:.0f}%;height:100%;background:{color};border-radius:4px"></div></div>'
            f'<span style="font-size:0.72rem;font-weight:700;color:{color}">{v:.1f}%</span></div>')

def get_all_cols(files_dfs):
    seen=set(); cols=[]
    for _,df in files_dfs:
        for c in df.columns:
            if c not in seen: cols.append(c); seen.add(c)
    return cols


# ──────────────────────────────────────────────────────────────────────────────
# DATA PROFILE
# ──────────────────────────────────────────────────────────────────────────────
def profile_df(df):
    n = len(df); profiles=[]
    for col in df.columns:
        s=df[col]; null_c=int(s.isna().sum()); nn=s.dropna()
        u=int(s.nunique()); dtype=str(s.dtype)
        sample=" ".join(nn.astype(str).head(20).tolist())
        ar=len(re.findall(r'[\u0600-\u06FF]',sample))
        if pd.api.types.is_numeric_dtype(s): ctype="Numeric"
        elif pd.api.types.is_datetime64_any_dtype(s): ctype="Date"
        else: ctype="Arabic" if ar>len(sample)*0.2 else "Text"
        comp=round((1-null_c/n)*100,1) if n else 100
        uniq=round(u/n*100,1) if n else 0
        p={"col":col,"dtype":dtype,"ctype":ctype,"n":n,"null_c":null_c,
           "null_pct":round(null_c/n*100,1) if n else 0,
           "unique_c":u,"completeness":comp,"uniqueness":uniq}
        if ctype=="Numeric" and len(nn):
            nv=nn.astype(float)
            p.update({"min":round(float(nv.min()),2),"max":round(float(nv.max()),2),
                      "mean":round(float(nv.mean()),2),"median":round(float(nv.median()),2),
                      "std":round(float(nv.std()),2)})
        else:
            p.update({"min":None,"max":None,"mean":None,"median":None,"std":None})
        p["top_values"]=[(str(k),int(v)) for k,v in s.value_counts().head(5).items()]
        profiles.append(p)
    return profiles

def render_profile(df, label=""):
    profiles=profile_df(df)
    n=len(df); nc=len(df.columns)
    null_t=int(df.isna().sum().sum())
    comp=round((1-null_t/(n*nc))*100,1) if n*nc else 100
    uniq=round(df.drop_duplicates().shape[0]/n*100,1) if n else 100
    dups=int(df.duplicated().sum())
    dq=round(comp*0.6+uniq*0.4,1)

    def col_c(v,hi=90,lo=70):
        return "#16a34a" if v>=hi else "#d97706" if v>=lo else "#dc2626"

    cc,uc,dc=col_c(comp),col_c(uniq),col_c(dq,85,65)
    st.markdown(f"""<div class="mrow mrow-4">
      <div class="mc"><div class="val">{n:,}</div><div class="lbl">Total Rows</div></div>
      <div class="mc"><div class="val">{nc}</div><div class="lbl">Columns</div></div>
      <div class="mc {'g' if comp>=90 else 'o' if comp>=70 else 'r'}">
        <div class="val" style="color:{cc}">{comp}%</div><div class="lbl">Completeness</div></div>
      <div class="mc {'g' if dups==0 else 'r'}">
        <div class="val" style="color:{'#16a34a' if dups==0 else '#dc2626'}">{dups:,}</div>
        <div class="lbl">Duplicate Rows</div></div>
    </div>""", unsafe_allow_html=True)

    # Gauges
    def gauge(v, lbl, color, icon):
        circ=v*1.885
        return f"""<div class="gauge-wrap">
          <svg width="130" height="76" viewBox="0 0 130 76">
            <path d="M13,68 A52,52 0 0,1 117,68" fill="none" stroke="#e2e8f0" stroke-width="10" stroke-linecap="round"/>
            <path d="M13,68 A52,52 0 0,1 117,68" fill="none" stroke="{color}" stroke-width="10"
              stroke-linecap="round" stroke-dasharray="{circ:.1f} 163.4"/>
            <text x="65" y="60" text-anchor="middle" font-size="15" font-weight="900" fill="{color}"
              font-family="Inter,sans-serif">{v:.0f}%</text>
          </svg>
          <div style="font-size:0.7rem;font-weight:700;color:var(--muted);margin-top:-4px">{icon} {lbl}</div>
        </div>"""

    g1,g2,g3=st.columns(3)
    with g1: st.markdown(gauge(comp,"Completeness",cc,"✅"),unsafe_allow_html=True)
    with g2: st.markdown(gauge(uniq,"Uniqueness",uc,"🔷"),unsafe_allow_html=True)
    with g3: st.markdown(gauge(dq,"DQ Score",dc,"🏅"),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    rows_html=""
    for p in profiles:
        cc2=col_c(p["completeness"]); uc2=col_c(p["uniqueness"])
        rows_html+=f"""<tr>
          <td style="font-weight:600;font-family:'IBM Plex Mono',monospace;font-size:0.75rem">{p['col']}</td>
          <td><span style="background:#dbeafe;color:#1d4ed8;padding:2px 7px;border-radius:10px;font-size:0.64rem;font-weight:700">{p['ctype']}</span></td>
          <td>{mini_bar(p['completeness'],cc2)}</td>
          <td style="color:var(--muted);font-size:0.78rem">{p['null_c']:,}</td>
          <td>{mini_bar(p['uniqueness'],uc2)}</td>
          <td style="color:var(--muted);font-size:0.78rem">{p['unique_c']:,}</td>
        </tr>"""
    st.markdown(f"""<div style="background:var(--card);border:1.5px solid var(--border);border-radius:12px;overflow-x:auto;box-shadow:var(--shadow)">
      <table class="prof-tbl"><thead><tr>
        <th>COLUMN</th><th>TYPE</th><th>COMPLETENESS</th><th>EMPTY</th><th>UNIQUENESS</th><th>UNIQUE</th>
      </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    sel=st.selectbox("🔍 Column detail:",[ p["col"] for p in profiles],key=f"psel_{label}")
    p=next((x for x in profiles if x["col"]==sel),None)
    if not p: return
    d1,d2=st.columns(2,gap="large")
    with d1:
        cc2=col_c(p["completeness"])
        st.markdown(f"""<div class="card"><div class="card-title">🏥 Health</div>
          <div style="font-size:0.83rem;line-height:2.3">
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
              <span style="color:var(--muted)">Completeness</span><b style="color:{cc2}">{p['completeness']}%</b></div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
              <span style="color:var(--muted)">Uniqueness</span><b>{p['uniqueness']}%</b></div>
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
              <span style="color:var(--muted)">Empty values</span><b style="color:#dc2626">{p['null_c']:,}</b></div>
            <div style="display:flex;justify-content:space-between;padding:1px 0">
              <span style="color:var(--muted)">Data type</span><b>{p['dtype']}</b></div>
          </div></div>""", unsafe_allow_html=True)
    with d2:
        if p["ctype"]=="Numeric" and p["mean"] is not None:
            st.markdown(f"""<div class="card"><div class="card-title">📈 Statistics</div>
              <div style="font-size:0.83rem;line-height:2.3">
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
                  <span style="color:var(--muted)">Min / Max</span><b>{p['min']:,} / {p['max']:,}</b></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
                  <span style="color:var(--muted)">Mean</span><b style="color:var(--blue-mid)">{p['mean']:,}</b></div>
                <div style="display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9;padding:1px 0">
                  <span style="color:var(--muted)">Median</span><b>{p['median']:,}</b></div>
                <div style="display:flex;justify-content:space-between;padding:1px 0">
                  <span style="color:var(--muted)">Std Dev</span><b>{p['std']:,}</b></div>
              </div></div>""", unsafe_allow_html=True)
        elif p["top_values"]:
            max_c=p["top_values"][0][1]
            bars=""
            PAL=["#2563eb","#3b82f6","#60a5fa","#93c5fd","#bfdbfe"]
            for ii,(val,cnt) in enumerate(p["top_values"]):
                bw=int(cnt/max_c*100); pct2=cnt/n*100 if n else 0
                bars+=f"""<div style="margin-bottom:8px">
                  <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                    <span style="font-size:0.79rem;font-weight:600;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{val}</span>
                    <span style="font-size:0.72rem;color:var(--muted)">{cnt:,} ({pct2:.1f}%)</span></div>
                  <div style="height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden">
                    <div style="width:{bw}%;height:100%;background:{PAL[ii]};border-radius:3px"></div></div></div>"""
            st.markdown(f'<div class="card"><div class="card-title">🏆 Top Values</div>{bars}</div>',unsafe_allow_html=True)

    # Export
    out=io.BytesIO()
    rows_exp=[{"Column":p2["col"],"Type":p2["ctype"],"Completeness%":p2["completeness"],
               "Empty":p2["null_c"],"Unique":p2["unique_c"],"Uniqueness%":p2["uniqueness"]}
              for p2 in profiles]
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        pd.DataFrame(rows_exp).to_excel(w, sheet_name="Profile", index=False)
    out.seek(0)
    st.download_button("⬇️ Download Profile", data=out, file_name=f"profile_{label}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key=f"dlp_{label}")


# ──────────────────────────────────────────────────────────────────────────────
# MATCHING ENGINE
# ──────────────────────────────────────────────────────────────────────────────
def run_matching(files_dfs, rules, prog=None):
    results=[]
    pairs=[(i,j) for i in range(len(files_dfs)) for j in range(i,len(files_dfs))]
    total=sum(len(files_dfs[i][1])*(len(files_dfs[j][1]) if i!=j else len(files_dfs[j][1])) for i,j in pairs) or 1
    done=0
    for rule in rules:
        for fi,fj in pairs:
            li,dfi=files_dfs[fi]; lj,dfj=files_dfs[fj]
            cfgi=[c for c in rule["columns"] if c["file_idx"]==fi]
            cfgj=[c for c in rule["columns"] if c["file_idx"]==fj]
            if not cfgi or not cfgj: continue
            ki=[[normalize_text(str(dfi[c["col"]].iloc[r]) if c["col"] in dfi.columns else "") for c in cfgi] for r in range(len(dfi))]
            kj=[[normalize_text(str(dfj[c["col"]].iloc[r]) if c["col"] in dfj.columns else "") for c in cfgj] for r in range(len(dfj))]
            same=(fi==fj)
            for ii in range(len(dfi)):
                if prog and done%150==0: prog.progress(min(done/total,.99))
                done+=1
                if not any(ki[ii]): continue
                for jj in range(ii+1 if same else 0, len(dfj)):
                    if not any(kj[jj]): continue
                    scores=[]; ok=True
                    for k,(ci,cj) in enumerate(zip(cfgi,cfgj)):
                        a,b=ki[ii][k],kj[jj][k]
                        sc=100 if ci["match_type"]=="exact" else fuzz.token_sort_ratio(a,b)
                        scores.append(sc)
                        if sc<ci["threshold"]: ok=False; break
                    if not ok: continue
                    avg=round(sum(scores)/len(scores))
                    rec={"Rule":rule["name"],"Rule_Merge":rule.get("merge_mode","auto"),
                         "Sys_A":li,"Row_A":ii+2,"Sys_B":lj,"Row_B":jj+2,
                         "Avg_Score":avg,"Status":"Exact Match" if avg==100 else "Similar",
                         "_fi":fi,"_fj":fj,"_ri":ii,"_rj":jj}
                    for k,ci in enumerate(cfgi):
                        rec[f"A:{ci['col']}"]=str(dfi[ci["col"]].iloc[ii]) if ci["col"] in dfi.columns else ""
                    for k,cj in enumerate(cfgj):
                        rec[f"B:{cj['col']}"]=str(dfj[cj["col"]].iloc[jj]) if cj["col"] in dfj.columns else ""
                    results.append(rec)
    if prog: prog.progress(1.0)
    return pd.DataFrame(results) if results else pd.DataFrame()

def build_clusters(res_df, files_dfs):
    if res_df is None or len(res_df)==0: return []
    parent={}
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x: parent[x]=find(parent[x])
        return parent[x]
    def union(x,y): parent[find(x)]=find(y)
    smap={}; rmap={}
    for _,row in res_df.iterrows():
        a=(int(row["_fi"]),int(row["_ri"])); b=(int(row["_fj"]),int(row["_rj"]))
        union(a,b); key=tuple(sorted([a,b]))
        smap[key]=max(smap.get(key,0),int(row["Avg_Score"]))
        rmap[key]=row.get("Rule_Merge","auto")
    groups=defaultdict(set)
    for node in parent: groups[find(node)].add(node)
    clusters=[]
    for _,members in groups.items():
        members=sorted(members); max_sc=0; has_manual=False
        for ii,a in enumerate(members):
            for b in members[ii+1:]:
                key=tuple(sorted([a,b]))
                max_sc=max(max_sc,smap.get(key,0))
                if rmap.get(key)=="manual": has_manual=True
        records=[]
        for fi,ri in members:
            lbl,df=files_dfs[fi]
            records.append({"source_label":lbl,"file_idx":fi,"row_idx":ri,
                            "data":df.iloc[ri].to_dict() if ri<len(df) else {}})
        clusters.append({"members":members,"max_score":max_sc,"records":records,
                         "merge_mode":"manual" if has_manual else "auto"})
    clusters.sort(key=lambda x:-x["max_score"])
    return clusters

def pick_golden(records, trust_ranking):
    all_cols=set()
    for r in records: all_cols.update(r["data"].keys())
    golden={}
    for col in all_cols:
        ranking=trust_ranking.get(col,[r["source_label"] for r in records])
        chosen=None
        for lbl in ranking:
            for r in records:
                if r["source_label"]==lbl:
                    val=r["data"].get(col,"")
                    if str(val).strip() not in ("","nan","None"): chosen=val; break
            if chosen is not None: break
        golden[col]=chosen if chosen is not None else (records[0]["data"].get(col,"") if records else "")
    return golden


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFS={"step":1,"files_dfs":[],"rules":[],"results_df":None,"clusters":None,
      "trust_ranking":{},"golden_records":{},"steward_decisions":{},"steward_overrides":{},"final_df":None}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v

step=st.session_state.step


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
STEPS_NAV=[("1","📂","Data Sources"),("2","⚙️","Match Rules"),("3","🔍","Results & Profile"),
           ("4","🔀","Merge Setup"),("5","👤","Steward Review"),("6","🏅","Export")]

with st.sidebar:
    st.markdown("""<div style="padding:14px 8px 6px 8px">
      <div style="font-size:1rem;font-weight:900;color:#1d4ed8;letter-spacing:-0.02em">🏅 Golden Data</div>
      <div style="font-size:0.7rem;color:#94a3b8;margin-top:2px">Master Data Management</div>
    </div><hr style="border:none;border-top:1px solid #e2e8f0;margin:8px 0">""", unsafe_allow_html=True)
    for num,icon,name in STEPS_NAV:
        n=int(num)
        cls="nav-active" if n==step else "nav-done" if n<step else ""
        dc="nd-active" if n==step else "nd-done" if n<step else ""
        pfx="✓" if n<step else num
        st.markdown(f'<div class="nav-item {cls}"><span class="nav-dot {dc}"></span>{icon} {name}</div>',unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:10px 0">',unsafe_allow_html=True)
    if st.button("🔄 New Session", use_container_width=True):
        for k,v in DEFS.items(): st.session_state[k]=v
        st.rerun()
    if st.session_state.files_dfs:
        tot=sum(len(df) for _,df in st.session_state.files_dfs)
        ns=len(st.session_state.files_dfs)
        nc2=len(st.session_state.clusters) if st.session_state.clusters else 0
        st.markdown(f"""<div style="margin-top:12px;background:#eff6ff;border:1px solid #bfdbfe;
          border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:1.3rem;font-weight:900;color:#2563eb">{tot:,}</div>
          <div style="font-size:0.68rem;color:#64748b">Total Records</div>
          <div style="font-size:0.78rem;font-weight:700;color:#475569;margin-top:3px">{ns} Systems{f' · {nc2} Clusters' if nc2 else ''}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
tr=sum(len(df) for _,df in st.session_state.files_dfs)
ns=len(st.session_state.files_dfs)
nc3=len(st.session_state.clusters) if st.session_state.clusters else 0
ng=len(st.session_state.golden_records)
badges=""
if tr:  badges+=f'<div class="hero-stat"><span class="hv">{tr:,}</span>Records</div>'
if ns:  badges+=f'<div class="hero-stat"><span class="hv">{ns}</span>Systems</div>'
if nc3: badges+=f'<div class="hero-stat"><span class="hv">{nc3}</span>Clusters</div>'
if ng:  badges+=f'<div class="hero-stat"><span class="hv">{ng}</span>Golden</div>'

st.markdown(f"""<div class="hero">
  <div class="hero-icon">🏅</div>
  <div class="hero-text">
    <h1>Golden Data MDM</h1>
    <p class="sub">Master Data Management · Multi-System Integration · Golden Record Engine</p>
    <p class="tag">✦ Let's Master your Data ✦</p>
  </div>
  {"<div class='hero-stats'>"+badges+"</div>" if badges else ""}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — DATA SOURCES
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.markdown('<div class="page-title">📂 Data Sources</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Connect your source systems — each system can be a file upload or a database reference</div>',unsafe_allow_html=True)

    col_main,col_side=st.columns([2.2,1],gap="large")
    with col_main:
        st.markdown('<div class="card"><div class="card-title">⚙️ Source Configuration</div>',unsafe_allow_html=True)
        num_sys=st.number_input("Number of source systems:",min_value=1,max_value=10,value=2,step=1)
        new_files=[]
        for i in range(int(num_sys)):
            st.markdown(f'<div class="sys-block"><div class="sys-block-title">System {i+1}</div>',unsafe_allow_html=True)
            c1,c2,c3=st.columns([1.8,1.6,0.9])
            with c1: sys_name=st.text_input("System name:",value=f"System_{i+1}",key=f"sn_{i}",placeholder="e.g. CRM, ERP, Oracle")
            with c2: src_type=st.selectbox("Source type:",["📄 File Upload","🗄️ Database System"],key=f"st_{i}")
            with c3: icon=st.selectbox("Icon:",["🏢","💾","🗄️","📊","☁️","🔧","📡","🏭"],key=f"ic_{i}")

            if "File" in src_type:
                up=st.file_uploader(f"Upload file for **{sys_name}**:",type=["csv","xlsx","xls","json"],key=f"up_{i}")
                if up:
                    df=read_file(up)
                    if df is not None:
                        new_files.append((sys_name,df))
                        c=src_color(sys_name)
                        st.markdown(f"""<div style="background:{c}0d;border:1px solid {c}30;border-radius:8px;
                          padding:8px 12px;margin-top:6px;display:flex;align-items:center;gap:8px">
                          <span>{icon}</span>
                          <div><b style="color:{c}">{sys_name}</b>
                          <span style="color:var(--muted);font-size:0.76rem"> · {len(df):,} rows · {len(df.columns)} columns · {', '.join(list(df.columns)[:4])}{'…' if len(df.columns)>4 else ''}</span></div>
                        </div>""", unsafe_allow_html=True)
                    else: st.error(f"Could not read file for {sys_name}")
            else:
                st.markdown(f"""<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:8px;padding:8px 12px;margin-top:4px">
                  <span style="font-size:0.78rem;color:#92400e">🗄️ <b>Database Reference</b> — upload an exported file (CSV/Excel) from your {sys_name} system</span>
                </div>""", unsafe_allow_html=True)
                up=st.file_uploader(f"Upload export from {sys_name}:",type=["csv","xlsx","xls","json"],key=f"up_db_{i}")
                if up:
                    df=read_file(up)
                    if df is not None:
                        new_files.append((sys_name,df))
                        c=src_color(sys_name)
                        st.markdown(f"""<div style="background:{c}0d;border:1px solid {c}30;border-radius:8px;
                          padding:8px 12px;margin-top:6px;display:flex;align-items:center;gap:8px">
                          <span>{icon}</span><b style="color:{c}">{sys_name}</b>
                          <span style="color:var(--muted);font-size:0.76rem">{len(df):,} rows</span>
                        </div>""", unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("▶ Continue to Match Rules →",use_container_width=True):
            if not new_files: st.error("Please upload at least one file.")
            else:
                st.session_state.files_dfs=new_files
                for k in ["rules","results_df","clusters","golden_records","steward_decisions","steward_overrides","final_df"]:
                    st.session_state[k]=[] if k=="rules" else {} if k in ["golden_records","steward_decisions","steward_overrides"] else None
                st.session_state.step=2; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    with col_side:
        st.markdown("""<div class="card"><div class="card-title">📋 What is MDM?</div>
          <p style="font-size:0.81rem;color:#475569;line-height:2.1;margin:0">
            <b>Master Data Management</b> unifies:<br>
            🔗 Data from multiple systems<br>
            🔍 Configurable matching rules<br>
            🏅 Golden (authoritative) records<br>
            👤 Data steward review workflow<br>
            ⬇️ Clean, unified master export
          </p></div>
          <div class="card"><div class="card-title">📁 Supported Formats</div>
          <p style="font-size:0.81rem;color:#475569;line-height:2.1;margin:0">
            📄 CSV files<br>📊 Excel (.xlsx / .xls)<br>🗂️ JSON files<br>
            🗄️ Database exports (SAP, Oracle, SQL Server, Salesforce…)
          </p></div>""", unsafe_allow_html=True)
        if st.session_state.files_dfs:
            st.markdown('<div class="card"><div class="card-title">✅ Connected Systems</div>',unsafe_allow_html=True)
            for lbl,df in st.session_state.files_dfs:
                c=src_color(lbl)
                st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                            f'{src_badge(lbl)}<span style="font-size:0.76rem;color:var(--muted)">{len(df):,} rows · {len(df.columns)} cols</span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — MATCH RULES
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    fds=st.session_state.files_dfs
    if not fds:
        st.warning("Please go back and upload files first.")
        if st.button("← Back"): st.session_state.step=1; st.rerun()
        st.stop()

    st.markdown('<div class="page-title">⚙️ Match Rules</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Define rules to detect duplicate or matching records across systems. Each rule has its own merge strategy.</div>',unsafe_allow_html=True)

    num_r=st.number_input("Number of matching rules:",min_value=1,max_value=8,
                           value=max(1,len(st.session_state.rules)),step=1)
    rules=[]
    for r_idx in range(int(num_r)):
        prev_name=st.session_state.rules[r_idx]["name"] if r_idx<len(st.session_state.rules) else f"Rule_{r_idx+1}"
        prev_merge=st.session_state.rules[r_idx].get("merge_mode","auto") if r_idx<len(st.session_state.rules) else "auto"
        with st.expander(f"📌 Rule {r_idx+1} — {prev_name}",expanded=(r_idx==0)):
            rc1,rc2,rc3=st.columns([2,1.4,1.2])
            with rc1: rname=st.text_input("Rule name:",value=prev_name,key=f"rn_{r_idx}")
            with rc2:
                midx=0 if prev_merge=="auto" else 1
                mchoice=st.selectbox("Merge mode:",["🤖 Auto Merge","👤 Manual (Steward Review)"],index=midx,key=f"rm_{r_idx}")
                rmerge="auto" if "Auto" in mchoice else "manual"
            with rc3:
                if rmerge=="auto":
                    st.markdown('<br><span class="rb-auto">⚡ Auto — instant merge</span>',unsafe_allow_html=True)
                else:
                    st.markdown('<br><span class="rb-man">👤 Steward must approve</span>',unsafe_allow_html=True)

            nc_r=st.number_input("Number of matching columns:",min_value=1,max_value=6,value=1,step=1,key=f"nc_{r_idx}")
            rcols=[]
            for c_idx in range(int(nc_r)):
                st.markdown(f"<div style='background:#f8faff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin:6px 0'>"
                            f"<div style='font-size:0.67rem;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px'>Match Column {c_idx+1}</div>",unsafe_allow_html=True)
                for fi,(lbl,df) in enumerate(fds):
                    x1,x2,x3,x4=st.columns([1.4,2.2,1.2,0.9])
                    with x1: st.markdown(f"{src_badge(lbl)}",unsafe_allow_html=True)
                    with x2: sel=st.selectbox("Column:",list(df.columns),key=f"rc_{r_idx}_{c_idx}_{fi}")
                    with x3: mt=st.selectbox("Method:",["Fuzzy","Exact"],key=f"mt_{r_idx}_{c_idx}_{fi}")
                    with x4:
                        if mt=="Fuzzy": thr=st.slider("Threshold:",50,100,80,5,key=f"thr_{r_idx}_{c_idx}_{fi}")
                        else: thr=100; st.markdown("<br><b style='color:#16a34a;font-size:0.8rem'>100%</b>",unsafe_allow_html=True)
                    rcols.append({"file_idx":fi,"col":sel,"match_type":mt.lower(),"threshold":thr})
                st.markdown("</div>",unsafe_allow_html=True)
            rules.append({"name":rname,"merge_mode":rmerge,"columns":rcols})

    st.markdown("<br>",unsafe_allow_html=True)
    b1,b2=st.columns(2)
    with b1:
        if st.button("← Back to Sources",use_container_width=True): st.session_state.step=1; st.rerun()
    with b2:
        if st.button("🚀 Run Matching →",use_container_width=True):
            st.session_state.rules=rules; st.session_state.results_df=None
            st.session_state.clusters=None; st.session_state.step=3; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — RESULTS + DATA PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    fds=st.session_state.files_dfs; rules=st.session_state.rules
    if not fds or not rules:
        st.warning("Please configure files and rules first.")
        if st.button("← Back"): st.session_state.step=2; st.rerun()
        st.stop()

    if st.session_state.results_df is None:
        st.markdown('<div class="card"><div style="font-size:1.1rem;font-weight:800;margin-bottom:12px">⏳ Running Matching Engine…</div>',unsafe_allow_html=True)
        prog=st.progress(0); status=st.empty()
        status.text("🔄 Preparing data…"); time.sleep(0.2)
        try:
            status.text("🔍 Comparing records across rules and systems…")
            results=run_matching(fds, rules, prog)
            st.session_state.results_df=results
            status.text("🧩 Building clusters…")
            st.session_state.clusters=build_clusters(results, fds)
            status.text("✅ Done!")
            time.sleep(0.3)
        except Exception as e:
            st.error(f"❌ Error: {e}"); st.stop()
        st.markdown("</div>",unsafe_allow_html=True)
        st.rerun()

    results=st.session_state.results_df
    clusters=st.session_state.clusters or []
    total_m=len(results)
    exact_m=int((results["Status"]=="Exact Match").sum()) if total_m else 0
    auto_cl=sum(1 for c in clusters if c["merge_mode"]=="auto")
    man_cl =sum(1 for c in clusters if c["merge_mode"]=="manual")

    st.markdown('<div class="page-title">🔍 Match Results & Data Profile</div>',unsafe_allow_html=True)
    st.markdown(f"""<div class="mrow mrow-4">
      <div class="mc"><div class="val">{total_m:,}</div><div class="lbl">Match Pairs</div></div>
      <div class="mc r"><div class="val" style="color:#dc2626">{exact_m:,}</div><div class="lbl">Exact Matches</div></div>
      <div class="mc g"><div class="val" style="color:#16a34a">{auto_cl}</div><div class="lbl">Auto Clusters</div></div>
      <div class="mc o"><div class="val" style="color:#d97706">{man_cl}</div><div class="lbl">Manual Clusters</div></div>
    </div>""", unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(["🔗 Matched Pairs (Token View)","🧩 Clusters","📊 Data Profile"])

    with tab1:
        if total_m>0:
            node_to_cl={node:i for i,cl in enumerate(clusters) for node in cl["members"]}
            tokens=[]
            for _,row in results.iterrows():
                key=(int(row["_fi"]),int(row["_ri"]))
                ci=node_to_cl.get(key,-1)
                tokens.append(f"TKN-{ci+1:04d}" if ci>=0 else "—")

            pairs_df=results.copy()
            pairs_df.insert(0,"Token",tokens)
            disp=pairs_df[[c for c in pairs_df.columns if not c.startswith("_")]].sort_values("Token")

            st.markdown('<div class="ib ib-bl">Each <b>Token</b> is a unique Match Group ID. Rows sharing the same token belong to the same cluster of duplicates. They are grouped together below.</div>',unsafe_allow_html=True)

            # Group by token
            token_rows={}
            for _,row in disp.iterrows():
                t=row["Token"]
                if t not in token_rows: token_rows[t]=[]
                token_rows[t].append(row)

            for token,rows in list(token_rows.items())[:120]:
                rm=rows[0].get("Rule_Merge","auto") if "Rule_Merge" in rows[0].index else "auto"
                ml=f'<span class="rb-auto">⚡ Auto</span>' if rm=="auto" else f'<span class="rb-man">👤 Manual</span>'
                rule_name=rows[0].get("Rule","") if "Rule" in rows[0].index else ""
                st.markdown(f"""<div class="pg">
                  <div class="pg-hdr">
                    <span class="token-badge">{token}</span>
                    <span style="font-size:0.78rem;color:var(--muted)">{len(rows)} pair(s)</span>
                    {ml}
                    <span style="font-size:0.72rem;color:var(--muted2);margin-left:auto">📌 {rule_name}</span>
                  </div>""", unsafe_allow_html=True)
                for row in rows:
                    vcols=[c for c in row.index if c.startswith("A:") or c.startswith("B:")]
                    vals=" &nbsp;·&nbsp; ".join([f"<span style='color:var(--muted);font-size:0.72rem'>{c}:</span> <b style='font-size:0.8rem'>{row[c]}</b>" for c in vcols[:5]])
                    sc2=int(row["Avg_Score"])
                    st.markdown(f"""<div class="pg-row">
                      {src_badge(str(row.get("Sys_A","A")))} → {src_badge(str(row.get("Sys_B","B")))}
                      <span style="flex:1;min-width:0">{vals}</span>
                      {sp(sc2)}
                    </div>""", unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)

            if len(token_rows)>120: st.info(f"Showing 120 of {len(token_rows)} token groups.")
            out=io.BytesIO()
            with pd.ExcelWriter(out,engine='openpyxl') as w: disp.to_excel(w,sheet_name="Match Pairs",index=False)
            out.seek(0)
            st.download_button("⬇️ Download All Match Pairs",data=out,file_name="match_pairs.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("No matches found. Try lowering thresholds or adjusting rules.")

    with tab2:
        if clusters:
            st.markdown(f"""<div class="mrow mrow-3">
              <div class="mc"><div class="val">{len(clusters)}</div><div class="lbl">Total Clusters</div></div>
              <div class="mc g"><div class="val" style="color:#16a34a">{auto_cl}</div><div class="lbl">Auto Merge</div></div>
              <div class="mc o"><div class="val" style="color:#d97706">{man_cl}</div><div class="lbl">Needs Review</div></div>
            </div>""", unsafe_allow_html=True)
            for i,cl in enumerate(clusters[:60]):
                sc_cls="sp-hi" if cl["max_score"]>=90 else "sp-mid" if cl["max_score"]>=70 else "sp-lo"
                mb='<span class="rb-auto">⚡ Auto</span>' if cl["merge_mode"]=="auto" else '<span class="rb-man">👤 Manual</span>'
                st.markdown(f"""<div class="cl-card">
                  <div class="cl-header">
                    <span class="cl-id">GRP-{i+1:03d}</span>
                    <span class="token-badge">TKN-{i+1:04d}</span>
                    <span class="sp {sc_cls}">{cl['max_score']}%</span> {mb}
                    <span style="font-size:0.76rem;color:var(--muted);margin-left:auto">{len(cl['records'])} records</span>
                  </div>""", unsafe_allow_html=True)
                for rec in cl["records"]:
                    fv=list(rec["data"].values())[0] if rec["data"] else "—"
                    st.markdown(f"""<div class="rec-row">
                      {src_badge(rec["source_label"])}
                      <span style="color:var(--muted);font-size:0.76rem">Row {rec["row_idx"]+2}:</span>
                      <b>{fv}</b></div>""", unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
        else:
            st.info("No clusters found.")

    with tab3:
        sys_tabs=st.tabs([lbl for lbl,_ in fds])
        for ti,(tab,(lbl,df)) in enumerate(zip(sys_tabs,fds)):
            with tab: render_profile(df,label=lbl)

    st.markdown("<br>",unsafe_allow_html=True)
    b1,b2=st.columns(2)
    with b1:
        if st.button("← Back to Rules",use_container_width=True): st.session_state.step=2; st.rerun()
    with b2:
        if st.button("▶ Configure Merge →",use_container_width=True): st.session_state.step=4; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — MERGE SETUP (Trust Ranking)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    fds=st.session_state.files_dfs; clusters=st.session_state.clusters or []
    if not fds or not clusters:
        st.warning("Please run matching first.")
        if st.button("← Back"): st.session_state.step=3; st.rerun()
        st.stop()

    file_labels=[lbl for lbl,_ in fds]
    all_cols=get_all_cols(fds)
    auto_cl=sum(1 for c in clusters if c["merge_mode"]=="auto")
    man_cl =sum(1 for c in clusters if c["merge_mode"]=="manual")

    st.markdown('<div class="page-title">🔀 Merge Setup</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Set system trust ranking per column — the highest-ranked system with a non-empty value becomes the golden record source.</div>',unsafe_allow_html=True)

    st.markdown(f"""<div class="mrow mrow-3">
      <div class="mc"><div class="val">{len(clusters)}</div><div class="lbl">Total Clusters</div></div>
      <div class="mc g"><div class="val" style="color:#16a34a">{auto_cl}</div><div class="lbl">Auto (instant)</div></div>
      <div class="mc o"><div class="val" style="color:#d97706">{man_cl}</div><div class="lbl">Manual Review</div></div>
    </div>""", unsafe_allow_html=True)

    if auto_cl: st.markdown('<div class="ib ib-gr"><b>⚡ Auto clusters</b> will merge immediately using the ranking below — no review step needed.</div>',unsafe_allow_html=True)
    if man_cl:  st.markdown('<div class="ib ib-gd"><b>👤 Manual clusters</b> will go to the Steward Review stage for field-by-field approval before merging.</div>',unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">🏆 System Trust Ranking — Per Column</div>',unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.83rem;color:var(--muted);margin-bottom:16px">For each column, select systems in order of trust (first = most trusted). Auto merge picks the value from the highest-ranked system that has a non-empty value.</p>',unsafe_allow_html=True)

    trust_ranking={}
    for col in all_cols:
        st.markdown(f"<b style='font-size:0.84rem'>`{col}`</b>",unsafe_allow_html=True)
        prev_order=st.session_state.trust_ranking.get(col, file_labels)
        # Ensure all labels are in list
        valid_prev=[l for l in prev_order if l in file_labels]
        for l in file_labels:
            if l not in valid_prev: valid_prev.append(l)
        ordered=st.multiselect(f"Rank for **{col}** (select in order, 1st = most trusted):",
                                options=file_labels, default=valid_prev, key=f"tr_{col}")
        full=ordered+[l for l in file_labels if l not in ordered]
        trust_ranking[col]=full
        rank_html=""
        for ri,lbl in enumerate(full):
            c=src_color(lbl)
            rank_html+=f"""<span style="display:inline-flex;align-items:center;gap:4px;
              background:{c}10;border:1px solid {c}28;border-radius:8px;padding:3px 10px;
              margin-right:5px;margin-bottom:4px;font-size:0.76rem;font-weight:700;color:{c}">
              <span style="background:{c};color:#fff;border-radius:50%;width:15px;height:15px;
                display:inline-flex;align-items:center;justify-content:center;font-size:0.62rem;font-weight:900">{ri+1}</span>
              {lbl}</span>"""
        st.markdown(f'<div style="margin-bottom:4px">{rank_html}</div>',unsafe_allow_html=True)
        st.markdown('<hr class="section-div">',unsafe_allow_html=True)

    st.session_state.trust_ranking=trust_ranking
    st.markdown("</div>",unsafe_allow_html=True)

    b1,b2=st.columns(2)
    with b1:
        if st.button("← Back to Results",use_container_width=True): st.session_state.step=3; st.rerun()
    with b2:
        btn="⚡ Apply Ranking & Review Manual →" if man_cl else "⚡ Auto-Generate All Golden Records →"
        if st.button(btn,use_container_width=True):
            # Immediately merge auto clusters
            gr={}
            for i,cl in enumerate(clusters):
                if cl["merge_mode"]=="auto":
                    gr[i]=pick_golden(cl["records"],trust_ranking)
            st.session_state.golden_records=gr
            if man_cl>0:
                st.session_state.steward_decisions={i:"pending" for i,cl in enumerate(clusters) if cl["merge_mode"]=="manual"}
                st.session_state.steward_overrides={}
                st.session_state.step=5
            else:
                st.session_state.step=6
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — STEWARD REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif step == 5:
    clusters=st.session_state.clusters or []
    decisions=st.session_state.steward_decisions
    overrides=st.session_state.steward_overrides
    all_cols=get_all_cols(st.session_state.files_dfs)
    manual_cls=[(i,cl) for i,cl in enumerate(clusters) if cl["merge_mode"]=="manual"]

    if not manual_cls:
        st.info("No manual clusters to review.")
        if st.button("▶ Go to Export"): st.session_state.step=6; st.rerun()
        st.stop()

    approved=sum(1 for v in decisions.values() if v=="approve")
    rejected=sum(1 for v in decisions.values() if v=="reject")
    pending =sum(1 for v in decisions.values() if v=="pending")

    st.markdown('<div class="page-title">👤 Data Steward Review</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Review each flagged cluster. Select the best value per field and approve or reject the merge.</div>',unsafe_allow_html=True)

    st.markdown(f"""<div class="mrow mrow-4">
      <div class="mc"><div class="val">{len(manual_cls)}</div><div class="lbl">For Review</div></div>
      <div class="mc g"><div class="val" style="color:#16a34a">{approved}</div><div class="lbl">Approved</div></div>
      <div class="mc r"><div class="val" style="color:#dc2626">{rejected}</div><div class="lbl">Rejected</div></div>
      <div class="mc o"><div class="val" style="color:#d97706">{pending}</div><div class="lbl">Pending</div></div>
    </div>""", unsafe_allow_html=True)

    pct=(approved+rejected)/len(manual_cls)*100 if manual_cls else 0
    bar_color="#16a34a" if pct==100 else "#2563eb"
    st.markdown(f"""<div style="background:#e2e8f0;border-radius:6px;height:8px;margin-bottom:16px">
      <div style="width:{pct:.0f}%;height:100%;background:{bar_color};border-radius:6px;transition:width .3s"></div>
    </div>""", unsafe_allow_html=True)

    filt=st.radio("Filter:",["All","⏳ Pending","✅ Approved","❌ Rejected"],horizontal=True)
    st.markdown("<br>",unsafe_allow_html=True)

    for i,cl in manual_cls:
        d=decisions.get(i,"pending")
        if filt=="⏳ Pending" and d!="pending": continue
        if filt=="✅ Approved" and d!="approve": continue
        if filt=="❌ Rejected" and d!="reject": continue

        icon="✅" if d=="approve" else "❌" if d=="reject" else "⏳"
        sbadge=f'<span class="sb-app">Approved</span>' if d=="approve" else \
               f'<span class="sb-rej">Rejected</span>' if d=="reject" else \
               f'<span class="sb-pnd">Pending</span>'

        with st.expander(f"{icon}  GRP-{i+1:03d} · TKN-{i+1:04d} · {len(cl['records'])} records · Score {cl['max_score']}%",expanded=(d=="pending")):
            st.markdown(sbadge,unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)

            # Side-by-side record comparison
            nr=min(len(cl["records"]),4)
            rec_cols=st.columns(nr)
            for r_idx,rec in enumerate(cl["records"][:4]):
                with rec_cols[r_idx]:
                    c=src_color(rec["source_label"])
                    st.markdown(f"""<div style="background:{c}08;border:1.5px solid {c}22;
                        border-radius:10px;padding:12px 13px">
                      <div style="font-size:0.67rem;font-weight:800;color:{c};text-transform:uppercase;
                        letter-spacing:.08em;margin-bottom:8px">{rec['source_label']}<br>Row {rec['row_idx']+2}</div>""",unsafe_allow_html=True)
                    for col in all_cols:
                        val=rec["data"].get(col,"")
                        empty=str(val).strip() in ("","nan","None")
                        vc="#94a3b8" if empty else "#0f172a"
                        disp="—" if empty else str(val)
                        fw="400" if empty else "600"
                        st.markdown(f"""<div style="margin-bottom:6px">
                          <div style="font-size:0.66rem;color:#94a3b8;font-weight:600">{col}</div>
                          <div style="font-size:0.81rem;color:{vc};font-weight:{fw}">{disp}</div>
                        </div>""",unsafe_allow_html=True)
                    st.markdown("</div>",unsafe_allow_html=True)

            st.markdown('<hr class="section-div">',unsafe_allow_html=True)
            st.markdown("**🏅 Build Golden Record — select best value per column:**",unsafe_allow_html=True)

            ov_vals=overrides.get(i,{})
            new_ov={}
            for col in all_cols:
                opts={}
                for rec in cl["records"]:
                    v=str(rec["data"].get(col,""))
                    if v.strip() not in ("","nan","None"):
                        opts[f"[{rec['source_label']}]  {v}"]=v
                opts["✏️ Custom value…"]="__custom__"
                ok_list=list(opts.keys())
                cur_idx=0
                if col in ov_vals:
                    for ki,(k,v) in enumerate(opts.items()):
                        if v==ov_vals[col]: cur_idx=ki; break
                oc1,oc2=st.columns([3,1])
                with oc1:
                    sel=st.selectbox(f"{col}:",ok_list,index=cur_idx,key=f"ov_{i}_{col}")
                with oc2:
                    if opts.get(sel)=="__custom__":
                        cv=st.text_input("Value:",value=ov_vals.get(col,""),key=f"cv_{i}_{col}")
                        new_ov[col]=cv
                    else:
                        new_ov[col]=opts.get(sel,"")
                        st.markdown("<br><span style='color:#16a34a;font-size:0.95rem'>✓</span>",unsafe_allow_html=True)

            overrides[i]=new_ov
            st.session_state.steward_overrides=overrides

            st.markdown("<br>",unsafe_allow_html=True)
            a1,a2,a3=st.columns(3)
            with a1:
                if st.button(f"✅ Approve",key=f"app_{i}",use_container_width=True):
                    decisions[i]="approve"; overrides[i]=new_ov
                    st.session_state.steward_decisions=decisions
                    st.session_state.steward_overrides=overrides; st.rerun()
            with a2:
                if st.button(f"❌ Reject",key=f"rej_{i}",use_container_width=True):
                    decisions[i]="reject"
                    st.session_state.steward_decisions=decisions; st.rerun()
            with a3:
                if d!="pending":
                    if st.button("🔄 Reset",key=f"rst_{i}",use_container_width=True):
                        decisions[i]="pending"
                        st.session_state.steward_decisions=decisions; st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)
    b1,b2,b3=st.columns(3)
    with b1:
        if st.button("← Back to Merge Setup",use_container_width=True): st.session_state.step=4; st.rerun()
    with b2:
        if st.button("⚡ Approve All Pending",use_container_width=True):
            for i,cl in manual_cls:
                if decisions.get(i,"pending")=="pending":
                    decisions[i]="approve"
                    if i not in overrides or not overrides[i]:
                        overrides[i]=pick_golden(cl["records"],st.session_state.trust_ranking)
            st.session_state.steward_decisions=decisions
            st.session_state.steward_overrides=overrides; st.rerun()
    with b3:
        if st.button("▶ Finalize & Export →",use_container_width=True):
            gr=dict(st.session_state.golden_records)
            for i,cl in manual_cls:
                if decisions.get(i)=="approve":
                    ov=overrides.get(i)
                    if ov:
                        gr[i]=ov
                    else:
                        gr[i]=pick_golden(cl["records"],st.session_state.trust_ranking)
            st.session_state.golden_records=gr
            st.session_state.step=6; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
elif step == 6:
    fds=st.session_state.files_dfs; clusters=st.session_state.clusters or []
    gr=st.session_state.golden_records; decisions=st.session_state.steward_decisions
    if not clusters:
        st.warning("No clusters found. Please go back.")
        if st.button("← Back"): st.session_state.step=3; st.rerun()
        st.stop()

    all_cols=get_all_cols(fds)

    merged_ids=set()
    for i,cl in enumerate(clusters):
        if cl["merge_mode"]=="auto" and i in gr: merged_ids.add(i)
        elif cl["merge_mode"]=="manual" and decisions.get(i)=="approve" and i in gr: merged_ids.add(i)

    cl_members=set()
    for i in merged_ids:
        for node in clusters[i]["members"]: cl_members.add(node)

    final_rows=[]
    for i in merged_ids:
        g=gr[i]; cl=clusters[i]
        row={"_Source":"GOLDEN","_Group":f"GRP-{i+1:03d}","_Token":f"TKN-{i+1:04d}",
             "_Merge_Mode":cl["merge_mode"].upper()}
        for col in all_cols: row[col]=g.get(col,"") if isinstance(g,dict) else ""
        final_rows.append(row)

    for fi,(lbl,df) in enumerate(fds):
        for ri in range(len(df)):
            if (fi,ri) not in cl_members:
                row={"_Source":lbl,"_Group":"—","_Token":"—","_Merge_Mode":"—"}
                for col in all_cols: row[col]=df[col].iloc[ri] if col in df.columns else ""
                final_rows.append(row)

    fcols=["_Source","_Group","_Token","_Merge_Mode"]+all_cols
    final_df=pd.DataFrame(final_rows,columns=fcols) if final_rows else pd.DataFrame(columns=fcols)
    st.session_state.final_df=final_df

    total_in=sum(len(df) for _,df in fds)
    golden_c=len(merged_ids)
    non_cl=len([r for r in final_rows if r["_Source"]!="GOLDEN"])
    resolved=total_in-len(final_rows)
    man_app=sum(1 for i,cl in enumerate(clusters) if cl["merge_mode"]=="manual" and decisions.get(i)=="approve")
    man_rej=sum(1 for i,cl in enumerate(clusters) if cl["merge_mode"]=="manual" and decisions.get(i)=="reject")

    st.markdown('<div class="page-title">🏅 Export — Golden Master Records</div>',unsafe_allow_html=True)
    st.markdown(f"""<div style="background:linear-gradient(135deg,var(--green-pale),#dcfce7);
        border:1.5px solid var(--green-border);border-radius:16px;padding:18px 24px;margin-bottom:18px">
      <h3 style="margin:0 0 5px 0;color:#15803d;font-size:1.05rem">🏅 Golden Records Ready</h3>
      <p style="margin:0;color:#166534;font-size:0.83rem">Your unified master dataset is ready for download.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="mrow mrow-5">
      <div class="mc"><div class="val">{total_in:,}</div><div class="lbl">Input Records</div></div>
      <div class="mc o"><div class="val" style="color:#d97706">{golden_c}</div><div class="lbl">Golden Records</div></div>
      <div class="mc"><div class="val" style="color:#2563eb">{non_cl:,}</div><div class="lbl">Unique (Unmatched)</div></div>
      <div class="mc g"><div class="val" style="color:#16a34a">{man_app}</div><div class="lbl">Steward Approved</div></div>
      <div class="mc r"><div class="val" style="color:#dc2626">{man_rej}</div><div class="lbl">Steward Rejected</div></div>
    </div>""", unsafe_allow_html=True)

    tab_p,tab_m,tab_o=st.tabs(["📋 Master Records Preview","🗺️ Merge Map","📊 Output Profile"])
    merge_map=[]
    for i,cl in enumerate(clusters):
        if cl["merge_mode"]=="auto":
            status="Auto-Merged" if i in merged_ids else "Not Merged"
        else:
            status={"approve":"Steward Approved","reject":"Steward Rejected"}.get(decisions.get(i,"pending"),"Pending Review")
        for rec in cl["records"]:
            merge_map.append({"Token":f"TKN-{i+1:04d}","Group":f"GRP-{i+1:03d}",
                              "System":rec["source_label"],"Row":rec["row_idx"]+2,
                              "Merge Mode":cl["merge_mode"].upper(),"Status":status,"Score":cl["max_score"]})
    with tab_p: st.dataframe(final_df.head(200),use_container_width=True)
    with tab_m:
        if merge_map: st.dataframe(pd.DataFrame(merge_map),use_container_width=True)
        else: st.info("No merge map data.")
    with tab_o:
        if len(final_df)>0:
            out_df=final_df[[c for c in final_df.columns if not c.startswith("_")]]
            if len(out_df.columns)>0: render_profile(out_df,label="output")

    st.markdown("<br>",unsafe_allow_html=True)
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        final_df.to_excel(w,sheet_name='Golden Master Records',index=False)
        if merge_map: pd.DataFrame(merge_map).to_excel(w,sheet_name='Merge Map',index=False)
        for lbl,df in fds: df.to_excel(w,sheet_name=f'Src-{lbl[:24]}',index=False)
    out.seek(0)
    st.download_button("⬇️ Download Master Dataset (Excel)",data=out,
                       file_name="golden_master_records.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

    st.markdown("<br>",unsafe_allow_html=True)
    b1,b2=st.columns(2)
    with b1:
        back=5 if any(cl["merge_mode"]=="manual" for cl in clusters) else 4
        if st.button("← Back",use_container_width=True): st.session_state.step=back; st.rerun()
    with b2:
        if st.button("🔄 Start New Session",use_container_width=True):
            for k,v in DEFS.items(): st.session_state[k]=v
            st.rerun()
