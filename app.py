"""Consumer360 interactive dashboard UI (brand-configurable + stakeholder views)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
BRAND_FILE = ROOT / "config" / "brand.yaml"


def load_brand() -> dict:
    defaults = {
        "product_name": "Consumer360",
        "company_name": "Retail Intelligence Lab",
        "tagline": "Precision Growth Engine",
        "primary_color": "#0f766e",
        "secondary_color": "#f59e0b",
        "accent_color": "#0284c7",
        "danger_color": "#dc2626",
        "success_color": "#15803d",
        "bg_base": "#f4efe7",
        "bg_grad_1": "#ffd9a9",
        "bg_grad_2": "#b9f2ea",
        "text_primary": "#101010",
        "text_muted": "#5f5f5f",
        "card_bg": "rgba(255, 255, 255, 0.62)",
        "font_display": "DM Serif Display",
        "font_body": "Space Grotesk",
        "logo_path": "",
    }

    if BRAND_FILE.exists():
        with BRAND_FILE.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        brand = raw.get("brand", {})
        defaults.update({k: v for k, v in brand.items() if v is not None})
    return defaults


BRAND = load_brand()
st.set_page_config(page_title=f"{BRAND['product_name']} | Retail Intelligence", page_icon="C", layout="wide")


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Serif+Display:ital@0;1&display=swap');

        :root {{
            --bg: {BRAND['bg_base']};
            --text: {BRAND['text_primary']};
            --muted: {BRAND['text_muted']};
            --card: {BRAND['card_bg']};
            --line: rgba(16, 16, 16, 0.08);
            --accent: {BRAND['primary_color']};
            --accent2: {BRAND['secondary_color']};
            --accent3: {BRAND['accent_color']};
            --danger: {BRAND['danger_color']};
            --ok: {BRAND['success_color']};
        }}

        .stApp {{
            background:
                radial-gradient(1300px 600px at 85% -10%, {BRAND['bg_grad_1']} 0%, transparent 55%),
                radial-gradient(900px 500px at -5% 120%, {BRAND['bg_grad_2']} 0%, transparent 50%),
                linear-gradient(160deg, #faf7f2 0%, #eee6da 100%);
            color: var(--text);
        }}

        html, body, [class*="css"] {{ font-family: '{BRAND['font_body']}', sans-serif; }}
        h1, h2, h3 {{ font-family: '{BRAND['font_display']}', serif; letter-spacing: 0.3px; }}

        .hero {{
            background: linear-gradient(135deg, rgba(16,16,16,0.95), rgba(28,42,37,0.92));
            color: #fff;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px 24px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.2);
        }}

        .metric-card {{
            background: var(--card);
            border: 1px solid var(--line);
            backdrop-filter: blur(8px);
            border-radius: 16px;
            padding: 14px 16px;
            min-height: 96px;
        }}

        .metric-label {{ color: var(--muted); font-size: 13px; }}
        .metric-value {{ font-size: 26px; font-weight: 700; line-height: 1.2; color: var(--text); }}
        .kpi-up {{ color: var(--ok); font-weight: 700; }}
        .kpi-down {{ color: var(--danger); font-weight: 700; }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #fff7eb 0%, #f1f8f7 100%);
            border-right: 1px solid var(--line);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame | dict]:
    data: dict[str, pd.DataFrame | dict] = {}
    csv_map = {
        "rfm": "customer_rfm_segments.csv",
        "cohort": "cohort_retention.csv",
        "clv": "customer_clv.csv",
        "mba": "market_basket_rules.csv",
        "sales_trend": "sales_trend.csv",
        "top_products_revenue": "top_products_revenue.csv",
        "top_products_volume": "top_products_volume.csv",
        "revenue_by_region": "revenue_by_region.csv",
        "champions": "campaign_champions.csv",
        "churn": "campaign_churn_risk.csv",
    }
    for k, v in csv_map.items():
        p = REPORTS / v
        data[k] = pd.read_csv(p) if p.exists() else pd.DataFrame()

    summary_path = REPORTS / "kpi_summary.json"
    if summary_path.exists():
        with summary_path.open("r", encoding="utf-8") as f:
            data["summary"] = json.load(f)
    else:
        data["summary"] = {"total_revenue": 0, "total_customers": 0, "total_orders": 0, "avg_order_value": 0}

    if not data["sales_trend"].empty and "order_month" in data["sales_trend"].columns:
        data["sales_trend"]["order_month"] = pd.to_datetime(data["sales_trend"]["order_month"])
    if not data["cohort"].empty and "cohort_month" in data["cohort"].columns:
        data["cohort"]["cohort_month"] = pd.to_datetime(data["cohort"]["cohort_month"])
    return data


def render_header(summary: dict) -> None:
    logo_path = str(BRAND.get("logo_path", "")).strip()
    cols = st.columns([0.12, 0.88]) if logo_path and Path(logo_path).exists() else st.columns([1])

    if len(cols) > 1:
        with cols[0]:
            st.image(logo_path, use_column_width=True)
        with cols[1]:
            st.markdown(
                f"""
                <div class="hero">
                    <h1 style="margin:0;">{BRAND['product_name']}</h1>
                    <p style="margin:6px 0 0 0;opacity:0.84;">{BRAND['company_name']} | {BRAND['tagline']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div class="hero">
                <h1 style="margin:0;">{BRAND['product_name']}</h1>
                <p style="margin:6px 0 0 0;opacity:0.84;">{BRAND['company_name']} | {BRAND['tagline']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><div class='metric-label'>Total Revenue</div><div class='metric-value'>${summary.get('total_revenue', 0):,.0f}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-label'>Customers</div><div class='metric-value'>{summary.get('total_customers', 0):,}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-label'>Orders</div><div class='metric-value'>{summary.get('total_orders', 0):,}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='metric-label'>Avg Order Value</div><div class='metric-value'>${summary.get('avg_order_value', 0):,.2f}</div></div>", unsafe_allow_html=True)


def render_cmo_view(data: dict) -> None:
    trend = data["sales_trend"].copy()
    region = data["revenue_by_region"].copy()
    rfm = data["rfm"].copy()

    if trend.empty or region.empty or rfm.empty:
        st.warning("Pipeline outputs missing. Run `python -m src.main` first.")
        return

    latest = trend.iloc[-1]
    growth_class = "kpi-up" if latest.get("mom_growth_pct", 0) >= 0 else "kpi-down"
    st.markdown(f"<p>Latest MoM Growth: <span class='{growth_class}'>{latest.get('mom_growth_pct', 0):.2f}%</span></p>", unsafe_allow_html=True)

    a, b = st.columns([1.7, 1.1])
    with a:
        fig = px.area(trend, x="order_month", y="total_revenue", line_shape="spline", color_discrete_sequence=[BRAND["primary_color"]], title="Revenue Trend")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig2 = px.pie(region, names="region", values="region_revenue", hole=0.5, color_discrete_sequence=[BRAND["primary_color"], BRAND["secondary_color"], BRAND["accent_color"], "#84cc16", "#f97316"], title="Revenue by Region")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    seg = rfm.groupby("segment", as_index=False).agg(customers=("customer_id", "nunique"), revenue=("monetary", "sum")).sort_values("revenue", ascending=False)
    fig3 = px.bar(seg, x="segment", y="revenue", color="customers", color_continuous_scale="Teal", title="Segment Revenue Concentration")
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, use_container_width=True)


def render_retention_view(data: dict) -> None:
    cohort = data["cohort"].copy()
    churn = data["churn"].copy()
    rfm = data["rfm"].copy()

    if cohort.empty or rfm.empty:
        st.warning("Retention outputs missing. Run pipeline first.")
        return

    pivot = cohort.pivot_table(index="cohort_month", columns="cohort_index", values="retention_rate", aggfunc="mean")
    heat = go.Figure(data=go.Heatmap(z=pivot.values, x=[str(c) for c in pivot.columns], y=[pd.to_datetime(i).strftime("%Y-%m") for i in pivot.index], colorscale=[[0, "#fef3c7"], [0.45, BRAND["secondary_color"]], [1, BRAND["primary_color"]]], colorbar=dict(title="Retention")))
    heat.update_layout(title="Cohort Retention", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(heat, use_container_width=True)

    c1, c2 = st.columns([1.1, 1.9])
    with c1:
        risk_count = len(churn) if not churn.empty else 0
        st.metric("Churn Risk Customers", f"{risk_count:,}")
        st.metric("Churn Risk %", f"{(risk_count / max(len(rfm), 1)) * 100:.1f}%")
    with c2:
        if churn.empty:
            st.info("No churn-risk rows available.")
        else:
            st.dataframe(churn.sort_values("recency_days", ascending=False).head(200), use_container_width=True, height=320)


def render_regional_view(data: dict, region: str) -> None:
    rfm = data["rfm"].copy()
    champs = data["champions"].copy()
    churn = data["churn"].copy()
    clv = data["clv"].copy()

    if region != "All":
        if not rfm.empty and "region" in rfm.columns:
            rfm = rfm[rfm["region"].astype(str) == region]
        if not champs.empty and "region" in champs.columns:
            champs = champs[champs["region"].astype(str) == region]
        if not churn.empty and "region" in churn.columns:
            churn = churn[churn["region"].astype(str) == region]

    x, y, z = st.columns(3)
    x.metric("Active Customers", f"{rfm['customer_id'].nunique() if not rfm.empty else 0:,}")
    x.metric("Champions", f"{len(champs):,}")
    y.metric("Churn Risk", f"{len(churn):,}")
    y.metric("Churn Share", f"{(len(churn) / max(len(rfm), 1)) * 100:.1f}%")
    z.metric("Avg CLV", f"${clv['predicted_clv'].dropna().mean() if not clv.empty else 0:,.0f}")
    z.metric("Median Monetary", f"${rfm['monetary'].median() if not rfm.empty else 0:,.0f}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Champion Activation List")
        st.dataframe(champs.sort_values("monetary", ascending=False).head(200), use_container_width=True, height=360)
    with c2:
        st.subheader("Retention Priority List")
        st.dataframe(churn.sort_values("recency_days", ascending=False).head(200), use_container_width=True, height=360)


def render_advanced_tabs(data: dict) -> None:
    t1, t2 = st.tabs(["RFM Deep Dive", "Market Basket and CLV"])

    with t1:
        rfm = data["rfm"].copy()
        if rfm.empty:
            st.info("RFM data not available")
        else:
            fig = px.scatter(rfm, x="frequency", y="monetary", color="segment", size="m_score", hover_data=["customer_id", "recency_days"], log_y=True, color_discrete_sequence=px.colors.qualitative.Bold, title="RFM Bubble Map")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        mba = data["mba"].copy()
        clv = data["clv"].copy()
        c1, c2 = st.columns([1.1, 1.4])
        with c1:
            st.subheader("Cross-Sell Rules")
            st.dataframe(mba.head(100) if not mba.empty else pd.DataFrame(), use_container_width=True, height=300)
        with c2:
            if clv.empty or "predicted_clv" not in clv.columns:
                st.info("CLV output unavailable")
            else:
                top = clv.dropna(subset=["predicted_clv"]).sort_values("predicted_clv", ascending=False).head(20)
                fig2 = px.bar(top, x="customer_id", y="predicted_clv", color="predicted_clv", color_continuous_scale=[[0, "#cffafe"], [0.5, BRAND["primary_color"]], [1, "#115e59"]], title="Top Predicted CLV")
                fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Customer", yaxis_title="Predicted CLV")
                fig2.update_xaxes(showticklabels=False)
                st.plotly_chart(fig2, use_container_width=True)


def main() -> None:
    inject_styles()

    if not REPORTS.exists():
        st.error("`reports/` not found. Run `python -m src.main` first.")
        st.stop()

    data = load_data()
    rfm = data["rfm"]
    regions = ["All"]
    if not rfm.empty and "region" in rfm.columns:
        regions += sorted(rfm["region"].dropna().astype(str).unique().tolist())

    st.sidebar.title(f"{BRAND['product_name']} Controls")
    stakeholder = st.sidebar.radio("Stakeholder Mode", ["CMO View", "Retention View", "Regional View"], index=0)
    region = st.sidebar.selectbox("Region", regions, index=0)

    render_header(data["summary"])

    if stakeholder == "CMO View":
        render_cmo_view(data)
    elif stakeholder == "Retention View":
        render_retention_view(data)
    else:
        render_regional_view(data, region)

    st.markdown("---")
    render_advanced_tabs(data)


if __name__ == "__main__":
    main()
