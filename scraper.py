from bs4 import BeautifulSoup
import requests
import json
import re

def tarifi_cek(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Sayfaya ulaşılamadı!")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # DİKKAT: Sitenizin HTML yapısına göre ana içeriğin bulunduğu class'ı buraya yazmalısınız.
    # Genellikle yemek sitelerinde içerik şu class'lardan birinin içindedir:
    # Örnekler: div.entry-content, div.tarif-detay, div.post-content vb.
    icerik_alani = soup.find('div', class_='entry-content') # Sitenize göre burayı güncelleyin
    
    if not icerik_alani:
        # Eğer özel bir class bulunamazsa tüm body'yi alıp temizleme yapabiliriz ama üstteki her zaman daha iyidir.
        icerik_alani = soup

    # Sosyal medya butonları, tarih, kategori ve etiketleri (istediğiniz fazlalıkları) barındıran 
    # etiketleri BeautifulSoup ile metinden ayıklayarak siliyoruz (çıkartıyoruz):
    for fazlalik in icerik_alani.select('.sharedaddy, .cat-links, .tags-links, .post-meta, .yorum-kutusu'):
        fazlalik.decompose()

    # Sadece metni alalım ve gereksiz boşlukları temizleyelim
    ham_metin = icerik_alani.get_text(separator='\n', strip=True)

    # İsteğe bağlı: Metnin başındaki veya sonundaki "Yayın tarihi...", "Beğen" gibi kalıntıları 
    # Regex veya string bölme işlemleriyle tamamen temizleyelim:
    # Örneğin "Yayın tarihi" ifadesinden öncesini/sonrasını ayırabilirsiniz:
    if "Yayın tarihi" in ham_metin:
        # Tarif genelde yayın tarihinden *önce* başlar
        temiz_aciklama = ham_metin.split("Yayın tarihi")[0].strip()
    else:
        temiz_aciklama = ham_metin

    # Eğer metin içinde "Beğen Yorum Yaz" gibi ifadeler kaldıysa onları da temizleyelim:
    temiz_aciklama = re.sub(r'\d+\s+Beğen.*', '', temiz_aciklama).strip()

    return temiz_aciklama

# JSON'a kaydetme kısmı
url = "KAYNAK_URL_BURAYA"
tarif_aciklamasi = tarifi_cek(url)

veri = {
    "aciklama": tarif_aciklamasi
}

with open("tarif.json", "w", encoding="utf-8") as f:
     json.dump(veri, f, ensure_ascii=False, indent=4)

print("İşlem tamamlandı, temizlenen açıklama JSON dosyasına yazıldı!")
