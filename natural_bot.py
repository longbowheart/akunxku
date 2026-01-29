import os
import requests
import random
from datetime import datetime
from requests_oauthlib import OAuth1

# Kredensial
auth = OAuth1(
    os.environ.get("X_API_KEY"),
    os.environ.get("X_API_SECRET"),
    os.environ.get("X_ACCESS_TOKEN"),
    os.environ.get("X_ACCESS_SECRET")
)
MY_ID = os.environ.get("MY_USER_ID")

def get_remaining_limit():
    """Mengecek apakah kita masih punya sisa nafas jam ini"""
    try:
        url = "https://api.twitter.com/2/users/me"
        res = requests.get(url, auth=auth)
        # Mengambil info limit dari header jika tersedia
        return res.headers.get('x-rate-limit-remaining', "Unknown")
    except: return "0"

def perform_follow_back():
    """Follow back adalah interaksi paling aman dan hemat kuota"""
    try:
        url = f"https://api.twitter.com/2/users/{MY_ID}/followers"
        res = requests.get(url, auth=auth)
        if res.status_code == 200:
            followers = res.json().get("data", [])
            for f in followers[:2]: # Cukup 2 orang tiap jalan
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", 
                              auth=auth, json={"target_user_id": f['id']})
            return f"Checked {len(followers)} followers"
    except: return "Follow back idle"

if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"--- Session {now} ---")
    
    limit = get_remaining_limit()
    print(f"Current Limit Hint: {limit}")

    # 1. Lakukan aksi yang paling penting: Follow Back
    fb_status = perform_follow_back()
    
    # 2. Posting Tweet hanya jika angka random beruntung (Hanya 30% peluang)
    # Ini untuk menghemat jatah 500 tweet sebulan
    action_status = "Skipped to save quota"
    if random.random() < 0.3:
        tweet_text = f"Building in silence. {random.choice(['🚀', '🔥', '📈'])} #{random.randint(100,999)}"
        res = requests.post("https://api.twitter.com/2/tweets", auth=auth, json={"text": tweet_text})
        action_status = f"Tweeted (Status: {res.status_code})"

    # Overwrite Laporan
    with open("activity.txt", "w") as f:
        f.write(f"Time: {now}\nLimit: {limit}\nFollback: {fb_status}\nAction: {action_status}")
    
    print(f"Summary: {fb_status} | {action_status}")

# ompapaznoob
