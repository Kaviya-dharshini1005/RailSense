import pandas as pd
import numpy as np
import os
from datetime import datetime

def fuse_sensor_and_vision():
    """
    Agent 3 — Fusion Agent
    Combines vibration sensor data with visual camera detections.
    When both agree, confidence jumps significantly.
    """
    # Load both data sources
    risk_df = pd.read_csv("data/risk_assessment.csv")
    vision_df = pd.read_csv("data/vision_detections.csv")
    
    # Merge on km_marker
    fused = risk_df.merge(
        vision_df[['km_marker', 'visual_defect', 'visual_severity', 'visual_confidence']],
        on='km_marker',
        how='left'
    )
    
    # Compute fused confidence
    # If both sensor AND vision agree on issue = higher confidence
    fused['sensor_agrees'] = fused['risk_score'] >= 60
    fused['vision_agrees'] = fused['visual_defect'] != 'no_defect'
    
    # Fused confidence logic
    fused_confidence = []
    for _, row in fused.iterrows():
        sensor_conf = float(row['confidence'].rstrip('%'))
        vision_conf = row['visual_confidence']
        
        if row['sensor_agrees'] and row['vision_agrees']:
            # Both detect issue = very high confidence
            fused_conf = min(99, (sensor_conf + vision_conf) / 2 + 15)
        elif row['sensor_agrees'] or row['vision_agrees']:
            # One detects issue = moderate boost
            fused_conf = (sensor_conf + vision_conf) / 2 + 5
        else:
            # Neither detects issue = low confidence
            fused_conf = (sensor_conf + vision_conf) / 2 - 5
        
        fused_confidence.append(round(fused_conf, 1))
    
    fused['fused_confidence'] = fused_confidence
    
    # Determine fusion verdict
    verdicts = []
    for _, row in fused.iterrows():
        sensor = "Issue Detected" if row['sensor_agrees'] else "Normal"
        vision = row['visual_defect'] if row['visual_defect'] != 'no_defect' else "Clear"
        
        if row['sensor_agrees'] and row['vision_agrees']:
            verdict = "🔴 VERIFIED ISSUE — Both Sensor & Vision Confirm"
        elif row['sensor_agrees']:
            verdict = "🟡 SENSOR ALERT — Awaiting Visual Confirmation"
        elif row['vision_agrees']:
            verdict = "🟡 VISUAL ALERT — Sensor Data Nominal"
        else:
            verdict = "🟢 CLEAR — Both Sources Nominal"
        
        verdicts.append(verdict)
    
    fused['fusion_verdict'] = verdicts
    
    print("🔗 RailSense Fusion Agent — Combining Sensor + Vision Data\n")
    
    # Summary
    verified = len(fused[fused['fusion_verdict'].str.contains("VERIFIED")])
    sensor_only = len(fused[fused['fusion_verdict'].str.contains("SENSOR ALERT")])
    vision_only = len(fused[fused['fusion_verdict'].str.contains("VISUAL ALERT")])
    clear = len(fused[fused['fusion_verdict'].str.contains("CLEAR")])
    
    print(f"Total segments analyzed: {len(fused)}")
    print(f"\nFusion Results:")
    print(f"🔴 Verified Issues (Sensor + Vision) : {verified}")
    print(f"🟡 Sensor Alert Only                 : {sensor_only}")
    print(f"🟡 Visual Alert Only                 : {vision_only}")
    print(f"🟢 Clear (Both Sources)              : {clear}")
    
    print(f"\n--- TOP VERIFIED ISSUES ---")
    verified_df = fused[fused['fusion_verdict'].str.contains("VERIFIED")].sort_values(
        'fused_confidence', ascending=False
    ).head(5)
    
    for _, row in verified_df.iterrows():
        print(f"\n✓ {row['km_marker']}")
        print(f"  Sensor Risk Score    : {row['risk_score']}/100")
        print(f"  Visual Defect        : {row['visual_defect']}")
        print(f"  Visual Severity      : {row['visual_severity']}")
        print(f"  FUSED CONFIDENCE     : {row['fused_confidence']}%")
        print(f"  Verdict              : {row['fusion_verdict']}")
    
    os.makedirs("data", exist_ok=True)
    fused.to_csv("data/fused_assessment.csv", index=False)
    print(f"\n✅ Fused assessment saved to data/fused_assessment.csv")
    
    return fused

if __name__ == "__main__":
    fuse_sensor_and_vision()