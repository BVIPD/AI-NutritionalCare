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
# PROFESSIONAL STYLING
# ================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global */
* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f8fafc;
}

.block-container {
    max-width: 1400px;
    padding: 2rem 1rem;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Header */
.app-header {
    background: white;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
    text-align: center;
}

.app-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
}

.app-subtitle {
    font-size: 1.1rem;
    color: #64748b;
    margin-top: 0.5rem;
}

/* Cards */
.card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
}

.card-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Info boxes */
.info-box {
    background: #f8fafc;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
    margin-bottom: 1rem;
}

.info-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.info-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
}

/* Buttons */
.stButton > button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.stDownloadButton > button {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
}

.stDownloadButton > button:hover {
    background: #059669;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    border: 2px dashed #cbd5e1;
}

[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6;
}

/* Select boxes */
.stSelectbox label {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.95rem;
}

.stSelectbox > div > div {
    border-radius: 8px;
    border-color: #e2e8f0;
}

/* Success/Warning */
.stSuccess, .stWarning {
    padding: 1rem;
    border-radius: 8px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER
# ================================
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🥗 AI-NutritionalCare</h1>
    <p class="app-subtitle">Your Personalized AI-Powered Diet Companion</p>
</div>
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
# UPLOAD SECTION
# ================================
st.markdown('<div class="card">', unsafe_allow_html=True)
uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type=["pdf"])

if st.button("✨ Generate Diet Recommendation"):
    if uploaded:
        with st.spinner("🔍 Analyzing your medical report..."):
            text = extract_text(uploaded)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.session_state.generated = True
        st.success("✅ Diet plan generated successfully!")
    else:
        st.warning("⚠️ Please upload a medical report to continue")
st.markdown('</div>', unsafe_allow_html=True)

# ================================
# OUTPUT SECTION
# ================================
if st.session_state.generated:
    
    # Patient Summary
    st.markdown(f"""
    <div class="card">
        <h2 class="card-title">📋 Patient Summary</h2>
        <div class="info-box">
            <div class="info-label">👤 Patient Name</div>
            <div class="info-value">{st.session_state.patient}</div>
        </div>
        <div class="info-box">
            <div class="info-label">🏥 Medical Condition</div>
            <div class="info-value">{', '.join(st.session_state.conditions)}</div>
        </div>
        <div class="info-box">
            <div class="info-label">📅 Plan Duration</div>
            <div class="info-value">1 Month (28 Days)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Week and Day Selection
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">📅 Select Your Plan Timeline</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        week = st.selectbox("Select Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
    with col2:
        day = st.selectbox("Select Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"])
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Diet Plan Display
    st.markdown(f"""
    <div class="card">
        <h2 class="card-title">🍽️ {day} Diet Plan</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
            
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🍳</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.2rem; margin-bottom: 0.75rem;">Breakfast</div>
                <div style="color: #475569; line-height: 1.6;">{DAY_PLAN["Breakfast"]}</div>
            </div>
            
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🍛</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.2rem; margin-bottom: 0.75rem;">Lunch</div>
                <div style="color: #475569; line-height: 1.6;">{DAY_PLAN["Lunch"]}</div>
            </div>
            
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌙</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.2rem; margin-bottom: 0.75rem;">Dinner</div>
                <div style="color: #475569; line-height: 1.6;">{DAY_PLAN["Dinner"]}</div>
            </div>
            
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🍎</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.2rem; margin-bottom: 0.75rem;">Snacks</div>
                <div style="color: #475569; line-height: 1.6;">{DAY_PLAN["Snacks"]}</div>
            </div>
            
            <div style="background: #eff6ff; padding: 1.5rem; border-radius: 8px; border: 1px solid #bfdbfe; grid-column: 1 / -1;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💡</div>
                <div style="font-weight: 700; color: #1e293b; font-size: 1.2rem; margin-bottom: 0.75rem;">Important Notes</div>
                <div style="color: #475569; line-height: 1.6;">{DAY_PLAN["Notes"]}</div>
            </div>
            
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Download Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="card-title">📥 Download Your Diet Plan</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📄 Download as JSON",
            data=pd.Series({
                "patient": st.session_state.patient,
                "conditions": st.session_state.conditions,
                "diet_plan": DAY_PLAN
            }).to_json(),
            file_name="diet_plan.json",
            mime="application/json"
        )
    
    with col2:
        pdf_file = generate_pdf(
            st.session_state.patient,
            st.session_state.conditions,
            DAY_PLAN
        )
        
        st.download_button(
            "📑 Download as PDF",
            data=pdf_file,
            file_name="diet_plan.pdf",
            mime="application/pdf"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <p style="color: #64748b; margin: 0; font-size: 0.95rem;">Made with ❤️ by AI-NutritionalCare Team | Powered by Advanced AI</p>
</div>
""", unsafe_allow_html=True)
