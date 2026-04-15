# -*- coding: utf-8 -*-
import json
import pathlib
import shutil
import time
import requests

BASE = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images")
MANIFEST = BASE / "manifest.json"
REFILL = pathlib.Path(r"C:\Mini project\Gulzar\refill_empty_folders.py")

EXTS = {".jpg", ".jpeg", ".png", ".webp"}
BANNED = [
    "shutterstock", "getty", "alamy", "istock", "pinterest", "instagram",
    "facebook", "twitter", "youtube", "lyrics", "spotify", "jiosaavn",
    "gaana", "wynk", "vector", "clipart", "template", "meme",
]


def get_serp_key() -> str:
    txt = REFILL.read_text(encoding="utf-8")
    marker = "SERP_API_KEY = \""
    i = txt.find(marker)
    if i == -1:
        raise RuntimeError("SERP_API_KEY not found")
    j = txt.find('"', i + len(marker))
    return txt[i + len(marker):j]


def fetch_and_save(query: str, out_path: pathlib.Path, serp_key: str, prefer_terms=None) -> bool:
    prefer_terms = [t.lower() for t in (prefer_terms or [])]
    params = {
        "engine": "google_images",
        "q": query,
        "num": 10,
        "ijn": 0,
        "api_key": serp_key,
        "safe": "active",
        "gl": "in",
        "hl": "en",
        "tbs": "isz:l",
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = r.json()
        items = data.get("images_results", [])
        # rank by preferred terms + width
        ranked = []
        for it in items:
            title = (it.get("title") or "").lower()
            source = (it.get("source") or "").lower()
            text = f"{title} {source}"
            if any(b in text for b in BANNED):
                continue
            score = 0
            for t in prefer_terms:
                if t in text:
                    score += 2
            if "poster" in text:
                score += 2
            if "official" in text:
                score += 1
            score += int((it.get("original_width") or 0) // 500)
            ranked.append((score, it))
        ranked.sort(key=lambda x: x[0], reverse=True)

        for _, it in ranked:
            url = it.get("original")
            if not url:
                continue
            try:
                img = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                ct = (img.headers.get("Content-Type") or "").lower()
                if img.status_code != 200 or "image" not in ct:
                    continue
                if len(img.content) < 45 * 1024:
                    continue
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(img.content)
                return True
            except Exception:
                continue
        return False
    except Exception:
        return False


def scene_folder(scene):
    return BASE / f"{scene['scene']:03d}_{scene['label']}"


def remove_ai_files(folder: pathlib.Path):
    removed = []
    for f in folder.glob("*"):
        if f.suffix.lower() in EXTS and ("ai" in f.stem or "pulid" in f.stem):
            f.unlink(missing_ok=True)
            removed.append(str(f))
    return removed


def main():
    serp_key = get_serp_key()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_scene = {s["scene"]: s for s in data}

    # 1) Add scene 36 v2 images to manifest
    s36 = by_scene[36]
    f36 = scene_folder(s36)
    add36 = [str(f36 / "036_img_ai_v2a.jpg"), str(f36 / "036_img_ai_v2b.jpg")]

    # 2) Add provided 41.jpg into scene 41
    src41 = pathlib.Path(r"C:\Users\naval\Downloads\41.jpg")
    s41 = by_scene[41]
    f41 = scene_folder(s41)
    dst41 = f41 / "041_img_user41.jpg"
    if src41.exists():
        f41.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src41, dst41)

    # 3) Replace with SERP results for requested scenes
    tasks = [
        (47, "1942 A Love Story official movie poster", ["1942", "love story", "poster", "official"], "047_img_serp_poster1.jpg"),
        (48, "Meghna Gulzar with Gulzar family photo", ["meghna", "gulzar", "family"], "048_img_serp1.jpg"),
        (34, "Anubhav 1972 movie poster Gulzar Geeta Dutt", ["anubhav", "1972", "poster"], "034_img_serp_poster1.jpg"),
        (41, "Meera 1979 Hema Malini official movie poster", ["meera", "1979", "poster"], "041_img_serp_poster1.jpg"),
        (45, "Masoom 1983 official movie poster", ["masoom", "1983", "poster"], "045_img_serp_poster1.jpg"),
        (49, "Lekin 1991 official movie poster Dimple Kapadia", ["lekin", "1991", "poster"], "049_img_serp_poster1.jpg"),
        (50, "Lekin 1991 movie still shadow scene", ["lekin", "1991"], "050_img_serp1.jpg"),
        (51, "Satya 1998 official movie poster Ram Gopal Varma", ["satya", "1998", "poster"], "051_img_serp_poster1.jpg"),
        (52, "Maqbool Omkara Haider movie posters collage", ["maqbool", "omkara", "haider", "poster"], "052_img_serp_poster1.jpg"),
    ]

    # remove AI in targeted replace scenes
    target_replace_scenes = {t[0] for t in tasks}
    for sn in target_replace_scenes:
        sf = scene_folder(by_scene[sn])
        if sf.exists():
            remove_ai_files(sf)

    # fetch replacements
    for sn, q, pref, fname in tasks:
        sf = scene_folder(by_scene[sn])
        out = sf / fname
        ok = fetch_and_save(q, out, serp_key, prefer_terms=pref)
        print(f"scene {sn}: {'saved' if ok else 'failed'} -> {out.name}")
        time.sleep(1.0)

    # rebuild manifest using existing listed + new local files ordering by name
    for s in data:
        sf = scene_folder(s)
        if not sf.exists():
            continue
        existing = [str(p) for p in sorted(sf.iterdir(), key=lambda p: p.name) if p.suffix.lower() in EXTS]
        # keep max 6 to avoid bloating
        s["images"] = existing[:6]

    # ensure scene 36 has v2 images included (even if ordering changed)
    s36_imgs = by_scene[36]["images"]
    for p in add36:
        if pathlib.Path(p).exists() and p not in s36_imgs:
            s36_imgs.append(p)

    # ensure scene 41 includes user image
    if dst41.exists() and str(dst41) not in by_scene[41]["images"]:
        by_scene[41]["images"].append(str(dst41))

    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("manifest updated")


if __name__ == "__main__":
    main()
