from bs4 import BeautifulSoup
import requests

# Örnek başlıklar (Bot korumasına karşı gerçek bir tarayıcı gibi görünmek için faydalıdır)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def parse_recipe_detail(recipe_url):
  try:
    print(f"-> İstek atılıyor: {recipe_url}")
    response = requests.get(recipe_url, headers=HEADERS, timeout=10)
    print(f"-> Status Code: {response.status_code}")

    if response.status_code != 200:
      print(
          f"-> HATA: Sayfaya erişilemedi! Status Code: {response.status_code}"
      )
      return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Yemek Adı (<meta property="og:title" content="...">)
    og_title = soup.find("meta", property="og:title")
    yemek_adi = None
    if og_title and og_title.get("content"):
      yemek_adi = og_title["content"].strip()

    if not yemek_adi:
      print("-> UYARI: Yemek adı (<meta property='og:title'>) bulunamadı!")
      return None
    print(f"-> Yemek Adı Bulundu: {yemek_adi}")

    # 2. Malzemeler (<div class="mlz"> ... </div>)
    mlz_div = soup.find("div", class_="mlz")
    malzemeler = ""
    if mlz_div:
      malzemeler = mlz_div.get_text(separator="\n", strip=True)

    if not malzemeler:
      print(
          "-> UYARI: Malzemeler (<div class='mlz'>) bulunamadı veya boş döndü!"
      )
      return None
    print("-> Malzemeler başarıyla çekildi.")

    # 3. entry-content altındaki paragrafları çek, <div> görene kadar devam et
    aciklama = ""
    entry_content = soup.find(class_="entry-content")

    if entry_content:
      aciklama_list = []
      for child in entry_content.children:
        if getattr(child, "name", None):
          # Karşımıza bir <div> çıkarsa veri çekmeyi durdur
          if child.name == "div":
            break

          # Eğer element bir paragrafsa metnini al
          if child.name == "p":
            text = child.get_text(strip=True)
            if text:
              aciklama_list.append(text)

      aciklama = "\n\n".join(aciklama_list)
      print(f"-> Açıklama başarıyla çekildi ({len(aciklama_list)} paragraf).")
    else:
      print("-> UYARI: 'entry-content' sınıfı bu sayfada bulunamadı!")

    return {
        "yemek adı": yemek_adi,
        "malzemeler": malzemeler,
        "açıklama": aciklama,
    }

  except Exception as e:
    print(f"-> KRİTİK HATA oluştu: {e}")
    return None
