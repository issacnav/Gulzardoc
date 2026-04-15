import json
import pathlib
import re

mf = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images\manifest.json")
data = json.loads(mf.read_text(encoding="utf-8"))

# Scenes likely requiring manual visual check due to synthetic/refill contamination
suspicious = []
for s in data:
    names=[pathlib.Path(p).name for p in s.get('images',[])]
    if any('_refill_' in n or '_ai' in n or '_serp' in n for n in names):
        suspicious.append((s['scene'], s['label'], names))

print('SUSPICIOUS_SCENES', len(suspicious))
for scene,label,names in suspicious:
    print(f"\n{scene:02d} {label}")
    for n in names:
        print(' ', n)
