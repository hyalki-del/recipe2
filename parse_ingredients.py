import csv
import re

# 1. Adım: rec.csv dosyasından doğrudan verileri okuyup benzersiz malzeme-birim ikililerini çıkaralım
units_list = [
    "su bardağı",
    "çay bardağı",
    "yemek kaşığı",
    "tatlı kaşığı",
    "çay kaşığı",
    "tepeleme yemek kaşığı",
    "tepeleme tatlı kaşığı",
    "gram",
    "gr",
    "kilo",
    "kg",
    "litre",
    "ml",
    "mililitre",
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
]

unique_pairs = set()

try:
  with open("rec.csv", mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      malzemeler_text = row.get("malzemeler", "")
      lines = str(malzemeler_text).split("\n")

      for line in lines:
        line = line.strip()
        # Başlık ve ara başlıkları ele
        if not line or "Malzemeleri" in line or (
            "için" in line and len(line) < 30
        ):
          continue

        # Sayıları ve kesirleri temizle
        clean = re.sub(
            r"^[\d\/\-\.\s–½¼¾⅓⅔⅛⅜⅝⅞]+", "", line
        ).strip()

        found_unit = "belirtilmemiş"
        found_item = clean

        # Birimi ayıkla
        for u in sorted(units_list, key=len, reverse=True):
          pattern = r"^(" + re.escape(u) + r")\.?\s*(.*)$"
          match = re.match(pattern, clean, re.IGNORECASE)
          if match:
            found_unit = match.group(1).lower()
            found_item = match.group(2).strip()
            break

        if found_item:
          unique_pairs.add((found_item, found_unit))

  # 2. Adım: Yeni CSV dosyasını oluştur
  with open(
      "malzeme_birim_kombinasyonlari.csv", mode="w", newline="", encoding="utf-8"
  ) as out_file:
    fieldnames = ["malzeme", "birim"]
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for malzeme, birim in sorted(unique_pairs):
      writer.writerow({"malzeme": malzeme, "birim": birim})

  print(
      "malzeme_birim_kombinasyonlari.csv başarıyla oluşturuldu! Toplam"
      f" kombinasyon: {len(unique_pairs)}"
  )

except Exception as e:
  print(f"Bir hata oluştu: {e}")
