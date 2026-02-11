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
# SESSION STATE (CRITICAL)
# ==================================================
if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []
if "diet_plan" not in st.session_state:
    st.session_state.diet_plan = {}

# ==================================================
# DARK UI CSS
# ==================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b1220, #020617);
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}
.block-container { max-width: 1200px; padding-top: 2rem; }

.card {
    background: linear-gradient(135deg, #020617, #0f172a);
    border-radius: 20px;
    padding: 1.8rem;
    border: 1px solid #1e293b;
    box-shadow: 0 30px 80px rgba(0,0,0,0.7);
    margin-bottom: 2rem;
}

h1, h2, h3 { color: #f9fafb; }

.diet-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.diet-card {
    background: #020617;
    border-radius: 16px;
    padding: 1.4rem;
    border: 1px solid #1e293b;
}

.diet-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 0.6rem;
}

.diet-text {
    color: #cbd5f5;
    font-size: 14px;
    line-height: 1.6;
}

.stButton > button {
    background: linear-gradient(135deg, #22d3ee, #3b82f6);
    color: #020617;
    font-weight: 700;
    border-radius: 14px;
    padding: 0.8rem 2.4rem;
    font-size: 16px;
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
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

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
    return "Patient Name Not Found"

def extract_conditions(text):
    t = text.lower()
    cond = []
    if "diabetes" in t: cond.append("Diabetes")
    if "cholesterol" in t: cond.append("High Cholesterol")
    if "hypertension" in t: cond.append("Hypertension")
    return cond or ["General Health"]

# ==================================================
# DIET DATA (USED FOR ALL DAYS)
# ==================================================
DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "Dinner": "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Snacks": "Roasted Chickpeas (30g), 1 Apple",
    "Notes": "Drink at least 8–10 glasses of water. Avoid sugary drinks."
}

# ==================================================
# PDF GENERATOR
# ==================================================
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
    c.drawString(40, y, f"Medical Conditions: {', '.join(conditions)}")
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

# ==================================================
# INPUT
# ==================================================
uploaded = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])

if st.button("✨ Generate Diet Recommendation"):
    if uploaded:
        text = extract_text(uploaded)
        st.session_state.patient = extract_patient_name(text)
        st.session_state.conditions = extract_conditions(text)
        st.session_state.diet_plan = DAY_PLAN
        st.session_state.generated = True
    else:
        st.warning("Please upload a PDF file")

# ==================================================
# OUTPUT
# ==================================================
if st.session_state.generated:

    st.markdown(f"""
    <div class="card">
    <h3>Patient Summary</h3>
    <b>Patient:</b> {st.session_state.patient}<br>
    <b>Medical Condition:</b> {", ".join(st.session_state.conditions)}<br>
    <b>Plan Duration:</b> 1 Month
    </div>
    """, unsafe_allow_html=True)

    week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    day = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"])

    st.markdown(f"""
    <div class="card">
    <h2>{day} Diet Plan</h2>

    <div class="diet-grid">
        {''.join([
            f'''
            <div class="diet-card">
                <div class="diet-title">{title}</div>
                <div class="diet-text">{content}</div>
            </div>
            ''' for title, content in st.session_state.diet_plan.items()
        ])}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ================= DOWNLOADS =================
    st.markdown("### ⬇️ Download")

    json_data = {
        "patient": st.session_state.patient,
        "conditions": st.session_state.conditions,
        "diet_plan": st.session_state.diet_plan
    }

    st.download_button(
        "Download JSON",
        data=pd.Series(json_data).to_json(),
        file_name="diet_plan.json",
        mime="application/json"
    )

    pdf_file = generate_pdf(
        st.session_state.patient,
        st.session_state.conditions,
        st.session_state.diet_plan
    )

    st.download_button(
        "Download PDF",
        data=pdf_file,
        file_name="diet_plan.pdf",
        mime="application/pdf"
    )
