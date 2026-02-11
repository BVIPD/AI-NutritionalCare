import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="wide"
)

# ==================================================
# GLOBAL DARK UI CSS (CLEAN & PROFESSIONAL)
# ==================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0b0f14, #0f172a);
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #f9fafb;
}

/* Card */
.card {
    background: linear-gradient(135deg, #0f172a, #020617);
    border-radius: 20px;
    padding: 1.8rem;
    border: 1px solid #1e293b;
    box-shadow: 0 25px 60px rgba(0,0,0,0.65);
    margin-bottom: 1.8rem;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #020617;
    border: 2px dashed #38bdf8;
    border-radius: 16px;
    padding: 1.3rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #22d3ee, #3b82f6);
    color: #020617;
    font-weight: 700;
    border-radius: 14px;
    padding: 0.8rem 2.2rem;
    font-size: 16px;
    border: none;
}

/* Select boxes */
div[data-baseweb="select"] {
    background-color: #020617 !important;
    border-radius: 12px;
}

/* Diet grid */
.diet-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.6rem;
    margin-top: 1.4rem;
}

.diet-card {
    background: #020617;
    border-radius: 16px;
    padding: 1.3rem;
    border: 1px solid #1e293b;
}

.diet-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 0.6rem;
}

.diet-text {
    color: #cbd5f5;
    font-size: 14px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="card">
<h1>🥗 AI-NutritionalCare</h1>
<p style="color:#9ca3af;font-size:18px;">
AI-driven Personalized Diet Recommendation System
</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# HELPERS
# ==================================================
def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    elif ext == "csv":
        df = pd.read_csv(file)
        text = "\n".join(df.astype(str).values.flatten())
    elif ext == "txt":
        text = file.read().decode("utf-8")

    return text.strip()


def extract_patient_name(text):
    patterns = [
        r"patient\s*name\s*[:\-]\s*([A-Za-z ]+)",
        r"name\s*[:\-]\s*([A-Za-z ]+)",
        r"mr\.?\s+([A-Za-z ]+)",
        r"ms\.?\s+([A-Za-z ]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()

    for line in text.splitlines():
        line = line.strip()
        if 4 < len(line) < 40 and line.replace(" ", "").isalpha():
            return line

    return "Patient Name Not Found"


def extract_conditions(text):
    t = text.lower()
    conditions = []
    if "diabetes" in t:
        conditions.append("Diabetes")
    if "cholesterol" in t:
        conditions.append("High Cholesterol")
    if "hypertension" in t or "blood pressure" in t:
        conditions.append("Hypertension")
    return conditions or ["General Health"]

# ==================================================
# SAMPLE DIET DATA (USED FOR ALL DAYS)
# ==================================================
DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "Dinner": "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Snacks": "Roasted Chickpeas (30g), 1 Apple",
    "Notes": "Drink at least 8–10 glasses of water. Avoid sugary drinks."
}

# ==================================================
# INPUT
# ==================================================
st.markdown("## 📤 Upload Patient Data")

uploaded = st.file_uploader(
    "Upload Medical Report (PDF / CSV / TXT)",
    type=["pdf", "csv", "txt"]
)

st.radio("Food Preference", ["Vegetarian", "Non-Vegetarian"])
run = st.button("✨ Generate Diet Recommendation")

# ==================================================
# OUTPUT
# ==================================================
if run:
    if not uploaded:
        st.warning("Please upload a medical report.")
        st.stop()

    text = extract_text(uploaded)
    patient = extract_patient_name(text)
    conditions = extract_conditions(text)

    # Patient Summary
    st.markdown(f"""
    <div class="card">
    <h3>Patient Summary</h3>
    <b>Patient:</b> {patient}<br>
    <b>Medical Condition:</b> {", ".join(conditions)}<br>
    <b>Plan Duration:</b> 1 Month
    </div>
    """, unsafe_allow_html=True)

    # Week & Day selector
    week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    day = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"])

    # Day Plan UI (PROFESSIONAL)
    st.markdown(f"""
    <div class="card">
    <h2>{day} Diet Plan</h2>

    <div class="diet-grid">
        <div class="diet-card">
            <div class="diet-title">🍳 Breakfast</div>
            <div class="diet-text">{DAY_PLAN["Breakfast"]}</div>
        </div>

        <div class="diet-card">
            <div class="diet-title">🍛 Lunch</div>
            <div class="diet-text">{DAY_PLAN["Lunch"]}</div>
        </div>

        <div class="diet-card">
            <div class="diet-title">🌙 Dinner</div>
            <div class="diet-text">{DAY_PLAN["Dinner"]}</div>
        </div>

        <div class="diet-card">
            <div class="diet-title">🍎 Snacks</div>
            <div class="diet-text">{DAY_PLAN["Snacks"]}</div>
        </div>

        <div class="diet-card">
            <div class="diet-title">📝 Notes</div>
            <div class="diet-text">{DAY_PLAN["Notes"]}</div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
