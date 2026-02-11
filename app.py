import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="AI-NutritionalCare", page_icon="🥗", layout="wide")

if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {font-family: 'Inter', sans-serif !important;}
.stApp {background: #f5f5f5 !important;}
.main .block-container {max-width: 1200px !important; padding: 2rem 1rem !important;}
#MainMenu, footer, header {display: none !important;}

/* White box containers */
.white-box {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
}

.stButton > button {
    background: #2563eb !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.stDownloadButton > button {
    background: #059669 !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
}

/* SELECT BOXES - WHITE TEXT ON BLACK BACKGROUND */
.stSelectbox label {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: white !important;
}

.stSelectbox svg {
    fill: white !important;
}

/* Metrics - black text */
[data-testid="stMetricValue"] {
    color: #000000 !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricLabel"] {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Info boxes - black text */
.stAlert {
    color: #000000 !important;
}

.stAlert * {
    color: #000000 !important;
}

/* Headings - black text */
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

p, span, div {
    color: #000000 !important;
}

/* Success box - black text */
.stSuccess {
    background-color: #d1fae5 !important;
    color: #000000 !important;
}

.stSuccess * {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_patient_name(text):
    patterns = [r"patient\s*name\s*[:\-]\s*([A-Za-z ]+)", r"name\s*[:\-]\s*([A-Za-z ]+)"]
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

DAY_PLAN = {
    "Breakfast": "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Lunch": "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "Dinner": "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Snacks": "Roasted Chickpeas (30g), 1 Apple",
    "Notes": "Drink at least 8–10 glasses of water. Avoid sugary drinks."
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

# HEADER
st.markdown('<div class="white-box">', unsafe_allow_html=True)
st.title("🥗 AI-NutritionalCare")
st.caption("Your Personalized AI-Powered Diet Companion")
st.markdown('</div>', unsafe_allow_html=True)

# UPLOAD
st.markdown('<div class="white-box">', unsafe_allow_html=True)
uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type=["pdf"])

if st.button("✨ Generate Diet Recommendation"):
    if uploaded:
        with st.spinner("Analyzing..."):
            text = extract_text(uploaded)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.session_state.generated = True
        st.success("✅ Diet plan generated successfully!")
    else:
        st.warning("⚠️ Please upload a medical report")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.generated:
    
    # PATIENT SUMMARY
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader("📋 Patient Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👤 Patient Name", st.session_state.patient)
    
    with col2:
        st.metric("🏥 Medical Condition", ', '.join(st.session_state.conditions))
    
    with col3:
        st.metric("📅 Plan Duration", "1 Month")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # TIMELINE SELECTION - BLACK BACKGROUND BOX
    st.markdown("""
    <div style="background: #1e293b; padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h3 style="color: white !important; margin: 0 0 1rem 0;">📅 Select Timeline</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    with col2:
        day = st.selectbox("Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"])
    
    # DIET PLAN
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader(f"🍽️ {day} Diet Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🍳 Breakfast")
        st.info(DAY_PLAN["Breakfast"])
        
        st.markdown("### 🍛 Lunch")
        st.info(DAY_PLAN["Lunch"])
    
    with col2:
        st.markdown("### 🌙 Dinner")
        st.info(DAY_PLAN["Dinner"])
        
        st.markdown("### 🍎 Snacks")
        st.info(DAY_PLAN["Snacks"])
    
    st.success(f"💡 **Important Notes:** {DAY_PLAN['Notes']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DOWNLOAD
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader("📥 Download Your Diet Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📄 Download JSON",
            data=pd.Series({"patient": st.session_state.patient, "conditions": st.session_state.conditions, "diet_plan": DAY_PLAN}).to_json(),
            file_name="diet_plan.json",
            mime="application/json"
        )
    
    with col2:
        st.download_button(
            "📑 Download PDF",
            data=generate_pdf(st.session_state.patient, st.session_state.conditions, DAY_PLAN),
            file_name="diet_plan.pdf",
            mime="application/pdf"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="white-box" style="text-align: center;">', unsafe_allow_html=True)
st.caption("Made with ❤️ by AI-NutritionalCare Team | Powered by Advanced AI")
st.markdown('</div>', unsafe_allow_html=True)
