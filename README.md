# 🌱 AI-Driven Decision Support for Soil Health & Nutrient Management

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-brightgreen)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-ff4b4b)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)](https://scikit-learn.org/)
[![Last Commit](https://img.shields.io/github/last-commit/ncvictorious/Agric-SoilHealth-AI)](https://github.com/ncvictorious/Agric-SoilHealth-AI/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/ncvictorious/Agric-SoilHealth-AI)](https://github.com/ncvictorious/Agric-SoilHealth-AI)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational)](#-license)

> Feasibility prototype for DEFRA: synthetic dataset → ML model → API → dashboard with explainable Alert Cards.

---

## 🔎 Quick look

**KPI Badges (synthetic data):**  
![AUC](https://img.shields.io/badge/AUC-0.998-brightgreen)
![Accuracy](https://img.shields.io/badge/Accuracy-0.995-brightgreen)
![F1](https://img.shields.io/badge/F1-0.667-yellow)

**Architecture (Mermaid):**
```mermaid
graph LR
  A[Data<br/>CSV/GeoJSON] --> B[Feature Engineering]
  B --> C[Model<br/>HGB Classifier]
  C --> D[FastAPI /score]
  D --> E[Streamlit Dashboard]
  C --> F[(Outputs<br/>metrics.json,<br/>feature_importance.png)]
🌱 Project summary
This repository contains the feasibility prototype developed for the DEFRA Agriculture & Soil Health Project (Edora AI-Robotics Solutions Ltd, 2025).
It demonstrates an AI-driven pipeline that predicts soil nutrient risks, visualises compliance alerts, and provides interpretable insights for farmers and regulators.

🎯 Objectives
Generate a realistic synthetic dataset simulating UK agricultural soil and weather conditions.

Train and validate a baseline ML model to predict nitrate/runoff risks.

Build a FastAPI service exposing prediction endpoints.

Develop a Streamlit dashboard for visualising alerts and soil compliance insights.

🧩 System architecture
DATA → MODEL → API → DASHBOARD

Layer	Description
Data Layer	Synthetic datasets (soil labs, rainfall, NDVI, fertiliser logs).
Model Layer	Histogram-Based Gradient Boosting Classifier (scikit-learn) on engineered features.
API Layer	FastAPI REST endpoint /score serving Alert Cards with risk explanations.
Dashboard Layer	Streamlit UI showing per-field risk indicators (Green / Amber / Red) + drivers.

🧠 Model performance (synthetic dataset)
Metric	Result
AUC	0.998
Accuracy	0.995
Precision / Recall / F1	0.667 / 0.667 / 0.667

These indicate strong predictive potential and a stable synthetic training environment.

⚙️ Project structure
bash
Copy code
Agric-SoilHealth-AI/
│
├── data/                # Synthetic dataset package
├── outputs/             # Trained model, metrics, and plots
├── screenshots/         # Dashboard + API images
│   ├── alert_dashboard.png
│   ├── fast_api1.png
│   ├── fast_api2.png
│   └── fast_api3.png
│
├── generate_data.py     # Step 1: Data generation
├── train_model.py       # Step 2: Model training
├── serve_api.py         # Step 3: FastAPI service
├── dashboard.py         # Step 4: Streamlit dashboard
├── requirements.txt     # Environment dependencies
│
├── docs/
│   ├── Feasibility Note.pdf
│   └── Technical Overview – System Architecture.pdf
└── README.md
🚀 Run it locally
1) Clone & set up
bash
Copy code
git clone https://github.com/ncvictorious/Agric-SoilHealth-AI.git
cd Agric-SoilHealth-AI
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt
2) Generate data & train model
bash
Copy code
python generate_data.py
python train_model.py
3) Start the API
bash
Copy code
uvicorn serve_api:app --reload --port 8000
# Open http://localhost:8000/docs
4) Launch the dashboard (new terminal)
bash
Copy code
streamlit run dashboard.py
# Open http://localhost:8501
🖼 Screenshots
FastAPI – POST /score

Alert Dashboard

📘 Documentation
[📄 Feasibility Note (PDF)](docs/Feasibility%20Note.pdf)

[📘 Technical Overview (PDF)](docs/Technical%20Overview.pdf)

🔬 Tech stack
Python 3.11 · scikit-learn 1.5 · FastAPI 0.115 · Streamlit 1.38 · Pandas 2.2 · Uvicorn 0.30

📄 License
./LICENSE.

🤝 Acknowledgements
Prototype developed for the DEFRA Farming Innovation Programme (Feasibility Round 4) by Edora AI-Robotics Solutions Ltd.
