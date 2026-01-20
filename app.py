import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import spacy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI-NutritionalCare",
    page_icon="🥗",
    layout="centered"
)

st.title("🥗 AI-NutritionalCare")
st.caption("AI-driven Personalized Diet Recommendation System")
st.markdown("---")

# -------------------- SAFE NLP (NO EXTERNAL MODELS) --------------------
@st.cache_resource
def load_nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp

nlp = load_nlp()

# -------------------- TEXT EXTRACTION --------------------
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
        except Exception:
            text = (
                "OCR not supported in this environment.\n"
                "Please upload PDF / TXT / CSV or paste text manually."
            )

    elif ext == "txt":
        text = uploaded_file.read().decode("utf-8")

    elif ext == "csv":
        df = pd.read_csv(uploaded_file)
        if "doctor_prescription" in df.columns:
            text = df["doctor_prescription"].iloc[0]
        else:
            text = "CSV missing 'doctor_prescription' column."

    return text.strip()

# -------------------- DIET GENERATION --------------------
def generate_diet(text, food_type):
    text = text.lower()

    diet = {
        "condition": [],
        "allowed_foods": [],
        "restricted_foods": [],
        "diet_plan": [],
        "lifestyle_advice": []
    }

    # Base foods
    veg_foods = ["vegetables", "fruits", "whole grains", "lentils"]
    nonveg_foods = veg_foods + ["eggs", "fish", "grilled chicken"]

    diet["allowed_foods"] = veg_foods if food_type == "Vegetarian" else nonveg_foods

    if "diabetes" in text:
        diet["condition"].append("Diabetes")
        diet["noticed_foods"] = "Low sugar foods recommended"
        diet["restricted_foods"].append("Sugar")
        diet["diet_plan"].append("Low sugar, low glycemic index diet.")
        diet["lifestyle_advice"].append("Daily walking for 30 minutes.")

    if "cholesterol" in text:
        diet["condition"].append("High Cholesterol")
        diet["restricted_foods"].append("Fried food")
        diet["diet_plan"].append("Increase fiber intake.")

    if "blood pressure" in text or "hypertension" in text:
        diet["condition"].append("Hypertension")
        diet["restricted_foods"].append("Excess salt")
        diet["diet_plan"].append("Low sodium diet.")
        diet["lifestyle_advice"].append("Stress management and regular exercise.")

    if not diet["condition"]:
        diet["condition"].append("General Health")
        diet["diet_plan"].append("Maintain a balanced diet.")
        diet["lifestyle_advice"].append("Stay active and hydrated.")

    return {
        "condition": ", ".join(diet["condition"]),
        "allowed_foods": list(set(diet["allowed_foods"])),
        "restricted_foods": list(set(diet["restricted_foods"])),
        "diet_plan": " ".join(diet["diet_plan"]),
        "lifestyle_advice": " ".join(diet["lifestyle_advice"])
    }

# -------------------- OUTPUT FORMATTING (SIR STYLE) --------------------
def format_output(diet, patient):
    output = f"""
Patient: {patient}
Listing 1: Sample Diet Plan from AI-NutritionalCare

Medical Condition: {diet['condition']}

Allowed Foods:
- {', '.join(diet['allowed_foods'])}

Restricted Foods:
- {', '.join(diet['restricted_foods'])}

Diet Plan:
{diet['diet_plan']}

Lifestyle Advice:
{diet['lifestyle_advice']}
"""
    return output.strip()

# -------------------- PDF GENERATION --------------------
def generate_pdf(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    for line in text.split("\n"):
        c.drawString(40, y, line)
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    buffer.seek(0)
    return buffer

# -------------------- USER INPUT UI --------------------
st.subheader("📄 Upload Medical Report")

patient_name = st.text_input("👤 Patient Name", placeholder="Enter patient name")

food_type = st.radio(
    "🥦 Food Preference",
    ["Vegetarian", "Non-Vegetarian"]
)

uploaded_file = st.file_uploader(
    "Upload PDF / Image / TXT / CSV",
    type=["pdf", "png", "jpg", "jpeg", "txt", "csv"]
)

manual_text = st.text_area(
    "OR paste doctor prescription text",
    height=150
)

process_btn = st.button("🔍 Generate Diet Recommendation")

# -------------------- PIPELINE --------------------
if process_btn:
    if uploaded_file is None and manual_text.strip() == "":
        st.warning("Please upload a file or enter text.")
    else:
        if patient_name.strip() == "":
            patient_name = "Anonymous Patient"

        if uploaded_file:
            text = extract_text(uploaded_file)
        else:
            text = manual_text

        diet = generate_diet(text, food_type)
        formatted_output = format_output(diet, patient_name)

        st.subheader("🧾 Final Diet Plan")
        st.code(formatted_output)

        # JSON Download
        st.download_button(
            "⬇️ Download JSON",
            data=pd.Series(diet).to_json(),
            file_name=f"{patient_name}_DietPlan.json",
            mime="application/json"
        )

        # PDF Download
        pdf_file = generate_pdf(formatted_output)
        st.download_button(
            "⬇️ Download PDF",
            data=pdf_file,
            file_name=f"{patient_name}_DietPlan.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.caption("© AI-NutritionalCare | End-to-End Deployed Diet Recommendation System")
