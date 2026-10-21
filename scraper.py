from bs4 import BeautifulSoup
import json
import requests

url = 'https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')

  # 1. Yemek adını alalım
  title_tag = soup.find('title')
  if title_tag:
    full_title = title_tag.get_text(strip=True)
    yemek_adi = full_title.split('-')[0].strip()
  else:
    yemek_adi = 'Bilinmeyen Yemek'

  # 2. Ana içerik alanını buluyoruz
  entry_content = soup.find(class_='entry-content')

  malzemeler = []
  aciklama = []

  if entry_content:
    # Son kural: container-fluid ve sayfa-container öğelerini al/çıkar
    for unwanted in entry_content.select('.container-fluid, .sayfa-container'):
      unwanted.decompose()

    lines = [
        line.strip()
        for line in entry_content.get_text(separator='\n').split('\n')
        if line.strip()
    ]

    is_aciklama = False

    for line in lines:
      line_lower = line.lower()

      # Tarif adımlarını ayırma mantığı
      if (
          any(
              fiil in line_lower
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

  with open('tarif.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

  print('Tarif başarıyla tarif.json dosyasına kaydedildi.')
else:
  print(f'Sayfaya erişilemedi. Hata kodu: {response.status_code}')
