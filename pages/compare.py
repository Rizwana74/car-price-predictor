# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  pages/compare.py
#  All specs locked. Only fuel efficiency is adjustable per car.
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import (
    get_manufacturers, get_models, get_car_features, get_manufacturer_ranges,
)
from utils.predictor import build_input_df, compare_two_cars


def _locked_mini(label, value, unit=""):
    return f"""
    <div style="flex:1;background:#0f1420;border:1px solid #2a3550;border-radius:10px;padding:0.65rem 0.8rem;">
        <div style="font-size:0.62rem;color:#7a90a8;text-transform:uppercase;letter-spacing:.08em;">{label} 🔒</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#64b5f6;">
            {value}{(' ' + unit) if unit else ''}
        </div>
    </div>
    """


def _car_panel(prefix, car_lookup, manufacturers, default_idx=0):
    """Render one car selection panel. Returns (mfr, model, features, fe_val)."""
    emoji = "🚗" if prefix == "A" else "🚙"
    st.markdown(
        f"<div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;"
        f"color:#e8eaf6;margin-bottom:0.6rem'>{emoji} Car {prefix}</div>",
        unsafe_allow_html=True,
    )

    mfr  = st.selectbox(f"Manufacturer {prefix}", manufacturers, index=default_idx, key=f"mfr_{prefix}")
    mdl  = st.selectbox(f"Model {prefix}", get_models(car_lookup, mfr), key=f"mdl_{prefix}")
    feat = get_car_features(car_lookup, mfr, mdl)
    rng  = get_manufacturer_ranges(car_lookup, mfr)

    # Locked spec mini-cards row
    st.markdown(
        f'<div style="display:flex;gap:8px;margin:10px 0;">'
        + _locked_mini("Engine",  f"{feat.get('engine_size','—')}", "L")
        + _locked_mini("Power",   f"{int(feat.get('horsepower',0))}", "hp")
        + _locked_mini("Weight",  f"{feat.get('curb_weight','—')}", "k lbs")
        + '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="display:flex;gap:8px;margin:0 0 10px 0;">'
        + _locked_mini("Wheelbase", f"{feat.get('wheelbase','—')}", "in")
        + _locked_mini("Fuel Tank", f"{feat.get('fuel_capacity','—')}", "gal")
        + _locked_mini("Fuel Type", feat.get("vehicle_type","—"))
        + '</div>',
        unsafe_allow_html=True,
    )

    # Fuel efficiency — only adjustable field
    fe_min = float(rng.get("fe_min", 8))
    fe_max = float(rng.get("fe_max", 80))
    fe_def = float(feat.get("fuel_efficiency", 28.0))
    fe_def = max(fe_min, min(fe_max, fe_def))

    st.markdown(
        f"<div style='font-size:0.72rem;color:#a0b8d0;margin-bottom:4px;'>"
        f"🔋 Fuel Efficiency (mpg) — Adjustable: {int(fe_min)}–{int(fe_max)} mpg</div>",
        unsafe_allow_html=True,
    )
    if fe_min == fe_max:
        fe_val = int(fe_min)
        st.markdown(
            f"<div style='background:#0f1420;border:1px solid #2a3550;border-radius:8px;"
            f"padding:0.5rem 0.8rem;color:#64b5f6;font-weight:700;font-family:Syne,sans-serif;'>"
            f"{fe_min:.0f} mpg 🔒</div>",
            unsafe_allow_html=True,
        )
    else:
        fe_val = int(st.slider(
            f"Fuel Efficiency {prefix} (mpg)",
            fe_min, fe_max, fe_def, 1.0,
            key=f"fe_{prefix}",
            label_visibility="collapsed",
        ))

    return mfr, mdl, feat, fe_val


def render(car_lookup: dict, preprocessor, model):
    st.markdown('<div class="section-head">🔀 Compare Two Cars</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">Select two cars to compare their predicted 2026 prices. '
        'All specs are auto-filled and locked from dataset. '
        'Only <b>Fuel Efficiency</b> is adjustable.</div>',
        unsafe_allow_html=True,
    )

    manufacturers = get_manufacturers(car_lookup)
    col_a, col_sep, col_b = st.columns([5, 1, 5])

    with col_a:
        mfr_a, mdl_a, feat_a, fe_a = _car_panel("A", car_lookup, manufacturers, default_idx=0)

    with col_sep:
        st.markdown(
            "<div style='text-align:center;padding-top:4rem;"
            "font-size:2rem;color:#3f51b5'>⚡</div>",
            unsafe_allow_html=True,
        )

    with col_b:
        default_b = 1 if len(manufacturers) > 1 else 0
        mfr_b, mdl_b, feat_b, fe_b = _car_panel("B", car_lookup, manufacturers, default_idx=default_b)

    st.markdown("")
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        compare_clicked = st.button("⚡  Compare Prices Now")

    if compare_clicked:
        def _make_df(mfr, feat, fe):
            hw = feat.get("horsepower", 150.0)
            cw = feat.get("curb_weight", 3.0)
            perf = float(hw) / max(float(cw), 0.1)
            return build_input_df(
                manufacturer       = mfr,
                vehicle_type       = feat.get("vehicle_type", "Passenger"),
                sales_in_thousands = feat.get("sales_in_thousands", 50.0),
                engine_size        = feat.get("engine_size", 2.0),
                horsepower         = float(hw),
                wheelbase          = feat.get("wheelbase", 107.0),
                width              = feat.get("width", 70.0),
                length             = feat.get("length", 180.0),
                curb_weight        = float(cw),
                fuel_capacity      = feat.get("fuel_capacity", 17.0),
                fuel_efficiency    = float(fe),
                power_perf_factor  = perf,
            )

        with st.spinner("Comparing…"):
            df_a = _make_df(mfr_a, feat_a, fe_a)
            df_b = _make_df(mfr_b, feat_b, fe_b)
            comp = compare_two_cars(preprocessor, model, df_a, df_b)

        st.markdown("---")
        st.markdown('<div class="section-head">📊 Comparison Results</div>', unsafe_allow_html=True)

        ca, mid, cb = st.columns([5, 2, 5])
        winner_a = comp["cheaper"] == "A"
        winner_b = comp["cheaper"] == "B"

        with ca:
            cls_a  = "compare-winner" if winner_a else "compare-loser"
            badge  = "🏆 BETTER VALUE" if winner_a else ""
            st.markdown(f"""
            <div class="{cls_a}">
                <div style="font-size:0.7rem;color:#7a90a8;letter-spacing:.1em">{badge}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;color:#e8eaf6;margin:4px 0">{mfr_a} {mdl_a}</div>
                <div style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;color:#64b5f6">${comp['price_a']:,.0f}</div>
                <div style="font-size:0.75rem;color:#7a90a8">2026 Estimated Price</div>
                <div style="font-size:0.78rem;color:#a0b8d0;margin-top:4px">⛽ {fe_a} mpg</div>
            </div>
            """, unsafe_allow_html=True)

        with mid:
            st.markdown(f"""
            <div style="text-align:center;padding-top:1.5rem">
                <div style="font-size:0.7rem;color:#7a90a8;letter-spacing:.08em;text-transform:uppercase">Difference</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:700;color:#ffb74d">${comp['diff']:,.0f}</div>
                <div style="font-size:0.75rem;color:#7a90a8">{comp['pct_diff']}% cheaper</div>
            </div>
            """, unsafe_allow_html=True)

        with cb:
            cls_b   = "compare-winner" if winner_b else "compare-loser"
            badge_b = "🏆 BETTER VALUE" if winner_b else ""
            st.markdown(f"""
            <div class="{cls_b}">
                <div style="font-size:0.7rem;color:#7a90a8;letter-spacing:.1em">{badge_b}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;color:#e8eaf6;margin:4px 0">{mfr_b} {mdl_b}</div>
                <div style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;color:#64b5f6">${comp['price_b']:,.0f}</div>
                <div style="font-size:0.75rem;color:#7a90a8">2026 Estimated Price</div>
                <div style="font-size:0.78rem;color:#a0b8d0;margin-top:4px">⛽ {fe_b} mpg</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        fig = go.Figure(go.Bar(
            x=[f"{mfr_a} {mdl_a}", f"{mfr_b} {mdl_b}"],
            y=[comp["price_a"], comp["price_b"]],
            marker_color=["#81c784" if winner_a else "#ef9a9a", "#81c784" if winner_b else "#ef9a9a"],
            text=[f"${comp['price_a']:,.0f}", f"${comp['price_b']:,.0f}"],
            textposition="outside",
            textfont={"color": "#b0bec5", "size": 12},
            width=[0.4, 0.4],
        ))
        fig.update_layout(
            paper_bgcolor="#1a1f2e", plot_bgcolor="#141929",
            font={"color": "#b0bec5"}, height=320,
            margin=dict(t=30, b=20, l=10, r=10),
            yaxis={"gridcolor": "#2a3550", "color": "#607d8b", "tickformat": "$,.0f"},
            xaxis={"color": "#b0bec5"},
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-head">📋 Full Spec Comparison</div>', unsafe_allow_html=True)
        spec_rows = {
            "Engine Size (L)":       (feat_a.get("engine_size", "—"), feat_b.get("engine_size", "—")),
            "Horsepower (hp)":       (feat_a.get("horsepower", "—"), feat_b.get("horsepower", "—")),
            "Curb Weight (×1k lbs)": (feat_a.get("curb_weight", "—"), feat_b.get("curb_weight", "—")),
            "Fuel Efficiency (mpg)": (fe_a, fe_b),
            "Fuel Capacity (gal)":   (feat_a.get("fuel_capacity", "—"), feat_b.get("fuel_capacity", "—")),
            "Wheelbase (in)":        (feat_a.get("wheelbase", "—"), feat_b.get("wheelbase", "—")),
            "Width (in)":            (feat_a.get("width", "—"), feat_b.get("width", "—")),
            "Length (in)":           (feat_a.get("length", "—"), feat_b.get("length", "—")),
        }
        spec_df = pd.DataFrame(spec_rows, index=[f"{mfr_a} {mdl_a}", f"{mfr_b} {mdl_b}"]).T
        st.dataframe(spec_df, use_container_width=True)
