import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def simulate_historical_data(days=7):
    """
    Simulate 7 days of track health history per GPS segment.
    Each day a train runs the route and records health scores.
    """
    route_df = pd.read_csv("data/route.csv")
    
    records = []
    
    # Simulate gradual degradation on some segments
    degrading_segments = np.random.choice(
        route_df['km_marker'].values, 
        size=15, 
        replace=False
    )
    
    for _, segment in route_df.iterrows():
        base_score = np.random.randint(70, 100)
        is_degrading = segment['km_marker'] in degrading_segments
        
        for day in range(days):
            date = (datetime.now() - timedelta(days=(days - day))).strftime("%Y-%m-%d")
            
            if is_degrading:
                # Gradual deterioration
                daily_drop = np.random.uniform(3, 9)
                score = max(20, base_score - (day * daily_drop))
            else:
                # Healthy with minor fluctuation
                score = min(100, base_score + np.random.uniform(-3, 3))
            
            records.append({
                "km_marker": segment['km_marker'],
                "km": segment['km'],
                "lat": segment['lat'],
                "lon": segment['lon'],
                "date": date,
                "health_score": round(score, 1),
                "nearest_station": segment['nearest_station']
            })
    
    df = pd.DataFrame(records)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/track_history.csv", index=False)
    
    print("✅ Historical track data generated!")
    print(f"Total records: {len(df)}")
    print(f"Days simulated: {days}")
    print(f"Segments tracked: {len(route_df)}")
    print(f"\nSample degrading segment:")
    sample = df[df['km_marker'] == degrading_segments[0]]
    print(sample[['date', 'km_marker', 'health_score']].to_string())
    
    return df

def get_latest_scores():
    """Get today's health score per segment"""
    df = pd.read_csv("data/track_history.csv")
    latest = df.sort_values('date').groupby('km_marker').last().reset_index()
    return latest

def get_trend(km_marker):
    """Get health trend for a specific segment"""
    df = pd.read_csv("data/track_history.csv")
    segment = df[df['km_marker'] == km_marker].sort_values('date')
    
    if len(segment) < 2:
        return 0, "Insufficient data"
    
    scores = segment['health_score'].values
    daily_change = (scores[-1] - scores[0]) / len(scores)
    
    if daily_change < -5:
        trend = "Rapidly Deteriorating"
    elif daily_change < -2:
        trend = "Deteriorating"
    elif daily_change < 0:
        trend = "Slowly Declining"
    else:
        trend = "Stable"
    
    return round(daily_change, 2), trend

if __name__ == "__main__":
    df = simulate_historical_data(days=7)
    
    # Show trend analysis
    print("\n--- TREND ANALYSIS SAMPLE ---")
    latest = get_latest_scores()
    critical = latest[latest['health_score'] < 60].head(3)
    
    for _, row in critical.iterrows():
        change, trend = get_trend(row['km_marker'])
        print(f"\n📍 {row['km_marker']} | Score: {row['health_score']}")
        print(f"   Trend: {trend} ({change} pts/day)")