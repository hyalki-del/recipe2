import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class TarifAnaliz(BaseModel):
    kalori: float = Field(description="Malzeme miktarları hesaba katılarak hesaplanmış toplam porsiyon kalorisi sayısal değeri")
    kriter_1_makro_mikro: int = Field(description="1 ile 5 arasında puan (protein, karbonhidrat, yağ dengesi ve mikro besin kalitesi)")
    kriter_2_enerji_yogunlugu: int = Field(description="1 ile 5 arasında puan (enerji yoğunluğu / kalori kontrolü uygunluğu)")
    kriter_3_glisemik_indeks: int = Field(description="1 ile 5 arasında puan (kan şekerini dengeleme / düşük glisemik yük potansiyeli)")
    kriter_4_posa_lif: int = Field(description="1 ile 5 arasında puan (lif ve sindirim sistemi dostu olma durumu)")
    kriter_5_volumetrik: int = Field(description="1 ile 5 arasında puan (hacim / tokluk hissi yaratma kapasitesi)")
    kriter_6_islenmislik: int = Field(description="1 ile 5 arasında puan (işlenmemiş/doğal gıda oranı, katkı maddesiz olma)")
    kriter_7_saglik_surdurulebilirlik: int = Field(description="1 ile 5 arasında puan (klinik uyumluluk, metabolik sağlık ve sürdürülebilirlik skoru)")
    uzman_yorumu: str = Field(description="Miktar ve içerik odaklı kısa ve profesyonel diyetisyen değerlendirmesi")

def analiz_et():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY çevre değişkeni bulunamadı!")

    client = genai.Client(api_key=api_key)

    input_file = "rec.csv"
    output_file = "rec_analiz_sonuc.csv"

    if not os.path.exists(input_file):
        print(f"Hata: '{input_file}' dosyası bulunamadı.")
        return

    # Eğer daha önce kısmen analiz yapıldıysa sonuç dosyasını okuyalım, yoksa baştan başlayalım
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        print(f"Mevcut '{output_file}' dosyası bulundu. Kaldığı yerden devam ediliyor...")
    else:
        df = pd.read_csv(input_file)
        # Yeni kolonları boş olarak ekleyelim
        for col in ["kalori", "kriter_1_makro_mikro", "kriter_2_enerji_yogunlugu", 
                    "kriter_3_glisemik_indeks", "kriter_4_posa_lif", "kriter_5_volumetrik", 
                    "kriter_6_islenmislik", "kriter_7_saglik_surdurulebilirlik", "uzman_yorumu"]:
            if col not in df.columns:
                df[col] = None

    print("Yapay zeka beslenme uzmanı analiz işlemine devam ediyor...")

    for index, row in df.iterrows():
        # Eğer bu satır daha önce analiz edilmişse (kalori sütunu doluysa) atla
        if pd.notna(row.get("kalori")) and row.get("kalori") != "":
            continue

        yemek_adi = row.get("yemek_adi", row.get("isim", "Bilinmeyen Yemek"))
        malzemeler = row.get("malzeme", row.get("malzemeler", ""))
        tarif = row.get("tarif", row.get("aciklama", ""))

        prompt = f"""
        Sen uzman bir beslenme ve diyetetik uzmanısın. USDA veritabanı standartlarına dayalı olarak aşağıdaki tarifi analiz et.
        Malzemelerin yanında yazan miktarları hesaba katarak porsiyon başına düşen toplam kaloriyi hesapla.
        
        Yemek Adı: {yemek_adi}
        Malzemeler ve Miktarları: {malzemeler}
        Tarif / Açıklama: {tarif}
        """

        success = False
        retry_count = 0
        max_retries = 3

        while not success and retry_count < max_retries:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json",
                        response_schema=TarifAnaliz,
                    )
                )
                
                data = json.loads(response.text)
                
                df.at[index, "kalori"] = data.get("kalori", 0)
                df.at[index, "kriter_1_makro_mikro"] = data.get("kriter_1_makro_mikro", 0)
                df.at[index, "kriter_2_enerji_yogunlugu"] = data.get("kriter_2_enerji_yogunlugu", 0)
                df.at[index, "kriter_3_glisemik_indeks"] = data.get("kriter_3_glisemik_indeks", 0)
                df.at[index, "kriter_4_posa_lif"] = data.get("kriter_4_posa_lif", 0)
                df.at[index, "kriter_5_volumetrik"] = data.get("kriter_5_volumetrik", 0)
                df.at[index, "kriter_6_islenmislik"] = data.get("kriter_6_islenmislik", 0)
                df.at[index, "kriter_7_saglik_surdurulebilirlik"] = data.get("kriter_7_saglik_surdurulebilirlik", 0)
                df.at[index, "uzman_yorumu"] = data.get("uzman_yorumu", "")
                
                success = True
                
            except Exception as e:
                if "429" in str(e):
                    print(f"Kota sınırı (429) aşıldı (Satır {index}). 60 saniye bekleniyor...")
                    time.sleep(60) # Kota aşımında biraz daha uzun bekleyip tekrar deneyebilir
                    retry_count += 1
                else:
                    print(f"Hata oluştu (Satır {index}): {e}")
                    df.at[index, "uzman_yorumu"] = "Analiz hatası"
                    break

        # Her satırdan sonra ilerlemeyi CSV'ye kaydet ki kota dolarsa veri kaybı yaşanmasın
        df.to_csv(output_file, index=False, encoding='utf-8')
        time.sleep(1)

    print(f"İşlem tamamlandı veya durduruldu. Güncel sonuçlar '{output_file}' dosyasına kaydedildi.")

if __name__ == "__main__":
    analiz_et()
