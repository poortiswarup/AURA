import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.storage import (
    get_articles, add_article, delete_article,
    get_companies, add_company, update_company, delete_company,
    get_snapshots, add_snapshot
)
from data.sentiment_engine import analyze

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AURA Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme state ───────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

IS_DARK = st.session_state.theme == "dark"
BG       = "#0f0f13" if IS_DARK else "#f8fafc"
CARD     = "#16161d" if IS_DARK else "#ffffff"
CARD2    = "#1c1c26" if IS_DARK else "#f1f5f9"
BORDER   = "rgba(255,255,255,0.07)" if IS_DARK else "rgba(0,0,0,0.08)"
TEXT     = "#f1f5f9" if IS_DARK else "#0f172a"
MUTED    = "#6b7280" if IS_DARK else "#475569"
PLOT_BG  = "#0f0f13" if IS_DARK else "#ffffff"
GRID_CLR = "rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.06)"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton, [data-testid="stToolbar"] {{ display: none; }}

/* Light mode text fixes */
{"" if IS_DARK else """
[data-testid="stSidebar"] * { color: #0f172a !important; }
[data-testid="stSidebar"] .stRadio label { color: #0f172a !important; font-weight: 500; }
[data-testid="stSidebar"] button { color: #0f172a !important; }
.stSelectbox label, .stTextInput label, .stTextArea label,
.stSlider label, .stNumberInput label { color: #0f172a !important; font-weight: 500; }
.stMarkdown p, .stMarkdown div { color: #0f172a; }
p, span, label, div { color: #0f172a; }

/* Fix buttons in light mode */
.stButton button { color: #0f172a !important; border-color: #e2e8f0 !important; background: #f1f5f9 !important; }
.stButton button:hover { background: #e2e8f0 !important; }

/* Dark Mode toggle button - match dark style */
[data-testid="stSidebar"] .stButton button {
    background: #1c1c26 !important;
    color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton button:hover { background: #2a2a38 !important; }

/* Radio buttons - pink when selected */
[data-testid="stSidebar"] .stRadio span[data-checked="true"] {
    background: #ec4899 !important;
    border-color: #ec4899 !important;
}
[data-testid="stSidebar"] .stRadio span { border-color: #cbd5e1 !important; }

/* Fix dark input boxes in light mode */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #94a3b8 !important; opacity: 1 !important; }
.stTextInput input { color: #0f172a !important; }
.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}
.stSelectbox div[data-baseweb="select"] span { color: #0f172a !important; }
.stSelectbox div[data-baseweb="popover"] { background: #ffffff !important; }
.stSelectbox div[data-baseweb="popover"] li { color: #0f172a !important; }
.stNumberInput button {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
}
.stDateInput input {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #0f172a !important; }
"""}

.stApp {{ background: {BG} !important; font-family: 'DM Sans', sans-serif; color: {TEXT}; }}

[data-testid="stSidebar"] {{
    background: {CARD} !important;
    border-right: 1px solid {BORDER} !important;
}}

.aura-title {{ font-size: 26px; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 2px; }}
.aura-title span {{ color: #ec4899; }}
.aura-sub {{ font-size: 13px; color: {MUTED}; margin-bottom: 24px; }}

.metric-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 20px; position: relative; overflow: hidden;
}}
.metric-card::before {{
    content: ''; position: absolute; top: -20px; right: -20px;
    width: 80px; height: 80px; border-radius: 50%; background: rgba(236,72,153,0.06);
}}
.metric-icon {{ font-size: 20px; margin-bottom: 12px; }}
.metric-value {{
    font-size: 28px; font-weight: 700; color: {TEXT};
    font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; margin-bottom: 4px;
}}
.metric-label {{ font-size: 12px; color: {MUTED}; font-weight: 500; }}
.metric-sub {{ font-size: 11px; color: {MUTED}; opacity: 0.7; margin-top: 2px; }}
.metric-badge {{
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 20px; margin-top: 8px;
}}
.badge-pos {{ background: rgba(16,185,129,0.12); color: #10b981; }}
.badge-neg {{ background: rgba(239,68,68,0.12); color: #ef4444; }}
.badge-warn {{ background: rgba(249,115,22,0.12); color: #f97316; }}

.article-card {{
    background: {CARD2}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 14px 16px; margin-bottom: 8px;
}}
.article-ticker {{ color: #ec4899; font-size: 11px; font-weight: 700; }}
.article-meta {{ color: {MUTED}; font-size: 10px; }}
.article-headline {{ color: {TEXT}; font-size: 13px; margin: 4px 0 8px; line-height: 1.4; }}

.sent-badge {{
    display: inline-block; border-radius: 20px; padding: 2px 10px;
    font-size: 10px; font-weight: 600; border: 1px solid transparent;
}}
.sent-very_positive {{ background: rgba(16,185,129,0.12); color: #10b981; border-color: rgba(16,185,129,0.2); }}
.sent-positive      {{ background: rgba(16,185,129,0.08); color: #6ee7b7; border-color: rgba(16,185,129,0.15); }}
.sent-neutral       {{ background: rgba(107,114,128,0.1); color: #9ca3af; border-color: rgba(107,114,128,0.2); }}
.sent-negative      {{ background: rgba(249,115,22,0.1);  color: #f97316; border-color: rgba(249,115,22,0.2); }}
.sent-very_negative {{ background: rgba(239,68,68,0.1);   color: #ef4444; border-color: rgba(239,68,68,0.2); }}

.company-card {{
    background: {CARD2}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 16px; margin-bottom: 8px;
}}
.company-avatar {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 36px; height: 36px; border-radius: 10px;
    background: rgba(236,72,153,0.12); color: #ec4899;
    font-size: 11px; font-weight: 700;
}}
.risk-low      {{ background: rgba(16,185,129,0.12); color: #10b981; border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 600; display:inline-block; }}
.risk-moderate {{ background: rgba(234,179,8,0.12);  color: #eab308; border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 600; display:inline-block; }}
.risk-high     {{ background: rgba(249,115,22,0.12); color: #f97316; border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 600; display:inline-block; }}
.risk-critical {{ background: rgba(239,68,68,0.12);  color: #ef4444; border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 600; display:inline-block; }}

.section-title {{
    font-size: 12px; font-weight: 600; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;
}}

.gauge-wrap {{ margin: 4px 0 2px; }}
.gauge-track {{
    width: 100%; height: 5px; background: rgba(255,255,255,0.08);
    border-radius: 10px; position: relative; margin-bottom: 4px;
}}
.gauge-fill {{ height: 100%; border-radius: 10px; }}
.gauge-labels {{ display: flex; justify-content: space-between; font-size: 9px; color: {MUTED}; }}
.gauge-score {{ font-size: 11px; font-weight: 600; text-align: center; }}

div[data-testid="stHorizontalBlock"] > div {{ gap: 12px; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def sentiment_badge(label):
    display = (label or "neutral").replace("_", " ")
    return f'<span class="sent-badge sent-{label}">{display}</span>'

def risk_badge(level):
    level = level or "low"
    return f'<span class="risk-{level}">{level.capitalize()}</span>'

def gauge_html(score, label=None):
    score = float(score or 0)
    pct = ((score + 1) / 2) * 100
    if score < -0.5:   color = "#ef4444"
    elif score < -0.2: color = "#f97316"
    elif score < 0.2:  color = "#eab308"
    elif score < 0.5:  color = "#34d399"
    else:              color = "#10b981"
    html = f"""
    <div class="gauge-wrap">
      <div class="gauge-track">
        <div class="gauge-fill" style="width:{pct:.1f}%;background:{color}"></div>
      </div>
      <div class="gauge-labels"><span>-1</span><span style="color:{color};font-weight:600">{score:.2f}</span><span>+1</span></div>
      {f'<div style="font-size:10px;color:{MUTED};text-align:center">{label}</div>' if label else ''}
    </div>"""
    return html

def metric_card_html(icon, value, label, sub=None, badge=None, badge_class="badge-pos"):
    return f"""
    <div class="metric-card">
      <div class="metric-icon">{icon}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-label">{label}</div>
      {f'<div class="metric-sub">{sub}</div>' if sub else ''}
      {f'<div class="metric-badge {badge_class}">{badge}</div>' if badge else ''}
    </div>"""

def calc_risk(score):
    if score is None: return "low"
    if score < -0.5:  return "critical"
    if score < -0.2:  return "high"
    if score < 0.1:   return "moderate"
    return "low"

def calc_trend(articles):
    if len(articles) < 2: return "stable"
    articles = sorted(articles, key=lambda a: a.get("created_date",""))
    half = len(articles) // 2
    older = sum(a.get("aggregate_score",0) for a in articles[:half]) / max(half,1)
    newer = sum(a.get("aggregate_score",0) for a in articles[half:]) / max(len(articles)-half,1)
    if newer - older > 0.05:  return "rising"
    if older - newer > 0.05:  return "falling"
    return "stable"

def trend_arrow(trend):
    return {"rising":"↑","falling":"↓","stable":"—"}.get(trend,"—")

def plotly_base(fig):
    fig.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans", color=TEXT),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=GRID_CLR, linecolor=BORDER, tickfont=dict(size=11, color=MUTED))
    fig.update_yaxes(gridcolor=GRID_CLR, linecolor=BORDER, tickfont=dict(size=11, color=MUTED))
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:16px 0 16px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:8px">
      <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#ec4899,#db2777);display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 0 20px rgba(236,72,153,0.35)">⚡</div>
      <div style="font-size:20px;font-weight:700;letter-spacing:-0.5px"><span style="color:#ec4899">AU</span><span>RA</span></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "News Feed", "Companies", "Sentiment", "Market"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🌙 Dark Mode" if not IS_DARK else "☀️ Light Mode", use_container_width=True):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if page == "Dashboard":
    st.markdown('<div class="aura-title"><span>AURA</span> Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="aura-sub">Affective Uncertainty & Risk Analytics</div>', unsafe_allow_html=True)

    articles  = get_articles()
    companies = get_companies()
    snapshots = get_snapshots()

    avg_sent = sum(a.get("aggregate_score",0) for a in articles) / max(len(articles),1)
    critical = sum(1 for c in companies if c.get("risk_level") in ("critical","high"))

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("📰", len(articles), "Articles Analyzed", "Total news articles"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card_html("🏢", len(companies), "Companies Tracked", "Active monitoring"), unsafe_allow_html=True)
    with c3:
        badge_cls = "badge-pos" if avg_sent >= 0 else "badge-neg"
        badge_lbl = "Positive" if avg_sent >= 0 else "Negative"
        st.markdown(metric_card_html("📈", f"{avg_sent:.3f}", "Avg. Sentiment", badge=badge_lbl, badge_class=badge_cls), unsafe_allow_html=True)
    with c4:
        badge_cls = "badge-warn" if critical > 0 else "badge-pos"
        badge_lbl = "Action needed" if critical > 0 else "All clear"
        st.markdown(metric_card_html("⚠️", critical, "Risk Alerts", "High / Critical", badge=badge_lbl, badge_class=badge_cls), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sentiment over time chart
    snap_df = pd.DataFrame(snapshots)
    if not snap_df.empty and "date" in snap_df.columns:
        snap_df["date"] = pd.to_datetime(snap_df["date"])
        snap_df = snap_df.sort_values("date").tail(30)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=snap_df["date"], y=snap_df["avg_sentiment"],
            fill="tozeroy", fillcolor="rgba(236,72,153,0.12)",
            line=dict(color="#ec4899", width=2.5),
            name="Sentiment"
        ))
        fig.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=1)
        fig.update_layout(title="Sentiment Over Time (Last 30 Days)", height=280,
                          showlegend=False, title_font_size=13, title_font_color=MUTED)
        st.plotly_chart(plotly_base(fig), use_container_width=True)
    elif articles:
        # Build chart from articles if no snapshots
        art_df = pd.DataFrame(articles)
        if "created_date" in art_df.columns:
            art_df["date"] = pd.to_datetime(art_df["created_date"]).dt.date
            daily = art_df.groupby("date")["aggregate_score"].mean().reset_index()
            daily.columns = ["date","sentiment"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily["date"], y=daily["sentiment"],
                fill="tozeroy", fillcolor="rgba(236,72,153,0.12)",
                line=dict(color="#ec4899", width=2.5), name="Sentiment"
            ))
            fig.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=1)
            fig.update_layout(title="Sentiment Over Time", height=280,
                              showlegend=False, title_font_size=13, title_font_color=MUTED)
            st.plotly_chart(plotly_base(fig), use_container_width=True)

    # Bottom: Recent articles + Companies
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Recent Articles</div>', unsafe_allow_html=True)
        if not articles:
            st.markdown(f'<div class="article-card" style="text-align:center;color:{MUTED};padding:32px">No articles yet. Add from News Feed.</div>', unsafe_allow_html=True)
        for a in articles[:6]:
            label = a.get("sentiment_label","neutral")
            score = a.get("aggregate_score")
            pub   = a.get("publish_date","")
            try:
                pub = datetime.strptime(pub, "%Y-%m-%d").strftime("%b %-d") if pub else ""
            except: pass
            st.markdown(f"""
            <div class="article-card">
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                <span class="article-ticker">{a.get('company','')}</span>
                <span class="article-meta">· {a.get('source','')} · {pub}</span>
              </div>
              <div class="article-headline">{a.get('headline','')[:100]}{'...' if len(a.get('headline',''))>100 else ''}</div>
              <div style="display:flex;align-items:center;gap:8px">
                {sentiment_badge(label)}
                <span style="font-size:10px;color:{MUTED}">Score: {f"{score:.3f}" if score is not None else "—"}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-title">Tracked Companies</div>', unsafe_allow_html=True)
        if not companies:
            st.markdown(f'<div class="company-card" style="text-align:center;color:{MUTED};padding:32px">No companies yet. Add from Companies page.</div>', unsafe_allow_html=True)
        for c in companies[:8]:
            sent = c.get("latest_sentiment")
            trend = c.get("sentiment_trend","stable")
            st.markdown(f"""
            <div class="company-card">
              <div style="display:flex;align-items:center;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:10px">
                  <div class="company-avatar">{c.get('ticker','??')[:2]}</div>
                  <div>
                    <div style="font-size:13px;font-weight:600;color:{TEXT}">{c.get('ticker','')}</div>
                    <div style="font-size:11px;color:{MUTED}">{c.get('name','')}</div>
                  </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px">
                  <span style="font-size:13px;color:{MUTED}">{trend_arrow(trend)}</span>
                  <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{MUTED}">{f"{sent:.2f}" if sent is not None else "—"}</span>
                  {risk_badge(c.get('risk_level','low'))}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: NEWS FEED
# ══════════════════════════════════════════════════════════════════════════════

elif page == "News Feed":
    st.markdown('<div class="aura-title">News Feed</div>', unsafe_allow_html=True)
    st.markdown('<div class="aura-sub">Analyze and track financial news sentiment</div>', unsafe_allow_html=True)

    # ── Add article form ──────────────────────────────────────────
    with st.expander("✨ Analyze New Article", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            headline = st.text_area("Headline *", placeholder="Enter the news headline or article text...", height=90)
        with col2:
            company = st.text_input("Company / Ticker *", placeholder="e.g. TSLA")
            source  = st.text_input("Source", placeholder="e.g. Reuters")
            url_in  = st.text_input("Article URL", placeholder="https://...")

        if st.button("⚡ Analyze Sentiment", type="primary", use_container_width=True):
            if headline.strip() and company.strip():
                with st.spinner("Running sentiment analysis..."):
                    scores = analyze(headline.strip(), company.strip())
                    add_article({
                        "headline":    headline.strip(),
                        "company":     company.strip().upper(),
                        "source":      source.strip() or None,
                        "url":         url_in.strip() or None,
                        "publish_date": date.today().isoformat(),
                        **scores
                    })
                st.success(f"✅ Analyzed! Sentiment: **{scores['sentiment_label'].replace('_',' ')}** (score: {scores['aggregate_score']:.3f})")
                st.rerun()
            else:
                st.error("Headline and Company/Ticker are required.")

    # ── Filters ───────────────────────────────────────────────────
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        search = st.text_input("🔍 Search", placeholder="Search headlines or companies...", label_visibility="collapsed")
    with fc2:
        filter_label = st.selectbox("Filter", ["all","very_positive","positive","neutral","negative","very_negative"],
                                    label_visibility="collapsed",
                                    format_func=lambda x: "All Sentiments" if x=="all" else x.replace("_"," ").title())

    articles = get_articles()
    filtered = [a for a in articles if
        (not search or search.lower() in a.get("headline","").lower() or search.lower() in a.get("company","").lower()) and
        (filter_label == "all" or a.get("sentiment_label") == filter_label)
    ]

    if not filtered:
        st.markdown(f'<div class="article-card" style="text-align:center;color:{MUTED};padding:48px">No articles found. Click "Analyze New Article" above to add one.</div>', unsafe_allow_html=True)

    for a in filtered:
        label = a.get("sentiment_label","neutral")
        score = a.get("aggregate_score")
        pub   = a.get("publish_date","")
        try:
            pub = datetime.strptime(pub, "%Y-%m-%d").strftime("%b %-d, %Y") if pub else ""
        except: pass

        with st.container():
            st.markdown(f"""
            <div class="article-card">
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap">
                <span class="article-ticker">{a.get('company','')}</span>
                {f'<span class="article-meta">· {a.get("source","")}</span>' if a.get('source') else ''}
                {f'<span class="article-meta">· {pub}</span>' if pub else ''}
                <span style="margin-left:auto">{sentiment_badge(label)}</span>
              </div>
              <div style="font-size:14px;font-weight:500;color:{TEXT};margin-bottom:10px;line-height:1.5">{a.get('headline','')}</div>
              <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
                <div style="flex:1;min-width:120px">
                  <div style="font-size:10px;color:{MUTED};margin-bottom:2px">VADER</div>
                  {gauge_html(a.get('vader_score',0))}
                </div>
                <div style="flex:1;min-width:120px">
                  <div style="font-size:10px;color:{MUTED};margin-bottom:2px">TextBlob</div>
                  {gauge_html(a.get('textblob_score',0))}
                </div>
                <div style="flex:1;min-width:120px">
                  <div style="font-size:10px;color:{MUTED};margin-bottom:2px">L-M</div>
                  {gauge_html(a.get('lm_score',0))}
                </div>
                <div style="flex:1;min-width:120px">
                  <div style="font-size:10px;color:{MUTED};margin-bottom:2px">FinBERT</div>
                  {gauge_html(a.get('finbert_score',0))}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            if st.button(f"🗑 Delete", key=f"del_art_{a['id']}", help="Delete this article"):
                delete_article(a["id"])
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPANIES
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Companies":
    st.markdown('<div class="aura-title">Companies</div>', unsafe_allow_html=True)
    st.markdown('<div class="aura-sub">Track and monitor company sentiment</div>', unsafe_allow_html=True)

    with st.expander("➕ Track New Company", expanded=False):
        cc1, cc2, cc3 = st.columns(3)
        with cc1: new_ticker = st.text_input("Ticker Symbol *", placeholder="e.g. AAPL")
        with cc2: new_name   = st.text_input("Company Name *", placeholder="e.g. Apple Inc.")
        with cc3: new_sector = st.text_input("Sector", placeholder="e.g. Technology")

        if st.button("🏢 Add Company", type="primary", use_container_width=True):
            if new_ticker.strip() and new_name.strip():
                result = add_company({"ticker": new_ticker.strip().upper(), "name": new_name.strip(), "sector": new_sector.strip() or None})
                if result:
                    st.success(f"✅ Now tracking {new_ticker.upper()}")
                    st.rerun()
                else:
                    st.warning(f"{new_ticker.upper()} is already being tracked.")
            else:
                st.error("Ticker and Company Name are required.")

    # Sync sentiment from articles
    companies = get_companies()
    articles  = get_articles()

    for company in companies:
        comp_arts = [a for a in articles if a.get("company","").upper() == company.get("ticker","").upper() and a.get("aggregate_score") is not None]
        if comp_arts:
            avg   = sum(a["aggregate_score"] for a in comp_arts) / len(comp_arts)
            trend = calc_trend(comp_arts)
            risk  = calc_risk(avg)
            if (abs((company.get("latest_sentiment") or 999) - avg) > 0.001 or
                company.get("sentiment_trend") != trend or
                company.get("risk_level") != risk):
                update_company(company["id"], {
                    "latest_sentiment": round(avg, 4),
                    "sentiment_trend":  trend,
                    "risk_level":       risk
                })

    companies = get_companies()

    if not companies:
        st.markdown(f'<div class="company-card" style="text-align:center;color:{MUTED};padding:48px">No companies tracked yet. Use the form above.</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, c in enumerate(companies):
            sent  = c.get("latest_sentiment")
            trend = c.get("sentiment_trend","stable")
            with cols[i % 3]:
                st.markdown(f"""
                <div class="company-card">
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                    <div style="display:flex;align-items:center;gap:10px">
                      <div class="company-avatar">{c.get('ticker','??')[:2]}</div>
                      <div>
                        <div style="font-size:14px;font-weight:600;color:{TEXT}">{c.get('ticker','')}</div>
                        <div style="font-size:11px;color:{MUTED}">{c.get('name','')}</div>
                      </div>
                    </div>
                  </div>
                  {f'<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px"><span style="color:{MUTED}">Sector</span><span style="color:{TEXT}">{c.get("sector","")}</span></div>' if c.get("sector") else ""}
                  <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:6px">
                    <span style="color:{MUTED}">Sentiment</span>
                    <span style="font-family:monospace;color:{TEXT}">{trend_arrow(trend)} {f"{sent:.3f}" if sent is not None else "—"}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px">
                    <span style="color:{MUTED}">Risk Level</span>
                    {risk_badge(c.get('risk_level','low'))}
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑 Remove", key=f"del_co_{c['id']}", use_container_width=True):
                    delete_company(c["id"])
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SENTIMENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Sentiment":
    st.markdown('<div class="aura-title">Sentiment Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="aura-sub">Multi-model sentiment breakdown</div>', unsafe_allow_html=True)

    articles  = get_articles()
    companies_list = sorted(set(a.get("company","") for a in articles if a.get("company")))

    filter_co = st.selectbox("Filter by Company", ["All Companies"] + companies_list)
    filtered  = articles if filter_co == "All Companies" else [a for a in articles if a.get("company") == filter_co]

    if not filtered:
        st.markdown(f"""
        <div style="background:{CARD2};border:1px solid {BORDER};border-radius:12px;
                    padding:48px 24px;text-align:center">
            <div style="font-size:28px;margin-bottom:12px">📰</div>
            <div style="font-size:14px;font-weight:600;color:{TEXT};margin-bottom:6px">No articles to analyze</div>
            <div style="font-size:12px;color:{MUTED}">Add news articles from the News Feed page first.</div>
        </div>""", unsafe_allow_html=True)
    else:
        LABEL_KEYS   = ["very_negative","negative","neutral","positive","very_positive"]
        LABEL_NAMES  = ["Very Negative","Negative","Neutral","Positive","Very Positive"]
        LABEL_COLORS = ["#ef4444","#f97316","#6b7280","#34d399","#10b981"]

        dist = [filtered.count(a) if False else sum(1 for a in filtered if a.get("sentiment_label")==k) for k in LABEL_KEYS]

        model_avgs = {
            "VADER":              sum(a.get("vader_score",0) for a in filtered) / len(filtered),
            "TextBlob":           sum(a.get("textblob_score",0) for a in filtered) / len(filtered),
            "Loughran-McDonald":  sum(a.get("lm_score",0) for a in filtered) / len(filtered),
            "FinBERT":            sum(a.get("finbert_score",0) for a in filtered) / len(filtered),
        }

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            pie_data = [(LABEL_NAMES[i], dist[i], LABEL_COLORS[i]) for i in range(5) if dist[i] > 0]
            if pie_data:
                fig_pie = go.Figure(go.Pie(
                    labels=[p[0] for p in pie_data],
                    values=[p[1] for p in pie_data],
                    marker_colors=[p[2] for p in pie_data],
                    hole=0.5,
                    textinfo="label+percent",
                    textfont=dict(size=11)
                ))
                fig_pie.update_layout(title="Sentiment Distribution", height=300,
                                      title_font_size=13, title_font_color=MUTED,
                                      showlegend=False)
                st.plotly_chart(plotly_base(fig_pie), use_container_width=True)

        with col2:
            # Radar chart
            radar_vals = [abs(v) for v in model_avgs.values()]
            fig_radar = go.Figure(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=list(model_avgs.keys()) + [list(model_avgs.keys())[0]],
                fill="toself", fillcolor="rgba(236,72,153,0.15)",
                line=dict(color="#ec4899", width=2),
                name="Score"
            ))
            fig_radar.update_layout(
                title="Model Agreement", height=300,
                title_font_size=13, title_font_color=MUTED,
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=9, color=MUTED), gridcolor=GRID_CLR),
                    angularaxis=dict(tickfont=dict(size=11, color=TEXT), gridcolor=GRID_CLR)
                )
            )
            st.plotly_chart(plotly_base(fig_radar), use_container_width=True)

        # Bar chart
        bar_colors = ["#10b981" if v >= 0 else "#ef4444" for v in model_avgs.values()]
        fig_bar = go.Figure(go.Bar(
            x=list(model_avgs.keys()),
            y=list(model_avgs.values()),
            marker_color=bar_colors,
            marker_line_width=0,
        ))
        fig_bar.add_hline(y=0, line_color=MUTED, line_width=1, line_dash="dot")
        fig_bar.update_layout(title="Average Score by Model", height=260,
                              title_font_size=13, title_font_color=MUTED, yaxis_range=[-1,1])
        st.plotly_chart(plotly_base(fig_bar), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MARKET CORRELATION
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Market":
    st.markdown('<div class="aura-title">Market Correlation</div>', unsafe_allow_html=True)
    st.markdown('<div class="aura-sub">Sentiment vs. market movement analysis</div>', unsafe_allow_html=True)

    snapshots = get_snapshots()
    companies_list = sorted(set(s.get("company","") for s in snapshots if s.get("company")))

    filter_co = st.selectbox("Filter by Company", ["All Companies"] + companies_list)
    filtered  = snapshots if filter_co == "All Companies" else [s for s in snapshots if s.get("company") == filter_co]
    sorted_s  = sorted(filtered, key=lambda x: x.get("date",""))

    # Add snapshot form
    with st.expander("➕ Add Market Snapshot", expanded=not bool(snapshots)):
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1: snap_co    = st.text_input("Company", placeholder="TSLA")
        with sc2: snap_date  = st.date_input("Date", value=date.today())
        with sc3: snap_price = st.number_input("Stock Price ($)", min_value=0.0, step=0.01)
        with sc4: snap_pct   = st.number_input("Price Change %", step=0.01)
        snap_sent = st.slider("Avg Sentiment", -1.0, 1.0, 0.0, 0.01)

        if st.button("💾 Save Snapshot", type="primary"):
            if snap_co.strip():
                add_snapshot({
                    "company":         snap_co.strip().upper(),
                    "date":            snap_date.isoformat(),
                    "avg_sentiment":   snap_sent,
                    "stock_price":     snap_price,
                    "price_change_pct": snap_pct,
                    "article_count":   1
                })
                st.success("Snapshot saved!")
                st.rerun()

    if not sorted_s:
        st.markdown(f"""
        <div style="background:{CARD2};border:1px solid {BORDER};border-radius:12px;
                    padding:48px 24px;text-align:center;margin-top:8px">
            <div style="font-size:28px;margin-bottom:12px">📊</div>
            <div style="font-size:14px;font-weight:600;color:{TEXT};margin-bottom:6px">No snapshot data yet</div>
            <div style="font-size:12px;color:{MUTED}">Market snapshot data will appear here once added.</div>
        </div>""", unsafe_allow_html=True)
    else:
        snap_df = pd.DataFrame(sorted_s)
        snap_df["date"] = pd.to_datetime(snap_df["date"])

        # Correlation calculation
        pairs = snap_df.dropna(subset=["avg_sentiment","price_change_pct"])
        correlation = None
        if len(pairs) >= 3:
            correlation = pairs["avg_sentiment"].corr(pairs["price_change_pct"])

        if correlation is not None:
            mc1, mc2, mc3 = st.columns(3)
            corr_color = "#10b981" if correlation > 0 else "#ef4444"
            strength   = "Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.4 else "Weak"
            strength_color = "#ec4899" if abs(correlation) > 0.5 else MUTED

            with mc1:
                st.markdown(metric_card_html("📊", f"{correlation:.4f}", "Pearson Correlation", "Sentiment ↔ Price Change"), unsafe_allow_html=True)
            with mc2:
                st.markdown(metric_card_html("📅", len(filtered), "Data Points", "Daily snapshots"), unsafe_allow_html=True)
            with mc3:
                st.markdown(metric_card_html("💡", strength, "Signal Strength", f"|r| = {abs(correlation):.3f}"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        # Dual line chart
        if "stock_price" in snap_df.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=snap_df["date"], y=snap_df["avg_sentiment"],
                name="Sentiment", line=dict(color="#ec4899", width=2),
                yaxis="y1"
            ))
            fig_line.add_trace(go.Scatter(
                x=snap_df["date"], y=snap_df["stock_price"],
                name="Price ($)", line=dict(color="#8b5cf6", width=2),
                yaxis="y2"
            ))
            fig_line.update_layout(
                title="Sentiment vs. Stock Price",
                height=320, title_font_size=13, title_font_color=MUTED,
                yaxis=dict(title="Sentiment", gridcolor=GRID_CLR, color="#ec4899"),
                yaxis2=dict(title="Price ($)", overlaying="y", side="right", color="#8b5cf6"),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(plotly_base(fig_line), use_container_width=True)

        # Scatter plot
        scatter_df = snap_df.dropna(subset=["avg_sentiment","price_change_pct"])
        if not scatter_df.empty:
            fig_scatter = px.scatter(
                scatter_df, x="avg_sentiment", y="price_change_pct",
                trendline="ols",
                color_discrete_sequence=["#ec4899"],
                labels={"avg_sentiment":"Sentiment Score","price_change_pct":"Price Change %"},
                title="Sentiment vs. Price Change Scatter"
            )
            fig_scatter.update_traces(marker=dict(opacity=0.6, size=8))
            fig_scatter.update_layout(height=320, title_font_size=13, title_font_color=MUTED)
            st.plotly_chart(plotly_base(fig_scatter), use_container_width=True)
