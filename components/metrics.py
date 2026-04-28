# ─────────────────────────────────────────────
#  components/metrics.py — Reusable metric tiles
# ─────────────────────────────────────────────

import streamlit as st


def metric_row(items: list):
    """
    items: list of (label, value) tuples
    Renders them in equal-width columns with st.metric.
    """
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)
