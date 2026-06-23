import streamlit as st
import sqlglot
from sqlglot import exp
import pandas as pd
import io
import re

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
.badge-ref    { background: rgba(236,72,153,0.12); color: #f9a8d4; border: 1px solid rgba(236,72,153,0.25); }
.badge-syn    { background: rgba(245,158,11,0.12); color: #fcd34d; border: 1px solid rgba(245,158,11,0.25); }

.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.dim  { color: #5a5f7a !important; }
.section-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: #5a5f7a !important; margin-bottom: 8px; }

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Dialects ──────────────────────────────────────────────────────────────────

DIALECTS = {
    "Auto-detect": None,
    "Oracle": "oracle",
    "SQL Server (T-SQL)": "tsql",
    "MySQL": "mysql",
    "PostgreSQL": "postgres",
    "BigQuery": "bigquery",
    "Snowflake": "snowflake",
    "Spark / Hive": "spark",
    "Standard SQL": None,
}


# ── Embedded SQL extraction (dynamic SQL wrapped in string literals) ──────────

_EMBEDDED_SQL_PATTERN = re.compile(r"'((?:[^']|'')*)'")
_SQL_START_PATTERN = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)


def _extract_embedded_sql_statements(raw_sql_text: str) -> list[str]:
    """
    Scan the raw SQL text for string literals that themselves contain a full
    SQL statement - the classic dynamic-SQL pattern used by
    `EXECUTE IMMEDIATE '...'` (Oracle/PLSQL), `EXEC sp_executesql N'...'`
    (T-SQL), `EXEC ('...')`, or a PL/SQL variable assignment like
    `v_sql := 'SELECT ...'`. Each match is unescaped (doubled '' -> ')
    and returned as a standalone SQL string ready to be parsed on its own.
    """
    found = []
    for m in _EMBEDDED_SQL_PATTERN.finditer(raw_sql_text):
        inner = m.group(1).replace("''", "'")
        if _SQL_START_PATTERN.match(inner.strip()):
            found.append(inner.strip())
    return found


# ── Parser engine ───────────────────────────────────────────────────────────
#
# Design notes (why this works for deeply nested subqueries):
#
# 1. Alias resolution is fully recursive. A subquery alias (e.g. `alt1`) is
#    resolved by walking down through any number of nested wrapper subqueries
#    until a real base table is found at the bottom of the FROM chain.
#
# 2. Column extraction is scope-aware. Each SELECT's column list is parsed
#    within its own scope, instead of flattening every SELECT node in the
#    whole AST into one bucket — that flattening is what causes inner
#    subquery scratch columns to leak into the wrong table.
#
# 3. Tables/columns referenced only in WHERE, JOIN...ON, GROUP BY, HAVING, or
#    ORDER BY (never appearing in any SELECT list) are still captured and
#    tagged with the clause they came from.
#
# 4. Duplicate column names across different tables are never merged or
#    dropped — every occurrence is kept under its own table. A separate
#    "Synonyms" view groups same-named columns across tables for visibility.

def _resolve_subquery_root_table(subquery_node, alias_map, visited=None):
    """Follow a Subquery down through nested wrappers to find its real base table."""
    if visited is None:
        visited = set()
    node_id = id(subquery_node)
    if node_id in visited:
        return None
    visited.add(node_id)

    inner = subquery_node.this
    if not isinstance(inner, exp.Select):
        return None

    from_clause = inner.find(exp.From)
    if from_clause is None:
        return None

    from_this = from_clause.this
    if isinstance(from_this, exp.Table):
        name = (from_this.name or "").upper()
        return alias_map.get(name, name) if name else None

    if isinstance(from_this, exp.Subquery):
        return _resolve_subquery_root_table(from_this, alias_map, visited)

    return None


def _build_alias_map(stmt):
    """Global alias -> real_table_name map, with recursive subquery resolution."""
    alias_map = {}

    for table in stmt.find_all(exp.Table):
        name = (table.name or "").upper()
        if not name:
            continue
        alias_map[name] = name
        alias = (table.alias or "").upper()
        if alias and alias != name:
            alias_map[alias] = name

    # Resolve subquery aliases; loop a few times in case one subquery's FROM
    # references another alias that hasn't been resolved yet.
    for _ in range(5):
        changed = False
        for sq in stmt.find_all(exp.Subquery):
            sq_alias = (sq.alias or "").upper()
            if not sq_alias or sq_alias in alias_map:
                continue
            resolved = _resolve_subquery_root_table(sq, alias_map)
            if resolved:
                alias_map[sq_alias] = resolved
                changed = True
        if not changed:
            break

    return alias_map


def _get_effective_select(select_node, visited=None):
    """
    Drill through a pure passthrough wrapper (`SELECT * FROM (subquery)` with
    no real projection of its own) to reach the SELECT that defines the
    actual columns.
    """
    if visited is None:
        visited = set()
    node_id = id(select_node)
    if node_id in visited:
        return select_node
    visited.add(node_id)

    exprs = select_node.expressions
    is_pure_star = len(exprs) == 1 and isinstance(exprs[0], exp.Star)
    if not is_pure_star:
        return select_node

    from_clause = select_node.find(exp.From)
    if from_clause is None:
        return select_node

    from_this = from_clause.this
    if isinstance(from_this, exp.Subquery) and isinstance(from_this.this, exp.Select):
        return _get_effective_select(from_this.this, visited)

    return select_node


def _ensure_table(all_tables, name, alias, is_cte):
    if name not in all_tables:
        all_tables[name] = {
            "alias": alias if alias and alias != name else "",
            "joins": [],
            "is_cte": is_cte,
            "columns": [],
            "refs": [],  # {clause, column, logic} - refs found outside the SELECT list, with full condition text
        }
    return all_tables[name]


def _parse_column(col_expr, alias_map, all_tables, cte_names, dialect):
    """Parse a single SELECT-list expression and register it under its source table."""
    alias = (col_expr.alias or "").strip()
    inner = col_expr.this if isinstance(col_expr, exp.Alias) else col_expr
    raw_expr = inner.sql(dialect=dialect or "oracle").strip()

    if isinstance(inner, exp.Star) or raw_expr == "*":
        _add_select_col(all_tables, cte_names, "", "*", "", "")
        return

    if isinstance(inner, exp.Column):
        tprefix = (inner.table or "").upper()
        col_name = inner.name or raw_expr
        source = alias_map.get(tprefix, tprefix) if tprefix else ""
        real_alias = alias if alias.upper() != col_name.upper() else ""
        _add_select_col(all_tables, cte_names, source, col_name, real_alias, "")
        return

    # Expression (CASE, SUM, window function, etc.)
    col_name = alias or raw_expr[:80]
    logic = raw_expr
    first_col = inner.find(exp.Column)
    source = ""
    if first_col is not None and first_col.table:
        source = alias_map.get(first_col.table.upper(), first_col.table.upper())

    real_alias = alias if alias.upper() != col_name.upper() else ""
    _add_select_col(all_tables, cte_names, source, col_name, real_alias, logic)


def _add_select_col(all_tables, cte_names, source, col_name, alias, logic):
    target = source or (next(iter(all_tables), "UNKNOWN"))
    table_entry = _ensure_table(all_tables, target, "", target.upper() in cte_names)
    table_entry["columns"].append({"column": col_name, "alias": alias, "logic": logic})


def _nearest_enclosing_single_table(node):
    """
    For an unprefixed column reference, walk up to the nearest enclosing
    SELECT and, if its FROM is a single real table with no joins, return that
    table's name. Lets bare `ORDER BY col` / `WHERE col = ...` references
    inside single-table subqueries resolve correctly instead of falling back
    to "unresolved".
    """
    parent = node.parent
    while parent is not None and not isinstance(parent, exp.Select):
        parent = parent.parent
    if parent is None:
        return None

    from_clause = parent.find(exp.From)
    if from_clause is None or parent.find(exp.Join) is not None:
        return None

    from_this = from_clause.this
    if isinstance(from_this, exp.Table):
        return (from_this.name or "").upper() or None
    return None


def _split_and_conditions(node):
    """Split a boolean expression tree on top-level AND into individual conditions."""
    if isinstance(node, exp.And):
        return _split_and_conditions(node.left) + _split_and_conditions(node.right)
    return [node]


def _direct_columns_excluding_nested_selects(cond):
    """
    Return columns belonging directly to `cond`, excluding any column that
    sits inside a nested SELECT (e.g. inside an EXISTS(...) or IN (subquery)).
    Columns inside the nested SELECT get registered with full precision when
    that inner SELECT's own WHERE/JOIN/etc. is processed - this avoids
    duplicating long subquery text against every column it contains.
    """
    result = []
    for col in cond.find_all(exp.Column):
        p = col.parent
        nested = False
        while p is not None and p is not cond.parent:
            if isinstance(p, exp.Select):
                nested = True
                break
            p = p.parent
        if not nested:
            result.append(col)
    return result


def _collect_clause_refs(stmt, alias_map, all_tables, cte_names):
    """
    Capture every table/column reference from WHERE, JOIN...ON, GROUP BY,
    HAVING and ORDER BY - including ones buried inside nested subqueries -
    and attach the full condition text (the actual logic), not just the bare
    column name. A condition like `a.status = 'ACTIVE'` is recorded against
    column `status` with logic `a.status = 'ACTIVE'`, not just the word
    "status". Columns that sit inside a deeper nested SELECT (e.g. inside an
    EXISTS or IN subquery) are left for that inner SELECT's own clause pass,
    so the same long subquery text isn't duplicated against every column it
    contains.
    """

    def register_condition(col, clause_label, logic_text):
        tprefix = (col.table or "").upper()
        col_name = col.name or col.sql()
        if tprefix:
            source = alias_map.get(tprefix, tprefix)
        else:
            fallback = _nearest_enclosing_single_table(col) or ""
            source = alias_map.get(fallback, fallback)
        target = source or "Unresolved (no table prefix)"
        table_entry = _ensure_table(all_tables, target, "", target.upper() in cte_names)
        ref_key = (clause_label, col_name, logic_text)
        existing = {(r["clause"], r["column"], r["logic"]) for r in table_entry["refs"]}
        if ref_key not in existing:
            table_entry["refs"].append({"clause": clause_label, "column": col_name, "logic": logic_text})

    def register_node(node, clause_label, split_on_and):
        if node is None:
            return
        conditions = _split_and_conditions(node) if split_on_and else [node]
        for cond in conditions:
            cond_text = cond.sql(dialect="oracle").strip()
            direct_cols = _direct_columns_excluding_nested_selects(cond)
            for col in direct_cols:
                register_condition(col, clause_label, cond_text)

    # WHERE - every WHERE node anywhere in the tree, including inside nested
    # subqueries (find_all walks the whole subtree regardless of depth).
    for where in stmt.find_all(exp.Where):
        register_node(where.this, "WHERE", split_on_and=True)

    # JOIN ... ON - every join condition at every nesting level.
    for join in stmt.find_all(exp.Join):
        register_node(join.args.get("on"), "JOIN ON", split_on_and=True)

    # GROUP BY / HAVING / ORDER BY - kept as single units per clause (AND
    # splitting doesn't apply the same way here).
    for group in stmt.find_all(exp.Group):
        register_node(group, "GROUP BY", split_on_and=False)
    for having in stmt.find_all(exp.Having):
        register_node(having.this, "HAVING", split_on_and=True)
    for order in stmt.find_all(exp.Order):
        register_node(order, "ORDER BY", split_on_and=False)


def _collect_join_types(stmt, all_tables):
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


def _get_outer_select(stmt):
    """Return the statement's own outermost SELECT (not a CTE body)."""
    all_selects = list(stmt.find_all(exp.Select))
    for s in all_selects:
        parent = s.parent
        if isinstance(parent, (exp.Subquery, exp.CTE)):
            continue
        return s
    return all_selects[-1] if all_selects else None


_DYNAMIC_SQL_PROC_NAMES = {"SP_EXECUTESQL", "EXECUTE", "EXEC", "IMMEDIATE"}


def _parse_single_statement(stmt, all_tables):
    """Run the full extraction pipeline (tables, joins, columns, clause refs) for one parsed statement."""
    cte_names = {c.alias.upper() for c in stmt.find_all(exp.CTE)}
    alias_map = _build_alias_map(stmt)

    # Register every real table in the statement, even ones that only ever
    # appear in a WHERE/JOIN condition and never in a SELECT list.
    for table in stmt.find_all(exp.Table):
        name = (table.name or "").upper()
        alias = (table.alias or "").upper()
        if not name or name in _DYNAMIC_SQL_PROC_NAMES:
            continue
        _ensure_table(all_tables, name, alias, name in cte_names)

    _collect_join_types(stmt, all_tables)

    # Each CTE has its own column scope.
    for cte in stmt.find_all(exp.CTE):
        cte_select = cte.this
        if isinstance(cte_select, exp.Select):
            eff = _get_effective_select(cte_select)
            for col_expr in eff.expressions:
                _parse_column(col_expr, alias_map, all_tables, cte_names, None)

    # The statement's own outer SELECT, drilling through pure
    # `SELECT * FROM (...)` passthrough wrappers.
    outer_select = _get_outer_select(stmt)
    if outer_select is not None:
        eff = _get_effective_select(outer_select)
        for col_expr in eff.expressions:
            _parse_column(col_expr, alias_map, all_tables, cte_names, None)

    # Capture anything referenced in WHERE / JOIN ON / GROUP BY / HAVING / ORDER BY,
    # at every subquery nesting level, with the full condition logic attached.
    _collect_clause_refs(stmt, alias_map, all_tables, cte_names)


def parse_sql(sql_text: str, dialect: str | None = None) -> dict:
    """
    Full SQL parser using sqlglot.

    Also scans the raw text for dynamic SQL embedded inside string literals
    (e.g. `EXECUTE IMMEDIATE '...'`, `EXEC sp_executesql N'...'`) and parses
    those statements too, merging their tables/columns into the same result -
    so a query string built dynamically still gets fully analyzed.

    Returns:
      {
        "ctes": [str],
        "tables": {
            TABLE_NAME: {
                alias, joins, is_cte,
                columns: [{column, alias, logic}],
                refs: [{clause, column, logic}],   # refs found outside the SELECT list
            }
        },
        "errors": [str],
        "embedded_sql_found": [str],   # any dynamic-SQL strings that were detected and parsed
      }
    """
    errors = []
    statements = []

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
        try:
            _parse_single_statement(stmt, all_tables)
        except Exception as e:
            errors.append(f"Failed to fully analyze a statement: {e}")

    # Dynamic SQL detection: parse any SQL string literals found embedded in
    # the raw text (covers EXECUTE IMMEDIATE, sp_executesql, EXEC('...'), and
    # PL/SQL string-built statements), and merge their tables/columns in too.
    embedded_sql_found = _extract_embedded_sql_statements(sql_text)
    for embedded_sql in embedded_sql_found:
        for try_dialect in ([dialect, None] if dialect else [None]):
            try:
                embedded_statements = sqlglot.parse(
                    embedded_sql,
                    dialect=try_dialect,
                    error_level=sqlglot.ErrorLevel.IGNORE,
                )
                for stmt in embedded_statements:
                    if stmt:
                        _parse_single_statement(stmt, all_tables)
                break
            except Exception:
                continue

    return {
        "ctes": sorted({t for t, info in all_tables.items() if info["is_cte"]}),
        "tables": all_tables,
        "errors": errors,
        "embedded_sql_found": embedded_sql_found,
    }


def find_synonyms(tables: dict) -> dict:
    """
    Group SELECT-list columns by name across all tables. Returns only names
    that appear in 2+ distinct tables. Nothing is deduplicated away — every
    occurrence (with its own table/alias) is preserved in the grouping.
    """
    by_name: dict = {}
    for tname, info in tables.items():
        for col in info["columns"]:
            cname = (col["column"] or "").strip()
            if not cname or cname == "*":
                continue
            key = cname.upper()
            by_name.setdefault(key, []).append({
                "display_name": cname,
                "table": tname,
                "alias": col["alias"],
                "logic": col["logic"],
            })
    return {name: occ for name, occ in by_name.items() if len({o["table"] for o in occ}) > 1}


def build_column_mapping(tables: dict) -> dict:
    """
    For every real (table, column) pair, gather every place it is used in the
    query: each SELECT-list usage (with whatever alias was given there, or no
    alias at all) plus every non-SELECT usage (WHERE / JOIN ON / GROUP BY /
    HAVING / ORDER BY), with its full condition logic. This shows, in one
    place, the complete relationship between a column's real name and every
    name/context it shows up under across the whole query.

    Returns:
      { (table, real_column_upper): {
            "table": str,
            "real_column": str,         # as it appears in the column list (display case)
            "select_usages": [{"alias": str}],         # aliases this column was selected as (empty string = no alias / used as-is)
            "other_usages": [{"clause": str, "logic": str}],
        }
      }
    """
    mapping: dict = {}

    def entry_for(tname, real_col):
        key = (tname, real_col.upper())
        if key not in mapping:
            mapping[key] = {
                "table": tname,
                "real_column": real_col,
                "select_usages": [],
                "other_usages": [],
            }
        return mapping[key]

    for tname, info in tables.items():
        for col in info["columns"]:
            cname = (col["column"] or "").strip()
            if not cname or cname == "*":
                continue
            # If this entry has logic (a derived expression), the "real column"
            # concept doesn't apply the same way - still track it under its alias/name.
            e = entry_for(tname, cname)
            e["select_usages"].append({"alias": col["alias"], "logic": col["logic"]})

        for ref in info["refs"]:
            cname = (ref["column"] or "").strip()
            if not cname:
                continue
            e = entry_for(tname, cname)
            e["other_usages"].append({"clause": ref["clause"], "logic": ref["logic"]})

    # Only keep entries that actually have more than one usage worth mapping
    # (a column used exactly once, nowhere else, isn't an interesting "mapping").
    return {
        k: v for k, v in mapping.items()
        if (len(v["select_usages"]) + len(v["other_usages"])) > 1
    }


def result_to_df(tables: dict) -> pd.DataFrame:
    rows = []
    for tname, info in tables.items():
        if not info["columns"] and not info["refs"]:
            rows.append({
                "Table": tname,
                "Table Alias": info["alias"],
                "Is CTE": "✓" if info["is_cte"] else "",
                "Join Type": " | ".join(info["joins"]) if info["joins"] else "Main Table",
                "Column": "",
                "Column Alias": "",
                "Logic / Expression": "",
                "Found In": "",
            })
            continue

        for col in info["columns"]:
            rows.append({
                "Table": tname,
                "Table Alias": info["alias"],
                "Is CTE": "✓" if info["is_cte"] else "",
                "Join Type": " | ".join(info["joins"]) if info["joins"] else ("CTE" if info["is_cte"] else "Main Table"),
                "Column": col["column"],
                "Column Alias": col["alias"],
                "Logic / Expression": col["logic"],
                "Found In": "SELECT",
            })
        for ref in info["refs"]:
            rows.append({
                "Table": tname,
                "Table Alias": info["alias"],
                "Is CTE": "✓" if info["is_cte"] else "",
                "Join Type": " | ".join(info["joins"]) if info["joins"] else ("CTE" if info["is_cte"] else "Main Table"),
                "Column": ref["column"],
                "Column Alias": "",
                "Logic / Expression": ref.get("logic", ""),
                "Found In": ref["clause"],
            })
    return pd.DataFrame(rows)


def synonyms_to_df(synonyms: dict) -> pd.DataFrame:
    rows = []
    for col_name, occurrences in sorted(synonyms.items()):
        for occ in occurrences:
            rows.append({
                "Column Name": occ["display_name"],
                "Table": occ["table"],
                "Column Alias": occ["alias"] or "—",
                "Logic / Expression": occ["logic"] or "—",
                "Tables Sharing This Name": len({o["table"] for o in occurrences}),
            })
    return pd.DataFrame(rows)


def mapping_to_df(mapping: dict) -> pd.DataFrame:
    rows = []
    for (tname, _), info in mapping.items():
        for u in info["select_usages"]:
            rows.append({
                "Table": info["table"],
                "Real Column": info["real_column"],
                "Used As": u["alias"] or info["real_column"],
                "Context": "SELECT",
                "Logic / Expression": u.get("logic") or "—",
            })
        for u in info["other_usages"]:
            rows.append({
                "Table": info["table"],
                "Real Column": info["real_column"],
                "Used As": info["real_column"],
                "Context": u["clause"],
                "Logic / Expression": u["logic"] or "—",
            })
    return pd.DataFrame(rows)


# ── EXAMPLE SQL ───────────────────────────────────────────────────────────────

EXAMPLE_SQL = """SELECT * FROM (
  SELECT
    ROW_NUMBER() OVER(PARTITION BY C1.CIF ORDER BY alt1.ALT_ID_VAL DESC) AS rn,
    alt1.ALT_ID_VAL   AS FCUBS_Identifier,
    alt2.ALT_ID_VAL   AS SME_Identifier,
    lkp.ID_TYP_DESC,
    c2.ALT_ID_VAL_AD  AS MDM_Identifier
  FROM C360_ORS.C_BO_PRTY c1
  LEFT JOIN (
    SELECT * FROM (
      SELECT CIF, ALT_ID_VAL,
        ROW_NUMBER() OVER(PARTITION BY CIF ORDER BY ALT_ID_VAL DESC) r
      FROM C360_ORS.C_L_FCU_ALT
    ) x
  ) alt1 ON alt1.CIF = c1.CIF
  LEFT JOIN C360_ORS.C_L_SME_ALT alt2 ON alt2.CIF = c1.CIF
  LEFT JOIN C360_ORS.C_BO_PRTY_RLE_ALT_ID c2 ON c1.ROWID_OBJECT = c2.PRTY_FK
  LEFT JOIN C360_ORS.C_L_LKP_ALT_ID_TYP lkp ON lkp.ID_TYP = c2.ALT_ID_TYP
  WHERE c1.PRTY_TYP = 'Org' AND c1.CIF = 10217301
) t
"""


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem;">
  <div style="display:inline-flex; align-items:center; gap:10px; margin-bottom:8px;">
    <div style="width:36px;height:36px;background:linear-gradient(135deg,#4f6ef7,#7c3aed);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;">⚡</div>
    <span style="font-size:26px;font-weight:700;letter-spacing:-0.5px;">SQL BI Analyzer</span>
  </div>
  <p style="color:#8b90a7 !important;font-size:15px;margin:0;">
    Paste any SQL script — get every table, column, alias, synonym, and inline expression, even inside nested subqueries.
  </p>
</div>
""", unsafe_allow_html=True)

# Controls row
col_dialect, col_spacer, col_btn_ex = st.columns([2, 4, 2])
with col_dialect:
    dialect_choice = st.selectbox("Dialect", list(DIALECTS.keys()), index=0, label_visibility="collapsed")
with col_btn_ex:
    if st.button("📋 Load example", use_container_width=True):
        st.session_state["sql_input"] = EXAMPLE_SQL

# SQL Input
sql_input = st.text_area(
    "SQL Script",
    value=st.session_state.get("sql_input", ""),
    height=260,
    placeholder="-- Paste your SQL script here...",
    label_visibility="collapsed",
    key="sql_ta",
)

# Analyze button
c1, c2, c3 = st.columns([2, 2, 4])
with c1:
    analyze_clicked = st.button("🔍  Analyze", use_container_width=True)
with c2:
    if st.button("🗑  Clear", use_container_width=True):
        st.session_state["sql_input"] = ""
        st.session_state.pop("result", None)
        st.rerun()

if analyze_clicked and sql_input.strip():
    dialect = DIALECTS[dialect_choice]
    with st.spinner("Analyzing..."):
        result = parse_sql(sql_input.strip(), dialect)
    st.session_state["result"] = result
    if result["errors"]:
        for e in result["errors"][:3]:
            st.warning(f"Warning: {e}")
    if result.get("embedded_sql_found"):
        st.info(f"🔎 Detected {len(result['embedded_sql_found'])} dynamic SQL string(s) embedded in the script (e.g. EXECUTE IMMEDIATE / sp_executesql) — they were extracted and analyzed too.")

# ── RESULTS ───────────────────────────────────────────────────────────────────
if "result" in st.session_state and st.session_state["result"]:
    result = st.session_state["result"]
    tables = result["tables"]
    ctes = result["ctes"]
    synonyms = find_synonyms(tables)
    col_mapping = build_column_mapping(tables)

    if not tables:
        st.error("No tables found. Check that the SQL is valid, or try a different dialect.")
        st.stop()

    st.success("✓ Analysis complete")

    total_cols = sum(len(i["columns"]) for i in tables.values())
    total_joins = sum(len(i["joins"]) for i in tables.values())
    total_refs = sum(len(i["refs"]) for i in tables.values())

    # Stats
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Tables", len(tables))
    m2.metric("Columns", total_cols)
    m3.metric("Joins", total_joins)
    m4.metric("CTEs", len(ctes))
    m5.metric("Other Refs", total_refs)
    m6.metric("Synonyms", len(synonyms))
    m7.metric("Mapped Columns", len(col_mapping))

    # CTE strip
    if ctes:
        badges = " ".join(f'<span class="badge badge-cte">{c}</span>' for c in ctes)
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);
                    border-radius:10px;padding:10px 14px;margin:12px 0;">
          <span style="font-size:12px;font-weight:600;color:#f59e0b;margin-left:8px;">⚙ CTEs / Pre-SQL</span>
          {badges}
        </div>""", unsafe_allow_html=True)

    # Synonym alert strip
    if synonyms:
        syn_badges = " ".join(f'<span class="badge badge-syn">{name}</span>' for name in sorted(synonyms))
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);
                    border-radius:10px;padding:10px 14px;margin:12px 0;">
          <span style="font-size:12px;font-weight:600;color:#f59e0b;margin-left:8px;">⚠ Columns appearing in multiple tables</span>
          {syn_badges}
        </div>""", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋  Detailed View", "🔁  Synonyms", "🔗  Column Mapping", "📊  Full Table"])

    # ── Tab 1: Detailed ──
    with tab1:
        st.markdown('<p class="section-label">Tables and Columns</p>', unsafe_allow_html=True)

        for tname, info in tables.items():
            cte_badge = '<span class="badge badge-cte">CTE</span>' if info["is_cte"] else ""
            alias_badge = f'<span class="badge badge-alias">alias: {info["alias"]}</span>' if info["alias"] else ""
            join_badges = " ".join(f'<span class="badge badge-join">{j}</span>' for j in info["joins"])
            col_count = len(info["columns"])
            ref_count = len(info["refs"])

            label = f"🗃 {tname}  {cte_badge}{alias_badge}{join_badges}  —  {col_count} column(s)"
            if ref_count:
                label += f", {ref_count} other reference(s)"

            with st.expander(label, expanded=True):
                if info["columns"]:
                    rows = [{
                        "Column": c["column"],
                        "Alias": c["alias"] or "—",
                        "Logic / Expression": c["logic"] or "—",
                    } for c in info["columns"]]
                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Column": st.column_config.TextColumn("Column", width="medium"),
                            "Alias": st.column_config.TextColumn("Alias", width="medium"),
                            "Logic / Expression": st.column_config.TextColumn("Logic / Expression", width="large"),
                        }
                    )
                else:
                    st.markdown('<p class="dim">No columns selected from this table directly.</p>', unsafe_allow_html=True)

                if info["refs"]:
                    st.markdown('<p class="section-label" style="margin-top:14px;">Referenced outside SELECT (WHERE / JOIN ON / GROUP BY / HAVING / ORDER BY)</p>', unsafe_allow_html=True)
                    ref_rows = [{
                        "Clause": r["clause"],
                        "Column": r["column"],
                        "Full Condition / Logic": r.get("logic", ""),
                    } for r in info["refs"]]
                    st.dataframe(
                        pd.DataFrame(ref_rows),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Clause": st.column_config.TextColumn("Clause", width="small"),
                            "Column": st.column_config.TextColumn("Column", width="medium"),
                            "Full Condition / Logic": st.column_config.TextColumn("Full Condition / Logic", width="large"),
                        }
                    )

    # ── Tab 2: Synonyms ──
    with tab2:
        st.markdown('<p class="section-label">Columns sharing the same name across different tables</p>', unsafe_allow_html=True)
        if not synonyms:
            st.markdown('<p class="dim">No duplicate column names were found across tables.</p>', unsafe_allow_html=True)
        else:
            for col_name, occurrences in sorted(synonyms.items()):
                table_badges = " ".join(f'<span class="badge badge-table">{o["table"]}</span>' for o in occurrences)
                with st.expander(f"🔁 {col_name}  —  found in {len({o['table'] for o in occurrences})} tables  {table_badges}", expanded=True):
                    rows = [{
                        "Table": o["table"],
                        "Column": o["display_name"],
                        "Alias": o["alias"] or "—",
                        "Logic / Expression": o["logic"] or "—",
                    } for o in occurrences]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            df_syn = synonyms_to_df(synonyms)
            csv_buf = io.StringIO()
            df_syn.to_csv(csv_buf, index=False, encoding="utf-8-sig")
            st.download_button(
                label="⬇  Export Synonyms CSV",
                data=csv_buf.getvalue().encode("utf-8-sig"),
                file_name="sql_synonyms.csv",
                mime="text/csv",
            )

    # ── Tab 3: Column Mapping ──
    with tab3:
        st.markdown('<p class="section-label">Every name/context a real column is used under across the query</p>', unsafe_allow_html=True)
        if not col_mapping:
            st.markdown('<p class="dim">No column has more than one usage worth mapping in this query.</p>', unsafe_allow_html=True)
        else:
            for (tname, col_key), info in col_mapping.items():
                total_usages = len(info["select_usages"]) + len(info["other_usages"])
                used_as_names = sorted({u["alias"] for u in info["select_usages"] if u["alias"]})
                alias_hint = f"  (aliased as: {', '.join(used_as_names)})" if used_as_names else ""

                with st.expander(
                    f"🔗 {info['table']}.{info['real_column']}{alias_hint}  —  {total_usages} usage(s)",
                    expanded=True,
                ):
                    rows = []
                    for u in info["select_usages"]:
                        rows.append({
                            "Context": "SELECT",
                            "Used As": u["alias"] or info["real_column"],
                            "Logic / Expression": u.get("logic") or "—",
                        })
                    for u in info["other_usages"]:
                        rows.append({
                            "Context": u["clause"],
                            "Used As": info["real_column"],
                            "Logic / Expression": u["logic"] or "—",
                        })
                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Context": st.column_config.TextColumn("Context", width="small"),
                            "Used As": st.column_config.TextColumn("Used As", width="medium"),
                            "Logic / Expression": st.column_config.TextColumn("Logic / Expression", width="large"),
                        }
                    )

            st.markdown("---")
            df_map = mapping_to_df(col_mapping)
            csv_buf_map = io.StringIO()
            df_map.to_csv(csv_buf_map, index=False, encoding="utf-8-sig")
            st.download_button(
                label="⬇  Export Column Mapping CSV",
                data=csv_buf_map.getvalue().encode("utf-8-sig"),
                file_name="sql_column_mapping.csv",
                mime="text/csv",
            )

    # ── Tab 4: Full table ──
    with tab4:
        df_full = result_to_df(tables)
        st.dataframe(df_full, use_container_width=True, hide_index=True)

        csv_buffer = io.StringIO()
        df_full.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇  Export CSV",
            data=csv_buffer.getvalue().encode("utf-8-sig"),
            file_name="sql_bi_analysis.csv",
            mime="text/csv",
            use_container_width=False,
        )

elif analyze_clicked and not sql_input.strip():
    st.warning("Paste a SQL script first.")
