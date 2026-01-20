import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import re
import spacy
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="centered"
)

st.title("🥗 AI-NutritionalCare")
st.caption("AI-driven Personalized Diet Recommendation System")
st.markdown("---")

# ---------------- NLP SAFE LOAD ----------------
@st.cache_resource
def load_spacy():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp

nlp = load_spacy()

# ---------------- UTILITIES ----------------
def extract_patient_name(text):
    patterns = [
        r"patient\s*name\s*[:\-]\s*(.+)",
        r"patient\s*[:\-]\s*(.+)",
        r"name\s*[:\-]\s*(.+)"
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().split("\n")[0]
    return "Unknown Patient"

def extract_text(uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    text = ""

    if ext == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    elif ext in ["png", "jpg", "jpeg"]:
        try:
            img = Image.open(uploaded_file)
            text = pytesseract.image_to_string(img)
        except:
            text = ""

    elif ext == "txt":
        text = uploaded_file.read().decode("utf-8")

    elif ext == "csv":
        df = pd.read_csv(uploaded_file)
        if "doctor_prescription" in df.columns:
            text = df["doctor_prescription"].iloc[0]
        elif "patient_name" in df.columns:
            text = "Patient Name: " + df["patient_name"].iloc[0]

    return text.strip()

# ---------------- DIET ENGINE ----------------
def generate_monthly_diet(condition_text, food_pref):
    veg = food_pref == "Vegetarian"

    base_protein = (
        ["lentils", "paneer", "tofu"]
        if veg else
        ["grilled chicken", "fish", "eggs"]
    )

    month_plan = {}

    for week in range(1, 5):
        month_plan[f"Week {week}"] = {
            "Breakfast": f"Oats, fruits, {base_protein[0]}",
            "Lunch": f"Brown rice, vegetables, {base_protein[1]}",
            "Snack": "Fruits or nuts",
            "Dinner": f"Salad, soup, {base_protein[2]}"
        }

    return month_plan

def infer_conditions(text):
    conditions = []
    if "diabetes" in text.lower():
        conditions.append("Diabetes")
    if "cholesterol" in text.lower():
        conditions.append("High Cholesterol")
    if "hypertension" in text.lower() or "blood pressure" in text.lower():
        conditions.append("Hypertension")

    return conditions or ["General Health"]

# ---------------- PDF GENERATOR ----------------
def generate_pdf(patient, conditions, diet):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "AI-NutritionalCare Diet Report")

    y -= 40
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Patient: {patient}")
    y -= 20
    c.drawString(50, y, f"Medical Conditions: {', '.join(conditions)}")

    y -= 30
    for week, meals in diet.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, week)
        y -= 20
        c.setFont("Helvetica", 10)
        for m, v in meals.items():
            c.drawString(60, y, f"{m}: {v}")
            y -= 15
        y -= 10

        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- UI INPUT ----------------
st.subheader("📄 Upload Medical Report")

food_pref = st.radio("🍽 Food Preference", ["Vegetarian", "Non-Vegetarian"])

uploaded_file = st.file_uploader(
    "Upload PDF / Image / TXT / CSV",
    type=["pdf", "png", "jpg", "jpeg", "txt", "csv"]
)

manual_text = st.text_area("OR paste doctor prescription text", height=120)

process = st.button("🔍 Generate Diet Recommendation")

# ---------------- EXECUTION ----------------
if process:
    if not uploaded_file and not manual_text.strip():
        st.warning("Please upload a file or paste text.")
    else:
        with st.spinner("Analyzing medical data..."):
            text = extract_text(uploaded_file) if uploaded_file else manual_text

            patient = extract_patient_name(text)
            conditions = infer_conditions(text)
            monthly_diet = generate_monthly_diet(text, food_pref)

        st.markdown("## 📋 Final Diet Plan")

        st.markdown(f"""
        **Patient:** {patient}  
        **Medical Condition:** {", ".join(conditions)}
        """)

        for week, meals in monthly_diet.items():
            with st.expander(week):
                for k, v in meals.items():
                    st.write(f"**{k}:** {v}")

        json_data = {
            "patient": patient,
            "conditions": conditions,
            "diet_plan": monthly_diet
        }

        st.download_button(
            "⬇️ Download JSON",
            data=pd.Series(json_data).to_json(),
            file_name=f"{patient}_DietPlan.json",
            mime="application/json"
        )

        pdf_file = generate_pdf(patient, conditions, monthly_diet)

        st.download_button(
            "⬇️ Download PDF",
            data=pdf_file,
            file_name=f"{patient}_DietPlan.pdf",
            mime="application/pdf"
        )

        st.success("✅ Diet plan generated successfully!")

st.markdown("---")
st.caption("© AI-NutritionalCare | Internship Project – End-to-End Deployment")
