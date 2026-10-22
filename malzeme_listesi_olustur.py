import pandas as pd
import re

# 1. CSV dosyasını oku
df = pd.read_csv('sadece_malzemeler.csv')

# Ölçü birimleri listesi
units_list = [
    'su bardağı', 'çay bardağı', 'yemek kaşığı', 'tatlı kaşığı', 'çay kaşığı',
    'gr', 'gram', 'kg', 'kilogram', 'ml', 'mililitre', 'litre', 'lt',
    'adet', 'diş', 'avuç', 'paket', 'bağ', 'tutam', 'dilim', 'baş', 'şişe',
    'bardak', 'kase', 'tepeleme', 'kepçe', 'fiske', 'pk', 'dal', 'yaprak', 
    'kilo', 'kutu', 'parça', 'ölçek', 'demet'
]

extracted_rows = []
for idx, val in df['malzeme_ve_birim'].items():
    if not isinstance(val, str):
        continue
    parts = val.split(',')
    for p in parts:
        p_raw = p.strip()
        if not p_raw:
            continue
        p_lower = p_raw.lower()
        
        # Hazırlık detaylarını temizleme
        clean_name = re.split(r'[\–\-\(\/]', p_lower)[0].strip()
        for u in units_list:
            clean_name = re.sub(r'\b' + re.escape(u) + r'\b\.?', '', clean_name)
        clean_name = re.sub(r'[\d\s\,\.\–\-\/\½\¼\¾\⅓\⅔]+', ' ', clean_name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name).strip(' .,-–')
        clean_name = re.sub(r'^[\+\&\s]+', '', clean_name).strip()
        clean_name = re.sub(r'&[a-z]+;', '', clean_name).strip()
        
        if len(clean_name) > 2:
            extracted_rows.avnend(clean_name) if hasattr(extracted_rows, 'avnend') else extracted_rows.append(clean_name)

# Benzersizleştirme ve sıralama
unique_materials = sorted(list(set(extracted_rows)))
print(f"Toplam benzersiz malzeme sayısı: {len(unique_materials)}")

# CSV dosyası olarak kaydet
material_df = pd.DataFrame({'malzeme_adi': unique_materials})
material_df.to_csv('sadece_benzersiz_malzemeler.csv', index=False, encoding='utf-8-sig')
print("Liste 'sadece_benzersiz_malzemeler.csv' olarak kaydedildi.")
