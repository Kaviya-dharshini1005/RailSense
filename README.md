# RailSense 🚆
### Autonomous AI Track Health Monitoring System for Indian Railways

---

## The Problem

Indian Railways operates 68,000 km of track and runs 13,000+ trains daily — 
yet track inspection is still done manually by trackmen who walk 10-15 km 
every day on foot, alone, in all weather conditions.

- 55.8% of train accidents involve railway staff failures
- Trackmen work in dangerous conditions with shrinking workforce
- Younger generation unwilling to take up the job
- Japan's automated solution (Doctor Yellow) costs ₹500+ crore — 
  built for Shinkansen, not scalable to Indian Railways

**The result: a national infrastructure crisis in slow motion.**

---

## Our Solution

RailSense is an autonomous multi-agent AI system that continuously monitors 
track health from vibration data — detecting degradation before it becomes 
dangerous, dispatching maintenance crews automatically, with zero humans 
required in the decision loop.

**Core insight:** Mount a low-cost sensor on any existing train. Every train 
that runs its normal route becomes a track inspection unit. 13,000 trains × 
daily routes = entire 68,000 km network monitored automatically.

What Japan does with a ₹500 crore dedicated train, RailSense does with 
hardware that costs a fraction of that — on trains already running.

---

## Agent Architecture

| Agent | Role | Status |
|-------|------|--------|
| Agent 1 — Sensor Agent | Collects vibration data from moving train | ✅ Live |
| Agent 2 — Vision Agent | Detects visible track defects via camera | 🔨 In Development |
| Agent 3 — Fusion Agent | Combines sensor + vision outputs | 🔨 In Development |
| Agent 4 — Health Assessment Agent | Computes Track Health Score per GPS zone | ✅ Live |
| Agent 5 — Risk Assessment Agent | Multi-factor risk scoring with confidence % | ✅ Live |
| Agent 6 — Maintenance Planning Agent | Recommends action + nearest crew | 🔨 In Development |
| Agent 7 — Dispatch Agent | Generates autonomous work orders | 🔨 In Development |
| Agent 8 — Learning Agent | Improves thresholds from historical data | 🔮 Planned |

## How It Works
Vibration Data (Sensor Agent)
↓
Track Health Score 0-100 (Health Agent)
↓
Multi-Factor Risk Score (Risk Agent)
→ Anomaly Strength   (35%)
→ Traffic Density    (25%)
→ Train Speed        (20%)
→ Historical Trend   (20%)
↓
Severity Classification + Confidence %
↓
Nearest Crew Dispatch + Work Order (Dispatch Agent)
---

## Track Health Index

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | 🟢 Healthy | No action needed |
| 70-89 | 🟡 Monitor | Log and observe |
| 50-69 | 🟠 Maintenance Needed | Schedule inspection |
| < 50 | 🔴 Critical | Immediate action |

---

## Risk Engine Output Example
📍 KM_990 — Chennai-Mumbai Central Line
Health Score  : 40.8/100
Risk Score    : 98.0/100
Confidence    : 83.7%
Traffic       : High Traffic (8 trains/hour)
Train Speed   : 120 km/h
Trend         : Rapidly Deteriorating (-5.8 pts/day)
Action        : 🔴 REPAIR WITHIN 24 HOURS

---

## Deployment Vision

**Round 1 (Current):** Software simulation on laptop — 
proves the full agent pipeline works end to end.

**Round 2 (Hardware):** Raspberry Pi + accelerometer sensor 
mounted on maintenance trolley — real vibration data, 
same software stack.

**Production:** Smartphone mounted on any existing train — 
uses built-in accelerometer, streams data to cloud model in 
real time. No new infrastructure. No dedicated vehicle. 
Deployable on all 13,000 trains immediately.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9 |
| ML Model | Scikit-learn — Isolation Forest |
| Dashboard | Streamlit |
| Mapping | Plotly Mapbox |
| Data | NumPy, Pandas |
| Visualization | Plotly, Matplotlib |

---

## Project Structure
RailSense/
├── data/
│   ├── simulate_data.py       # Agent 1 — Sensor simulation
│   ├── gps_route.py           # GPS coordinates, Chennai-Mumbai route
│   ├── history_manager.py     # 7-day historical health tracking
│   └── weather_fetcher.py     # Live weather risk adjustment (coming)
├── model/
│   └── train_model.py         # Isolation Forest training
├── agents/
│   ├── alert_engine.py        # Initial alert classification
│   ├── risk_agent.py          # Multi-factor risk engine
│   ├── maintenance_agent.py   # Crew dispatch planning (coming)
│   └── dispatch_agent.py      # Autonomous work orders (coming)
├── dashboard/
│   └── app.py                 # Streamlit dashboard (coming)
└── README.md

---

## How To Run

```bash
# Install dependencies
pip install numpy pandas scikit-learn matplotlib plotly streamlit

# Step 1 — Generate track data
python data/simulate_data.py

# Step 2 — Generate GPS route
python data/gps_route.py

# Step 3 — Generate historical data
python data/history_manager.py

# Step 4 — Train health model
python model/train_model.py

# Step 5 — Run risk assessment
python agents/risk_agent.py
```

---

## India-Specific Innovation

- Designed for Indian broad gauge (1676mm) track geometry
- Route simulation on real Chennai-Mumbai Central Railway corridor
- Traffic density weighted for Indian Railways schedule patterns
- Low-cost deployment model viable at Indian Railways budget scale
- Maintenance windows aligned with Indian Railways night corridor schedule

---

## Theme

Railways + Agentic & Autonomous Systems — FARAWAY Hackathon 2026

## Team

Active Development — June 2026

## Status

🔨 Round 1 Prototype — Core agent pipeline operational

---

## How It Works
