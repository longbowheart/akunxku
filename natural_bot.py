import os
import requests
import random
import time
from datetime import datetime
from requests_oauthlib import OAuth1

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
    try:
        res = requests.get(f"https://api.twitter.com/2/users/me", auth=X_AUTH, timeout=10)
        return res.headers.get('x-rate-limit-remaining', "N/A")
    except: return "Check Error"

def human_delay(low=10, high=30):
    time.sleep(random.randint(low, high))

def organic_growth():
    summary = []
    try:
        # 1. FOLLBACK (Maks 5 orang)
        res_f = requests.get(f"https://api.twitter.com/2/users/{MY_ID}/followers", auth=X_AUTH)
        if res_f.status_code == 200:
            fol = res_f.json().get("data", [])[:5]
            for f in fol:
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", auth=X_AUTH, json={"target_user_id": f['id']})
                human_delay(2, 5)
            summary.append(f"Follback:{len(fol)}")

        # 2. INTERAKSI KOMUNITAS (Cari akun 100% follow back)
        queries = ['#Web3 "follow back"', '#Crypto "ifb"', 'AI "follback"']
        q = random.choice(queries)
        res_s = requests.get(f"https://api.twitter.com/2/tweets/search/recent?query={q} -is:retweet&expansions=author_id", auth=X_AUTH)
        if res_s.status_code == 200:
            t_data = res_s.json().get("data", [])
            if t_data:
                target = random.choice(t_data)
                # Like & Follow
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/likes", auth=X_AUTH, json={"tweet_id": target['id']})
                requests.post(f"https://api.twitter.com/2/users/{MY_ID}/following", auth=X_AUTH, json={"target_user_id": target['author_id']})
                summary.append(f"Hunter:Matched {q}")

    except Exception as e:
        summary.append(f"Err:{str(e)[:20]}")
    return " | ".join(summary)

if __name__ == "__main__":
    pre_l = get_limit_info()
    
    # Eksekusi aksi
    act_log = organic_growth()
    human_delay(20, 60)
    
    # Tweet hanya jika angka hoki (30% chance)
    tw_status = "Skip"
    if random.random() < 0.3:
        thoughts = ["Quality over quantity. 💎", "Networking is the new net worth. #Web3", "Staying consistent. 📈"]
        res_tw = requests.post("https://api.twitter.com/2/tweets", auth=X_AUTH, json={"text": f"{random.choice(thoughts)} {random.randint(1,99)}"})
        tw_status = "Done" if res_tw.status_code == 201 else f"Fail:{res_tw.status_code}"

    post_l = get_limit_info()
    
    report = (
        f"🛡️ SAFE-MODE REPORT @HeartLongbow\n"
        f"📉 Limit: {pre_l} -> {post_l}\n"
        f"🛠 Actions: {act_log}\n"
        f"🐦 Tweet: {tw_status}"
    )
    
    print(report)
    notify(report)
    with open("activity.txt", "w") as f: f.write(report)

# ompapaznoob
