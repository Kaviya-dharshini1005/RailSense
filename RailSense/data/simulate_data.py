import numpy as np
import pandas as pd
import os

def generate_track_data(duration=100, sampling_rate=50, anomaly=True):
    t = np.linspace(0, duration, duration * sampling_rate)
    
    # Normal vibration - smooth low amplitude signal
    normal = np.random.normal(0, 0.2, len(t)) + 0.5 * np.sin(2 * np.pi * 2 * t)
    signal = normal.copy()
    labels = ['normal'] * len(t)

    if anomaly:
        anomaly_indices = np.random.choice(len(t), size=15, replace=False)
        for idx in anomaly_indices:
            deviation_type = np.random.choice([
                'high_impact_deviation',
                'geometry_deviation', 
                'structural_irregularity'
            ])
            if deviation_type == 'high_impact_deviation':
                signal[idx] += np.random.uniform(3, 5)
                labels[idx] = 'high_impact_deviation'
            elif deviation_type == 'geometry_deviation':
                end = min(idx + 20, len(t))
                signal[idx:end] += np.sin(np.linspace(0, np.pi, end - idx)) * 2
                for i in range(idx, end):
                    labels[i] = 'geometry_deviation'
            elif deviation_type == 'structural_irregularity':
                for i in range(idx, len(t), 50):
                    signal[i] += 1.5
                    labels[i] = 'structural_irregularity'

    df = pd.DataFrame({'time': t, 'vibration': signal, 'label': labels})
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_track_data()
    df.to_csv("data/track_data.csv", index=False)
    print("✅ Track health data generated successfully!")
    print(f"Total monitoring points: {len(df)}")
    print(f"\nTrack Health Breakdown:\n{df['label'].value_counts()}")