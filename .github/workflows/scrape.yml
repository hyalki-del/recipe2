from datetime import datetime
import json
import os
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
  """Belirtilen sayfadaki tarif linklerini çeker."""
  if page_number == 1:
    url = "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/"
  else:
    url = BASE_CATEGORY_URL.format(page_number)

  try:
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
      print(f"Sayfa okunamadı: {url} (Status: {response.status_code})")
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
      href = a["href"]
      if (
          "ardaninmutfagi.com/" in href
          and "/category/" not in href
          and href != "https://www.ardaninmutfagi.com/"
          and href not in links
      ):
        links.append(href)

    return list(dict.fromkeys(links))
  except Exception as e:
    print(f"Sayfa çekilirken hata oluştu {url}: {e}")
    return []


def parse_recipe_detail(recipe_url):
  """Tarif sayfasından başlık, malzemeler ve açıklama bilgisini çeker."""
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
    print(f"Tarif detay hatası ({recipe_url}): {e}")
    return None


def main():
  all_recipes = []
  scraped_links = set()

  print("Veri çekme işlemi başlatılıyor...")

  for page in range(1, TOTAL_PAGES + 1):
    print(
        f"Sayfa işleniyor: {page} / {TOTAL_PAGES}"
        f" (Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    )
    links = get_recipe_links_from_page(page)

    for link in links:
      if link not in scraped_links:
        scraped_links.add(link)
        try:
          recipe_data = parse_recipe_detail(link)
          if recipe_data:
            all_recipes.append(recipe_data)
        except Exception as err:
          print(f"Link işlenirken atlandı {link}: {err}")
        time.sleep(0.3)  # Sunucuyu yormamak için kısa bekleme

  # rec.json dosyasına kaydet
  try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
      json.dump(all_recipes, f, ensure_ascii=False, indent=4)
    print(
        f"İşlem tamamlandı! Toplam {len(all_recipes)} tarif {OUTPUT_FILE} dosyasına"
        " kaydedildi."
    )
  except Exception as e:
    print(f"JSON dosyası kaydedilirken hata oluştu: {e}")
    # Dosya yazılamazsa exit code 2 vererek çökmesini önlemek için kritik değilse geçebiliriz
    # ama ana hata genelde request veya parsing sırasında patlamasıdır.


if __name__ == "__main__":
  main()
