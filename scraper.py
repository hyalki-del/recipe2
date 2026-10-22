from datetime import datetime
import json
import os
import sys
import time
from bs4 import BeautifulSoup
import requests

MAIN_URL = "https://www.ardaninmutfagi.com/category/yemek-tarifleri"
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


def get_main_categories():
  """Ana sayfadaki <ul class="dropdown-menu ck-liste"> altından 15 kategori linkini çeker."""
  try:
    print(f"Ana kategori listesi alınıyor: {MAIN_URL}")
    response = requests.get(MAIN_URL, headers=HEADERS, timeout=10)
    if response.status_code != 200:
      print(f"Ana sayfa yüklenemedi. HTTP Kod: {response.status_code}")
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    ul_element = soup.find("ul", class_="dropdown-menu ck-liste")

    categories = set()
    if ul_element:
      for a in ul_element.find_all("a", href=True):
        href = a["href"].strip()
        cleaned = clean_url(href)
        if cleaned and cleaned not in categories:
          categories.add(cleaned)

    print(f"-> Toplam {len(categories)} adet ana kategori bulundu.")
    return list(categories)
  except Exception as e:
    print(f"Kategori çekme hatası: {e}")
    return []


def get_recipe_links_from_category_page(category_url, page_number):
  """Belirli bir kategorinin n. sayfasındaki tarif linklerini toplar."""
  if page_number == 1:
    url = category_url
  else:
    # Örn: https://www.ardaninmutfagi.com/category/et-yemekleri/page/2/
    url = f"{category_url}/page/{page_number}/"

  try:
    response = requests.get(url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
      return []  # Sayfa yoksa (örn: 404) boş liste döndür

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
        line_lower = line.lower()
        if (
            "malzemeleri" in line_lower
            or "için malzemeler" in line_lower
            or "malzemeler" in line_lower
        ):
          continue
        if yemek_adi and yemek_adi.lower() in line_lower:
          continue

        sub_parts = line.split(",")
        for part in sub_parts:
          p_clean = part.strip()
          if p_clean:
            p_lower = p_clean.lower()
            if "malzemeler" in p_lower or "malzemeleri" in p_lower:
              continue
            cleaned_items.append(p_clean)

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

  # Daha önceden oluşmuş rec.json varsa yükle (kaldığı yerden devam etme)
  if os.path.exists(OUTPUT_FILE):
    try:
      with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_recipes = json.load(f)
        for item in all_recipes:
          if "yemek adı" in item:
            scraped_titles.add(item["yemek adı"])
      print(
          f"Daha önceden çekilmiş {len(all_recipes)} tarif dosyadan yüklendi."
      )
    except:
      pass

  print("=== ARDA'NIN MUTFAĞI TÜM ARŞİVİ ÇEKME İŞLEMİ BAŞLATILDI ===")
  sys.stdout.flush()

  # 1. 15 Ana Kategoriyi Al
  categories = get_main_categories()
  if not categories:
    print("Hiç kategori bulunamadı, işlem sonlandırılıyor.")
    return

  # 2. Her kategoriyi ve sayfalarını tara
  for idx, cat_url in enumerate(categories, 1):
    print(f"\n--- Kategori [{idx}/{len(categories)}]: {cat_url} ---")
    sys.stdout.flush()

    page = 1
    while True:
      links = get_recipe_links_from_category_page(cat_url, page)

      # Eğer bu sayfada hiç tarif linki bulunamadıysa, bu kategorinin sonuna gelinmiştir
      if not links:
        break

      print(
          f"  [Sayfa {page}] Bulunan temiz tarif linki sayısı: {len(links)}"
      )
      sys.stdout.flush()

      new_recipes_on_page = 0
      for link in links:
        if link not in scraped_links:
          scraped_links.add(link)
          recipe_data = parse_recipe_detail(link)

          if recipe_data:
            yemek_adi = recipe_data["yemek adı"]

            if yemek_adi not in scraped_titles:
              scraped_titles.add(yemek_adi)
              all_recipes.append(recipe_data)
              new_recipes_on_page += 1

              # Her başarılı tarifte rec.json dosyasına anında yaz
              with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_recipes, f, ensure_ascii=False, indent=4)

              print(f"     [BAŞARILI ve KAYDEDİLDİ] {yemek_adi}")
              sys.stdout.flush()

            time.sleep(0.05)  # Sunucuyu yormamak için kısa bekleme

      # Eğer bu sayfadaki tüm linkler daha önce taranmışsa ve yeni tarif gelmediyse sonraki kategoriye geçilebilir
      # Yine de emin olmak için sayfaları artırmaya devam ediyoruz (sayfa boş dönünce break oluyor)
      page += 1

  print(
      f"\n=== İŞLEM TAMAMLANDI! Toplam {len(all_recipes)} benzersiz tarif"
      f" {OUTPUT_FILE} dosyasına kaydedildi. ==="
  )
  sys.stdout.flush()


if __name__ == "__main__":
  main()
