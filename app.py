import streamlit as st
import random

st.set_page_config(layout="wide")

# ================== CUSTOM CSS ==================
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #f3f8ff;
}

/* Hide default */
#MainMenu, footer, header {visibility: hidden;}

/* Main container */
.main-container {
    max-width: 1100px;
    margin: auto;
}

/* Header */
.header {
    background: linear-gradient(135deg,#cfe4ff,#a9cfff);
    padding: 30px;
    border-radius: 20px;
    margin-top: 30px;
}

/* Section Title */
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 40px;
    margin-bottom: 20px;
}

/* Card */
.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

/* Pill Button */
.pill {
    display: inline-block;
    padding: 10px 25px;
    border-radius: 50px;
    background: #dbeafe;
    cursor: pointer;
    margin-right: 10px;
    font-weight: 500;
}

.pill.active {
    background: #3b82f6;
    color: white;
}

/* Generate Button */
.generate-btn button {
    background: linear-gradient(135deg,#3b82f6,#60a5fa);
    color: white;
    border-radius: 40px;
    height: 50px;
    font-weight: 600;
}

/* Meal Badge */
.kcal {
    background: #3b82f6;
    color: white;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    float: right;
}

</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>🥗 DietPlanner AI</h1>
<p>Personalised nutrition guidance</p>
</div>
""", unsafe_allow_html=True)

# ================== PREFERENCES ==================
st.markdown('<div class="section-title">Step 1: Set Preferences</div>', unsafe_allow_html=True)

diet = st.radio("Food Preference", ["Vegetarian", "Non-Vegetarian"], horizontal=True)
budget = st.radio("Budget", ["Low", "Medium", "High"], horizontal=True)
days = st.slider("Duration (Days)", 1, 30, 7)

# ================== MEAL DATABASE ==================
veg_meals = [
("Oatmeal with banana",320),
("Paneer rice bowl",450),
("Mixed vegetable soup",120),
("Turmeric milk",90),
("Poha",300),
("Dal + Roti",480),
("Veg salad",150),
("Almond milk",110),
("Upma",280),
("Rajma rice",500),
("Idli sambar",350),
("Vegetable sandwich",290)
]

nonveg_meals = [
("Boiled eggs & toast",350),
("Grilled chicken rice",520),
("Chicken soup",200),
("Milk",120),
("Fish curry rice",500),
("Egg curry",430),
("Chicken salad",280),
("Yogurt",100),
("Omelette",330),
("Chicken breast",450),
("Mutton curry",600),
("Scrambled eggs",300)
]

# ================== GENERATE ==================
if st.button("✨ Generate Diet Plan"):

    st.markdown('<div class="section-title">Predicted Condition</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Mild Anemia")
    st.progress(0.90)
    st.write("Confidence: 90%")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Health Metrics Analysis</div>', unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)

    col1.markdown('<div class="card"><b>Hemoglobin</b><br>Low<br><span style="color:red;">Abnormal</span></div>', unsafe_allow_html=True)
    col2.markdown('<div class="card"><b>BMI</b><br>High<br><span style="color:red;">Abnormal</span></div>', unsafe_allow_html=True)
    col3.markdown('<div class="card"><b>Cholesterol</b><br>Borderline<br><span style="color:red;">Risk</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">Your {days}-Day Diet Plan</div>', unsafe_allow_html=True)

    tabs = st.tabs([f"Day {i}" for i in range(1, days+1)])

    for i in range(days):
        with tabs[i]:
            if diet == "Vegetarian":
                meals = random.sample(veg_meals,4)
            else:
                meals = random.sample(nonveg_meals,4)

            total = 0
            for meal in meals:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"<b>{meal[0]}</b><span class='kcal'>{meal[1]} kcal</span>", unsafe_allow_html=True)
                total += meal[1]
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="card"><b>Day Total:</b> {total} kcal</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Dietary Recommendations</div>', unsafe_allow_html=True)

    colA,colB = st.columns(2)
    colA.markdown('<div class="card"><b>Foods to Favour</b><br>Oats<br>Leafy Greens<br>Lentils</div>', unsafe_allow_html=True)
    colB.markdown('<div class="card"><b>Foods to Limit</b><br>Refined Sugar<br>Processed Meat<br>High Sodium</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
