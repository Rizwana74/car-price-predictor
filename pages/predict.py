# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  pages/predict.py
#  ALL specs auto-fill & lock from the selected manufacturer+model.
#  ONLY Fuel Efficiency is adjustable, clamped to the manufacturer range.
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import (
    get_manufacturers, get_models, get_car_features, get_manufacturer_ranges,
)
from utils.predictor   import build_input_df, predict_price, depreciation_schedule
from utils.config      import THEME, FUEL_PRICE_2026, AVG_MILES_PER_YEAR


def _locked_card(label, value, unit="", col_obj=None):
    """Render a read-only spec tile."""
    html = f"""
    <div class="spec-locked">
        <div class="spec-locked-label">{label} 🔒</div>
        <div class="spec-locked-value">{value}{(' ' + unit) if unit else ''}</div>
    </div>
    """
    if col_obj:
        col_obj.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render(car_lookup: dict, preprocessor, model):
    # ── Step 1: Manufacturer & Model ──────────────────────────────────────
    st.markdown('<div class="section-head">🏭 Step 1 — Select Manufacturer & Model</div>', unsafe_allow_html=True)

    col_mfr, col_mdl = st.columns(2)
    with col_mfr:
        manufacturers = get_manufacturers(car_lookup)
        manufacturer  = st.selectbox(
            "Manufacturer",
            manufacturers,
            help="Choose a car brand — all specs auto-fill from dataset",
        )
    with col_mdl:
        models_list = get_models(car_lookup, manufacturer)
        car_model   = st.selectbox(
            "Model",
            models_list,
            help="Models are filtered by the selected manufacturer",
        )

    # ── Auto-fill features ────────────────────────────────────────────────
    features   = get_car_features(car_lookup, manufacturer, car_model)
    mfr_ranges = get_manufacturer_ranges(car_lookup, manufacturer)

    if features:
        st.markdown(
            f'<div class="info-box">✅ <b>All specs auto-filled</b> from dataset for '
            f'<b>{manufacturer} {car_model}</b>. '
            f'All values are locked to the real data. Only <b>Fuel Efficiency</b> '
            f'can be adjusted within the manufacturer\'s actual range.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="warn-box">⚠️ No historical data found for this combination. '
            'Default values are shown.</div>',
            unsafe_allow_html=True,
        )

    # ── Extract all spec values ───────────────────────────────────────────
    engine_size  = float(features.get("engine_size",  2.0))
    horsepower   = float(features.get("horsepower",   150.0))
    vehicle_type = features.get("vehicle_type", "Passenger")
    wheelbase    = float(features.get("wheelbase",    107.0))
    width        = float(features.get("width",        70.0))
    length       = float(features.get("length",       180.0))
    curb_weight  = float(features.get("curb_weight",  3.0))
    sales_k      = float(features.get("sales_in_thousands", 50.0))
    fuel_capacity = float(features.get("fuel_capacity", 17.0))

    # Fuel efficiency range for slider
    fe_min = float(mfr_ranges.get("fe_min", 8))
    fe_max = float(mfr_ranges.get("fe_max", 80))
    fe_default = float(features.get("fuel_efficiency", 28.0))
    fe_default = max(fe_min, min(fe_max, fe_default))

    # ── Step 2: Specs layout ──────────────────────────────────────────────
    st.markdown('<div class="section-head">⚙️ Step 2 — Car Specifications (Auto-Filled)</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # ── Column 1: Engine & Power (LOCKED) ────────────────────────────────
    with c1:
        st.markdown(
            "<div style='font-size:0.8rem;font-weight:600;color:#a0b8d0;"
            "text-transform:uppercase;letter-spacing:.06em;margin-bottom:0.6rem'>"
            "🔧 Engine & Power</div>",
            unsafe_allow_html=True,
        )
        _locked_card("Engine Size", f"{engine_size:.1f}", "L")
        _locked_card("Horsepower", f"{int(horsepower)}", "hp")
        _locked_card("Vehicle Type", vehicle_type)

    # ── Column 2: Dimensions (LOCKED) ────────────────────────────────────
    with c2:
        st.markdown(
            "<div style='font-size:0.8rem;font-weight:600;color:#a0b8d0;"
            "text-transform:uppercase;letter-spacing:.06em;margin-bottom:0.6rem'>"
            "📐 Dimensions</div>",
            unsafe_allow_html=True,
        )
        _locked_card("Wheelbase", f"{wheelbase:.1f}", "in")
        _locked_card("Width",     f"{width:.1f}",     "in")
        _locked_card("Length",    f"{length:.1f}",    "in")

    # ── Column 3: Weight & Fuel ──────────────────────────────────────────
    with c3:
        st.markdown(
            "<div style='font-size:0.8rem;font-weight:600;color:#a0b8d0;"
            "text-transform:uppercase;letter-spacing:.06em;margin-bottom:0.6rem'>"
            "⚖️ Weight & Fuel</div>",
            unsafe_allow_html=True,
        )
        _locked_card("Curb Weight",   f"{curb_weight:.3f}", "×1000 lbs")
        _locked_card("Fuel Capacity", f"{fuel_capacity:.1f}", "gal")

        # ── ONLY adjustable field ─────────────────────────────────────────
        st.markdown(
            f"<div style='margin-top:0.8rem'>"
            f"<div style='font-size:0.68rem;color:#a0b8d0;text-transform:uppercase;"
            f"letter-spacing:.08em;margin-bottom:4px;'>🔋 Fuel Efficiency (mpg)</div>"
            f"<div style='font-size:0.72rem;color:#5a7a9a;margin-bottom:6px;'>"
            f"Adjustable · Range: {int(fe_min)}–{int(fe_max)} mpg</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if fe_min == fe_max:
            fuel_efficiency_val = int(fe_min)
            _locked_card("Fuel Efficiency", f"{fuel_efficiency_val}", "mpg")
        else:
            fuel_efficiency_val = st.slider(
                "Fuel Efficiency (mpg)",
                min_value=fe_min,
                max_value=fe_max,
                value=fe_default,
                step=1.0,
                key="pred_fe",
                label_visibility="collapsed",
            )
            fuel_efficiency_val = int(fuel_efficiency_val)

    # Derived feature
    perf_factor = (horsepower / curb_weight) if curb_weight > 0 else float(features.get("power_perf_factor", 50.0))

    # ── Step 2b: Full Summary ─────────────────────────────────────────────
    with st.expander("📋 Full Specification Summary", expanded=False):
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Engine",        f"{engine_size} L")
        sc2.metric("Horsepower",    f"{int(horsepower)} hp")
        sc3.metric("Curb Weight",   f"{curb_weight:.2f}k lbs")
        sc4.metric("Power/Weight",  f"{perf_factor:.1f}")
        sc5, sc6, sc7, sc8 = st.columns(4)
        sc5.metric("Fuel Tank",     f"{fuel_capacity:.1f} gal")
        sc6.metric("Fuel Economy",  f"{fuel_efficiency_val} mpg")
        sc7.metric("Wheelbase",     f"{wheelbase} in")
        sc8.metric("Vehicle Type",  vehicle_type)

    st.markdown("")

    # ── Predict Button ────────────────────────────────────────────────────
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        predict_clicked = st.button("🔮  Predict 2026 Price", key="pred_btn")

    if predict_clicked:
        input_df = build_input_df(
            manufacturer       = manufacturer,
            vehicle_type       = vehicle_type,
            sales_in_thousands = sales_k,
            engine_size        = engine_size,
            horsepower         = horsepower,
            wheelbase          = wheelbase,
            width              = width,
            length             = length,
            curb_weight        = curb_weight,
            fuel_capacity      = fuel_capacity,
            fuel_efficiency    = float(fuel_efficiency_val),
            power_perf_factor  = perf_factor,
        )

        with st.spinner("Calculating 2026 price estimate…"):
            result = predict_price(preprocessor, model, input_df)

        _render_result(result, manufacturer, car_model, input_df)


# ── Result rendering ─────────────────────────────────────────────────────────
def _render_result(result: dict, manufacturer: str, car_model: str, input_df: pd.DataFrame):
    st.markdown("---")
    st.markdown('<div class="section-head">💰 2026 Price Prediction</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    segment_colors = {
        "Budget":    ("#81c784", "rgba(129,199,132,0.15)", "rgba(129,199,132,0.3)"),
        "Mid-Range": ("#64b5f6", "rgba(100,181,246,0.15)", "rgba(100,181,246,0.3)"),
        "Premium":   ("#ffb74d", "rgba(255,183,77,0.15)",  "rgba(255,183,77,0.3)"),
        "Luxury":    ("#ef9a9a", "rgba(239,154,154,0.15)", "rgba(239,154,154,0.3)"),
    }
    seg = result["segment"]
    seg_col, seg_bg, seg_border = segment_colors.get(seg, segment_colors["Mid-Range"])

    with left:
        st.markdown(f"""
        <div class="result-wrapper">
            <div class="year-tag">2026 ESTIMATED PRICE</div>
            <div class="result-label">{manufacturer} {car_model}</div>
            <div class="result-price">${result['price_usd']:,.0f}</div>
            <div class="result-sub">
                Base prediction: ${result['base_price_k']:.2f}k
                &nbsp;→&nbsp; ×2.08 inflation adjustment
            </div>
            <div class="result-band">
                📊 Confidence range:&nbsp;
                <strong>${result['confidence_low']:,.0f}</strong>
                &nbsp;–&nbsp;
                <strong>${result['confidence_high']:,.0f}</strong>
            </div>
            <div style="margin-top:0.8rem">
                <span class="segment-badge"
                      style="background:{seg_bg};border:1px solid {seg_border};color:{seg_col}">
                    {result['segment_icon']} {seg} Segment
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-head" style="margin-top:0">🧠 Price Drivers</div>', unsafe_allow_html=True)
        insights = result.get("insights", [])
        if insights:
            for ins in insights:
                icon = "✅" if ins["direction"] == "positive" else ("❌" if ins["direction"] == "negative" else "🔵")
                cls  = f"insight-{ins['direction']}"
                st.markdown(f"""
                <div class="insight-row {cls}">
                    <span class="insight-icon">{icon}</span>
                    <div>
                        <div class="insight-label">{ins['label']}</div>
                        <div class="insight-text">{ins['description']}</div>
                        <div class="insight-pct">Impact weight: {ins['impact_pct']}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                Feature importance insights are available for tree-based models
                (Random Forest, Gradient Boosting, LightGBM).
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="section-head">📊 Market Position</div>', unsafe_allow_html=True)
    _render_gauge(result)

    st.markdown('<div class="section-head">📉 Depreciation Forecast (2026–2036)</div>', unsafe_allow_html=True)
    _render_depreciation(result)

    st.markdown('<div class="section-head">⛽ Annual Running Costs (2026)</div>', unsafe_allow_html=True)
    _render_fuel_costs(result, input_df)


def _render_gauge(result: dict):
    price_k = result["adjusted_price_k"]
    low_k   = result["confidence_low"]  / 1000
    high_k  = result["confidence_high"] / 1000

    fig = go.Figure(go.Indicator(
        mode   = "gauge+number+delta",
        value  = price_k,
        number = {"prefix": "$", "suffix": "k", "font": {"size": 36, "color": "#64b5f6", "family": "Syne"}},
        delta  = {"reference": 30, "increasing": {"color": "#ef9a9a"}, "decreasing": {"color": "#81c784"}},
        gauge  = {
            "axis":  {"range": [0, 160], "tickcolor": "#607d8b", "tickfont": {"size": 10, "color": "#607d8b"}},
            "bar":   {"color": "#3f51b5", "thickness": 0.25},
            "bgcolor": "#141929",
            "bordercolor": "#2a3550",
            "steps": [
                {"range": [0, 20],   "color": "rgba(129,199,132,0.2)"},
                {"range": [20, 40],  "color": "rgba(100,181,246,0.15)"},
                {"range": [40, 70],  "color": "rgba(255,183,77,0.15)"},
                {"range": [70, 160], "color": "rgba(239,154,154,0.15)"},
            ],
            "threshold": {"line": {"color": "#ffffff", "width": 2}, "thickness": 0.75, "value": price_k},
        },
        title = {"text": "2026 Price vs Market Segments (Budget / Mid / Premium / Luxury)",
                 "font": {"size": 12, "color": "#90a4ae"}},
    ))
    fig.update_layout(
        paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
        font={"color": "#b0bec5"}, height=280,
        margin=dict(t=40, b=10, l=10, r=10),
    )
    fig.add_annotation(
        x=0.5, y=0.1, xref="paper", yref="paper",
        text=f"Confidence range: ${low_k:.0f}k – ${high_k:.0f}k",
        showarrow=False, font={"size": 11, "color": "#7986cb"},
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_depreciation(result: dict):
    schedule = depreciation_schedule(result["price_usd"], years=10)
    df = pd.DataFrame(schedule)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["value"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(63,81,181,0.12)",
        line={"color": "#64b5f6", "width": 2.5},
        marker={"size": 7, "color": "#64b5f6"},
        hovertemplate="<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_annotation(x=df["year"].iloc[0],  y=df["value"].iloc[0],
                       text=f"<b>${df['value'].iloc[0]:,.0f}</b>",
                       showarrow=False, yshift=16, font={"color": "#81c784", "size": 11})
    fig.add_annotation(x=df["year"].iloc[-1], y=df["value"].iloc[-1],
                       text=f"<b>${df['value'].iloc[-1]:,.0f}</b>",
                       showarrow=False, yshift=16, font={"color": "#ef9a9a", "size": 11})
    fig.update_layout(
        paper_bgcolor="#1a1f2e", plot_bgcolor="#141929",
        font={"color": "#b0bec5"}, height=300,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis={"title": "Year", "gridcolor": "#2a3550", "color": "#607d8b", "tickmode": "linear"},
        yaxis={"title": "Estimated Value (USD)", "gridcolor": "#2a3550", "color": "#607d8b", "tickformat": "$,.0f"},
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    retained = df["value"].iloc[-1] / df["value"].iloc[0] * 100
    d1, d2, d3 = st.columns(3)
    d1.metric("Purchase Price (2026)", f"${result['price_usd']:,.0f}")
    d2.metric("10-Year Value (2036)",  f"${df['value'].iloc[-1]:,.0f}")
    d3.metric("Value Retained",        f"{retained:.1f}%", delta=f"-{100-retained:.1f}%")


def _render_fuel_costs(result: dict, input_df: pd.DataFrame):
    mpg      = float(input_df["Fuel_efficiency"].iloc[0])
    gal_year = AVG_MILES_PER_YEAR / mpg if mpg > 0 else 0
    annual   = gal_year * FUEL_PRICE_2026
    monthly  = annual / 12
    per_mile = (FUEL_PRICE_2026 / mpg) if mpg > 0 else 0

    years      = list(range(2026, 2032))
    price_proj = [FUEL_PRICE_2026 * (1.03 ** i) for i in range(6)]
    costs      = [(AVG_MILES_PER_YEAR / mpg) * p for p in price_proj]

    fig = go.Figure(go.Bar(
        x=years, y=costs,
        marker_color="#3f51b5",
        text=[f"${c:,.0f}" for c in costs],
        textposition="outside",
        textfont={"color": "#90a4ae", "size": 10},
        hovertemplate="<b>%{x}</b><br>Annual Fuel Cost: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#1a1f2e", plot_bgcolor="#141929",
        font={"color": "#b0bec5"}, height=260,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis={"gridcolor": "#2a3550", "color": "#607d8b"},
        yaxis={"gridcolor": "#2a3550", "color": "#607d8b", "tickformat": "$,.0f"},
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Annual Fuel Cost", f"${annual:,.0f}")
    f2.metric("Monthly Cost",     f"${monthly:,.0f}")
    f3.metric("Cost Per Mile",    f"${per_mile:.2f}")
    f4.metric("Fuel Economy",     f"{mpg:.0f} mpg")

    st.markdown(
        f'<div class="info-box">📌 Estimates based on {AVG_MILES_PER_YEAR:,} miles/year '
        f'at ${FUEL_PRICE_2026}/gal (2026 projection). Fuel price escalated at 3%/yr for 5-year chart.</div>',
        unsafe_allow_html=True,
    )
