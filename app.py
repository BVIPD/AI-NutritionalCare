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
# COMPLETE CSS - FORCES BLACK TEXT AND REMOVES BOXES
# ================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* FORCE EVERYTHING TO USE INTER FONT AND BLACK TEXT */
* {
    font-family: 'Inter', sans-serif !important;
    color: #000000 !important;
}

/* Background */
.stApp {
    background: #f0f2f6 !important;
}

.main .block-container {
    max-width: 1400px !important;
    padding: 1rem !important;
}

/* REMOVE ALL STREAMLIT DEFAULT CONTAINERS AND BOXES */
.element-container {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stVerticalBlock"] > div {
    background: transparent !important;
    gap: 0 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 1rem !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden !important;
    display: none !important;
}

/* FORCE ALL TEXT TO BE BLACK */
p, span, div, h1, h2, h3, h4, h5, h6, label {
    color: #000000 !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 2rem !important;
}

[data-testid="stFileUploader"] section {
    background: white !important;
}

[data-testid="stFileUploader"] label {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Buttons - Blue primary, Green download */
.stButton > button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    font-size: 1rem !important;
}

.stButton > button:hover {
    background: #2563eb !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.4) !important;
}

.stDownloadButton > button {
    background: #10b981 !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.stDownloadButton > button:hover {
    background: #059669 !important;
}

/* Select boxes */
.stSelectbox label {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: white !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: white !important;
    color: #000000 !important;
}

/* Success and Warning messages */
.stSuccess {
    background-color: #d1fae5 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    border-left: 4px solid #10b981 !important;
}

.stWarning {
    background-color: #fef3c7 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    border-left: 4px solid #f59e0b !important;
}

.stSuccess *, .stWarning * {
    color: #000000 !important;
}

/* Column containers */
[data-testid="column"] {
    background: transparent !important;
    padding: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

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

# ================================
# HEADER
# ================================
st.markdown("""
<div style="background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem; text-align: center;">
    <h1 style="font-size: 2.5rem; font-weight: 700; color: #000000; margin: 0;">🥗 AI-NutritionalCare</h1>
    <p style="font-size: 1.1rem; color: #000000; margin-top: 0.5rem;">Your Personalized AI-Powered Diet Companion</p>
</div>
""", unsafe_allow_html=True)

# ================================
# UPLOAD SECTION
# ================================
st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">', unsafe_allow_html=True)

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

# ================================
# RESULTS
# ================================
if st.session_state.generated:
    
    # Patient Summary
    st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.75rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.75rem;">📋 Patient Summary</h2>
        
        <div style="background: #f9fafb; padding: 1.25rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #000000; text-transform: uppercase; margin-bottom: 0.5rem;">👤 PATIENT NAME</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: #000000;">{st.session_state.patient}</div>
        </div>
        
        <div style="background: #f9fafb; padding: 1.25rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #000000; text-transform: uppercase; margin-bottom: 0.5rem;">🏥 MEDICAL CONDITION</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: #000000;">{', '.join(st.session_state.conditions)}</div>
        </div>
        
        <div style="background: #f9fafb; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <div style="font-size: 0.875rem; font-weight: 600; color: #000000; text-transform: uppercase; margin-bottom: 0.5rem;">📅 PLAN DURATION</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: #000000;">1 Month (28 Days)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Selection
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.75rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem;">📅 Select Timeline</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    with col2:
        day = st.selectbox("Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"])
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Diet Plan
    st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.75rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.75rem;">🍽️ {day} Diet Plan</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">
            
            <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🍳</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-bottom: 0.75rem;">Breakfast</div>
                <div style="font-size: 1rem; color: #000000; line-height: 1.6;">{DAY_PLAN["Breakfast"]}</div>
            </div>
            
            <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🍛</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-bottom: 0.75rem;">Lunch</div>
                <div style="font-size: 1rem; color: #000000; line-height: 1.6;">{DAY_PLAN["Lunch"]}</div>
            </div>
            
            <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🌙</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-bottom: 0.75rem;">Dinner</div>
                <div style="font-size: 1rem; color: #000000; line-height: 1.6;">{DAY_PLAN["Dinner"]}</div>
            </div>
            
            <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🍎</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-bottom: 0.75rem;">Snacks</div>
                <div style="font-size: 1rem; color: #000000; line-height: 1.6;">{DAY_PLAN["Snacks"]}</div>
            </div>
            
            <div style="background: #dbeafe; padding: 1.5rem; border-radius: 8px; border: 1px solid #93c5fd; grid-column: 1 / -1;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">💡</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-bottom: 0.75rem;">Important Notes</div>
                <div style="font-size: 1rem; color: #000000; line-height: 1.6;">{DAY_PLAN["Notes"]}</div>
            </div>
            
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Downloads
    st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size: 1.75rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem;">📥 Download</h2>', unsafe_allow_html=True)
    
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

st.markdown("""
<div style="text-align: center; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-top: 2rem;">
    <p style="color: #000000; margin: 0;">Made with ❤️ by AI-NutritionalCare Team</p>
</div>
""", unsafe_allow_html=True)
