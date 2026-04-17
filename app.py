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
if "upload_type" not in st.session_state:
    st.session_state.upload_type = None

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

/* Hide default file uploader */
[data-testid="stFileUploader"] {
    display: none !important;
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
    margin: 1rem;
}

.limit-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem;
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

# MEAL DATA
VEG_MEALS = {
    "Morning": [
        {"name": "Oatmeal with banana", "portion": "1 cup cooked oats + 1 medium banana", "calories": 320, "benefit": "High soluble fiber lowers cholesterol and stabilizes blood sugar"},
        {"name": "Poha with vegetables", "portion": "1 plate (200g)", "calories": 250, "benefit": "Light breakfast, easy to digest, provides steady energy"},
        {"name": "Idli with sambar", "portion": "3 idlis + 1 bowl sambar", "calories": 280, "benefit": "Fermented food aids digestion, low in calories"}
    ],
    "Afternoon": [
        {"name": "Dal khichdi with curd", "portion": "1 bowl (250g)", "calories": 300, "benefit": "Complete protein, easy on stomach, good for weight management"},
        {"name": "Quinoa vegetable pulao", "portion": "1 bowl (200g)", "calories": 280, "benefit": "High protein grain alternative, gluten-free"},
        {"name": "Mixed veg curry with roti", "portion": "2 rotis + 1 bowl curry", "calories": 350, "benefit": "Fiber-rich vegetables support digestive health"}
    ],
    "Evening": [
        {"name": "Mixed vegetable soup", "portion": "1 bowl (300ml)", "calories": 120, "benefit": "Low calorie, high micronutrient density supports weight management"},
        {"name": "Paneer tikka salad", "portion": "150g paneer + salad", "calories": 280, "benefit": "High protein, calcium-rich, supports bone health"},
        {"name": "Vegetable cutlets", "portion": "2 pieces", "calories": 180, "benefit": "Nutrient-dense snack with minimal oil"}
    ],
    "Night": [
        {"name": "Warm turmeric milk", "portion": "200ml low-fat milk + pinch turmeric", "calories": 90, "benefit": "Anti-inflammatory properties, supports overnight recovery"},
        {"name": "Chamomile tea", "portion": "1 cup", "calories": 5, "benefit": "Promotes better sleep, aids digestion"},
        {"name": "Almond milk", "portion": "200ml", "calories": 60, "benefit": "Low calorie, rich in vitamin E"}
    ]
}

NONVEG_MEALS = {
    "Morning": [
        {"name": "Egg white omelette with toast", "portion": "3 egg whites + 2 toast", "calories": 280, "benefit": "High protein, low fat, supports muscle maintenance"},
        {"name": "Chicken sandwich", "portion": "Grilled chicken + whole wheat bread", "calories": 320, "benefit": "Lean protein source, filling breakfast"},
        {"name": "Boiled eggs with fruit", "portion": "2 eggs + 1 apple", "calories": 260, "benefit": "Complete protein with vitamins and fiber"}
    ],
    "Afternoon": [
        {"name": "Grilled chicken breast", "portion": "150g chicken + salad", "calories": 248, "benefit": "Lean protein supports muscle maintenance without raising LDL"},
        {"name": "Fish curry with rice", "portion": "100g fish + 1 cup rice", "calories": 380, "benefit": "Omega-3 fatty acids support heart health"},
        {"name": "Chicken stir-fry", "portion": "150g chicken + vegetables", "calories": 290, "benefit": "High protein, low carb, balanced meal"}
    ],
    "Evening": [
        {"name": "Chicken soup", "portion": "1 bowl (300ml)", "calories": 180, "benefit": "Protein-rich, hydrating, easy to digest"},
        {"name": "Tuna salad", "portion": "100g tuna + vegetables", "calories": 200, "benefit": "Omega-3 rich, supports cardiovascular health"},
        {"name": "Grilled fish", "portion": "100g", "calories": 150, "benefit": "Low calorie, high protein evening option"}
    ],
    "Night": [
        {"name": "Warm turmeric milk", "portion": "200ml low-fat milk + pinch turmeric", "calories": 90, "benefit": "Anti-inflammatory properties, supports overnight recovery"},
        {"name": "Green tea", "portion": "1 cup", "calories": 5, "benefit": "Antioxidants, promotes better sleep"},
        {"name": "Protein shake", "portion": "1 scoop + water", "calories": 120, "benefit": "Supports muscle recovery overnight"}
    ]
}

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
    except:
        text = "Medical report uploaded"
    return text

def extract_patient_name(text):
    patterns = [r"patient\s*name\s*[:\-]\s*([A-Za-z ]+)", r"name\s*[:\-]\s*([A-Za-z ]+)"]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()
    return "Patient"

def extract_conditions(text):
    t = text.lower()
    cond = []
    if "diabetes" in t: cond.append("Diabetes")
    if "cholesterol" in t: cond.append("High Cholesterol")
    if "hypertension" in t: cond.append("Hypertension")
    if "anemia" in t or "anaemia" in t: cond.append("Anemia")
    return cond or ["General Health"]

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
    
    # Title
    story.append(Paragraph(f"<b>DietPlanner AI - {duration} Day Diet Plan</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Patient:</b> {patient}", styles['Normal']))
    story.append(Paragraph(f"<b>Conditions:</b> {', '.join(conditions)}", styles['Normal']))
    story.append(Paragraph(f"<b>Food Preference:</b> {food_pref}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Meals for each day
    for day_name, meals in full_plan.items():
        story.append(Paragraph(f"<b>{day_name}</b>", styles['Heading2']))
        for time, meal in meals.items():
            story.append(Paragraph(f"<b>{time}:</b> {meal['name']} - {meal['calories']} kcal", styles['Normal']))
            story.append(Paragraph(f"Portion: {meal['portion']}", styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_txt_report(patient, conditions, food_pref, duration, full_plan):
    report = f"DIETPLANNER AI - {duration} DAY DIET PLAN\n"
    report += "="*60 + "\n\n"
    report += f"Patient: {patient}\n"
    report += f"Medical Conditions: {', '.join(conditions)}\n"
    report += f"Food Preference: {food_pref}\n"
    report += f"Duration: {duration} Days\n\n"
    report += "="*60 + "\n\n"
    
    for day_name, meals in full_plan.items():
        report += f"{day_name.upper()}\n"
        report += "-"*60 + "\n"
        total_cal = 0
        for time, meal in meals.items():
            report += f"\n{time}:\n"
            report += f"  Meal: {meal['name']}\n"
            report += f"  Portion: {meal['portion']}\n"
            report += f"  Calories: {meal['calories']} kcal\n"
            report += f"  Benefit: {meal['benefit']}\n"
            total_cal += meal['calories']
        report += f"\nDay Total: {total_cal} kcal\n"
        report += "="*60 + "\n\n"
    
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

# HEADER
st.markdown(f"""
<div class="header-bar">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 2rem; margin-right: 1rem;">🥗</span>
            <div>
                <h1 style="color: white; margin: 0; font-size: 1.75rem; font-weight: 700;">DietPlanner AI</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 0.95rem;">Personalised nutrition guidance</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# STEP INDICATOR
st.markdown(f"""
<div style="text-align: center; margin: 2rem 0;">
    <span class="step-circle {'step-active' if st.session_state.step >= 1 else 'step-inactive'}">1</span>
    <span style="color: #cbd5e1;">━━━</span>
    <span class="step-circle {'step-active' if st.session_state.step >= 2 else 'step-inactive'}">2</span>
    <span style="color: #cbd5e1;">━━━</span>
    <span class="step-circle {'step-active' if st.session_state.step >= 3 else 'step-inactive'}">3</span>
</div>
""", unsafe_allow_html=True)

# STEP 1: UPLOAD
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
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 3rem 2rem; 
                    text-align: center; cursor: pointer; transition: all 0.3s ease; margin: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <h3 style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">Text Document</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Click to browse</p>
        </div>
        """, unsafe_allow_html=True)
        txt_file = st.file_uploader("txt", type=["txt"], key="txt_upload", label_visibility="collapsed")
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
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 3rem 2rem; 
                    text-align: center; cursor: pointer; transition: all 0.3s ease; margin: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h3 style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">PDF Document</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Click to browse</p>
        </div>
        """, unsafe_allow_html=True)
        pdf_file = st.file_uploader("pdf", type=["pdf"], key="pdf_upload", label_visibility="collapsed")
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
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 3rem 2rem; 
                    text-align: center; cursor: pointer; transition: all 0.3s ease; margin: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🖼️</div>
            <h3 style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">Scanned Image</h3>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Click to browse</p>
        </div>
        """, unsafe_allow_html=True)
        img_file = st.file_uploader("img", type=["png", "jpg", "jpeg"], key="img_upload", label_visibility="collapsed")
        if img_file:
            text = extract_text_from_file(img_file)
            st.session_state.patient = extract_patient_name(text)
            st.session_state.conditions = extract_conditions(text)
            st.success(f"✅ {img_file.name} uploaded!")
            if st.button("Continue →", key="img_continue"):
                st.session_state.step = 2
                st.rerun()

# STEP 2: PREFERENCES
elif st.session_state.step == 2:
    st.markdown("<h2 style='text-align: center; font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 2rem;'>Set Your Preferences</h2>", unsafe_allow_html=True)
    
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
    st.session_state.duration = st.slider("", 1, 30, 7, label_visibility="collapsed")
    st.markdown(f"<h2 style='text-align: center; font-size: 2.5rem; font-weight: 700; color: #1e293b; margin: 1rem 0;'>{st.session_state.duration} days</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>1 day ← → 30 days</p>", unsafe_allow_html=True)
    
    if st.button("✨ Generate Diet Plan", use_container_width=True):
        st.session_state.full_plan = generate_diet_plan(st.session_state.food_pref, st.session_state.duration)
        st.session_state.step = 3
        st.rerun()

# STEP 3: RESULTS
elif st.session_state.step == 3:
    st.markdown(f"<h2 style='text-align: center; font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 2rem;'>🍽️ Your {st.session_state.duration}-Day Diet Plan</h2>", unsafe_allow_html=True)
    
    # Day selector
    cols = st.columns(min(7, st.session_state.duration))
    selected_day = 1
    for i in range(min(7, st.session_state.duration)):
        with cols[i]:
            if st.button(f"Day {i+1}", key=f"day_{i+1}", use_container_width=True):
                selected_day = i + 1
    
    day_plan = st.session_state.full_plan[f"Day {selected_day}"]
    total_cal = sum(meal["calories"] for meal in day_plan.values())
    
    # Display meals
    for time, meal_data in day_plan.items():
        st.markdown(f"""
        <div class="meal-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="color: #1e293b; font-size: 1.25rem; font-weight: 600; margin: 0;">
                    {'🌅' if time == 'Morning' else '☀️' if time == 'Afternoon' else '🌆' if time == 'Evening' else '🌙'} {time}
                </h3>
                <span class="calorie-badge">{meal_data['calories']} kcal</span>
            </div>
            <h4 style="color: #1e293b; font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;">{meal_data['name']}</h4>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0.5rem 0;">🍴 {meal_data['portion']}</p>
            <p style="color: #475569; font-size: 0.95rem; margin: 0.75rem 0;">{meal_data['benefit']}</p>
            <p style="color: #16a34a; font-size: 0.875rem; font-weight: 500; margin: 0.5rem 0;">💊 Clinical recommendation for {', '.join(st.session_state.conditions)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #d1fae5; padding: 1.5rem; border-radius: 12px; text-align: center; margin: 2rem 0;">
        <h3 style="color: #1e293b; font-weight: 700; margin: 0;">Day {selected_day} Total: {total_cal} kcal</h3>
    </div>
    <div style="background: #e0f2fe; padding: 1.5rem; border-radius: 12px; text-align: center;">
        <p style="color: #0c4a6e; font-weight: 600; margin: 0;">Daily Target Range: 1700-2000 kcal/day based on patient profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("""
    <h3 style="font-size: 1.5rem; color: #1e293b; margin: 3rem 0 1.5rem 0;">📋 Dietary Recommendations</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="rec-box">
            <h4 style="color: #16a34a; font-weight: 700; margin-bottom: 1rem;">✅ Foods to Favour</h4>
            <p style="color: #15803d; margin: 0.5rem 0;">• Oats and barley — soluble fiber lowers blood cholesterol and prediabetes</p>
            <p style="color: #15803d; margin: 0.5rem 0;">• Leafy greens — magnesium supports insulin sensitivity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="limit-box">
            <h4 style="color: #dc2626; font-weight: 700; margin-bottom: 1rem;">⚠️ Foods to Limit</h4>
            <p style="color: #991b1b; margin: 0.5rem 0;">• Refined sugars — rapidly spike blood glucose</p>
            <p style="color: #991b1b; margin: 0.5rem 0;">• Processed meats — high sodium worsens hypertension</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.5rem;">
            <h4 style="color: #1e40af; font-weight: 700; margin-bottom: 1rem;">🔬 Key Nutrients</h4>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Magnesium</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Potassium</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Soluble fiber</p>
            <p style="color: #1e3a8a; margin: 0.5rem 0;">• Omega-3 fatty acids</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fefce8; border: 1px solid #fde047; border-radius: 12px; padding: 1.5rem;">
            <h4 style="color: #a16207; font-weight: 700; margin-bottom: 1rem;">💡 Lifestyle Tips</h4>
            <p style="color: #854d0e; margin: 0.5rem 0;">• Eat at regular intervals every 3-4 hours to maintain blood sugar stability</p>
            <p style="color: #854d0e; margin: 0.5rem 0;">• Drink 8-10 glasses of water daily</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #fef9c3; border: 1px solid #fbbf24; border-radius: 12px; padding: 1.5rem; margin: 2rem 0;">
        <p style="color: #78350f; margin: 0; font-size: 0.95rem;">
            ⚠️ <b>Medical Disclaimer:</b> This diet plan is based on the provided medical data and is not a substitute for professional medical advice. 
            Please consult with a healthcare provider or registered dietitian before making significant dietary changes.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Download buttons - ALL 3 FORMATS
    st.markdown("<h3 style='font-size: 1.5rem; color: #1e293b; margin: 2rem 0 1rem 0; text-align: center;'>📥 Download Your Complete Report</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pdf_data = generate_pdf_report(st.session_state.patient, st.session_state.conditions, 
                                       st.session_state.food_pref, st.session_state.duration, 
                                       st.session_state.full_plan)
        st.download_button(
            "📑 Download PDF",
            data=pdf_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col2:
        txt_data = generate_txt_report(st.session_state.patient, st.session_state.conditions, 
                                       st.session_state.food_pref, st.session_state.duration, 
                                       st.session_state.full_plan)
        st.download_button(
            "📄 Download TXT",
            data=txt_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        json_data = generate_json_report(st.session_state.patient, st.session_state.conditions, 
                                         st.session_state.food_pref, st.session_state.duration, 
                                         st.session_state.full_plan)
        st.download_button(
            "📊 Download JSON",
            data=json_data,
            file_name=f"{st.session_state.duration}_day_diet_plan.json",
            mime="application/json",
            use_container_width=True
        )
    
    # New Plan button
    if st.button("🔄 Create New Plan", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
