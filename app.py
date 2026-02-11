import streamlit as st
import pdfplumber
import pandas as pd
import re
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {font-family: 'Inter', sans-serif !important;}
.stApp {background: #f5f5f5 !important;}
.main .block-container {max-width: 1000px !important; padding: 1rem !important;}
#MainMenu, footer, header {display: none !important;}
section[data-testid="stFileUploadDropzone"] {background: transparent !important;}
.stButton > button {background: #2563eb !important; color: white !important; border: none !important; padding: 0.75rem 2rem !important; border-radius: 8px !important; font-weight: 600 !important; width: 100% !important;}
.stDownloadButton > button {background: #059669 !important; color: white !important; border: none !important; padding: 0.75rem 2rem !important; border-radius: 8px !important; font-weight: 600 !important; width: 100% !important;}
.stSelectbox label {color: #000000 !important; font-weight: 600 !important;}
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

# 28 DAYS OF VARIED MEAL PLANS
MEAL_PLANS = {
    1: {"Breakfast": "Oats Porridge with Banana, Almonds", "Lunch": "Brown Rice, Dal, Cucumber Salad", "Dinner": "2 Rotis, Mix Veg Curry, Curd", "Snacks": "Apple, Green Tea"},
    2: {"Breakfast": "2 Whole Wheat Chapatis, Mixed Veg Sabzi, Yogurt", "Lunch": "1 cup Brown Rice, Dal Tadka, Raita, Salad", "Dinner": "2 Rotis, Palak Paneer, Mixed Salad", "Snacks": "Roasted Chickpeas (30g), 1 Apple"},
    3: {"Breakfast": "Poha with Peanuts, Lemon", "Lunch": "Quinoa, Rajma Curry, Salad", "Dinner": "2 Rotis, Bhindi Masala, Raita", "Snacks": "Carrot Sticks, Hummus"},
    4: {"Breakfast": "Upma with Vegetables", "Lunch": "Brown Rice, Chana Dal, Stir-fry Veggies", "Dinner": "2 Rotis, Aloo Gobi, Salad", "Snacks": "Banana, Handful Nuts"},
    5: {"Breakfast": "Idli (3), Sambar, Coconut Chutney", "Lunch": "Brown Rice, Moong Dal, Beetroot Salad", "Dinner": "2 Rotis, Baingan Bharta, Curd", "Snacks": "Orange, Walnuts"},
    6: {"Breakfast": "Vegetable Dalia", "Lunch": "Whole Wheat Roti (2), Chole, Salad", "Dinner": "Brown Rice, Dal Fry, Cabbage Salad", "Snacks": "Pear, Green Tea"},
    7: {"Breakfast": "Besan Chilla (2), Mint Chutney", "Lunch": "Brown Rice, Kadhi, Stir-fry Beans", "Dinner": "2 Rotis, Lauki Sabzi, Raita", "Snacks": "Guava, Almonds"},
    8: {"Breakfast": "Oats Idli, Sambar", "Lunch": "Bajra Roti (2), Dal, Mixed Veg", "Dinner": "Brown Rice, Palak Dal, Tomato Salad", "Snacks": "Pomegranate, Cashews"},
    9: {"Breakfast": "Ragi Dosa (2), Chutney", "Lunch": "Brown Rice, Toor Dal, Carrot Salad", "Dinner": "2 Rotis, Mushroom Curry, Curd", "Snacks": "Kiwi, Pistachios"},
    10: {"Breakfast": "Vegetable Poha", "Lunch": "Whole Wheat Roti (2), Methi Dal, Salad", "Dinner": "Brown Rice, Aloo Matar, Raita", "Snacks": "Apple, Herbal Tea"},
    11: {"Breakfast": "Moong Dal Chilla (2)", "Lunch": "Brown Rice, Arhar Dal, Cucumber Raita", "Dinner": "2 Rotis, Cauliflower Curry, Salad", "Snacks": "Mango Slices, Nuts"},
    12: {"Breakfast": "Broken Wheat Upma", "Lunch": "Bajra Roti (2), Sambhar, Mixed Veg", "Dinner": "Brown Rice, Chana Dal, Beetroot Salad", "Snacks": "Papaya, Green Tea"},
    13: {"Breakfast": "Vegetable Uttapam (2)", "Lunch": "Brown Rice, Masoor Dal, Onion Salad", "Dinner": "2 Rotis, Spinach Paneer, Curd", "Snacks": "Grapes, Walnuts"},
    14: {"Breakfast": "Semolina Upma with Veggies", "Lunch": "Whole Wheat Roti (2), Rajma, Salad", "Dinner": "Brown Rice, Dal Tadka, Cabbage Slaw", "Snacks": "Orange, Almonds"},
    15: {"Breakfast": "Oats Pancakes (2), Honey", "Lunch": "Brown Rice, Moong Dal, Tomato Salad", "Dinner": "2 Rotis, Baingan Curry, Raita", "Snacks": "Pear, Cashews"},
    16: {"Breakfast": "Vegetable Vermicelli", "Lunch": "Bajra Roti (2), Chole, Mixed Salad", "Dinner": "Brown Rice, Arhar Dal, Cucumber Raita", "Snacks": "Banana, Pistachios"},
    17: {"Breakfast": "Ragi Porridge with Nuts", "Lunch": "Brown Rice, Kadhi, Stir-fry Cabbage", "Dinner": "2 Rotis, Bhindi Fry, Curd", "Snacks": "Guava, Green Tea"},
    18: {"Breakfast": "Besan Chilla (2) with Veggies", "Lunch": "Whole Wheat Roti (2), Dal Fry, Salad", "Dinner": "Brown Rice, Palak Dal, Onion Salad", "Snacks": "Apple, Walnuts"},
    19: {"Breakfast": "Idli (3), Coconut Chutney", "Lunch": "Brown Rice, Toor Dal, Carrot Raita", "Dinner": "2 Rotis, Aloo Gobi, Mixed Salad", "Snacks": "Kiwi, Almonds"},
    20: {"Breakfast": "Vegetable Poha with Lemon", "Lunch": "Bajra Roti (2), Methi Dal, Salad", "Dinner": "Brown Rice, Chana Dal, Beetroot Salad", "Snacks": "Orange, Nuts"},
    21: {"Breakfast": "Moong Dal Dosa (2)", "Lunch": "Brown Rice, Masoor Dal, Cucumber Salad", "Dinner": "2 Rotis, Lauki Sabzi, Raita", "Snacks": "Pomegranate, Cashews"},
    22: {"Breakfast": "Broken Wheat Porridge", "Lunch": "Whole Wheat Roti (2), Rajma, Mixed Veg", "Dinner": "Brown Rice, Dal Tadka, Tomato Salad", "Snacks": "Mango, Green Tea"},
    23: {"Breakfast": "Oats Upma", "Lunch": "Brown Rice, Moong Dal, Onion Raita", "Dinner": "2 Rotis, Mushroom Curry, Salad", "Snacks": "Papaya, Walnuts"},
    24: {"Breakfast": "Vegetable Dalia", "Lunch": "Bajra Roti (2), Chole, Carrot Salad", "Dinner": "Brown Rice, Arhar Dal, Cabbage Slaw", "Snacks": "Grapes, Almonds"},
    25: {"Breakfast": "Ragi Idli (3), Sambar", "Lunch": "Brown Rice, Kadhi, Mixed Veg", "Dinner": "2 Rotis, Palak Paneer, Curd", "Snacks": "Pear, Pistachios"},
    26: {"Breakfast": "Besan Pancakes (2)", "Lunch": "Whole Wheat Roti (2), Dal Fry, Salad", "Dinner": "Brown Rice, Chana Dal, Cucumber Raita", "Snacks": "Apple, Cashews"},
    27: {"Breakfast": "Vegetable Vermicelli", "Lunch": "Brown Rice, Toor Dal, Beetroot Salad", "Dinner": "2 Rotis, Baingan Bharta, Raita", "Snacks": "Banana, Green Tea"},
    28: {"Breakfast": "Oats Porridge with Berries", "Lunch": "Bajra Roti (2), Methi Dal, Mixed Salad", "Dinner": "Brown Rice, Dal Tadka, Tomato Salad", "Snacks": "Orange, Walnuts"}
}

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

st.markdown("""
<div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">
    <h1 style="font-size: 2.25rem; font-weight: 700; color: #000; margin: 0;">🥗 AI-NutritionalCare</h1>
    <p style="font-size: 1rem; color: #666; margin: 0.5rem 0 0 0;">Your Personalized AI-Powered Diet Companion</p>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📄 Upload Medical Report (PDF)", type=["pdf"], label_visibility="collapsed")
st.markdown('<div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 1rem 0;">', unsafe_allow_html=True)
if st.button("✨ Generate Diet Recommendation"):
    if uploaded:
        with st.spinner("Analyzing..."):
            text = extract_text(uploaded)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.session_state.generated = True
        st.success("✅ 28-Day Diet Plan Generated!")
    else:
        st.warning("⚠️ Please upload a report")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.generated:
    
    st.markdown("""
    <div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #000; margin: 0 0 1rem 0;">📋 Patient Summary</h2>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Patient", st.session_state.patient)
    with col2:
        st.metric("🏥 Condition", ', '.join(st.session_state.conditions))
    with col3:
        st.metric("📅 Duration", "28 Days")
    
    st.markdown('<div style="background: #1e293b; padding: 1.75rem; border-radius: 12px; margin: 1rem 0;"><h3 style="color: white !important; margin: 0 0 1rem 0; font-size: 1.25rem;">📅 Select Timeline</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        week = st.selectbox("Week", ["Week 1", "Week 2", "Week 3", "Week 4"], label_visibility="collapsed")
    with col2:
        day_num = st.selectbox("Day", list(range(1, 29)), format_func=lambda x: f"Day {x}", label_visibility="collapsed")
    
    plan = MEAL_PLANS[day_num]
    
    st.markdown(f"""
    <div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 1rem 0;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #000; margin: 0 0 1rem 0;">🍽️ Day {day_num} Diet Plan</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🍳 Breakfast")
        st.info(plan["Breakfast"])
        st.markdown("### 🍛 Lunch")
        st.info(plan["Lunch"])
    with col2:
        st.markdown("### 🌙 Dinner")
        st.info(plan["Dinner"])
        st.markdown("### 🍎 Snacks")
        st.info(plan["Snacks"])
    
    st.success("💡 Drink 8-10 glasses of water daily. Avoid sugary drinks and processed foods.")
    
    st.markdown("""
    <div style="background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 1rem 0;">
        <h2 style="font-size: 1.5rem; font-weight: 700; color: #000; margin: 0 0 1rem 0;">📥 Download</h2>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📄 Download JSON", data=pd.Series({"patient": st.session_state.patient, "conditions": st.session_state.conditions, "day": day_num, "plan": plan}).to_json(), file_name=f"day{day_num}_plan.json", mime="application/json")
    with col2:
        st.download_button("📑 Download PDF", data=generate_pdf(st.session_state.patient, st.session_state.conditions, plan), file_name=f"day{day_num}_plan.pdf", mime="application/pdf")

st.markdown('<div style="background: white; padding: 1.25rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; margin-top: 1rem;"><p style="color: #666; margin: 0; font-size: 0.9rem;">Made with ❤️ by AI-NutritionalCare Team</p></div>', unsafe_allow_html=True)
