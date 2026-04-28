# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  pages/visualization.py
#  Interactive Plotly visualizations.
#  FIX: _LAYOUT no longer contains xaxis/yaxis keys — those are passed
#       directly in each fig.update_layout() call to avoid
#       "multiple values for keyword argument 'xaxis'" TypeError.
# ─────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.config import THEME, INFLATION_MULTIPLIER

FG = "#b0bec5"

# ── Base layout WITHOUT xaxis/yaxis (avoids duplicate kwarg crash) ─────────
_LAYOUT_BASE = dict(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#141929",
    font={"color": "#b0bec5", "family": "DM Sans"},
    margin=dict(t=40, b=20, l=20, r=20),
)

# Default axis styles reused per-chart
_XAXIS = {"gridcolor": "#2a3550", "color": "#607d8b"}
_YAXIS = {"gridcolor": "#2a3550", "color": "#607d8b"}


def render(df: pd.DataFrame):
    # ── Sidebar filters ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.8rem;color:#90a4ae;font-weight:600'>CHART FILTERS</div>",
            unsafe_allow_html=True,
        )

        brands_all = sorted(df["Manufacturer"].dropna().unique().tolist())
        selected_brands = st.multiselect(
            "Filter Brands",
            brands_all,
            default=[],
            help="Leave empty to show all brands",
        )
        if "Vehicle_type" in df.columns:
            vtypes = sorted(df["Vehicle_type"].dropna().unique().tolist())
            selected_type = st.selectbox("Vehicle Type", ["All"] + vtypes)
        else:
            selected_type = "All"

        price_min = float(df["Price_in_thousands"].min())
        price_max = float(df["Price_in_thousands"].max())
        price_range = st.slider(
            "Price Range (thousands)",
            price_min, price_max,
            (price_min, price_max),
        )

    # ── Apply filters ──────────────────────────────────────────────────────
    fdf = df.copy()
    if selected_brands:
        fdf = fdf[fdf["Manufacturer"].isin(selected_brands)]
    if selected_type != "All" and "Vehicle_type" in fdf.columns:
        fdf = fdf[fdf["Vehicle_type"] == selected_type]
    fdf = fdf[
        (fdf["Price_in_thousands"] >= price_range[0]) &
        (fdf["Price_in_thousands"] <= price_range[1])
    ]

    if fdf.empty:
        st.warning("⚠️ No data matches current filters. Please widen your selection.")
        return

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Distribution",
        "🔥 Correlation",
        "🏷️ By Brand",
        "⚡ Performance",
        "📈 Market Insights",
    ])

    # ── TAB 1: Distribution ────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-head">Price Distribution</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.histogram(
                fdf, x="Price_in_thousands",
                nbins=30,
                color_discrete_sequence=["#3f51b5"],
                labels={"Price_in_thousands": "Price (thousands USD)"},
                title="Price Distribution",
            )
            fig.add_vline(
                x=fdf["Price_in_thousands"].median(),
                line_dash="dash", line_color="#64b5f6",
                annotation_text=f"Median: ${fdf['Price_in_thousands'].median():.1f}k",
                annotation_font_color="#64b5f6",
            )
            fig.update_layout(
                **_LAYOUT_BASE,
                title_font_color=FG,
                height=340,
                xaxis=dict(**_XAXIS),
                yaxis=dict(**_YAXIS),
            )
            fig.update_traces(marker_line_color="#0d1018", marker_line_width=1, opacity=0.85)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.scatter(
                fdf, x="Horsepower", y="Price_in_thousands",
                color="Engine_size",
                color_continuous_scale="Plasma",
                labels={"Price_in_thousands": "Price (thousands)", "Engine_size": "Engine (L)"},
                title="Horsepower vs Price",
                hover_data=["Manufacturer"],
            )
            fig2.update_layout(
                **_LAYOUT_BASE,
                title_font_color=FG,
                height=340,
                xaxis=dict(**_XAXIS),
                yaxis=dict(**_YAXIS),
                coloraxis_colorbar={
                    "tickfont": {"color": FG},
                    "title": {"text": "Engine (L)", "font": {"color": FG}},
                },
            )
            fig2.update_traces(marker=dict(opacity=0.8, size=8))
            st.plotly_chart(fig2, use_container_width=True)

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Min Price",    f"${fdf['Price_in_thousands'].min():.1f}k")
        s2.metric("Max Price",    f"${fdf['Price_in_thousands'].max():.1f}k")
        s3.metric("Mean Price",   f"${fdf['Price_in_thousands'].mean():.1f}k")
        s4.metric("Median Price", f"${fdf['Price_in_thousands'].median():.1f}k")
        s5.metric("Total Models", str(len(fdf)))

    # ── TAB 2: Correlation Heatmap ─────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-head">Feature Correlations</div>', unsafe_allow_html=True)

        num_df = fdf.select_dtypes(include="number").drop(columns=["Launch_Year"], errors="ignore")
        corr   = num_df.corr().round(2)

        fig = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            colorscale="RdBu_r",
            zmin=-1, zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 9},
            hoverongaps=False,
            colorbar={"tickfont": {"color": FG}},
        ))
        fig.update_layout(
            **_LAYOUT_BASE,
            height=500,
            title="Pearson Correlation Matrix",
            title_font_color=FG,
            xaxis={"color": "#607d8b", "tickangle": -35, "gridcolor": "transparent"},
            yaxis={"color": "#607d8b", "gridcolor": "transparent"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            '<div class="info-box">📌 Values near <b>+1.0</b> = strong positive correlation. '
            'Near <b>-1.0</b> = strong negative. Near <b>0</b> = little relationship.</div>',
            unsafe_allow_html=True,
        )

    # ── TAB 3: Price by Manufacturer ──────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-head">Average Price by Manufacturer</div>', unsafe_allow_html=True)

        avg = (
            fdf.groupby("Manufacturer")["Price_in_thousands"]
               .agg(["mean", "min", "max", "count"])
               .reset_index()
               .sort_values("mean", ascending=False)
        )
        avg.columns = ["Manufacturer", "Mean", "Min", "Max", "Count"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=avg["Manufacturer"], y=avg["Mean"],
            name="Avg Price",
            marker_color="#3f51b5",
            opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Avg: $%{y:.1f}k<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=avg["Manufacturer"], y=avg["Max"],
            mode="markers", name="Max",
            marker={"color": "#ef9a9a", "size": 7, "symbol": "triangle-up"},
            hovertemplate="<b>%{x}</b><br>Max: $%{y:.1f}k<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=avg["Manufacturer"], y=avg["Min"],
            mode="markers", name="Min",
            marker={"color": "#81c784", "size": 7, "symbol": "triangle-down"},
            hovertemplate="<b>%{x}</b><br>Min: $%{y:.1f}k<extra></extra>",
        ))
        fig.update_layout(
            **_LAYOUT_BASE,
            height=420,
            title="Price Range by Manufacturer",
            title_font_color=FG,
            legend={"font": {"color": FG}},
            xaxis={"color": "#607d8b", "tickangle": -40, "gridcolor": "transparent"},
            yaxis={"color": "#607d8b", "tickformat": "$,.0f", "gridcolor": "#2a3550"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            avg.style.format({"Mean": "${:.1f}k", "Min": "${:.1f}k", "Max": "${:.1f}k"}),
            use_container_width=True, hide_index=True,
        )

    # ── TAB 4: Performance ─────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-head">Performance Analysis</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.scatter(
                fdf, x="Curb_weight", y="Price_in_thousands",
                size="Engine_size",
                color="Fuel_efficiency",
                color_continuous_scale="RdYlGn",
                hover_data=["Manufacturer"],
                labels={
                    "Curb_weight": "Curb Weight (×1k lbs)",
                    "Price_in_thousands": "Price (thousands)",
                    "Engine_size": "Engine (L)",
                    "Fuel_efficiency": "MPG",
                },
                title="Weight vs Price (size=Engine, color=MPG)",
            )
            fig.update_layout(
                **_LAYOUT_BASE,
                title_font_color=FG,
                height=380,
                xaxis=dict(**_XAXIS),
                yaxis=dict(**_YAXIS),
                coloraxis_colorbar={"tickfont": {"color": FG}},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "Vehicle_type" in fdf.columns and fdf["Vehicle_type"].nunique() > 1:
                fig2 = px.box(
                    fdf, x="Vehicle_type", y="Fuel_efficiency",
                    color="Vehicle_type",
                    color_discrete_map={"Passenger": "#3f51b5", "Car": "#64b5f6"},
                    labels={"Fuel_efficiency": "MPG", "Vehicle_type": "Vehicle Type"},
                    title="Fuel Efficiency by Vehicle Type",
                )
                fig2.update_layout(
                    **_LAYOUT_BASE,
                    title_font_color=FG,
                    height=380,
                    xaxis=dict(**_XAXIS),
                    yaxis=dict(**_YAXIS),
                    showlegend=False,
                )
            else:
                fig2 = px.scatter(
                    fdf, x="Horsepower", y="Fuel_efficiency",
                    color="Price_in_thousands",
                    color_continuous_scale="Blues",
                    hover_data=["Manufacturer"],
                    labels={"Horsepower": "Horsepower (hp)", "Fuel_efficiency": "MPG"},
                    title="Horsepower vs Fuel Efficiency",
                )
                fig2.update_layout(
                    **_LAYOUT_BASE,
                    title_font_color=FG,
                    height=380,
                    xaxis=dict(**_XAXIS),
                    yaxis=dict(**_YAXIS),
                )
            st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 5: Market Insights ─────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-head">Market Insights</div>', unsafe_allow_html=True)

        fdf_adj = fdf.copy()
        fdf_adj["Price_2026_k"] = fdf_adj["Price_in_thousands"] * INFLATION_MULTIPLIER

        col1, col2 = st.columns(2)

        with col1:
            top10 = (
                fdf_adj.groupby("Manufacturer")["Price_2026_k"]
                       .mean().sort_values(ascending=False).head(10).reset_index()
            )
            fig = px.bar(
                top10, x="Price_2026_k", y="Manufacturer",
                orientation="h",
                color="Price_2026_k",
                color_continuous_scale=[[0, "#3f51b5"], [1, "#64b5f6"]],
                labels={"Price_2026_k": "2026 Avg Price (thousands)", "Manufacturer": ""},
                title="Top 10 Brands by 2026 Est. Price",
                text="Price_2026_k",
            )
            fig.update_traces(texttemplate="$%{text:.1f}k", textposition="outside", textfont_color=FG)
            fig.update_layout(
                **_LAYOUT_BASE,
                title_font_color=FG,
                height=380,
                showlegend=False,
                coloraxis_showscale=False,
                xaxis=dict(**_XAXIS),
                yaxis={"gridcolor": "transparent", "color": "#607d8b"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            brand_summary = (
                fdf_adj.groupby("Manufacturer").agg(
                    avg_price=("Price_2026_k", "mean"),
                    avg_mpg=("Fuel_efficiency", "mean"),
                    count=("Price_2026_k", "count"),
                ).reset_index()
            )
            fig2 = px.scatter(
                brand_summary, x="avg_mpg", y="avg_price",
                size="count", color="avg_price",
                hover_name="Manufacturer",
                color_continuous_scale="Blues_r",
                labels={
                    "avg_mpg":   "Avg Fuel Economy (MPG)",
                    "avg_price": "Avg 2026 Price (thousands)",
                },
                title="Efficiency vs Price by Brand",
                size_max=40,
            )
            fig2.update_layout(
                **_LAYOUT_BASE,
                title_font_color=FG,
                height=380,
                xaxis=dict(**_XAXIS),
                yaxis=dict(**_YAXIS),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-head">📊 Dataset Summary</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records",    str(len(fdf)))
        m2.metric("Brands",           str(fdf["Manufacturer"].nunique()))
        m3.metric("Avg 2026 Price",   f"${fdf['Price_in_thousands'].mean() * INFLATION_MULTIPLIER:.1f}k")
        m4.metric("Avg Fuel Economy", f"{fdf['Fuel_efficiency'].mean():.1f} mpg")
