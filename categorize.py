import pandas as pd
import re
import difflib

# 1. kategori.html dosyasını oku ve kategorileri temiz bir şekilde parse et
with open('kategori.html', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
clean_lines = [re.sub(r'<[^>]+>', '', line).strip() for line in lines]
clean_lines = [l for l in clean_lines if l]

current_cat = None
categories_dict = {}
all_cat_recipes_norm = {}

def normalize_tr(text):
    return text.lower().replace('İ', 'i').replace('I', 'ı').replace('Ş', 'ş').replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ö', 'ö').replace('Ç', 'ç')

for line in clean_lines:
    if '--- Kategori' in line:
        # Linkten sadece kategori adını alıyoruz (örn: https://.../category/corbalar -> corbalar)
        url = line.split('---')[1].strip().split(': ')[1]
        current_cat = url.split('/')[-1].replace('-', ' ')
        categories_dict[current_cat] = []
    elif '[BAŞARILI ve KAYDEDİLDİ]' in line:
        recipe_name = line.replace('[BAŞARILI ve KAYDEDİLDİ]', '').strip()
        if current_cat:
            categories_dict[current_cat].append(recipe_name)
            all_cat_recipes_norm[normalize_tr(recipe_name)] = current_cat

# 2. rec.csv dosyasını oku
rec_df = pd.read_csv('rec.csv')

# 3. Kategori eşleştirmesi yap
matched_categories = []
for idx, row in rec_df.iterrows():
    name = str(row['yemek adı']).strip()
    norm_name = normalize_tr(name)
    
    cat = None
    if norm_name in all_cat_recipes_norm:
        cat = all_cat_recipes_norm[norm_name]
    elif norm_name + " tarifi" in all_cat_recipes_norm:
        cat = all_cat_recipes_norm[norm_name + " tarifi"]
    elif norm_name.replace(" tarifi", "") in all_cat_recipes_norm:
        cat = all_cat_recipes_norm[norm_name.replace(" tarifi", "")]
    else:
        # Özel eşleştirmeler
        if 'keçi ayağı' in norm_name or 'fıstıklı çıtır muhallebi' in norm_name or 'güllaç' in norm_name:
            cat = 'tatlilar'
        elif 'pide tiridi' in norm_name or 'bonfileli humus' in norm_name or 'tas kebabı' in norm_name:
            cat = 'et yemekleri'
        elif 'kuru fasulye' in norm_name:
            cat = 'sebze yemekleri'
        else:
            matches = difflib.get_close_matches(norm_name, list(all_cat_recipes_norm.keys()), n=1, cutoff=0.7)
            if matches:
                cat = all_cat_recipes_norm[matches[0]]
            else:
                cat = 'diğer'
    matched_categories.append(cat)

# 4. Kategori sütununu en başa (0. indekse) ekle
if 'kategori' in rec_df.columns:
    rec_df.drop(columns=['kategori'], inplace=True)
rec_df.insert(0, 'kategori', matched_categories)

# 5. Yeni dosyaya kaydet
rec_df.to_csv('rec_kategorili.csv', index=False)
print("İşlem tamamlandı! Kategori sütunu en baştadır ve link içermez.")
