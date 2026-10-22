import csv
import os
import re

input_file = "rec.csv"
output_file = "malzeme_birim_ozet.csv"

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

material_units = {}

try:
  with open(input_file, mode="r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
      m_text = str(row.get("malzemeler", ""))
      lines = m_text.split("\n")

      for line in lines:
        line = line.strip()
        if not line or "Malzemeleri" in line or (
            "için" in line and len(line) < 30
        ):
          continue

        match = re.match(r"^([\d\/\-\.\s–½¼¾⅓⅔⅛⅜⅝⅞]+)(.*)$", line)
        if match:
          rest = match.group(2).strip()
        else:
          rest = line

        found_unit = "belirtilmemiş"
        found_item = rest

        for u in sorted(units_list, key=len, reverse=True):
          pattern = r"^(" + re.escape(u) + r")\.?\s*(.*)$"
          m = re.match(pattern, rest, re.IGNORECASE)
          if m:
            found_unit = m.group(1).lower()
            found_item = m.group(2).strip()
            break

        if found_item:
          mat_clean = found_item.strip()
          mat_key = mat_clean.lower()

          if 1 < len(mat_key) < 80:
            if mat_key not in material_units:
              material_units[mat_key] = {"original": mat_clean, "units": set()}
            material_units[mat_key]["units"].add(found_unit)

  result_rows = []
  for mat_key, info in material_units.items():
    orig_name = info["original"]
    units = sorted(list(info["units"]))

    primary_unit = units[0] if units else "belirtilmemiş"
    other_units = ", ".join(units[1:]) if len(units) > 1 else ""

    result_rows.append({
        "malzeme": orig_name,
        "birim": primary_unit,
        "diğer_birimler": other_units,
    })

  with open(
      output_file, mode="w", newline="", encoding="utf-8"
  ) as out_file:
    fieldnames = ["malzeme", "birim", "diğer_birimler"]
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_rows)

  print(f"'{output_file}' başarıyla oluşturuldu!")

except Exception as e:
  print(f"Bir hata oluştu: {e}")
