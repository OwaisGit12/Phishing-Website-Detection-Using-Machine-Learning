# inspect_model.py
import joblib
import pandas as pd
import os

MODEL = "model.pkl"
path = os.path.join(os.path.dirname(__file__), MODEL)
m = joblib.load(path)
print("MODEL TYPE:", type(m))

# Try multiple ways to get expected feature names
fn = None
try:
    fn = getattr(m, "feature_names_in_", None)
    if fn is not None:
        print("feature_names_in_ (sklearn):", list(fn))
except Exception as e:
    print("feature_names_in_ error:", e)

# XGBoost booster case
try:
    booster = getattr(m, "get_booster", None)
    if booster:
        b = m.get_booster()
        fnb = b.feature_names
        print("booster.feature_names (xgboost):", fnb)
except Exception as e:
    print("booster feature_names error:", e)

# If it's a pipeline, try to find the final estimator
try:
    from sklearn.pipeline import Pipeline
    if isinstance(m, Pipeline):
        print("Model is a sklearn Pipeline. Steps:", m.named_steps.keys())
except Exception:
    pass

# Print repr to help debug
print("Model repr (short):", repr(m)[:1000])
