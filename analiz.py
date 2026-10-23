import csv

def process_data(input_file, output_file):
    cleaned_rows = []
    
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = f.readlines()
    except FileNotFoundError:
        print(f"Hata: '{input_file}' dosyası bulunamadı.")
        return
        
    for line in reader:
        line = line.strip()
        if not line:
            continue
            
        # Başlıktaki 'malzeme' kelimesini atlayalım
        if line.lower() == 'malzeme':
            continue
            
        # 3. Kural: "-" işareti varsa, "-" öncesi ve sonrasını ayır
        detay = ""
        if "-" in line:
            parts = line.split("-", 1)
            line = parts[0].strip()
            detay = parts[1].strip()
            
        # Satırdaki kelimeleri ayır
        words = line.split()
        if not words:
            if detay:
                cleaned_rows.append({
                    "birim": "",
                    "malzeme": "",
                    "detay": detay
                })
            continue
            
        # 1. & 2. Kural: Malzeme genelde son 1 veya 2 kelime, kalanı birim
        if len(words) >= 2:
            malzeme = " ".join(words[-2:])
            birim = " ".join(words[:-2])
        else:
            malzeme = words[0]
            birim = ""
            
        cleaned_rows.append({
            "birim": birim,
            "malzeme": malzeme,
            "detay": detay
        })

    # Sonuçları 'tm_ay.csv' olarak kaydet
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["birim", "malzeme", "detay"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in cleaned_rows:
            writer.writerow(row)

if __name__ == "__main__":
    input_filename = "temizlenmis_malzemeler.csv" # Girdi dosyanız
    output_filename = "tm_ay.csv"                 # Çıktı dosyanız
    
    process_data(input_filename, output_filename)
    print(f"İşlem tamamlandı. Sonuç '{output_filename}' dosyasına kaydedildi.")
