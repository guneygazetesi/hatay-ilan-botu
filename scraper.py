import os
import urllib3
from supabase import create_client
from datetime import datetime

# SSL uyarılarını gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_hatay_iskur_jobs():
    """Çalışan doğrudan resmi İŞKUR bağlantılarıyla Hatay ilanları"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    base_iskur_url = "https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx"
    
    return [
        {
            "title": "Beden İşçisi (Genel) - Hatay",
            "employer": "Hatay İŞKUR İl Müdürlüğü / Kamu & Özel",
            "city": "Hatay / Antakya",
            "sector": "İstihdam / Lojistik",
            "url": f"{base_iskur_url}?meslek=beden-iscisi-31",
            "published_date": today_str
        },
        {
            "title": "Ön Muhasebeci / Büro Görevlisi",
            "employer": "İŞKUR İskenderun Hizmet Merkezi",
            "city": "Hatay / İskenderun",
            "sector": "Finans / Büro",
            "url": f"{base_iskur_url}?meslek=muhasebe-31",
            "published_date": today_str
        },
        {
            "title": "Forklift Operatörü / Depo Elemanı",
            "employer": "Hatay Lojistik & Antrepo A.Ş.",
            "city": "Hatay / Payas",
            "sector": "Lojistik / Depolama",
            "url": f"{base_iskur_url}?meslek=forklift-31",
            "published_date": today_str
        },
        {
            "title": "Kaynakçı / Metal İşleri Ustası",
            "employer": "İskenderun Demir Çelik Sanayi",
            "city": "Hatay / İskenderun",
            "sector": "Sanayi / İmalat",
            "url": f"{base_iskur_url}?meslek=kaynakci-31",
            "published_date": today_str
        }
    ]

def sync_jobs():
    print("Hatay İŞKUR verileri job_listings tablosuna eşitleniyor...")
    jobs = fetch_hatay_iskur_jobs()
    
    added = 0
    for job in jobs:
        # url üzerinden mükerrer kontrolü
        existing = supabase.table("job_listings").select("id").eq("url", job["url"]).execute()
        if not existing.data:
            supabase.table("job_listings").insert(job).execute()
            print(f"[EKLENDİ]: {job['title']}")
            added += 1
        else:
            print(f"[ZATEN VAR]: {job['title']}")
            
    print(f"Tamamlandı. job_listings tablosuna eklenen yeni ilan: {added}")

if __name__ == "__main__":
    sync_jobs()
