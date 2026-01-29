import os
import requests
import random
import time
from datetime import datetime
from requests_oauthlib import OAuth1

# Konfigurasi
X_AUTH = OAuth1(
    os.environ.get("X_API_KEY"), os.environ.get("X_API_SECRET"),
    os.environ.get("X_ACCESS_TOKEN"), os.environ.get("X_ACCESS_SECRET")
)
MY_ID = os.environ.get("MY_USER_ID")
NTFY_URL = f"https://ntfy.sh/{os.environ.get('NTFY_TOPIC')}"

def notify(msg):
    try: requests.post(NTFY_URL, data=msg.encode('utf-8'), timeout=15)
    except: pass

def get_limit_info():
    """Mengambil sisa limit dari header X API"""
    try:
        # Gunakan endpoint yang paling ringan untuk cek limit
        res = requests.get("https://api.twitter.com/2/users/me", auth=X_AUTH, timeout=10)
        remaining = res.headers.get('x-rate-limit-remaining', "N/A")
        reset_time = res.headers.get('x-rate-limit-reset', "N/A")
        
        if reset_time != "N/A":
            reset_dt = datetime.fromtimestamp(int(reset_time)).strftime('%H:%M:%S')
            return f"{remaining} (Reset: {reset_dt})"
        return f"{remaining}"
    except: return "Error Check"

def human_delay(min_s, max_s):
    time.sleep(random.randint(min_s, max_s))

def perform_organic_actions():
    """Aksi utama: Follback dan Hunter Komunitas"""
    results = []
    try:
        # 1. Follow Back
        res_fb = requests.get(f"https://api.twitter.com/2/users/{MY_ID}/followers", auth=X_AUTH)
        if res_fb.status_code == 200:
            for f in res_fb.json().get("data", [])[:2]:
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", auth=X_AUTH, json={"target_user_id": f['id']})
            results.append(f"Follback: {len(res_fb.json().get('data', []))[:2]} done")

        # 2. Community Hunter (Peluang 60%)
        if random.random() < 0.6:
            topics = ['#Web3 "follow"', '#Crypto "ifb"', '#AI "follback"']
            q = random.choice(topics)
            search = requests.get(f"https://api.twitter.com/2/tweets/search/recent?query={q} -is:retweet&expansions=author_id", auth=X_AUTH)
            if search.status_code == 200:
                t = random.choice(search.json().get('data', []))
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", auth=X_AUTH, json={"target_user_id": t['author_id']})
                results.append(f"Hunter: Joined {q}")
    except Exception as e:
        results.append(f"Action Error: {str(e)}")
    return " | ".join(results) if results else "No actions performed"

if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # --- STEP 1: CEK LIMIT AWAL ---
    pre_limit = get_limit_info()
    
    # --- STEP 2: EKSEKUSI AKSI ---
    action_log = perform_organic_actions()
    human_delay(10, 30)
    
    # --- STEP 3: TWEET ORGANIK (OPSIONAL) ---
    tweet_status = "Skip"
    if random.random() < 0.3:
        txt = f"Building organic connections in #Web3. {random.randint(1,99)}"
        tw_res = requests.post("https://api.twitter.com/2/tweets", auth=X_AUTH, json={"text": txt})
        tweet_status = "Success" if tw_res.status_code == 201 else f"Failed({tw_res.status_code})"

    # --- STEP 4: CEK LIMIT AKHIR ---
    post_limit = get_limit_info()

    # --- STEP 5: LAPORAN ---
    report = (
        f"📊 X-BOT REPORT @HeartLongbow\n"
        f"⏰ Time: {now}\n"
        f"📉 Limit: {pre_limit} -> {post_limit}\n"
        f"🛠 Actions: {action_log}\n"
        f"🐦 Tweet: {tweet_status}"
    )
    
    print(report)
    notify(report)
    
    # Overwrite activity.txt
    with open("activity.txt", "w") as f:
        f.write(report)

# ompapaznoob
