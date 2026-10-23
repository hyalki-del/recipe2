import csv
import re

def process_data(input_file, output_file):
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı.")
        return
        
    # 1. Kural: Tekrar eden satırları sil (orijinal sırayı koruyarak)
    unique_lines = list(dict.fromkeys(lines))
    
    # Tanımlanan birimler (Çok kelimeli olanlar uzunluk sırasına göre öne alındı)
    units = [
        "küçük tutam", "dolu tutam", "su bardağı", "tatlı kaşığı", "yemek kaşığı", 
        "çay bardağı", "tutam", "kaşık", "ml", "fiske", "adet", "gr.", "gram", 
        "kg.", "kilo", "kase", "fincan", "bağ", "avuç", "diş"
    ]
    units = sorted(units, key=len, reverse=True)
    
    quantity_modifiers = ["yarım", "çeyrek", "tam"]
    
    cleaned_rows = []
    
    for line in unique_lines:
        # Başlıktaki 'malzeme' kelimesini atlayalım
        if line.lower().startswith('malzeme'):
            continue
            
        # Parantez içerisindeki ifadeleri detay olarak al ve satırdan temizle
        paren_match = re.search(r'\((.*?)\)', line)
        paren_detail = ""
        if paren_match:
            paren_detail = paren_match.group(1).strip()
            line = re.sub(r'\(.*?\)', '', line).strip()
            
        # "-" işareti varsa, sonrasını detay olarak al
        dash_detail = ""
        if "-" in line:
            parts = line.split("-", 1)
            line = parts[0].strip()
            dash_detail = parts[1].strip()
            
        # Detayları birleştir
        detay_parts = [p for p in [dash_detail, paren_detail] if p]
        detay = " - ".join(detay_parts)
        
        # 2. Kural: Hücrelerin içindeki sayıları ve kesirli sayıları sil
        line = re.sub(r'\b\d+([.,]\d+)?(/\d+)?\b', '', line)
        line = re.sub(r'\s+', ' ', line).strip()
        
        # 3. Kural: "yarım", "çeyrek", "tam" gibi miktar belirteçlerini ayır
        q_mod = ""
        for q in quantity_modifiers:
            pattern = r'(?:^|\s)' + re.escape(q) + r'(?:\s|$)'
            if re.search(pattern, line, re.IGNORECASE):
                q_mod = q
                line = re.sub(pattern, ' ', line, flags=re.IGNORECASE).strip()
                break
                
        # 4. Kural: Birimleri ayrı kolona yaz
        unit = ""
        for u in units:
            pattern = r'(?:^|\s)' + re.escape(u) + r'(?:\s|$)'
            if re.search(pattern, line, re.IGNORECASE):
                unit = u
                line = re.sub(pattern, ' ', line, flags=re.IGNORECASE).strip()
                break
                
        # Kalan kısım malzeme adı olur
        malzeme = re.sub(r'\s+', ' ', line).strip()
        
        cleaned_rows.append({
            "miktar_belirteci": q_mod,
            "birim": unit,
            "malzeme": malzeme,
            "detay": detay
        })

    # Sonuçları 'tm_ay.csv' olarak kaydet (Kolonlar: miktar_belirteci, birim, malzeme, detay)
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["miktar_belirteci", "birim", "malzeme", "detay"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in cleaned_rows:
            writer.writerow(row)

if __name__ == "__main__":
    input_filename = "temizlenmis_malzemeler.csv"
    output_filename = "tm_ay.csv"
    
    process_data(input_filename, output_filename)
    print(f"İşlem tamamlandı. Sonuç '{output_filename}' dosyasına kaydedildi.")
