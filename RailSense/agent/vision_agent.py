import numpy as np
import pandas as pd
import os
from datetime import datetime

# Simulated defect types a camera would detect visually
VISUAL_DEFECTS = [
    'surface_crack',
    'rail_corrosion', 
    'missing_bolt',
    'weld_defect',
    'ballast_void',
    'no_defect'
]

# Severity weights per visual defect
DEFECT_SEVERITY = {
    'surface_crack':  0.85,
    'rail_corrosion': 0.60,
    'missing_bolt':   0.75,
    'weld_defect':    0.90,
    'ballast_void':   0.50,
    'no_defect':      0.0
}

def simulate_camera_frame(km_marker, health_score):
    """
    Simulate what a camera mounted on a train would detect.
    In real deployment this would be a CV model on actual images.
    Health score influences probability of defect detection.
    """
    # Lower health score = higher chance of visual defect
    defect_probability = max(0, (100 - health_score) / 100)
    
    if np.random.random() < defect_probability:
        # Pick a defect weighted by severity
        # 5 defect types (excluding 'no_defect')
        defect_types = ['surface_crack', 'rail_corrosion', 'missing_bolt', 'weld_defect', 'ballast_void']
        defect_weights = [0.25, 0.20, 0.25, 0.20, 0.10]
        defect = np.random.choice(defect_types, p=defect_weights)
    else:
        defect = 'no_defect'
    
    severity = DEFECT_SEVERITY[defect]
    
    # Simulate confidence of visual detection
    if defect == 'no_defect':
        confidence = round(np.random.uniform(90, 99), 1)
    else:
        confidence = round(np.random.uniform(70, 95), 1)
    
    return {
        "km_marker": km_marker,
        "visual_defect": defect,
        "visual_severity": severity,
        "visual_confidence": confidence,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_vision_agent():
    """
    Run vision agent across all route segments.
    Simulates a camera scanning track as train passes over it.
    """
    history_df = pd.read_csv("data/track_history.csv")
    latest = history_df.sort_values('date').groupby(
        'km_marker'
    ).last().reset_index()
    
    print("👁️  RailSense Vision Agent Running...\n")
    print("Simulating camera-based track inspection across route...\n")
    
    results = []
    for _, row in latest.iterrows():
        frame = simulate_camera_frame(
            row['km_marker'],
            row['health_score']
        )
        frame['km'] = row['km']
        frame['lat'] = row['lat']
        frame['lon'] = row['lon']
        frame['health_score'] = row['health_score']
        results.append(frame)
    
    df = pd.DataFrame(results)
    
    # Summary
    defect_counts = df[df['visual_defect'] != 'no_defect']
    
    print(f"Total segments scanned: {len(df)}")
    print(f"Visual defects detected: {len(defect_counts)}")
    print(f"\nDefect Breakdown:")
    print(df['visual_defect'].value_counts().to_string())
    
    print(f"\n--- TOP VISUAL DEFECTS FOUND ---")
    top = df[df['visual_defect'] != 'no_defect'].sort_values(
        'visual_severity', ascending=False
    ).head(5)
    
    for _, row in top.iterrows():
        print(f"\n📷 {row['km_marker']}")
        print(f"   Defect Type  : {row['visual_defect']}")
        print(f"   Severity     : {row['visual_severity']}")
        print(f"   Confidence   : {row['visual_confidence']}%")
        print(f"   Health Score : {row['health_score']}/100")
    
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/vision_detections.csv", index=False)
    print(f"\n✅ Vision detections saved to data/vision_detections.csv")
    
    return df

if __name__ == "__main__":
    run_vision_agent()