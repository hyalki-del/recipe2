from bs4 import BeautifulSoup
import requests

# Senin verdiğin örnek test linki
TEST_URL = (
    "https://www.ardaninmutfagi.com/yemek-tarifleri/et-yemekleri/ayvali-kuzu-eti"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def test_parse():
  print(f"Test ediliyor: {TEST_URL}\n")
  response = requests.get(TEST_URL, headers=HEADERS, timeout=10)

  if response.status_code != 200:
    print(f"Hata: Sayfa yüklenemedi (Status code: {response.status_code})")
    return

  soup = BeautifulSoup(response.text, "html.parser")

  # 1. Yemek Adı (<meta property="og:title" content="...">)
  og_title = soup.find("meta", property="og:title")
  yemek_adi = (
      og_title["content"].strip()
      if og_title and og_title.get("content")
      else "Bulunamadı"
  )

  # 2. Malzemeler (<div class="mlz"> ... </div>)
  mlz_div = soup.find("div", class_="mlz")
  malzemeler = ""
  aciklama = ""

  if mlz_div:
    # Boş / gereksiz satırları atlayarak temiz bir metin alıyoruz
    malzemeler = mlz_div.get_text(separator="\n", strip=True)

    # 3. Hemen arkasından gelen <p> </p> arasındaki data "açıklama"
    next_p = mlz_div.find_next("p")
    if next_p:
      aciklama = next_p.get_text(strip=True)
  else:
    malzemeler = "Bulunamadı"
    aciklama = "Bulunamadı"

  # Sonucu ekrana yazdıralım
  print("--- ÇEKİLEN VERİLER ---")
  print(f"Yemek Adı : {yemek_adi}")
  print(f"\nMalzemeler:\n{malzemeler}")
  print(f"\nAçıklama  :\n{aciklama}")


if __name__ == "__main__":
  test_parse()
