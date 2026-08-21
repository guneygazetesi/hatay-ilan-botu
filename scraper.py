import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime

# Supabase bağlantısı
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_sample_jobs():
    """
    Bolt'un Supabase tablosundaki zorunlu 'position_type' ve diğer tüm alanlarla uyumlu veri şablonu.
    """
    sample_data = [
        {
            "title": "Hatay Mustafa Kemal Üniversitesi 30 Sözleşmeli Personel Alımı",
            "institution": "Hatay Mustafa Kemal Üniversitesi",
            "institution_type": "Üniversite",
            "district": "Antakya",
            "position_type": "Sözleşmeli Personel",
            "category": "Sözleşmeli Personel",
            "position_count": 30,
            "deadline": "2026-09-30T23:59:59Z",
            "details": "Farklı birimlerde istihdam edilmek üzere büro personeli, destek personeli ve koruma güvenlik görevlisi alımı yapılacaktır.",
            "official_url": "https://www.mku.edu.tr/duyurular/personel-alimi-2026",
            "is_active": True
        },
        {
            "title": "Hatay Büyükşehir Belediyesi Zabıta ve İtfaiye Eri Alımı",
            "institution": "Hatay Büyükşehir Belediyesi",
            "institution_type": "Belediye",
            "district": "Tüm Hatay",
            "position_type": "Memur",
            "category": "Memur",
            "position_count": 50,
            "deadline": "2026-10-15T17:00:00Z",
            "details": "657 sayılı Devlet Memurları Kanununa tabi olarak istihdam edilmek üzere zabıta memuru ve itfaiye eri alımı.",
            "official_url": "https://www.hatay.bel.tr/duyuru/zabita-itfaiye-alimi-2026",
            "is_active": True
        }
    ]
    return sample_data

def sync_jobs():
    jobs = fetch_sample_jobs()
    print(f"Toplam {len(jobs)} ilan kontrol ediliyor...")

    for job in jobs:
        # official_url üzerinden mükerrer kontrolü
        existing = supabase.table("jobs").select("id").eq("official_url", job["official_url"]).execute()
        
        if not existing.data:
            supabase.table("jobs").insert(job).execute()
            print(f"[EKLENDİ] {job['title']}")
        else:
            print(f"[ZATEN MEVCUT] {job['title']}")

if __name__ == "__main__":
    sync_jobs()
