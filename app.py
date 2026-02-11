import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="wide"
)

# --------------------------------------------------
# DARK UI CSS (CUSTOM)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0b0f14, #111827);
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #f9fafb;
}

.subtitle {
    color: #9ca3af;
    font-size: 18px;
}

/* Cards */
.card {
    background: #111827;
    border-radius: 18px;
    padding: 1.5rem;
    border: 1px solid #1f2937;
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
    margin-bottom: 1.5rem;
}

/* Diet cards */
.diet-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.diet-card {
    background: #0f172a;
    border-radius: 16px;
    padding: 1.2rem;
    border: 1px solid #1e293b;
}

.diet-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

/* Upload */
[data-testid="stFileUploader"] {
    background: #020617;
    border: 2px dashed #38bdf8;
    border-radius: 14px;
    padding: 1.2rem;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #22d3ee, #3b82f6);
    color: black;
    font-weight: 700;
    border-radius: 12px;
    padding: 0.8rem 2rem;
    font-size: 16px;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="card">
<h1>🥗 AI-NutritionalCare</h1>
<p class="subtitle">AI-driven Personalized Diet Recommendation System</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
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
        r"patient\s*[:\-]\s*([A-Za-z ]+)",
        r"mr\.?\s+([A-Za-z ]+)",
        r"ms\.?\s+([A-Za-z ]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()

    for line in text.splitlines():
        line = line.strip()
        if 3 < len(line) < 40 and line.replace(" ", "").isalpha():
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

# --------------------------------------------------
# SAMPLE DAY PLAN (LIKE FRIEND)
# --------------------------------------------------
DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "Dinner": "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Snacks": "Roasted Chickpeas (30g), 1 Apple",
    "Notes": "Hydration: Drink at least 8–10 glasses of water."
}

# --------------------------------------------------
# INPUT
# --------------------------------------------------
st.markdown("## 📤 Upload Patient Data")

uploaded = st.file_uploader(
    "Upload Medical Report (PDF / CSV / TXT)",
    type=["pdf", "csv", "txt"]
)

st.radio("Food Preference", ["Vegetarian", "Non-Vegetarian"])
run = st.button("✨ Generate Diet Recommendation")

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
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

    # Week Selector
    week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    day = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"])

    # Day Card Layout (LIKE FRIEND)
    st.markdown(f"""
    <div class="card">
    <h2>{day} Diet Plan</h2>

    <div class="diet-grid">
        <div class="diet-card">
            <div class="diet-title">🍳 Breakfast</div>
            {DAY_PLAN["Breakfast"]}
        </div>

        <div class="diet-card">
            <div class="diet-title">🍛 Lunch</div>
            {DAY_PLAN["Lunch"]}
        </div>

        <div class="diet-card">
            <div class="diet-title">🌙 Dinner</div>
            {DAY_PLAN["Dinner"]}
        </div>

        <div class="diet-card">
            <div class="diet-title">🍎 Snacks</div>
            {DAY_PLAN["Snacks"]}
        </div>

        <div class="diet-card">
            <div class="diet-title">📝 Notes</div>
            {DAY_PLAN["Notes"]}
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
