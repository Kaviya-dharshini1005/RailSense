import pandas as pd
import numpy as np
import os

# Simulated GPS coordinates along Chennai-Mumbai Central Railway
# Real route: ~1662 km, we simulate 50 key km markers

def generate_route():
    # Approximate GPS points along Chennai-Mumbai route
    route_points = [
        {"km": 0,    "lat": 13.0827, "lon": 80.2707, "station": "Chennai Central"},
        {"km": 50,   "lat": 13.2500, "lon": 79.9500, "station": "Arakkonam"},
        {"km": 130,  "lat": 13.6667, "lon": 79.5000, "station": "Katpadi"},
        {"km": 210,  "lat": 14.1667, "lon": 78.8333, "station": "Renigunta"},
        {"km": 310,  "lat": 14.4426, "lon": 78.1476, "station": "Cuddapah"},
        {"km": 420,  "lat": 15.1667, "lon": 77.3333, "station": "Guntakal"},
        {"km": 530,  "lat": 15.8281, "lon": 76.6722, "station": "Hospet"},
        {"km": 620,  "lat": 16.8333, "lon": 76.0000, "station": "Gadag"},
        {"km": 720,  "lat": 17.3333, "lon": 75.0167, "station": "Solapur"},
        {"km": 850,  "lat": 18.0000, "lon": 74.0000, "station": "Kurduwadi"},
        {"km": 950,  "lat": 18.5167, "lon": 73.8553, "station": "Pune"},
        {"km": 1100, "lat": 19.0000, "lon": 73.5000, "station": "Karjat"},
        {"km": 1200, "lat": 19.2183, "lon": 72.9781, "station": "Thane"},
        {"km": 1270, "lat": 19.0760, "lon": 72.8777, "station": "Mumbai CST"},
    ]

    # Interpolate to get a point every 10km
    full_route = []
    for i in range(len(route_points) - 1):
        p1 = route_points[i]
        p2 = route_points[i + 1]
        km_diff = p2["km"] - p1["km"]
        steps = km_diff // 10

        for s in range(steps):
            frac = s / steps
            full_route.append({
                "km_marker": f"KM_{p1['km'] + s * 10}",
                "km": p1["km"] + s * 10,
                "lat": p1["lat"] + frac * (p2["lat"] - p1["lat"]),
                "lon": p1["lon"] + frac * (p2["lon"] - p1["lon"]),
                "nearest_station": p1["station"]
            })

    df = pd.DataFrame(full_route)

    # Assign simulated maintenance crews along the route
    crew_positions = []
    for i, row in df.iterrows():
        if i % 8 == 0:  # crew every ~80km
            crew_positions.append({
                "crew_id": f"Crew_{len(crew_positions) + 1}",
                "km": row["km"],
                "lat": row["lat"],
                "lon": row["lon"],
                "members": np.random.randint(3, 6),
                "status": np.random.choice(
                    ["Available", "Available", "On Duty"],
                    p=[0.5, 0.3, 0.2]
                )
            })

    route_df = pd.DataFrame(full_route)
    crew_df = pd.DataFrame(crew_positions)

    os.makedirs("data", exist_ok=True)
    route_df.to_csv("data/route.csv", index=False)
    crew_df.to_csv("data/crews.csv", index=False)

    print("✅ GPS route generated!")
    print(f"Total route segments: {len(route_df)}")
    print(f"Maintenance crews deployed: {len(crew_df)}")
    print(f"\nSample route points:")
    print(route_df.head(3).to_string())
    print(f"\nSample crews:")
    print(crew_df.head(3).to_string())

    return route_df, crew_df

if __name__ == "__main__":
    generate_route()