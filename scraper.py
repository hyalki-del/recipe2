from datetime import datetime
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import requests

BASE_CATEGORY_URL = (
    "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/page/{}/"
)
TOTAL_PAGES = 142
OUTPUT_FILE = "rec.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_recipe_links_from_page(page_number):
  if page_number == 1:
    url = "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/"
  else:
    url = BASE_CATEGORY_URL.format(page_number)

  try:
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
      print(f"-> Sayfa okunamadı: {url} (Status: {response.status_code})")
      sys.stdout.flush()
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
      href = a["href"].strip()
      # URL sonundaki olası boşluk veya slash farklarını normalize etmek için temizleyelim
      if href.endswith("/"):
        href = href[:-1]

      if (
          "ardaninmutfagi.com/" in href
          and "/category/" not in href
          and "/page/" not in href
          and href != "https://www.ardaninmutfagi.com"
          and href != "https://www.ardaninmutfagi.com/"
      ):
        links.add(href)

    return list(links)
  except Exception as e:
    print(f"-> Sayfa çekilirken hata oluştu {url}: {e}")
    sys.stdout.flush()
    return []


def parse_recipe_detail(recipe_url):
  try:
    response = requests.get(recipe_url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
      return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Yemek Adı
    og_title = soup.find("meta", property="og:title")
    yemek_adi = None
    if og_title and og_title.get("content"):
      yemek_adi = og_title["content"].strip()

    if not yemek_adi:
      return None

    # 2. Malzemeler
    mlz_div = soup.find("div", class_="mlz")
    malzemeler = ""
    aciklama = ""

    if mlz_div:
      malzemeler = mlz_div.get_text(separator="\n", strip=True)
      next_p = mlz_div.find_next("p")
      if next_p:
        aciklama = next_p.get_text(strip=True)

    if not malzemeler:
      return None

    return {
        "yemek adı": yemek_adi,
        "malzemeler": malzemeler,
        "açıklama": aciklama,
    }

  except Exception as e:
    return None


def main():
  all_recipes = []
  scraped_links = set()
  scraped_titles = set()  # Aynı yemeğin tekrar eklenmesini önler

  print("=== VERİ ÇEKME İŞLEMİ BAŞLATILDI ===")
  sys.stdout.flush()

  for page in range(1, TOTAL_PAGES + 1):
    print(f"\n[Sayfa {page}/{TOTAL_PAGES}] taranıyor...")
    sys.stdout.flush()

    links = get_recipe_links_from_page(page)
    print(f"-> Bu sayfada {len(links)} unique link bulundu.")
    sys.stdout.flush()

    for link in links:
      # URL normalizasyonu
      norm_link = link[:-1] if link.endswith("/") else link

      if norm_link not in scraped_links:
        scraped_links.add(norm_link)
        recipe_data = parse_recipe_detail(link)
        if recipe_data:
          yemek_adi = recipe_data["yemek adı"]

          # Eğer bu yemek ismi daha önce eklenmediyse listeye al
          if yemek_adi not in scraped_titles:
            scraped_titles.add(yemek_adi)
            all_recipes.append(recipe_data)
            print(f"   [BAŞARILI] {yemek_adi}")
            sys.stdout.flush()
        time.sleep(0.1)

  # rec.json dosyasına kaydet
  try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
      json.dump(all_recipes, f, ensure_ascii=False, indent=4)
    print(
        f"\n=== İŞLEM TAMAMLANDI! Toplam {len(all_recipes)} benzersiz tarif"
        f" {OUTPUT_FILE} dosyasına yazıldı. ==="
    )
    sys.stdout.flush()
  except Exception as e:
    print(f"JSON kaydedilirken hata: {e}")
    sys.stdout.flush()


if __name__ == "__main__":
  main()
