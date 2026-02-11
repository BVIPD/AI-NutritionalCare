import streamlit as st
import pdfplumber
import pandas as pd
import re
import random
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="AI-NutritionalCare", page_icon="🥗", layout="centered")

if "generated" not in st.session_state:
    st.session_state.generated = False
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []
if "full_plan" not in st.session_state:
    st.session_state.full_plan = {}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* {font-family: 'Inter', sans-serif !important;}
.stApp {background: #f5f5f5 !important;}
.main .block-container {max-width: 1000px !important; padding: 1rem !important;}
#MainMenu, footer, header {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
.element-container {background: transparent !important; padding: 0 !important; margin: 0 !important;}
div[data-testid="stVerticalBlock"] {gap: 0 !important; background: transparent !important;}
.stMarkdown {background: transparent !important; margin: 0 !important;}
.stButton > button {background: #2563eb !important; color: white !important; border: none !important; padding: 0.75rem 2rem !important; border-radius: 8px !important; font-weight: 600 !important; width: 100% !important;}
.stDownloadButton > button {background: #059669 !important; color: white !important; border: none !important; padding: 0.75rem 2rem !important; border-radius: 8px !important; font-weight: 600 !important; width: 100% !important;}
[data-testid="stFileUploader"] {background: transparent !important; border: 2px dashed #cbd5e1 !important; border-radius: 8px !important; padding: 1.5rem !important;}
.stSelectbox label {color: #000 !important; font-weight: 600 !important;}
.stSelectbox div[data-baseweb="select"] {background-color: #1e293b !important;}
.stSelectbox div[data-baseweb="select"] > div {background-color: #1e293b !important; color: white !important; font-weight: 500 !important;}
.stSelectbox svg {fill: white !important;}
[role="listbox"] {background-color: #1e293b !important;}
[role="option"] {background-color: #1e293b !important; color: white !important;}
[role="option"]:hover {background-color: #334155 !important;}
[data-baseweb="select"] span {color: white !important;}
[data-testid="stMetricValue"] {color: #000 !important; font-size: 1.25rem !important; font-weight: 600 !important;}
[data-testid="stMetricLabel"] {color: #000 !important; font-weight: 600 !important;}
h1, h2, h3 {color: #000 !important;}
</style>
""", unsafe_allow_html=True)

# MEAL OPTIONS - Different meals for variety
BREAKFAST_OPTIONS = [
    "2 Whole Wheat Chapatis (50g each), Mixed Vegetable Sabzi, Yogurt",
    "Oatmeal with Berries, Almonds, and Low-fat Milk",
    "Poha with Vegetables, Peanuts, and Green Chutney",
    "Idli (3pcs) with Sambar and Coconut Chutney",
    "Upma with Vegetables and a Glass of Buttermilk",
    "Vegetable Paratha (2) with Curd and Pickle",
    "Moong Dal Cheela with Mint Chutney"
]

LUNCH_OPTIONS = [
    "1 cup Brown Rice, Dal Tadka, Cucumber Raita, Salad",
    "2 Rotis, Rajma Curry, Jeera Rice, Mixed Salad",
    "Quinoa Pulao, Mixed Vegetable Curry, Raita",
    "2 Multigrain Rotis, Chana Masala, Vegetable Salad",
    "Brown Rice, Sambhar, Cabbage Poriyal, Curd",
    "2 Rotis, Mix Veg Sabzi, Dal Fry, Salad",
    "Millet Khichdi with Curd and Papad"
]

DINNER_OPTIONS = [
    "2 Rotis, Palak Paneer, Mixed Vegetable Salad",
    "Grilled Paneer, Quinoa, Stir-fried Vegetables",
    "2 Rotis, Bhindi Masala, Tomato Soup",
    "Brown Rice, Moong Dal, Bottle Gourd Curry",
    "2 Chapatis, Tofu Curry, Green Salad",
    "Vegetable Soup, Grilled Vegetables, 1 Roti",
    "2 Rotis, Baingan Bharta, Sprouts Salad"
]

SNACKS_OPTIONS = [
    "Roasted Chickpeas (30g), 1 Apple",
    "Mixed Nuts (30g), 1 Orange",
    "Carrot Sticks with Hummus",
    "Greek Yogurt with Berries",
    "Sprouts Salad with Lemon",
    "Roasted Makhana (30g), Green Tea",
    "Fruit Salad (Apple, Banana, Pomegranate)"
]

NOTES_OPTIONS = [
    "Drink at least 8–10 glasses of water. Avoid sugary drinks.",
    "Stay hydrated. Limit salt intake. Include a 30-min walk.",
    "Avoid processed foods. Practice portion control.",
    "Include fiber-rich foods. Limit oil and sugar.",
    "Eat at regular intervals. Avoid late-night meals."
]

def extract_text_from_file(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    elif file.type == "text/csv":
        df = pd.read_csv(file)
        text = df.to_string()
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

def generate_28_day_plan():
    plan = {}
    for day in range(1, 29):
        plan[f"Day {day}"] = {
            "Breakfast": random.choice(BREAKFAST_OPTIONS),
            "Lunch": random.choice(LUNCH_OPTIONS),
            "Dinner": random.choice(DINNER_OPTIONS),
            "Snacks": random.choice(SNACKS_OPTIONS),
            "Notes": random.choice(NOTES_OPTIONS)
        }
    return plan

def generate_pdf(patient, conditions, full_plan):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "AI-NutritionalCare - 28 Day Diet Plan")
    y -= 30
    
    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Patient: {patient}")
    y -= 20
    c.drawString(40, y, f"Conditions: {', '.join(conditions)}")
    y -= 30
    
    for day_name, meals in full_plan.items():
        if y < 100:
            c.showPage()
            y = 800
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, day_name)
        y -= 18
        
        c.setFont("Helvetica", 9)
        for meal, food in meals.items():
            c.drawString(50, y, f"{meal}: {food[:80]}")
            y -= 14
        y -= 10
    
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("""
<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">
    <h1 style="font-size: 2.25rem; font-weight: 700; color: #000; margin: 0;">🥗 AI-NutritionalCare</h1>
    <p style="font-size: 1rem; color: #666; margin: 0.5rem 0 0 0;">Your Personalized AI-Powered Diet Companion</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">', unsafe_allow_html=True)
uploaded = st.file_uploader("📄 Upload Medical Report (PDF/TXT/CSV)", type=["pdf", "txt", "csv"])
if st.button("✨ Generate 28-Day Diet Plan"):
    if uploaded:
        with st.spinner("Generating your personalized 28-day meal plan..."):
            text = extract_text_from_file(uploaded)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.session_state.full_plan = generate_28_day_plan()
            st.session_state.generated = True
        st.success("✅ 28-day diet plan generated!")
    else:
        st.warning("⚠️ Please upload a report")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.generated:
    
    st.markdown('<div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.subheader("📋 Patient Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Patient", st.session_state.patient)
    with col2:
        st.metric("🏥 Condition", ', '.join(st.session_state.conditions))
    with col3:
        st.metric("📅 Duration", "28 Days")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: #1e293b; padding: 1.75rem; border-radius: 12px; margin-bottom: 1rem;"><h3 style="color: white !important; margin: 0 0 1rem 0; font-size: 1.25rem;">📅 Select Day</h3></div>', unsafe_allow_html=True)
    
    day_options = [f"Day {i}" for i in range(1, 29)]
    selected_day = st.selectbox("Choose Day", day_options)
    
    day_plan = st.session_state.full_plan[selected_day]
    
    st.markdown('<div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.subheader(f"🍽️ {selected_day} Diet Plan")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🍳 Breakfast")
        st.info(day_plan["Breakfast"])
        st.markdown("### 🍛 Lunch")
        st.info(day_plan["Lunch"])
    with col2:
        st.markdown("### 🌙 Dinner")
        st.info(day_plan["Dinner"])
        st.markdown("### 🍎 Snacks")
        st.info(day_plan["Snacks"])
    st.success(f"💡 {day_plan['Notes']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.subheader("📥 Download Complete 28-Day Plan")
    col1, col2 = st.columns(2)
    with col1:
        json_data = {
            "patient": st.session_state.patient,
            "conditions": st.session_state.conditions,
            "duration": "28 Days",
            "meal_plan": st.session_state.full_plan
        }
        st.download_button("📄 Download JSON (All 28 Days)", data=pd.Series(json_data).to_json(indent=2), file_name="28_day_diet_plan.json", mime="application/json")
    with col2:
        st.download_button("📑 Download PDF (All 28 Days)", data=generate_pdf(st.session_state.patient, st.session_state.conditions, st.session_state.full_plan), file_name="28_day_diet_plan.pdf", mime="application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="background: white; padding: 1.25rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;"><p style="color: #666; margin: 0; font-size: 0.9rem;">Made with ❤️ by AI-NutritionalCare Team</p></div>', unsafe_allow_html=True)
