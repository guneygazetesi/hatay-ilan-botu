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

ISKUR_URL = "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?il=31"

DISTRICTS = [
    ("Hatay İl Geneli Tüm Açık İş İlanları", "Hatay Güncel İş İlanları", "Hatay / İl Geneli", "Tüm Sektörler & Meslekler"),
    ("Antakya Bölgesi Açık Pozisyonlar", "Antakya Bölgesi", "Hatay / Antakya", "Merkez İlçe & Çevresi"),
    ("İskenderun Bölgesi Açık Pozisyonları", "İskenderun Bölgesi", "Hatay / İskenderun", "Sanayi, Liman ve Ticaret"),
    ("Defne Bölgesi Açık Pozisyonlar", "Defne Bölgesi", "Hatay / Defne", "Hizmet ve Ticaret"),
    ("Dörtyol Bölgesi Açık Pozisyonlar", "Dörtyol Bölgesi", "Hatay / Dörtyol", "Sanayi, Narenciye ve Lojistik"),
    ("Samandağ Bölgesi Açık Pozisyonlar", "Samandağ Bölgesi", "Hatay / Samandağ", "Tarım, Turizm ve Hizmet"),
    ("Kırıkhan Bölgesi Açık Pozisyonları", "Kırıkhan Bölgesi", "Hatay / Kırıkhan", "Tarım, İmalat ve Ticaret"),
    ("Reyhanlı Bölgesi Açık Pozisyonlar", "Reyhanlı Bölgesi", "Hatay / Reyhanlı", "Tarım, Lojistik ve Ticaret"),
    ("Arsuz Bölgesi Açık Pozisyonlar", "Arsuz Bölgesi", "Hatay / Arsuz", "Turizm, Hizmet ve Tarım"),
    ("Payas Bölgesi Açık Pozisyonlar", "Payas Bölgesi", "Hatay / Payas", "Ağır Sanayi, Metal ve Lojistik"),
    ("Erzin Bölgesi Açık Pozisyonları", "Erzin Bölgesi", "Hatay / Erzin", "Narenciye, Sanayi ve Turizm"),
    ("Altınözü Bölgesi Açık Pozisyonları", "Altınözü Bölgesi", "Hatay / Altınözü", "Zeytincilik, Tarım ve Hizmet"),
    ("Hassa Bölgesi Açık Pozisyonlar", "Hassa Bölgesi", "Hatay / Hassa", "Tarım, Madencilik ve İmalat"),
    ("Belen Bölgesi Açık Pozisyonlar", "Belen Bölgesi", "Hatay / Belen", "Lojistik, Ulaşım ve Hizmet"),
    ("Yayladağı Bölgesi Açık Pozisyonlar", "Yayladağı Bölgesi", "Hatay / Yayladağı", "Tarım, Hayvancılık ve Ticaret"),
    ("Kumlu Bölgesi Açık Pozisyonlar", "Kumlu Bölgesi", "Hatay / Kumlu", "Tarım ve Hayvancılık")
]

def sync_district_portals():
    print("Hatay ilçeleri senkronize ediliyor...")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for title, employer, city, sector in DISTRICTS:
        item = {
            "title": title,
            "employer": employer,
            "city": city,
            "sector": sector,
            "url": ISKUR_URL,
            "published_date": today_str
        }
        # Başlığa göre kontrol ederek mükerrer eklemeyi engelle
        existing = supabase.table("job_listings").select("id").eq("title", title).execute()
        if not existing.data:
            supabase.table("job_listings").insert(item).execute()
            print(f"[EKLENDİ]: {title}")
        else:
            supabase.table("job_listings").update(item).eq("title", title).execute()
            print(f"[GÜNCELLENDİ]: {title}")

if __name__ == "__main__":
    sync_district_portals()
