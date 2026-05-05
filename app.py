import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client

# -------------------------
# SUPABASE CONFIG
# -------------------------
SUPABASE_URL = "YOUR_URL"
SUPABASE_KEY = "YOUR_KEY"

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
    st.image("logo.png", width=300)

with col2:
    st.title("Performance Management Dashboard")

# -------------------------
# LOAD DATA FROM DATABASE
# -------------------------
@st.cache_data(ttl=5)
def load_data():
    response = supabase.table("employees").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        df = pd.DataFrame({
            "Employee": ["Alice", "Bob"],
            "Q1": [70, 60],
            "Q2": [75, 65],
            "Q3": [80, 70],
            "Q4": [85, 72],
            "Appraisal Completed": [True, False]
        })
    return df

def save_data(df):
    # Clear table and insert fresh data
    supabase.table("employees").delete().neq("Employee", "").execute()
    supabase.table("employees").insert(df.to_dict(orient="records")).execute()

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
df["Improvement %"] = ((df["Q4"] - df["Q1"]) / df["Q1"]) * 100

avg_improvement = df["Improvement %"].mean()
completion_rate = df["Appraisal Completed"].mean() * 100

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

selected_employee = st.selectbox("Select Employee", df["Employee"])

emp_data = df[df["Employee"] == selected_employee]

trend = pd.DataFrame({
    "Quarter": ["Q1", "Q2", "Q3", "Q4"],
    "Score": [
        emp_data["Q1"].values[0],
        emp_data["Q2"].values[0],
        emp_data["Q3"].values[0],
        emp_data["Q4"].values[0],
    ]
})

st.line_chart(trend.set_index("Quarter"))

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("© 2026 Performance Dashboard")
