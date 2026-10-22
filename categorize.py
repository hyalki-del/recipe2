import pandas as pd
import re
import difflib

# 1. kategori.html dosyasını oku ve kategorileri parse et
with open('kategori.html', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
clean_lines = [re.sub(r'<[^>]+>', '', line).strip() for line in lines]
clean_lines = [l for l in clean_lines if l]

current_category = None
categories_dict = {}
all_cat_recipes = {}

for line in clean_lines:
    if '--- Kategori' in line:
        current_category = line.split('---')[1].strip().split(': ')[1] # kategori URL'si veya adı
        categories_dict[current_category] = []
    elif '[BAŞARILI ve KAYDEDİLDİ]' in line:
        recipe_name = line.replace('[BAŞARILI ve KAYDEDİLDİ]', '').strip()
        if current_category:
            categories_dict[current_category].append(recipe_name)
            all_cat_recipes[recipe_name.lower().strip()] = current_category

# 2. rec.csv dosyasını oku
rec_df = pd.read_csv('rec.csv')

# 3. Doğru kategori sütununu ekle
matched_categories = []
for idx, row in rec_df.iterrows():
    name = str(row['yemek adı']).strip().lower()
    cat = None
    if name in all_cat_recipes:
        cat = all_cat_recipes[name]
    elif name + " tarifi" in all_cat_recipes:
        cat = all_cat_recipes[name + " tarifi"]
    elif name.replace(" tarifi", "") in all_cat_recipes:
        cat = all_cat_recipes[name.replace(" tarifi", "")]
    else:
        # En yakın eşleşme
        matches = difflib.get_close_matches(name, list(all_cat_recipes.keys()), n=1, cutoff=0.7)
        if matches:
            cat = all_cat_recipes[matches[0]]
        else:
            cat = "Diğer / Kategorisiz"
    matched_categories.append(cat)

rec_df['kategori'] = matched_categories
rec_df.to_csv('rec_kategorili.csv', index=False)
print("Eşleştirme tamamlandı ve rec_kategorili.csv olarak kaydedildi!")
