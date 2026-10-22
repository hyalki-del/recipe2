import pandas as pd
import re

# 1. Kaynak CSV dosyasını oku
df = pd.read_csv('sadece_malzemeler.csv')

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
        
        # Parantez veya hazırlık eklerini temizle
        t_clean = re.split(r'[\(\/]', p_lower)[0].strip()
        
        # Baştaki rakam, kesirli sayı veya aralığı (örn: "3 – 4", "1,5", "½") yakala
        match = re.match(r'^([\d\s\,\.\–\-\/\½\¼\¾\⅓\⅔]+)(.+)', t_clean)
        
        if match:
            num_part = match.group(1).strip()
            rem = match.group(2).strip()
            
            words = rem.split()
            if not words:
                continue
            
            # İlk kelimeyi birim olarak al
            unit = words[0]
            
            # Eğer ölçü birimi 2 kelimeden oluşuyorsa (örn: "su bardağı", "yemek kaşığı")
            if len(words) > 1 and unit in ['su', 'yemek', 'tatlı', 'çay', 'küçük', 'dolu', 'tepeleme']:
                unit = f"{words[0]} {words[1]}"
                material = " ".join(words[2:])
            else:
                material = " ".join(words[1:])
            
            # Eğer sayıdan sonra gelen tek kelimeyse (örn: "1 yumurta"), o birim değil malzemedir
            if not material:
                material = unit
                unit = "-"
        else:
            # Başında rakam yoksa (örn: "Tuz", "Karabiber")
            unit = "-"
            material = t_clean
        
        # Malzeme adındaki kalan tire ve gereksiz boşlukları temizle
        material = re.split(r'[\–\-]', material)[0].strip()
        material = re.sub(r'[\s\,\.\–\-\/\½\¼\¾\⅓\⅔]+', ' ', material).strip(' .,-–')
        
        if len(material) > 2:
            extracted_rows.append({
                'malzeme_adi': material,
                'birim': unit if unit else '-'
            })

res_df = pd.DataFrame(extracted_rows)

# Tekrar eden benzersiz malzeme ve birim kombinasyonlarını al
final_df = res_df.drop_duplicates(subset=['malzeme_adi', 'birim']).sort_values('malzeme_adi').reset_index(drop=True)

print(f"Toplam benzersiz kayıt sayısı: {len(final_df)}")

# CSV olarak kaydet
final_df.to_csv('sadece_malzeme_ve_birimleri_akilli.csv', index=False, encoding='utf-8-sig')
print("Dosya başarıyla 'sadece_malzeme_ve_birimleri_akilli.csv' olarak kaydedildi.")
