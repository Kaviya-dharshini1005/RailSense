import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import os
from datetime import datetime

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS points"""
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def find_nearest_crew(track_lat, track_lon, crews_df):
    """Find the nearest available maintenance crew"""
    crews_df['distance'] = crews_df.apply(
        lambda row: haversine_distance(track_lat, track_lon, row['lat'], row['lon']),
        axis=1
    )
    
    # Prefer available crews
    available = crews_df[crews_df['status'] == 'Available']
    if len(available) > 0:
        nearest = available.loc[available['distance'].idxmin()]
    else:
        nearest = crews_df.loc[crews_df['distance'].idxmin()]
    
    return nearest

def determine_repair_window(km, risk_score):
    """
    Determine optimal repair window based on traffic patterns.
    Higher traffic zones get evening/night windows to minimize disruption.
    """
    # Night corridors: 11 PM - 5 AM (low traffic)
    if risk_score >= 80:
        return "11:00 PM - 2:00 AM (Urgent Window)"
    elif km % 300 < 100:
        # Major station areas: need wider window
        return "10:00 PM - 3:00 AM (Extended Window)"
    else:
        # Remote sections: flexible
        return "9:00 PM - 4:00 AM (Standard Window)"

def determine_action_type(visual_defect, risk_score):
    """Map defect to specific maintenance action"""
    action_map = {
        'surface_crack':  'Rail Section Replacement',
        'rail_corrosion': 'Rail Surface Treatment & Inspection',
        'missing_bolt':   'Fastener & Connection Repair',
        'weld_defect':    'Weld Inspection & Rework',
        'ballast_void':   'Ballast Replenishment & Tamping',
        'no_defect':      'Sensor-Based Inspection'
    }
    return action_map.get(visual_defect, 'Full Track Section Assessment')

def run_maintenance_planning():
    """
    Agent 6 — Maintenance Planning Agent
    Takes verified issues and recommends nearest crew + repair action.
    """
    fused_df = pd.read_csv("data/fused_assessment.csv")
    crews_df = pd.read_csv("data/crews.csv")
    route_df = pd.read_csv("data/route.csv")
    
    # Merge route GPS data
    fused_df = fused_df.merge(
        route_df[['km_marker', 'lat', 'lon']],
        on='km_marker',
        how='left'
    )
    
    # Filter verified issues only
    verified = fused_df[
        fused_df['fusion_verdict'].str.contains("VERIFIED")
    ].copy()
    
    print("🔧 RailSense Maintenance Planning Agent\n")
    print(f"Processing {len(verified)} verified maintenance issues...\n")
    
    recommendations = []
    for _, issue in verified.iterrows():
        # Find nearest crew
        nearest_crew = find_nearest_crew(
            issue['lat'], issue['lon'], crews_df
        )
        
        # Determine repair window
        window = determine_repair_window(
            issue['km'], issue['risk_score']
        )
        
        # Determine action
        action = determine_action_type(
            issue['visual_defect'], issue['risk_score']
        )
        
        # Repair urgency
        if issue['risk_score'] >= 90:
            urgency = "URGENT"
            deadline = "12 Hours"
        elif issue['risk_score'] >= 80:
            urgency = "HIGH"
            deadline = "24 Hours"
        else:
            urgency = "MEDIUM"
            deadline = "48 Hours"
        
        recommendations.append({
            "issue_id": len(recommendations) + 1,
            "km_marker": issue['km_marker'],
            "km": issue['km'],
            "risk_score": issue['risk_score'],
            "fused_confidence": issue['fused_confidence'],
            "defect_type": issue['visual_defect'],
            "recommended_action": action,
            "nearest_crew": nearest_crew['crew_id'],
            "crew_distance_km": round(nearest_crew['distance'], 2),
            "crew_members": int(nearest_crew['members']),
            "crew_status": nearest_crew['status'],
            "repair_window": window,
            "urgency": urgency,
            "deadline": deadline,
            "estimated_duration_hours": np.random.randint(2, 8)
        })
    
    rec_df = pd.DataFrame(recommendations)
    rec_df = rec_df.sort_values('risk_score', ascending=False)
    
    # Summary
    urgent = len(rec_df[rec_df['urgency'] == 'URGENT'])
    high = len(rec_df[rec_df['urgency'] == 'HIGH'])
    medium = len(rec_df[rec_df['urgency'] == 'MEDIUM'])
    
    print(f"Total verified issues: {len(rec_df)}")
    print(f"\nUrgency Breakdown:")
    print(f"🔴 URGENT (< 12 hrs) : {urgent}")
    print(f"🟠 HIGH (< 24 hrs)   : {high}")
    print(f"🟡 MEDIUM (< 48 hrs) : {medium}")
    
    print(f"\n--- MAINTENANCE RECOMMENDATIONS ---")
    for _, row in rec_df.head(5).iterrows():
        print(f"\n📍 Issue #{row['issue_id']} — {row['km_marker']}")
        print(f"   Risk Score      : {row['risk_score']}/100")
        print(f"   Defect Type     : {row['defect_type']}")
        print(f"   Recommended     : {row['recommended_action']}")
        print(f"   Nearest Crew    : {row['nearest_crew']}")
        print(f"   Distance        : {row['crew_distance_km']} km")
        print(f"   Crew Size       : {row['crew_members']} members")
        print(f"   Repair Window   : {row['repair_window']}")
        print(f"   Urgency         : {row['urgency']}")
        print(f"   Deadline        : {row['deadline']}")
    
    os.makedirs("data", exist_ok=True)
    rec_df.to_csv("data/maintenance_recommendations.csv", index=False)
    print(f"\n✅ Recommendations saved to data/maintenance_recommendations.csv")
    
    return rec_df

if __name__ == "__main__":
    run_maintenance_planning()