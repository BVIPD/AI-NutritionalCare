import streamlit as st
import pandas as pd
import pdfplumber
import re
import json
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

st.markdown("""
<style>
.card {
    background-color: #f8fbff;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.day {
    font-size: 18px;
    font-weight: 700;
    color: #1f4fd8;
}
.recipe {
    background-color: #eef6ff;
    padding: 12px;
    border-radius: 10px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

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
    conditions = []
    t = text.lower()
    if "diabetes" in t:
        conditions.append("Diabetes")
    if "cholesterol" in t:
        conditions.append("High Cholesterol")
    if "hypertension" in t or "blood pressure" in t:
        conditions.append("Hypertension")
    return conditions if conditions else ["General Health"]

# --------------------------------------------------
# 28 UNIQUE MEALS (NO REPETITION)
# --------------------------------------------------
VEG_MEALS = [
    ("Vegetable Khichdi","Rice, dal, vegetables","Wash rice & dal. Pressure cook with vegetables and salt."),
    ("Chapati & Cabbage Sabzi","Wheat flour, cabbage","Knead dough. Roll chapati. Stir-fry cabbage."),
    ("Vegetable Upma","Rava, vegetables","Roast rava. Cook with vegetables & water."),
    ("Oats Porridge","Oats, water","Boil water. Add oats. Cook 5 minutes."),
    ("Curd Rice","Rice, curd","Mix cooked rice with curd and salt."),
    ("Vegetable Dalia","Broken wheat, vegetables","Pressure cook till soft."),
    ("Paneer Bhurji","Paneer, onion","Crumble paneer. Cook with onion."),
    ("Lemon Rice","Rice, lemon","Mix lemon juice with rice."),
    ("Idli & Sambar","Idli batter","Steam idli. Prepare sambar."),
    ("Vegetable Poha","Poha, peanuts","Cook poha with onion."),
    ("Rajma Rice","Rajma, rice","Cook rajma curry. Serve with rice."),
    ("Stuffed Paratha","Wheat flour, potato","Stuff potato. Cook paratha."),
    ("Vegetable Pulao","Rice, vegetables","Cook rice with vegetables."),
    ("Sprouts Salad","Sprouts","Boil sprouts. Add lemon."),
    ("Tomato Soup","Tomato","Boil & blend tomatoes."),
    ("Vegetable Sandwich","Bread, vegetables","Toast with vegetables."),
    ("Masala Oats","Oats, vegetables","Cook oats with spices."),
    ("Curd Bowl","Curd, cucumber","Mix curd & veggies."),
    ("Veg Fried Rice","Rice, vegetables","Stir fry vegetables & rice."),
    ("Paneer Salad","Paneer","Mix paneer & vegetables."),
    ("Vegetable Soup","Vegetables","Boil vegetables."),
    ("Ragi Porridge","Ragi flour","Cook slowly with water."),
    ("Cabbage Fry","Cabbage","Stir fry lightly."),
    ("Besan Chilla","Besan","Cook batter on pan."),
    ("Dal & Chapati","Dal","Serve dal with chapati."),
    ("Vegetable Cutlet","Vegetables","Mash, shape & shallow fry."),
    ("Bottle Gourd Curry","Lauki","Cook with spices."),
    ("Fruit Bowl","Fruits","Chop and serve.")
]

NONVEG_MEALS = [
    ("Egg Omelette","Eggs, onion","Beat eggs and cook."),
    ("Grilled Chicken","Chicken","Grill with spices."),
    ("Fish Curry","Fish","Cook with tomato gravy."),
    ("Boiled Eggs","Eggs","Boil 10 minutes."),
    ("Chicken Soup","Chicken","Boil with spices."),
    ("Egg Fried Rice","Rice, egg","Stir fry egg and rice."),
    ("Grilled Fish","Fish","Pan grill."),
    ("Chicken Sandwich","Bread, chicken","Toast sandwich."),
    ("Egg Bhurji","Eggs","Scramble with onion."),
    ("Chicken Pulao","Rice, chicken","Cook together."),
    ("Fish Fry","Fish","Shallow fry."),
    ("Chicken Curry","Chicken","Cook in gravy."),
    ("Egg Curry","Eggs","Cook boiled eggs."),
    ("Chicken Salad","Chicken","Mix with veggies."),
    ("Fish Soup","Fish","Boil lightly."),
    ("Egg Toast","Eggs","Serve on toast."),
    ("Chicken Wrap","Chapati","Wrap chicken."),
    ("Grilled Chicken Veg","Chicken","Grill with veggies."),
    ("Fish Rice Bowl","Fish","Serve with rice."),
    ("Egg Salad","Eggs","Mix chopped eggs."),
    ("Chicken Stir Fry","Chicken","Quick fry."),
    ("Fish Lemon Curry","Fish","Cook with lemon."),
    ("Egg Rice","Eggs","Serve scrambled eggs."),
    ("Chicken Stew","Chicken","Slow cook."),
    ("Fish Stew","Fish","Cook in broth."),
    ("Egg Paratha","Eggs","Cook inside paratha."),
    ("Chicken Cutlet","Chicken","Shallow fry."),
    ("Protein Bowl","Chicken & eggs","Serve together.")
]

# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------
def generate_pdf(patient, conditions, plan):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI-NutritionalCare Diet Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Patient: {patient}")
    y -= 20
    c.drawString(40, y, f"Medical Conditions: {', '.join(conditions)}")
    y -= 30

    day = 1
    for food, ing, steps in plan:
        if y < 120:
            c.showPage()
            y = height - 40

        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"Day {day}: {food}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Ingredients: {ing}")
        y -= 15
        c.drawString(50, y, f"Steps: {steps}")
        y -= 20
        day += 1

    c.save()
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# INPUT UI
# --------------------------------------------------
uploaded = st.file_uploader("📄 Upload Medical Report (PDF / CSV / TXT)", type=["pdf","csv","txt"])
preference = st.radio("🥦 Food Preference", ["Vegetarian","Non-Vegetarian"])
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

    meals = VEG_MEALS if preference == "Vegetarian" else NONVEG_MEALS

    st.subheader("📄 Output")
    st.markdown(f"""
**Patient:** {patient}  
**Medical Condition:** {', '.join(conditions)}  
**Listing 1:** Sample Diet Plan from AI-NutritionalCare
""")

    st.subheader("📅 1-Month Diet Plan (Day-wise)")
    day = 1
    for week in range(4):
        st.markdown(f"### Week {week+1}")
        for i in range(7):
            food, ing, steps = meals[week*7+i]
            st.markdown(f"""
<div class="card">
<div class="day">Day {day}: {food}</div>
<b>Ingredients:</b> {ing}
<div class="recipe"><b>How to Cook:</b> {steps}</div>
</div>
""", unsafe_allow_html=True)
            day += 1

    # Downloads
    diet_json = {
        "patient": patient,
        "conditions": conditions,
        "diet_plan": [
            {"day": i+1, "meal": m[0], "ingredients": m[1], "steps": m[2]}
            for i, m in enumerate(meals)
        ]
    }

    st.download_button(
        "⬇️ Download JSON",
        json.dumps(diet_json, indent=2),
        file_name="diet_plan.json",
        mime="application/json"
    )

    pdf = generate_pdf(patient, conditions, meals)
    st.download_button(
        "⬇️ Download PDF",
        pdf,
        file_name=f"{patient.replace(' ','_')}_DietPlan.pdf",
        mime="application/pdf"
    )

st.divider()
st.caption("© AI-NutritionalCare | Internship Final Submission")
