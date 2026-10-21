from bs4 import BeautifulSoup
import requests

url = 'https://www.ardaninmutfagi.com/yemek-tarifleri/tavuk-yemekleri/cajun-baharatli-tavuk-firin-patates'

# Bot korumalarını atlamak için User-Agent ekliyoruz
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')

  # "entry-content" sınıfını bul
  entry_content = soup.find(class_='entry-content')

  if entry_content:
    # Tüm HTML etiketlerini temizleyip düz metin (plain text) alıyoruz
    plain_text = entry_content.get_text(separator='\n', strip=True)
    print(plain_text)

    # İsteğe bağlı: Çıktıyı bir .txt dosyasına kaydetmek isterseniz:
    # with open("tarif.txt", "w", encoding="utf-8") as f:
    #     f.write(plain_text)
  else:
    print("Hedef sınıf ('entry-content') sayfada bulunamadı.")
else:
  print(f'Sayfaya erişilemedi. Hata kodu: {response.status_code}')
