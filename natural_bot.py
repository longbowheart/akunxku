import os
import requests
from requests_oauthlib import OAuth1

def check_keys():
    # Mengambil kunci dari environment
    k = {
        "API_KEY": os.environ.get("X_API_KEY", ""),
        "API_SEC": os.environ.get("X_API_SECRET", ""),
        "ACC_TOK": os.environ.get("X_ACCESS_TOKEN", ""),
        "ACC_SEC": os.environ.get("X_ACCESS_SECRET", "")
    }

    # Cek apakah ada yang kosong
    for name, value in k.items():
        if not value:
            print(f"⚠️ Secret {name} kosong! Cek settingan GitHub.")
            return

    auth = OAuth1(k["API_KEY"], k["API_SEC"], k["ACC_TOK"], k["ACC_SEC"])
    
    # Tes Pintu Masuk (Auth)
    print("--- MEMULAI TES KONEKSI ---")
    url = "https://api.twitter.com/2/users/me"
    try:
        res = requests.get(url, auth=auth, timeout=10)
        print(f"Hasil Status: {res.status_code}")
        
        if res.status_code == 200:
            user_data = res.json().get("data", {})
            print(f"✅ KONEKSI SUKSES!")
            print(f"Username: @{user_data.get('username')}")
            print(f"ID Akun: {user_data.get('id')}")
            print("--- SEGERA UPDATE MY_USER_ID DENGAN ID DI ATAS ---")
        elif res.status_code == 401:
            print("❌ ERROR 401: Kredensial ditolak. Pastikan API Key dan Access Token baru.")
            print("Tip: Cek apakah Anda tertukar antara API Secret dan Access Token Secret.")
        elif res.status_code == 403:
            print("❌ ERROR 403: Akses dilarang. Cek App Permissions (harus Read/Write).")
        else:
            print(f"❌ ERROR LAIN: {res.text}")
            
    except Exception as e:
        print(f"❗ Terjadi kesalahan teknis: {str(e)}")

if __name__ == "__main__":
    check_keys()

# ompapaznoob
