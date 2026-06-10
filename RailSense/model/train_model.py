import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
import pickle
import os

def train_model():
    # Load the simulated data
    df = pd.read_csv("data/track_data.csv")
    
    # Features for training
    X = df[['vibration']].values
    
    # Train Isolation Forest
    # contamination = roughly how much of data is anomalous
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    
    model.fit(X)
    
    # Predict (-1 = anomaly, 1 = normal)
    df['prediction'] = model.predict(X)
    df['anomaly_score'] = model.decision_function(X)
    
    # Convert to readable labels
    df['predicted_label'] = df['prediction'].map({1: 'normal', -1: 'anomaly'})
    
    # Show results
    print("✅ Model trained successfully!")
    print(f"\nDetection Summary:")
    print(f"Total anomalies detected: {(df['prediction'] == -1).sum()}")
    print(f"Total normal points: {(df['prediction'] == 1).sum()}")
    
    # Save model
    os.makedirs("model", exist_ok=True)
    with open("model/railsense_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("\n✅ Model saved to model/railsense_model.pkl")
    
    # Save predictions
    df.to_csv("data/track_data_predictions.csv", index=False)
    print("✅ Predictions saved to data/track_data_predictions.csv")
    
    return model, df

if __name__ == "__main__":
    model, df = train_model()