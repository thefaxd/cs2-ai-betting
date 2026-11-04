import streamlit as st
import pandas as pd
import numpy as np
import joblib

import joblib
import numpy as np

# 1. โหลดโมเดล AI ที่เคยเทรนไว้
model = joblib.load('cs2_win_model.joblib')

def predict_match_from_api_data(team_a_stats, team_b_stats):
    """
    team_a_stats และ team_b_stats คือข้อมูลสถิติที่ดึงมาจาก API หรือฐานข้อมูล
    รูปแบบต้องตรงกับ Features ที่ใช้ตอนเทรนโมเดล
    """
    features = np.array([[
        team_a_stats['winrate_3m'],
        team_b_stats['winrate_3m'],
        team_a_stats['hltv_rating'],
        team_b_stats['hltv_rating'],
        team_a_stats['h2h_wins'],
        team_b_stats['h2h_wins']
    ]])
    
    # คำนวณความน่าจะเป็นที่ Team A จะชนะ
    prob_a = model.predict_proba(features)[0][1]
    return prob_a

# เซ็ตหน้าตาเว็บ
st.set_page_config(page_title="CS2 Value Bet AI Predictor", page_icon="🎮", layout="wide")

st.title("🎮 CS2 AI Win Predictor & Value Bet Calculator")
st.caption("เฟส 1: ระบบจำลองวิเคราะห์ความน่าจะเป็นและการลงทุน")

# โหลดโมเดล
@st.cache_resource
def load_model():
    return joblib.load('cs2_win_model.joblib')

model = load_model()

# แผงรับข้อมูล input ฝั่งซ้าย
st.sidebar.header("⚙️ ตั้งค่าการแข่งขัน & อัตราต่อรอง")

col_a, col_b = st.sidebar.columns(2)

with col_a:
    st.subheader("Team A")
    winrate_a = st.slider("Team A Winrate (3M)", 0.0, 1.0, 0.65)
    rating_a = st.number_input("Team A Rating", 0.5, 2.0, 1.12)
    h2h_a = st.number_input("Team A H2H Wins", 0, 20, 4)
    odds_a = st.number_input("Odds Team A", 1.01, 10.0, 1.95)

with col_b:
    st.subheader("Team B")
    winrate_b = st.slider("Team B Winrate (3M)", 0.0, 1.0, 0.50)
    rating_b = st.number_input("Team B Rating", 0.5, 2.0, 1.02)
    h2h_b = st.number_input("Team B H2H Wins", 0, 20, 2)
    odds_b = st.number_input("Odds Team B", 1.01, 10.0, 1.85)

bankroll = st.sidebar.number_input("💰 ทุนทั้งหมด (Bankroll)", 100, 100000, 10000, step=500)
kelly_fraction = st.sidebar.slider("🛡️ Kelly Fraction (ความเสี่ยง)", 0.1, 1.0, 0.25)

# ปุ่มคำนวณ
if st.button("🚀 วิเคราะห์ผลและหา Value Bet"):
    input_data = pd.DataFrame([{
        'team_a_winrate_3m': winrate_a,
        'team_b_winrate_3m': winrate_b,
        'team_a_hltv_rating': rating_a,
        'team_b_hltv_rating': rating_b,
        'h2h_team_a_wins': h2h_a,
        'h2h_team_b_wins': h2h_b
    }])

    # 1. คำนวณความน่าจะเป็น
    prob_a = model.predict_proba(input_data)[0][1]
    prob_b = 1.0 - prob_a

    # 2. คำนวณ Expected Value (EV)
    ev_a = (prob_a * odds_a) - 1.0
    ev_b = (prob_b * odds_b) - 1.0

    st.markdown("---")
    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.metric(label="โอกาส Team A ชนะ (AI Calculated)", value=f"{prob_a*100:.1f}%")
        st.write(f"**Odds ที่เปิดมา:** {odds_a}")
        st.write(f"**Expected Value (EV):** {ev_a*100:+.2f}%")
        
        if ev_a > 0:
            b = odds_a - 1.0
            q = 1.0 - prob_a
            kelly_stake = ((b * prob_a - q) / b) * kelly_fraction
            stake_amount = bankroll * kelly_stake
            st.success(f"✅ **VALUE BET!** ควรวางเดิมพัน Team A: **{stake_amount:.2f} บาท** ({kelly_stake*100:.2f}% ของทุน)")
        else:
            st.error("❌ **NO BET** (ไม่มี Value ชัดเจน)")

    with res_col2:
        st.metric(label="โอกาส Team B ชนะ (AI Calculated)", value=f"{prob_b*100:.1f}%")
        st.write(f"**Odds ที่เปิดมา:** {odds_b}")
        st.write(f"**Expected Value (EV):** {ev_b*100:+.2f}%")
        
        if ev_b > 0:
            b = odds_b - 1.0
            q = 1.0 - prob_b
            kelly_stake = ((b * prob_b - q) / b) * kelly_fraction
            stake_amount = bankroll * kelly_stake
            st.success(f"✅ **VALUE BET!** ควรวางเดิมพัน Team B: **{stake_amount:.2f} บาท** ({kelly_stake*100:.2f}% ของทุน)")
        else:
            st.error("❌ **NO BET** (ไม่มี Value ชัดเจน)")
