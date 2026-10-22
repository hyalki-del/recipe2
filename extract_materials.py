import pandas as pd
import re

# 1. Adım: CSV dosyasını okuma
df = pd.read_csv('sadece_malzemeler.csv')

units_list = [
    'su bardağı', 'çay bardağı', 'yemek kaşığı', 'tatlı kaşığı', 'çay kaşığı',
    'gr', 'gram', 'kg', 'kilogram', 'ml', 'mililitre', 'litre', 'lt',
    'adet', 'diş', 'avuç', 'paket', 'bağ', 'tutam', 'dilim', 'baş', 'şişe',
    'bardak', 'kase', 'tepeleme', 'kepçe', 'fiske', 'pk', 'dal', 'yaprak', 
    'kilo', 'kutu', 'parça', 'ölçek', 'demet'
]

# 2. Adım: Malzemeleri miktar, birim ve hazırlık yazı ۱۹arından arındırıp benzersizleştirme
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
        found_units = []
        for u in units_list:
            pattern = r'\b' + re.escape(u) + r'\b\.?'
            if re.search(pattern, p_lower):
                found_units.append(u)
        
        clean_name = p_lower
        clean_name = re.split(r'[\–\-\(\/]', clean_name)[0].strip()
        for u in units_list:
            clean_name = re.sub(r'\b' + re.escape(u) + r'\b\.?', '', clean_name)
        clean_name = re.sub(r'[\d\s\,\.\–\-\/\½\¼\¾\⅓\⅔]+', ' ', clean_name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name).strip(' .,-–')
        clean_name = re.sub(r'^[\+\&\s]+', '', clean_name).strip()
        clean_name = re.sub(r'&[a-z]+;', '', clean_name).strip()
        
        if len(clean_name) > 2:
            extracted_rows.append({
                'malzeme': clean_name,
                'birimler': list(dict.fromkeys(found_units))
            })

res_df = pd.DataFrame(extracted_rows)

# 3. Adım: Ölçü birimlerini kolonlara ayırma (1. birim, 2. birim, diğer birimler)
agg_data = []
for malzeme, group in res_df.groupby('malzeme'):
    all_units = []
    for units_list_item in group['birimler']:
        for u in units_list_item:
            if u not in all_units:
                all_units.append(u)
    agg_data.append({
        'malzeme': malzeme,
        'birim_1': all_units[0] if len(all_units) > 0 else '-',
        'birim_2': all_units[1] if len(all_units) > 1 else '-',
        'diger_birimler': ', '.join(all_units[2:]) if len(all_units) > 2 else '-'
    })

final_df = pd.DataFrame(agg_data)

# 4. Adım: USDA referansları ve kalori hesaplamaları (Tereyağı 770 kcal/100g kuralı dahil)
def calculate_calories(row):
    name = row['malzeme'].lower()
    unit = row['birim_1'].lower()
    
    base_kcal = 250.0
    gram_multiplier = 100.0
    
    # Özel ve temel USDA kalori tanımları (100g / 100ml bazlı)
    if 'tereyağı' in name:
        base_kcal = 770.0 # İstediğiniz özel kural
    elif 'zeytinyağı' in name or 'ayçiçek yağı' in name or 'sıvıyağ' in name:
        base_kcal = 884.0
    elif 'un' in name:
        base_kcal = 364.0
    elif 'şeker' in name:
        base_kcal = 387.0
    elif 'yumurta' in name:
        base_kcal = 143.0
    elif 'süt' in name:
        base_kcal = 42.0
    elif 'yoğurt' in name:
        base_kcal = 61.0
    elif 'su' == name:
        base_kcal = 0.0
    elif 'tuz' in name:
        base_kcal = 0.0
    elif 'patates' in name:
        base_kcal = 77.0
    elif 'domates' in name:
        base_kcal = 18.0
    elif 'soğan' in name:
        base_kcal = 40.0
    elif 'sarımsak' in name:
        base_kcal = 149.0
    elif 'tavuk' in name:
        base_kcal = 165.0
    elif 'kıyma' in name:
        base_kcal = 250.0
    elif 'pirinç' in name:
        base_kcal = 360.0
    elif 'makarna' in name:
        base_kcal = 371.0
    elif 'kaşar peyniri' in name:
        base_kcal = 403.0
    elif 'beyaz peynir' in name:
        base_kcal = 264.0
    elif 'ceviz' in name:
        base_kcal = 654.0
    elif 'badem' in name:
        base_kcal = 579.0
    
    # Ölçü birimlerinin Gram / Mililitre karşılıkları
    if 'yemek kaşığı' in unit:
        gram_multiplier = 14.0 if ('yağ' in name or 'tereyağı' in name) else 12.0
    elif 'tatlı kaşığı' in unit:
        gram_multiplier = 5.0
    elif 'çay kaşığı' in unit:
        gram_multiplier = 3.0
    elif 'su bardağı' in unit:
        gram_multiplier = 200.0
    elif 'avuç' in unit:
        gram_multiplier = 30.0
    elif 'adet' in unit:
        gram_multiplier = 50.0 if 'yumurta' in name else 150.0
    elif 'diş' in unit:
        gram_multiplier = 5.0
    elif 'gr' in unit or 'gram' in unit or 'ml' in unit:
        gram_multiplier = 1.0
    elif 'kg' in unit or 'litre' in unit:
        gram_multiplier = 1000.0
    elif 'dilim' in unit:
        gram_multiplier = 30.0
    
    total_kcal = (base_kcal / 100.0) * gram_multiplier
    return f"{base_kcal} kcal (100g)", round(total_kcal, 2)

refs, calcs = [], []
for _, row in final_df.iterrows():
    r_val, c_val = calculate_calories(row)
    refs.append(r_val)
    calcs.append(c_val)

final_df['usda_referans'] = refs
final_df['hesaplanan_kalori'] = calcs

# Excel dosyası olarak dışa aktar
final_df.to_excel('malzemeler_birimler_ve_kaloriler.xlsx', index=False)
print("İşlem başarıyla tamamlandı, dosya kaydedildi!")
