import os
import pandas as pd

# Scriptin bulunduğu klasörün yolunu baz alarak dosya yolunu otomatik bulma
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'tm.csv')

# CSV dosyasını oku
df = pd.read_csv(file_path)

print(f"Orijinal satır sayısı: {len(df)}")

# Tekrarlayan (duplike) satırları kaldır
df_cleaned = df.drop_duplicates()

print(f"Tekrarlayan satırlar silindikten sonraki satır sayısı: {len(df_cleaned)}")

# Temizlenmiş veriyi aynı dosyaya veya yeni bir dosyaya kaydetme
# (Eğer mevcut tm.csv dosyasının üzerine yazmasını isterseniz dosya adını 'tm.csv' yapabilirsiniz)
output_path = os.path.join(current_dir, 'tm.csv')
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Tekrarlayan satırlar temizlendi ve dosya güncellendi: {output_path}")
