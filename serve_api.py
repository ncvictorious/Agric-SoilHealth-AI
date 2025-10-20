# serve_api.py
import os, uuid, json
from datetime import date
import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

DATA_DIR = "data"
OUT_DIR = "outputs"

# load panels & model
PANELS = pd.read_csv(os.path.join(DATA_DIR, "panels.csv"))
MODEL = joblib.load(os.path.join(OUT_DIR, "risk_model_hgb.pkl"))

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

class ScoreRequest(BaseModel):
    field_id: str
    date: str = Field(..., description="YYYY-MM-DD")

class Driver(BaseModel):
    feature: str
    value: float | int | None = None
    impact: float

class Action(BaseModel):
    role: str
    action: str

class AlertResponse(BaseModel):
    alert_id: str
    field_id: str
    date: str
    alert_type: str
    score: float
    priority: str
    top_drivers: list[Driver]
    plain_language: str
    recommended_actions: list[Action]
    model_version: str
    status: str

app = FastAPI(title="Healthy Soils AI – Alert API", version="0.1.0")

@app.get("/")
def root():
    return {"ok": True}

@app.post("/score", response_model=AlertResponse)
def score(req: ScoreRequest):
    # select the row for field/date; fallback to nearest date if exact missing
    df = PANELS[(PANELS.field_id == req.field_id) & (PANELS.date == req.date)]
    if df.empty:
        # fallback: use the latest available for that field
        df = PANELS[PANELS.field_id == req.field_id].sort_values("date").tail(1)
        if df.empty:
            # fallback to any field
            df = PANELS.sort_values("date").tail(1)
    row = df.iloc[0]

    X = row[FEATURES].values.reshape(1, -1)
    proba = float(MODEL.predict_proba(X)[0,1])
    pr = priority(proba)

    drivers = [
        {"feature":"kg_N_applied_last_30d","value": float(row["kg_N_applied_last_30d"]), "impact": +0.30},
        {"feature":"recent_heavy_rain_48h","value": float(row["recent_heavy_rain_48h"]), "impact": +0.25},
        {"feature":"ndvi_mean_30d","value": float(row["ndvi_mean_30d"]), "impact": -0.20},
    ]

    msg = (
        f"Predicted nitrate/runoff risk {proba:.2f} ({pr}). "
        f"Drivers: N applied={row['kg_N_applied_last_30d']:.1f} kg/ha (30d), "
        f"rain(48h)={row['recent_heavy_rain_48h']:.1f} mm, "
        f"NDVI~{row['ndvi_mean_30d']:.2f}."
    )
    actions = [
        {"role":"Farmer","action":"Delay further N; consider split applications once soils drain."},
        {"role":"Advisor","action":"Assess buffer strips downslope; schedule lab resample if >6 months old."}
    ]

    alert = {
        "alert_id": f"AL-{uuid.uuid4().hex[:8]}",
        "field_id": row["field_id"],
        "date": str(row["date"]),
        "alert_type": "Nitrate_Surplus",
        "score": round(proba, 3),
        "priority": pr,
        "top_drivers": drivers,
        "plain_language": msg,
        "recommended_actions": actions,
        "model_version": "hgb-v0",
        "status": "open"
    }
    return alert
