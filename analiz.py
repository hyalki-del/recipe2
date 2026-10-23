import csv
import re

def process_data(input_file, output_file):
    cleaned_rows = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = f.readlines()
        
    for line in reader:
        line = line.strip()
        if not line:
            continue
            
        # Başlıktaki 'malzeme' kelimesini atlayalım (eğer varsa)
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
            # Sadece "-" içeren veya boş kalan satırlar için detay varsa kaydedelim
            if detay:
                cleaned_rows.append({
                    "birim": "",
                    "malzeme": "",
                    "detay": detay
                })
            continue
            
        # 1. & 2. Kural: Malzeme genelde son 1 veya 2 kelime
        # (Örn: "su bardağı yoğurt" -> birim: "su bardağı", malzeme: "yoğurt")
        # Tek kelimelik malzemeler için (örn: "Tuz") kontrol
        if len(words) >= 2:
            # Son kelime veya bazı durumlarda son 2 kelime malzeme olabilir. 
            # Verinizin yapısına göre son 2 kelimeyi malzeme kabul ediyoruz:
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

    # Sonuçları temizlenmiş_malzemeler.csv olarak kaydet
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["birim", "malzeme", "detay"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in cleaned_rows:
            writer.writerow(row)

if __name__ == "__main__":
    # Yüklediğiniz dosyanın adı
    input_filename = "temizlenmiş_malzemeler.csv" 
    output_filename = "temizlenmiş_malzemeler.csv" # Aynı dosy üzerine yazabilir veya yeni dosya yapabilirsiniz
    
    # Not: Eğer girdi dosyanızın adı farklıysa (örn: ham_veriler.csv), burayı değiştirebilirsiniz.
    process_data("ham_veri.csv", output_filename)
    print(f"İşlem tamamlandı. Sonuç '{output_filename}' dosyasına kaydedildi.")
