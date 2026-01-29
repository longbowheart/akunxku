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

def get_stats():
    """Mengambil jumlah follower terbaru"""
    try:
        url = f"https://api.twitter.com/2/users/{MY_ID}?user.fields=public_metrics"
        res = requests.get(url, auth=X_AUTH, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", {})
            return data.get("public_metrics", {}).get("followers_count", 0)
    except: return "N/A"
    return "N/A"

def perform_actions():
    """Melakukan aksi organik dan mencatat jumlahnya"""
    acts = {"like": 0, "rt": 0, "tweet": 0}
    
    try:
        # Cari konten komunitas
        q = random.choice(['#Web3', '#Crypto', '#AI'])
        url = f"https://api.twitter.com/2/tweets/search/recent?query={q} -is:retweet&max_results=10"
        res = requests.get(url, auth=X_AUTH)
        
        if res.status_code == 200:
            tweets = res.json().get("data", [])
            if tweets:
                target = random.choice(tweets)
                # Sesekali Like (Peluang 70%)
                if random.random() < 0.7:
                    requests.post(f"https://api.twitter.com/2/users/{MY_ID}/likes", auth=X_AUTH, json={"tweet_id": target['id']})
                    acts["like"] += 1
                # Sesekali RT (Peluang 40%)
                if random.random() < 0.4:
                    requests.post(f"https://api.twitter.com/2/users/{MY_ID}/retweets", auth=X_AUTH, json={"tweet_id": target['id']})
                    acts["rt"] += 1

        # Posting Tweet (Peluang 30% per sesi)
        if random.random() < 0.3:
            quotes = ["Consistent growth is the goal.", "Building connections in Web3.", "Step by step."]
            tw_res = requests.post("https://api.twitter.com/2/tweets", auth=X_AUTH, json={"text": f"{random.choice(quotes)} {random.randint(1,99)}"})
            if tw_res.status_code == 201:
                acts["tweet"] += 1
                
    except: pass
    return acts

if __name__ == "__main__":
    # 1. Ambil data follower
    followers = get_stats()
    
    # 2. Jalankan aksi harian
    counts = perform_actions()
    
    # 3. Susun Laporan
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = (
        f"📊 DAILY LOG @HeartLongbow\n"
        f"👥 Follower: {followers}\n"
        f"❤️ Like Hari Ini: {counts['like']}\n"
        f"🔁 RT Hari Ini: {counts['rt']}\n"
        f"✍️ Tweet Hari Ini: {counts['tweet']}\n"
        f"⏰ Update: {now}"
    )
    
    print(report)
    notify(report)
    
    # Overwrite file aktivitas
    with open("activity.txt", "w") as f:
        f.write(report)

# ompapaznoob
