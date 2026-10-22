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
TOTAL_PAGES = 10  # İlk 10 sayfa
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


def get_recipe_links_from_page(page_number):
  if page_number == 1:
    url = "https://www.ardaninmutfagi.com/category/ramazan-tarifleri/"
  else:
    url = BASE_CATEGORY_URL.format(page_number)

  try:
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
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

    # 2. Malzemeler (Başlıklar temizlenir ve virgüllü formata dönüştürülür)
    mlz_div = soup.find("div", class_="mlz")
    malzemeler = ""
    if mlz_div:
      raw_text = mlz_div.get_text(separator="\n", strip=True)
      lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

      cleaned_items = []
      for line in lines:
        # "Malzemeleri" içeren başlık satırlarını veya yemek adını ele
        if "malzemeleri" in line.lower() or "için malzemeler" in line.lower():
          continue
        if yemek_adi and yemek_adi.lower() in line.lower():
          continue

        # Satır içindeki virgülleri de parçalayarak tekil malzeme öğelerine ayır
        parts = [p.strip() for p in line.split(",") if p.strip()]
        for part in parts:
          if "malzemeler" in part.lower() or "malzemeleri" in part.lower():
            continue
          cleaned_items.append(part)

      malzemeler = ", ".join(cleaned_items)

    if not malzemeler:
      return None

    # 3. Açıklama (Sadece <p> etiketleri alınıyor)
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
  scraped_links = set()
  scraped_titles = set()

  if os.path.exists(OUTPUT_FILE):
    try:
      with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_recipes = json.load(f)
        for item in all_recipes:
          if "yemek adı" in item:
            scraped_titles.add(item["yemek adı"])
    except:
      pass

  print(f"=== İLK {TOTAL_PAGES} SAYFA İÇİN TARİF ÇEKME İŞLEMİ BAŞLATILDI ===")
  sys.stdout.flush()

  for page in range(1, TOTAL_PAGES + 1):
    print(f"\n[Sayfa {page}/{TOTAL_PAGES}] taranıyor...")
    sys.stdout.flush()

    links = get_recipe_links_from_page(page)
    print(f"-> Bulunan temiz tarif linki sayısı: {len(links)}")
    sys.stdout.flush()

    for link in links:
      if link not in scraped_links:
        scraped_links.add(link)
        recipe_data = parse_recipe_detail(link)

        if recipe_data:
          yemek_adi = recipe_data["yemek adı"]

          if yemek_adi not in scraped_titles:
            scraped_titles.add(yemek_adi)
            all_recipes.append(recipe_data)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
              json.dump(all_recipes, f, ensure_ascii=False, indent=4)

            print(f"   [BAŞARILI ve KAYDEDİLDİ] {yemek_adi}")
            sys.stdout.flush()

          time.sleep(0.05)

  print(
      f"\n=== İŞLEM TAMAMLANDI! Toplam {len(all_recipes)} tarif"
      f" {OUTPUT_FILE} dosyasına kaydedildi. ==="
  )
  sys.stdout.flush()


if __name__ == "__main__":
  main()
