import os
import re
import pandas as pd

# Scriptin bulunduğu klasörün yolunu baz alarak dosya yolunu otomatik bulma
current_dir = os.path.dirname(os.path.abspath(__file__))

# Dosya adınızı kendi projenize göre buraya yazın (Örn: 'rec_kategorili.csv')
file_path = os.path.join(current_dir, 'rec_kategorili.csv')

# Verisetini yükle
df = pd.read_csv(file_path)

# Yaygın birimlerin listesi (Birimlerin kalması istendiği için korunuyor)
units_list = [
    'su bardağı',
    'çay bardağı',
    'yemek kaşığı',
    'tatlı kaşığı',
    'çay kaşığı',
    'gram',
    'gr',
    'kg',
    'kilogram',
    'ml',
    'mililitre',
    'litre',
    'lt',
    'adet',
    'diş',
    'tutam',
    'avuç',
    'paket',
    'bardak',
    'baş',
    'demet',
    'dilim',
    'kutu',
    'şişe',
    'kahve fincanı',
]

cleaned_ingredients = []

for idx, row in df.iterrows():
  malzemeler_text = str(row['malzemeler'])

  # Ondalık sayılardaki virgüllerin bölünmeyi engellemesi için düzenleme
  cleaned_text = re.sub(r'(\d),(\d)', r'\1.\2', malzemeler_text)

  parts = []
  for line in cleaned_text.split('\n'):
    sub_parts = line.split(',')
    for sp in sub_parts:
      sp = sp.strip()
      if sp:
        parts.append(sp)

  for part in parts:
    # Başlık satırlarını (örn: "Şerbeti için Malzemeler") eleme
    if 'Malzemeleri' in part or ('için' in part and len(part) < 40):
      continue

    # Sayıları, kesirli ifadeleri ve aralarındaki tire/boşlukları baştan temizleme (Birimler kalır)
    text_cleaned = re.sub(
        r'^[\d\/\.\–\-\s,½¾¼⅓⅔]+', '', part, flags=re.IGNORECASE
    )

    text_cleaned = text_cleaned.strip()
    if text_cleaned and len(text_cleaned) > 1:
      cleaned_ingredients.append(text_cleaned)

# Sadece birim ve malzeme adından oluşan yeni DataFrame
result_df = pd.DataFrame({'malzeme': cleaned_ingredients})

# Çıktı dosyasını kaydetme
output_path = os.path.join(current_dir, 'temizlenmis_malzemeler.csv')
result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(
    f'Toplam {len(result_df)} adet malzeme (sayılardan arındırılmış) başarıyla'
    ' kaydedildi!'
)
