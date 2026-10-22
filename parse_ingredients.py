import csv

# rec.csv dosyasını oku
result_data = []

try:
  with open("rec.csv", mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      yemek = row.get("yemek adı", "")
      malzemeler_text = row.get("malzemeler", "")

      lines = str(malzemeler_text).split("\n")
      for line in lines:
        line = line.strip()
        # Başlık satırlarını eleyelim
        if not line or "Malzemeleri" in line or (
            "için" in line and len(line) < 30
        ):
          continue
        result_data.append({"yemek adı": yemek, "malzeme_ve_birim": line})

  # Yeni CSV dosyasını oluştur
  with open(
      "sadece_malzemeler.csv", mode="w", newline="", encoding="utf-8"
  ) as out_file:
    fieldnames = ["yemek adı", "malzeme_ve_birim"]
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_data)

  print("sadece_malzemeler.csv başarıyla oluşturuldu!")

except Exception as e:
  print(f"Bir hata oluştu: {e}")
