import json
import pathlib
import requests
import time

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

def fetch_and_save(query: str, out_path: pathlib.Path, num_to_skip: int = 0) -> bool:
    params = {
        "engine": "google_images",
        "q": query,
        "num": 15,
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
        
        skipped = 0
        for it in items:
            title = (it.get("title") or "").lower()
            source = (it.get("source") or "").lower()
            text = f"{title} {source}"
            
            if any(b in text for b in BANNED_TERMS):
                continue
                
            url = it.get("original")
            if not url:
                continue
                
            if skipped < num_to_skip:
                skipped += 1
                continue
                
            try:
                img_r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                ct = (img_r.headers.get("Content-Type") or "").lower()
                if img_r.status_code != 200 or "image" not in ct:
                    continue
                if len(img_r.content) < MIN_FILE_KB * 1024:
                    continue
                    
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(img_r.content)
                return True
            except Exception:
                continue
        return False
    except Exception as e:
        print(f"API Error: {e}")
        return False

def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    
    total_downloaded = 0
    
    for scene in data:
        num = scene["scene"]
        label = scene["label"]
        query = scene.get("query", "")
        
        folder = BASE / f"{num:03d}_{label}"
        
        existing_imgs = [p for p in folder.glob("*") if p.suffix.lower() in IMAGE_EXTS]
        count = len(existing_imgs)
        
        if count < 3 and query:
            print(f"Scene {num} ({label}) has {count} images. Searching for more...")
            
            needed = 3 - count
            for i in range(needed):
                # Try to skip the first `count + i` results to get unique images
                out_name = f"{num:03d}_img_new_{count + i + 1}.jpg"
                out_path = folder / out_name
                
                print(f"  Downloading {out_name}...")
                success = fetch_and_save(query, out_path, num_to_skip=count + i)
                
                if success:
                    print(f"  [OK] Saved {out_name}")
                    total_downloaded += 1
                else:
                    print(f"  [FAIL] Failed to find a good image for {out_name}")
                    
                time.sleep(1.0)
                
    print(f"\nTotal new images downloaded: {total_downloaded}")

if __name__ == "__main__":
    main()