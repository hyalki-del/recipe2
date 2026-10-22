def parse_recipe_detail(recipe_url):
  try:
    print(f"İstek atılıyor: {recipe_url}")
    response = requests.get(recipe_url, headers=HEADERS, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
      print("Sayfaya erişilemedi!")
      return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # ... (diğer kodlar)
    
    entry_content = soup.find(class_="entry-content")
    if not entry_content:
      print("Uyarı: 'entry-content' sınıfı bu sayfada bulunamadı!")
      
  except Exception as e:
    print(f"Hata oluştu: {e}")
    return None
