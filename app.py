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
    layout="centered"
)

st.title("🥗 AI-NutritionalCare")
st.caption("AI-driven Personalized Diet Recommendation System")
st.divider()

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
        text = " ".join(df.astype(str).iloc[0].values)

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
# MEAL DATA (BREAKFAST / LUNCH / DINNER)
# --------------------------------------------------
VEG_DAYS = [
    {"breakfast": "Oats Porridge", "lunch": "Veg Pulao", "dinner": "Chapati & Mixed Veg"},
    {"breakfast": "Idli & Sambar", "lunch": "Rajma Rice", "dinner": "Curd Rice"},
    {"breakfast": "Vegetable Poha", "lunch": "Veg Khichdi", "dinner": "Tomato Soup"},
    {"breakfast": "Masala Oats", "lunch": "Dal & Chapati", "dinner": "Paneer Bhurji"},
    {"breakfast": "Ragi Porridge", "lunch": "Veg Fried Rice", "dinner": "Cabbage Fry"},
    {"breakfast": "Sprouts Salad", "lunch": "Veg Biryani", "dinner": "Curd Bowl"},
    {"breakfast": "Fruit Bowl", "lunch": "Stuffed Paratha", "dinner": "Veg Soup"},
    {"breakfast": "Upma", "lunch": "Vegetable Dalia", "dinner": "Paneer Salad"},
    {"breakfast": "Besan Omelette", "lunch": "Bottle Gourd Khichdi", "dinner": "Veg Cutlet"},
    {"breakfast": "Curd & Fruits", "lunch": "Veg Sandwich", "dinner": "Lemon Rice"},
    {"breakfast": "Vegetable Toast", "lunch": "Veg Pulao", "dinner": "Dal Soup"},
    {"breakfast": "Oats Idli", "lunch": "Veg Fried Rice", "dinner": "Chapati & Sabzi"},
    {"breakfast": "Smoothie Bowl", "lunch": "Rajma Rice", "dinner": "Tomato Soup"},
    {"breakfast": "Poha", "lunch": "Veg Khichdi", "dinner": "Curd Rice"},
    {"breakfast": "Ragi Dosa", "lunch": "Dal & Chapati", "dinner": "Veg Soup"},
    {"breakfast": "Idli", "lunch": "Veg Biryani", "dinner": "Paneer Bhurji"},
    {"breakfast": "Oats Porridge", "lunch": "Veg Sandwich", "dinner": "Cabbage Fry"},
    {"breakfast": "Sprouts Bowl", "lunch": "Veg Pulao", "dinner": "Curd Bowl"},
    {"breakfast": "Fruit Salad", "lunch": "Stuffed Paratha", "dinner": "Tomato Soup"},
    {"breakfast": "Masala Oats", "lunch": "Veg Fried Rice", "dinner": "Paneer Salad"},
    {"breakfast": "Vegetable Upma", "lunch": "Veg Khichdi", "dinner": "Veg Soup"},
    {"breakfast": "Ragi Porridge", "lunch": "Dal & Chapati", "dinner": "Curd Rice"},
    {"breakfast": "Poha", "lunch": "Veg Biryani", "dinner": "Tomato Soup"},
    {"breakfast": "Oats Smoothie", "lunch": "Veg Sandwich", "dinner": "Paneer Bhurji"},
    {"breakfast": "Idli", "lunch": "Rajma Rice", "dinner": "Veg Soup"},
    {"breakfast": "Fruit Bowl", "lunch": "Veg Pulao", "dinner": "Curd Bowl"},
    {"breakfast": "Besan Toast", "lunch": "Veg Khichdi", "dinner": "Dal Soup"},
    {"breakfast": "Vegetable Poha", "lunch": "Veg Fried Rice", "dinner": "Paneer Salad"}
]

NONVEG_DAYS = [
    {"breakfast": "Boiled Eggs & Toast", "lunch": "Grilled Chicken & Rice", "dinner": "Fish Curry"},
    {"breakfast": "Egg Omelette", "lunch": "Chicken Pulao", "dinner": "Chicken Soup"},
    {"breakfast": "Egg Toast", "lunch": "Fish Rice Bowl", "dinner": "Chicken Stir Fry"},
    {"breakfast": "Scrambled Eggs", "lunch": "Chicken Curry", "dinner": "Egg Salad"},
    {"breakfast": "Boiled Eggs", "lunch": "Grilled Fish", "dinner": "Chicken Wrap"},
    {"breakfast": "Egg Bhurji", "lunch": "Chicken Biryani", "dinner": "Fish Soup"},
    {"breakfast": "Protein Toast", "lunch": "Chicken Fried Rice", "dinner": "Egg Curry"},
    {"breakfast": "Egg Sandwich", "lunch": "Chicken Pulao", "dinner": "Fish Fry"},
    {"breakfast": "Egg Omelette", "lunch": "Grilled Chicken", "dinner": "Chicken Soup"},
    {"breakfast": "Boiled Eggs", "lunch": "Fish Curry", "dinner": "Chicken Salad"},
    {"breakfast": "Egg Toast", "lunch": "Chicken Rice", "dinner": "Egg Bhurji"},
    {"breakfast": "Egg Wrap", "lunch": "Fish Rice Bowl", "dinner": "Chicken Stir Fry"},
    {"breakfast": "Scrambled Eggs", "lunch": "Chicken Curry", "dinner": "Fish Soup"},
    {"breakfast": "Egg Omelette", "lunch": "Chicken Pulao", "dinner": "Egg Salad"},
    {"breakfast": "Boiled Eggs", "lunch": "Grilled Fish", "dinner": "Chicken Wrap"},
    {"breakfast": "Egg Toast", "lunch": "Chicken Fried Rice", "dinner": "Fish Curry"},
    {"breakfast": "Egg Bhurji", "lunch": "Chicken Biryani", "dinner": "Chicken Soup"},
    {"breakfast": "Protein Bowl", "lunch": "Fish Rice Bowl", "dinner": "Egg Curry"},
    {"breakfast": "Egg Sandwich", "lunch": "Chicken Pulao", "dinner": "Fish Fry"},
    {"breakfast": "Boiled Eggs", "lunch": "Grilled Chicken", "dinner": "Chicken Salad"},
    {"breakfast": "Egg Omelette", "lunch": "Fish Curry", "dinner": "Egg Bhurji"},
    {"breakfast": "Egg Toast", "lunch": "Chicken Rice", "dinner": "Fish Soup"},
    {"breakfast": "Scrambled Eggs", "lunch": "Chicken Curry", "dinner": "Egg Salad"},
    {"breakfast": "Egg Wrap", "lunch": "Fish Rice Bowl", "dinner": "Chicken Stir Fry"},
    {"breakfast": "Boiled Eggs", "lunch": "Chicken Pulao", "dinner": "Fish Curry"},
    {"breakfast": "Egg Sandwich", "lunch": "Grilled Fish", "dinner": "Chicken Soup"},
    {"breakfast": "Egg Bhurji", "lunch": "Chicken Fried Rice", "dinner": "Egg Curry"},
    {"breakfast": "Protein Toast", "lunch": "Chicken Biryani", "dinner": "Fish Soup"}
]

def generate_month_plan(pref):
    return VEG_DAYS if pref == "Vegetarian" else NONVEG_DAYS

# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------
def generate_pdf(patient, conditions, plan):
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
# INPUT UI
# --------------------------------------------------
uploaded = st.file_uploader("📄 Upload Medical Report (PDF / CSV / TXT)", type=["pdf", "csv", "txt"])
preference = st.radio("🥦 Food Preference", ["Vegetarian", "Non-Vegetarian"])
run = st.button("✨ Generate Diet Recommendation")

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
if run:
    if not uploaded:
        st.warning("Please upload a file.")
        st.stop()

    raw_text = extract_text(uploaded)
    patient = extract_patient_name(raw_text)
    conditions = extract_conditions(raw_text)
    month_plan = generate_month_plan(preference)

    st.subheader("📄 Output")
    st.markdown(f"""
**Patient:** {patient}  
**Medical Condition:** {', '.join(conditions)}  
**Listing 1:** Sample Diet Plan from AI-NutritionalCare
""")

    st.subheader("📅 1-Month Diet Plan (Breakfast • Lunch • Dinner)")
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

    st.download_button(
        "⬇️ Download JSON",
        data=pd.Series({
            "patient": patient,
            "conditions": conditions,
            "diet_plan": month_plan
        }).to_json(),
        file_name="diet_plan.json",
        mime="application/json"
    )

    pdf_file = generate_pdf(patient, conditions, month_plan)
    st.download_button(
        "⬇️ Download PDF",
        data=pdf_file,
        file_name=f"{patient.replace(' ', '_')}_DietPlan.pdf",
        mime="application/pdf"
    )
