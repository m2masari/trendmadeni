import yfinance as yf
from datetime import datetime, timedelta
import os
import pandas as pd
from datetime import datetime, timedelta
import os
from ftplib import FTP


# ------------------------------------------------
# TARİH YARDIMCI FONKSİYONLAR
# ------------------------------------------------

def get_last_business_day(date):
    # Pazartesi -> Cuma
    if date.weekday() == 0:
        return date - timedelta(days=3)
    # Pazar -> Cuma
    if date.weekday() == 6:
        return date - timedelta(days=2)
    # Cumartesi -> Cuma
    if date.weekday() == 5:
        return date - timedelta(days=1)
    return date - timedelta(days=1)


def get_last_3_business_days():
    today = datetime.now()
    days = []

    # Cumartesi veya Pazar → Perşembe + Cuma
    if today.weekday() in [5, 6]:
        friday = get_last_business_day(today)
        thursday = get_last_business_day(friday)
        return [thursday, friday]

    # Normal gün → son 3 iş günü
    current = today
    while len(days) < 3:
        if current.weekday() < 5:
            days.append(current)
        current -= timedelta(days=1)

    return days


# ------------------------------------------------
# ANA FONKSİYON
# ------------------------------------------------

def update_index(FILE_PATH, SYMBOL):

    print(f"\n🔍 İşleniyor: {SYMBOL}")

    try:
        ticker = yf.Ticker(SYMBOL)

        # Son 7 günü çekiyoruz (içinden 3 iş günü alacağız)
        hist = ticker.history(period="7d")

        if hist.empty:
            print("❌ Veri bulunamadı.")
            return

        # TXT içeriğini sözlüğe al
        data_dict = {}
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        data_dict[parts[0]] = parts[1]

        target_days = get_last_3_business_days()
        updated_info = []

        for day in target_days:

            date_str = f"{day.month}/{day.day}/{day.year}"

            # Yahoo tarih formatı
            yahoo_date = day.strftime("%Y-%m-%d")

            if yahoo_date in hist.index.strftime("%Y-%m-%d"):
                close_price = hist.loc[yahoo_date]["Close"]
                price_str = f"{close_price:.4f}"

                data_dict[date_str] = price_str
                updated_info.append(f"📅 {date_str}: {price_str}")

        # Tarihe göre sırala
        sorted_dates = sorted(
            data_dict.keys(),
            key=lambda d: datetime.strptime(d, "%m/%d/%Y")
        )

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            for d in sorted_dates:
                f.write(f"{d}\t{data_dict[d]}\n")

        for info in updated_info:
            print(f"✅ {info}")

        print(f"📁 {FILE_PATH} güncellendi. Toplam kayıt: {len(data_dict)}")

    except Exception as e:
        print(f"❌ Hata: {str(e)}")


# ------------------------------------------------
# MARKET LİSTESİ
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
# ÇALIŞTIR
# ------------------------------------------------

if __name__ == "__main__":

    start_time = datetime.now()
    print(f"🚀 Yahoo Güncelleme Başladı: {start_time.strftime('%H:%M:%S')}")

    for file_path, symbol in markets:
        update_index(file_path, symbol)

    end_time = datetime.now()
    print(f"\n✨ Tüm işlemler tamamlandı. Süre: {end_time - start_time}")

# --- CONFIGURATION (GoDaddy FTP Bilgileri) ---
FTP_HOST = "92.205.148.23"
FTP_USER = "testftp@trendmadeni.com"
FTP_PASS = "9Nes1948..?"
FTP_PATH = ""

def godaddy_yukle(dosya_adi):
    """Güncellenen dosyayı FTP üzerinden GoDaddy sunucusuna yükler."""
    try:
        with FTP() as ftp:
            ftp.connect(FTP_HOST, 21, timeout=30)
            ftp.login(user=FTP_USER, passwd=FTP_PASS)
            
            # GoDaddy için Pasif Modu aktif et
            ftp.set_pasv(True)
            
            # Eğer FTP_PATH doluysa o klasöre git, boşsa kök dizinde kal
            if FTP_PATH:
                ftp.cwd(FTP_PATH)
            
            with open(dosya_adi, 'rb') as f:
                ftp.storbinary(f"STOR {dosya_adi}", f)
            print(f"🚀 {dosya_adi} başarıyla GoDaddy'ye yüklendi.")
    except Exception as e:
        print(f"❌ FTP Hatası ({dosya_adi}): {e}")

godaddy_yukle("data2_BIST100.txt")
godaddy_yukle("data7_dowjones.txt")
godaddy_yukle("data8_SP500.txt")
godaddy_yukle("data9_Nikkei225.txt")
godaddy_yukle("data10_DAX.txt")
godaddy_yukle("data11_FTSE100.txt")
godaddy_yukle("data13_thy.txt")

print("\n" + "="*40)
print("📝 YATIRIM DATA UPDATE LOG")
print("="*40)
print(f"🕒 Bitiş Zamanı : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"⏱ Süre         : {end_time - start_time}")
print("="*40 + "\n")


