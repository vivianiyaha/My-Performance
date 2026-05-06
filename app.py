import streamlit as st
import pandas as pd
import numpy as np
import os
from supabase import create_client

# -------------------------
# SUPABASE CONFIG (USE ENV VARS)
# -------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://klfkkitsbuaclttnncap.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_2tcV04t6R3BXva5v2K-rLw_skW2ls_p")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Performance Dashboard", layout="wide")

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
    <style>
    .stApp {background-color: white;}
    h1, h2, h3 {color: black;}
    .metric-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid orange;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
col1, col2 = st.columns([1, 6])

with col1:
    try:
        st.image("logo.png", width=120)
    except:
        st.write("")

with col2:
    st.title("Performance Management Dashboard")

# -------------------------
# LOAD DATA FROM DATABASE
# -------------------------
@st.cache_data(ttl=10)
def load_data():
    try:
        response = supabase.table("employees").select("*").execute()
        data = response.data

        if not data:
            raise ValueError("Empty table")

        df = pd.DataFrame(data)

    except Exception as e:
        st.warning(f"Using fallback data (DB issue: {e})")

        df = pd.DataFrame({
            "employee": ["Alice", "Bob"],
            "q1": [70, 60],
            "q2": [75, 65],
            "q3": [80, 70],
            "q4": [85, 72],
            "appraisal_completed": [True, False]
        })

    return df


def save_data(df):
    try:
        # Replace table contents safely
        supabase.table("employees").delete().neq("employee", "").execute()
        supabase.table("employees").insert(df.to_dict(orient="records")).execute()
    except Exception as e:
        st.error(f"Save failed: {e}")

# -------------------------
# SESSION STATE
# -------------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "last_saved" not in st.session_state:
    st.session_state.last_saved = st.session_state.data.copy()

# -------------------------
# EDITABLE TABLE
# -------------------------
st.subheader("Employee Quarterly Reviews")

edited_df = st.data_editor(st.session_state.data, num_rows="dynamic")

# -------------------------
# AUTO SAVE
# -------------------------
if not edited_df.equals(st.session_state.last_saved):
    save_data(edited_df)
    st.session_state.last_saved = edited_df.copy()
    st.session_state.data = edited_df.copy()
    st.toast("Saved to cloud ✅")

df = edited_df.copy()

# -------------------------
# KPI CALCULATIONS
# -------------------------
try:
    df["improvement_pct"] = ((df["q4"] - df["q1"]) / df["q1"]) * 100

    avg_improvement = df["improvement_pct"].mean()
    completion_rate = df["appraisal_completed"].mean() * 100
except:
    avg_improvement = 0
    completion_rate = 0

# -------------------------
# KPI DISPLAY
# -------------------------
st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <h3>% Improvement Over Time</h3>
        <h2>{avg_improvement:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <h3>Appraisal Completion Rate</h3>
        <h2>{completion_rate:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# TREND
# -------------------------
st.subheader("Employee Performance Trend")

if not df.empty:
    selected_employee = st.selectbox("Select Employee", df["employee"])

    emp_data = df[df["employee"] == selected_employee]

    if not emp_data.empty:
        trend = pd.DataFrame({
            "Quarter": ["Q1", "Q2", "Q3", "Q4"],
            "Score": [
                emp_data["q1"].values[0],
                emp_data["q2"].values[0],
                emp_data["q3"].values[0],
                emp_data["q4"].values[0],
            ]
        })

        st.line_chart(trend.set_index("Quarter"))

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("© 2026 Performance Dashboard")
