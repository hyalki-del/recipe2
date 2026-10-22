def main():
  all_recipes = []
  scraped_links = set()
  scraped_titles = set()

  # Eğer daha önce kısmen yazılmış bir dosya varsa üstüne yazmamak için yükleyebiliriz
  # Ama sıfırdan başlamak istiyorsak boş liste ile başlarız.
  if os.path.exists(OUTPUT_FILE):
    try:
      with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_recipes = json.load(f)
        for item in all_recipes:
          scraped_titles.add(item.get("yemek adı"))
    except:
      pass

  print("=== HIZLANDIRILMIŞ VE ANLIK KAYITLI VERİ ÇEKME BAŞLATILDI ===")
  sys.stdout.flush()

  for page in range(1, TOTAL_PAGES + 1):
    print(f"\n[Sayfa {page}/{TOTAL_PAGES}] taranıyor...")
    sys.stdout.flush()

    links = get_recipe_links_from_page(page)
    print(f"-> Ayıklanan gerçek tarif linki sayısı: {len(links)}")
    sys.stdout.flush()

    for link in links:
      norm_link = link[:-1] if link.endswith("/") else link
      if norm_link not in scraped_links:
        scraped_links.add(norm_link)
        recipe_data = parse_recipe_detail(link)
        if recipe_data:
          yemek_adi = recipe_data["yemek adı"]
          if yemek_adi not in scraped_titles:
            scraped_titles.add(yemek_adi)
            all_recipes.append(recipe_data)

            # HER TARİF BULUNDUĞUNDA ANINDA JSON DOSYASINA YAZ
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
              json.dump(all_recipes, f, ensure_ascii=False, indent=4)

            print(f"   [BAŞARILI ve KAYDEDİLDİ] {yemek_adi}")
            sys.stdout.flush()
        time.sleep(0.05)

  print(
      f"\n=== İŞLEM TAMAMLANDI! Toplam {len(all_recipes)} benzersiz tarif"
      f" kaydedildi. ==="
  )
  sys.stdout.flush()
