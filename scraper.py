from datetime import datetime
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import requests

URL = "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/"
OUTPUT_FILE = "rec.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def test_connection():
  print(f"Bağlantı test ediliyor: {URL}")
  sys.stdout.flush()

  try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    print(f"HTTP Status Kodu: {response.status_code}")
    sys.stdout.flush()

    if response.status_code != 200:
      print(
          "UYARI: Site isteği engelledi veya sayfa bulunamadı!"
          f" Yanıt:\n{response.text[:500]}"
      )
      sys.stdout.flush()
      return False

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
      href = a["href"].strip()
      if href.endswith("/"):
        href = href[:-1]
      if (
          "ardaninmutfagi.com/yemek-tarifleri/" in href
          and "/category/" not in href
          and "/page/" not in href
      ):
        links.add(href)

    print(f"Başarılı! İlk sayfada bulunan tarif linki sayısı: {len(links)}")
    sys.stdout.flush()
    for l in list(links)[:5]:
      print(f" - Örnek link: {l}")
    sys.stdout.flush()
    return True

  except Exception as e:
    print(f"Bağlantı sırasında kritik hata: {e}")
    sys.stdout.flush()
    return False


if __name__ == "__main__":
  test_connection()
