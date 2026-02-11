import streamlit as st
import pdfplumber
import pandas as pd
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
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []

# --------------------------------------------------
# GLOBAL CSS (NO EMPTY BOXES)
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #f5f5f5; }

/* Kill Streamlit auto spacing */
.main .block-container {
    max-width: 1200px;
    padding-top: 1rem;
    padding-bottom: 1rem;
}

div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }
section.main > div:empty { display: none !important; }

#MainMenu, header, footer { display: none !important; }

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    width: 100%;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border: none;
}

.stDownloadButton > button {
    background-color: #059669;
    color: white;
    border: none;
}

/* Select boxes */
.stSelectbox label {
    font-weight: 600;
    color: black;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b;
    color: white;
}

[data-baseweb="select"] span {
    color: white;
}

/* Metrics */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: black;
    font-weight: 600;
}

h1, h2, h3 { color: black; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
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
    c = []
    if "diabetes" in t: c.append("Diabetes")
    if "cholesterol" in t: c.append("High Cholesterol")
    if "hypertension" in t: c.append("Hypertension")
    return c or ["General Health"]

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
    c.drawString(40, y, f"Conditions: {', '.join(conditions)}")
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

# --------------------------------------------------
# HEADER
# --------------------------------------------------
with st.container():
    st.markdown("""
    <div style="background:white; padding:2rem; border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <h1>🥗 AI-NutritionalCare</h1>
        <p>Your Personalized AI-Powered Diet Companion</p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
with st.container():
    st.markdown("""
    <div style="background:white; padding:2rem; border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type=["pdf"])

    if st.button("✨ Generate Diet Recommendation"):
        if uploaded:
            with st.spinner("Analyzing medical report..."):
                text = extract_text(uploaded)
                st.session_state.patient = extract_patient_name(text)
                st.session_state.conditions = extract_conditions(text)
                st.session_state.generated = True
            st.success("Diet plan generated successfully!")
        else:
            st.warning("Please upload a PDF report")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------
if st.session_state.generated:

    # PATIENT SUMMARY
    with st.container():
        st.markdown("""
        <div style="background:white; padding:2rem; border-radius:12px;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)

        st.subheader("📋 Patient Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Patient", st.session_state.patient)
        c2.metric("Conditions", ", ".join(st.session_state.conditions))
        c3.metric("Plan Duration", "1 Month")

        st.markdown("</div>", unsafe_allow_html=True)

    # TIMELINE
    with st.container():
        st.markdown("""
        <div style="background:#1e293b; padding:2rem; border-radius:12px;">
            <h3 style="color:white;">📅 Select Timeline</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        week = col1.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"])
        day = col2.selectbox("Day", [f"Day {i}" for i in range(1, 8)])

    # DIET PLAN
    with st.container():
        st.markdown("""
        <div style="background:white; padding:2rem; border-radius:12px;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)

        st.subheader(f"🍽️ {day} Diet Plan")

        c1, c2 = st.columns(2)
        c1.info(f"🍳 Breakfast\n\n{DAY_PLAN['Breakfast']}")
        c1.info(f"🍛 Lunch\n\n{DAY_PLAN['Lunch']}")
        c2.info(f"🌙 Dinner\n\n{DAY_PLAN['Dinner']}")
        c2.info(f"🍎 Snacks\n\n{DAY_PLAN['Snacks']}")

        st.success(f"💡 {DAY_PLAN['Notes']}")

        st.markdown("</div>", unsafe_allow_html=True)

    # DOWNLOADS
    with st.container():
        st.markdown("""
        <div style="background:white; padding:2rem; border-radius:12px;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)

        st.subheader("📥 Download Your Diet Plan")
        c1, c2 = st.columns(2)

        c1.download_button(
            "📄 Download JSON",
            data=pd.Series({
                "patient": st.session_state.patient,
                "conditions": st.session_state.conditions,
                "diet_plan": DAY_PLAN
            }).to_json(),
            file_name="diet_plan.json",
            mime="application/json"
        )

        c2.download_button(
            "📑 Download PDF",
            data=generate_pdf(
                st.session_state.patient,
                st.session_state.conditions,
                DAY_PLAN
            ),
            file_name="diet_plan.pdf",
            mime="application/pdf"
        )

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
with st.container():
    st.markdown("""
    <div style="background:white; padding:1.2rem; border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.1); text-align:center;">
        <p>Made with ❤️ by AI-NutritionalCare Team | Powered by Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
