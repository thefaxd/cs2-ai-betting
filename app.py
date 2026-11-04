import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="CS2 HLTV Style AI Predictor", page_icon="🎮", layout="wide")

st.title("🎮 CS2 Pro Match AI Analyzer & Value Betting")
st.caption("ระบบวิเคราะห์แมตช์การแข่งขันระดับโปร พร้อมสถิติสไตล์ HLTV และคำนวณความคุ้มค่าการลงทุน")

# โหลดโมเดล AI
@st.cache_resource
def load_ai_model():
    try:
        return joblib.load('cs2_win_model.joblib')
    except:
        return None

model = load_ai_model()

# Sidebar สำหรับตั้งค่า API และเงินทุน
st.sidebar.header("⚙️ ตั้งค่าระบบ & API")
api_token = st.sidebar.text_input("PandaScore API Token", type="password", placeholder="kL5q5X-Y0MFxQ9otvf7xEKy3aUPPS4tqcrlEhu49Qh7NpTd7qn8")
bankroll = st.sidebar.number_input("💰 ทุนทั้งหมด (Bankroll - บาท)", 100, 100000, 10000, step=500)
kelly_fraction = st.sidebar.slider("🛡️ Kelly Fraction (ระดับความเสี่ยง)", 0.1, 1.0, 0.25)

# ฟังก์ชันดึงข้อมูลแมตช์จาก PandaScore API
def fetch_upcoming_matches(token):
    if not token:
        return []
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

# ดึงข้อมูลแมตช์จริง (ถ้ามี Token) ถ้าไม่มีใช้ข้อมูลจำลอง (Mock Matches)
matches_data = fetch_upcoming_matches(api_token)

if not matches_data:
    # ข้อมูลจำลอง (Mock Matches) กรณีไม่ได้ใส่ API Token เพื่อให้กดทดสอบได้ทันที
    matches_data = [
        {
            "name": "Vitality vs Natus Vincere",
            "tournament": {"name": "BLAST Premier World Final"},
            "opponents": [{"opponent": {"name": "Team Vitality"}}, {"opponent": {"name": "Natus Vincere"}}],
            "mock_stats": {
                "team_a_winrate": 0.72, "team_b_winrate": 0.65,
                "team_a_rating": 1.18, "team_b_rating": 1.12,
                "team_a_h2h": 5, "team_b_h2h": 3,
                "odds_a": 1.75, "odds_b": 2.10
            }
        },
        {
            "name": "FaZe vs G2 Esports",
            "tournament": {"name": "Intel Extreme Masters (IEM)"},
            "opponents": [{"opponent": {"name": "FaZe Clan"}}, {"opponent": {"name": "G2 Esports"}}],
            "mock_stats": {
                "team_a_winrate": 0.58, "team_b_winrate": 0.60,
                "team_a_rating": 1.08, "team_b_rating": 1.10,
                "team_a_h2h": 4, "team_b_h2h": 4,
                "odds_a": 1.90, "odds_b": 1.90
            }
        }
    ]

# --- ส่วนเลือกคู่แข่งขัน ---
st.markdown("### 🏟️ เลือกแมตช์การแข่งขันที่ต้องการวิเคราะห์")
match_names = [m.get('name', 'Unknown Match') for m in matches_data]
selected_match_name = st.selectbox("เลือกคู่แข่งขัน:", match_names)

# ค้นหาข้อมูลแมตช์ที่ถูกเลือก
selected_match = next((m for m in matches_data if m.get('name') == selected_match_name), matches_data[0])

tournament_name = selected_match.get('tournament', {}).get('name', 'Pro Tournament')
opponents = selected_match.get('opponents', [])

if len(opponents) >= 2:
    team_a_name = opponents[0]['opponent']['name']
    team_b_name = opponents[1]['opponent']['name']
else:
    team_a_name, team_b_name = "Team A", "Team B"

st.info(🏆 **ทัวร์นาเมนต์:** {tournament_name} | **แมตช์:** {team_a_name} vs {team_b_name})

# ดึงสถิติ (ถ้ามีใน mock หรือกำหนดค่าเริ่มต้นให้ปรับแต่งได้)
default_stats = selected_match.get('mock_stats', {
    "team_a_winrate": 0.60, "team_b_winrate": 0.55,
    "team_a_rating": 1.10, "team_b_rating": 1.05,
    "team_a_h2h": 3, "team_b_h2h": 2,
    "odds_a": 1.85, "odds_b": 1.95
})

st.markdown("---")
st.markdown("### 📊 สถิติเชิงลึก (HLTV Style Stats)")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🔴 {team_a_name} (Team A)")
    winrate_a = st.slider(f"Winrate 3 Months ({team_a_name})", 0.0, 1.0, float(default_stats['team_a_winrate']), key="wa")
    rating_a = st.number_input(f"HLTV Rating ({team_a_name})", 0.5, 2.0, float(default_stats['team_a_rating']), key="ra")
    h2h_a = st.number_input(f"H2H Wins ({team_a_name})", 0, 20, int(default_stats['team_a_h2h']), key="ha")
    odds_a = st.number_input(f"Decimal Odds ({team_a_name})", 1.01, 10.0, float(default_stats['odds_a']), key="oa")

with col2:
    st.subheader(f"🔵 {team_b_name} (Team B)")
    winrate_b = st.slider(f"Winrate 3 Months ({team_b_name})", 0.0, 1.0, float(default_stats['b_winrate'] if 'b_winrate' in default_stats else default_stats['team_b_winrate']), key="wb")
    rating_b = st.number_input(f"HLTV Rating ({team_b_name})", 0.5, 2.0, float(default_stats['team_b_rating']), key="rb")
    h2h_b = st.number_input(f"H2H Wins ({team_b_name})", 0, 20, int(default_stats['team_b_h2h']), key="hb")
    odds_b = st.number_input(f"Decimal Odds ({team_b_name})", 1.01, 10.0, float(default_stats['odds_b']), key="ob")

# --- ปุ่มกดวิเคราะห์ ---
st.markdown("---")
if st.button("🚀 ประเมินผลและคำนวณ Value Betting ด้วย AI", use_container_width=True):
    if model is None:
        st.error("ไม่พบไฟล์โมเดล AI (cs2_win_model.joblib) กรุณาตรวจสอบว่าอัปโหลดขึ้น GitHub เรียบร้อยแล้ว")
    else:
        input_data = pd.DataFrame([{
            'team_a_winrate_3m': winrate_a,
            'team_b_winrate_3m': winrate_b,
            'team_a_hltv_rating': rating_a,
            'team_b_hltv_rating': rating_b,
            'h2h_team_a_wins': h2h_a,
            'h2h_team_b_wins': h2h_b
        }])

        # คำนวณความน่าจะเป็นจาก AI
        prob_a = model.predict_proba(input_data)[0][1]
        prob_b = 1.0 - prob_a

        # คำนวณ Expected Value (EV)
        ev_a = (prob_a * odds_a) - 1.0
        ev_b = (prob_b * odds_b) - 1.0

        st.markdown("### 🎯 ผลการวิเคราะห์จาก AI")
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.metric(label=f"โอกาสชนะของ {team_a_name}", value=f"{prob_a*100:.1f}%")
            st.write(f"**ราคา Odds:** {odds_a} | **EV:** {ev_a*100:+.2f}%")
            
            if ev_a > 0:
                b_val = odds_a - 1.0
                q_val = 1.0 - prob_a
                kelly_stake = ((b_val * prob_a - q_val) / b_val) * kelly_fraction
                stake_amount = bankroll * kelly_stake
                st.success(f"✅ **VALUE BET!**\nควรลงทุน {team_a_name}: **{stake_amount:.2f} บาท** ({kelly_stake*100:.2f}% ของทุน)")
            else:
                st.warning("❌ **NO VALUE** (ไม่คุ้มค่าแก่การลงทุน)")

        with res_col2:
            st.metric(label=f"โอกาสชนะของ {team_b_name}", value=f"{prob_b*100:.1f}%")
            st.write(f"**ราคา Odds:** {odds_b} | **EV:** {ev_b*100:+.2f}%")
            
            if ev_b > 0:
                b_val = odds_b - 1.0
                q_val = 1.0 - prob_b
                kelly_stake = ((b_val * prob_b - q_val) / b_val) * kelly_fraction
                stake_amount = bankroll * kelly_stake
                st.success(f"✅ **VALUE BET!**\nควรลงทุน {team_b_name}: **{stake_amount:.2f} บาท** ({kelly_stake*100:.2f}% ของทุน)")
            else:
                st.warning("❌ **NO VALUE** (ไม่คุ้มค่าแก่การลงทุน)")
