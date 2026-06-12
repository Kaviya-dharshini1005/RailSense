import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
sys.path.append('..')

# Page config
st.set_page_config(
    page_title="Indian Railways — RailSense Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #1e3a8a 0%, #dc2626 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .header-container h1 {
        margin: 0;
        font-size: 2.5em;
    }
    .logo {
        font-size: 3em;
    }
    .status-badge {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.9em;
    }
    .status-green { background-color: #10b981; color: white; }
    .status-yellow { background-color: #f59e0b; color: white; }
    .status-orange { background-color: #ff8c42; color: white; }
    .status-red { background-color: #ef4444; color: white; }
    .metric-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-box h3 { margin: 0; font-size: 2em; }
    .metric-box p { margin: 5px 0 0 0; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# Authentication System
def login_page():
    st.markdown("""
    <div class="header-container">
        <div class="logo">🚆</div>
        <div>
            <h1>🇮🇳 Indian Railways</h1>
            <p style="margin: 0; font-size: 1.2em;">RailSense — Track Health Monitoring System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## Login to RailSense Portal")
        
        user_type = st.selectbox(
            "Select Your Role:",
            ["Select an option", "Track Maintenance Official", "Station Manager", "Operations Chief", "Quality Inspector"]
        )
        
        if user_type != "Select an option":
            employee_id = st.text_input("Employee ID (e.g., IR-123456)")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                if employee_id and password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = user_type
                    st.session_state.employee_id = employee_id
                    st.rerun()
                else:
                    st.error("Please enter both Employee ID and Password")
    
    with col2:
        st.markdown("### 🎫 Quick Links")
        st.markdown("""
        **For Passengers:**
        
        [🚂 Book Train Tickets](https://www.irctc.co.in)
        
        **For Railway Officials:**
        
        Login with your credentials
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #666;">
        <p><strong>🇮🇳 Indian Railways</strong></p>
        <p>Ministry of Railways | Autonomous Track Health Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        risk_df = pd.read_csv("data/risk_assessment.csv")
        validation_df = pd.read_csv("data/validation_results.csv")
        rul_df = pd.read_csv("data/rul_predictions.csv")
        dispatch_df = pd.read_csv("data/dispatch_tickets.csv")
        route_df = pd.read_csv("data/route.csv")
        crews_df = pd.read_csv("data/crews.csv")
        return risk_df, validation_df, rul_df, dispatch_df, route_df, crews_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Routes data
ROUTES = {
    "Chennai - Mumbai (Central)": {
        "start": (13.0827, 80.2707),
        "end": (19.0760, 72.8777),
        "trains": ["Rajdhani Express", "Shatabdi Express", "Local Passenger 101", "Freight Express"]
    },
    "Delhi - Kolkata (Eastern)": {
        "start": (28.7041, 77.1025),
        "end": (22.5726, 88.3639),
        "trains": ["Rajdhani Express", "Howrah Express", "Local Passenger 201", "Mail Express"]
    },
    "Mumbai - Bangalore (South)": {
        "start": (19.0760, 72.8777),
        "end": (12.9716, 77.5946),
        "trains": ["Express 301", "Shatabdi", "Passenger Express", "Goods Train"]
    },
    "Delhi - Chennai (North-South)": {
        "start": (28.7041, 77.1025),
        "end": (13.0827, 80.2707),
        "trains": ["Tamil Nadu Express", "Rajdhani", "Mail Express", "Passenger Local"]
    }
}

# Main app
if not st.session_state.logged_in:
    login_page()
else:
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="logo">🚆</div>
        <div>
            <h1>🇮🇳 Indian Railways</h1>
            <p style="margin: 0; font-size: 1.2em;">RailSense — Autonomous Track Health Monitoring</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Railway Map", "Risk Analysis", "RUL Predictions", "Work Orders", 
         "Crew Details", "FAQ", "Contact Us"],
        key="page_nav"
    )
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**🇮🇳 Logged in as:**\n\n{st.session_state.user_type}\n\n{st.session_state.employee_id}")
    
    # Load data
    risk_df, validation_df, rul_df, dispatch_df, route_df, crews_df = load_data()
    
    if risk_df is not None:
        
        # PAGE: Dashboard
        if page == "Dashboard":
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                critical = len(dispatch_df[dispatch_df['priority_flag'] == 'CRITICAL'])
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{critical}</h3>
                    <p>Critical Issues</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                verified = len(validation_df[validation_df['trains_reported'] >= 2])
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{verified}</h3>
                    <p>Verified Issues</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                imminent = len(rul_df[rul_df['days_until_critical'] <= 1])
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{imminent}</h3>
                    <p>Imminent Failures</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_conf = risk_df['confidence'].str.rstrip('%').astype(float).mean()
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{avg_conf:.0f}%</h3>
                    <p>Avg Confidence</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                monitored = len(route_df)
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{monitored}</h3>
                    <p>Segments</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Risk Distribution")
                fig_risk = px.histogram(risk_df, x='risk_score', nbins=20, 
                    color_discrete_sequence=['#dc2626'], title="")
                st.plotly_chart(fig_risk, use_container_width=True)
            
            with col2:
                st.subheader("Work Order Status")
                urgency = dispatch_df['urgency_level'].value_counts()
                fig_urg = px.pie(values=urgency.values, names=urgency.index, title="")
                st.plotly_chart(fig_urg, use_container_width=True)
        
        # PAGE: Railway Map
        elif page == "Railway Map":
            st.subheader("Interactive Railway Route Map — 🇮🇳 India")
            
            selected_route = st.selectbox("Select Route:", list(ROUTES.keys()))
            route_info = ROUTES[selected_route]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scattergeo(
                    lon=[route_info['start'][1], route_info['end'][1]],
                    lat=[route_info['start'][0], route_info['end'][0]],
                    mode='markers+lines',
                    marker=dict(size=15, color=['green', 'red']),
                    line=dict(width=2, color='blue')
                ))
                
                fig.update_layout(
                    title=f"Route: {selected_route}",
                    geo=dict(scope='asia', 
                        center=dict(lat=20, lon=78),
                        projection_type='mercator'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🚂 Active Trains")
                for train in route_info['trains']:
                    st.markdown(f"• {train}")
        
        # PAGE: Risk Analysis
        elif page == "Risk Analysis":
            st.subheader("Track Health Risk Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### High Risk Zones")
                top_risk = risk_df.nlargest(10, 'risk_score')[['km_marker', 'risk_score']]
                for _, row in top_risk.iterrows():
                    if row['risk_score'] >= 80:
                        status = '<span class="status-badge status-red">🔴</span>'
                    elif row['risk_score'] >= 60:
                        status = '<span class="status-badge status-orange">🟠</span>'
                    else:
                        status = '<span class="status-badge status-yellow">🟡</span>'
                    st.markdown(f"{row['km_marker']} — {row['risk_score']:.1f} {status}", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Urgency Breakdown")
                fig_urg = px.pie(dispatch_df, names='urgency_level', title="")
                st.plotly_chart(fig_urg, use_container_width=True)
        
        # PAGE: RUL Predictions
        elif page == "RUL Predictions":
            st.subheader("Failure Timeline — Days to Critical")
            
            rul_valid = rul_df[rul_df['days_until_critical'] != float('inf')].sort_values('days_until_critical')
            
            fig = px.bar(rul_valid, x='km_marker', y='days_until_critical',
                color_discrete_sequence=['#dc2626'],
                labels={'days_until_critical': 'Days', 'km_marker': 'Location'})
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Imminent (< 1 day)", len(rul_df[rul_df['days_until_critical'] <= 1]))
            with col2:
                st.metric("🟠 Urgent (1-3 days)", len(rul_df[(rul_df['days_until_critical'] > 1) & (rul_df['days_until_critical'] <= 3)]))
            with col3:
                st.metric("🟡 Soon (3-7 days)", len(rul_df[(rul_df['days_until_critical'] > 3) & (rul_df['days_until_critical'] <= 7)]))
        
        # PAGE: Work Orders
        elif page == "Work Orders":
            st.subheader("Autonomous Dispatch Work Orders")
            
            filter_urgency = st.selectbox("Filter by Urgency:", ['ALL', 'URGENT', 'HIGH', 'MEDIUM'])
            
            if filter_urgency != 'ALL':
                filtered = dispatch_df[dispatch_df['urgency_level'] == filter_urgency]
            else:
                filtered = dispatch_df
            
            st.metric("Total Work Orders", len(filtered))
            
            for _, row in filtered.head(10).iterrows():
                with st.expander(f"{row['track_location_km']} — Crew: {row['assigned_crew']} — {row['repair_deadline']}"):
                    st.write(f"**Defect:** {row['defect_type']}")
                    st.write(f"**Action:** {row['action']}")
                    st.write(f"**Window:** {row['repair_window']}")
        
        # PAGE: Crew Details
        elif page == "Crew Details":
            st.subheader("Maintenance Crews — Station Wise")
            
            crews_df_sorted = crews_df.sort_values('km')
            
            for _, crew in crews_df_sorted.iterrows():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{crew['crew_id']}**")
                with col2:
                    st.write(f"📍 KM {crew['km']}")
                with col3:
                    st.write(f"👥 {crew['members']} members")
                with col4:
                    status_col = "status-green" if crew['status'] == 'Available' else "status-orange"
                    st.markdown(f'<span class="status-badge {status_col}">{crew["status"]}</span>', unsafe_allow_html=True)
        
        # PAGE: FAQ
        elif page == "FAQ":
            st.subheader("Frequently Asked Questions")
            
            faqs = {
                "What is RailSense?": "RailSense is an autonomous AI system that monitors railway track health in real-time using vibration sensors, cameras, and multi-train validation.",
                "How does it detect anomalies?": "The system uses Isolation Forest ML model to detect vibration anomalies, combined with visual inspection via camera, and validates findings across multiple train passes.",
                "What do the colors mean?": "🟢 Green = Healthy (90-100), 🟡 Yellow = Monitor (70-89), 🟠 Orange = Maintenance (50-69), 🔴 Red = Critical (<50)",
                "How are crews assigned?": "Maintenance crews are automatically assigned based on proximity to the fault location and current availability.",
                "What is RUL prediction?": "RUL (Remaining Useful Life) predicts how many days until a track section becomes critical, enabling preventive maintenance."
            }
            
            for question, answer in faqs.items():
                with st.expander(question):
                    st.write(answer)
        
        # PAGE: Contact Us
        elif page == "Contact Us":
            st.subheader("Contact RailSense Support")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚨 Emergency Support")
                st.write("📞 Toll-Free: 1800-RAIL-SOS")
                st.write("📧 Email: support@railsense.gov.in")
                st.write("⏰ 24/7 Available")
            
            with col2:
                st.markdown("### 🏢 Office Address")
                st.write("Indian Railways HQ")
                st.write("Ministry of Railways")
                st.write("New Delhi, India")
            
            st.markdown("---")
            st.markdown("### Send Feedback")
            with st.form("feedback_form"):
                name = st.text_input("Your Name")
                email = st.text_input("Email")
                message = st.text_area("Message")
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.success("Thank you! Your feedback has been recorded.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p><strong>🇮🇳 Indian Railways — RailSense System</strong></p>
    <p>Autonomous Track Health Monitoring | Ministry of Railways</p>
</div>
""", unsafe_allow_html=True)
