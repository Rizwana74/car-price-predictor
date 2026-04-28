# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  components/sidebar.py — Sidebar navigation
# ─────────────────────────────────────────────

import streamlit as st


def render(car_lookup: dict, artifacts_ok: bool, missing_msg: str = "") -> str:
    with st.sidebar:
        st.markdown("""
        <div style='padding:0.5rem 0 1rem'>
            <div style='font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:#e8eaf6'>
                🚗 Car Price Predictor
            </div>
            <div style='font-size:0.72rem;color:#7090a0;margin-top:3px'>
                2026 Edition &nbsp;·&nbsp; ML Powered
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["🔮  Predict Price", "🔀  Compare Cars", "📊  Visualizations", "ℹ️  About"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        if artifacts_ok:
            n_brands = len(car_lookup)
            n_models = sum(len(v) for v in car_lookup.values())
            st.markdown(f"""
            <div style='font-size:0.75rem;color:#8aabb0;line-height:1.8'>
                <div style='color:#81c784;'>● Models loaded</div>
                <div style='color:#81c784;'>● Dataset ready</div>
                <div style='color:#81c784;'>{n_brands} manufacturers · {n_models} models</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Missing model files!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Streamlit · Scikit-learn\nLightGBM · Plotly")

    return page
