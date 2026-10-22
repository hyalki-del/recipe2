import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

# OpenAI istemcisini başlat (Çevre değişkeninden API anahtarını alır)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def yemek_kategorize_et(yemek_adi, malzemeler, aciklama):
    prompt = f"""
Aşağıda verilen yemek tarifini en uygun ana kategoriye (Örn: Çorbalar, Et Yemekleri, Tavuk Yemekleri, Sebze Yemekleri, Tatlılar, Hamur İşleri, Salatalar, Makarnalar ve Pilavlar vb.) dahil et. Sadece kategorinin adını tek kelime veya kısa bir grup olarak (maksimum 2-3 kelime) yaz, başka hiçbir açıklama yapma.

Yemek Adı: {yemek_adi}
Malzemeler: {malzemeler}
Açıklama: {aciklama}

Kategori:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Hızlı ve ekonomik model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return "Diğer"

def main():
    dosya_adi = "rec.csv"
    cikis_dosyasi = "rec_kategorili.csv"
    
    print(f"'{dosya_adi}' okunuyor...")
    df = pd.read_csv(dosya_adi)
    
    kategoriler = []
    print("Yemekler kategorize ediliyor...")
    
    # tqdm ile ilerleme çubuğu göstererek satırları işleyelim
    for index, row in tqdm(df.iterrows(), total=len(df)):
        kat = yemek_kategorize_et(
            str(row.get('yemek adı', '')), 
            str(row.get('malzemeler', '')), 
            str(row.get('açıklama', ''))
        )
        kategoriler.append(kat)
    
    # Yeni 'kategori' kolonunu en başa ekle
    df.insert(0, 'kategori', kategoriler)
    
    # Yeni dosyaya kaydet
    df.to_csv(cikis_dosyasi, index=False, encoding='utf-8-sig')
    print(f"İşlem tamamlandı! Sonuçlar '{cikis_dosyasi}' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
