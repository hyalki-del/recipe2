from bs4 import BeautifulSoup
import json
import requests

url = 'https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')
  entry_content = soup.find(class_='entry-content')

  if entry_content:
    # Tüm satırları ayrı ayrı alıyoruz (\n karakterine göre bölüyoruz)
    lines = [
        line.strip()
        for line in entry_content.get_text(separator='\n').split('\n')
        if line.strip()
    ]

    malzemeler = []
    aciklama = []

    # Basit bir mantık: İçinde yemek hazırlama fiilleri veya anlatım geçenler açıklama,
    # kısa ve genellikle miktar/malzeme adı içerenler malzeme listesidir.
    # Veya site yapısına göre genelde ilk satırlar malzeme, sonrakiler tariftir.

    # Arda'nın Mutfağı formatı için örnek bir ayrıştırma mantığı:
    # Genellikle "Beğen", "Yorum Yaz", "Kategoriler" gibi alt kısımları ayıklamak gerekir.

    is_aciklama = False

    for line in lines:
      # Sosyal medya butonları, kategori ve etiketleri listeye dahil etmiyoruz
      if any(
          keyword in line.lower()
          for keyword in [
              'beğen',
              'yorum yaz',
              'tweetle',
              'paylaş',
              'yayın tarihi',
              'kategoriler',
              'etiketler',
          ]
      ):
        continue

      # Eğer cümle içinde tarif fiilleri geçmeye başladıysa veya uzun bir anlatımsa "açıklama" kısmına atıyoruz
      if (
          any(
              fiil in line.lower()
              for fiil in [
                  'kesin',
                  'doğrayın',
                  'kıyın',
                  'yerleştirin',
                  'harmanlayın',
                  'sıkın',
                  'pişirin',
                  'çırpın',
                  'kızdırın',
                  'bulayıp',
                  'çıkarıp',
                  'alıp',
              ]
          )
          or len(line.split()) > 7
      ):
        is_aciklama = True

      if not is_aciklama:
        malzemeler.append(line)
      else:
        aciklama.append(line)

    # JSON veri yapısı
    data = {'malzemeler': malzemeler, 'aciklama': ' '.join(aciklama)}

    # JSON dosyasına yazma
    with open('tarif.json', 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

    print('Malzemeler ve açıklama başarıyla ayrıştırılıp JSON kaydedildi.')
  else:
    print("Hedef sınıf ('entry-content') sayfada bulunamadı.")
else:
  print(f'Sayfaya erişilemedi. Hata kodu: {response.status_code}')
