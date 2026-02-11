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
    layout="centered"
)

# --------------------------------------------------
# CSS (CLEAN WHITE UI)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #111827;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
}

h1 { color: #065f46; font-size: 36px; }
h2 { color: #047857; font-size: 26px; }

.card {
    background: #f9fafb;
    padding: 1.3rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
}

[data-testid="stFileUploader"] {
    background: #ecfdf5;
    border: 2px dashed #10b981;
    border-radius: 12px;
    padding: 1rem;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #10b981, #047857);
    color: white;
    border-radius: 10px;
    padding: 0.7rem;
    font-size: 16px;
    font-weight: 600;
}

/* Fix expander dark bars */
details summary {
    background: #ffffff !important;
    color: #111827 !important;
    font-weight: 600;
}
details {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="card">
<h1>🥗 AI-NutritionalCare</h1>
<p>AI-driven Personalized Diet Recommendation System</p>
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
# DIET PLAN (28 DAYS)
# --------------------------------------------------
PLAN = [
    {"breakfast": "Oats Porridge", "lunch": "Veg Pulao", "dinner": "Chapati & Mixed Veg"}
] * 28

# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------
def generate_pdf(patient, conditions, plan):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "AI-NutritionalCare Diet Report")
    y -= 40

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Patient: {patient}")
    y -= 20
    c.drawString(40, y, f"Medical Condition: {', '.join(conditions)}")
    y -= 30

    for i, day in enumerate(plan, 1):
        if y < 120:
            c.showPage()
            y = 800

        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"Day {i}")
        y -= 15

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Breakfast: {day['breakfast']}")
        y -= 12
        c.drawString(50, y, f"Lunch: {day['lunch']}")
        y -= 12
        c.drawString(50, y, f"Dinner: {day['dinner']}")
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# INPUT
# --------------------------------------------------
st.markdown("## 📥 Upload Patient Data")

uploaded = st.file_uploader(
    "Upload Medical Report (PDF / CSV / TXT)",
    type=["pdf", "csv", "txt"]
)

st.markdown("## 🥦 Food Preference")
st.radio("", ["Vegetarian", "Non-Vegetarian"])

run = st.button("✨ Generate Diet Recommendation")

# --------------------------------------------------
# OUTPUT (SHORT + CLEAN)
# --------------------------------------------------
if run:
    if not uploaded:
        st.warning("Please upload a medical report.")
        st.stop()

    text = extract_text(uploaded)
    patient = extract_patient_name(text)
    conditions = extract_conditions(text)

    # Patient Summary
    st.markdown("## 📄 Patient Summary")
    st.markdown(f"""
    <div class="card">
    <b>Patient:</b> {patient}<br>
    <b>Medical Condition:</b> {", ".join(conditions)}<br>
    <b>Plan Duration:</b> 1 Month
    </div>
    """, unsafe_allow_html=True)

    # Downloads (TOP)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📄 Download JSON",
            data=pd.Series({
                "patient": patient,
                "conditions": conditions,
                "diet_plan": PLAN
            }).to_json(),
            file_name="diet_plan.json",
            mime="application/json"
        )

    with col2:
        st.download_button(
            "📑 Download PDF",
            data=generate_pdf(patient, conditions, PLAN),
            file_name=f"{patient.replace(' ', '_')}_DietPlan.pdf",
            mime="application/pdf"
        )

    # Diet Plan (Week Tabs)
    st.markdown("## 🗓️ 1-Month Diet Plan")

    tabs = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])
    idx = 0

    for tab in tabs:
        with tab:
            for _ in range(7):
                day = PLAN[idx]
                with st.expander(f"🍽️ Day {idx + 1}"):
                    st.write(f"**Breakfast:** {day['breakfast']}")
                    st.write(f"**Lunch:** {day['lunch']}")
                    st.write(f"**Dinner:** {day['dinner']}")
                idx += 1
