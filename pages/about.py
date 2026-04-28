# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
#  pages/about.py
# ─────────────────────────────────────────────

import streamlit as st


def render():
    st.markdown('<div class="section-head">ℹ️ About This Application</div>', unsafe_allow_html=True)

    st.markdown("""
This is a **production-grade Machine Learning web app** that predicts 2026 car prices using a
model trained on real automotive sales data — with inflation adjustment, explainability,
depreciation forecasting, and interactive market visualizations.
""")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🧠 ML Pipeline")
        st.markdown("""
- **Dataset:** 157 cars, 16 features (Car Sales dataset, ~2000)
- **Cleaning:** Null imputation, Launch Year extraction, Power/Weight feature
- **Preprocessing:** StandardScaler + OneHotEncoder via `ColumnTransformer`
- **Models trained:** Linear Regression, Decision Tree, Random Forest,
  Gradient Boosting, LightGBM
- **Selection:** Highest Test R² after 5-fold cross-validation
- **Tuning:** `RandomizedSearchCV`
- **2026 adjustment:** CPI inflation multiplier ×2.08 applied to base prediction
- **Confidence band:** ±12% around prediction
""")

    with col2:
        st.markdown("#### 🏗️ App Architecture")
        st.markdown("""
```
car-price-predictor/
├── app.py               # Entry point + routing
├── pages/               # One file per page
│   ├── predict.py
│   ├── visualization.py
│   ├── compare.py
│   └── about.py
├── components/          # Reusable UI parts
│   ├── hero.py
│   ├── sidebar.py
│   └── metrics.py
├── utils/               # Logic & backend
│   ├── config.py
│   ├── data_loader.py
│   ├── predictor.py
│   ├── load_model.py
│   └── preprocess.py
├── models/              # ML artifacts
│   ├── best_model.pkl
│   └── preprocessor.pkl
├── data/
│   ├── Car_sales.csv
│   └── car_data.json
└── assets/
    └── styles.css
```
""")

    st.markdown("#### ⚙️ Key Design Decisions")
    st.markdown("""
- **All specs are auto-filled & locked** from the dataset when you select a manufacturer + model.
  This ensures predictions use accurate, real-world values rather than user guesses.
- **Wheelbase, Width, Length, Curb Weight, Engine Size, Horsepower, Fuel Capacity** are all
  locked read-only tiles — they are fixed for that specific model in the dataset.
- **Fuel Efficiency** is the *only* adjustable field, clamped to the manufacturer's actual
  model range — so you can explore realistic efficiency scenarios without impossible values.
- All specs update dynamically when you change the manufacturer or model selection.
""")

    st.markdown("#### 📦 Tech Stack")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Framework",  "Streamlit")
    c2.metric("ML Library", "Scikit-learn")
    c3.metric("Boosting",   "LightGBM")
    c4.metric("Charts",     "Plotly")
