import requests
import pandas as pd

# ใส่ API Token ของคุณที่ได้จากหน้า Dashboard ของ PandaScore
API_TOKEN = "YOUR_PANDASCORE_API_TOKEN"
BASE_URL = "https://api.pandascore.co"

def get_cs2_live_matches():
    """
    ฟังก์ชันดึงข้อมูลการแข่งขัน CS2 ที่กำลังแข่งขันอยู่แบบ Real-time (Live)
    """
    url = f"{BASE_URL}/csgo/matches/running"  # CS2 ใน PandaScore ยังใช้Endpoint นำหน้าด้วย csgo หรือ cs2 ตามโครงสร้างระบบ
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        matches = response.json()
        print(f"พบแมตช์ที่กำลังแข่งอยู่ทั้งหมด: {len(matches)} แมตช์")
        return matches
    else:
        print(f"Error: {response.status_code}", response.text)
        return []

def get_upcoming_matches():
    """
    ฟังก์ชันดึงข้อมูลแมตช์ที่กำลังจะเกิดขึ้นเร็วๆ นี้ (Upcoming matches)
    เพื่อให้เรานำข้อมูลทีมมาวิเคราะห์ล่วงหน้าก่อนเรตราคาจะเปิด
    """
    url = f"{BASE_URL}/csgo/matches/upcoming"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}", response.text)
        return []

# --- ตัวอย่างการเรียกใช้งาน ---
if __name__ == "__main__":
    print("กำลังดึงข้อมูลแมตช์ CS2 จาก PandaScore...")
    live_matches = get_cs2_live_matches()
    
    for match in live_matches:
        match_name = match.get('name')
        tournament = match.get('tournament', {}).get('name')
        opponents = match.get('opponents', [])
        
        print(ทัวร์นาเมนต์: {tournament})
        print(แมตช์: {match_name})
        if len(opponents) >= 2:
            team_a = opponents[0]['opponent']['name']
            team_b = opponents[1]['opponent']['name']
            print(ระหว่าง: {team_a} vs {team_b})
        print("-" * 40)
