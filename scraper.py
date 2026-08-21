import os
import urllib3
from supabase import create_client
from datetime import datetime

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Supabase ortam değişkenleri
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hatay ve 15 ilçesinin resmi MERNİS ilçe kodlu İŞKUR bağlantıları
DISTRICTS = [
    ("Hatay İl Geneli Tüm Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Tümü", "Tüm Sektörler", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31"),
    ("Antakya İŞKUR İş İlanları", "İŞKUR Antakya Hizmet Merkezi", "Hatay / Antakya", "Merkez İlçe İlanları", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=2081"),
    ("İskenderun İŞKUR İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / İskenderun", "Sanayi, Liman ve Ticaret", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1413"),
    ("Defne İŞKUR İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Defne", "Hizmet, Turizm ve Ticaret", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=2082"),
    ("Dörtyol İŞKUR İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Dörtyol", "Sanayi, Narenciye ve Lojistik", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1289"),
    ("Kırıkhan İŞKUR İş İlanları", "İŞKUR Kırıkhan Hizmet Merkezi", "Hatay / Kırıkhan", "Tarım, İmalat ve Ticaret", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1464"),
    ("Reyhanlı İŞKUR İş İlanları", "İŞKUR Reyhanlı Hizmet Merkezi", "Hatay / Reyhanlı", "Tarım, Lojistik ve Ticaret", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1597"),
    ("Samandağ İŞKUR İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Samandağ", "Tarım, Turizm ve Hizmet", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1604"),
    ("Payas İŞKUR İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Payas", "Ağır Sanayi, Metal ve Lojistik", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=2084"),
    ("Arsuz İŞKUR İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / Arsuz", "Turizm, Hizmet ve Tarım", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=2080"),
    ("Erzin İŞKUR İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Erzin", "Narenciye, Sanayi ve Turizm", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1898"),
    ("Altınözü İŞKUR İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Altınözü", "Zeytincilik, Tarım ve Hizmet", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1131"),
    ("Hassa İŞKUR İş İlanları", "İŞKUR Kırıkhan Hizmet Merkezi", "Hatay / Hassa", "Tarım, Madencilik ve İmalat", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1382"),
    ("Belen İŞKUR İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / Belen", "Lojistik, Ulaşım ve Hizmet", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1877"),
    ("Yayladağı İŞKUR İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Yayladağı", "Tarım, Hayvancılık ve Ticaret", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1721"),
    ("Kumlu İŞKUR İş İlanları", "İŞKUR Reyhanlı Hizmet Merkezi", "Hatay / Kumlu", "Tarım ve Hayvancılık", "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31&ilce=1968")
]

def sync_district_portals():
    print("Hatay il ve tüm ilçelerinin İŞKUR portalları eşitleniyor...")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for title, employer, city, sector, url in DISTRICTS:
        item = {
            "title": title,
            "employer": employer,
            "city": city,
            "sector": sector,
            "url": url,
            "published_date": today_str
        }
        
        # Mükerrer kontrolü ve ekleme/güncelleme
        existing = supabase.table("job_listings").select("id").eq("url", url).execute()
        if not existing.data:
            supabase.table("job_listings").insert(item).execute()
            print(f"[EKLENDİ]: {title}")
        else:
            supabase.table("job_listings").update(item).eq("url", url).execute()
            print(f"[GÜNCELLENDİ]: {title}")
            
    print("Senkronizasyon başarıyla tamamlandı.")

if __name__ == "__main__":
    sync_district_portals()
