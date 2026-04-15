# -*- coding: utf-8 -*-
"""
Gulzar Documentary - Video Image Scraper
Budget: 1 SerpAPI call per scene = 70 calls total (out of 250 remaining).
Each call requests LARGE images and fetches 6 results; best 3 are kept.

Output: C:\\Mini project\\Gulzar\\gulzar_video_images\\
  001_title/  002_intro/ ...  storyboard.html  manifest.json
"""

import json, time, requests
from pathlib import Path
from docx import Document

# ?? CONFIG ????????????????????????????????????????????????????????????????????
SERP_API_KEY     = "efafce5ea12a988d328480d96cd2f2e872a6ce46e35bf249b6350c074c650276"
TRANSCRIPT_PATH  = Path(r"C:\Users\naval\Downloads\marathi trascribe.docx")
OUTPUT_DIR       = Path(r"C:\Mini project\Gulzar\gulzar_video_images")
IMAGES_PER_SCENE = 3      # images to keep per scene
FETCH_PER_CALL   = 6      # results requested per API call (gives options)
DELAY            = 1.2    # seconds between API calls
IMAGE_EXTS       = (".jpg", ".jpeg", ".png", ".webp")
HEADERS          = {"User-Agent": "Mozilla/5.0"}
MIN_FILE_KB      = 40     # reject files smaller than this (low-res guard)

# ?? SCENE MAP ?????????????????????????????????????????????????????????????????
# ONE query per scene  ==>  ONE API call per scene  ==>  70 calls total.
# Queries are English; chosen to get the closest visual to what is narrated.
SCENES = [
    {"para_idx": 0,   "label": "title_beyond_emotions",
     "query": "Gulzar poet India iconic portrait white kurta beard"},
    {"para_idx": 2,   "label": "gulzar_symbol_hindi_cinema",
     "query": "Gulzar lyricist director Bollywood India stage award ceremony"},
    {"para_idx": 3,   "label": "awards_oscar_phalke_padma",
     "query": "Gulzar Oscar Award 2009 Jai Ho Academy Award ceremony India"},
    {"para_idx": 4,   "label": "birth_dina_partition_1947",
     "query": "India Pakistan partition 1947 Punjab refugees border displacement train"},
    {"para_idx": 5,   "label": "mumbai_car_painting_books",
     "query": "vintage car workshop garage 1950s India worker painting automobile"},
    {"para_idx": 6,   "label": "bimal_roy_bandini_film",
     "query": "Bimal Roy film director India vintage portrait Bollywood 1960s"},
    {"para_idx": 7,   "label": "mora_gora_ang_lai_le_song",
     "query": "Bandini 1963 Hindi film Nutan song river scene India"},
    {"para_idx": 9,   "label": "tagore_guru_bimal_roy",
     "query": "Rabindranath Tagore portrait Nobel laureate India Bengal"},
    {"para_idx": 10,  "label": "bimal_roy_affection_flight",
     "query": "Indian Airlines vintage aircraft 1960s India retro plane airport"},
    {"para_idx": 11,  "label": "bimal_roy_declining_health",
     "query": "Bimal Roy Indian film director portrait last days Bollywood 1966"},
    {"para_idx": 12,  "label": "poetry_vs_film_song",
     "query": "Bollywood music recording studio 1960s India lyricist composer session"},
    {"para_idx": 13,  "label": "lata_mangeshkar_recording",
     "query": "Lata Mangeshkar recording studio microphone India portrait singing"},
    {"para_idx": 16,  "label": "hemant_kumar_mumbai_house",
     "query": "Hemant Kumar singer India Bengali portrait Bollywood music"},
    {"para_idx": 17,  "label": "meena_kumari_gulzar_moon",
     "query": "Meena Kumari actress India portrait iconic tragic queen Bollywood"},
    {"para_idx": 18,  "label": "meena_kumari_poetry_notebooks",
     "query": "Meena Kumari actress India writing poetry handwritten notebook vintage"},
    {"para_idx": 19,  "label": "rd_burman_song_dispute",
     "query": "RD Burman Pancham composer India portrait Bollywood music studio"},
    {"para_idx": 20,  "label": "asha_bhosle_lauta_do",
     "query": "Asha Bhosle singer India portrait recording studio microphone"},
    {"para_idx": 21,  "label": "ijaazat_mera_kuch_samaan",
     "query": "Ijaazat 1987 Gulzar film Rekha Naseeruddin Shah poster India"},
    {"para_idx": 22,  "label": "love_letters_memories",
     "query": "old love letters tied ribbon nostalgia vintage India keepsakes memory"},
    {"para_idx": 26,  "label": "midnight_walk_rd_burman",
     "query": "Mumbai midnight street 1970s vintage India night road old Bollywood era"},
    {"para_idx": 30,  "label": "journey_dina_delhi_mumbai",
     "query": "vintage steam train journey India 1960s railway romantic landscape"},
    {"para_idx": 34,  "label": "beautiful_lyrics_rd_burman",
     "query": "RD Burman Gulzar music collaboration India Bollywood 1970s studio"},
    {"para_idx": 35,  "label": "gulzar_rakhi_marriage_meghna",
     "query": "Rakhi actress Bollywood India portrait 1970s films"},
    {"para_idx": 36,  "label": "tujhse_naraaz_nahi_zindagi",
     "query": "Masoom 1983 Gulzar film Naseeruddin Shah Jugal Hansraj child scene"},
    {"para_idx": 37,  "label": "separation_aandhi_rakhi",
     "query": "Aandhi 1975 Gulzar film poster Suchitra Sen Sanjeev Kumar India"},
    {"para_idx": 40,  "label": "quiet_grief_incomplete_relation",
     "query": "Masoom 1983 film India sad emotional child Gulzar scene"},
    {"para_idx": 44,  "label": "ghazal_jagjit_singh_loneliness",
     "query": "Jagjit Singh ghazal singer India portrait concert stage performance"},
    {"para_idx": 47,  "label": "sham_se_ankh_mein_nami_ghazal",
     "query": "Jagjit Singh Gulzar ghazal concert India stage 1999 Marasim album"},
    {"para_idx": 48,  "label": "gulzar_writing_soul",
     "query": "Gulzar poet writing pen notebook India close-up portrait thoughtful"},
    {"para_idx": 52,  "label": "gulzar_ghazals_journey",
     "query": "Indian mushaira poetry recitation stage India ghazal evening audience"},
    {"para_idx": 53,  "label": "directing_mere_apne",
     "query": "Mere Apne 1971 Gulzar film poster Vinod Khanna Meena Kumari India"},
    {"para_idx": 54,  "label": "gulzar_acted_film",
     "query": "Gulzar director India film set old photograph behind camera"},
    {"para_idx": 56,  "label": "mirza_ghalib_doordarshan",
     "query": "Mirza Ghalib 1988 Doordarshan serial Naseeruddin Shah India TV classic"},
    {"para_idx": 57,  "label": "mujhe_jaan_na_kaho_love",
     "query": "Gulzar romantic love song poetry India vintage couple film scene"},
    {"para_idx": 58,  "label": "geeta_dutt_kanu_roy",
     "query": "Geeta Dutt singer India portrait vintage Bollywood recording studio"},
    {"para_idx": 60,  "label": "gulzar_master_of_words",
     "query": "Gulzar poet India stage shayari mushaira thoughtful portrait"},
    {"para_idx": 61,  "label": "aandhi_1975_ban_indira",
     "query": "Aandhi 1975 Gulzar film India political Suchitra Sen poster ban"},
    {"para_idx": 65,  "label": "dil_dhundta_hai_mausam",
     "query": "Mausam 1975 Gulzar film Sanjeev Kumar Sharmila Tagore India poster"},
    {"para_idx": 68,  "label": "koshish_sanjeev_sharmila_jaya",
     "query": "Koshish 1972 Gulzar film Sanjeev Kumar Jaya Bhaduri deaf mute India"},
    {"para_idx": 69,  "label": "meera_film_vani_jairam",
     "query": "Meera 1979 Gulzar film Hema Malini India poster devotional bhakti"},
    {"para_idx": 70,  "label": "mere_to_girdhar_gopal_bhakti",
     "query": "Meera bhakti India painting saint devotional Hema Malini temple 1979"},
    {"para_idx": 72,  "label": "sahir_prasoon_swanand",
     "query": "Sahir Ludhianvi poet lyricist India portrait Bollywood literature"},
    {"para_idx": 73,  "label": "childrens_songs_india",
     "query": "Indian school children singing classroom creative Gulzar kids songs"},
    {"para_idx": 74,  "label": "shekhar_kapoor_shabana_azmi",
     "query": "Shabana Azmi actress India stage literary event portrait Bollywood"},
    {"para_idx": 75,  "label": "lakdi_ki_kathi_masoom",
     "query": "Lakdi Ki Kaathi Masoom 1983 India children song horse toy school"},
    {"para_idx": 79,  "label": "sare_ke_sare_gama_kitaab",
     "query": "Kitaab 1977 Gulzar film India children music school scene"},
    {"para_idx": 83,  "label": "chappa_chappa_charkha",
     "query": "1942 A Love Story India 1994 film Anil Kapoor Manisha Koirala poster"},
    {"para_idx": 85,  "label": "meghna_son_samay_grandfather",
     "query": "Meghna Gulzar director India portrait with father Gulzar family"},
    {"para_idx": 87,  "label": "hridayanath_lekin_yara_seeli",
     "query": "Lekin 1991 Gulzar film Dimple Kapadia India supernatural poster"},
    {"para_idx": 88,  "label": "mere_saath_jaye_na_shadow",
     "query": "Lekin 1991 India ghost film scene shadow loneliness supernatural"},
    {"para_idx": 89,  "label": "goli_maar_bheje_gangster",
     "query": "Satya 1998 Ram Gopal Varma Mumbai gangster underworld film India"},
    {"para_idx": 90,  "label": "shakespeare_maqbool_omkara_haider",
     "query": "Maqbool Omkara Haider Vishal Bhardwaj Shakespeare trilogy India Bollywood"},
    {"para_idx": 91,  "label": "bidi_jalai_le_omkara",
     "query": "Bidi Jalai Le Omkara 2006 Bollywood film song dance India"},
    {"para_idx": 92,  "label": "gulzar_javed_akhtar_together",
     "query": "Gulzar Javed Akhtar together stage India literary event poets friends"},
    {"para_idx": 93,  "label": "shabana_poetry_difference",
     "query": "Shabana Azmi Gulzar Javed Akhtar India literary event stage together"},
    {"para_idx": 96,  "label": "angoor_comedy_sanjeev_deven",
     "query": "Angoor 1982 Gulzar film comedy poster Sanjeev Kumar Deven Verma India"},
    {"para_idx": 97,  "label": "chappa_chappa_chule_chimte",
     "query": "Chappa Chappa Charkha Chale 1942 Love Story Anil Kapoor India 1994"},
    {"para_idx": 98,  "label": "parichay_jitendra_amitabh",
     "query": "Parichay 1972 Gulzar film India Jitendra poster Bollywood"},
    {"para_idx": 99,  "label": "gulzar_poetry_books_legacy",
     "query": "Gulzar poetry book collection India shelf Urdu Hindi literature"},
    {"para_idx": 103, "label": "chaiyya_chaiyya_train_dil_se",
     "query": "Chaiyya Chaiyya Dil Se 1998 Shah Rukh Khan Malaika Arora train rooftop"},
    {"para_idx": 104, "label": "translation_32_languages",
     "query": "Kusumagraj Marathi poet India portrait Nagpur literary Vishnu Waman Shirwadkar"},
    {"para_idx": 105, "label": "satrangi_re_dil_se",
     "query": "Satrangi Re Dil Se 1998 Mani Ratnam AR Rahman Shah Rukh Khan India song"},
    {"para_idx": 109, "label": "gulzar_shabd_malhar_personality",
     "query": "Gulzar white kurta elderly India poet stage speech iconic award"},
    {"para_idx": 110, "label": "life_mystery_time_fleeting",
     "query": "Gulzar contemplative poet India interview thoughtful close-up elderly"},
    {"para_idx": 113, "label": "kajrare_kajrare_bunty_babli",
     "query": "Kajrare Kajrare Bunty Babli 2005 Aishwarya Amitabh Abhishek dance"},
    {"para_idx": 114, "label": "school_prayer_song",
     "query": "Indian school children morning prayer assembly hall India singing"},
    {"para_idx": 115, "label": "binaca_geetmala_radio",
     "query": "Binaca Geetmala Ameen Sayani radio India 1970s vintage countdown Bollywood"},
    {"para_idx": 116, "label": "jai_ho_slumdog_ar_rahman_oscar",
     "query": "Jai Ho Slumdog Millionaire AR Rahman Oscar 2009 Academy Award India"},
    {"para_idx": 118, "label": "kabhi_kabhi_lagta_closing",
     "query": "Gulzar reciting poetry India stage audience evening mushaira iconic"},
    {"para_idx": 121, "label": "gulzar_beyond_emotions_conclusion",
     "query": "Gulzar India legend poet smiling stage speech iconic portrait elderly"},
]


# ?? HELPERS ???????????????????????????????????????????????????????????????????

def load_transcript():
    doc = Document(TRANSCRIPT_PATH)
    return {i: p.text.strip() for i, p in enumerate(doc.paragraphs) if p.text.strip()}


def sanitize(name):
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name).strip("_")


def fetch_images(query, num=6):
    """One SerpAPI call; returns results sorted widest-first."""
    params = {
        "engine":  "google_images",
        "q":       query,
        "num":     num,
        "ijn":     0,
        "api_key": SERP_API_KEY,
        "safe":    "active",
        "gl":      "in",
        "hl":      "en",
        "tbs":     "isz:l",   # large images only
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = r.json()
        if "error" in data:
            print(f"    [SerpAPI error] {data['error']}")
            return []
        items = data.get("images_results", [])
        out = []
        for it in items:
            url = it.get("original")
            if url:
                out.append({
                    "url":   url,
                    "thumb": it.get("thumbnail", ""),
                    "w":     it.get("original_width", 0),
                    "h":     it.get("original_height", 0),
                })
        out.sort(key=lambda x: x["w"], reverse=True)
        return out
    except Exception as e:
        print(f"    [API error] {e}")
        return []


def download(url, dest):
    """Download and reject files that are too small (thumbnails/icons)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        ct = r.headers.get("Content-Type", "")
        if r.status_code != 200 or "image" not in ct:
            return False
        data = r.content
        if len(data) < MIN_FILE_KB * 1024:
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def scrape_scene(num, scene, scene_dir):
    query = scene["query"]
    results = fetch_images(query, num=FETCH_PER_CALL)
    saved = 0
    for i, item in enumerate(results):
        if saved >= IMAGES_PER_SCENE:
            break
        url = item["url"]
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in IMAGE_EXTS:
            ext = ".jpg"
        dest = scene_dir / f"{num:03d}_img{i+1}{ext}"
        if dest.exists():
            saved += 1
            continue
        if download(url, dest):
            saved += 1
            w, h = item["w"], item["h"]
            dim = f"{w}x{h}" if w else "?"
            print(f"      [{dim}] {dest.name}")
        time.sleep(0.25)
    return saved


# ?? STORYBOARD HTML ???????????????????????????????????????????????????????????

def write_storyboard(entries):
    css = (
        "body{font-family:system-ui,sans-serif;max-width:1400px;margin:0 auto;"
        "padding:1.5rem;background:#1a1a2e;color:#eee}"
        "h1{font-size:1.8rem;color:#e2b96f}"
        "p.sub{color:#888;font-size:.85rem;margin-bottom:2rem}"
        ".scene{display:grid;grid-template-columns:280px 1fr;gap:1.5rem;"
        "margin-bottom:1.5rem;border:1px solid #333;border-radius:10px;"
        "padding:1.25rem;background:#16213e}"
        ".num{font-size:2rem;font-weight:700;color:#e2b96f}"
        ".lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#555;margin:.25rem 0 .75rem}"
        ".txt{font-size:.9rem;line-height:1.7;color:#ccc;border-left:3px solid #e2b96f;"
        "padding-left:.75rem;margin-bottom:.5rem;font-family:serif}"
        ".q{font-size:.7rem;color:#555}"
        ".imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}"
        ".card{border-radius:6px;overflow:hidden;background:#0f3460}"
        ".card img{width:100%;height:160px;object-fit:cover;object-position:top center;display:block}"
        ".card p{font-size:10px;padding:4px 6px;margin:0;color:#888;"
        "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    )
    lines = [
        '<!DOCTYPE html><html><head><meta charset="utf-8">',
        "<title>Gulzar Documentary Storyboard</title>",
        f"<style>{css}</style></head><body>",
        "<h1>Gulzar Documentary - Visual Storyboard</h1>",
        '<p class="sub">Images matched paragraph-by-paragraph to the Marathi transcript.</p>',
    ]
    for e in entries:
        n, scene, text, imgs = e["num"], e["scene"], e["text"], e["images"]
        lbl = scene["label"].replace("_", " ")
        lines.append('<div class="scene">')
        lines.append("<div>")
        lines.append(f'<div class="num">#{n:02d}</div>')
        lines.append(f'<div class="lbl">{lbl}</div>')
        if text:
            excerpt = text[:280] + ("..." if len(text) > 280 else "")
            lines.append(f'<div class="txt">{excerpt}</div>')
        lines.append(f'<div class="q">Search: {scene["query"]}</div>')
        lines.append("</div>")
        lines.append('<div class="imgs">')
        for img in imgs:
            rel = img.relative_to(OUTPUT_DIR)
            lines.append(
                f'<div class="card"><img src="{rel}" loading="lazy">'
                f"<p>{img.stem}</p></div>"
            )
        if not imgs:
            lines.append('<p style="color:#555;font-size:.8rem">No images downloaded.</p>')
        lines.append("</div></div>")
    lines.append("</body></html>")
    out = OUTPUT_DIR / "storyboard.html"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Storyboard  -> {out}")


def write_manifest(entries):
    data = [
        {
            "scene":        e["num"],
            "label":        e["scene"]["label"],
            "text_marathi": e["text"],
            "query":        e["scene"]["query"],
            "images":       [str(i) for i in e["images"]],
        }
        for e in entries
    ]
    out = OUTPUT_DIR / "manifest.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Manifest    -> {out}")


# ?? MAIN ?????????????????????????????????????????????????????????????????????

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paras = load_transcript()
    total_scenes = len(SCENES)
    print(f"Transcript paragraphs : {len(paras)}")
    print(f"Scenes to scrape      : {total_scenes}")
    print(f"API calls planned     : {total_scenes}  (1 per scene)\n")

    entries = []
    total_images = 0

    for n, scene in enumerate(SCENES, 1):
        label     = scene["label"]
        scene_dir = OUTPUT_DIR / f"{n:03d}_{label}"
        scene_dir.mkdir(exist_ok=True)
        para_text = paras.get(scene["para_idx"], "")

        print(f"[{n:02d}/{total_scenes}] {label}")
        print(f"  Query : {scene['query']}")

        saved = scrape_scene(n, scene, scene_dir)
        total_images += saved
        status = f"{saved} image(s)" if saved else "NONE"
        print(f"  Saved : {status}")

        imgs = [f for f in sorted(scene_dir.glob("*")) if f.suffix.lower() in IMAGE_EXTS]
        entries.append({"num": n, "scene": scene, "text": para_text, "images": imgs})
        time.sleep(DELAY)

    print(f"\n{'='*55}")
    print(f"Scenes scraped : {total_scenes}")
    print(f"Images saved   : {total_images}")
    print(f"Output folder  : {OUTPUT_DIR}")
    write_storyboard(entries)
    write_manifest(entries)
    print("\nDone! Open storyboard.html in your browser.")


if __name__ == "__main__":
    main()
