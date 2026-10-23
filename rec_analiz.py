import os
import pandas as pd
from google import genai
from google.genai import types
import json
import time

def analiz_et():
    # GitHub Secrets üzerinden gelen Gemini API Key kontrolü
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY çevre değişkeni bulunamadı! Lütfen GitHub Secrets ayarlarına ekleyin.")

    client = genai.Client(api_key=api_key)

    input_file = "rec.csv"
    output_file = "rec_analiz_sonuc.csv"

    if not os.path.exists(input_file):
        print(f"Hata: '{input_file' dosyası kök dizinde bulunamadı.")
        return

    df = pd.read_csv(input_file)
    
    kaloriler = []
    k1_list = []
    k2_list = []
    k3_list = []
    k4_list = []
    k5_list = []
    k6_list = []
    k7_list = []
    yorumlar = []

    print("Yapay zeka beslenme uzmanı analizi başlatılıyor...")

    for index, row in df.iterrows():
        # Kolon isimlerinizin rec.csv içindeki yapısına göre esnek okunması
        yemek_adi = row.get("yemek_adi", row.get("isim", "Bilinmeyen Yemek"))
        malzemeler = row.get("malzeme", row.get("malzemeler", ""))
        tarif = row.get("tarif", row.get("aciklama", ""))

        prompt = f"""
        Sen uzman bir beslenme ve diyetetik uzmanısın. USDA (FoodData Central) veritabanı standartlarına dayalı olarak aşağıdaki yemeği analiz et ve JSON formatında yanıt ver:
        
        Yemek Adı: {yemek_adi}
        Malzemeler: {malzemeler}
        Tarif / Açıklama: {tarif}
        
        Lütfen şu alanları içeren saf bir JSON objesi döndür (başka hiçbir metin veya markdown etiketi ekleme):
        {{
          "kalori": <porsiyon başına toplam tahmini kalori sayısal değeri>,
          "kriter_1_makro_mikro": <1 ile 5 arasında puan (protein, karbonhidrat, yağ dengesi ve mikro besin kalitesi)>,
          "kriter_2_enerji_yogunlugu": <1 ile 5 arasında puan (enerji yoğunluğu / kalori kontrolü uygunluğu)>,
          "kriter_3_glisemik_indeks": <1 ile 5 arasında puan (kan şekerini dengeleme / düşük glisemik yük potansiyeli)>,
          "kriter_4_posa_lif": <1 ile 5 arasında puan (lif ve sindirim sistemi dostu olma durumu)>,
          "kriter_5_volumetrik": <1 ile 5 arasında puan (hacim / tokluk hissi yaratma kapasitesi)>,
          "kriter_6_islenmislik": <1 ile 5 arasında puan (işlenmemiş/doğal gıda oranı, katkı maddesiz olma)>,
          "kriter_7_saglik_surdurulebilirlik": <1 ile 5 arasında puan (klinik uyumluluk, metabolik sağlık ve sürdürülebilirlik skoru)>,
          "uzman_yorumu": "<Diyetisyen gözüyle kısa ve profesyonel değerlendirme cümlesi>"
        }}
        """

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            text_resp = response.text.strip()
            
            # Markdown temizliği (varsa)
            if text_resp.startswith("```json"):
                text_resp = text_resp[7:]
            if text_resp.endswith("```"):
                text_resp = text_resp[:-3]
            text_resp = text_resp.strip()
            
            data = json.loads(text_resp)
            
            kaloriler.append(data.get("kalori", 0))
            k1_list.append(data.get("kriter_1_makro_mikro", 0))
            k2_list.append(data.get("kriter_2_enerji_yogunlugu", 0))
            k3_list.append(data.get("kriter_3_glisemik_indeks", 0))
            k4_list.append(data.get("kriter_4_posa_lif", 0))
            k5_list.append(data.get("kriter_5_volumetrik", 0))
            k6_list.append(data.get("kriter_6_islenmislik", 0))
            k7_list.append(data.get("kriter_7_saglik_surdurulebilirlik", 0))
            yorumlar.append(data.get("uzman_yorumu", ""))
            
        except Exception as e:
            print(f"Hata oluştu (Satır {index}): {e}")
            kaloriler.append(None)
            k1_list.append(None)
            k2_list.append(None)
            k3_list.append(None)
            k4_list.append(None)
            k5_list.append(None)
            k6_list.append(None)
            k7_list.append(None)
            yorumlar.append("Analiz hatası")
            
        time.sleep(0.5) # API hız sınırlarını korumak için kısa bekleme

    # Yeni kolonları DataFrame'e ekle
    df["kalori"] = kaloriler
    df["kriter_1_makro_mikro"] = k1_list
    df["kriter_2_enerji_yogunlugu"] = k2_list
    df["kriter_3_glisemik_indeks"] = k3_list
    df["kriter_4_posa_lif"] = k4_list
    df["kriter_5_volumetrik"] = k5_list
    df["kriter_6_islenmislik"] = k6_list
    df["kriter_7_saglik_surdurulebilirlik"] = k7_list
    df["uzman_yorumu"] = yorumlar

    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"İşlem tamamlandı. Sonuçlar '{output_file}' dosyasına kaydedildi.")

if __name__ == "__main__":
    analiz_et()
