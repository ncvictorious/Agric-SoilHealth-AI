# generate_data.py
import os, json, random, math
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

def rectangle_polygon(lon, lat, width_deg=0.004, height_deg=0.003):
    xw, yh = width_deg/2, height_deg/2
    return [[[ # GeoJSON polygon ring
        [lon - xw, lat - yh],
        [lon + xw, lat - yh],
        [lon + xw, lat + yh],
        [lon - xw, lat + yh],
        [lon - xw, lat - yh]
    ]]]

# 1) fields
num_fields = 50
LON_MIN, LON_MAX = -4.2, -3.7
LAT_MIN, LAT_MAX = 51.55, 51.85

fields = []
for i in range(num_fields):
    lon = np.random.uniform(LON_MIN, LON_MAX)
    lat = np.random.uniform(LAT_MIN, LAT_MAX)
    w = np.random.uniform(0.0025, 0.0060)
    h = np.random.uniform(0.0020, 0.0050)
    poly = rectangle_polygon(lon, lat, w, h)
    field_id = f"F{i+1:03d}"
    lat_m = 111_000.0
    lon_m = 111_000.0 * math.cos(math.radians(lat))
    area_m2 = (w * lon_m) * (h * lat_m)
    fields.append({
        "type": "Feature",
        "properties": {
            "field_id": field_id,
            "name": f"Field {i+1}",
            "area_m2": round(area_m2, 2),
            "soil_type": random.choice(["Clay", "Sandy", "Loam", "Silt", "Peat"])
        },
        "geometry": {"type": "Polygon", "coordinates": poly[0]}
    })
fields_fc = {"type": "FeatureCollection", "features": fields}
with open(os.path.join(OUT_DIR, "fields.geojson"), "w") as f:
    json.dump(fields_fc, f)

fields_preview = pd.DataFrame([{
    "field_id": f["properties"]["field_id"],
    "name": f["properties"]["name"],
    "area_m2": f["properties"]["area_m2"],
    "soil_type": f["properties"]["soil_type"],
} for f in fields])

# 2) soil lab samples
num_samples = 200
samples_rows = []
for i in range(num_samples):
    field = random.choice(fields)
    fid = field["properties"]["field_id"]
    sample_date = datetime.today().date() - timedelta(days=int(np.random.uniform(10, 180)))
    ph = float(np.clip(np.random.normal(6.0, 0.6), 4.5, 8.0))
    om = float(np.clip(np.random.normal(3.0, 0.8), 1.0, 8.0))
    nitrate = float(np.clip(np.random.normal(15, 8), 0, 60))
    p = float(np.clip(np.random.normal(12, 6), 0, 60))
    k = float(np.clip(np.random.normal(150, 50), 20, 400))
    coords = field["geometry"]["coordinates"][0]
    lons = [c[0] for c in coords]; lats = [c[1] for c in coords]
    lon = float(np.random.uniform(min(lons), max(lons)))
    lat = float(np.random.uniform(min(lats), max(lats)))
    samples_rows.append({
        "sample_id": f"S{i+1:04d}",
        "field_id": fid,
        "sample_date": sample_date.isoformat(),
        "depth_cm": "0-15",
        "ph": round(ph, 2),
        "organic_matter_pct": round(om, 2),
        "nitrate_mgkg": round(nitrate, 1),
        "phosphorus_mgkg": round(p, 1),
        "potassium_mgkg": round(k, 1),
        "lon": round(lon, 6),
        "lat": round(lat, 6)
    })
soil_samples = pd.DataFrame(samples_rows)
soil_samples.to_csv(os.path.join(OUT_DIR, "soil_samples.csv"), index=False)

# 3) crops per field
crops = ["Grassland", "Winter Wheat", "Spring Barley", "Silage Maize", "Oilseed Rape"]
crops_df = pd.DataFrame({
    "field_id": fields_preview["field_id"],
    "crop": [random.choice(crops) for _ in range(len(fields_preview))]
})
crops_df.to_csv(os.path.join(OUT_DIR, "crops.csv"), index=False)

# 4) 30-day time series for rainfall/NDVI + fertiliser events (sparse)
days = 30
end_date = datetime.today().date()
start_date = end_date - timedelta(days=days-1)
date_list = [start_date + timedelta(days=i) for i in range(days)]

rain_rows, ndvi_rows, fert_rows = [], [], []
for fid in fields_preview["field_id"]:
    wetness = np.random.uniform(0.3, 1.2)
    crop = crops_df.loc[crops_df.field_id == fid, "crop"].values[0]
    base_ndvi = {"Grassland":0.65,"Winter Wheat":0.55,"Spring Barley":0.5,"Silage Maize":0.45,"Oilseed Rape":0.5}.get(crop,0.5)
    for d in date_list:
        rain = max(0.0, np.random.gamma(shape=1.2, scale=3.0) * wetness)
        season_noise = np.random.normal(0, 0.02)
        ndvi = float(np.clip(base_ndvi + season_noise, 0.1, 0.9))
        rain_rows.append({"field_id": fid, "date": d.isoformat(), "rain_mm": round(rain, 1)})
        ndvi_rows.append({"field_id": fid, "date": d.isoformat(), "ndvi": round(ndvi, 3)})

    n_events = np.random.choice([0,1,1,2,2,3], p=[0.1,0.25,0.25,0.2,0.15,0.05])
    if n_events > 0:
        chosen = sorted(np.random.choice(date_list, size=n_events, replace=False))
        for idx, d in enumerate(chosen, start=1):
            kg_per_ha = float(np.clip(np.random.normal(80, 35), 20, 220))
            fert_rows.append({
                "spread_id": f"{fid}-{d.isoformat()}-{idx}",
                "field_id": fid,
                "date": d.isoformat(),
                "product": np.random.choice(["Ammonium_Nitrate","Urea","NPK_20_10_10","UAN"]),
                "kg_per_ha": round(kg_per_ha, 1)
            })

rain_df = pd.DataFrame(rain_rows)
ndvi_df = pd.DataFrame(ndvi_rows)
fert_df = pd.DataFrame(fert_rows)
rain_df.to_csv(os.path.join(OUT_DIR, "rainfall_daily.csv"), index=False)
ndvi_df.to_csv(os.path.join(OUT_DIR, "ndvi_daily.csv"), index=False)
fert_df.to_csv(os.path.join(OUT_DIR, "fertiliser_logs.csv"), index=False)

# 5) panels (daily features) + synthetic label
ndvi_df_sorted = ndvi_df.sort_values(["field_id","date"]).copy()
ndvi_df_sorted["ndvi_mean_30d"] = ndvi_df_sorted.groupby("field_id")["ndvi"].expanding().mean().reset_index(level=0, drop=True)

rain_df_sorted = rain_df.sort_values(["field_id","date"]).copy()
rain_df_sorted["rain_mm"] = rain_df_sorted["rain_mm"].astype(float)
rain_df_sorted["recent_heavy_rain_48h"] = rain_df_sorted.groupby("field_id")["rain_mm"].rolling(window=2, min_periods=1).sum().reset_index(level=0, drop=True)

grid = pd.MultiIndex.from_product([fields_preview["field_id"], [d.isoformat() for d in date_list]], names=["field_id","date"])
grid_df = pd.DataFrame(index=grid).reset_index()
fert_daily = pd.merge(grid_df, fert_df[["field_id","date","kg_per_ha"]], how="left", on=["field_id","date"]).fillna({"kg_per_ha":0.0})
fert_daily["kg_N_applied_last_30d"] = fert_daily.groupby("field_id")["kg_per_ha"].cumsum()

panel = pd.merge(ndvi_df_sorted[["field_id","date","ndvi","ndvi_mean_30d"]],
                 rain_df_sorted[["field_id","date","recent_heavy_rain_48h"]],
                 on=["field_id","date"], how="left")
panel = pd.merge(panel, fert_daily[["field_id","date","kg_N_applied_last_30d"]], on=["field_id","date"], how="left")

latest_lab = soil_samples.sort_values("sample_date").groupby("field_id").tail(1)[["field_id","ph","organic_matter_pct","nitrate_mgkg","phosphorus_mgkg","potassium_mgkg"]]
panel = pd.merge(panel, latest_lab, on="field_id", how="left")

field_stat = fields_preview.copy()
field_stat["slope_mean"] = np.round(np.random.uniform(0.5, 5.0, size=len(field_stat)), 2)
field_stat["flow_accumulation"] = np.round(np.random.uniform(0.0, 0.2, size=len(field_stat)), 3)
panel = pd.merge(panel, field_stat[["field_id","slope_mean","flow_accumulation"]], on="field_id", how="left")

def risk_score(row):
    base = 0.2
    base += min(row.get("recent_heavy_rain_48h",0)/50.0, 0.4)
    base += min(row.get("kg_N_applied_last_30d",0)/400.0, 0.4)
    base -= min(row.get("ndvi_mean_30d",0), 0.3)
    return max(0.0, min(1.0, base))

panel["risk_score"] = panel.apply(risk_score, axis=1)
panel["risk_label"] = (panel["risk_score"] >= 0.6).astype(int)

panel.to_csv(os.path.join(OUT_DIR, "panels.csv"), index=False)

print("✅ Synthetic dataset saved in ./data/")
for fn in ["fields.geojson","soil_samples.csv","crops.csv","rainfall_daily.csv","ndvi_daily.csv","fertiliser_logs.csv","panels.csv"]:
    print("  -", fn)
