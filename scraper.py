import os
import requests
import urllib3
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from supabase import create_client
from datetime import datetime, timedelta

# SSL uyarılarını gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Supabase Bağlantısı
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase bağlantı bilgileri eksik!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hatay ve ilçeleri anahtar kelimeleri
HATAY_KEYWORDS = [
    "hatay", "antakya", "iskenderun", "defne", "dörtyol", 
    "kırıkhan", "samandağ", "reyhanlı", "payas", "erzin", 
    "altınözü", "hassa", "belen", "kumlu", "yayladağı", "hmkü", "mku", "iste"
]

def clean_text(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def detect_district(text):
    text_lower = text.lower()
    for kw in HATAY_KEYWORDS:
        if kw in text_lower and kw not in ["hatay", "hmkü", "mku", "iste"]:
            return kw.capitalize()
    return "Tüm Hatay"

def detect_institution_type(text):
    t = text.lower()
    if "üniversite" in t or "rektörlük" in t or "fakülte" in t:
        return "Üniversite"
    if "belediye" in t:
        return "Belediye"
    if "bakanlık" in t or "valilik" in t or "kaymakamlık" in t or "müdürlük" in t:
        return "Bakanlık/Valilik"
    return "Kamu Kurumu"

def detect_position_type(text):
    t = text.lower()
    if "akademik" in t or "öğretim üyesi" in t or "araştırma görevlisi" in t:
        return "Akademik Personel"
    if "sözleşmeli" in t or "4/b" in t:
        return "Sözleşmeli Personel"
    if "işçi" in t or "sürekli işçi" in t:
        return "Sürekli İşçi"
    if "memur" in t:
        return "Memur"
    return "Sözleşmeli Personel"

def scrape_resmi_gazete():
    """Resmi Gazete ilanlarını SSL hatası olmadan tarar."""
    found_jobs = []
    rss_urls = [
        "https://www.resmigazete.gov.tr/rss/cesitli-ilanlar.xml",
        "https://www.resmigazete.gov.tr/rss/ilanlar.xml"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in rss_urls:
        try:
            # verify=False eklenerek SSL doğrulama hatası çözüldü
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item"):
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    full_content = f"{title} {desc}".lower()
                    
                    if any(kw in full_content for kw in HATAY_KEYWORDS):
                        clean_desc = clean_text(desc)
                        found_jobs.append({
                            "title": title[:180],
                            "institution": title.split("-")[0].strip() if "-" in title else "Hatay Kamu Kurumu",
                            "institution_type": detect_institution_type(title),
                            "district": detect_district(full_content),
                            "position_type": detect_position_type(full_content),
                            "category": detect_position_type(full_content),
                            "position_count": 1,
                            "deadline": (datetime.now() + timedelta(days=15)).isoformat(),
                            "details": clean_desc if clean_desc else f"Resmi ilan detayı: {title}",
                            "official_url": link.strip(),
                            "is_active": True
                        })
        except Exception as e:
            print(f"Resmi Gazete Tarama Hatası ({url}): {e}")
            
    return found_jobs

def scrape_hmku_duyurular():
    """Hatay Mustafa Kemal Üniversitesi resmi duyurularını canlı tarar."""
    found_jobs = []
    url = "https://www.mku.edu.tr/duyurular"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                text = link.get_text(strip=True)
                t_low = text.lower()
                if any(w in t_low for w in ["personel", "öğretim üyesi", "sözleşmeli", "alım", "kadro"]):
                    href = link['href']
                    full_url = href if href.startswith('http') else f"https://www.mku.edu.tr/{href.lstrip('/')}"
                    found_jobs.append({
                        "title": text[:180],
                        "institution": "Hatay Mustafa Kemal Üniversitesi",
                        "institution_type": "Üniversite",
                        "district": "Antakya",
                        "position_type": detect_position_type(text),
                        "category": detect_position_type(text),
                        "position_count": 1,
                        "deadline": (datetime.now() + timedelta(days=15)).isoformat(),
                        "details": f"HMKÜ Resmi Alım Duyurusu: {text}",
                        "official_url": full_url,
                        "is_active": True
                    })
    except Exception as e:
        print(f"HMKÜ Tarama Hatası: {e}")
        
    return found_jobs

def sync_jobs():
    print("Canlı Resmi Gazete & HMKÜ tarayıcısı başlatılıyor...")
    
    live_jobs = []
    live_jobs.extend(scrape_resmi_gazete())
    live_jobs.extend(scrape_hmku_duyurular())
    
    print(f"Canlı kaynaklardan {len(live_jobs)} adet ilan yakalandı.")
    
    added_count = 0
    for job in live_jobs:
        existing = supabase.table("jobs").select("id").eq("official_url", job["official_url"]).execute()
        if not existing.data:
            supabase.table("jobs").insert(job).execute()
            print(f"[YENİ CANLI İLAN EKLENDİ]: {job['title']}")
            added_count += 1
        else:
            print(f"[ZATEN MEVCUT]: {job['title']}")
            
    print(f"Tarama bitti. Veritabanına eklenen yeni ilan: {added_count}")

if __name__ == "__main__":
    sync_jobs()
