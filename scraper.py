from datetime import datetime
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import requests

# Tek bir sayfa için hedef kategori URL'si (Ramazan tarifleri 1. sayfa)
TARGET_PAGE_URL = "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/"
OUTPUT_FILE = "rec.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def clean_url(url):
  """Linklerin sonundaki #comments, #respond veya / gibi ekleri temizler."""
  if "#" in url:
    url = url.split("#")[0]
  url = url.strip()
  if url.endswith("/"):
    url = url[:-1]
  return url


def get_recipe_links_from_single_page(url):
  """Sadece belirtilen tek bir sayfadan tarif linklerini toplar."""
  try:
    print(f"Bağlanılıyor: {url}")
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
      print(f"Hata: Sayfa yüklenemedi. HTTP Kod: {response.status_code}")
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
      href = a["href"].strip()
      cleaned = clean_url(href)

      if (
          "ardaninmutfagi.com/yemek-tarifleri/" in cleaned
          and "/category/" not in cleaned
          and "/page/" not in cleaned
      ):
        links.add(cleaned)

    return list(links)
  except Exception as e:
    print(f"Bağlantı hatası: {e}")
    return []


def parse_recipe_detail(recipe_url):
  try:
    response = requests.get(recipe_url, headers=HEADERS, timeout=10)
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
    if mlz_div:
      malzemeler = mlz_div.get_text(separator="\n", strip=True)

    if not malzemeler:
      return None

    # 3. Açıklama (Div'lerde kesilme sorunu düzeltildi, sadece <p> etiketleri alınıyor)
    aciklama = ""
    entry_content = soup.find(class_="entry-content")

    if entry_content:
      aciklama_list = []
      for child in entry_content.children:
        if getattr(child, "name", None):
          if child.name == "p":
            text = child.get_text(strip=True)
            if text:
              aciklama_list.append(text)

      aciklama = "\n\n".join(aciklama_list)

    return {
        "yemek adı": yemek_adi,
        "malzemeler": malzemeler,
        "açıklama": aciklama,
    }
  except Exception as e:
    return None


def main():
  all_recipes = []
  scraped_titles = set()

  print("=== TEK SAYFA TARİF ÇEKME İŞLEMİ BAŞLATILDI ===")
  sys.stdout.flush()

  # Sadece ilk sayfadaki linkleri al
  links = get_recipe_links_from_single_page(TARGET_PAGE_URL)
  print(f"-> İlk sayfada bulunan temiz tarif linki sayısı: {len(links)}")
  sys.stdout.flush()

  for link in links:
    recipe_data = parse_recipe_detail(link)

    if recipe_data:
      yemek_adi = recipe_data["yemek adı"]

      if yemek_adi not in scraped_titles:
        scraped_titles.add(yemek_adi)
        all_recipes.append(recipe_data)

        print(f"   [BAŞARILI] {yemek_adi}")
        sys.stdout.flush()

      time.sleep(0.05)

  # Elde edilen verileri rec.json dosyasına kaydet
  with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_recipes, f, ensure_ascii=False, indent=4)

  print(
      f"\n=== İŞLEM TAMAMLANDI! İlk sayfadaki {len(all_recipes)} tarif"
      f" {OUTPUT_FILE} dosyasına kaydedildi. ==="
  )
  sys.stdout.flush()


if __name__ == "__main__":
  main()
