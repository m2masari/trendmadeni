import yfinance as yf
from datetime import datetime
import os
import time


# ------------------------------------------------
# TARİH PARSE
# ------------------------------------------------

def parse_date(date_str):
    m, d, y = date_str.split("/")
    return datetime(int(y), int(m), int(d))


# ------------------------------------------------
# VERİ ÇEKME (RETRY'Lİ)
# ------------------------------------------------

def download_data(symbol):

    for attempt in range(3):
        try:
            data = yf.download(
                symbol,
                period="10d",
                interval="1d",
                progress=False,
                threads=False
            )

            if not data.empty:
                return data

        except Exception as e:
            print(f"⚠ Deneme {attempt+1} başarısız: {e}")

        time.sleep(3)

    return None


# ------------------------------------------------
# ANA GÜNCELLEME
# ------------------------------------------------

def update_index(file_path, symbol):

    print(f"\n🔍 İşleniyor: {symbol}")

    hist = download_data(symbol)

    if hist is None or hist.empty:
        print("❌ Veri alınamadı (Yahoo engellemiş olabilir).")
        return

    data_dict = {}

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    data_dict[parts[0]] = parts[1]

    # Son 3 gerçek işlem günü
    last_days = hist.tail(3)

    updated_info = []

    for idx, row in last_days.iterrows():

        date_obj = idx.to_pydatetime()
        date_str = f"{date_obj.month}/{date_obj.day}/{date_obj.year}"

        close_price = row["Close"]
        price_str = f"{close_price:.4f}"

        data_dict[date_str] = price_str
        updated_info.append(f"📅 {date_str}: {price_str}")

    sorted_dates = sorted(data_dict.keys(), key=parse_date)

    with open(file_path, "w", encoding="utf-8") as f:
        for d in sorted_dates:
            f.write(f"{d}\t{data_dict[d]}\n")

    for info in updated_info:
        print(f"✅ {info}")

    print(f"📁 {file_path} güncellendi. Toplam kayıt: {len(data_dict)}")

    time.sleep(2)  # rate limit koruması


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
# ÇALIŞTIR
# ------------------------------------------------

if __name__ == "__main__":

    start_time = datetime.now()
    print(f"🚀 Yahoo Güncelleme Başladı: {start_time.strftime('%H:%M:%S')}")

    for file_path, symbol in markets:
        update_index(file_path, symbol)

    end_time = datetime.now()
    print(f"\n✨ Tüm işlemler tamamlandı. Süre: {end_time - start_time}")

