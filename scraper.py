from bs4 import BeautifulSoup
import json
import requests

url = 'https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates'

# Bot korumalarını atlamak için User-Agent ekliyoruz
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')
  entry_content = soup.find(class_='entry-content')

  if entry_content:
    # Tüm metni alıyoruz
    plain_text = entry_content.get_text(separator=' ', strip=True)

    # Aradaki fazla boşlukları ve alt alta geçişleri (\n veya \r) tek boşluğa indiriyoruz
    cleaned_text = ' '.join(plain_text.split())

    # Sadece içeriği içeren JSON yapısı (url alanı çıkarıldı)
    data = {'content': cleaned_text}

    # JSON dosyasına yazma
    with open('tarif.json', 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

    print('Tarif başarıyla temizlenerek tarif.json dosyasına kaydedildi.')
  else:
    print("Hedef sınıf ('entry-content') sayfada bulunamadı.")
else:
  print(f'Sayfaya erişilemedi. Hata kodu: {response.status_code}')
