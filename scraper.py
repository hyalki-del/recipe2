from bs4 import BeautifulSoup
import requests
import json

def tarifi_cek(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Sayfaya ulaşılamadı: {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. ADIM: Sayfanın yapısından hareketle ana içerik kapsayıcısını buluyoruz.
    # Arda'nın Mutfağı altyapısında tarif metni bu class içinde başlar.
    icerik_alani = soup.find('div', class_='entry-content')
    
    if not icerik_alani:
        # Alternatif olası ana kapsayıcılar
        icerik_alani = soup.find('article') or soup.find('div', class_='post-content')

    if icerik_alani:
        # 2. ADIM: Konumsal olarak içerik alanının içinde yer alan ama tarifle ilgisi olmayan 
        # alt yapı elementlerini (paylaşım butonları, sosyal medya alanları vb.) 
        # kelime aramadan doğrudan HTML ağacından söküp atıyoruz (.decompose()).
        istenmeyen_yapilar = icerik_alani.select(
            '.sharedaddy, '
            '.sd-block, '
            '.post-meta, '
            '.cat-links, '
            '.tags-links, '
            '.yarim-sayfa-begen'
        )
        for yapi in istenmeyen_yapilar:
            yapi.decompose()

        # 3. ADIM: Sadece yapısal olarak içerik alanında kalan temiz metni alıyoruz.
        # Böylece alt kısımdaki tarih, beğeni sayısı ve etiketler hiç dahil edilmez.
        temiz_metin = icerik_alani.get_text(separator='\n', strip=True)
        return temiz_metin

    return "İçerik alanı bulunamadı."

# Kullanım
url = "https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates"
tarif_aciklamasi = tarifi_cek(url)

veri = {
    "aciklama": tarif_aciklamasi
}

with open("tarif.json", "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)

print("Tarif başarıyla yapısal olarak filtrelendi ve JSON'a kaydedildi!")
