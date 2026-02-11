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
# MODERN UI WITH PROFESSIONAL STYLING
# ================================
st.markdown("""
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.stApp {
    background: #f5f7fa;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1200px;
    padding: 2rem 1rem;
}

/* Remove all default streamlit empty containers */
.element-container:has(> .stMarkdown > div > div[data-testid="stMarkdownContainer"]:empty) {
    display: none !important;
}

div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div[style*=""] {
    gap: 0 !important;
}

/* Remove streamlit branding */
footer {display: none !important;}
#MainMenu {display: none !important;}
header {visibility: hidden !important;}
.viewerBadge_container__1QSob {display: none !important;}

/* Remove extra spacing */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}

.element-container {
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Main header container */
.main-header {
    background: white;
    border-radius: 16px;
    padding: 3rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
}

.main-title {
    font-size: 3rem;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 0.5rem;
    text-align: center;
}

.subtitle {
    font-size: 1.1rem;
    color: #64748b;
    text-align: center;
    font-weight: 400;
}

/* Upload section */
.upload-container {
    background: white;
    border-radius: 16px;
    padding: 2.5rem;
    margin: 0 0 2rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
}

.upload-container label {
    color: #1a202c !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    margin-bottom: 1rem !important;
}

/* File uploader styling */
[data-testid="stFileUploader"] {
    background: #f8fafc;
    border-radius: 12px;
    padding: 2rem;
    border: 2px dashed #cbd5e1;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"] label {
    color: #475569 !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6;
    background: #eff6ff;
}

/* Buttons */
.stButton > button {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.875rem 3rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    width: 100%;
}

.stButton > button:hover {
    background: #2563eb;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    transform: translateY(-1px);
}

/* Download buttons */
.stDownloadButton > button {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    margin: 0.5rem 0;
}

.stDownloadButton > button:hover {
    background: #059669;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Summary card */
.summary-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 0 0 2rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
}

.summary-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}

.info-row {
    display: flex;
    align-items: center;
    margin: 1rem 0;
    padding: 1.25rem;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
}

.info-row:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
}

.info-label {
    font-weight: 600;
    color: #475569;
    font-size: 1rem;
}

.info-value {
    color: #1e293b;
    font-size: 1rem;
}

/* Select boxes */
.stSelectbox {
    margin: 0;
}

.stSelectbox label {
    color: #1a202c !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    margin-bottom: 0.5rem !important;
}

.stSelectbox > div > div {
    background: white;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
    font-size: 0.95rem;
}

.stSelectbox > div > div:hover {
    border-color: #3b82f6;
}

.stSelectbox [data-baseweb="select"] {
    background-color: white;
}

.stSelectbox [data-baseweb="select"] > div {
    background-color: white;
    color: #1e293b;
    font-weight: 500;
}

/* Download section */
.download-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 0 0 2rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
}

/* Selection section styling */
.selection-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 0 0 2rem 0;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-label {
    color: #1a202c;
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    display: block;
}

.section-label {
    color: #1a202c;
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    display: block;
}

/* Animations - subtle */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Warning/Info boxes */
.stWarning, .stSuccess {
    background: white;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stSuccess {
    border-left-color: #10b981;
}

/* Divider */
hr {
    display: none;
}

/* Custom subheader */
.custom-subheader {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a202c;
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Responsive */
@media (max-width: 768px) {
    .main-title {
        font-size: 2rem;
    }
    
    .subtitle {
        font-size: 0.95rem;
    }
    
    .upload-container, .summary-card, .download-section, .selection-section {
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
        st.markdown('<p style="color: #475569; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.95rem;">📆 Week</p>', unsafe_allow_html=True)
        week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"], label_visibility="collapsed")
    with col2:
        st.markdown('<p style="color: #475569; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.95rem;">🗓️ Day</p>', unsafe_allow_html=True)
        day = st.selectbox("Day", ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"], label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ================================
    # PROFESSIONAL DIET PLAN DISPLAY
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
                padding: 0;
                background: transparent;
            }}
            
            .container {{
                background: white;
                padding: 2.5rem;
                border-radius: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                border: 1px solid #e2e8f0;
            }}
            
            h2 {{
                color: #1a202c;
                font-size: 1.75rem;
                font-weight: 700;
                margin-bottom: 2rem;
                text-align: center;
                padding-bottom: 1rem;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.25rem;
                margin-top: 1.5rem;
            }}
            
            .card {{
                background: #f8fafc;
                padding: 1.75rem;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                transition: all 0.2s ease;
                position: relative;
            }}
            
            .card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                border-color: #cbd5e1;
            }}
            
            .card-icon {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                display: block;
            }}
            
            .card-title {{
                font-size: 1.2rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .card-content {{
                color: #475569;
                font-size: 0.95rem;
                line-height: 1.6;
                font-weight: 400;
            }}
            
            .notes-card {{
                grid-column: 1 / -1;
                background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
                border-color: #bfdbfe;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 1.5rem;
                }}
                
                h2 {{
                    font-size: 1.5rem;
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
<div style="text-align: center; margin-top: 3rem; padding: 2rem; 
            background: white; border-radius: 16px;
            border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);">
    <p style="color: #64748b; font-size: 0.9rem; margin: 0;">
        Made with ❤️ by AI-NutritionalCare Team | Powered by Advanced AI
    </p>
</div>
""", unsafe_allow_html=True)
