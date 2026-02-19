import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

# ------------------------------------------------
# ZAMAN DİLİMİ
# ------------------------------------------------

TR_TZ = ZoneInfo("Europe/Istanbul")

US_INDEXES = ["^DJI", "^GSPC"]


# ------------------------------------------------
# SON 3 İŞ GÜNÜ (TR saatine göre)
# ------------------------------------------------

def get_last_3_business_days():
    today = datetime.now(TR_TZ)
    days = []

    current = today
    while len(days) < 3:
        if current.weekday() < 5:
            days.append(current)
        current -= timedelta(days=1)

    return days


# ------------------------------------------------
# YAHOO VERİ ÇEKME
# ------------------------------------------------

def fetch_yahoo_close(symbol):

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=7d&interval=1d"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=30)

    if r.status_code != 200:
        return None

    data = r.json()

    try:
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]

        price_dict = {}

        for ts, close in zip(timestamps, closes):

            if close is None:
                continue

            date = datetime.fromtimestamp(ts, TR_TZ)

            # 🔥 ABD endeksleri için 1 gün ileri kayma düzeltmesi
            if symbol in US_INDEXES and date.hour < 3:
                date -= timedelta(days=1)

            date_str = date.strftime("%m/%d/%Y")
            price_dict[date_str] = f"{close:.4f}"

        return price_dict

    except:
        return None


# ------------------------------------------------
# DOSYA GÜNCELLEME
# ------------------------------------------------

def update_index(FILE_PATH, SYMBOL):

    print(f"\n🔍 İşleniyor: {SYMBOL}")

    yahoo_data = fetch_yahoo_close(SYMBOL)

    if not yahoo_data:
        print("❌ Veri alınamadı.")
        return

    data_dict = {}

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    data_dict[parts[0]] = parts[1]

    target_days = get_last_3_business_days()

    for day in target_days:
        date_str = day.strftime("%m/%d/%Y")

        if date_str in yahoo_data:
            data_dict[date_str] = yahoo_data[date_str]
            print(f"✅ {date_str}: {yahoo_data[date_str]}")

    sorted_dates = sorted(
        data_dict.keys(),
        key=lambda d: datetime.strptime(d, "%m/%d/%Y")
    )

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        for d in sorted_dates:
            f.write(f"{d}\t{data_dict[d]}\n")

    print(f"📁 {FILE_PATH} güncellendi. Toplam kayıt: {len(data_dict)}")


# ------------------------------------------------
# MARKET LİSTESİ
# ------------------------------------------------

markets = [
    ("data2_BIST100.txt", "XU100.IS"),
    ("data7_dowjones.txt", "^DJI"),
    ("data8_SP500.txt", "^GSPC"),
    ("data9_Nikkei225.txt", "^N225"),
    ("data10_DAX.txt", "^GDAXI"),
    ("data11_FTSE100.txt", "^FTSE")
]


# ------------------------------------------------
# ANA ÇALIŞTIRMA
# ------------------------------------------------

if __name__ == "__main__":

    start_time = datetime.now(TR_TZ)
    print(f"🚀 Yahoo Güncelleme Başladı: {start_time.strftime('%H:%M:%S')}")

    for file_path, symbol in markets:
        update_index(file_path, symbol)

    end_time = datetime.now(TR_TZ)

    print(f"\n✨ Tüm işlemler tamamlandı. Süre: {end_time - start_time}")

