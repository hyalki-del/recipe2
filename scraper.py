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

    # 1. ADIM: Sadece ana tarif gövdesinin bulunduğu üst kapsayıcıyı seçiyoruz.
    # (Böylece sidebar, header, footer ve ana menüler baştan oyun dışı kalır.)
    icerik_alani = soup.find('div', class_='entry-content') # WordPress sitelerinde standarttır
    
    if not icerik_alani:
        # Eğer site farklı bir etiket kullanıyorsa alternatif ana kapsayıcıları deneyebiliriz:
        icerik_alani = soup.find('article') or soup.find('div', class_='post-content')

    if icerik_alani:
        # 2. ADIM: Kelime aramak yerine, bu içerik kutusunun *içerisinde* alt kısımda 
        # yer alan yapısal elementleri (HTML taglerini) yerleşkesine göre bulup çöpe atıyoruz (decompose).
        # Bu etiketler genellikle sosyal paylaşım, footer veya meta alanlarıdır.
        istenmeyen_yapilar = icerik_alani.select(
            '.sharedaddy, '          # Sosyal medya paylaşım blokları
            '.post-footer, '          # Yazı sonu alanı
            '.cat-links, '            # Kategoriler bloğu
            '.tags-links, '           # Etiketler bloğu
            '.yarisma-meta, '         # Varsa ek meta alanları
            'div[style*="clear"]'     # Temizlik divleri
        )
        
        for yapi in istenmeyen_yapilar:
            yapi.decompose() # Bu HTML bloğunu sayfadan tamamen söküp atar

        # 3. ADIM: Geriye sadece tarifin yazılı olduğu saf HTML blokları kalır.
        # Sadece bu alanın metnini alıyoruz.
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

print("Tarif başarıyla ve kelime filtresine takılmadan çekildi!")
