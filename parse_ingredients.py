import csv

# Benzersiz malzeme ve birim ikililerini tutmak için set kullanıyoruz
unique_pairs = set()

try:
  with open("sadece_malzemeler.csv", mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      malzeme = row.get("malzeme", "").strip()
      birim = row.get("birim", "").strip()

      if malzeme:
        # Aynı malzeme ve birim kombinasyonunun tekrar etmesini engeller,
        # ancak aynı malzemenin farklı birimleri varsa ayrı satır olarak ekler.
        unique_pairs.add((malzeme, birim))

  # Yeni CSV dosyasını oluştur
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
