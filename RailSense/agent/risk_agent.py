import pandas as pd
import numpy as np
import sys
sys.path.append('.')
from data.history_manager import get_trend

# Traffic density per route zone (trains per hour, simulated)
TRAFFIC_DENSITY = {
    "high":   {"label": "High Traffic",   "trains_per_hour": 8,  "weight": 1.0},
    "medium": {"label": "Medium Traffic", "trains_per_hour": 4,  "weight": 0.65},
    "low":    {"label": "Low Traffic",    "trains_per_hour": 1,  "weight": 0.30},
}

# Average train speeds per zone type
SPEED_PROFILE = {
    "high":   120,  # km/h
    "medium": 80,
    "low":    50,
}

def get_traffic_zone(km):
    """Assign traffic density based on proximity to major stations"""
    major_station_kms = [0, 210, 420, 720, 950, 1270]
    for s in major_station_kms:
        if abs(km - s) < 80:
            return "high"
    if km % 200 < 100:
        return "medium"
    return "low"

def compute_confidence(health_score, anomaly_strength):
    """Convert model output to confidence percentage"""
    base = min(abs(anomaly_strength) * 300, 60)
    health_factor = max(0, (100 - health_score) / 100) * 40
    confidence = base + health_factor
    return min(round(confidence, 1), 99.0)

def compute_risk_score(km_marker, km, health_score, anomaly_strength):
    """
    Multi-factor risk engine:
    Risk = Anomaly Strength (35%) 
         + Traffic Density (25%) 
         + Train Speed (20%) 
         + Historical Trend (20%)
    """
    # Factor 1 — Anomaly Strength (0-100)
    anomaly_factor = min(abs(anomaly_strength) * 400, 100)

    # Factor 2 — Traffic Density
    zone = get_traffic_zone(km)
    traffic_factor = TRAFFIC_DENSITY[zone]["weight"] * 100

    # Factor 3 — Train Speed risk
    speed = SPEED_PROFILE[zone]
    speed_factor = (speed / 120) * 100

    # Factor 4 — Historical Trend
    daily_change, trend = get_trend(km_marker)
    if trend == "Rapidly Deteriorating":
        trend_factor = 90
    elif trend == "Deteriorating":
        trend_factor = 65
    elif trend == "Slowly Declining":
        trend_factor = 40
    else:
        trend_factor = 10

    # Weighted risk score
    risk_score = (
        anomaly_factor * 0.35 +
        traffic_factor * 0.25 +
        speed_factor   * 0.20 +
        trend_factor   * 0.20
    )
    risk_score = round(min(risk_score, 100), 1)

    # Confidence
    confidence = compute_confidence(health_score, anomaly_strength)

    # Action
    if risk_score >= 80:
        action = "🔴 REPAIR WITHIN 24 HOURS"
    elif risk_score >= 60:
        action = "🟠 SCHEDULE REPAIR WITHIN 72 HOURS"
    elif risk_score >= 40:
        action = "🟡 MONITOR CLOSELY — INSPECT NEXT WEEK"
    else:
        action = "🟢 NO ACTION NEEDED"

    return {
        "km_marker": km_marker,
        "km": km,
        "health_score": health_score,
        "risk_score": risk_score,
        "confidence": f"{confidence}%",
        "traffic_zone": TRAFFIC_DENSITY[zone]["label"],
        "train_speed": f"{speed} km/h",
        "trend": trend,
        "recommended_action": action
    }

def run_risk_assessment():
    """Run full risk assessment on all degraded segments"""
    df = pd.read_csv("data/track_data_predictions.csv")
    route_df = pd.read_csv("data/route.csv")
    history_df = pd.read_csv("data/track_history.csv")

    # Get latest health scores from history
    latest = history_df.sort_values('date').groupby('km_marker').last().reset_index()

    # Only assess degraded segments from history
    deviations = latest[latest['health_score'] < 85].copy()

    print("🚆 RailSense Risk Assessment Agent\n")
    results = []
    for _, row in deviations.iterrows():
        # Simulate anomaly strength based on health score
        anomaly_strength = (100 - row['health_score']) / 100

        result = compute_risk_score(
            row['km_marker'],
            row['km'],
            row['health_score'],
            anomaly_strength
        )
        results.append(result)

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('risk_score', ascending=False)

    print(f"Total deviation zones assessed: {len(results_df)}")
    print(f"\nRisk Breakdown:")
    print(f"🔴 Repair within 24hrs : {len(results_df[results_df['risk_score'] >= 80])}")
    print(f"🟠 Repair within 72hrs : {len(results_df[(results_df['risk_score'] >= 60) & (results_df['risk_score'] < 80)])}")
    print(f"🟡 Inspect next week   : {len(results_df[(results_df['risk_score'] >= 40) & (results_df['risk_score'] < 60)])}")
    print(f"🟢 No action needed    : {len(results_df[results_df['risk_score'] < 40])}")

    print(f"\n--- TOP 5 HIGH RISK ZONES ---")
    for _, row in results_df.head(5).iterrows():
        print(f"\n📍 {row['km_marker']}")
        print(f"   Health Score  : {round(row['health_score'], 1)}/100")
        print(f"   Risk Score    : {row['risk_score']}/100")
        print(f"   Confidence    : {row['confidence']}")
        print(f"   Traffic       : {row['traffic_zone']}")
        print(f"   Speed         : {row['train_speed']}")
        print(f"   Trend         : {row['trend']}")
        print(f"   Action        : {row['recommended_action']}")

    results_df.to_csv("data/risk_assessment.csv", index=False)
    print(f"\n✅ Risk assessment saved to data/risk_assessment.csv")
    return results_df

if __name__ == "__main__":
    run_risk_assessment()