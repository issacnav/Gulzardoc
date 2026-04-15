# -*- coding: utf-8 -*-
"""
Refill only selected empty Gulzar scene folders with improved queries.

What this script does:
1) Targets ONLY the listed empty folders.
2) Uses multiple refined queries per scene (stops as soon as 3 good images are saved).
3) Filters out obvious junk/promo/stock results by title/source terms.
4) Keeps quality guardrails (large image search + min file size + min dimensions when available).
5) Copies every newly saved file into "All images" to keep the flat folder in sync.
"""

import shutil
import time
from pathlib import Path

import requests

# %% CONFIG %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
SERP_API_KEY = "efafce5ea12a988d328480d96cd2f2e872a6ce46e35bf249b6350c074c650276"
BASE_DIR = Path(r"C:\Mini project\Gulzar\gulzar_video_images")
ALL_IMAGES_DIR = Path(r"C:\Mini project\Gulzar\All images")

IMAGES_PER_SCENE = 3
RESULTS_PER_QUERY = 10
DELAY_BETWEEN_CALLS = 1.0
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")
HEADERS = {"User-Agent": "Mozilla/5.0"}
MIN_FILE_KB = 45
MIN_WIDTH = 900

# Hard reject terms to reduce ads/stock/social thumbnails.
BANNED_TERMS = {
    "shutterstock",
    "getty",
    "alamy",
    "istock",
    "pinterest",
    "instagram",
    "facebook",
    "twitter",
    "youtube thumbnail",
    "lyrics video",
    "mp3",
    "spotify",
    "jiosaavn",
    "gaana",
    "wynk",
    "amazon",
    "flipkart",
    "wallpaper",
    "clipart",
    "vector",
    "template",
    "meme",
    "ai art",
    "stock photo",
}

# Scene-specific refill plan (only the 21 folders you listed).
TARGETS = {
    "005_mumbai_car_painting_books": {
        "queries": [
            "1950s Mumbai car workshop India black and white mechanic painting",
            "vintage Indian auto garage worker painting car 1950s",
            "young man reading books in garage workshop India vintage",
        ],
        "must_have": {"mumbai", "india", "vintage", "workshop", "garage", "car"},
    },
    "010_bimal_roy_declining_health": {
        "queries": [
            "Bimal Roy director portrait 1960s black and white",
            "Bimal Roy rare photo film director",
            "Bimal Roy on set vintage",
        ],
        "must_have": {"bimal", "roy"},
    },
    "014_meena_kumari_gulzar_moon": {
        "queries": [
            "Meena Kumari Gulzar rare photo",
            "Meena Kumari portrait classic",
            "Meena Kumari poetry actress black and white",
        ],
        "must_have": {"meena", "kumari"},
    },
    "020_midnight_walk_rd_burman": {
        "queries": [
            "RD Burman Gulzar candid photo",
            "Mumbai night street vintage black and white 1970s India",
            "RD Burman Panchamda portrait vintage",
        ],
        "must_have": {"rd", "burman", "mumbai", "night", "vintage"},
    },
    "021_journey_dina_delhi_mumbai": {
        "queries": [
            "vintage Indian railway steam train 1950s India",
            "India partition refugee train 1947 historical photo",
            "old Delhi to Mumbai train journey India vintage",
        ],
        "must_have": {"india", "train", "railway", "vintage"},
    },
    "023_gulzar_rakhi_marriage_meghna": {
        "queries": [
            "Gulzar Rakhee marriage photo",
            "Gulzar with Rakhee actress vintage",
            "Gulzar with daughter Meghna Gulzar family photo",
        ],
        "must_have": {"gulzar", "rakhee", "meghna", "family"},
    },
    "034_mujhe_jaan_na_kaho_love": {
        "queries": [
            "Mujhe Jaan Na Kaho Meri Jaan song still",
            "Anubhav 1972 Geeta Dutt song scene",
            "romantic old Hindi film couple black and white gulzar lyrics",
        ],
        "must_have": {"mujhe", "jaan", "anubhav", "geeta", "gulzar"},
    },
    "041_mere_to_girdhar_gopal_bhakti": {
        "queries": [
            "Meera 1979 Hema Malini devotional scene",
            "Mere To Giridhar Gopal song Meera film",
            "Meera bhakti painting Krishna devotional classic",
        ],
        "must_have": {"meera", "girdhar", "devotional", "hema", "krishna"},
    },
    "043_childrens_songs_india": {
        "queries": [
            "Indian school children singing group assembly",
            "children singing Indian classroom choir",
            "kids music class India school",
        ],
        "must_have": {"children", "school", "singing", "india", "kids"},
    },
    "044_shekhar_kapoor_shabana_azmi": {
        "queries": [
            "Shekhar Kapur and Shabana Azmi photo",
            "Shabana Azmi Shekhar Kapur event",
            "Shabana Azmi portrait classic Bollywood",
        ],
        "must_have": {"shabana", "azmi", "shekhar", "kapur"},
    },
    "045_lakdi_ki_kathi_masoom": {
        "queries": [
            "Lakdi Ki Kaathi Masoom song scene children",
            "Masoom 1983 children song still",
            "Masoom 1983 film poster child",
        ],
        "must_have": {"lakdi", "kaathi", "masoom", "children"},
    },
    "047_chappa_chappa_charkha": {
        "queries": [
            "Chappa Chappa Charkha Chale 1942 A Love Story song still",
            "1942 A Love Story Chappa Chappa scene",
            "Anil Kapoor Manisha Koirala 1942 A Love Story song",
        ],
        "must_have": {"chappa", "charkha", "1942", "love", "story"},
    },
    "048_meghna_son_samay_grandfather": {
        "queries": [
            "Gulzar with Meghna Gulzar photo",
            "Meghna Gulzar family photo",
            "Gulzar with grandson family",
        ],
        "must_have": {"gulzar", "meghna", "family", "grandson", "samay"},
    },
    "049_hridayanath_lekin_yara_seeli": {
        "queries": [
            "Lekin 1991 Yara Seeli Seeli scene",
            "Lekin 1991 Dimple Kapadia poster",
            "Hridaynath Mangeshkar Lekin song",
        ],
        "must_have": {"lekin", "yara", "seeli", "hridaynath", "dimple"},
    },
    "050_mere_saath_jaye_na_shadow": {
        "queries": [
            "Mere Saath Jaaye Na Meri Parchhai Lekin song scene",
            "Lekin 1991 haunting scene Dimple Kapadia",
            "Lekin film shadow loneliness scene",
        ],
        "must_have": {"lekin", "parchhai", "shadow", "dimple"},
    },
    "051_goli_maar_bheje_gangster": {
        "queries": [
            "Goli Maar Bheje Mein Satya 1998 song",
            "Satya 1998 Mumbai gangster film still",
            "Manoj Bajpayee Satya Bhiku Mhatre still",
        ],
        "must_have": {"satya", "goli", "bheje", "gangster", "mumbai"},
    },
    "052_shakespeare_maqbool_omkara_haider": {
        "queries": [
            "Maqbool Omkara Haider poster collage",
            "Vishal Bhardwaj Shakespeare trilogy stills",
            "Maqbool poster Omkara poster Haider poster",
        ],
        "must_have": {"maqbool", "omkara", "haider", "shakespeare", "vishal"},
    },
    "054_gulzar_javed_akhtar_together": {
        "queries": [
            "Gulzar and Javed Akhtar together on stage",
            "Gulzar Javed Akhtar event photo",
            "Gulzar Javed Akhtar conversation",
        ],
        "must_have": {"gulzar", "javed", "akhtar", "together"},
    },
    "057_chappa_chappa_chule_chimte": {
        "queries": [
            "Chappa Chappa Charkha Chale song 1942 A Love Story",
            "Chappa Chappa lyrics Gulzar song still",
            "1942 A Love Story song scene train village",
        ],
        "must_have": {"chappa", "charkha", "1942", "gulzar"},
    },
    "064_life_mystery_time_fleeting": {
        "queries": [
            "Gulzar thoughtful portrait close up",
            "Gulzar interview reflective expression",
            "Gulzar quote about time life image",
        ],
        "must_have": {"gulzar", "time", "life", "thoughtful", "portrait"},
    },
    "065_kajrare_kajrare_bunty_babli": {
        "queries": [
            "Kajra Re song Bunty Aur Babli Aishwarya Amitabh Abhishek",
            "Kajra Re still Aishwarya Rai dance",
            "Bunty Aur Babli Kajra Re official song frame",
        ],
        "must_have": {"kajra", "bunty", "babli", "aishwarya", "amitabh", "abhishek"},
    },
}


def is_valid_result(item: dict, must_have_terms: set[str]) -> bool:
    title = (item.get("title") or "").lower()
    source = (item.get("source") or "").lower()
    text = f"{title} {source}"

    # Hard reject obvious bad sources/types.
    for term in BANNED_TERMS:
        if term in text:
            return False

    # If metadata exists, encourage scene relevance.
    if text.strip():
        if not any(t in text for t in must_have_terms):
            # Do not hard fail if dimensions are very high and metadata is weak;
            # leave room for valid images missing good titles.
            if int(item.get("w", 0) or 0) < 1200:
                return False
    return True


def fetch_image_urls(query: str, num: int = RESULTS_PER_QUERY) -> list[dict]:
    params = {
        "engine": "google_images",
        "q": query,
        "num": num,
        "ijn": 0,
        "api_key": SERP_API_KEY,
        "safe": "active",
        "gl": "in",
        "hl": "en",
        "tbs": "isz:l",  # large images
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = r.json()
        if "error" in data:
            print(f"    [SerpAPI error] {data['error']}")
            return []
        results = data.get("images_results", [])
        out = []
        for it in results:
            url = it.get("original")
            if not url:
                continue
            out.append(
                {
                    "url": url,
                    "title": it.get("title", ""),
                    "source": it.get("source", ""),
                    "w": it.get("original_width", 0) or 0,
                    "h": it.get("original_height", 0) or 0,
                }
            )
        # Prefer wider images first.
        out.sort(key=lambda x: int(x.get("w", 0)), reverse=True)
        return out
    except Exception as exc:
        print(f"    [API error] {exc}")
        return []


def download_image(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        ct = r.headers.get("Content-Type", "").lower()
        if r.status_code != 200 or "image" not in ct:
            return False
        data = r.content
        if len(data) < MIN_FILE_KB * 1024:
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def scene_number(folder_name: str) -> str:
    return folder_name.split("_", 1)[0]


def refill_folder(folder_name: str, cfg: dict) -> int:
    folder = BASE_DIR / folder_name
    folder.mkdir(exist_ok=True)
    num = scene_number(folder_name)

    # Recount if folder got filled manually.
    existing = [f for f in folder.glob("*") if f.suffix.lower() in IMAGE_EXTS]
    if len(existing) >= IMAGES_PER_SCENE:
        print(f"[{num}] {folder_name} already has {len(existing)} image(s), skipping.")
        return 0

    saved = 0
    seen_urls = set()
    must_have = set(cfg.get("must_have", set()))

    print(f"\n[{num}] {folder_name}")
    for query in cfg["queries"]:
        if saved >= IMAGES_PER_SCENE:
            break

        print(f"  Query: {query}")
        results = fetch_image_urls(query, num=RESULTS_PER_QUERY)

        for it in results:
            if saved >= IMAGES_PER_SCENE:
                break
            url = it["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Metadata + relevance filter.
            if int(it.get("w", 0)) and int(it.get("w", 0)) < MIN_WIDTH:
                continue
            if not is_valid_result(it, must_have):
                continue

            ext = Path(url.split("?")[0]).suffix.lower()
            if ext not in IMAGE_EXTS:
                ext = ".jpg"
            dest = folder / f"{num}_refill_{saved+1}{ext}"

            if download_image(url, dest):
                saved += 1
                # Keep All images folder in sync.
                ALL_IMAGES_DIR.mkdir(exist_ok=True)
                shutil.copy2(dest, ALL_IMAGES_DIR / dest.name)
                print(f"    ' {dest.name} [{it.get('w', '?')}x{it.get('h', '?')}]")
            time.sleep(0.25)

        time.sleep(DELAY_BETWEEN_CALLS)

    print(f"  Saved in {folder_name}: {saved}")
    return saved


def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    ALL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    total_saved = 0
    total_calls_est = sum(len(v["queries"]) for v in TARGETS.values())
    print(f"Target folders: {len(TARGETS)}")
    print(f"Max API calls (worst case): {total_calls_est}")

    for folder_name in TARGETS:
        total_saved += refill_folder(folder_name, TARGETS[folder_name])

    print("\n" + "=" * 56)
    print(f"Total new images saved: {total_saved}")
    print(f"Scene folder root      : {BASE_DIR}")
    print(f"Flat folder synced     : {ALL_IMAGES_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()

