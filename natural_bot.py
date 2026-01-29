import os
import requests
from requests_oauthlib import OAuth1

def mask_secret(secret_value):
    """Menyensor rahasia: hanya tampilkan 3 awal dan 3 akhir."""
    if not secret_value:
        return "KOSONG/TIDAK TERBACA"
    if len(secret_value) <= 6:
        return "*** (Terlalu Pendek)"
    return f"{secret_value[:3]}...{secret_value[-3:]} (Panjang: {len(secret_value)})"

def diagnostic_secrets():
    # Daftar kunci yang kita panggil dari YAML env
    env_keys = {
        "X_API_KEY": os.environ.get("X_API_KEY"),
        "X_API_SECRET": os.environ.get("X_API_SECRET"),
        "X_ACCESS_TOKEN": os.environ.get("X_ACCESS_TOKEN"),
        "X_ACCESS_SECRET": os.environ.get("X_ACCESS_SECRET"),
        "MY_USER_ID": os.environ.get("MY_USER_ID"),
        "NTFY_TOPIC": os.environ.get("NTFY_TOPIC")
    }

    print("🔍 --- REPOSITORY SECRETS CHECKER ---")
    all_present = True
    
    for name, value in env_keys.items():
        masked = mask_secret(value)
        print(f"🔹 {name}: {masked}")
        if value is None or value == "":
            all_present = False

    print("\n--- ANALISIS ---")
    if all_present:
        print("✅ Semua variabel terbaca oleh sistem.")
        # Coba koneksi singkat ke X jika semua ada
        try:
            auth = OAuth1(env_keys["X_API_KEY"], env_keys["X_API_SECRET"], 
                          env_keys["X_ACCESS_TOKEN"], env_keys["X_ACCESS_SECRET"])
            res = requests.get("https://api.twitter.com/2/users/me", auth=auth)
            print(f"📡 Test Koneksi X API: Status {res.status_code}")
            if res.status_code == 200:
                print(f"🎉 Sukses! Terhubung sebagai @{res.json()['data']['username']}")
            else:
                print(f"❌ Gagal Koneksi: {res.text}")
        except Exception as e:
            print(f"❗ Error Teknis: {str(e)}")
    else:
        print("❌ Ada variabel yang KOSONG. Cek penamaan di file .yml dan Settings GitHub.")

if __name__ == "__main__":
    diagnostic_secrets()

# ompapaznoob
