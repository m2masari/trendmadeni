import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

url = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

veriler = []

# --- 1) Gram Altın ve Külçe Altın ($) ---
tur_esleme = {
    "ALTIN (TL/GR)": "Gram Altın",
    "Külçe Altın ($)": "Külçe Altın ($)"
}

for a_tag in soup.find_all("a"):
    text = a_tag.get_text(strip=True)
    if text in tur_esleme:
        tur = tur_esleme[text]
        alis_tag = a_tag.find_next("li", class_="cell009")
        satis_tag = alis_tag.find_next("li", class_="cell009") if alis_tag else None

        if alis_tag and satis_tag:
            try:
                alis = float(alis_tag.text.replace(".", "").replace(",", "."))
                satis = float(satis_tag.text.replace(".", "").replace(",", "."))
                veriler.append({
                    "timestamp": timestamp,
                    "tür": tur,
                    "alış": alis,
                    "satış": satis
                })
            except ValueError:
                print(f"⚠️ Hatalı sayı biçimi: {alis_tag.text} / {satis_tag.text}")

# --- 2) Gümüş Gram ---
gumus_tag = soup.find("b", string=lambda x: x and "Gumus Gram" in x)
if gumus_tag:
    alis_tag = gumus_tag.find_next("li", class_="cell009")
    satis_tag = alis_tag.find_next("li", class_="cell009") if alis_tag else None

    if alis_tag and satis_tag:
        try:
            alis = float(alis_tag.text.replace(".", "").replace(",", "."))
            satis = float(satis_tag.text.replace(".", "").replace(",", "."))
            veriler.append({
                "timestamp": timestamp,
                "tür": "Gümüş Gram",
                "alış": alis,
                "satış": satis
            })
        except ValueError:
            print(f"⚠️ Gümüş için sayı hatası: {alis_tag.text} / {satis_tag.text}")

# --- 3) CSV Kaydet ---
if veriler:
    df = pd.DataFrame(veriler)
    csv_path = "altin_gumus_fiyatlari.csv"

    if os.path.exists(csv_path):
        mevcut = pd.read_csv(csv_path)
        df = pd.concat([mevcut, df], ignore_index=True)

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("✅ Veri CSV dosyasına yazıldı:\n", df)
else:
    print("⚠️ Veri bulunamadı, CSV yazılmadı.")
