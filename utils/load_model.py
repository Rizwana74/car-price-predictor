# ─────────────────────────────────────────────
#  utils/load_model.py
#  Safe model loader — handles pickle version mismatches gracefully.
#  If the stored .pkl files are incompatible with the current
#  numpy/sklearn version, it automatically retrains the model.
# ─────────────────────────────────────────────

import os
import pickle
import subprocess
import sys

from utils.config import MODEL_PATH, PREPROCESSOR_PATH, BASE_DIR


def safe_load_artifacts():
    """
    Try to load preprocessor + model from pkl.
    If loading fails due to version incompatibility, auto-retrain.
    Returns (preprocessor, model).
    """
    try:
        with open(PREPROCESSOR_PATH, "rb") as f:
            preprocessor = pickle.load(f)
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return preprocessor, model

    except Exception as e:
        err = str(e)
        # Known numpy/sklearn pickle incompatibility errors
        if any(kw in err for kw in [
            "BitGenerator", "numpy.random", "cannot import",
            "No module named", "sklearn", "module 'numpy'",
        ]):
            return _auto_retrain()
        raise


def _auto_retrain():
    """Run retrain_model.py in a subprocess and reload the artifacts."""
    retrain_script = os.path.join(BASE_DIR, "retrain_model.py")
    if not os.path.exists(retrain_script):
        raise FileNotFoundError(
            f"retrain_model.py not found at {retrain_script}. "
            "Please run: python retrain_model.py"
        )

    result = subprocess.run(
        [sys.executable, retrain_script],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Auto-retrain failed:\n{result.stderr}\n\n"
            "Please run manually: python retrain_model.py"
        )

    # Reload freshly generated artifacts
    with open(PREPROCESSOR_PATH, "rb") as f:
        preprocessor = pickle.load(f)
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    return preprocessor, model
