import os
import urllib3
from supabase import create_client
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hatay ve 15 ilçesi için çalışan genel İŞKUR arama bağlantısı
BASE_ISKUR_URL = "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31"

DISTRICTS = [
    ("Hatay İl Geneli Tüm Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / İl Geneli", "Tüm Sektörler & Meslekler"),
    ("Antakya İŞKUR Açık İş İlanları", "İŞKUR Antakya Hizmet Merkezi", "Hatay / Antakya", "Merkez İlçe & Çevresi"),
    ("İskenderun İŞKUR Açık İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / İskenderun", "Sanayi, Liman ve Ticaret"),
    ("Defne İŞKUR Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Defne", "Hizmet ve Ticaret"),
    ("Dörtyol İŞKUR Açık İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Dörtyol", "Sanayi, Narenciye ve Lojistik"),
    ("Kırıkhan İŞKUR Açık İş İlanları", "İŞKUR Kırıkhan Hizmet Merkezi", "Hatay / Kırıkhan", "Tarım, İmalat ve Ticaret"),
    ("Reyhanlı İŞKUR Açık İş İlanları", "İŞKUR Reyhanlı Hizmet Merkezi", "Hatay / Reyhanlı", "Tarım, Lojistik ve Ticaret"),
    ("Samandağ İŞKUR Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Samandağ", "Tarım, Turizm ve Hizmet"),
    ("Payas İŞKUR Açık İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Payas", "Ağır Sanayi, Metal ve Lojistik"),
    ("Arsuz İŞKUR Açık İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / Arsuz", "Turizm, Hizmet ve Tarım"),
    ("Erzin İŞKUR Açık İş İlanları", "İŞKUR Dörtyol Hizmet Merkezi", "Hatay / Erzin", "Narenciye, Sanayi ve Turizm"),
    ("Altınözü İŞKUR Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Altınözü", "Zeytincilik, Tarım ve Hizmet"),
    ("Hassa İŞKUR Açık İş İlanları", "İŞKUR Kırıkhan Hizmet Merkezi", "Hatay / Hassa", "Tarım, Madencilik ve İmalat"),
    ("Belen İŞKUR Açık İş İlanları", "İŞKUR İskenderun Hizmet Merkezi", "Hatay / Belen", "Lojistik, Ulaşım ve Hizmet"),
    ("Yayladağı İŞKUR Açık İş İlanları", "İŞKUR Hatay İl Müdürlüğü", "Hatay / Yayladağı", "Tarım, Hayvancılık ve Ticaret"),
    ("Kumlu İŞKUR Açık İş İlanları", "İŞKUR Reyhanlı Hizmet Merkezi", "Hatay / Kumlu", "Tarım ve Hayvancılık")
]

def sync_district_portals():
    print("Hatay genel İŞKUR ilan portalları eşitleniyor...")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for title, employer, city, sector in DISTRICTS:
        item = {
            "title": title,
            "employer": employer,
            "city": city,
            "sector": sector,
            "url": f"{BASE_ISKUR_URL}&district={city.split('/')[-1].strip().lower()}",
            "published_date": today_str
        }
        existing = supabase.table("job_listings").select("id").eq("url", item["url"]).execute()
        if not existing.data:
            supabase.table("job_listings").insert(item).execute()
            print(f"[EKLENDİ]: {title}")
        else:
            supabase.table("job_listings").update(item).eq("url", item["url"]).execute()
            print(f"[GÜNCELLENDİ]: {title}")

if __name__ == "__main__":
    sync_district_portals()
