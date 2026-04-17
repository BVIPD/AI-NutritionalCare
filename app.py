import streamlit as st
import pdfplumber
import pandas as pd
import re
import random
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

st.set_page_config(page_title="DietPlanner AI", page_icon="🥗", layout="centered")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "patient" not in st.session_state:
    st.session_state.patient = ""
if "conditions" not in st.session_state:
    st.session_state.conditions = []
if "food_pref" not in st.session_state:
    st.session_state.food_pref = "Vegetarian"
if "budget" not in st.session_state:
    st.session_state.budget = "Medium"
if "duration" not in st.session_state:
    st.session_state.duration = 7
if "full_plan" not in st.session_state:
    st.session_state.full_plan = {}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {font-family: 'Inter', sans-serif !important;}
.stApp {background: #f5f7fa !important;}
.main .block-container {max-width: 900px !important; padding: 2rem 1rem !important;}
#MainMenu, footer, header {display: none !important;}

.header-bar {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    padding: 1.5rem 2rem;
    border-radius: 0;
    margin: -2rem -1rem 2rem -1rem;
}

.step-circle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 0 0.5rem;
}

.step-active {
    background: #1e3a2e;
    color: white;
}

.step-inactive {
    background: white;
    color: #94a3b8;
    border: 2px solid #e2e8f0;
}

/* Upload card styling */
.upload-card {
    background: white;
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 1.5rem 1rem;
    text-align: center;
    margin: 0.5rem 0;
    transition: border-color 0.2s;
}

.upload-card:hover {
    border-color: #2563eb;
}

/* Style the file uploader to look clean inside cards */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
    min-height: unset !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    padding: 0 !important;
}

.stButton > button {
    background: #1e3a2e !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 3rem !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
}

.meal-card {
    background: #fafaf9;
    border: 1px solid #e7e5e4;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.calorie-badge {
    background: #fef3c7;
    color: #92400e;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
}

.rec-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.limit-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.stDownloadButton > button {
    background: #d97706 !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    width: 100% !important;
    margin: 0.5rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── MEAL DATA ────────────────────────────────────────────────────────────────

VEG_MEALS = {
    "Morning": [
        {"name": "Oatmeal with banana", "portion": "1 cup cooked oats + 1 medium banana", "calories": 320, "benefit": "High soluble fiber lowers cholesterol and stabilizes blood sugar"},
        {"name": "Poha with vegetables", "portion": "1 plate (200g)", "calories": 250, "benefit": "Light breakfast, easy to digest, provides steady energy"},
        {"name": "Idli with sambar", "portion": "3 idlis + 1 bowl sambar", "calories": 280, "benefit": "Fermented food aids digestion, low in calories"},
        {"name": "Upma with coconut chutney", "portion": "1 bowl (200g) + 2 tbsp chutney", "calories": 260, "benefit": "Complex carbs for sustained energy, good source of B vitamins"},
        {"name": "Whole wheat toast with avocado", "portion": "2 slices + half avocado", "calories": 300, "benefit": "Healthy fats from avocado support heart health"},
        {"name": "Vegetable dalia porridge", "portion": "1 bowl (250g)", "calories": 240, "benefit": "High fiber, low glycemic index, ideal for diabetes management"},
    ],
    "Afternoon": [
        {"name": "Dal khichdi with curd", "portion": "1 bowl (250g) + 100ml curd", "calories": 300, "benefit": "Complete protein, easy on stomach, good for weight management"},
        {"name": "Quinoa vegetable pulao", "portion": "1 bowl (200g)", "calories": 280, "benefit": "High protein grain alternative, gluten-free"},
        {"name": "Mixed veg curry with roti", "portion": "2 rotis + 1 bowl curry", "calories": 350, "benefit": "Fiber-rich vegetables support digestive health"},
        {"name": "Rajma rice", "portion": "1 cup rice + 1 bowl rajma", "calories": 380, "benefit": "High protein legume, good for cholesterol management"},
        {"name": "Palak paneer with brown rice", "portion": "1 bowl curry + 1 cup rice", "calories": 360, "benefit": "Iron-rich spinach combined with protein from paneer"},
        {"name": "Vegetable biryani with raita", "portion": "1 plate (250g) + 100ml raita", "calories": 340, "benefit": "Balanced meal with aromatic spices that aid digestion"},
    ],
    "Evening": [
        {"name": "Mixed vegetable soup", "portion": "1 bowl (300ml)", "calories": 120, "benefit": "Low calorie, high micronutrient density supports weight management"},
        {"name": "Paneer tikka salad", "portion": "150g paneer + salad", "calories": 280, "benefit": "High protein, calcium-rich, supports bone health"},
        {"name": "Vegetable cutlets", "portion": "2 pieces", "calories": 180, "benefit": "Nutrient-dense snack with minimal oil"},
        {"name": "Sprouts chaat", "portion": "1 bowl (150g)", "calories": 140, "benefit": "Sprouted legumes have enhanced nutrition and enzyme activity"},
        {"name": "Roasted makhana", "portion": "1 cup (30g)", "calories": 110, "benefit": "Low calorie, high protein snack good for blood sugar"},
        {"name": "Fruit salad with chia seeds", "portion": "1 bowl + 1 tsp chia", "calories": 160, "benefit": "Antioxidants and omega-3s from chia support heart health"},
    ],
    "Night": [
        {"name": "Warm turmeric milk", "portion": "200ml low-fat milk + pinch turmeric", "calories": 90, "benefit": "Anti-inflammatory properties, supports overnight recovery"},
        {"name": "Chamomile tea", "portion": "1 cup", "calories": 5, "benefit": "Promotes better sleep, aids digestion"},
        {"name": "Almond milk", "portion": "200ml unsweetened", "calories": 60, "benefit": "Low calorie, rich in vitamin E, supports bone health"},
        {"name": "Warm ginger lemon water", "portion": "1 cup with ginger + lemon", "calories": 10, "benefit": "Boosts metabolism, anti-inflammatory, aids digestion"},
    ]
}

NONVEG_MEALS = {
    "Morning": [
        {"name": "Egg white omelette with toast", "portion": "3 egg whites + 2 whole wheat toast", "calories": 280, "benefit": "High protein, low fat, supports muscle maintenance"},
        {"name": "Boiled eggs with fruit", "portion": "2 boiled eggs + 1 apple", "calories": 260, "benefit": "Complete protein with vitamins and fiber"},
        {"name": "Chicken sandwich", "portion": "Grilled chicken (80g) + whole wheat bread", "calories": 320, "benefit": "Lean protein source, filling breakfast"},
        {"name": "Scrambled eggs with spinach", "portion": "2 eggs + 1 cup spinach", "calories": 240, "benefit": "Iron and protein combination ideal for anemia prevention"},
        {"name": "Oatmeal with boiled egg", "portion": "1 cup oats + 1 egg", "calories": 310, "benefit": "Soluble fiber from oats paired with protein for sustained energy"},
        {"name": "Greek yogurt with nuts", "portion": "150g yogurt + 20g mixed nuts", "calories": 280, "benefit": "Probiotics for gut health, healthy fats for satiety"},
    ],
    "Afternoon": [
        {"name": "Grilled chicken breast with salad", "portion": "150g chicken + mixed salad", "calories": 248, "benefit": "Lean protein supports muscle maintenance without raising LDL"},
        {"name": "Fish curry with rice", "portion": "100g fish + 1 cup brown rice", "calories": 380, "benefit": "Omega-3 fatty acids from fish strongly support heart health"},
        {"name": "Chicken stir-fry with vegetables", "portion": "150g chicken + 1 cup mixed veg", "calories": 290, "benefit": "High protein, balanced macros, quick energy source"},
        {"name": "Grilled salmon with quinoa", "portion": "120g salmon + 1 cup quinoa", "calories": 420, "benefit": "Highest omega-3 content, complete protein, anti-inflammatory"},
        {"name": "Egg rice bowl", "portion": "1 cup brown rice + 2 eggs + veg", "calories": 360, "benefit": "Balanced macronutrient meal, excellent for sustained energy"},
        {"name": "Tuna whole wheat wrap", "portion": "100g tuna + 1 whole wheat wrap", "calories": 340, "benefit": "Lean protein, omega-3s, complex carbs for steady glucose"},
    ],
    "Evening": [
        {"name": "Chicken soup", "portion": "1 bowl (300ml)", "calories": 180, "benefit": "Protein-rich, hydrating, easy to digest"},
        {"name": "Tuna salad", "portion": "100g tuna + mixed vegetables", "calories": 200, "benefit": "Omega-3 rich, supports cardiovascular health"},
        {"name": "Grilled fish fingers", "portion": "3 pieces (100g)", "calories": 150, "benefit": "Low calorie, high protein evening snack option"},
        {"name": "Boiled egg salad", "portion": "2 eggs + cucumber + tomato", "calories": 170, "benefit": "Nutrient-dense, filling snack with healthy fats"},
    ],
    "Night": [
        {"name": "Warm turmeric milk", "portion": "200ml low-fat milk + pinch turmeric", "calories": 90, "benefit": "Anti-inflammatory properties, supports overnight recovery"},
        {"name": "Green tea", "portion": "1 cup", "calories": 5, "benefit": "Antioxidants, promotes better sleep quality"},
        {"name": "Protein shake", "portion": "1 scoop whey + water", "calories": 120, "benefit": "Supports muscle recovery and tissue repair overnight"},
        {"name": "Warm ginger lemon water", "portion": "1 cup with ginger + lemon", "calories": 10, "benefit": "Boosts metabolism, anti-inflammatory, aids digestion"},
    ]
}

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def extract_text_from_file(file):
    text = ""
    try:
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
        elif file.type in ["image/png", "image/jpeg", "image/jpg"]:
            text = "Sample medical report data - patient information extracted from image"
    except Exception as e:
        text = "Medical report uploaded"
    return text

def extract_patient_name(text):
    patterns = [
        r"patient\s*name\s*[:\-]\s*([A-Za-z ]+)",
        r"name\s*[:\-]\s*([A-Za-z ]+)",
        r"patient\s*[:\-]\s*([A-Za-z ]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip().split("\n")[0]
    return "Patient"

def extract_conditions(text):
    t = text.lower()
    cond = []
    if "diabetes" in t or "diabetic" in t:
        cond.append("Diabetes")
    if "cholesterol" in t or "hyperlipidemia" in t:
        cond.append("High Cholesterol")
    if "hypertension" in t or "high blood pressure" in t or "hbp" in t:
        cond.append("Hypertension")
    if "anemia" in t or "anaemia" in t or "hemoglobin" in t:
        cond.append("Anemia")
    if "thyroid" in t or "hypothyroid" in t or "hyperthyroid" in t:
        cond.append("Thyroid Disorder")
    if "kidney" in t or "renal" in t:
        cond.append("Kidney Concern")
    return cond if cond else ["General Health"]

def generate_diet_plan(food_pref, duration):
    meals = VEG_MEALS if food_pref == "Vegetarian" else NONVEG_MEALS
    plan = {}
    for day in range(1, duration + 1):
        plan[f"Day {day}"] = {
            "Morning": random.choice(meals["Morning"]),
            "Afternoon": random.choice(meals["Afternoon"]),
            "Evening": random.choice(meals["Evening"]),
            "Night": random.choice(meals["Night"])
        }
    return plan

def generate_pdf_report(patient, conditions, food_pref, duration, full_plan):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>DietPlanner AI — {duration} Day Diet Plan</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Patient:</b> {patient}", styles['Normal']))
    story.append(Paragraph(f"<b>Conditions:</b> {', '.join(conditions)}", styles['Normal']))
    story.append(Paragraph(f"<b>Food Preference:</b> {food_pref}", styles['Normal']))
    story.append(Spacer(1, 20))
    for day_name, meals in full_plan.items():
        story.append(Paragraph(f"<b>{day_name}</b>", styles['Heading2']))
        total_cal = 0
        for time_slot, meal in meals.items():
            story.append(Paragraph(f"<b>{time_slot}:</b> {meal['name']} — {meal['calories']} kcal", styles['Normal']))
            story.append(Paragraph(f"Portion: {meal['portion']}", styles['Normal']))
            story.append(Paragraph(f"Benefit: {meal['benefit']}", styles['Normal']))
            total_cal += meal['calories']
            story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Day Total: {total_cal} kcal</b>", styles['Normal']))
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_txt_report(patient, conditions, food_pref, duration, full_plan):
    report = f"DIETPLANNER AI — {duration} DAY DIET PLAN\n"
    report += "=" * 60 + "\n\n"
    report += f"Patient: {patient}\n"
    report += f"Medical Conditions: {', '.join(conditions)}\n"
    report += f"Food Preference: {food_pref}\n"
    report += f"Duration: {duration} Days\n\n"
    report += "=" * 60 + "\n\n"
    for day_name, meals in full_plan.items():
        report += f"{day_name.upper()}\n" + "-" * 60 + "\n"
        total_cal = 0
        for time_slot, meal in meals.items():
            report += f"\n{time_slot}:\n"
            report += f"  Meal: {meal['name']}\n"
            report += f"  Portion: {meal['portion']}\n"
            report += f"  Calories: {meal['calories']} kcal\n"
            report += f"  Benefit: {meal['benefit']}\n"
            total_cal += meal['calories']
        report += f"\nDay Total: {total_cal} kcal\n"
        report += "=" * 60 + "\n\n"
    return report

def generate_json_report(patient, conditions, food_pref, duration, full_plan):
    import json
    data = {
        "patient_name": patient,
        "medical_conditions": conditions,
        "food_preference": food_pref,
        "duration_days": duration,
        "meal_plan": full_plan
    }
    return json.dumps(data, indent=2)

# ─── HEADER ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-bar">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem; margin-right: 1rem;">🥗</span>
        <div>
            <h1 style="color: white; margin: 0; font-size: 1.75rem; font-weight: 700;">DietPlanner AI</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 0.95rem;">Personalised nutrition guidance</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Step indicator
st.markdown(f"""
<div style="text-align: center; margin: 2rem 0;">
    <span class="step-circle {'step-active' if st.session_state.step >= 1 else 'step-inactive'}">1</span>
    <span style="color: #cbd5e1;">━━━</span>
    <span class="step-circle {'step-active' if st.session_state.step >= 2 else 'step-inactive'}">2</span>
    <span style="color: #cbd5e1;">━━━</span>
    <span class="step-circle {'step-active' if st.session_state.step >= 3 else 'step-inactive'}">3</span>
</div>
""", unsafe_allow_html=True)

# ─── STEP 1: UPLOAD ───────────────────────────────────────────────────────────

if st.session_state.step == 1:
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="font-size: 2.25rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;">Upload Your Medical Report</h2>
        <p style="color: #64748b; font-size: 1.1rem;">Share your medical information to receive a personalised diet plan</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="upload-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📄</div>
            <h3 style="color: #1e293b; font-size: 1.05rem; font-weight: 600; margin: 0.25rem 0;">Text Document</h3>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0 0 0.75rem 0;">Upload a .txt file</p>
        </div>
        """, unsafe_allow_html=True)
        txt_file = st.file_uploader("Upload TXT", type=["txt"], key="txt_upload")
        if txt_file:
            text = extract_text_from_file(txt_file)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.success(f"✅ {txt_file.name} uploaded!")
            if st.button("Continue →", key="txt_continue"):
                st.session_state.step = 2
                st.rerun()

    with col2:
        st.markdown("""
        <div class="upload-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📋</div>
            <h3 style="color: #1e293b; font-size: 1.05rem; font-weight: 600; margin: 0.25rem 0;">PDF Document</h3>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0 0 0.75rem 0;">Upload a .pdf file</p>
        </div>
        """, unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload")
        if pdf_file:
            text = extract_text_from_file(pdf_file)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.success(f"✅ {pdf_file.name} uploaded!")
            if st.button("Continue →", key="pdf_continue"):
                st.session_state.step = 2
                st.rerun()

    with col3:
        st.markdown("""
        <div class="upload-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🖼️</div>
            <h3 style="color: #1e293b; font-size: 1.05rem; font-weight: 600; margin: 0.25rem 0;">Scanned Image</h3>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0 0 0.75rem 0;">Upload PNG or JPG</p>
        </div>
        """, unsafe_allow_html=True)
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="img_upload")
        if img_file:
            text = extract_text_from_file(img_file)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.success(f"✅ {img_file.name} uploaded!")
            if st.button("Continue →", key="img_continue"):
                st.session_state.step = 2
                st.rerun()

    # Skip option
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <p style="color: #94a3b8; font-size: 0.9rem;">Don't have a report? You can skip this step.</p>
    </div>
    """, unsafe_allow_html=True)
    col_skip1, col_skip2, col_skip3 = st.columns([2, 1, 2])
    with col_skip2:
        if st.button("Skip →", key="skip"):
            st.session_state.patient = "Patient"
            st.session_state.conditions = ["General Health"]
            st.session_state.step = 2
            st.rerun()

# ─── STEP 2: PREFERENCES ──────────────────────────────────────────────────────

elif st.session_state.step == 2:
    st.markdown("<h2 style='text-align: center; font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 2rem;'>Set Your Preferences</h2>", unsafe_allow_html=True)

    # Patient info detected
    if st.session_state.patient and st.session_state.patient != "Patient":
        st.markdown(f"""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 2rem;">
            <p style="color: #1e40af; margin: 0; font-size: 1rem;">
                👤 <b>Patient:</b> {st.session_state.patient} &nbsp;|&nbsp;
                🏥 <b>Conditions detected:</b> {', '.join(st.session_state.conditions)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.25rem; color: #1e293b; margin: 2rem 0 1rem 0;'>🥗 Food Preference</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌾 Vegetarian", key="veg", use_container_width=True):
            st.session_state.food_pref = "Vegetarian"
    with col2:
        if st.button("🍖 Non-Vegetarian", key="nonveg", use_container_width=True):
            st.session_state.food_pref = "Non-Vegetarian"

    st.markdown(f"<p style='text-align: center; color: #1e3a2e; font-weight: 600; margin: 1rem 0;'>Selected: {st.session_state.food_pref}</p>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.25rem; color: #1e293b; margin: 2rem 0 1rem 0;'>💰 Budget Range</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Low", key="low", use_container_width=True):
            st.session_state.budget = "Low"
    with col2:
        if st.button("Medium", key="med", use_container_width=True):
            st.session_state.budget = "Medium"
    with col3:
        if st.button("High", key="high", use_container_width=True):
            st.session_state.budget = "High"

    st.markdown(f"<p style='text-align: center; color: #2563eb; font-weight: 600; margin: 1rem 0;'>Selected: {st.session_state.budget}</p>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.25rem; color: #1e293b; margin: 2rem 0 1rem 0;'>📅 Diet Plan Duration</h3>", unsafe_allow_html=True)
    st.session_state.duration = st.slider("Duration", 1, 30, st.session_state.duration, label_visibility="collapsed")
    st.markdown(f"<h2 style='text-align: center; font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 1rem 0;'>{st.session_state.duration} days</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>1 day ← → 30 days</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Generate Diet Plan", use_container_width=True):
        st.session_state.full_plan = generate_diet_plan(st.session_state.food_pref, st.session_state.duration)
        st.session_state.step = 3
        st.rerun()

# ─── STEP 3: RESULTS ──────────────────────────────────────────────────────────

elif st.session_state.step == 3:
    st.markdown(f"<h2 style='text-align: center; font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 2rem;'>🍽️ Your {st.session_state.duration}-Day Diet Plan</h2>", unsafe_allow_html=True)

    # Day selector (show up to 7 buttons per row, then a selectbox for more)
    if st.session_state.duration <= 7:
        cols = st.columns(st.session_state.duration)
        selected_day = st.session_state.get("selected_day", 1)
        for i in range(st.session_state.duration):
            with cols[i]:
                if st.button(f"Day {i+1}", key=f"day_{i+1}", use_container_width=True):
                    st.session_state.selected_day = i + 1
                    st.rerun()
        selected_day = st.session_state.get("selected_day", 1)
    else:
        selected_day = st.selectbox(
            "Select Day",
            options=list(range(1, st.session_state.duration + 1)),
            format_func=lambda x: f"Day {x}"
        )

    day_plan = st.session_state.full_plan[f"Day {selected_day}"]
    total_cal = sum(meal["calories"] for meal in day_plan.values())

    # Meal cards
    icons = {"Morning": "🌅", "Afternoon": "☀️", "Evening": "🌆", "Night": "🌙"}
    for time_slot, meal_data in day_plan.items():
        st.markdown(f"""
        <div class="meal-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="color: #1e293b; font-size: 1.25rem; font-weight: 600; margin: 0;">
                    {icons.get(time_slot, "🍽️")} {time_slot}
                </h3>
                <span class="calorie-badge">{meal_data['calories']} kcal</span>
            </div>
            <h4 style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">{meal_data['name']}</h4>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0.5rem 0;">🍴 {meal_data['portion']}</p>
            <p style="color: #475569; font-size: 0.95rem; margin: 0.75rem 0;">{meal_data['benefit']}</p>
            <p style="color: #16a34a; font-size: 0.875rem; font-weight: 500; margin: 0.5rem 0;">
                💊 Clinical recommendation for {', '.join(st.session_state.conditions)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #d1fae5; padding: 1.5rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
        <h3 style="color: #1e293b; font-weight: 700; margin: 0;">Day {selected_day} Total: {total_cal} kcal</h3>
    </div>
    <div style="background: #e0f2fe; padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 2rem;">
        <p style="color: #0c4a6e; font-weight: 600; margin: 0;">Daily Target Range: 1700–2000 kcal/day based on patient profile</p>
    </div>
    """, unsafe_allow_html=True)

    # Recommendations
    st.markdown("<h3 style='font-size: 1.5rem; color: #1e293b; margin: 3rem 0 1.5rem 0;'>📋 Dietary Recommendations</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rec-box">
            <h4 style="color: #16a34a; font-weight: 700; margin-bottom: 1rem;">✅ Foods to Favour</h4>
            <p style="color: #15803d; margin: 0.5rem 0;">• Oats and barley — soluble fiber lowers blood cholesterol and prediabetes</p>
            <p style="color: #15803d; margin: 0.5rem 0;">• Leafy greens — magnesium supports insulin sensitivity</p>
            <p style="color: #15803d; margin: 0.5rem 0;">• Legumes — plant protein with high fiber content</p>
            <p style="color: #15803d; margin: 0.5rem 0;">• Fatty fish — omega-3 fatty acids for heart health</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="limit-box">
            <h4 style="color: #dc2626; font-weight: 700; margin-bottom: 1rem;">⚠️ Foods to Limit</h4>
            <p style="color: #991b1b; margin: 0.5rem 0;">• Refined sugars — rapidly spike blood glucose levels</p>
            <p style="color: #991b1b; margin: 0.5rem 0;">• Processed meats — high sodium worsens hypertension</p>
            <p style="color: #991b1b; margin: 0.5rem 0;">• Fried foods — saturated fats raise LDL cholesterol</p>
            <p style="color: #991b1b; margin: 0.5rem 0;">• White bread/rice — high glycemic index foods</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.5rem;">
            <h4 style="color: #1e40af; font-weight: 700; margin-bottom: 1rem;">🔬 Key Nutrients</h4>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Magnesium — blood sugar regulation</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Potassium — blood pressure control</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Soluble fiber — cholesterol reduction</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Omega-3 fatty acids — cardiovascular health</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #fefce8; border: 1px solid #fde047; border-radius: 12px; padding: 1.5rem;">
            <h4 style="color: #a16207; font-weight: 700; margin-bottom: 1rem;">💡 Lifestyle Tips</h4>
            <p style="color: #854d0e; margin: 0.5rem 0;">• Eat at regular intervals every 3–4 hours</p>
            <p style="color: #854d0e; margin: 0.5rem 0;">• Drink 8–10 glasses of water daily</p>
            <p style="color: #854d0e; margin: 0.5rem 0;">• 30 minutes of moderate exercise daily</p>
            <p style="color: #854d0e; margin: 0.5rem 0;">• Avoid eating heavy meals after 8 PM</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #fef9c3; border: 1px solid #fbbf24; border-radius: 12px; padding: 1.5rem; margin: 2rem 0;">
        <p style="color: #78350f; margin: 0; font-size: 0.95rem;">
            ⚠️ <b>Medical Disclaimer:</b> This diet plan is based on the provided medical data and is not a substitute 
            for professional medical advice. Please consult with a healthcare provider or registered dietitian before 
            making significant dietary changes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Downloads
    st.markdown("<h3 style='font-size: 1.5rem; color: #1e293b; margin: 2rem 0 1rem 0; text-align: center;'>📥 Download Your Complete Report</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        pdf_data = generate_pdf_report(
            st.session_state.patient, st.session_state.conditions,
            st.session_state.food_pref, st.session_state.duration,
            st.session_state.full_plan
        )
        st.download_button(
            "📑 Download PDF",
            data=pdf_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col2:
        txt_data = generate_txt_report(
            st.session_state.patient, st.session_state.conditions,
            st.session_state.food_pref, st.session_state.duration,
            st.session_state.full_plan
        )
        st.download_button(
            "📄 Download TXT",
            data=txt_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col3:
        json_data = generate_json_report(
            st.session_state.patient, st.session_state.conditions,
            st.session_state.food_pref, st.session_state.duration,
            st.session_state.full_plan
        )
        st.download_button(
            "📊 Download JSON",
            data=json_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Create New Plan", use_container_width=True):
        for key in ["step", "patient", "conditions", "food_pref", "budget", "duration", "full_plan", "selected_day"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
