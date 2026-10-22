import csv
import json

# JSON dosyasını oku
with open("rec.json", "r", encoding="utf-8") as json_file:
  data = json.load(json_file)

# JSON verisinin yapısal durumuna göre (liste veya sözlük) işleme alalım
# Eğer rec.json bir sözlük içinde liste barındırıyorsa uygun anahtarı seçebilirsiniz.
if isinstance(data, dict):
  # Eğer tüm veri tek bir sözlükse, liste içine alalım
  data = [data]

if len(data) > 0:
  # CSV sütun başlıklarını JSON nesnesinin anahtarlarından alıyoruz
  fieldnames = data[0].keys()

  # CSV dosyasına yazma işlemi
  with open("rec.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()  # Başlıkları yaz
    for row in data:
      writer.writerow(row)  # Verileri yaz

  print("Dönüştürme başarılı: rec.csv oluşturuldu.")
else:
  print("JSON dosyası boş.")
