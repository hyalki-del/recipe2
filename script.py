import pandas as pd
import re

# 1. Verisetini yükleyin
df = pd.read_csv('rec_kategorili.csv')

# 2. Yaygın birimlerin listesi
units_list = [
    'su bardağı', 'çay bardağı', 'yemek kaşığı', 'tatlı kaşığı', 'çay kaşığı',
    'gram', 'gr', 'kg', 'kilogram', 'ml', 'mililitre', 'litre', 'lt',
    'adet', 'diş', 'tutam', 'avuç', 'paket', 'bardak', 'baş', 'demet',
    'dilim', 'kutu', 'şişe', 'kahve fincanı'
]
units_pattern = '|'.join(sorted(units_list, key=len, reverse=True))

parsed_rows = []

for idx, row in df.iterrows():
    yemek = row['yemek adı']
    kategori = row['kategori']
    malzemeler_text = str(row['malzemeler'])
    
    # Ondalık sayılardaki (örn: 2,5) virgüllerin veri bölünmesini engellemesi için geçici nokta yapılması
    cleaned_text = re.sub(r'(\d),(\d)', r'\1.\2', malzemeler_text)
    
    # Hem satır sonu hem de virgül ile parçalama
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
            
        parsed_rows.append({
            'kategori': kategori,
            'yemek_adı': yemek,
            'orijinal_malzeme_satiri': part
        })

# Yeni yapılandırılmış DataFrame
parsed_df = pd.DataFrame(parsed_rows)

# Temizlenen veriyi yeni bir CSV olarak kaydetme
parsed_df.to_csv('temizlenmis_malzemeler.csv', index=False, encoding='utf-8-sig')
print(f"Toplam {len(parsed_df)} adet malzeme satırı başarıyla ayrıştırıldı!")
