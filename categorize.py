import pandas as pd
from tqdm import tqdm

def yemek_kategorize_et(yemek_adi, malzemeler, aciklama):
    metin = f"{str(yemek_adi)} {str(malzemeler)} {str(aciklama)}".lower()
    
    # Anahtar kelime tabanlı akıllı kural seti
    if any(k in metin for k in ['çorba', 'mercimek', 'tarhana', 'ezogelin', 'şehriye']):
        return 'Çorbalar'
    elif any(k in metin for k in ['kek', 'kurabiye', 'pasta', 'börek', 'poğaça', 'baklava', 'tatlı', 'şerbet', 'muhallebi', 'sütlaç', 'kadayıf', 'şeker', 'çikolata', 'dondurma']):
        return 'Tatlılar ve Hamur İşleri'
    elif any(k in metin for k in ['et', 'kıyma', 'antrikot', 'biftek', 'köfte', 'pirzola', 'kavurma', 'kebap', 'ciğer']):
        return 'Et Yemekleri'
    elif any(k in metin for k in ['tavuk', 'piliç', 'göğsü', 'but']):
        return 'Tavuk Yemekleri'
    elif any(k in metin for k in ['balık', 'karides', 'levrek', 'çipura', 'somon', 'hamsi', 'kalamar']):
        return 'Deniz Ürünleri'
    elif any(k in metin for k in ['makarna', 'erişte', 'spaghetti', 'penne']):
        return 'Makarnalar'
    elif any(k in metin for k in ['pilav', 'pirinç', 'bulgur']):
        return 'Pilavlar'
    elif any(k in metin for k in ['salata', 'marul', 'roka', 'maydanoz', 'yeşillik', 'sos', 'meze']):
        return 'Salatalar ve Mezeler'
    elif any(k in metin for k in ['sebze', 'patlıcan', 'kabak', 'ıspanak', 'pırasa', 'bamya', 'fasulye', 'nohut', 'mercimek']):
        return 'Sebze ve Bakliyat Yemekleri'
    else:
        return 'Diğer'

def main():
    dosya_adi = "rec.csv"
    cikis_dosyasi = "rec_kategorili.csv"
    
    print(f"'{dosya_adi}' okunuyor...")
    df = pd.read_csv(dosya_adi)
    
    kategoriler = []
    print("Yemekler kategorize ediliyor...")
    
    for index, row in tqdm(df.iterrows(), total=len(df)):
        kat = yemek_kategorize_et(
            row.get('yemek adı', ''), 
            row.get('malzemeler', ''), 
            row.get('açıklama', '')
        )
        kategoriler.append(kat)
    
    # Yeni 'kategori' kolonunu en başa ekle
    df.insert(0, 'kategori', kategoriler)
    
    # Yeni dosyaya kaydet
    df.to_csv(cikis_dosyasi, index=False, encoding='utf-8-sig')
    print(f"İşlem tamamlandı! Sonuçlar '{cikis_dosyasi}' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
