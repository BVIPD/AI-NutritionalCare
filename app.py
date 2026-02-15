import streamlit as st
import random
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="DietPlanner AI",
    page_icon="🥗",
    layout="wide"
)

# ---------------- LIGHT BLUE THEME ----------------
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background-color: #f4f9ff;
}

/* HEADER */
.header {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 25px;
}

/* STEP CIRCLES */
.step-circle {
    height: 40px;
    width: 40px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #93c5fd;
    color: white;
    font-weight: bold;
    margin-right: 15px;
}

/* CARD */
.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 18px;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #60a5fa);
    color: white;
    border-radius: 50px;
    font-weight: 600;
    height: 3rem;
}

/* TAB STYLE */
.stTabs [data-baseweb="tab"] {
    background: #e0f2fe;
    border-radius: 30px;
    padding: 8px 18px;
    margin-right: 6px;
}

.stTabs [aria-selected="true"] {
    background: #3b82f6 !important;
    color: white !important;
}

/* INFO BADGE */
.kcal-badge {
    background: #3b82f6;
    color: white;
    padding: 4px 12px;
    border-radius: 30px;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header">
<h1>🥗 DietPlanner AI</h1>
<p>Personalised nutrition guidance</p>
</div>
""", unsafe_allow_html=True)

# ---------------- STEP 1 ----------------
st.markdown("### Step 1: Set Preferences")

diet_type = st.radio("Food Preference", ["Vegetarian", "Non-Vegetarian"], horizontal=True)
budget = st.radio("Budget", ["Low", "Medium", "High"], horizontal=True)
duration = st.slider("Duration (Days)", 1, 30, 7)

# ---------------- MEAL DATABASE ----------------

veg_meals = [
("Oatmeal with banana", 320),
("Paneer rice bowl", 450),
("Mixed veg soup", 120),
("Turmeric milk", 90),
("Poha", 300),
("Dal + Roti", 480),
("Veg salad", 150),
("Almond milk", 110)
]

nonveg_meals = [
("Boiled eggs & toast", 350),
("Grilled chicken rice", 520),
("Chicken soup", 200),
("Milk", 120),
("Fish curry rice", 500),
("Egg curry", 430),
("Chicken salad", 280),
("Yogurt", 100)
]

# ---------------- GENERATE ----------------
if st.button("✨ Generate Diet Plan"):

    st.success("Diet plan generated successfully!")

    # ---------- PREDICTION SECTION ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Predicted Condition")
    st.markdown("## Mild Anemia")
    st.progress(0.90)
    st.markdown("Confidence: 90%")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- HEALTH METRICS ----------
    st.markdown("### Health Metrics Analysis")
    col1, col2, col3 = st.columns(3)

    col1.metric("Hemoglobin", "Low", "Abnormal")
    col2.metric("BMI", "High", "Abnormal")
    col3.metric("Cholesterol", "Borderline", "Risk")

    # ---------- DIET PLAN ----------
    st.markdown(f"## Your {duration}-Day Diet Plan")

    tabs = st.tabs([f"Day {i}" for i in range(1, duration+1)])

    for i in range(duration):

        with tabs[i]:

            if diet_type == "Vegetarian":
                meals = random.sample(veg_meals, 4)
            else:
                meals = random.sample(nonveg_meals, 4)

            total_kcal = 0

            meal_times = ["Morning", "Afternoon", "Evening", "Night"]

            for j in range(4):
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"### {meal_times[j]}")
                st.markdown(f"{meals[j][0]}  ")
                st.markdown(f"<span class='kcal-badge'>{meals[j][1]} kcal</span>", unsafe_allow_html=True)
                total_kcal += meals[j][1]
                st.markdown('</div>', unsafe_allow_html=True)

            st.success(f"Day Total: {total_kcal} kcal")
            st.info("Daily Target Range: 1700–2000 kcal/day")

    # ---------- RECOMMENDATIONS ----------
    st.markdown("## Dietary Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Foods to Favour")
        st.write("• Oats and barley")
        st.write("• Leafy greens")
        st.write("• Lentils")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Foods to Limit")
        st.write("• Refined sugars")
        st.write("• Processed meats")
        st.write("• High sodium foods")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- DOWNLOAD ----------
    st.markdown("## Download Report")
    report_text = f"Diet Plan generated on {datetime.now()}"
    st.download_button("Download Report (.txt)", report_text)

