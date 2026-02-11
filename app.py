import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --------------------------------------------------
# PAGE CONFIG (VERTICAL)
# --------------------------------------------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="centered"
)

# --------------------------------------------------
# CSS FIX (TEXT VISIBILITY + VERTICAL FLOW)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #111827;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2rem;
    max-width: 850px;
}

h1 {
    color: #065f46;
    font-size: 40px;
    font-weight: 800;
}

h2 {
    color: #047857;
    font-size: 28px;
    font-weight: 700;
}

h3 {
    color: #065f46;
}

p, label, span {
    color: #1f2937;
    font-size: 16px;
}

/* Card */
.card {
    background: #f9fafb;
    padding: 1.5rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #ecfdf5;
    border: 2px dashed #10b981;
    border-radius: 12px;
    padding: 1rem;
}

/* Button */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #10b981, #047857);
    color: white;
    border-radius: 10px;
    padding: 0.7rem;
    font-size: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER (VISIBLE!)
# --------------------------------------------------
st.markdown("""
<div class="card">
<h1>🥗 AI-NutritionalCare</h1>
<p>AI-driven Personalized Diet Recommendation System</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------
def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

    elif ext == "csv":
        df = pd.read_csv(file)
        text = " ".join(df.astype(str).values.flatten())

    elif ext == "txt":
        text = file.read().decode("utf-8")

    return text.strip()


def extract_patient_name(text):
    match = re.search(r"patient\s*[:\-]\s*([A-Za-z ]+)", text, re.I)
    return match.group(1).strip() if match else "Unknown Patient"


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
# DIET DATA
# --------------------------------------------------
VEG_DAYS = [{"breakfast": "Oats Porridge", "lunch": "Veg Pulao", "dinner": "Chapati & Mixed Veg"}] * 28
NONVEG_DAYS = [{"breakfast": "Boiled Eggs", "lunch": "Chicken Rice", "dinner": "Fish Curry"}] * 28

def generate_plan(pref):
    return VEG_DAYS if pref == "Vegetarian" else NONVEG_DAYS

# --------------------------------------------------
# INPUT (STACKED, NOT HORIZONTAL)
# --------------------------------------------------
st.markdown("## 📥 Upload Patient Data")

uploaded = st.file_uploader(
    "Upload Medical Report (PDF / CSV / TXT)",
    type=["pdf", "csv", "txt"]
)

st.markdown("## 🥦 Food Preference")
preference = st.radio("", ["Vegetarian", "Non-Vegetarian"])

run = st.button("✨ Generate Diet Recommendation")

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
if run:
    if not uploaded:
        st.warning("Please upload a medical report.")
        st.stop()

    raw = extract_text(uploaded)
    patient = extract_patient_name(raw)
    conditions = extract_conditions(raw)
    plan = generate_plan(preference)

    st.markdown("## 📄 Output")

    st.markdown(f"""
    <div class="card">
    <b>Patient:</b> {patient}<br>
    <b>Medical Condition:</b> {", ".join(conditions)}<br>
    <b>Listing 1:</b> Sample Diet Plan from AI-NutritionalCare
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📅 1-Month Diet Plan")

    for i, day in enumerate(plan, 1):
        with st.expander(f"🍽️ Day {i}"):
            st.write(f"**Breakfast:** {day['breakfast']}")
            st.write(f"**Lunch:** {day['lunch']}")
            st.write(f"**Dinner:** {day['dinner']}")

    # --------------------------------------------------
    # DOWNLOADS
    # --------------------------------------------------
    st.markdown("## ⬇️ Download")

    st.download_button(
        "📄 Download JSON",
        data=pd.Series({
            "patient": patient,
            "conditions": conditions,
            "diet_plan": plan
        }).to_json(),
        file_name="diet_plan.json",
        mime="application/json"
    )
