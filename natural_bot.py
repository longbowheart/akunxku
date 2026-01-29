import os
import requests
from requests_oauthlib import OAuth1

# Ambil kredensial dari Secrets
keys = {
    "api_key": os.environ.get("X_API_KEY"),
    "api_secret": os.environ.get("X_API_SECRET"),
    "access_token": os.environ.get("X_ACCESS_TOKEN"),
    "access_secret": os.environ.get("X_ACCESS_SECRET"),
    "my_id": os.environ.get("MY_USER_ID")
}

def notify_ntfy(msg):
    topic = os.environ.get("NTFY_TOPIC")
    if topic:
        try: requests.post(f"https://ntfy.sh/{topic}", data=msg.encode('utf-8'))
        except: pass

def run_diagnostic():
    auth = OAuth1(keys["api_key"], keys["api_secret"], 
                  keys["access_token"], keys["access_secret"])
    
    results = ["🔍 --- X API DIAGNOSTIC REPORT ---"]
    
    # TEST 1: Kredensial Dasar (OAuth 1.0a)
    print("Testing Step 1: Authentication...")
    url_me = "https://api.twitter.com/2/users/me"
    res_me = requests.get(url_me, auth=auth)
    
    if res_me.status_code == 200:
        results.append("✅ STEP 1: Auth Sukses! Kunci API & Access Token Valid.")
        username = res_me.json().get("data", {}).get("username")
        actual_id = res_me.json().get("data", {}).get("id")
        results.append(f"   Identitas: @{username} (ID: {actual_id})")
        
        # Cek apakah MY_USER_ID di Secret sudah benar
        if keys["my_id"] != actual_id:
            results.append(f"   ⚠️ WARNING: Secret MY_USER_ID ({keys['my_id']}) tidak cocok dengan ID asli ({actual_id})!")
    
    elif res_me.status_code == 401:
        results.append("❌ STEP 1: Auth Gagal (401). Token salah atau perlu Regenerate.")
    else:
        results.append(f"❌ STEP 1: Error Lain ({res_me.status_code}): {res_me.text}")

    # TEST 2: Izin Menulis (Permissions)
    if res_me.status_code == 200:
        print("Testing Step 2: Write Permissions...")
        url_tweet = "https://api.twitter.com/2/tweets"
        res_tweet = requests.post(url_tweet, auth=auth, json={"text": "Diagnostic Test Check ✅"})
        
        if res_tweet.status_code == 201:
            results.append("✅ STEP 2: Write Sukses! Bot bisa posting tweet.")
        elif res_tweet.status_code == 403:
            results.append("❌ STEP 2: Permission Gagal (403). Ubah ke 'Read and Write' di Developer Portal.")
        else:
            results.append(f"❌ STEP 2: Gagal Posting ({res_tweet.status_code}): {res_tweet.text}")

    # Gabungkan hasil dan kirim
    final_report = "\n".join(results)
    print(final_report)
    notify_ntfy(final_report)

if __name__ == "__main__":
    run_diagnostic()

# ompapaznoob
