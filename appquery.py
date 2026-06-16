import streamlit as st
import sqlglot
from sqlglot import exp
import pandas as pd
import re
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SQL BI Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Main background */
.stApp { background: #0f1117; }
[data-testid="stAppViewContainer"] > .main { background: #0f1117; }
[data-testid="stHeader"] { background: #0f1117; border-bottom: 1px solid rgba(255,255,255,0.08); }

/* Sidebar */
[data-testid="stSidebar"] { background: #1a1d27; border-right: 1px solid rgba(255,255,255,0.08); }

/* Text */
h1, h2, h3, h4, p, div, span, label { color: #f0f0f5 !important; }
.stMarkdown p { color: #8b90a7 !important; }

/* Textarea */
.stTextArea textarea {
    background: #1a1d27 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #f0f0f5 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
}
.stTextArea textarea:focus {
    border-color: #4f6ef7 !important;
    box-shadow: 0 0 0 2px rgba(79,110,247,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: #4f6ef7 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all .15s !important;
}
.stButton > button:hover { background: #3d5ce8 !important; transform: translateY(-1px) !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #1a1d27 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #5a5f7a !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f0f0f5 !important; font-size: 28px !important; font-weight: 700 !important; }

/* Expander */
[data-testid="stExpander"] {
    background: #1a1d27 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
    background: #21253a !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
[data-testid="stExpander"] summary:hover { background: #252a40 !important; }
[data-testid="stExpander"] summary p { color: #f0f0f5 !important; font-weight: 600 !important; font-size: 14px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }
.dvn-scroller { background: #1a1d27 !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1a1d27 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: #f0f0f5 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #1a1d27 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: #8b90a7 !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #21253a !important;
    color: #f0f0f5 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* Info/warning boxes */
[data-testid="stInfo"] { background: rgba(79,110,247,0.1) !important; border: 1px solid rgba(79,110,247,0.25) !important; border-radius: 8px !important; }
[data-testid="stWarning"] { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.25) !important; border-radius: 8px !important; }
[data-testid="stSuccess"] { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.25) !important; border-radius: 8px !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: #21253a !important;
    color: #f0f0f5 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #252a40 !important; }

/* Tags/badges */
.badge {
    display: inline-block;
    font-size: 11px;
    padding: 2px 9px;
    border-radius: 20px;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px 3px;
}
.badge-cte    { background: rgba(124,58,237,0.2); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }
.badge-join   { background: rgba(79,110,247,0.15); color: #818cf8; border: 1px solid rgba(79,110,247,0.25); }
.badge-alias  { background: rgba(34,197,94,0.12); color: #86efac; border: 1px solid rgba(34,197,94,0.2); }
.badge-table  { background: rgba(79,110,247,0.1); color: #93c5fd; border: 1px solid rgba(79,110,247,0.2); }

.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.dim  { color: #5a5f7a !important; }
.section-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: #5a5f7a !important; margin-bottom: 8px; }

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Parser ────────────────────────────────────────────────────────────────────

DIALECTS = {
    "Auto-detect": None,
    "Oracle": "oracle",
    "SQL Server (T-SQL)": "tsql",
    "MySQL": "mysql",
    "PostgreSQL": "postgres",
    "BigQuery": "bigquery",
    "Snowflake": "snowflake",
    "Spark / Hive": "spark",
    "Standard SQL": "ansi",
}

def parse_sql(sql_text: str, dialect: str | None = None) -> dict:
    """
    Full SQL parser using sqlglot.
    Returns:
      {
        "ctes": [str],
        "tables": { TABLE_NAME: { alias, joins, is_cte, columns: [{column, alias, logic, source_table}] } },
        "errors": [str],
        "raw_sql": str
      }
    """
    errors = []
    
    # Try with chosen dialect, fallback to None
    for try_dialect in ([dialect, None] if dialect else [None]):
        try:
            statements = sqlglot.parse(
                sql_text,
                dialect=try_dialect,
                error_level=sqlglot.ErrorLevel.WARN,
            )
            break
        except Exception as e:
            errors.append(str(e))
            statements = []

    all_tables: dict = {}

    for stmt in statements:
        if not stmt:
            continue

        # ── CTEs ──
        cte_names = {c.alias.upper() for c in stmt.find_all(exp.CTE)}

        # ── Alias map: alias_or_name → real_name ──
        alias_map: dict = {}
        for table in stmt.find_all(exp.Table):
            name = (table.name or "").upper()
            alias = (table.alias or "").upper()
            if not name:
                continue
            alias_map[name] = name
            if alias and alias != name:
                alias_map[alias] = name
            if name not in all_tables:
                all_tables[name] = {
                    "alias": alias if alias != name else "",
                    "joins": [],
                    "is_cte": name in cte_names,
                    "columns": [],
                }

        # ── Join types ──
        for join in stmt.find_all(exp.Join):
            tbl = join.find(exp.Table)
            if not tbl:
                continue
            tname = (tbl.name or "").upper()
            kind = (join.args.get("kind") or "").upper()
            side = (join.args.get("side") or "").upper()
            jtype = f"{side} {kind}".strip() or "JOIN"
            if tname in all_tables:
                all_tables[tname]["joins"].append(jtype)

        # ── Find outermost SELECT (not inside CTE body) ──
        outer_select = _get_outer_select(stmt)
        if outer_select is None:
            continue

        # ── Parse SELECT columns ──
        for col_expr in outer_select.expressions:
            _parse_column(col_expr, alias_map, all_tables, cte_names, dialect)

    return {
        "ctes": sorted({t for t, info in all_tables.items() if info["is_cte"]}),
        "tables": all_tables,
        "errors": errors,
    }


def _get_outer_select(stmt) -> exp.Select | None:
    """Return the outermost SELECT, skipping CTE bodies."""
    all_selects = list(stmt.find_all(exp.Select))
    for s in all_selects:
        parent = s.parent
        if isinstance(parent, (exp.Subquery, exp.CTE)):
            continue
        return s
    return all_selects[-1] if all_selects else None


def _parse_column(col_expr, alias_map, all_tables, cte_names, dialect):
    """Parse a single SELECT expression and add to all_tables."""
    alias = (col_expr.alias or "").strip()

    if isinstance(col_expr, exp.Alias):
        inner = col_expr.this
    else:
        inner = col_expr

    raw_expr = inner.sql(dialect=dialect or "oracle").strip()

    # Wildcard
    if isinstance(inner, exp.Star) or raw_expr == "*":
        _add_col(all_tables, alias_map, cte_names, "", "*", "", "")
        return

    # Simple column reference: table.column
    if isinstance(inner, exp.Column):
        tprefix = (inner.table or "").upper()
        col_name = inner.name or raw_expr
        source = alias_map.get(tprefix, tprefix)
        real_alias = alias if alias.upper() != col_name.upper() else ""
        _add_col(all_tables, alias_map, cte_names, source, col_name, real_alias, "")
        return

    # Expression (CASE, SUM, ROUND, etc.)
    col_name = alias or raw_expr[:60]
    logic = raw_expr

    # Try to find source table from first column reference inside expression
    first_col = inner.find(exp.Column)
    source = ""
    if first_col and first_col.table:
        source = alias_map.get(first_col.table.upper(), first_col.table.upper())

    real_alias = alias if alias.upper() != col_name.upper() else ""
    _add_col(all_tables, alias_map, cte_names, source, col_name, real_alias, logic)


def _add_col(all_tables, alias_map, cte_names, source, col_name, alias, logic):
    target = source or (list(all_tables.keys())[0] if all_tables else "UNKNOWN")
    if target not in all_tables:
        all_tables[target] = {
            "alias": "",
            "joins": [],
            "is_cte": target.upper() in {c.upper() for c in cte_names},
            "columns": [],
        }
    all_tables[target]["columns"].append({
        "column": col_name,
        "alias": alias,
        "logic": logic,
    })


def result_to_df(tables: dict) -> pd.DataFrame:
    rows = []
    for tname, info in tables.items():
        if not info["columns"]:
            rows.append({
                "Table": tname,
                "Table Alias": info["alias"],
                "Is CTE": "✓" if info["is_cte"] else "",
                "Join Type": " | ".join(info["joins"]) if info["joins"] else "Main Table",
                "Column": "",
                "Column Alias": "",
                "Logic / Expression": "",
            })
        else:
            for i, col in enumerate(info["columns"]):
                rows.append({
                    "Table": tname,
                    "Table Alias": info["alias"],
                    "Is CTE": "✓" if info["is_cte"] else "",
                    "Join Type": " | ".join(info["joins"]) if info["joins"] else ("CTE" if info["is_cte"] else "Main Table"),
                    "Column": col["column"],
                    "Column Alias": col["alias"],
                    "Logic / Expression": col["logic"],
                })
    return pd.DataFrame(rows)


# ── EXAMPLE SQL ───────────────────────────────────────────────────────────────

EXAMPLE_SQL = """-- BI Report: Monthly Customer Activity by Branch
WITH monthly_totals AS (
  SELECT
    t.branch_id,
    t.account_type_cd        AS acct_type,
    SUM(t.txn_amount)        AS total_amount,
    COUNT(t.txn_id)          AS txn_count,
    AVG(t.txn_amount)        AS avg_txn
  FROM transactions t
  WHERE t.txn_date >= TRUNC(SYSDATE, 'MM')
    AND t.status_cd = 'POSTED'
  GROUP BY t.branch_id, t.account_type_cd
),
customer_segments AS (
  SELECT
    c.customer_id            AS cust_id,
    c.cust_full_name         AS cust_name,
    c.segment_code           AS segment,
    c.risk_rating_cd         AS risk_rating,
    CASE
      WHEN c.avg_balance > 1000000 THEN 'Premium'
      WHEN c.avg_balance > 100000  THEN 'High Value'
      WHEN c.avg_balance > 10000   THEN 'Mid Tier'
      ELSE 'Standard'
    END                      AS value_tier
  FROM dim_customers c
  WHERE c.status_flag = 'A'
    AND c.close_dt IS NULL
)
SELECT
  cs.cust_id,
  cs.cust_name,
  cs.segment,
  cs.value_tier,
  cs.risk_rating,
  b.branch_name_ar           AS branch_name,
  b.region_code              AS region,
  mt.acct_type,
  mt.total_amount,
  mt.txn_count,
  ROUND(mt.avg_txn, 2)       AS avg_txn_amount,
  p.product_name             AS product,
  p.risk_weight              AS risk_wt,
  SYSDATE                    AS report_dt
FROM customer_segments       cs
INNER JOIN monthly_totals    mt ON cs.cust_id      = mt.branch_id
LEFT  JOIN dim_branches       b  ON mt.branch_id   = b.branch_id
LEFT  JOIN dim_products       p  ON cs.segment     = p.segment_code
ORDER BY mt.total_amount DESC
"""


# ── UI ────────────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem;">
  <div style="display:inline-flex; align-items:center; gap:10px; margin-bottom:8px;">
    <div style="width:36px;height:36px;background:linear-gradient(135deg,#4f6ef7,#7c3aed);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">⚡</div>
    <span style="font-size:26px;font-weight:700;letter-spacing:-0.5px;">SQL BI Analyzer</span>
  </div>
  <p style="color:#8b90a7 !important;font-size:15px;margin:0;">
    الصق أي SQL Script — هيطلعلك كل جدول وأعمدته والـ aliases والـ logic
  </p>
</div>
""", unsafe_allow_html=True)

# Controls row
col_dialect, col_spacer, col_btn_ex = st.columns([2, 4, 2])
with col_dialect:
    dialect_choice = st.selectbox("Dialect", list(DIALECTS.keys()), index=0, label_visibility="collapsed")
with col_btn_ex:
    if st.button("📋 مثال", use_container_width=True):
        st.session_state["sql_input"] = EXAMPLE_SQL

# SQL Input
sql_input = st.text_area(
    "SQL Script",
    value=st.session_state.get("sql_input", ""),
    height=260,
    placeholder="-- الصق الـ SQL Script هنا...",
    label_visibility="collapsed",
    key="sql_ta",
)

# Analyze button
c1, c2, c3 = st.columns([2, 2, 4])
with c1:
    analyze_clicked = st.button("🔍  تحليل", use_container_width=True)
with c2:
    if st.button("🗑  مسح", use_container_width=True):
        st.session_state["sql_input"] = ""
        st.session_state.pop("result", None)
        st.rerun()

if analyze_clicked and sql_input.strip():
    dialect = DIALECTS[dialect_choice]
    with st.spinner("جاري التحليل..."):
        result = parse_sql(sql_input.strip(), dialect)
    st.session_state["result"] = result
    if result["errors"]:
        for e in result["errors"][:3]:
            st.warning(f"تحذير: {e}")

# ── RESULTS ───────────────────────────────────────────────────────────────────
if "result" in st.session_state and st.session_state["result"]:
    result = st.session_state["result"]
    tables = result["tables"]
    ctes   = result["ctes"]

    if not tables:
        st.error("لم يتم العثور على جداول. تأكد من صحة الـ SQL أو جرب dialect مختلف.")
        st.stop()

    st.success("✓ تم التحليل بنجاح")

    total_cols  = sum(len(i["columns"]) for i in tables.values())
    total_joins = sum(len(i["joins"])   for i in tables.values())

    # Stats
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("الجداول",    len(tables))
    m2.metric("الأعمدة",    total_cols)
    m3.metric("Joins",       total_joins)
    m4.metric("CTEs",        len(ctes))
    m5.metric("Expressions", sum(1 for i in tables.values() for c in i["columns"] if c["logic"]))

    # CTE strip
    if ctes:
        badges = " ".join(f'<span class="badge badge-cte">{c}</span>' for c in ctes)
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);
                    border-radius:10px;padding:10px 14px;margin:12px 0;">
          <span style="font-size:12px;font-weight:600;color:#f59e0b;margin-left:8px;">⚙ CTEs / Pre-SQL</span>
          {badges}
        </div>""", unsafe_allow_html=True)

    # Tabs: Detail view  |  Full table view
    tab1, tab2 = st.tabs(["📋  عرض تفصيلي", "📊  جدول كامل"])

    # ── Tab 1: Detailed ──
    with tab1:
        st.markdown('<p class="section-label">الجداول والأعمدة</p>', unsafe_allow_html=True)

        for tname, info in tables.items():
            cte_badge   = '<span class="badge badge-cte">CTE</span>'   if info["is_cte"] else ""
            alias_badge = f'<span class="badge badge-alias">alias: {info["alias"]}</span>' if info["alias"] else ""
            join_badges = " ".join(f'<span class="badge badge-join">{j}</span>' for j in info["joins"])
            col_count   = len(info["columns"])

            label = f"🗃 {tname}  {cte_badge}{alias_badge}{join_badges}  —  {col_count} عمود"

            with st.expander(label, expanded=True):
                if not info["columns"]:
                    st.markdown('<p class="dim">لا توجد أعمدة محددة في الـ SELECT</p>', unsafe_allow_html=True)
                    continue

                rows = []
                for c in info["columns"]:
                    rows.append({
                        "Column": c["column"],
                        "Alias / اختصار": c["alias"] or "—",
                        "Logic / Expression": c["logic"] or "—",
                    })
                df = pd.DataFrame(rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Column":             st.column_config.TextColumn("Column", width="medium"),
                        "Alias / اختصار":     st.column_config.TextColumn("Alias", width="medium"),
                        "Logic / Expression": st.column_config.TextColumn("Logic / Expression", width="large"),
                    }
                )

    # ── Tab 2: Full table ──
    with tab2:
        df_full = result_to_df(tables)
        st.dataframe(df_full, use_container_width=True, hide_index=True)

        # Export
        csv_buffer = io.StringIO()
        df_full.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇  تصدير CSV",
            data=csv_buffer.getvalue().encode("utf-8-sig"),
            file_name="sql_bi_analysis.csv",
            mime="text/csv",
            use_container_width=False,
        )

elif analyze_clicked and not sql_input.strip():
    st.warning("الصق SQL Script أولاً.")
