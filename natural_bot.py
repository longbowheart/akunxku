import os
import requests
import random
import time
from datetime import datetime
from requests_oauthlib import OAuth1

# Ambil dari Secrets yang sudah valid
X_KEYS = {
    "api_key": os.environ.get("X_API_KEY"),
    "api_secret": os.environ.get("X_API_SECRET"),
    "access_token": os.environ.get("X_ACCESS_TOKEN"),
    "access_secret": os.environ.get("X_ACCESS_SECRET"),
    "my_id": os.environ.get("MY_USER_ID")
}
NTFY_URL = f"https://ntfy.sh/{os.environ.get('NTFY_TOPIC')}"

def notify(msg):
    try: requests.post(NTFY_URL, data=msg.encode('utf-8'), timeout=15)
    except: pass

def get_auth():
    return OAuth1(X_KEYS["api_key"], X_KEYS["api_secret"], 
                  X_KEYS["access_token"], X_KEYS["access_secret"])

def create_reports(status_msg, ga_msg, err="None"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Selalu menimpa file
    with open("activity.txt", "w") as f:
        f.write(f"Last Activity: {now}\nGA Status: {ga_msg}\nLog: {err}")
    with open("status.txt", "w") as f:
        f.write(f"Timestamp: {now}\nLast Content: {status_msg}")

def hunt_early_ga():
    try:
        queries = ["FCFS giveaway", "first 100 follow", "early bird giveaway"]
        q = random.choice(queries)
        url = f"https://api.twitter.com/2/tweets/search/recent?query={q} -is:retweet&expansions=author_id&user.fields=public_metrics"
        res = requests.get(url, auth=get_auth(), timeout=15)
        
        if res.status_code != 200: return f"API Idle ({res.status_code})"

        data = res.json().get("data", [])
        users = {u["id"]: u for u in res.json().get("includes", {}).get("users", [])}
        random.shuffle(data)

        for tw in data:
            author = users.get(tw["author_id"])
            if author and author["public_metrics"]["followers_count"] > 5000:
                if "drop" in tw["text"].lower(): continue
                t_id = tw["id"]
                # Aksi Like, RT, Follow
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/likes", auth=get_auth(), json={"tweet_id": t_id}, timeout=10)
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/retweets", auth=get_auth(), json={"tweet_id": t_id}, timeout=10)
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/following", auth=get_auth(), json={"target_user_id": author["id"]}, timeout=10)
                return f"Joined GA: @{author['username']}"
        return "No suitable GA found"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Peluang 50% jalan agar tidak terdeteksi bot kaku
    if random.random() < 0.5:
        quotes = [
            "Consistency is the bridge between goals and accomplishment.",
            "Great things never come from comfort zones.",
            "Focus on being productive instead of busy.",
            "Action is the foundational key to all success.",
            "The secret of getting ahead is getting started.",
            "Stay humble, hustle hard.", "Your only limit is your mind.",
            "Make today so awesome that yesterday gets jealous.",
            "Hustle in silence, let success be your noise.",
            "Dream big, work hard, stay focused."
        ]
        
        selected = random.choice(quotes)
        err_log = "None"
        
        try:
            # Post Tweet
            st_res = requests.post("https://api.twitter.com/2/tweets", auth=get_auth(), json={"text": selected}, timeout=15)
            if st_res.status_code != 201: err_log = f"Post Failed: {st_res.status_code}"
            
            # Jeda agar terlihat manusiawi
            time.sleep(random.randint(60, 180))
            
            # Cari GA
            ga_status = hunt_early_ga()
            
            # Buat Laporan & Kirim Notif
            create_reports(selected, ga_status, err_log)
            notify(f"✅ Bot HeartLongbow Berhasil!\nPost: {st_res.status_code}\nGA: {ga_status}")
            
        except Exception as e:
            create_reports("Error", "Error", str(e))
            notify(f"⚠️ Error Bot: {str(e)}")
    else:
        print("Organic sleep mode...")

# ompapaznoob
