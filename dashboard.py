# dashboard.py
import os
import pandas as pd
import joblib
import streamlit as st

DATA_DIR = "data"
OUT_DIR = "outputs"

st.set_page_config(page_title="Healthy Soils – Alert Demo", layout="wide")

panels = pd.read_csv(os.path.join(DATA_DIR, "panels.csv"))
fields = sorted(panels["field_id"].unique().tolist())
dates = sorted(panels["date"].unique().tolist())

model = joblib.load(os.path.join(OUT_DIR, "risk_model_hgb.pkl"))

FEATURES = [
    "ndvi","ndvi_mean_30d","recent_heavy_rain_48h","kg_N_applied_last_30d",
    "ph","organic_matter_pct","nitrate_mgkg","phosphorus_mgkg","potassium_mgkg",
    "slope_mean","flow_accumulation"
]

def priority(p):
    if p >= 0.8: return "Red"
    if p >= 0.6: return "Amber"
    if p >= 0.4: return "Yellow"
    return "Green"

st.title("Healthy Soils – Preliminary Alert Dashboard")

col1, col2 = st.columns(2)
with col1:
    fid = st.selectbox("Field", fields, index=0)
with col2:
    dt = st.selectbox("Date", dates, index=len(dates)-1)

row = panels[(panels.field_id == fid) & (panels.date == dt)]
if row.empty:
    st.warning("No record for that field/date — showing latest.")
    row = panels[panels.field_id == fid].sort_values("date").tail(1)
r = row.iloc[0]

X = r[FEATURES].values.reshape(1, -1)
proba = float(model.predict_proba(X)[0,1])
pr = priority(proba)

st.subheader("Alert Card")
st.markdown(f"""
**Type:** Nitrate_Surplus  
**Score:** `{proba:.3f}` — **Priority:** :{pr.lower()}_circle: **{pr}**  
**Drivers:**  
- kg_N_applied_last_30d = {r['kg_N_applied_last_30d']:.1f} kg/ha  
- recent_heavy_rain_48h = {r['recent_heavy_rain_48h']:.1f} mm  
- ndvi_mean_30d ≈ {r['ndvi_mean_30d']:.2f}  
""")

st.subheader("Feature snapshot")
st.dataframe(r[["field_id","date"] + FEATURES])
