
import streamlit as st
import pandas as pd
import numpy as np
import os
from supabase import create_client

# -------------------------
# SUPABASE CONFIG
# -------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://klfkkitsbuaclttnncap.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_2tcV04t6R3BXva5v2K-rLw_skW2ls_p")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Performance Dashboard", layout="wide")

# -------------------------
# LOAD DATA (READ ONLY — FIXED)
# -------------------------
@st.cache_data(ttl=10)
def load_data():
    response = supabase.table("employees").select("*").execute()
    data = response.data or []

    return pd.DataFrame(data)

# -------------------------
# SEED DATA (RUN ON DEMAND ONLY)
# -------------------------
def seed_data():
    default_data = [
        {
            "employee": "Alice",
            "q1": 70,
            "q2": 75,
            "q3": 80,
            "q4": 85,
            "appraisal_completed": True
        },
        {
            "employee": "Bob",
            "q1": 60,
            "q2": 65,
            "q3": 70,
            "q4": 72,
            "appraisal_completed": False
        }
    ]

    supabase.table("employees").insert(default_data).execute()

# -------------------------
# SAVE DATA (UPSERT SAFE VERSION)
# -------------------------
def save_data(df):
    try:
        # safer approach: delete + insert (controlled)
        supabase.table("employees").delete().neq("employee", "NONE").execute()

        supabase.table("employees").insert(
            df.to_dict(orient="records")
        ).execute()

    except Exception as e:
        st.error(f"Save failed: {e}")

# -------------------------
# HEADER
# -------------------------
st.title("Performance Management Dashboard")

if st.button("Seed Database (First Time Only)"):
    seed_data()
    st.success("Database seeded!")

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

edited_df = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    use_container_width=True
)

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
    st.metric("% Improvement", f"{avg_improvement:.2f}%")

with col2:
    st.metric("Completion Rate", f"{completion_rate:.2f}%")

# -------------------------
# TREND
# -------------------------
st.subheader("Employee Performance Trend")

if not df.empty:

    selected_employee = st.selectbox(
        "Select Employee",
        df["employee"].unique()
    )

    emp_data = df[df["employee"] == selected_employee]

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
st.caption("© 2026 Performance Dashboard")
