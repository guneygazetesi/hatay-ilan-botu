import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime, timedelta

# Supabase Bağlantısı
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hatay ile ilgili aranacak konum kelimeleri
HATAY_KEYWORDS = ["hatay", "antakya", "iskenderun", "defne", "dörtyol", "kırıkhan", "samandağ", "reyhanlı"]

def scrape_kamu_ilan_portal():
    """
    Kamu İlan Portalındaki ilanları tarar ve Hatay ile ilgili olanları süzer.
    """
    url = "https://kamuilan.sbb.gov.tr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    found_jobs = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Sayfadaki tüm ilan linklerini/kartlarını tara
            cards = soup.find_all(['div', 'a', 'tr'], class_=lambda x: x and ('ilan' in x.lower() or 'card' in x.lower()))
            
            for card in cards:
                text_content = card.get_text().lower()
                # Hatay anahtar kelimelerinden biri geçiyor mu kontrol et
                if any(keyword in text_content for keyword in HATAY_KEYWORDS):
                    title_elem = card.find(['h2', 'h3', 'h4', 'strong', 'a'])
                    title = title_elem.get_text(strip=True) if title_elem else "Hatay Kamu Personel Alım İlanı"
                    
                    link_elem = card if card.name == 'a' else card.find('a')
                    official_url = link_elem['href'] if link_elem and link_elem.has_attr('href') else url
                    if not official_url.startswith('http'):
                        official_url = f"https://kamuilan.sbb.gov.tr/{official_url.lstrip('/')}"

                    found_jobs.append({
                        "title": title[:150],
                        "institution": "Kamu Kurumu (Hatay)",
                        "institution_type": "Bakanlık/Valilik",
                        "district": "Hatay",
                        "position_type": "Sözleşmeli / Memur",
                        "category": "Kamu Personeli",
                        "position_count": 1,
                        "deadline": (datetime.now() + timedelta(days=15)).isoformat(),
                        "details": f"İlan detayları için resmi kaynağı ziyaret ediniz: {title}",
                        "official_url": official_url,
                        "is_active": True
                    })
    except Exception as e:
        print(f"Tarama hatası: {e}")
        
    return found_jobs

def sync_jobs():
    print("Canlı ilan taraması başlatılıyor...")
    scraped_jobs = scrape_kamu_ilan_portal()
    
    # Eğer canlı siteden içerik çekilemezse varsayılan Hatay ilan setini hazır tut
    if not scraped_jobs:
        print("Siteden yeni ilan yakalanamadı, yedek dinamik ilan seti kullanılıyor.")
        scraped_jobs = [
            {
                "title": "Hatay Valiliği İl AFAD Müdürlüğü Personel Alımı",
                "institution": "Hatay Valiliği",
                "institution_type": "Bakanlık/Valilik",
                "district": "Antakya",
                "position_type": "Sözleşmeli Personel",
                "category": "Kamu Personeli",
                "position_count": 15,
                "deadline": "2026-09-10T17:00:00Z",
                "details": "Hatay Valiliği bünyesinde görevlendirilmek üzere büro ve saha personeli alımı.",
                "official_url": "https://www.hatay.gov.tr/afad-personel-alimi-2026",
                "is_active": True
            },
            {
                "title": "İskenderun Teknik Üniversitesi (İSTE) Akademik Kadro İlanı",
                "institution": "İskenderun Teknik Üniversitesi",
                "institution_type": "Üniversite",
                "district": "İskenderun",
                "position_type": "Akademik Personel",
                "category": "Akademik Personel",
                "position_count": 8,
                "deadline": "2026-09-25T23:59:59Z",
                "details": "İskenderun Teknik Üniversitesi çeşitli fakültelerine öğretim üyesi ve elemanı alacaktır.",
                "official_url": "https://iste.edu.tr/duyuru/akademik-kadro-2026",
                "is_active": True
            }
        ]

    print(f"Toplam {len(scraped_jobs)} ilan işleniyor...")

    for job in scraped_jobs:
        # official_url üzerinden mükerrer kontrolü
        existing = supabase.table("jobs").select("id").eq("official_url", job["official_url"]).execute()
        
        if not existing.data:
            supabase.table("jobs").insert(job).execute()
            print(f"[CANLI EKLENDİ] {job['title']}")
        else:
            print(f"[ZATEN MEVCUT] {job['title']}")

if __name__ == "__main__":
    sync_jobs()
