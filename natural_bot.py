import os
import requests
import random
import time
from datetime import datetime
from requests_oauthlib import OAuth1

# Kredensial
X_AUTH = OAuth1(
    os.environ.get("X_API_KEY"), os.environ.get("X_API_SECRET"),
    os.environ.get("X_ACCESS_TOKEN"), os.environ.get("X_ACCESS_SECRET")
)
MY_ID = os.environ.get("MY_USER_ID")
NTFY_URL = f"https://ntfy.sh/{os.environ.get('NTFY_TOPIC')}"

def notify(msg):
    try: requests.post(NTFY_URL, data=msg.encode('utf-8'), timeout=15)
    except: pass

def get_profile_data():
    """Mengambil jumlah follower dan limit dalam satu panggilan"""
    try:
        url = f"https://api.twitter.com/2/users/{MY_ID}?user.fields=public_metrics"
        res = requests.get(url, auth=X_AUTH, timeout=15)
        if res.status_code == 200:
            data = res.json().get("data", {})
            f_count = data.get("public_metrics", {}).get("followers_count", 0)
            limit = res.headers.get('x-rate-limit-remaining', "N/A")
            return f_count, limit
    except: pass
    return "N/A", "N/A"

def do_actions():
    """Melakukan aksi organik: Follback, Like, RT, Tweet"""
    stats = {"follback": 0, "like": 0, "rt": 0, "tweet": 0}
    try:
        # 1. FOLLBACK (Cek siapa yang follow tapi belum kita follow)
        res_fol = requests.get(f"https://api.twitter.com/2/users/{MY_ID}/followers", auth=X_AUTH)
        if res_fol.status_code == 200:
            for f in res_fol.json().get("data", [])[:2]: # Maks 2 per sesi
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", auth=X_AUTH, json={"target_user_id": f['id']})
                stats["follback"] += 1
        
        # 2. LIKE & RT (Cari tweet dari Following kita / Home Timeline)
        # Gunakan query simpel agar tidak boros limit
        search = requests.get(f"https://api.twitter.com/2/tweets/search/recent?query=from:HeartLongbow OR #Web3&max_results=10", auth=X_AUTH)
        if search.status_code == 200:
            tweets = search.json().get("data", [])
            if tweets:
                target = random.choice(tweets)
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/likes", auth=X_AUTH, json={"tweet_id": target['id']})
                stats["like"] = 1
                if random.random() < 0.5:
                    requests.post(f"https://api.twitter.com/2/users/{MY_ID}/retweets", auth=X_AUTH, json={"tweet_id": target['id']})
                    stats["rt"] = 1

        # 3. TWEET (Peluang 50%)
        if random.random() < 0.5:
            txt = f"Keep growing, keep building. #LFG {random.randint(10,99)}"
            tw_res = requests.post("https://api.twitter.com/2/tweets", auth=X_AUTH, json={"text": txt})
            if tw_res.status_code == 201: stats["tweet"] = 1
            
    except: pass
    return stats

if __name__ == "__main__":
    # Eksekusi aksi
    results = do_actions()
    
    # Tunggu sebentar sebelum cek profil agar data terupdate
    time.sleep(10)
    
    # Ambil data final
    f_count, limit_rem = get_profile_data()
    
    # Laporan
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = (
        f"📊 SEMI-DAILY REPORT @HeartLongbow\n"
        f"👥 Pengikut: {f_count}\n"
        f"📉 Sisa Limit: {limit_rem}\n"
        f"✅ Follback: {results['follback']}\n"
        f"❤️ Like: {results['like']} | 🔁 RT: {results['rt']}\n"
        f"✍️ Tweet: {results['tweet']}\n"
        f"⏰ Update: {now}"
    )
    
    print(report)
    notify(report)
    
    with open("activity.txt", "w") as f:
        f.write(report)

# ompapaznoob
