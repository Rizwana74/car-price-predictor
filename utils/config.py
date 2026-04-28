# ─────────────────────────────────────────────
#  utils/config.py — Central configuration
# ─────────────────────────────────────────────

import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR          = os.path.join(BASE_DIR, "data")
CAR_DATA_PATH     = os.path.join(DATA_DIR, "car_data.json")
CSV_PATH          = os.path.join(DATA_DIR, "Car_sales.csv")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")
MODEL_PATH        = os.path.join(BASE_DIR, "models", "best_model.pkl")

# ── Inflation multiplier ───────────────────────────────────────────────────
# Original dataset from ~2000. CPI-adjusted to 2026 (×2.08).
INFLATION_MULTIPLIER = 2.08

# ── Feature columns expected by the model ─────────────────────────────────
FEATURE_COLUMNS = [
    "Manufacturer",
    "Sales_in_thousands",
    "Vehicle_type",
    "Engine_size",
    "Horsepower",
    "Wheelbase",
    "Width",
    "Length",
    "Curb_weight",
    "Fuel_capacity",
    "Fuel_efficiency",
    "Launch_Year",
    "Power_perf_factor",
]

NUMERIC_FEATURES = [
    "Sales_in_thousands",
    "Engine_size",
    "Horsepower",
    "Wheelbase",
    "Width",
    "Length",
    "Curb_weight",
    "Fuel_capacity",
    "Fuel_efficiency",
    "Launch_Year",
    "Power_perf_factor",
]

FEATURE_LABELS = {
    "Sales_in_thousands": "Sales Volume",
    "Engine_size":        "Engine Size",
    "Horsepower":         "Horsepower",
    "Wheelbase":          "Wheelbase",
    "Width":              "Width",
    "Length":             "Length",
    "Curb_weight":        "Curb Weight",
    "Fuel_capacity":      "Fuel Capacity",
    "Fuel_efficiency":    "Fuel Efficiency",
    "Launch_Year":        "Launch Year",
    "Power_perf_factor":  "Power/Weight Ratio",
}

# ── Launch year for predictions ────────────────────────────────────────────
LAUNCH_YEAR = 2026

# ── 2026 average fuel price estimate (USD/gal) ─────────────────────────────
FUEL_PRICE_2026    = 3.80
AVG_MILES_PER_YEAR = 15_000

# ── Theme palette ──────────────────────────────────────────────────────────
THEME = {
    "bg_dark":      "#0d1018",
    "bg_card":      "#1a1f2e",
    "bg_deep":      "#12151f",
    "border":       "#2a3550",
    "accent":       "#3f51b5",
    "accent_light": "#64b5f6",
    "accent2":      "#7c4dff",
    "text_primary": "#e8eaf6",
    "text_muted":   "#90a4ae",
    "text_dim":     "#607d8b",
    "green":        "#81c784",
    "amber":        "#ffb74d",
    "red":          "#ef9a9a",
}
