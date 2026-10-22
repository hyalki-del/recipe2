import json
import os
from bs4 import BeautifulSoup
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

JSON_FILE = "rec.json"


def load_existing_recipes():
  if not os.path.exists(JSON_FILE):
    return []
  try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception as e:
    print(f"JSON okuma hatası: {e}", flush=True)
    return []


def save_recipes(recipes):
  try:
    with open(JSON_FILE, "w", encoding="utf-8") as f:
      json.dump(recipes, f, ensure_ascii=False, indent=4)
    print("-> rec.json başarıyla güncellendi.", flush=True)
  except Exception as e:
    print(f"JSON kaydetme hatası: {e}", flush=True)


def parse_recipe_detail(recipe_url):
  try:
    print(f"-> İstek atılıyor: {recipe_url}", flush=True)
    response = requests.get(recipe_url, headers=HEADERS, timeout=10)
    print(f"-> Status Code: {response.status_code}", flush=True)

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

    # 3. Açıklama (entry-content altındaki paragraflar, div görene kadar)
    aciklama = ""
    entry_content = soup.find(class_="entry-content")

    if entry_content:
      aciklama_list = []
      for child in entry_content.children:
        if getattr(child, "name", None):
          if child.name == "div":
            break
          if child.name == "p":
            text = child.get_text(strip=True)
            if text:
              aciklama_list.append(text)
      aciklama = "\n\n".join(aciklama_list)

    return {
        "yemek adı": yemek_adi,
        "malzemeler": malzemeler,
        "açıklama": aciklama,
        "url": recipe_url,
    }
  except Exception as e:
    print(f"-> Hata oluştu: {e}", flush=True)
    return None


def get_recipe_urls_to_scrape():
  # BURAYA TARAMAK İSTEDİĞİNİZ LİNKLERİ EKLEMELİSİNİZ!
  # Eğer site ana sayfasından veya kategoriden link topluyorsanız o fonksiyonu buraya yazmalısınız.
  # Örnek sabit liste (Test etmek için birkaçı):
  urls = [
      # "https://ornek-yemek-sitesi.com/tarif-1",
      # "https://ornek-yemek-sitesi.com/tarif-2"
  ]
  return urls


if __name__ == "__main__":
  print("--- Scraper Başlatıldı ---", flush=True)

  existing_data = load_existing_recipes()
  existing_urls = {item.get("url") for item in existing_data if "url" in item}

  target_urls = get_recipe_urls_to_scrape()
  print(f"Toplam bulunan hedef URL sayısı: {len(target_urls)}", flush=True)

  new_recipes = []
  for url in target_urls:
    if url in existing_urls:
      print(f"Daha önce taranmış, atlanıyor: {url}", flush=True)
      continue

    recipe_data = parse_recipe_detail(url)
    if recipe_data:
      new_recipes.append(recipe_data)
      print(f"Başarıyla çekildi: {recipe_data['yemek adı']}", flush=True)

  if new_recipes:
    existing_data.extend(new_recipes)
    save_recipes(existing_data)
  else:
    print("Çekilen yeni tarif bulunamadı.", flush=True)
