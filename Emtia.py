from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time


def clean_price(text):
    if not text:
        return 0.0

    text = text.strip().replace('\xa0', '')

    if "." in text and "," in text:
        if text.rfind(".") > text.rfind(","):
            text = text.replace(",", "")
        else:
            text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", ".")

    try:
        return float(text)
    except:
        return 0.0


def update_today_price(page, url, file_name):
    print(f"\n🔍 İşleniyor: {url}")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)

        price_selector = 'div[data-test="instrument-price-last"]'
        page.wait_for_selector(price_selector, timeout=45000)

        price_text = page.locator(price_selector).first.inner_text()

    except Exception as e:
        print(f"❌ {file_name} için hata: {e}")
        return

    numeric_price = clean_price(price_text)
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

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="tr-TR"
        )

        page = context.new_page()

        # Görselleri engelle (hız + block azaltma)
        page.route("**/*.{png,jpg,jpeg,gif,webp,svg}", lambda route: route.abort())

        for url, file_name in markets:
            update_today_price(page, url, file_name)
            time.sleep(3)

        browser.close()

    print("\n✨ İşlem tamamlandı.")
