import streamlit as st
import pandas as pd
import pdfplumber
from PIL import Image
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="wide"
)

# -------------------- CUSTOM UI --------------------
st.markdown("""
<style>
body {background-color:#0e1117;}
.card {
    background:#161b22;
    padding:20px;
    border-radius:16px;
    margin-bottom:20px;
}
.title {
    font-size:32px;
    font-weight:700;
}
.subtitle {
    color:#9ba3af;
}
.recipe {
    background:#0d2538;
    padding:15px;
    border-radius:12px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<div class='title'>🥗 AI-NutritionalCare</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-driven Personalized Diet Recommendation System</div>", unsafe_allow_html=True)
st.divider()

# -------------------- TEXT EXTRACTION --------------------
def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

    elif ext == "csv":
        df = pd.read_csv(file)
        text = " ".join(df.astype(str).values.flatten())

    elif ext == "txt":
        text = file.read().decode("utf-8")

    else:
        text = ""

    return text.strip()

# -------------------- PATIENT NAME EXTRACTION --------------------
def extract_patient_name(text):
    match = re.search(r"(patient|name)\s*[:\-]\s*([A-Za-z ]+)", text, re.I)
    return match.group(2).strip() if match else "Unknown Patient"

# -------------------- CONDITIONS --------------------
def extract_conditions(text):
    conditions = []
    t = text.lower()
    if "diabetes" in t: conditions.append("Diabetes")
    if "cholesterol" in t: conditions.append("High Cholesterol")
    if "hypertension" in t or "blood pressure" in t: conditions.append("Hypertension")
    return conditions or ["General Health"]

# -------------------- MEAL + RECIPE DATABASE --------------------
MEALS = {
    "veg": [
        ("Vegetable Upma",
         "Ingredients: Rava, vegetables, mustard seeds, onion, oil.\n"
         "Steps:\n1. Dry roast rava.\n2. Heat oil, add mustard seeds.\n3. Add onions & vegetables.\n4. Add water, then rava.\n5. Cook till fluffy."),

        ("Oats Porridge",
         "Ingredients: Oats, water/milk, salt.\n"
         "Steps:\n1. Boil water.\n2. Add oats.\n3. Cook 5–7 mins.\n4. Serve warm."),

        ("Vegetable Khichdi",
         "Ingredients: Rice, dal, vegetables.\n"
         "Steps:\n1. Wash rice & dal.\n2. Cook with vegetables.\n3. Simmer till soft."),

        ("Chapati & Sabzi",
         "Ingredients: Wheat flour, vegetables.\n"
         "Steps:\n1. Knead dough.\n2. Roll chapatis.\n3. Cook on pan.\n4. Stir-fry vegetables separately.")
    ],
    "nonveg": [
        ("Egg Omelette",
         "Ingredients: Eggs, onion, oil.\n"
         "Steps:\n1. Beat eggs.\n2. Heat pan.\n3. Pour eggs.\n4. Cook both sides."),

        ("Grilled Chicken",
         "Ingredients: Chicken, spices.\n"
         "Steps:\n1. Marinate chicken.\n2. Grill 15–20 mins.\n3. Serve hot."),

        ("Fish Curry",
         "Ingredients: Fish, tomato, spices.\n"
         "Steps:\n1. Fry spices.\n2. Add tomato.\n3. Add fish.\n4. Simmer.")
    ]
}

# -------------------- 1-MONTH PLAN --------------------
def build_month_plan(pref):
    plan = {}
    meals = MEALS[pref]

    for week in range(1, 5):
        days = {}
        for day in range(1, 8):
            meal, recipe = meals[(week + day) % len(meals)]
            days[f"Day {day}"] = {
                "Meal": meal,
                "Recipe": recipe
            }
        plan[f"Week {week}"] = days
    return plan

# -------------------- PDF EXPORT --------------------
def generate_pdf(patient, conditions, plan):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(40, 800)

    text.textLine("AI-NutritionalCare Diet Report")
    text.textLine(f"Patient: {patient}")
    text.textLine(f"Medical Conditions: {', '.join(conditions)}")
    text.textLine("")

    for week, days in plan.items():
        text.textLine(week)
        for d, info in days.items():
            text.textLine(f"{d}: {info['Meal']}")
        text.textLine("")

    c.drawText(text)
    c.save()
    buffer.seek(0)
    return buffer

# -------------------- INPUT UI --------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

file = st.file_uploader("Upload Medical Report (PDF / CSV / TXT)")
pref = st.radio("Food Preference", ["veg", "nonveg"], horizontal=True)
manual = st.text_area("OR paste prescription text")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- PROCESS --------------------
if st.button("✨ Generate Diet Recommendation"):
    text = extract_text(file) if file else manual
    patient = extract_patient_name(text)
    conditions = extract_conditions(text)
    plan = build_month_plan(pref)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 📄 Output")
    st.write(f"**Patient:** {patient}")
    st.write(f"**Medical Condition:** {', '.join(conditions)}")
    st.write("**Listing 1:** Sample Diet Plan from AI-NutritionalCare")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 📅 1-Month Diet Plan (Day-wise with Recipes)")

    for week, days in plan.items():
        with st.expander(week):
            for d, info in days.items():
                st.markdown(f"### {d} — {info['Meal']}")
                st.markdown(f"<div class='recipe'>{info['Recipe']}</div>", unsafe_allow_html=True)

    # DOWNLOADS
    st.download_button(
        "⬇️ Download JSON",
        data=str(plan),
        file_name="diet_plan.json"
    )

    pdf = generate_pdf(patient, conditions, plan)
    st.download_button(
        "⬇️ Download PDF",
        data=pdf,
        file_name=f"{patient}_DietPlan.pdf"
    )
