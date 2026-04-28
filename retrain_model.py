# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────────
#  retrain_model.py
#  Regenerates best_model.pkl and preprocessor.pkl for YOUR
#  current Python / NumPy / scikit-learn version.
#
#  Usage:
#    pip install -r requirements.txt
#    python retrain_model.py
#    streamlit run app.py
# ─────────────────────────────────────────────────────────────────

import sys
import os

# Force UTF-8 stdout so Windows cp1252 terminals never crash
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Auto-install missing packages before importing them ───────────
def _ensure(pkg, import_name=None):
    import importlib, subprocess
    name = import_name or pkg
    try:
        importlib.import_module(name)
    except ImportError:
        print(f"[setup] Installing {pkg} ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg, "-q"]
        )

_ensure("pandas")
_ensure("numpy")
_ensure("scikit-learn", "sklearn")
_ensure("lightgbm")

# ── Now safe to import ────────────────────────────────────────────
import pickle
import pandas as pd
import numpy as np

from sklearn.pipeline        import Pipeline
from sklearn.compose         import ColumnTransformer
from sklearn.preprocessing   import StandardScaler, OneHotEncoder
from sklearn.impute          import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics         import mean_absolute_error, r2_score
from lightgbm                import LGBMRegressor

# ── Paths ─────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
CSV_PATH          = os.path.join(BASE_DIR, "data", "Car_sales.csv")
MODEL_PATH        = os.path.join(BASE_DIR, "models", "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")

# ── Feature definitions (must match utils/config.py) ──────────────
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
CATEGORICAL_FEATURES = ["Manufacturer", "Vehicle_type"]
TARGET               = "Price_in_thousands"

# ── 1. Load & clean data ──────────────────────────────────────────
print("[1/5] Loading data ...")
df = pd.read_csv(CSV_PATH)

df.drop(columns=["__year_resale_value", "Model"], inplace=True, errors="ignore")
df["Launch_Year"] = pd.to_datetime(
    df["Latest_Launch"], format="%m/%d/%Y", errors="coerce"
).dt.year
df.drop(columns=["Latest_Launch"], inplace=True, errors="ignore")
df.dropna(subset=[TARGET], inplace=True)

num_cols = df.select_dtypes(include="number").columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Derived feature
df["Power_perf_factor"] = df["Horsepower"] / df["Curb_weight"].replace(0, 1)

print(f"      Loaded {len(df)} rows, {df.shape[1]} columns")

# ── 2. Split ──────────────────────────────────────────────────────
print("[2/5] Splitting train / test ...")
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
X = df[ALL_FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── 3. Build preprocessor ─────────────────────────────────────────
print("[3/5] Building preprocessor ...")

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot",  OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer,     NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])

preprocessor.fit(X_train)

# ── 4. Train LightGBM ─────────────────────────────────────────────
print("[4/5] Training LightGBM model ...")

model = LGBMRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1,
)

X_train_proc = preprocessor.transform(X_train)
X_test_proc  = preprocessor.transform(X_test)

model.fit(X_train_proc, y_train)

y_pred = model.predict(X_test_proc)
mae    = mean_absolute_error(y_test, y_pred)
r2     = r2_score(y_test, y_pred)

print(f"      MAE : ${mae:.2f}k   |   R2 : {r2:.4f}")

# ── 5. Save ───────────────────────────────────────────────────────
print("[5/5] Saving model artifacts ...")
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)

with open(PREPROCESSOR_PATH, "wb") as f:
    pickle.dump(preprocessor, f, protocol=4)
print(f"      Saved: {PREPROCESSOR_PATH}")

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f, protocol=4)
print(f"      Saved: {MODEL_PATH}")

print("")
print("=" * 55)
print("  Done! Model files regenerated for your Python version.")
print("  Run:  streamlit run app.py")
print("=" * 55)
