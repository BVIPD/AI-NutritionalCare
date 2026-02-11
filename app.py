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
# MODERN UI WITH ANIMATIONS
# ================================
st.markdown("""
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1200px;
    padding: 2rem 1rem;
}

/* Remove default streamlit styling */
.stMarkdown, .stText {
    color: white;
}

/* Hide white boxes */
.element-container:has(> .stMarkdown > div > div[data-testid="stMarkdownContainer"]:empty) {
    display: none;
}

section[data-testid="stSidebar"] + div.block-container::before,
section[data-testid="stSidebar"] + div.block-container::after {
    display: none;
}

/* Remove extra padding and margins */
.element-container {
    margin-bottom: 0 !important;
}

div[data-testid="stVerticalBlock"] > div:has(> div > div > div > div[style*="display: none"]) {
    display: none;
}

/* Remove streamlit branding elements */
footer {
    display: none;
}

#MainMenu {
    display: none;
}

header {
    visibility: hidden;
}

/* Improve overall spacing */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Main header container */
.main-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 2rem 3rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    animation: fadeInDown 0.6s ease-out;
}

.main-title {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    text-align: center;
}

.subtitle {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.9);
    text-align: center;
    font-weight: 300;
    letter-spacing: 0.5px;
}

/* Upload section */
.upload-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    animation: fadeInUp 0.6s ease-out 0.2s both;
}

.upload-container label {
    color: #2d3748 !important;
    font-weight: 600 !important;
    font-size: 1.2rem !important;
    margin-bottom: 1rem !important;
}

/* File uploader styling */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 16px;
    padding: 2rem;
    border: 3px dashed rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"] label {
    color: white !important;
}

[data-testid="stFileUploader"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(240, 147, 251, 0.3);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
    padding: 0.75rem 3rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 20px rgba(245, 87, 108, 0.4);
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(245, 87, 108, 0.5);
}

/* Download buttons */
.stDownloadButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.7rem 2rem;
    border-radius: 12px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
    margin: 0.5rem 0;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* Summary card */
.summary-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    animation: fadeInUp 0.6s ease-out 0.4s both;
}

.summary-title {
    font-size: 2rem;
    font-weight: 700;
    color: #764ba2;
    margin-bottom: 1.5rem;
    border-bottom: 3px solid #f093fb;
    padding-bottom: 0.5rem;
}

.info-row {
    display: flex;
    align-items: center;
    margin: 1rem 0;
    padding: 1rem;
    background: linear-gradient(135deg, #f8f9ff 0%, #fff5f7 100%);
    border-radius: 12px;
    transition: all 0.3s ease;
}

.info-row:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-label {
    font-weight: 600;
    color: #764ba2;
    font-size: 1.1rem;
}

.info-value {
    color: #4a5568;
    font-size: 1.1rem;
}

/* Select boxes */
.stSelectbox {
    margin: 1rem 0;
}

.stSelectbox label {
    color: white !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
}

.stSelectbox > div > div {
    background: white;
    border-radius: 12px;
    border: 2px solid #e0e7ff;
    transition: all 0.3s ease;
    font-size: 1rem;
    padding: 0.5rem;
}

.stSelectbox > div > div:hover {
    border-color: #764ba2;
    box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
}

.stSelectbox [data-baseweb="select"] {
    background-color: white;
}

.stSelectbox [data-baseweb="select"] > div {
    background-color: white;
    color: #2d3748;
    font-weight: 500;
}

/* Download section */
.download-section {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    animation: fadeInUp 0.6s ease-out 0.6s both;
}

/* Selection section styling */
.selection-section {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 2rem 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-label {
    color: white;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: block;
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

/* Warning/Info boxes */
.stWarning {
    background: rgba(255, 193, 7, 0.1);
    border-left: 4px solid #ffc107;
    border-radius: 8px;
    padding: 1rem;
}

/* Divider */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    margin: 2rem 0;
}

/* Custom subheader */
.custom-subheader {
    font-size: 1.8rem;
    font-weight: 600;
    color: #764ba2;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f093fb;
}

/* Responsive */
@media (max-width: 768px) {
    .main-title {
        font-size: 2.5rem;
    }
    
    .subtitle {
        font-size: 1rem;
    }
    
    .upload-container, .summary-card, .download-section {
        padding: 1.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ================================
# HEADER
# ================================
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🥗 AI-NutritionalCare</h1>
    <p class="subtitle">Your Personalized AI-Powered Diet Companion</p>
</div>
""", unsafe_allow_html=True)
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
# INPUT SECTION
# ================================
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
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
    
    # Patient Summary Card
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="summary-title">📋 Patient Summary</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-row">
        <span class="info-label">👤 Patient Name:</span>&nbsp;&nbsp;
        <span class="info-value">{st.session_state.patient}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-row">
        <span class="info-label">🏥 Medical Condition:</span>&nbsp;&nbsp;
        <span class="info-value">{', '.join(st.session_state.conditions)}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-row">
        <span class="info-label">📅 Plan Duration:</span>&nbsp;&nbsp;
        <span class="info-value">1 Month (28 Days)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Week and Day Selection
    st.markdown('<div class="selection-section">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">📅 Select Your Plan Timeline</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color: white; font-weight: 600; margin-bottom: 0.5rem;">📆 Week</p>', unsafe_allow_html=True)
        week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"], label_visibility="collapsed")
    with col2:
        st.markdown('<p style="color: white; font-weight: 600; margin-bottom: 0.5rem;">🗓️ Day</p>', unsafe_allow_html=True)
        day = st.selectbox("Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"], label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ================================
    # ENHANCED DIET PLAN DISPLAY
    # ================================
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                padding: 20px;
                background: transparent;
            }}
            
            .container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
                animation: slideIn 0.6s ease-out;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            h2 {{
                color: white;
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 30px;
                text-align: center;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .card {{
                background: rgba(255, 255, 255, 0.95);
                padding: 24px;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
            }}
            
            .card:hover::before {{
                transform: scaleX(1);
            }}
            
            .card-icon {{
                font-size: 2.5rem;
                margin-bottom: 12px;
                display: block;
            }}
            
            .card-title {{
                font-size: 1.3rem;
                font-weight: 700;
                color: #764ba2;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .card-content {{
                color: #4a5568;
                font-size: 1rem;
                line-height: 1.6;
                font-weight: 400;
            }}
            
            .notes-card {{
                grid-column: 1 / -1;
                background: linear-gradient(135deg, #fff5f7 0%, #f8f9ff 100%);
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 24px;
                }}
                
                h2 {{
                    font-size: 2rem;
                }}
                
                .grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🍽️ {day} Diet Plan</h2>
            
            <div class="grid">
                <div class="card">
                    <span class="card-icon">🍳</span>
                    <div class="card-title">Breakfast</div>
                    <div class="card-content">{DAY_PLAN["Breakfast"]}</div>
                </div>
                
                <div class="card">
                    <span class="card-icon">🍛</span>
                    <div class="card-title">Lunch</div>
                    <div class="card-content">{DAY_PLAN["Lunch"]}</div>
                </div>
                
                <div class="card">
                    <span class="card-icon">🌙</span>
                    <div class="card-title">Dinner</div>
                    <div class="card-content">{DAY_PLAN["Dinner"]}</div>
                </div>
                
                <div class="card">
                    <span class="card-icon">🍎</span>
                    <div class="card-title">Snacks</div>
                    <div class="card-content">{DAY_PLAN["Snacks"]}</div>
                </div>
                
                <div class="card notes-card">
                    <span class="card-icon">💡</span>
                    <div class="card-title">Important Notes</div>
                    <div class="card-content">{DAY_PLAN["Notes"]}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, height=550)

    # ================================
    # DOWNLOAD SECTION
    # ================================
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="custom-subheader">📥 Download Your Diet Plan</h2>', unsafe_allow_html=True)
    
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

# ================================
# FOOTER
# ================================
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 2rem; 
            background: rgba(255, 255, 255, 0.1); border-radius: 16px;
            backdrop-filter: blur(10px);">
    <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9rem;">
        Made with ❤️ by AI-NutritionalCare Team | Powered by Advanced AI
    </p>
</div>
""", unsafe_allow_html=True)
