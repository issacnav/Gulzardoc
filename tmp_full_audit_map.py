import json, pathlib, re
mf = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images\manifest.json")
data = json.loads(mf.read_text(encoding="utf-8"))
pat_original = re.compile(r"^\d{3}_img\d+\.(jpg|jpeg|png|webp)$", re.I)
rows=[]
for s in data:
    names=[pathlib.Path(p).name for p in s.get('images',[])]
    kinds=[]
    for n in names:
        if '_refill_' in n:
            k='refill'
        elif '_ai' in n or 'pulid' in n:
            k='ai'
        elif '_serp' in n:
            k='serp'
        elif pat_original.match(n):
            k='original'
        elif 'user41' in n:
            k='user'
        else:
            k='other'
        kinds.append((n,k))
    rows.append((s['scene'],s['label'],kinds))

for scene,label,kinds in rows:
    print(f"{scene:02d} {label}")
    for n,k in kinds:
        print(f"  {k:8} {n}")
