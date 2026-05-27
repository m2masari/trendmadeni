import yfinance as yf
from datetime import datetime, timedelta
import os
import time
import random
from ftplib import FTP

# ------------------------------------------------
# FTP CONFIG
# ------------------------------------------------

FTP_HOST = "92.205.148.23"
FTP_USER = "testftp@trendmadeni.com"
FTP_PASS = "9Nes1948..?"
FTP_PATH = ""

# ------------------------------------------------
# TARİH FONKSİYONLARI
# ------------------------------------------------

def get_last_business_days(n=3):
    days = []
    current = datetime.now()

    while len(days) < n:
        if current.weekday() < 5:
            days.append(current)
        current -= timedelta(days=1)

    return days

# ------------------------------------------------
# SAFE YAHOO DOWNLOAD
# ------------------------------------------------

def safe_history(symbol, retries=3):
    for i in range(retries):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="7d")

            if data is not None and not data.empty:
                return data

        except Exception as e:
            print(f"⚠️ {symbol} retry {i+1}: {e}")
            time.sleep(2 + i)

    return None

# ------------------------------------------------
# FILE UPDATE
# ------------------------------------------------

def update_index(FILE_PATH, SYMBOL):

    print(f"\n🔍 İşleniyor: {SYMBOL}")

    hist = safe_history(SYMBOL)

    if hist is None:
        print(f"❌ {SYMBOL} veri alınamadı.")
        return

    data_dict = {}

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    data_dict[parts[0]] = parts[1]

    target_days = get_last_business_days(3)
    updated = []

    hist.index = hist.index.strftime("%Y-%m-%d")

    for day in target_days:
        date_str = f"{day.month}/{day.day}/{day.year}"
        yahoo_date = day.strftime("%Y-%m-%d")

        if yahoo_date in hist.index:
            close_price = hist.loc[yahoo_date]["Close"]
            price_str = f"{close_price:.4f}"

            data_dict[date_str] = price_str
            updated.append(f"{date_str} -> {price_str}")

    sorted_dates = sorted(
        data_dict.keys(),
        key=lambda x: datetime.strptime(x, "%m/%d/%Y")
    )

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        for d in sorted_dates:
            f.write(f"{d}\t{data_dict[d]}\n")

    for u in updated:
        print("✅", u)

    print(f"📁 {FILE_PATH} güncellendi")

# ------------------------------------------------
# FTP UPLOAD
# ------------------------------------------------

def upload_to_ftp(file_name):

    try:
        with FTP() as ftp:
            ftp.connect(FTP_HOST, 21, timeout=30)
            ftp.login(FTP_USER, FTP_PASS)
            ftp.set_pasv(True)

            if FTP_PATH:
                ftp.cwd(FTP_PATH)

            with open(file_name, "rb") as f:
                ftp.storbinary(f"STOR {file_name}", f)

            print(f"🚀 Upload OK: {file_name}")

    except Exception as e:
        print(f"❌ FTP error {file_name}: {e}")

# ------------------------------------------------
# MARKET LIST
# ------------------------------------------------

markets = [
    ("data2_BIST100.txt", "XU100.IS"),
    ("data7_dowjones.txt", "^DJI"),
    ("data8_SP500.txt", "^GSPC"),
    ("data9_Nikkei225.txt", "^N225"),
    ("data10_DAX.txt", "^GDAXI"),
    ("data11_FTSE100.txt", "^FTSE"),
    ("data13_thy.txt", "THYAO.IS"),
    ("data9_yen_usd.txt", "USDJPY=X"),
    ("data10_euro_usd.txt", "EUR=X"),
    ("data11_sterlin_usd.txt", "GBP=X")
]

# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":

    start_time = datetime.now()
    print(f"🚀 START: {start_time.strftime('%H:%M:%S')}")

    for file_path, symbol in markets:

        update_index(file_path, symbol)

        # 🧠 anti-block delay
        time.sleep(random.uniform(2, 5))

    # FTP upload
    print("\n📡 Uploading files...")

    for file_path, _ in markets:
        upload_to_ftp(file_path)

    end_time = datetime.now()

    print("\n" + "=" * 40)
    print("📝 UPDATE LOG")
    print("=" * 40)
    print(f"🕒 End: {end_time.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"⏱ Duration: {end_time - start_time}")
    print("=" * 40)


