# -*- coding: utf-8 -*-
"""Update manifest.json and regenerate storyboard.html with AI-generated images."""
import json, pathlib

BASE    = pathlib.Path(r"C:\Mini project\Gulzar\gulzar_video_images")
MF_PATH = BASE / "manifest.json"
EXTS    = {".jpg", ".jpeg", ".png", ".webp"}

# ── 1. UPDATE MANIFEST ────────────────────────────────────────────────────────
data = json.loads(MF_PATH.read_text(encoding="utf-8"))

updated = 0
for scene in data:
    num   = scene["scene"]
    label = scene["label"]
    folder = BASE / f"{num:03d}_{label}"
    if not folder.exists():
        continue

    # Existing listed paths that are still on disk
    existing_listed = [p for p in scene.get("images", []) if pathlib.Path(p).exists()]

    # Any new images in this folder not already in the list
    new_imgs = sorted(
        str(f) for f in folder.iterdir()
        if f.suffix.lower() in EXTS
        and str(f) not in existing_listed
    )

    new_list = existing_listed + new_imgs
    if new_list != scene.get("images", []):
        scene["images"] = new_list
        updated += 1

MF_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"manifest.json updated — {updated} scenes changed")

total    = sum(len(s["images"]) for s in data)
has_any  = sum(1 for s in data if s["images"])
zero     = [s["scene"] for s in data if not s["images"]]
print(f"total image paths : {total}")
print(f"scenes with images: {has_any}/70")
print(f"scenes still empty: {zero}")

# ── 2. REGENERATE STORYBOARD HTML ─────────────────────────────────────────────
CSS = (
    # Olive Leaf:#606c38  Black Forest:#283618  Cornsilk:#fefae0  Light Caramel:#dda15e  Copper:#bc6c25
    "body{font-family:system-ui,sans-serif;max-width:1400px;margin:0 auto;"
    "padding:1.5rem;background:#283618;color:#fefae0}"
    "h1{font-size:1.8rem;color:#dda15e}"
    "p.sub{color:#a0a87a;font-size:.85rem;margin-bottom:2rem}"
    ".scene{display:grid;grid-template-columns:300px 1fr;gap:1.5rem;"
    "margin-bottom:1.5rem;border:1px solid #606c38;border-radius:10px;"
    "padding:1.25rem;background:#1e2a10;box-shadow:0 4px 6px rgba(0,0,0,0.4)}"
    ".num{font-size:2rem;font-weight:700;color:#dda15e}"
    ".lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#a0a87a;margin:.25rem 0 .6rem}"
    ".txt{font-size:.88rem;line-height:1.7;color:#e8dfc0;border-left:3px solid #bc6c25;"
    "padding-left:.75rem;margin-bottom:.5rem;font-family:serif}"
    ".q{font-size:.68rem;color:#7a8a50;margin-top:.4rem}"
    ".imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;align-items:start}"
    ".card{border-radius:6px;overflow:hidden;background:#2d3d18;position:relative;border:1px solid #606c38;box-shadow:0 2px 4px rgba(0,0,0,0.3)}"
    ".card img{width:100%;height:150px;object-fit:cover;object-position:top center;display:block;cursor:pointer;transition:opacity 0.3s;}"
    ".card img:hover{opacity:0.82;}"
    ".card p{font-size:11px;padding:6px 8px;margin:0;color:#c8b890;"
    "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".badge{position:absolute;top:5px;right:5px;background:#bc6c25;color:#fefae0;"
    "font-size:9px;font-weight:700;padding:2px 5px;border-radius:3px}"
    ".empty{color:#7a8a50;font-size:.8rem;font-style:italic;padding:.5rem 0}"
    ".stats{background:#1e2a10;border-radius:8px;padding:1rem;margin-bottom:1.5rem;"
    "display:flex;gap:2rem;flex-wrap:wrap;border:1px solid #606c38}"
    ".stat{text-align:center} .stat .n{font-size:1.8rem;font-weight:700;color:#dda15e}"
    ".stat .l{font-size:.75rem;color:#a0a87a}"
    "@media(max-width:768px){.scene{grid-template-columns:1fr;gap:1rem;}body{padding:1rem;}}"
    ".modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;"
    "background-color:rgba(28,42,8,0.95);align-items:center;justify-content:center;flex-direction:column;}"
    ".modal img{max-width:95%;max-height:85vh;object-fit:contain;border-radius:8px;box-shadow:0 5px 15px rgba(0,0,0,0.6);}"
    ".modal p{color:#dda15e;margin-top:1rem;font-size:1.1rem;text-align:center;max-width:90%;font-family:serif;}"
    ".close{position:absolute;top:15px;right:25px;color:#fefae0;font-size:35px;font-weight:bold;cursor:pointer;transition:0.3s;}"
    ".close:hover,.close:focus{color:#bc6c25;text-decoration:none;cursor:pointer;}"
)

total_img   = sum(len(s["images"]) for s in data)
scenes_full = sum(1 for s in data if len(s["images"]) >= 3)
scenes_ai   = sum(1 for s in data if any("ai" in pathlib.Path(p).stem for p in s["images"]))

lines = [
    '<!DOCTYPE html><html lang="en"><head>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<title>Gulzar Documentary — Visual Storyboard</title>',
    f'<style>{CSS}</style></head><body>',
    '<h1>Gulzar Documentary — Visual Storyboard</h1>',
    '<p class="sub">All 70 scenes matched to the Marathi transcript. '
    'AI-generated images are marked <strong style="color:#e2b96f">AI</strong>.</p>',
    '<div class="stats">',
    f'<div class="stat"><div class="n">70</div><div class="l">Total Scenes</div></div>',
    f'<div class="stat"><div class="n">{total_img}</div><div class="l">Total Images</div></div>',
    f'<div class="stat"><div class="n">{scenes_full}</div><div class="l">Scenes ≥ 3 images</div></div>',
    f'<div class="stat"><div class="n">{scenes_ai}</div><div class="l">Scenes with AI images</div></div>',
    '</div>',
]

for scene in data:
    num   = scene["scene"]
    label = scene["label"].replace("_", " ")
    text  = scene.get("text_marathi", "")
    query = scene.get("query", "")
    imgs  = scene.get("images", [])

    excerpt = text[:300] + ("…" if len(text) > 300 else "")

    lines.append('<div class="scene">')
    lines.append("<div>")
    lines.append(f'<div class="num">#{num:02d}</div>')
    lines.append(f'<div class="lbl">{label}</div>')
    if excerpt:
        lines.append(f'<div class="txt">{excerpt}</div>')
    lines.append(f'<div class="q">🔍 {query}</div>')
    lines.append("</div>")
    lines.append('<div class="imgs">')

    if imgs:
        for img_path in imgs:
            p      = pathlib.Path(img_path)
            rel    = p.relative_to(BASE)
            is_ai  = "ai" in p.stem or "pulid" in p.stem
            badge  = '<span class="badge">AI</span>' if is_ai else ""
            lines.append(
                f'<div class="card">'
                f'<img src="{rel}" loading="lazy" title="{p.name}">'
                f'{badge}'
                f'<p>{p.name}</p>'
                f'</div>'
            )
    else:
        lines.append('<div class="empty">⚠ No images — needs generation</div>')

    lines.append("</div></div>")

lines.append('<div id="imgModal" class="modal">')
lines.append('<span class="close">&times;</span>')
lines.append('<img class="modal-content" id="modalImg">')
lines.append('<p id="caption"></p>')
lines.append('</div>')

lines.append('<script>')
lines.append('const modal = document.getElementById("imgModal");')
lines.append('const modalImg = document.getElementById("modalImg");')
lines.append('const captionText = document.getElementById("caption");')
lines.append('const closeBtn = document.getElementsByClassName("close")[0];')
lines.append('document.querySelectorAll(".card img").forEach(img => {')
lines.append('  img.onclick = function(){')
lines.append('    modal.style.display = "flex";')
lines.append('    modalImg.src = this.src;')
lines.append('    captionText.innerText = this.parentElement.querySelector("p").innerText;')
lines.append('  }')
lines.append('});')
lines.append('closeBtn.onclick = function() { modal.style.display = "none"; }')
lines.append('window.onclick = function(event) { if (event.target == modal) { modal.style.display = "none"; } }')
lines.append('</script>')

lines.append("</body></html>")

out = BASE / "storyboard.html"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"\nstoryboard.html regenerated -> {out}")
print(f"  {len(lines)} HTML lines written")
