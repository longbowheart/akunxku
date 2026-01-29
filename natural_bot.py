import os
import requests
from requests_oauthlib import OAuth1

# Kredensial
auth = OAuth1(
    os.environ.get("X_API_KEY"),
    os.environ.get("X_API_SECRET"),
    os.environ.get("X_ACCESS_TOKEN"),
    os.environ.get("X_ACCESS_SECRET")
)

def check_account_health():
    print("🔍 --- X ACCOUNT HEALTH CHECK ---")
    
    # 1. Cek Identitas & Status Akun
    url_me = "https://api.twitter.com/2/users/me?user.fields=created_at,public_metrics"
    res_me = requests.get(url_me, auth=auth)
    
    if res_me.status_code == 200:
        data = res_me.json().get("data", {})
        print(f"✅ Akun Aktif: @{data.get('username')}")
        print(f"📅 Dibuat: {data.get('created_at')}")
        print(f"📊 Followers: {data['public_metrics']['followers_count']}")
        
        # 2. Cek Limit Tweet (v2)
        # API Free tidak punya endpoint khusus cek sisa, 
        # tapi kita bisa tes dengan satu tarikan data kecil
        url_limit = "https://api.twitter.com/2/tweets/search/recent?query=from:TwitterDev"
        res_limit = requests.get(url_limit, auth=auth)
        
        # Lihat Header untuk sisa Limit
        remaining = res_limit.headers.get('x-rate-limit-remaining')
        reset_time = res_limit.headers.get('x-rate-limit-reset')
        
        print(f"\n📈 INFO LIMIT SEARCH:")
        print(f"Sisa Kuota Jam Ini: {remaining}")
        if reset_time:
            from datetime import datetime
            reset_dt = datetime.fromtimestamp(int(reset_time))
            print(f"Reset Pada: {reset_dt}")
            
    elif res_me.status_code == 401:
        print("❌ STATUS 401: Unauthorized. Kunci ditolak/expired.")
    elif res_me.status_code == 403:
        print("❌ STATUS 403: Forbidden. Akun mungkin ter-suspend atau App tidak punya izin Write.")
    else:
        print(f"❓ STATUS {res_me.status_code}: {res_me.text}")

if __name__ == "__main__":
    check_account_health()

# ompapaznoob
