import re
import pandas as pd

df = pd.read_csv("rec.csv")

result_data = []

for index, row in df.iterrows():
  yemek = row["yemek adı"]
  lines = str(row["malzemeler"]).split("\n")
  for line in lines:
    line = line.strip()
    if not line or "Malzemeleri" in line or ("için" in line and len(line) < 30):
      continue
    # Miktar ve birimleri ayıklama (örnek temel temizlik)
    result_data.append({"yemek adı": yemek, "malzeme_ve_birim": line})

result_df = pd.DataFrame(result_data)
result_df.to_csv("sadece_malzemeler.csv", index=False, encoding="utf-8")
print("sadece_malzemeler.csv başarıyla oluşturuldu!")
