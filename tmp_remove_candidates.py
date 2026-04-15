import json
import pathlib

data = json.loads(pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images\manifest.json").read_text(encoding="utf-8"))
for s in data:
    names = [pathlib.Path(p).name for p in s.get("images", [])]
    refill = [n for n in names if "_refill_" in n]
    ai = [n for n in names if "_ai" in n or "pulid" in n]
    if refill or ai:
        print(f"{s['scene']:02d} {s['label']}")
        if refill:
            print("  remove_refill:", ", ".join(refill))
        if ai:
            print("  remove_ai:", ", ".join(ai))
