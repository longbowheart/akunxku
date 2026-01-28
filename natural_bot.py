import os
import requests
import random
import time
from datetime import datetime
from requests_oauthlib import OAuth1

# Kredensial
X_KEYS = {
    "api_key": os.environ.get("X_API_KEY"),
    "api_secret": os.environ.get("X_API_SECRET"),
    "access_token": os.environ.get("X_ACCESS_TOKEN"),
    "access_secret": os.environ.get("X_ACCESS_SECRET"),
    "my_id": os.environ.get("MY_USER_ID")
}
NTFY_URL = f"https://ntfy.sh/{os.environ.get('NTFY_TOPIC')}"

def notify(msg):
    try: requests.post(NTFY_URL, data=msg.encode('utf-8'), timeout=10)
    except: print("Gagal mengirim notifikasi ntfy")

def get_auth():
    return OAuth1(X_KEYS["api_key"], X_KEYS["api_secret"], 
                  X_KEYS["access_token"], X_KEYS["access_secret"])

def create_reports(status_msg, ga_msg, error_log="None"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("activity.txt", "w") as f:
        f.write(f"Last Activity: {now}\nGA Status: {ga_msg}\nError Log: {error_log}")
    with open("status.txt", "w") as f:
        f.write(f"Timestamp: {now}\nLast Tweet: {status_msg}")

def hunt_early_ga():
    try:
        queries = ["FCFS giveaway", "first 100 follow", "early bird giveaway"]
        q = random.choice(queries)
        url = f"https://api.twitter.com/2/tweets/search/recent?query={q} -is:retweet&expansions=author_id&user.fields=public_metrics"
        res = requests.get(url, auth=get_auth(), timeout=15)
        
        if res.status_code != 200: return f"API Error {res.status_code}"

        data = res.json().get("data", [])
        users = {u["id"]: u for u in res.json().get("includes", {}).get("users", [])}
        random.shuffle(data)

        for tw in data:
            author = users.get(tw["author_id"])
            if author and author["public_metrics"]["followers_count"] > 10000:
                if "drop" in tw["text"].lower(): continue 
                t_id = tw["id"]
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/likes", auth=get_auth(), json={"tweet_id": t_id}, timeout=15)
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/retweets", auth=get_auth(), json={"tweet_id": t_id}, timeout=15)
                requests.post(f"https://api.twitter.com/2/users/{X_KEYS['my_id']}/following", auth=get_auth(), json={"target_user_id": author["id"]}, timeout=15)
                return f"Joined GA: @{author['username']}"
        return "No legit GA found in this cycle"
    except Exception as e:
        return f"Hunt Error: {str(e)}"

if __name__ == "__main__":
    # Peluang 50% jalan (lebih sering agar robust)
    if random.random() < 0.5:
        selected_quote = "System Idle"
        ga_msg = "No Action"
        err_msg = "None"
        
        try:
            eng_quotes = [
                "Consistency is key.", "Success is a habit.", "Focus on the goal.", 
                "Keep moving forward.", "Action creates opportunity.", "Stay humble, hustle hard.",
                "Quality over quantity.", "The best is yet to come.", "Do it with passion.",
                "Discipline equals freedom.", "Dream big, act fast.", "Stay focused and extra sparkly.",
                "Hard work pays off.", "Work in silence, let success speak.", "Progress is progress.",
                "Be better than yesterday.", "Mindset is everything.", "Make it happen.",
                "Don't wish for it, work for it.", "Everything is possible."
            ]
            selected_quote = random.choice(eng_quotes)
            st_res = requests.post("https://api.twitter.com/2/tweets", auth=get_auth(), json={"text": selected_quote}, timeout=15)
            
            if st_res.status_code != 201:
                err_msg = f"Tweet Failed: {st_res.status_code}"
            
            time.sleep(random.randint(100, 300))
            ga_msg = hunt_early_ga()
            
            notify(f"✅ Bot Status: {st_res.status_code}\nGA: {ga_msg}")
        except Exception as e:
            err_msg = str(e)
            notify(f"⚠️ Bot encountered an error: {err_msg}. Will retry in 3 hours.")
        
        create_reports(selected_quote, ga_msg, err_msg)
    else:
        print("Scheduled skip for organic look.")

# ompapaznoob
