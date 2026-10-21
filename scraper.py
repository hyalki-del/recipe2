from bs4 import BeautifulSoup
import json
import requests

url = 'https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')

  # 1. Sayfanın ana başlığını (<title>) çekiyoruz
  title_tag = soup.find('title')
  if title_tag:
    # Genellikle başlıklar "Cajun Baharatlı Tavuk Fırın Patates - Arda'nın Mutfağı" şeklinde gelir.
    # Sadece yemek adını almak için tire (-) işaretine göre bölüp ilk kısmı alabiliriz.
    full_title = title_tag.get_text(strip=True)
    yemek_adi = full_title.split('-')[0].strip()
  else:
    yemek_adi = 'Bilinmeyen Yemek'

  # 2. İçerik kısmını alıp malzemeler ve açıklama olarak ayırıyoruz
  entry_content = soup.find(class_='entry-content')

  malzemeler = []
  aciklama = []

  if entry_content:
    lines = [
        line.strip()
        for line in entry_content.get_text(separator='\n').split('\n')
        if line.strip()
    ]

    is_aciklama = False

    for line in lines:
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

  # 3. JSON veri yapısını oluşturuyoruz
  data = {
      'yemek_adi': yemek_adi,
      'malzemeler': malzemeler,
      'aciklama': ' '.join(aciklama),
  }

  # JSON dosyasına yazma
  with open('tarif.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

  print(
      'Yemek adı, malzemeler ve açıklama başarıyla JSON dosyasına kaydedildi.'
  )
else:
  print(f'Sayfaya erişilemedi. Hata kodu: {response.status_code}')
