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
# MARKET LİSTESİ
# ------------------------------------------------

markets = {
    "XU100.IS": "data2_BIST100.txt",
    "^DJI": "data7_dowjones.txt",
    "^GSPC": "data8_SP500.txt",
    "^N225": "data9_Nikkei225.txt",
    "^GDAXI": "data10_DAX.txt",
    "^FTSE": "data11_FTSE100.txt"
}


# ------------------------------------------------
# TEK SEFERDE TOPLU İNDİRME
# ------------------------------------------------

def download_all():

    symbols = list(markets.keys())

    print("📡 Yahoo'dan toplu veri çekiliyor...")

    data = yf.download(
        tickers=symbols,
        period="10d",
        interval="1d",
        group_by="ticker",
        threads=False,
        progress=False
    )

    return data


# ------------------------------------------------
# DOSYA GÜNCELLEME
# ------------------------------------------------

def update_files(all_data):

    for symbol, file_path in markets.items():

        print(f"\n🔍 İşleniyor: {symbol}")

        if symbol not in all_data:
            print("❌ Veri bulunamadı.")
            continue

        hist = all_data[symbol].dropna()

        if hist.empty:
            print("❌ Veri boş.")
            continue

        data_dict = {}

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        data_dict[parts[0]] = parts[1]

        last_days = hist.tail(3)

        for idx, row in last_days.iterrows():

            date_obj = idx.to_pydatetime()
            date_str = f"{date_obj.month}/{date_obj.day}/{date_obj.year}"

            close_price = row["Close"]
            price_str = f"{close_price:.4f}"

            data_dict[date_str] = price_str
            print(f"✅ {date_str}: {price_str}")

        sorted_dates = sorted(data_dict.keys(), key=parse_date)

        with open(file_path, "w", encoding="utf-8") as f:
            for d in sorted_dates:
                f.write(f"{d}\t{data_dict[d]}\n")

        print(f"📁 {file_path} güncellendi. Toplam kayıt: {len(data_dict)}")


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":

    start_time = datetime.now()
    print(f"🚀 Yahoo Güncelleme Başladı: {start_time.strftime('%H:%M:%S')}")

    all_data = download_all()

    if all_data is None or all_data.empty:
        print("❌ Yahoo tamamen blokladı. 10-15 dakika bekle.")
    else:
        update_files(all_data)

    end_time = datetime.now()
    print(f"\n✨ İşlem tamamlandı. Süre: {end_time - start_time}")

