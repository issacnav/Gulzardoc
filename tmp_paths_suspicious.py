import json
import pathlib

mf = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images\manifest.json")
data = json.loads(mf.read_text(encoding="utf-8"))
suspicious = {5,9,10,14,20,21,23,34,36,41,43,44,45,47,48,49,50,51,52,54,57,64,65}
for s in data:
    if s["scene"] in suspicious:
        print(f"SCENE {s['scene']:02d} {s['label']}")
        for p in s.get("images", []):
            print(p)
        print()
