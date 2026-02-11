import streamlit as st
import streamlit.components.v1 as components
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="wide"
)

# ================================
# SESSION STATE
# ================================
if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []

# ================================
# BASIC WHITE UI
# ================================
st.markdown("""
<style>
.stApp { background-color:#f8fafc; }
.block-container { max-width:1100px; }
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER
# ================================
st.title("🥗 AI-NutritionalCare")
st.caption("AI-driven Personalized Diet Recommendation System")
st.divider()

# ================================
# HELPERS
# ================================
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
        r"name\s*[:\-]\s*([A-Za-z ]+)"
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

# ================================
# DIET DATA
# ================================
DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "Dinner": "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Snacks": "Roasted Chickpeas (30g), 1 Apple",
    "Notes": "Drink at least 8–10 glasses of water. Avoid sugary drinks."
}

# ================================
# PDF GENERATOR
# ================================
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

# ================================
# INPUT
# ================================
uploaded = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])

if st.button("Generate Diet Recommendation"):
    if uploaded:
        text = extract_text(uploaded)
        st.session_state.patient = extract_patient_name(text)
        st.session_state.conditions = extract_conditions(text)
        st.session_state.generated = True
    else:
        st.warning("Please upload a medical report")

# ================================
# OUTPUT
# ================================
if st.session_state.generated:

    st.subheader("Patient Summary")
    st.write(f"**Patient:** {st.session_state.patient}")
    st.write(f"**Medical Condition:** {', '.join(st.session_state.conditions)}")
    st.write("**Plan Duration:** 1 Month")

    week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    day = st.selectbox("Select Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"])

    # ================================
    # PURE HTML RENDER (NO MARKDOWN)
    # ================================
    components.html(f"""
    <div style="background:#ffffff;padding:24px;border-radius:16px;
                box-shadow:0 8px 25px rgba(0,0,0,0.08);
                font-family:Segoe UI;">
      <h2>{day} Diet Plan</h2>

      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px;">

        <div style="background:#f1f5f9;padding:16px;border-radius:12px;">
          <b>🍳 Breakfast</b><br>{DAY_PLAN["Breakfast"]}
        </div>

        <div style="background:#f1f5f9;padding:16px;border-radius:12px;">
          <b>🍛 Lunch</b><br>{DAY_PLAN["Lunch"]}
        </div>

        <div style="background:#f1f5f9;padding:16px;border-radius:12px;">
          <b>🌙 Dinner</b><br>{DAY_PLAN["Dinner"]}
        </div>

        <div style="background:#f1f5f9;padding:16px;border-radius:12px;">
          <b>🍎 Snacks</b><br>{DAY_PLAN["Snacks"]}
        </div>

        <div style="background:#f1f5f9;padding:16px;border-radius:12px;">
          <b>📝 Notes</b><br>{DAY_PLAN["Notes"]}
        </div>

      </div>
    </div>
    """, height=420)

    # ================================
    # DOWNLOADS
    # ================================
    st.subheader("Download")

    st.download_button(
        "Download JSON",
        data=pd.Series({
            "patient": st.session_state.patient,
            "conditions": st.session_state.conditions,
            "diet_plan": DAY_PLAN
        }).to_json(),
        file_name="diet_plan.json",
        mime="application/json"
    )

    pdf_file = generate_pdf(
        st.session_state.patient,
        st.session_state.conditions,
        DAY_PLAN
    )

    st.download_button(
        "Download PDF",
        data=pdf_file,
        file_name="diet_plan.pdf",
        mime="application/pdf"
    )
