# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  components/hero.py — Hero banner
# ─────────────────────────────────────────────

import streamlit as st


def render():
    st.markdown("""
<div class="hero-box">
    <div class="hero-badge">ML · Regression · 2026 Prices · Explainable AI</div>
    <p class="hero-title">🚗 Car Price Predictor Pro</p>
    <p class="hero-sub">
        Select a manufacturer and model — all specs auto-fill instantly from the dataset.
        Only fuel efficiency is adjustable within real manufacturer ranges.
        Get an inflation-adjusted 2026 price with AI insights, depreciation forecast,
        and fuel cost estimates.
    </p>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-num">2026</div>
            <div class="hero-stat-label">Price Year</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-num">±12%</div>
            <div class="hero-stat-label">Confidence</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-num">×2.08</div>
            <div class="hero-stat-label">CPI Adjustment</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-num">10yr</div>
            <div class="hero-stat-label">Depreciation</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
