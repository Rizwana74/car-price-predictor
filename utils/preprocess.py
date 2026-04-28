# ─────────────────────────────────────────────
#  utils/preprocess.py — Data preprocessing helpers
# ─────────────────────────────────────────────

import pandas as pd
import numpy as np


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare raw CSV dataframe."""
    df = df.copy()
    df.drop(columns=["__year_resale_value", "Model"], inplace=True, errors="ignore")
    df["Launch_Year"] = pd.to_datetime(
        df.get("Latest_Launch", pd.Series(dtype=str)),
        format="%m/%d/%Y",
        errors="coerce",
    ).dt.year
    df.drop(columns=["Latest_Launch"], inplace=True, errors="ignore")
    df.dropna(subset=["Price_in_thousands"], inplace=True)
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    return df
