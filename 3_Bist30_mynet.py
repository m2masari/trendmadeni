import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os

# Tarih bilgisi
tarih = (datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')

# Sayfa URL
url = "https://finans.mynet.com/borsa/endeks/xu030-bist-30/"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# BIST 100 değeri class'a göre çekiliyor
bist100_span = soup.find("span", class_="dynamic-price-XU100")
veriler = []

if bist100_span:
    fiyat_str = bist100_span.text.strip()
    fiyat_float = float(fiyat_str.replace(".", "").replace(",", "."))
    veriler.append({
        'kaynak': 'mynet',
        'tur': 'BIST 100 endeks',
        'tarih': tarih,
        'önceki_kapanış': fiyat_float
    })

# BIST 30 değeri de eklenebilir
for span in soup.find_all("span"):
    if span.text.strip() == "BIST 30 Son Değer:":
        fiyat = span.find_next("span").text.strip()
        fiyat_float = float(fiyat.replace(".", "").replace(",", "."))
        veriler.append({
            'kaynak': 'mynet',
            'tur': 'BIST 30 endeks',
            'tarih': tarih,
            'önceki_kapanış': fiyat_float
        })
        break

# DataFrame ve CSV işlemleri
df_yeni = pd.DataFrame(veriler)
dosya_adi = "mynet_BIST_endeks.csv"

if not df_yeni.empty:
    print(df_yeni)
    if os.path.exists(dosya_adi):
        mevcut = pd.read_csv(dosya_adi, encoding="utf-8-sig")
        df_birlesik = pd.concat([mevcut, df_yeni], ignore_index=True)
        df_birlesik.drop_duplicates(subset=["tarih", "tur"], keep="last", inplace=True)
        df_birlesik.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
        print("✅ Veriler güncellendi.")
    else:
        df_yeni.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
        print("✅ Yeni dosya oluşturuldu.")
else:
    print("⚠️ Hiçbir veri bulunamadı.")