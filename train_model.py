# train_model.py
import os, json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import HistGradientBoostingClassifier
import matplotlib.pyplot as plt
import joblib

DATA_DIR = "data"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(DATA_DIR, "panels.csv"))

feature_cols = [
    "ndvi","ndvi_mean_30d","recent_heavy_rain_48h","kg_N_applied_last_30d",
    "ph","organic_matter_pct","nitrate_mgkg","phosphorus_mgkg","potassium_mgkg",
    "slope_mean","flow_accumulation"
]
df = df.dropna(subset=feature_cols + ["risk_label"]).copy()

X = df[feature_cols].values
y = df["risk_label"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

model = HistGradientBoostingClassifier(random_state=42)
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)[:,1]
pred = (proba >= 0.5).astype(int)

metrics = {
    "auc": float(roc_auc_score(y_test, proba)),
    "accuracy": float(accuracy_score(y_test, pred)),
}
prec, rec, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", zero_division=0)
metrics.update({"precision": float(prec), "recall": float(rec), "f1": float(f1)})

# permutation importance (simple, no extra deps)
from sklearn.inspection import permutation_importance
pi = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42)
imp = pd.DataFrame({"feature": feature_cols, "importance": pi.importances_mean}).sort_values("importance", ascending=False)

# save artifacts
joblib.dump(model, os.path.join(OUT_DIR, "risk_model_hgb.pkl"))
with open(os.path.join(OUT_DIR, "metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

plt.figure(figsize=(7,4))
plt.bar(imp["feature"], imp["importance"])
plt.xticks(rotation=45, ha="right")
plt.title("Permutation Importance (test set)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "feature_importance.png"), dpi=160)

print("✅ Model trained and saved to ./outputs/")
print("   metrics:", metrics)
print("   feature_importance.png written.")
