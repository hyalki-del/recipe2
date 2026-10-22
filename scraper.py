def parse_recipe_detail(recipe_url):
  try:
    response = requests.get(recipe_url, headers=HEADERS, timeout=10)
    if response.status_code != 200:
      return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Yemek Adı (<meta property="og:title" content="...">)
    og_title = soup.find("meta", property="og:title")
    yemek_adi = None
    if og_title and og_title.get("content"):
      yemek_adi = og_title["content"].strip()

    if not yemek_adi:
      return None

    # 2. Malzemeler (<div class="mlz"> ... </div>)
    mlz_div = soup.find("div", class_="mlz")
    malzemeler = ""
    if mlz_div:
      malzemeler = mlz_div.get_text(separator="\n", strip=True)

    if not malzemeler:
      return None

    # 3. entry-content altındaki paragrafları çek, <div> görene kadar devam et
    aciklama = ""
    entry_content = soup.find(class_="entry-content")
    
    if entry_content:
      aciklama_list = []
      # entry-content içerisindeki tüm çocuk elementleri (veya doğrudan paragrafları) sırayla gezelim
      for child in entry_content.children:
        # Eğer element bir tag (etiket) ise kontrol et
        if getattr(child, "name", None):
          # Karşımıza bir <div> çıkarsa veri çekmeyi tamamen durdur
          if child.name == "div":
            break
          
          # Eğer element bir paragrafsa metnini al
          if child.name == "p":
            text = child.get_text(strip=True)
            if text:
              aciklama_list.append(text)
              
      aciklama = "\n\n".join(aciklama_list)

    return {
        "yemek adı": yemek_adi,
        "malzemeler": malzemeler,
        "açıklama": aciklama,
    }
  except Exception as e:
    return None
