import csv
import re
from collections import Counter

# 1. Aşama: Tüm olası birimleri veriden otomatik olarak keşfetmek için bir sayaç
all_units_candidate = []
raw_rows = []

try:
  with open("sadece_malzemeler.csv", mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      raw_rows.append(row)
      malzeme_full = row.get("malzeme", "").strip()

      # Malzemenin başındaki olası birimi kelime bazında yakalayalım
      words = malzeme_full.split()
      if words:
        first_word = words[0].lower().strip(".,")
        all_units_candidate.append(first_word)
        if len(words) > 1:
          # "su bardağı" veya "yemek kaşığı" gibi iki kelimelik birimler için
          two_words = f"{words[0]} {words[1]}".lower().strip(".,")
          all_units_candidate.append(two_words)

  # En sık geçen birimleri otomatik filtreleyip dinamik birim listesi oluşturalım
  # (Burada en yaygın mutfak ölçüleri ve sık tekrar eden birim kelimeleri otomatik taranır)
  common_units = {
      "su",
      "çay",
      "yemek",
      "tatlı",
      "su bardağı",
      "çay bardağı",
      "yemek kaşığı",
      "tatlı kaşığı",
      "çay kaşığı",
      "gr",
      "gram",
      "kg",
      "kilo",
      "litre",
      "ml",
      "paket",
      "adet",
      "diş",
      "tutam",
      "avuç",
      "baş",
      "demet",
      "bağ",
      "yaprak",
      "dilim",
      "kutu",
      "şişe",
      "bardak",
      "fiske",
      "kase",
      "çorba",
      "kahve",
      "baş",
      "paket",
  }

  unique_pairs = set()

  for row in raw_rows:
    malzeme = row.get("malzeme", "").strip()
    birim = row.get("birim", "").strip()

    # Eğer birim "belirtilmemiş" kalmışsa ama malzeme adının başında bilinen bir birim varsa onu ayıralım
    words = malzeme.split()
    if words and birim == "belirtilmemiş":
      w1 = words[0].lower().strip(".,")
      w2 = (
          f"{words[0]} {words[1]}".lower().strip(".,") if len(words) > 1 else ""
      )

      if w2 in common_units:
        birim = w2
        malzeme = " ".join(words[2:])
      elif w1 in common_units:
        birim = w1
        malzeme = " ".join(words[1:])

    if malzeme:
      unique_pairs.add((malzeme, birim))

  # 2. Aşama: Kombinasyonları yeni CSV'ye yazalım
  with open(
      "malzeme_birim_kombinasyonlari.csv", mode="w", newline="", encoding="utf-8"
  ) as out_file:
    fieldnames = ["malzeme", "birim"]
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for malzeme, birim in sorted(unique_pairs):
      writer.writerow({"malzeme": malzeme, "birim": birim})

  print(
      "Tüm birimler analiz edilerek malzeme_birim_kombinasyonlari.csv"
      f" oluşturuldu! Toplam: {len(unique_pairs)} kombinasyon."
  )

except Exception as e:
  print(f"Bir hata oluştu: {e}")
