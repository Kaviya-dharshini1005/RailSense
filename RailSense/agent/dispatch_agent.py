import pandas as pd
import numpy as np
import os
from datetime import datetime
import sys
sys.path.append('.')

def generate_ticket_id():
    """Generate unique ticket ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TKT_{timestamp}"

def generate_dispatch_ticket(issue_num, rec):
    """Generate a complete autonomous work order ticket"""
    
    ticket = {
        "ticket_id": generate_ticket_id(),
        "issue_number": issue_num,
        "timestamp_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        
        # Location Details
        "track_location_km": f"KM_{rec['km']}",
        "km_marker": rec['km_marker'],
        
        # Problem Details
        "defect_type": rec['defect_type'],
        "risk_score": f"{rec['risk_score']}/100",
        "fused_confidence": f"{rec['fused_confidence']}%",
        
        # Recommended Action
        "action": rec['recommended_action'],
        "urgency_level": rec['urgency'],
        "repair_deadline": rec['deadline'],
        
        # Crew Assignment
        "assigned_crew": rec['nearest_crew'],
        "crew_size": f"{rec['crew_members']} members",
        "crew_status": rec['crew_status'],
        "distance_to_site": f"{rec['crew_distance_km']} km",
        
        # Operational Details
        "repair_window": rec['repair_window'],
        "estimated_duration": f"{rec['estimated_duration_hours']} hours",
        
        # Priority Flags
        "priority_flag": "CRITICAL" if rec['risk_score'] >= 90 else "HIGH" if rec['risk_score'] >= 80 else "MEDIUM",
        "auto_generated": "Yes",
        "human_approval_required": "No" if rec['risk_score'] >= 80 else "Optional",
        "status": "ASSIGNED"
    }
    
    return ticket

def format_ticket_display(ticket):
    """Format ticket for display"""
    display = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎟️  WORK ORDER — {ticket['ticket_id']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 LOCATION
   Track: {ticket['track_location_km']} | {ticket['km_marker']}

🔧 DEFECT DETAILS
   Type: {ticket['defect_type']}
   Risk Score: {ticket['risk_score']}
   Confidence: {ticket['fused_confidence']}

✅ RECOMMENDED ACTION
   {ticket['action']}

🚨 PRIORITY
   Level: {ticket['priority_flag']}
   Urgency: {ticket['urgency_level']}
   Deadline: {ticket['repair_deadline']}

👷 CREW ASSIGNMENT
   Crew: {ticket['assigned_crew']}
   Size: {ticket['crew_size']}
   Status: {ticket['crew_status']}
   Distance: {ticket['distance_to_site']}

⏰ OPERATIONAL
   Window: {ticket['repair_window']}
   Duration: {ticket['estimated_duration']}

📋 METADATA
   Auto-Generated: {ticket['auto_generated']}
   Human Approval: {ticket['human_approval_required']}
   Current Status: {ticket['status']}
   Created: {ticket['timestamp_created']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return display

def run_dispatch_agent():
    """
    Agent 7 — Dispatch Agent
    Generates autonomous work orders from maintenance recommendations.
    """
    rec_df = pd.read_csv("data/maintenance_recommendations.csv")
    
    print("🚀 RailSense Dispatch Agent — Autonomous Work Order Generation\n")
    print(f"Generating {len(rec_df)} autonomous work orders...\n")
    
    tickets = []
    for idx, (_, rec) in enumerate(rec_df.iterrows(), 1):
        ticket = generate_dispatch_ticket(idx, rec)
        tickets.append(ticket)
    
    tickets_df = pd.DataFrame(tickets)
    
    # Summary
    critical = len(tickets_df[tickets_df['priority_flag'] == 'CRITICAL'])
    high = len(tickets_df[tickets_df['priority_flag'] == 'HIGH'])
    medium = len(tickets_df[tickets_df['priority_flag'] == 'MEDIUM'])
    
    print(f"Total work orders generated: {len(tickets_df)}")
    print(f"\nPriority Distribution:")
    print(f"🔴 CRITICAL (Risk ≥ 90) : {critical}")
    print(f"🟠 HIGH (Risk 80-89)    : {high}")
    print(f"🟡 MEDIUM (Risk < 80)   : {medium}")
    
    print(f"\n--- SAMPLE WORK ORDERS ---")
    for idx, row in tickets_df.head(3).iterrows():
        print(format_ticket_display(row.to_dict()))
    
    # Save tickets
    os.makedirs("data", exist_ok=True)
    tickets_df.to_csv("data/dispatch_tickets.csv", index=False)
    print(f"\n✅ All {len(tickets_df)} work orders saved to data/dispatch_tickets.csv")
    
    # Also save first ticket as example JSON for reference
    example_ticket = tickets_df.iloc[0].to_dict()
    print(f"✅ First ticket ID: {example_ticket['ticket_id']}")
    
    return tickets_df

if __name__ == "__main__":
    run_dispatch_agent()