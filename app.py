import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title=“AI-NutritionalCare”, page_icon=“🥗”, layout=“centered”)

if “generated” not in st.session_state:
st.session_state.generated = False
if “patient” not in st.session_state:
st.session_state.patient = “”
if “conditions” not in st.session_state:
st.session_state.conditions = []

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #e8eaf0 !important;
}

.main .block-container {
    max-width: 1100px !important;
    padding: 2rem 1.5rem !important;
}

#MainMenu, footer, header {
    display: none !important;
}

.element-container {
    background: transparent !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 1rem !important;
    background: transparent !important;
}

.stMarkdown {
    background: transparent !important;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s ease !important;
    font-size: 1rem !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
}

.stDownloadButton > button {
    background: #10b981 !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
    background: #059669 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
}

[data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

.stSelectbox label {
    color: #1f2937 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 10px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: white !important;
    color: #1f2937 !important;
    font-weight: 500 !important;
    padding: 0.75rem 1rem !important;
}

.stSelectbox svg {
    fill: #6b7280 !important;
}

[role="listbox"] {
    background-color: white !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
}

[role="option"] {
    background-color: white !important;
    color: #1f2937 !important;
    padding: 0.75rem 1rem !important;
}

[role="option"]:hover {
    background-color: #f3f4f6 !important;
    color: #667eea !important;
}

[data-baseweb="select"] span {
    color: #1f2937 !important;
}

[data-testid="stMetricValue"] {
    color: #1f2937 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px !important;
}

h1 {
    color: #1f2937 !important;
    font-weight: 700 !important;
}

h2 {
    color: #374151 !important;
    font-weight: 600 !important;
}

h3 {
    color: #4b5563 !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}

.stAlert {
    background-color: #f0f9ff !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}

div[data-baseweb="notification"] {
    background-color: #f0fdf4 !important;
    border-left: 4px solid #10b981 !important;
}
</style>

“””, unsafe_allow_html=True)

def extract_text(file):
text = “”
with pdfplumber.open(file) as pdf:
for page in pdf.pages:
if page.extract_text():
text += page.extract_text() + “\n”
return text

def extract_patient_name(text):
patterns = [r”patient\s*name\s*[:-]\s*([A-Za-z ]+)”, r”name\s*[:-]\s*([A-Za-z ]+)”]
for p in patterns:
m = re.search(p, text, re.I)
if m:
return m.group(1).strip()
return “Patient Name Not Found”

def extract_conditions(text):
t = text.lower()
cond = []
if “diabetes” in t:
cond.append(“Diabetes”)
if “cholesterol” in t:
cond.append(“High Cholesterol”)
if “hypertension” in t:
cond.append(“Hypertension”)
return cond or [“General Health”]

DAY_PLAN = {
“Breakfast”: “2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt”,
“Lunch”: “1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad”,
“Dinner”: “2 Rotis, Palak Paneer, Mixed Vegetable Salad”,
“Snacks”: “Roasted Chickpeas (30g), 1 Apple”,
“Notes”: “Drink at least 8-10 glasses of water. Avoid sugary drinks.”
}

def generate_pdf(patient, conditions, diet):
buffer = BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
y = 800
c.setFont(“Helvetica-Bold”, 14)
c.drawString(40, y, “AI-NutritionalCare Diet Report”)
y -= 30
c.setFont(“Helvetica”, 11)
c.drawString(40, y, f”Patient: {patient}”)
y -= 20
c.drawString(40, y, f”Medical Conditions: {’, ’.join(conditions)}”)
y -= 30
for k, v in diet.items():
c.setFont(“Helvetica-Bold”, 11)
c.drawString(40, y, k)
y -= 15
c.setFont(“Helvetica”, 10)
c.drawString(50, y, v)
y -= 20
c.save()
buffer.seek(0)
return buffer

# Header Section

st.markdown(”””

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
    <h1 style="font-size: 2.5rem; font-weight: 700; color: white; margin: 0;">🥗 AI-NutritionalCare</h1>
    <p style="font-size: 1.1rem; color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Your Personalized AI-Powered Diet Companion</p>
</div>
""", unsafe_allow_html=True)

# Upload Section

st.markdown(’<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">’, unsafe_allow_html=True)
st.markdown(”### 📄 Upload Medical Report”)
uploaded = st.file_uploader(“Upload PDF”, type=[“pdf”], label_visibility=“collapsed”)
st.markdown(”</div>”, unsafe_allow_html=True)

# Generate Button

st.markdown(’<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">’, unsafe_allow_html=True)
if st.button(“✨ Generate Personalized Diet Plan”):
if uploaded:
with st.spinner(“🔍 Analyzing your medical report…”):
text = extract_text(uploaded)
st.session_state.patient = extract_patient_name(text)
st.session_state.conditions = extract_conditions(text)
st.session_state.generated = True
st.success(“✅ Diet plan generated successfully!”)
else:
st.warning(“⚠️ Please upload a medical report first”)
st.markdown(’</div>’, unsafe_allow_html=True)

if st.session_state.generated:

```
# Patient Summary
st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
st.markdown("### 📋 Patient Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👤 Patient Name", st.session_state.patient)
with col2:
    st.metric("🏥 Medical Condition", ', '.join(st.session_state.conditions))
with col3:
    st.metric("📅 Plan Duration", "1 Month")
st.markdown('</div>', unsafe_allow_html=True)

# Timeline Selection
st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
st.markdown("### 📅 Select Timeline")
col1, col2 = st.columns(2)
with col1:
    week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
with col2:
    day = st.selectbox("Day", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"])
st.markdown('</div>', unsafe_allow_html=True)

# Diet Plan Display
st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
st.markdown(f"### 🍽️ {day} Diet Plan")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.markdown("**🌅 Breakfast**")
    st.info(DAY_PLAN["Breakfast"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.markdown("**☀️ Lunch**")
    st.info(DAY_PLAN["Lunch"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.markdown("**🌙 Dinner**")
    st.info(DAY_PLAN["Dinner"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.markdown("**🍎 Snacks**")
    st.info(DAY_PLAN["Snacks"])
    st.markdown('</div>', unsafe_allow_html=True)

st.success(f"💡 Pro Tip: {DAY_PLAN['Notes']}")
st.markdown('</div>', unsafe_allow_html=True)

# Download Section
st.markdown('<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">', unsafe_allow_html=True)
st.markdown("### 📥 Download Your Diet Plan")
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
    st.download_button(
        "📑 Download as PDF",
        data=generate_pdf(st.session_state.patient, st.session_state.conditions, DAY_PLAN),
        file_name="diet_plan.pdf",
        mime="application/pdf"
    )
st.markdown('</div>', unsafe_allow_html=True)
```

# Footer

st.markdown(”””

<div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;">
    <p style="color: #6b7280; margin: 0; font-size: 0.95rem;">
        Made with ❤️ by AI-NutritionalCare Team | Transforming Healthcare Through AI
    </p>
</div>
""", unsafe_allow_html=True)
