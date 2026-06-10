import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import sys
sys.path.append('.')

def simulate_multi_train_passes(days=3):
    """
    Simulate 3 different trains running the same route on different days.
    Each train produces independent detections.
    """
    fused_df = pd.read_csv("data/fused_assessment.csv")
    
    # Simulate 3 train passes
    train_data = []
    for train_num in range(1, 4):
        for _, row in fused_df.iterrows():
            # Each train has slightly different detection confidence
            # but detects same issues (with random variation)
            noise = np.random.uniform(-0.05, 0.05)
            adjusted_confidence = np.clip(
                float(str(row['fused_confidence']).rstrip('%')) / 100 + noise,
                0, 1
            )
            
            # Probability of detecting issue based on adjusted confidence
            detects = np.random.random() < adjusted_confidence
            
            if detects:
                train_data.append({
                    "train_id": f"Train_{train_num}",
                    "km_marker": row['km_marker'],
                    "km": row['km'],
                    "detection_date": (
                        datetime.now() - timedelta(days=4-train_num)
                    ).strftime("%Y-%m-%d"),
                    "detection_confidence": round(adjusted_confidence * 100, 1),
                    "risk_score": row['risk_score'],
                    "defect_detected": row['visual_defect']
                })
    
    return pd.DataFrame(train_data)

def validate_detections(multi_train_df):
    """
    Group detections by km_marker and count how many trains reported it.
    If 2+ trains report same issue = VERIFIED
    """
    validation_results = []
    
    for km_marker, group in multi_train_df.groupby('km_marker'):
        trains_reporting = len(group)
        avg_confidence = group['detection_confidence'].mean()
        avg_risk = group['risk_score'].mean()
        
        # Validation logic
        if trains_reporting >= 2:
            validation_status = "VERIFIED BY MULTIPLE TRAINS"
            confidence_boost = min(99, avg_confidence + (trains_reporting * 10))
        else:
            validation_status = "SINGLE TRAIN DETECTION"
            confidence_boost = avg_confidence
        
        validation_results.append({
            "km_marker": km_marker,
            "km": group['km'].iloc[0],
            "trains_reported": trains_reporting,
            "train_list": ", ".join(group['train_id'].unique()),
            "avg_detection_confidence": round(avg_confidence, 1),
            "avg_risk_score": round(avg_risk, 1),
            "validation_status": validation_status,
            "final_confidence": round(confidence_boost, 1),
            "defect_type": group['defect_detected'].iloc[0],
            "first_detection": group['detection_date'].min(),
            "last_detection": group['detection_date'].max()
        })
    
    return pd.DataFrame(validation_results)

def run_validation_agent():
    """
    Multi-Train Validation Agent
    Increases confidence when multiple independent trains detect same issue.
    """
    print("🚂 RailSense Multi-Train Validation Agent\n")
    print("Simulating 3 independent train passes over the route...\n")
    
    # Simulate multi-train data
    multi_train_df = simulate_multi_train_passes(days=3)
    print(f"Total detections across 3 trains: {len(multi_train_df)}")
    print(f"Unique km_markers with detections: {multi_train_df['km_marker'].nunique()}\n")
    
    # Validate
    validation_df = validate_detections(multi_train_df)
    validation_df = validation_df.sort_values('final_confidence', ascending=False)
    
    # Summary
    verified = len(validation_df[validation_df['trains_reported'] >= 2])
    single = len(validation_df[validation_df['trains_reported'] == 1])
    
    print(f"Validation Results:")
    print(f"🟢 Verified by Multiple Trains (2+) : {verified}")
    print(f"🟡 Single Train Detection           : {single}")
    print(f"📈 Average Confidence Boost         : +{(validation_df['final_confidence'].mean() - validation_df['avg_detection_confidence'].mean()):.1f}%\n")
    
    print(f"--- TOP VALIDATED ISSUES ---")
    for _, row in validation_df.head(5).iterrows():
        print(f"\n✓ {row['km_marker']}")
        print(f"  Trains Reporting     : {row['trains_reported']} ({row['train_list']})")
        print(f"  Defect Type          : {row['defect_type']}")
        print(f"  Avg Confidence       : {row['avg_detection_confidence']}%")
        print(f"  Final Confidence     : {row['final_confidence']}% ⬆️")
        print(f"  Risk Score           : {row['avg_risk_score']}/100")
        print(f"  Detection Period     : {row['first_detection']} to {row['last_detection']}")
        print(f"  Status               : {row['validation_status']}")
    
    os.makedirs("data", exist_ok=True)
    
    # Save multi-train data
    multi_train_df.to_csv("data/multi_train_detections.csv", index=False)
    
    # Save validation results
    validation_df.to_csv("data/validation_results.csv", index=False)
    
    print(f"\n✅ Multi-train detections saved to data/multi_train_detections.csv")
    print(f"✅ Validation results saved to data/validation_results.csv")
    
    return validation_df

if __name__ == "__main__":
    run_validation_agent()