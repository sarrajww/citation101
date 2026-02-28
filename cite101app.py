import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Citation Source Analytics",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0f1117; }
    [data-testid="stSidebar"] { background: #1a1d2e; }
    .metric-card {
        background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
        border: 1px solid #2e3450;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #7c9ffc; margin: 0; }
    .metric-label { font-size: 0.85rem; color: #8892b0; margin-top: 4px; letter-spacing: 0.05em; text-transform: uppercase; }
    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #cdd6f4;
        border-left: 3px solid #7c9ffc; padding-left: 10px;
        margin-bottom: 16px;
    }
    div[data-testid="stTabs"] button { color: #8892b0; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #7c9ffc; border-bottom-color: #7c9ffc; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    institution = pd.read_csv(DATA_DIR / "institution.txt", sep="\t")
    institution.columns = institution.columns.str.strip()
    institution["count"] = pd.to_numeric(institution["count"], errors="coerce").fillna(0).astype(int)

    topic = pd.read_csv(DATA_DIR / "topic.txt", sep="\t")
    topic.columns = topic.columns.str.strip()
    topic["count"] = pd.to_numeric(topic["count"], errors="coerce").fillna(0).astype(int)

    ctype = pd.read_csv(DATA_DIR / "type.txt", sep="\t")
    ctype.columns = ctype.columns.str.strip()
    ctype["count"] = pd.to_numeric(ctype["count"], errors="coerce").fillna(0).astype(int)

    return institution, topic, ctype

institution_df, topic_df, type_df = load_data()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Citation Analytics")
    st.markdown("---")

    st.markdown("### Display Settings")
    top_n_inst = st.slider("Top N Institutions", 5, len(institution_df), 15)
    top_n_topic = st.slider("Top N Topics", 5, len(topic_df), 12)

    if "country" in institution_df.columns:
        all_countries = ["All"] + sorted(institution_df["country"].dropna().unique().tolist())
        sel_country = st.selectbox("Filter by Country", all_countries)
    else:
        sel_country = "All"

    st.markdown("---")
    st.markdown("### Dataset Summary")
    st.markdown(f"🏛 **{len(institution_df)}** institutions")
    st.markdown(f"🏷 **{len(topic_df)}** topics")
    st.markdown(f"📄 **{len(type_df)}** citation types")

# ── Apply filters ─────────────────────────────────────────
inst_filtered = institution_df.copy()
if sel_country != "All" and "country" in inst_filtered.columns:
    inst_filtered = inst_filtered[inst_filtered["country"] == sel_country]

inst_top = inst_filtered.nlargest(top_n_inst, "count")
topic_top = topic_df.nlargest(top_n_topic, "count")

# ── Header ────────────────────────────────────────────────
st.markdown("# 📚 Citation Source Analytics")
st.markdown("Visualizing the distribution of academic citation sources across institutions, topics, and publication types.")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
total_citations = institution_df["count"].sum()
total_types = type_df["count"].sum()
top_inst = institution_df.nlargest(1, "count").iloc[0]["name"]
top_topic = topic_df.nlargest(1, "count").iloc[0]["name"]

for col, val, label in [
    (c1, f"{total_citations:,}", "Total Institution Citations"),
    (c2, f"{len(institution_df['country'].dropna().unique()) if 'country' in institution_df.columns else '—'}", "Countries Represented"),
    (c3, top_inst.split()[-1] if len(top_inst) > 20 else top_inst, "Top Institution"),
    (c4, top_topic, "Top Topic"),
]:
    col.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{val}</p>
        <p class="metric-label">{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏛 Institutions", "🏷 Topics", "📄 Publication Types"])

COLORS = px.colors.qualitative.Pastel

# ═══════════════════════════════════════════════════════════
# TAB 1 — Institutions
# ═══════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown('<p class="section-title">Top Institutions by Citation Count</p>', unsafe_allow_html=True)
        fig_bar = px.bar(
            inst_top.sort_values("count"),
            x="count", y="name",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            text="count",
            hover_data={"country": True} if "country" in inst_top.columns else {},
        )
        fig_bar.update_traces(textposition="outside", textfont_size=11)
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            yaxis_title="", xaxis_title="Citations",
            coloraxis_showscale=False,
            margin=dict(l=0, r=40, t=10, b=10),
            height=420,
        )
        fig_bar.update_xaxes(gridcolor="#2e3450")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        if "country" in institution_df.columns:
            st.markdown('<p class="section-title">Citations by Country</p>', unsafe_allow_html=True)
            country_sum = institution_df.groupby("country")["count"].sum().reset_index().nlargest(12, "count")
            fig_pie = px.pie(
                country_sum, names="country", values="count",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#cdd6f4",
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=10),
                height=420,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Treemap
    if "country" in inst_filtered.columns:
        st.markdown('<p class="section-title">Institution Treemap</p>', unsafe_allow_html=True)
        fig_tree = px.treemap(
            inst_top,
            path=["country", "name"],
            values="count",
            color="count",
            color_continuous_scale="Blues",
        )
        fig_tree.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            margin=dict(l=0, r=0, t=10, b=10),
            height=350,
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    # Raw table
    with st.expander("📋 View Raw Data"):
        st.dataframe(inst_filtered.sort_values("count", ascending=False).reset_index(drop=True),
                     use_container_width=True, height=300)

# ═══════════════════════════════════════════════════════════
# TAB 2 — Topics
# ═══════════════════════════════════════════════════════════
with tab2:
    col_l, col_r = st.columns([2, 3], gap="large")

    with col_l:
        st.markdown('<p class="section-title">Topic Distribution</p>', unsafe_allow_html=True)
        fig_pie2 = px.pie(
            topic_top, names="name", values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie2.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            height=400,
        )
        st.plotly_chart(fig_pie2, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-title">Topic Ranking</p>', unsafe_allow_html=True)
        topic_sorted = topic_top.sort_values("count", ascending=True)
        fig_topic = px.bar(
            topic_sorted, x="count", y="name",
            orientation="h",
            color="count",
            color_continuous_scale="Teal",
            text="count",
        )
        fig_topic.update_traces(textposition="outside", textfont_size=11)
        fig_topic.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            yaxis_title="", xaxis_title="Citations",
            coloraxis_showscale=False,
            margin=dict(l=0, r=40, t=10, b=10),
            height=400,
        )
        fig_topic.update_xaxes(gridcolor="#2e3450")
        st.plotly_chart(fig_topic, use_container_width=True)

    # Word-cloud style bubble
    st.markdown('<p class="section-title">Topic Bubble Chart</p>', unsafe_allow_html=True)
    fig_bubble = px.scatter(
        topic_df, x=range(len(topic_df)), y=[1]*len(topic_df),
        size="count", text="name",
        color="count", color_continuous_scale="Teal",
        size_max=80,
    )
    fig_bubble.update_traces(textposition="middle center", textfont=dict(size=11, color="white"))
    fig_bubble.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#cdd6f4",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        coloraxis_showscale=False,
        showlegend=False,
        height=280,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    with st.expander("📋 View Raw Data"):
        st.dataframe(topic_df.sort_values("count", ascending=False).reset_index(drop=True),
                     use_container_width=True, height=300)

# ═══════════════════════════════════════════════════════════
# TAB 3 — Publication Types
# ═══════════════════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown('<p class="section-title">Publication Type Breakdown</p>', unsafe_allow_html=True)
        fig_donut = px.pie(
            type_df, names="name", values="count",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_donut.update_traces(
            textposition="outside",
            textinfo="label+percent",
            pull=[0.05 if i == 0 else 0 for i in range(len(type_df))],
        )
        fig_donut.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=420,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-title">Citation Volume by Type</p>', unsafe_allow_html=True)
        type_sorted = type_df.sort_values("count", ascending=True)
        fig_hbar = go.Figure(go.Bar(
            x=type_sorted["count"],
            y=type_sorted["name"],
            orientation="h",
            marker=dict(
                color=type_sorted["count"],
                colorscale="Purples",
                line=dict(color="rgba(0,0,0,0)"),
            ),
            text=type_sorted["count"],
            textposition="outside",
        ))
        fig_hbar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
            xaxis=dict(title="Citations", gridcolor="#2e3450"),
            yaxis_title="",
            margin=dict(l=0, r=60, t=10, b=10),
            height=420,
        )
        st.plotly_chart(fig_hbar, use_container_width=True)

    # Cumulative share
    st.markdown('<p class="section-title">Cumulative Share</p>', unsafe_allow_html=True)
    type_cum = type_df.sort_values("count", ascending=False).copy()
    type_cum["cumulative_pct"] = type_cum["count"].cumsum() / type_cum["count"].sum() * 100
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Bar(
        x=type_cum["name"], y=type_cum["count"],
        name="Count", marker_color="#7c9ffc", opacity=0.7,
    ))
    fig_cum.add_trace(go.Scatter(
        x=type_cum["name"], y=type_cum["cumulative_pct"],
        name="Cumulative %", yaxis="y2",
        line=dict(color="#f38ba8", width=2.5),
        marker=dict(size=6),
    ))
    fig_cum.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#cdd6f4",
        yaxis=dict(title="Count", gridcolor="#2e3450"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=60, t=30, b=10),
        height=320,
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    with st.expander("📋 View Raw Data"):
        st.dataframe(type_df.sort_values("count", ascending=False).reset_index(drop=True),
                     use_container_width=True, height=300)

# ── Footer ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p style="text-align:center; color:#4a5568; font-size:0.8rem;">Citation Source Analytics · Built with Streamlit & Plotly</p>', unsafe_allow_html=True)
