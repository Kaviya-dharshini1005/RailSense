import pandas as pd
import pickle
from datetime import datetime

def classify_severity(anomaly_score):
    """Autonomously classify severity based on anomaly score"""
    if anomaly_score < -0.15:
        return "CRITICAL"
    elif anomaly_score < -0.05:
        return "MODERATE"
    else:
        return "LOW"

def decide_action(severity):
    """Autonomous decision making - no human needed"""
    actions = {
        "CRITICAL": "🔴 IMMEDIATE ACTION: Slow down trains, dispatch maintenance crew now",
        "MODERATE": "🟡 SCHEDULE MAINTENANCE: Flag for inspection within 24 hours",
        "LOW": "🟢 LOG & MONITOR: Continue monitoring, review in next routine check"
    }
    return actions[severity]

def run_agent():
    # Load predictions
    df = pd.read_csv("data/track_data_predictions.csv")
    
    # Filter only anomalies
    anomalies = df[df['prediction'] == -1].copy()
    
    # Classify severity autonomously
    anomalies['severity'] = anomalies['anomaly_score'].apply(classify_severity)
    anomalies['action'] = anomalies['severity'].apply(decide_action)
    anomalies['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("🚆 RailSense Alert Agent Running...\n")
    print(f"Total anomalies found: {len(anomalies)}")
    print(f"\nSeverity Breakdown:")
    print(anomalies['severity'].value_counts().to_string())
    
    print(f"\n--- TOP CRITICAL ALERTS ---")
    critical = anomalies[anomalies['severity'] == 'CRITICAL']
    for _, row in critical.head(5).iterrows():
        print(f"\n⚠️  Time point: {row['time']:.2f}s")
        print(f"   Vibration: {row['vibration']:.4f}")
        print(f"   Severity: {row['severity']}")
        print(f"   Action: {row['action']}")
    
    # Save alert log
    anomalies.to_csv("data/alert_log.csv", index=False)
    print(f"\n✅ Alert log saved to data/alert_log.csv")
    
    return anomalies

if __name__ == "__main__":
    run_agent()