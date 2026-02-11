import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []

# ---------------- STYLES ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp { background: #e8eaf0 !important; }

.main .block-container {
    max-width: 1100px;
    padding: 2rem 1.5rem;
}

#MainMenu, footer, header { display: none; }

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    font-weight: 600;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_patient_name(text):
    patterns = [
        r"patient\s*name\s*[:-]\s*([A-Za-z ]+)",
        r"name\s*[:-]\s*([A-Za-z ]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()
    return "Patient Name Not Found"

def extract_conditions(text):
    t = text.lower()
    cond = []
    if "diabetes" in t:
        cond.append("Diabetes")
    if "cholesterol" in t:
        cond.append("High Cholesterol")
    if "hypertension" in t:
        cond.append("Hypertension")
    return cond or ["General Health"]

DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis, Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "Brown Rice, Dal Tadka, Cucumber Raita",
    "Dinner": "2 Rotis, Palak Paneer, Salad",
    "Snacks": "Roasted Chickpeas, 1 Apple",
    "Notes": "Drink 8–10 glasses of water. Avoid sugary drinks."
}

def generate_pdf(patient, conditions, diet):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI-NutritionalCare Diet Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Patient: {patient}")
    y -= 20
    c.drawString(40, y, f"Conditions: {', '.join(conditions)}")
    y -= 30

    for k, v in diet.items():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, k)
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(50, y, v)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- HEADER ----------------
st.markdown("""
<div style="background: linear-gradient(135deg,#667eea,#764ba2);
padding:2rem;border-radius:12px;margin-bottom:1.5rem;">
<h1 style="color:white;margin:0;">🥗 AI-NutritionalCare</h1>
<p style="color:white;">AI-Powered Personalized Diet Planner</p>
</div>
""", unsafe_allow_html=True)

# ---------------- UPLOAD ----------------
uploaded = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])

# ---------------- GENERATE ----------------
if st.button("✨ Generate Personalized Diet Plan"):
    if uploaded:
        text = extract_text(uploaded)
        st.session_state.patient = extract_patient_name(text)
        st.session_state.conditions = extract_conditions(text)
        st.session_state.generated = True
        st.success("Diet plan generated!")
    else:
        st.warning("Please upload a report first.")

# ---------------- RESULT ----------------
if st.session_state.generated:

    st.subheader("📋 Patient Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Patient", st.session_state.patient)
    c2.metric("Condition", ", ".join(st.session_state.conditions))
    c3.metric("Duration", "1 Month")

    week = st.selectbox("Week", ["Week 1","Week 2","Week 3","Week 4"])
    day = st.selectbox("Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"])

    st.subheader(f"🍽️ {day} Diet Plan")
    for k in ["Breakfast","Lunch","Dinner","Snacks"]:
        st.info(f"**{k}**\n\n{DAY_PLAN[k]}")

    st.success(DAY_PLAN["Notes"])

    col1, col2 = st.columns(2)
    col1.download_button(
        "📄 Download JSON",
        data=pd.Series({
            "patient": st.session_state.patient,
            "conditions": st.session_state.conditions,
            "diet": DAY_PLAN
        }).to_json(),
        file_name="diet_plan.json",
        mime="application/json"
    )

    col2.download_button(
        "📑 Download PDF",
        data=generate_pdf(
            st.session_state.patient,
            st.session_state.conditions,
            DAY_PLAN
        ),
        file_name="diet_plan.pdf",
        mime="application/pdf"
    )
