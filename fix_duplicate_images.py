import json
import pathlib
import hashlib
import requests
import time
import os

BASE = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images")
MANIFEST = BASE / "manifest.json"
SERP_API_KEY = "efafce5ea12a988d328480d96cd2f2e872a6ce46e35bf249b6350c074c650276"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MIN_FILE_KB = 45

BANNED_TERMS = {
    "shutterstock", "getty", "alamy", "istock", "pinterest", "instagram",
    "facebook", "twitter", "youtube thumbnail", "lyrics video", "mp3",
    "spotify", "jiosaavn", "gaana", "wynk", "amazon", "flipkart",
    "wallpaper", "clipart", "vector", "template", "meme", "ai art", "stock photo"
}

def get_hash(path):
    return hashlib.md5(path.read_bytes()).hexdigest()

def clean_duplicates(folder):
    """Deletes any images in the folder that have the same hash as another image.
    Prioritizes keeping original images over *img_new* images.
    Returns the number of images left, and a set of hashes present."""
    files = [f for f in folder.glob("*") if f.suffix.lower() in IMAGE_EXTS]
    
    # Sort files so that we keep originals (not containing "img_new") over "img_new"
    # and lower numbers over higher numbers
    files.sort(key=lambda x: (1 if "img_new" in x.name else 0, x.name))
    
    kept_hashes = set()
    kept_files = []
    
    for f in files:
        h = get_hash(f)
        if h in kept_hashes:
            print(f"    Deleting duplicate: {f.name}")
            f.unlink()
        else:
            kept_hashes.add(h)
            kept_files.append(f)
            
    return len(kept_files), kept_hashes

def fetch_search_results(query: str):
    params = {
        "engine": "google_images",
        "q": query,
        "num": 20,
        "ijn": 0,
        "api_key": SERP_API_KEY,
        "safe": "active",
        "gl": "in",
        "hl": "en",
        "tbs": "isz:l",
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = r.json()
        items = data.get("images_results", [])
        # Rank items by width to get good quality
        items.sort(key=lambda x: int(x.get("original_width", 0) or 0), reverse=True)
        return items
    except Exception as e:
        print(f"    API Error: {e}")
        return []

def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    
    total_downloaded = 0
    
    for scene in data:
        num = scene["scene"]
        label = scene["label"]
        query = scene.get("query", "")
        
        folder = BASE / f"{num:03d}_{label}"
        if not folder.exists():
            continue
            
        print(f"\nScene {num} ({label}): Checking duplicates...")
        count, existing_hashes = clean_duplicates(folder)
        
        if count < 3 and query:
            print(f"  Only {count} unique images left. Searching for {3 - count} more...")
            items = fetch_search_results(query)
            
            needed = 3 - count
            for it in items:
                if needed <= 0:
                    break
                    
                title = (it.get("title") or "").lower()
                source = (it.get("source") or "").lower()
                text = f"{title} {source}"
                
                if any(b in text for b in BANNED_TERMS):
                    continue
                    
                url = it.get("original")
                if not url:
                    continue
                    
                # Download and check hash
                try:
                    img_r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    ct = (img_r.headers.get("Content-Type") or "").lower()
                    if img_r.status_code != 200 or "image" not in ct:
                        continue
                    if len(img_r.content) < MIN_FILE_KB * 1024:
                        continue
                        
                    # Temp file
                    out_name = f"{num:03d}_img_new_{int(time.time())}.jpg"
                    out_path = folder / out_name
                    out_path.write_bytes(img_r.content)
                    
                    h = get_hash(out_path)
                    if h in existing_hashes:
                        # duplicate image!
                        out_path.unlink()
                    else:
                        # Success!
                        existing_hashes.add(h)
                        needed -= 1
                        total_downloaded += 1
                        print(f"    [OK] Saved unique image: {out_name}")
                        
                except Exception:
                    continue

if __name__ == "__main__":
    main()