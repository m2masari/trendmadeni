from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time

def clean_price(text):
    if not text:
        return 0.0
    
    # Boşlukları ve gereksiz karakterleri temizle
    text = text.strip().replace('\xa0', '')
    
    # Hem nokta hem virgül varsa (Örn: 6.930,73 veya 6,930.73)
    if "." in text and "," in text:
        # Son karakter hangisiyse o ondalık ayırıcıdır
        if text.rfind(".") > text.rfind(","):
            # Virgül binlik, nokta ondalıktır (İngilizce format: 6,930.73)
            text = text.replace(",", "")
        else:
            # Nokta binlik, virgül ondalıktır (Türkçe format: 6.930,73)
            text = text.replace(".", "").replace(",", ".")
    else:
        # Sadece virgül varsa ondalığa çevir
        text = text.replace(",", ".")
    
    try:
        return float(text)
    except ValueError:
        return 0.0

def update_today_price(url, file_name):
    print(f"\n🔍 İşleniyor: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Sayfa hızlandırma
        page.route("**/*.{png,jpg,jpeg,gif,webp,svg}", lambda route: route.abort())

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Spesifik hedefleme: Ana fiyat div'ini seç
            price_selector = 'div[data-test="instrument-price-last"]'
            page.wait_for_selector(price_selector, timeout=20000)
            
            # İlk eşleşen veriyi al
            price_text = page.locator(price_selector).first.inner_text()
            
        except Exception as e:
            print(f"❌ {file_name} için hata: {e}")
            price_text = None
        finally:
            browser.close()

    if not price_text:
        return

    # Fiyatı temizle
    numeric_price = clean_price(price_text)
    
    # Gram altın gibi yüksek değerli varlıklar için ondalık kontrolü
    # Eğer fiyat 10'dan küçükse ama önceki değerler 6000+ ise bir kayma vardır
    # Ancak bu kontrolü daha güvenli olan clean_price içinde hallettik.
    
    live_price = f"{numeric_price:.4f}"
    today = datetime.now()
    today_str = f"{today.month}/{today.day}/{today.year}"

    data_dict = {}
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    data_dict[parts[0]] = parts[1]

    data_dict[today_str] = live_price

    sorted_dates = sorted(
        data_dict.keys(),
        key=lambda d: datetime.strptime(d, "%m/%d/%Y")
    )

    with open(file_name, "w", encoding="utf-8") as f:
        for d in sorted_dates:
            f.write(f"{d}\t{data_dict[d]}\n")

    print(f"✅ {file_name} → {today_str} = {live_price}")

markets = [
    ("https://www.investing.com/currencies/gau-try?lang=tr", "data1_altin.txt"),
    ("https://www.investing.com/currencies/usd-try?lang=tr", "data3_dolar.txt"),
    ("https://www.investing.com/currencies/eur-try?lang=tr", "data4_euro.txt"),
    ("https://www.investing.com/currencies/xagg-try?lang=tr", "data5_gumus.txt"),
    ("https://www.investing.com/currencies/xptg-try?lang=tr", "data6_platin_gram.txt")
]

if __name__ == "__main__":
    start_time = datetime.now()
    for url, file_name in markets:
        update_today_price(url, file_name)
        time.sleep(1)
    print(f"\n✨ İşlem tamamlandı.")