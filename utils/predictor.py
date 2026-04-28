# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  utils/predictor.py — Prediction + Explainability
# ─────────────────────────────────────────────

import pandas as pd
import numpy as np
from utils.config import (
    FEATURE_COLUMNS, NUMERIC_FEATURES, FEATURE_LABELS,
    LAUNCH_YEAR, INFLATION_MULTIPLIER,
    FUEL_PRICE_2026, AVG_MILES_PER_YEAR,
)


def build_input_df(
    manufacturer: str,
    vehicle_type: str,
    sales_in_thousands: float,
    engine_size: float,
    horsepower: float,
    wheelbase: float,
    width: float,
    length: float,
    curb_weight: float,
    fuel_capacity: float,
    fuel_efficiency: float,
    power_perf_factor: float,
) -> pd.DataFrame:
    """Assemble a single-row DataFrame matching training feature columns."""
    return pd.DataFrame([{
        "Manufacturer":       manufacturer,
        "Sales_in_thousands": sales_in_thousands,
        "Vehicle_type":       vehicle_type,
        "Engine_size":        engine_size,
        "Horsepower":         horsepower,
        "Wheelbase":          wheelbase,
        "Width":              width,
        "Length":             length,
        "Curb_weight":        curb_weight,
        "Fuel_capacity":      fuel_capacity,
        "Fuel_efficiency":    fuel_efficiency,
        "Launch_Year":        LAUNCH_YEAR,
        "Power_perf_factor":  power_perf_factor,
    }])


def predict_price(preprocessor, model, input_df: pd.DataFrame) -> dict:
    processed    = preprocessor.transform(input_df)
    base_k       = float(model.predict(processed)[0])
    adjusted_k   = base_k * INFLATION_MULTIPLIER
    adjusted_usd = adjusted_k * 1000

    low  = adjusted_usd * 0.88
    high = adjusted_usd * 1.12

    insights = _build_insights(model, preprocessor, input_df, adjusted_usd)

    mpg         = float(input_df["Fuel_efficiency"].iloc[0])
    annual_cost = (AVG_MILES_PER_YEAR / mpg) * FUEL_PRICE_2026 if mpg > 0 else 0

    if adjusted_k < 20:
        segment = ("Budget", "🟢")
    elif adjusted_k < 40:
        segment = ("Mid-Range", "🔵")
    elif adjusted_k < 70:
        segment = ("Premium", "🟠")
    else:
        segment = ("Luxury", "🔴")

    return {
        "base_price_k":     round(base_k, 2),
        "adjusted_price_k": round(adjusted_k, 2),
        "price_usd":        round(adjusted_usd, 0),
        "confidence_low":   round(low, 0),
        "confidence_high":  round(high, 0),
        "insights":         insights,
        "annual_fuel_cost": round(annual_cost, 0),
        "segment":          segment[0],
        "segment_icon":     segment[1],
    }


def _build_insights(model, preprocessor, input_df: pd.DataFrame, price_usd: float) -> list:
    insights = []
    try:
        importances = model.feature_importances_
    except AttributeError:
        return insights

    try:
        all_feature_names = (
            list(preprocessor.get_feature_names_out())
            if hasattr(preprocessor, "get_feature_names_out")
            else []
        )
        if not all_feature_names:
            return insights

        imp_dict = dict(zip(all_feature_names, importances))
        numeric_imp = {}
        for raw_name in NUMERIC_FEATURES:
            for key in imp_dict:
                if key == f"num__{raw_name}" or key == raw_name:
                    numeric_imp[raw_name] = imp_dict[key]
                    break

        if not numeric_imp:
            return insights

        sorted_feats = sorted(numeric_imp.items(), key=lambda x: x[1], reverse=True)[:5]
        row = input_df.iloc[0]

        for feat_name, imp in sorted_feats:
            val   = float(row.get(feat_name, 0))
            label = FEATURE_LABELS.get(feat_name, feat_name)
            pct   = round(imp * 100, 1)

            if feat_name in ("Horsepower", "Engine_size", "Power_perf_factor"):
                direction = "positive" if val > 150 else "neutral"
                desc = f"{label} of {val:.1f} {'boosted' if direction=='positive' else 'had moderate impact on'} the price"
            elif feat_name == "Fuel_efficiency":
                direction = "positive" if val > 30 else "negative"
                desc = f"{'High' if val>30 else 'Lower'} fuel efficiency ({val:.0f} mpg) {'adds' if val>30 else 'slightly reduced'} value"
            elif feat_name == "Curb_weight":
                direction = "neutral"
                desc = f"Vehicle weight ({val:.2f}k lbs) contributes to the build quality rating"
            elif feat_name == "Sales_in_thousands":
                direction = "positive" if val > 30 else "neutral"
                desc = f"{'High' if val>30 else 'Moderate'} sales volume ({val:.0f}k units) reflects brand demand"
            else:
                direction = "neutral"
                desc = f"{label} ({val:.1f}) is a contributing factor"

            insights.append({
                "label":       label,
                "direction":   direction,
                "description": desc,
                "impact_pct":  pct,
            })
    except Exception:
        pass

    return insights


def compare_two_cars(preprocessor, model, input_df_a: pd.DataFrame, input_df_b: pd.DataFrame) -> dict:
    processed_a = preprocessor.transform(input_df_a)
    processed_b = preprocessor.transform(input_df_b)
    price_a = float(model.predict(processed_a)[0]) * INFLATION_MULTIPLIER * 1000
    price_b = float(model.predict(processed_b)[0]) * INFLATION_MULTIPLIER * 1000
    diff    = price_a - price_b
    cheaper = "A" if price_a < price_b else "B"
    return {
        "price_a":  round(price_a, 0),
        "price_b":  round(price_b, 0),
        "diff":     abs(round(diff, 0)),
        "cheaper":  cheaper,
        "pct_diff": round(abs(diff) / max(price_a, price_b) * 100, 1),
    }


def depreciation_schedule(price_usd: float, years: int = 10) -> list:
    rates    = [0.20, 0.15, 0.15, 0.10, 0.10, 0.08, 0.08, 0.07, 0.07, 0.06]
    schedule = [{"year": 2026, "value": round(price_usd, 0)}]
    val      = price_usd
    for i in range(min(years, len(rates))):
        val *= (1 - rates[i])
        schedule.append({"year": 2026 + i + 1, "value": round(val, 0)})
    return schedule
