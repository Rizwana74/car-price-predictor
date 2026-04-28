# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  utils/data_loader.py — Load car data & model artifacts
# ─────────────────────────────────────────────

import json
import pickle
import pandas as pd
import streamlit as st
from utils.config import CAR_DATA_PATH, CSV_PATH, PREPROCESSOR_PATH, MODEL_PATH


@st.cache_data(show_spinner=False)
def load_car_lookup() -> dict:
    """Load manufacturer → model → features lookup from JSON."""
    with open(CAR_DATA_PATH, "r") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_raw_dataframe() -> pd.DataFrame:
    """Load and clean the raw CSV for visualisations."""
    df = pd.read_csv(CSV_PATH)
    df.drop(columns=["__year_resale_value", "Model"], inplace=True, errors="ignore")
    df["Launch_Year"] = pd.to_datetime(
        df["Latest_Launch"], format="%m/%d/%Y", errors="coerce"
    ).dt.year
    df.drop(columns=["Latest_Launch"], inplace=True, errors="ignore")
    df.dropna(subset=["Price_in_thousands"], inplace=True)
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    return df


@st.cache_resource(show_spinner=False)
def load_model_artifacts():
    """
    Load preprocessor and best model.
    Automatically retrains if pkl files are incompatible with
    the current numpy/sklearn/python version.
    """
    # ── First try: direct pickle load ────────────────────────────
    try:
        with open(PREPROCESSOR_PATH, "rb") as f:
            preprocessor = pickle.load(f)
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return preprocessor, model

    except Exception as first_err:
        err_str = str(first_err)

    # ── Version mismatch? Auto-retrain ────────────────────────────
    COMPAT_ERRORS = [
        "BitGenerator", "numpy.random", "cannot import",
        "No module named", "numpy", "sklearn", "module ",
    ]
    if any(kw.lower() in err_str.lower() for kw in COMPAT_ERRORS):
        import subprocess, sys, os
        from utils.config import BASE_DIR
        retrain_script = os.path.join(BASE_DIR, "retrain_model.py")
        if os.path.exists(retrain_script):
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(
                [sys.executable, retrain_script],
                capture_output=True, text=True, cwd=BASE_DIR,
                env=env,
            )
            if result.returncode == 0:
                with open(PREPROCESSOR_PATH, "rb") as f:
                    preprocessor = pickle.load(f)
                with open(MODEL_PATH, "rb") as f:
                    model = pickle.load(f)
                return preprocessor, model
            else:
                raise RuntimeError(
                    f"Auto-retrain failed. Please run manually:\n\n"
                    f"  python retrain_model.py\n\n"
                    f"Error: {result.stderr[:500]}"
                )
        else:
            raise RuntimeError(
                "Pickle version mismatch — retrain_model.py not found.\n"
                "Please run:  python retrain_model.py"
            )

    # ── Other error — re-raise ────────────────────────────────────
    raise RuntimeError(str(first_err))


# ── Lookup helpers ─────────────────────────────────────────────────────────

def get_manufacturers(car_lookup: dict) -> list:
    return sorted(car_lookup.keys())


def get_models(car_lookup: dict, manufacturer: str) -> list:
    return sorted(car_lookup.get(manufacturer, {}).keys())


def get_car_features(car_lookup: dict, manufacturer: str, model: str) -> dict:
    return car_lookup.get(manufacturer, {}).get(model, {})


def get_manufacturer_ranges(car_lookup: dict, manufacturer: str) -> dict:
    """
    Compute min/max ranges for numeric specs across all models of a manufacturer.
    """
    models = car_lookup.get(manufacturer, {})
    if not models:
        return {}

    hps = [v["horsepower"]      for v in models.values() if "horsepower"      in v]
    fes = [v["fuel_efficiency"] for v in models.values() if "fuel_efficiency" in v]
    fcs = [v["fuel_capacity"]   for v in models.values() if "fuel_capacity"   in v]
    ess = [v["engine_size"]     for v in models.values() if "engine_size"     in v]

    return {
        "hp_min":  int(min(hps))   if hps else 50,
        "hp_max":  int(max(hps))   if hps else 700,
        "fe_min":  int(min(fes))   if fes else 8,
        "fe_max":  int(max(fes))   if fes else 80,
        "fc_min":  float(min(fcs)) if fcs else 8.0,
        "fc_max":  float(max(fcs)) if fcs else 40.0,
        "es_min":  float(min(ess)) if ess else 0.5,
        "es_max":  float(max(ess)) if ess else 10.0,
    }
