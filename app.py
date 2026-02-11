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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# GLOBAL CSS (WHITE MEDICAL UI)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #0f766e;
}

.card {
    background: #f9fafb;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
}

.stButton > button {
    background: linear-gradient(135deg, #10b981, #0f766e);
    color: white;
    border-radius: 12px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    border: none;
}

[data-testid="stFileUploader"] {
    border: 2px dashed #10b981;
    border-radius: 14px;
    padding: 1rem;
    background: #f0fdf4;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="card">
    <h1>🥗 AI-NutritionalCare</h1>
    <p style="font-size:18px;color:#374151;">
        AI-driven Personalized Diet Recommendation System
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# UTILITIES
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
    patterns = [
        r"patient\s*name\s*[:\-]\s*([A-Za-z ]+)",
        r"patient\s*[:\-]\s*([A-Za-z ]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Unknown Patient"


def extract_conditions(text):
    t = text.lower()
    conditions = []
    if "diabetes" in t:
        conditions.append("Diabetes")
    if "cholesterol" in t:
        conditions.append("High Cholesterol")
    if "hypertension" in t or "blood pressure" in t:
        conditions.append("Hypertension")
    return conditions if conditions else ["General Health"]

# --------------------------------------------------
# DIET DATA
# --------------------------------------------------
VEG_DAYS = [
    {"breakfast": "Oats Porridge", "lunch": "Veg Pulao", "dinner": "Chapati & Mixed Veg"},
    {"breakfast": "Idli & Sambar", "lunch": "Rajma Rice", "dinner": "Curd Rice"},
    {"breakfast": "Vegetable Poha", "lunch": "Veg Khichdi", "dinner": "Tomato Soup"},
    {"breakfast": "Masala Oats", "lunch": "Dal & Chapati", "dinner": "Paneer Bhurji"},
    {"breakfast": "Ragi Porridge", "lunch": "Veg Fried Rice", "dinner": "Cabbage Fry"},
    {"breakfast": "Sprouts Salad", "lunch": "Veg Biryani", "dinner": "Curd Bowl"},
    {"breakfast": "Fruit Bowl", "lunch": "Stuffed Paratha", "dinner": "Veg Soup"}
] * 4  # 28 days

NONVEG_DAYS = [
    {"breakfast": "Boiled Eggs & Toast", "lunch": "Grilled Chicken & Rice", "dinner": "Fish Curry"},
    {"breakfast": "Egg Omelette", "lunch": "Chicken Pulao", "dinner": "Chicken Soup"},
    {"breakfast": "Egg Toast", "lunch": "Fish Rice Bowl", "dinner": "Chicken Stir Fry"},
    {"breakfast": "Scrambled Eggs", "lunch": "Chicken Curry", "dinner": "Egg Salad"},
    {"breakfast": "Boiled Eggs", "lunch": "Grilled Fish", "dinner": "Chicken Wrap"},
    {"breakfast": "Egg Bhurji", "lunch": "Chicken Biryani", "dinner": "Fish Soup"},
    {"breakfast": "Protein Toast", "lunch": "Chicken Fried Rice", "dinner": "Egg Curry"}
] * 4

def generate_month_plan(pref):
    return VEG_DAYS if pref == "Vegetarian" else NONVEG_DAYS

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
# INPUT SECTION
# --------------------------------------------------
st.markdown("## 📥 Upload Patient Data")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload Medical Report (PDF / CSV / TXT)",
        type=["pdf", "csv", "txt"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    preference = st.radio("Food Preference", ["Vegetarian", "Non-Vegetarian"])
    run = st.button("✨ Generate Diet Recommendation")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
if run:
    if not uploaded:
        st.warning("Please upload a medical report.")
        st.stop()

    raw_text = extract_text(uploaded)
    patient = extract_patient_name(raw_text)
    conditions = extract_conditions(raw_text)
    month_plan = generate_month_plan(preference)

    # ---- PATIENT INFO (YOU ASKED THIS TO BE IN OUTPUT) ----
    st.markdown("## 📄 Output")

    st.markdown(f"""
    <div class="card">
    <b>Patient:</b> {patient}<br>
    <b>Medical Condition:</b> {', '.join(conditions)}<br>
    <b>Listing 1:</b> Sample Diet Plan from AI-NutritionalCare
    </div>
    """, unsafe_allow_html=True)

    # ---- DIET PLAN ----
    st.markdown("## 📅 1-Month Diet Plan (Breakfast • Lunch • Dinner)")

    tabs = st.tabs(["Week 1", "Week 2", "Week 3", "Week 4"])

    day_idx = 0
    for tab in tabs:
        with tab:
            for _ in range(7):
                day = month_plan[day_idx]
                with st.expander(f"🍽️ Day {day_idx + 1}"):
                    st.write(f"**Breakfast:** {day['breakfast']}")
                    st.write(f"**Lunch:** {day['lunch']}")
                    st.write(f"**Dinner:** {day['dinner']}")
                day_idx += 1

    # ---- DOWNLOADS ----
    st.markdown("## ⬇️ Download")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📄 Download JSON",
            data=pd.Series({
                "patient": patient,
                "conditions": conditions,
                "diet_plan": month_plan
            }).to_json(),
            file_name="diet_plan.json",
            mime="application/json"
        )

    with col2:
        pdf_file = generate_pdf(patient, conditions, month_plan)
        st.download_button(
            "📑 Download PDF",
            data=pdf_file,
            file_name=f"{patient.replace(' ', '_')}_DietPlan.pdf",
            mime="application/pdf"
        )
