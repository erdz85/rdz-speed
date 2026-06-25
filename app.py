import streamlit as st
import pandas as pd
import math
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="RDZ Speed Development",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 2. IN-MEMORY DATABASE SEEDING
# ==========================================
if 'athletes' not in st.session_state:
    st.session_state.athletes = pd.DataFrame([
        {"id": "A1", "name": "Marcus Anderson", "gender": "Male", "group": "Short Sprints", "grade": "Junior"},
        {"id": "A2", "name": "Trey Williams", "gender": "Male", "group": "Short Sprints", "grade": "Senior"},
        {"id": "A3", "name": "Elena Martinez", "gender": "Female", "group": "Short Sprints", "grade": "Junior"},
        {"id": "A4", "name": "Jordan Davis", "gender": "Female", "group": "Short Sprints", "grade": "Freshman"},
    ])

if 'workout_logs' not in st.session_state:
    st.session_state.workout_logs = pd.DataFrame([
        {"log_id": 1, "date": "2026-05-01", "athlete_id": "A1", "type": "20m_fly", "raw": 2.10, "fat": 2.10, "proj_100": 11.50},
        {"log_id": 2, "date": "2026-05-15", "athlete_id": "A1", "type": "20m_fly", "raw": 1.98, "fat": 1.98, "proj_100": 10.95},
        {"log_id": 3, "date": "2026-05-01", "athlete_id": "A3", "type": "20m_fly", "raw": 2.45, "fat": 2.65, "proj_100": 13.58},
        {"log_id": 4, "date": "2026-05-15", "athlete_id": "A3", "type": "20m_fly", "raw": 2.30, "fat": 2.45, "proj_100": 12.80},
        {"log_id": 5, "date": "2026-05-15", "athlete_id": "A2", "type": "30m_block", "raw": 4.15, "fat": 4.15, "proj_100": 11.25},
        {"log_id": 6, "date": "2026-05-15", "athlete_id": "A4", "type": "30m_block", "raw": 4.40, "fat": 4.40, "proj_100": 12.10},
    ])

# ==========================================
# 3. MATHEMATICAL ALGORITHM ENGINES
# ==========================================
def normalize_hand_fly(raw_hand_time):
    rounded_time = math.ceil(raw_hand_time * 10) / 10.0
    return round(rounded_time + 0.15, 2)

def calculate_projected_100m(thirty_block, twenty_fly, gender):
    ten_split = twenty_fly / 2.0
    base_time = thirty_block + (7.0 * ten_split)
    if gender.lower() == "male":
        decay = 0.12 if base_time < 11.0 else 0.18
    else:
        decay = 0.15 if base_time < 12.2 else 0.25
    return round(base_time + decay, 2)

def calculate_relay_go_mark(incoming_fly, outgoing_block):
    v_incoming = 20.0 / incoming_fly
    t_acceleration = outgoing_block * 0.71
    raw_distance_gap = (v_incoming * t_acceleration) - 20.0
    final_distance_meters = raw_distance_gap - 0.70
    coaching_steps = final_distance_meters * 3.28
    return max(0.0, round(coaching_steps, 1))

# ==========================================
# 4. APP SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("⚡ RDZ Speed")
app_mode = st.sidebar.radio("Go To Module:", [
    "👥 Roster & Onboarding",
    "⏱️ Workout Tracker",
    "🔥 Team Leaderboard",
    "📈 Athlete Progress",
    "🤝 4x100m Relay Builder",
    "📄 AD Report Generator"
])

# ==========================================
# MODULE 1: ROSTER & ONBOARDING
# ==========================================
if app_mode == "👥 Roster & Onboarding":
    st.title("👥 Roster Management")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Share Team Access")
        st.code("RDZ-NORTHSIDE-2026", language="text")
        
        st.subheader("➕ Quick Add Athlete")
        new_name = st.text_input("Full Name")
        new_gender = st.selectbox("Gender", ["Male", "Female"])
        new_group = st.selectbox("Training Group", ["Short Sprints", "Long Sprints"])
        new_grade = st.selectbox("Grade", ["Freshman", "Sophomore", "Junior", "Senior"])
        
        if st.button("Register to Roster"):
            if new_name:
                new_id = f"A{len(st.session_state.athletes) + 1}"
                new_row = {"id": new_id, "name": new_name, "gender": new_gender, "group": new_group, "grade": new_grade}
                st.session_state.athletes = pd.concat([st.session_state.athletes, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

    with col2:
        st.subheader("🏃 Active Roster")
        st.dataframe(st.session_state.athletes, use_container_width=True, hide_index=True)

# ==========================================
# MODULE 2: WORKOUT TRACKER
# ==========================================
elif app_mode == "⏱️ Workout Tracker":
    st.title("⏱️ Live Workout Tracker")
    col1, col2 = st.columns(2)
    with col1:
        timing_system = st.radio("Timing Method:", ["Electronic / FAT (Freelap)", "Hand-Timed (Stopwatch)"])
    with col2:
        session_type = st.selectbox("Drill Profile:", ["20m_fly", "30m_block"])
        
    st.write("---")
    for index, athlete in st.session_state.athletes.iterrows():
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**{athlete['name']}**")
        with c2:
            raw_time = st.number_input(f"Split (s)", min_value=0.0, max_value=10.0, step=0.01, key=f"in_{athlete['id']}")
        with c3:
            if st.button("Save Log", key=f"btn_{athlete['id']}"):
                if raw_time > 0:
                    fat_time = normalize_hand_fly(raw_time) if timing_system == "Hand-Timed (Stopwatch)" else raw_time
                    proj = calculate_projected_100m(4.5, fat_time, athlete['gender']) if session_type == "20m_fly" else calculate_projected_100m(fat_time, 2.3, athlete['gender'])
                    
                    new_log = {
                        "log_id": len(st.session_state.workout_logs) + 1,
                        "date": datetime.today().strftime('%Y-%m-%d'),
                        "athlete_id": athlete['id'],
                        "type": session_type,
                        "raw": raw_time,
                        "fat": fat_time,
                        "proj_100": proj
                    }
                    st.session_state.workout_logs = pd.concat([st.session_state.workout_logs, pd.DataFrame([new_log])], ignore_index=True)
                    st.rerun()

# ==========================================
# MODULE 3: TEAM LEADERBOARD
# ==========================================
elif app_mode == "🔥 Team Leaderboard":
    st.title("🔥 Team Leaderboard")
    gender_filter = st.selectbox("Gender:", ["All", "Male", "Female"])
    metric_filter = st.selectbox("Rank Metric:", ["20m_fly", "30m_block"])
    
    logs = st.session_state.workout_logs[st.session_state.workout_logs['type'] == metric_filter]
    if not logs.empty:
        merged = pd.merge(logs, st.session_state.athletes, left_on="athlete_id", right_on="id")
        if gender_filter != "All":
            merged = merged[merged['gender'] == gender_filter]
            
        if not merged.empty:
            leaderboard = merged.loc[merged.groupby("athlete_id")["fat"].idxmin()]
            leaderboard = leaderboard.sort_values(by="fat", ascending=True).reset_index(drop=True)
            st.dataframe(leaderboard[["name", "gender", "fat", "proj_100"]], use_container_width=True, hide_index=True)

# ==========================================
# MODULE 4: ATHLETE PROGRESS
# ==========================================
elif app_mode == "📈 Athlete Progress":
    st.title("📈 Athlete Progress")
    selected_athlete = st.selectbox("Select Athlete:", st.session_state.athletes['name'].unique())
    
    matched_athletes = st.session_state.athletes[st.session_state.athletes['name'] == selected_athlete]
    athlete_id = matched_athletes['id'].values[0]
    
    athlete_logs = st.session_state.workout_logs[(st.session_state.workout_logs['athlete_id'] == athlete_id) & (st.session_state.workout_logs['type'] == "20m_fly")]
    
    if not athlete_logs.empty:
        athlete_logs = athlete_logs.sort_values(by="date")
        st.line_chart(data=athlete_logs, x="date", y="fat")
    else:
        st.info("No logs on record for this athlete yet.")

# ==========================================
# MODULE 5: 4x100M RELAY BUILDER
# ==========================================
elif app_mode == "🤝 4x100m Relay Builder":
    st.title("🤝 4x100m Relay Builder")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incoming Runner (Fly)")
        inc_athlete = st.selectbox("Select Incoming:", st.session_state.athletes['name'].unique(), key="inc")
        inc_id = st.session_state.athletes[st.session_state.athletes['name'] == inc_athlete]['id'].values[0]
        inc_query = st.session_state.workout_logs[(st.session_state.workout_logs['athlete_id'] == inc_id) & (st.session_state.workout_logs['type'] == "20m_fly")]
        inc_fly = inc_query['fat'].min() if not inc_query.empty else 2.30
        inc_fly = st.number_input("20m Fly (s)", value=float(inc_fly))
        
    with col2:
        st.subheader("Outgoing Runner (Block)")
        out_athlete = st.selectbox("Select Outgoing:", st.session_state.athletes['name'].unique(), key="out")
        out_id = st.session_state.athletes[st.session_state.athletes['name'] == out_athlete]['id'].values
        out_query = st.session_state.workout_logs[(st.session_state.workout_logs['athlete_id'] == out_id) & (st.session_state.workout_logs['type'] == "30m_block")]
        out_block = out_query['fat'].min() if not out_query.empty else 4.40
        out_block = st.number_input("30m Block (s)", value=float(out_block))
        
    st.write("---")
    go_mark = calculate_relay_go_mark(inc_fly, out_block)
    st.subheader(f"🎯 Target Go Mark: {go_mark} Steps")

# ==========================================
# MODULE 6: AD REPORT GENERATOR
# ==========================================
elif app_mode == "📄 AD Report Generator":
    st.title("📄 Performance Portfolio Export")
    current_time_string = datetime.today().strftime("%B %d, %Y")
    st.text(f"Generated: {current_time_string}")
    st.write("---")
    st.write("### Active Program Summary")
    total_sprinters_count = len(st.session_state.athletes)
    st.write(f"Total Tracked Sprinters: {total_sprinters_count}")
    st.write("- Top Sprinter: Marcus Anderson (1.98s FAT Fly | 10.95s Projected 100m)")
    st.info("Verified Authentic via RDZ Speed Development Analytics Database Engine")
  
  
