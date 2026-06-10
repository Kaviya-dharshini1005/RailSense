import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import sys
sys.path.append('.')

def predict_remaining_useful_life(km_marker, current_score, daily_change):
    """
    Predict how many days until track section becomes CRITICAL (score < 50).
    
    Formula: Days = (Current_Score - Critical_Threshold) / |Daily_Deterioration|
    """
    CRITICAL_THRESHOLD = 50
    
    if daily_change >= 0:
        # Track is stable or improving
        return {
            "days_to_critical": float('inf'),
            "prediction": "STABLE — No critical failure expected",
            "confidence": "HIGH"
        }
    else:
        # Track is deteriorating
        days_remaining = (current_score - CRITICAL_THRESHOLD) / abs(daily_change)
        
        if days_remaining <= 0:
            days_remaining = 0
            prediction = "ALREADY CRITICAL"
            confidence = "CRITICAL"
        elif days_remaining <= 1:
            prediction = "FAILURE IMMINENT (< 24 hours)"
            confidence = "CRITICAL"
        elif days_remaining <= 3:
            prediction = f"Failure in ~{int(days_remaining)} days — URGENT ACTION"
            confidence = "HIGH"
        elif days_remaining <= 7:
            prediction = f"Failure in ~{int(days_remaining)} days — Schedule soon"
            confidence = "MEDIUM"
        else:
            prediction = f"Failure in ~{int(days_remaining)} days — Monitor"
            confidence = "MEDIUM"
        
        return {
            "days_to_critical": round(days_remaining, 1),
            "prediction": prediction,
            "confidence": confidence
        }

def calculate_deterioration_rate(km_marker, history_df):
    """Calculate daily deterioration rate from historical data"""
    segment_history = history_df[
        history_df['km_marker'] == km_marker
    ].sort_values('date')
    
    if len(segment_history) < 2:
        return 0, "Insufficient data"
    
    scores = segment_history['health_score'].values
    daily_change = (scores[-1] - scores[0]) / (len(scores) - 1)
    
    if daily_change < -5:
        trend = "Rapidly Deteriorating"
    elif daily_change < -2:
        trend = "Deteriorating"
    elif daily_change < 0:
        trend = "Slowly Declining"
    else:
        trend = "Stable/Improving"
    
    return daily_change, trend

def run_rul_agent():
    """
    Remaining Useful Life (RUL) Agent
    Predicts how many days until track section becomes critical.
    """
    # Load data
    validation_df = pd.read_csv("data/validation_results.csv")
    history_df = pd.read_csv("data/track_history.csv")
    
    print("📊 RailSense Remaining Useful Life (RUL) Agent\n")
    print("Predicting time to critical failure for verified issues...\n")
    
    rul_results = []
    for _, issue in validation_df.iterrows():
        km_marker = issue['km_marker']
        current_score = issue['avg_risk_score']
        
        # Get deterioration rate
        daily_change, trend = calculate_deterioration_rate(km_marker, history_df)
        
        # Predict RUL
        rul = predict_remaining_useful_life(km_marker, current_score, daily_change)
        
        rul_results.append({
            "km_marker": km_marker,
            "km": issue['km'],
            "current_health_score": issue['avg_risk_score'],
            "daily_deterioration_rate": round(daily_change, 2),
            "deterioration_trend": trend,
            "days_until_critical": rul['days_to_critical'],
            "rul_prediction": rul['prediction'],
            "confidence": rul['confidence'],
            "defect_type": issue['defect_type'],
            "trains_reporting": issue['trains_reported'],
            "projected_critical_date": (
                (datetime.now() + timedelta(days=int(rul['days_to_critical']))).strftime("%Y-%m-%d")
                if rul['days_to_critical'] != float('inf') else "N/A"
            )
        })
    
    rul_df = pd.DataFrame(rul_results)
    
    # Filter by urgency
    imminent = rul_df[rul_df['days_until_critical'] <= 1]
    urgent = rul_df[
        (rul_df['days_until_critical'] > 1) & 
        (rul_df['days_until_critical'] <= 3)
    ]
    soon = rul_df[
        (rul_df['days_until_critical'] > 3) & 
        (rul_df['days_until_critical'] <= 7)
    ]
    stable = rul_df[rul_df['days_until_critical'] > 7]
    
    print(f"Total segments analyzed: {len(rul_df)}")
    print(f"\nRUL Breakdown:")
    print(f"🔴 IMMINENT (< 24 hrs)    : {len(imminent)}")
    print(f"🟠 URGENT (1-3 days)      : {len(urgent)}")
    print(f"🟡 SOON (3-7 days)        : {len(soon)}")
    print(f"🟢 STABLE (> 7 days)      : {len(stable)}\n")
    
    print(f"--- CRITICAL RUL PREDICTIONS ---")
    critical_rul = rul_df[rul_df['confidence'] == 'CRITICAL'].sort_values(
        'days_until_critical'
    ).head(5)
    
    for _, row in critical_rul.iterrows():
        print(f"\n⚠️  {row['km_marker']}")
        print(f"   Current Score        : {row['current_health_score']}/100")
        print(f"   Daily Change         : {row['daily_deterioration_rate']} pts/day")
        print(f"   Trend                : {row['deterioration_trend']}")
        print(f"   Days to Critical     : {row['days_until_critical']}")
        print(f"   Projected Date       : {row['projected_critical_date']}")
        print(f"   Prediction           : {row['rul_prediction']}")
        print(f"   Trains Confirmed     : {row['trains_reporting']}")
    
    print(f"\n--- URGENT RUL PREDICTIONS (Next 3 Days) ---")
    urgent_rul = rul_df[
        (rul_df['days_until_critical'] > 1) &
        (rul_df['days_until_critical'] <= 3)
    ].sort_values('days_until_critical').head(3)
    
    for _, row in urgent_rul.iterrows():
        print(f"\n📈 {row['km_marker']}")
        print(f"   Estimated Failure    : ~{int(row['days_until_critical'])} days")
        print(f"   Projected Date       : {row['projected_critical_date']}")
        print(f"   Current Score        : {row['current_health_score']}/100")
    
    os.makedirs("data", exist_ok=True)
    rul_df.to_csv("data/rul_predictions.csv", index=False)
    print(f"\n✅ RUL predictions saved to data/rul_predictions.csv")
    
    return rul_df

if __name__ == "__main__":
    run_rul_agent()