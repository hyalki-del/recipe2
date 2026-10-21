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

    # 1. Yemek Adını (Başlığı) Sayfadan Doğrudan Çekelim
    baslik_elementi = soup.find('h1', class_='entry-title') or soup.find('h1')
    yemek_adi = baslik_elementi.get_text(strip=True) if baslik_elementi else "Tarif"

    # 2. Ana tarif gövdesini seçiyoruz
    icerik_alani = soup.find('div', class_='entry-content')
    
    if not icerik_alani:
        icerik_alani = soup.find('article') or soup.find('div', class_='post-content')

    if icerik_alani:
        # Alt kısımdaki gereksiz yapıları (sosyal medya, paylaşım vb.) yapısal olarak siliyoruz
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

        # \n (satır atlamalarını) koruyarak metni alıyoruz
        temiz_metin = icerik_alani.get_text(separator='\n', strip=True)
        
        return yemek_adi, temiz_metin

    return "Tarif", "İçerik alanı bulunamadı."

# Kullanım
url = "https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates"
yemek_adi, tarif_aciklamasi = tarifi_cek(url)

# JSON formatı (İstediğiniz gibi yemek adı ve açıklama ayrı ayrı, \n'ler korunarak)
veri = {
    "yemek_adi": yemek_adi,
    "aciklama": tarif_aciklamasi
}

with open("tarif.json", "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)

print("Tarif başarıyla, başlıkları ve \n düzeni korunarak JSON'a kaydedildi!")
