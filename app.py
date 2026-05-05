import streamlit as st
import pandas as pd
import numpy as np

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Performance Dashboard", layout="wide")

# -------------------------
# CUSTOM CSS (White, Black, Orange Theme)
# -------------------------
st.markdown("""
    <style>
    body {
        background-color: white;
        color: black;
    }
    .stApp {
        background-color: white;
    }
    h1, h2, h3 {
        color: black;
    }
    .metric-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid orange;
    }
    .stButton>button {
        background-color: orange;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER WITH LOGO
# -------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=80)  # Add your logo file in same folder

with col2:
    st.title("Performance Management Dashboard")

# -------------------------
# SAMPLE DATA (Editable)
# -------------------------
data = {
    "Employee": ["Alice", "Bob", "Charlie", "David"],
    "Q1": [70, 60, 80, 75],
    "Q2": [75, 65, 82, 78],
    "Q3": [80, 70, 85, 80],
    "Q4": [85, 72, 88, 83],
    "Appraisal Completed": [True, True, False, True]
}

df = pd.DataFrame(data)

# -------------------------
# EDITABLE TABLE
# -------------------------
st.subheader("Employee Quarterly Reviews")

df = st.data_editor(df, num_rows="dynamic")

# -------------------------
# KPI CALCULATIONS
# -------------------------
# % Improvement (Q1 → Q4)
df["Improvement %"] = ((df["Q4"] - df["Q1"]) / df["Q1"]) * 100

avg_improvement = df["Improvement %"].mean()

# Appraisal Completion Rate
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
# EMPLOYEE PERFORMANCE VIEW
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
# RAW DATA VIEW
# -------------------------
st.subheader("Full Data")

st.dataframe(df)

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("© 2026 Performance Dashboard | Built with Streamlit")
