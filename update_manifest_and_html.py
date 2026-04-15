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
    # Dark charcoal base + dm-elevation-3 shadow system
    "--elev3:inset 0 1px 0 0 rgba(255,255,255,0.05),inset 0 0 0 1px rgba(255,255,255,0.02),"
    "0 0 0 1px rgba(0,0,0,0.12),0 1px 1px -0.5px rgba(0,0,0,0.18),0 3px 3px -1.5px rgba(0,0,0,0.18);"
    # — embed the var in :root so we can reference it throughout
    "*{box-sizing:border-box}"
    ":root{--elev3:inset 0 1px 0 0 rgba(255,255,255,0.05),inset 0 0 0 1px rgba(255,255,255,0.02),"
    "0 0 0 1px rgba(0,0,0,0.12),0 1px 1px -0.5px rgba(0,0,0,0.18),0 3px 3px -1.5px rgba(0,0,0,0.18)}"
    "body{font-family:'Geist',-apple-system,BlinkMacSystemFont,system-ui,sans-serif;"
    "max-width:1400px;margin:0 auto;padding:2rem 1.5rem;background:#161616;color:#fff}"
    "h1{font-size:2rem;font-weight:800;letter-spacing:-0.03em;color:#fff;margin-bottom:.25rem}"
    "p.sub{color:rgba(235,235,245,.45);font-size:.82rem;margin-bottom:2rem;font-weight:400}"

    ".stats{background:#1e1e1e;border-radius:18px;padding:1.25rem 1.5rem;margin-bottom:1.75rem;"
    "display:flex;gap:2.5rem;flex-wrap:wrap;"
    "box-shadow:var(--elev3)}"
    ".stat{text-align:center}"
    ".stat .n{font-size:2rem;font-weight:800;color:#fff;letter-spacing:-0.03em;display:block}"
    ".stat .l{font-size:.7rem;color:rgba(235,235,245,.4);text-transform:uppercase;letter-spacing:.06em}"

    ".scene{display:grid;grid-template-columns:280px 1fr;gap:1.25rem;"
    "margin-bottom:.875rem;border-radius:20px;"
    "padding:1.25rem;background:#1e1e1e;"
    "box-shadow:var(--elev3);transition:background .2s}"
    ".scene:hover{background:#222}"

    ".num{font-size:2.2rem;font-weight:900;color:#fff;letter-spacing:-0.04em;line-height:1}"
    ".lbl{font-size:.65rem;text-transform:uppercase;letter-spacing:.12em;"
    "color:rgba(235,235,245,.3);margin:.3rem 0 .7rem;font-weight:500}"
    ".txt{font-size:.86rem;line-height:1.75;color:rgba(235,235,245,.75);"
    "border-left:2px solid #0a84ff;padding-left:.75rem;margin-bottom:.5rem}"
    ".q{font-size:.65rem;color:rgba(235,235,245,.22);margin-top:.5rem}"

    ".imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px;align-items:start}"
    ".card{border-radius:14px;overflow:hidden;background:#252525;position:relative;"
    "box-shadow:var(--elev3)}"
    ".card img{width:100%;height:148px;object-fit:cover;object-position:top center;display:block;"
    "cursor:pointer;transition:transform .3s ease,opacity .3s}"
    ".card img:hover{transform:scale(1.04);opacity:.88}"
    ".card p{font-size:10px;padding:5px 8px;margin:0;color:rgba(235,235,245,.35);"
    "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;background:#252525}"

    ".badge{position:absolute;top:7px;right:7px;background:#0a84ff;color:#fff;"
    "font-size:8px;font-weight:700;padding:2px 7px;border-radius:20px;letter-spacing:.04em}"
    ".empty{color:rgba(235,235,245,.22);font-size:.78rem;font-style:italic;padding:.5rem 0}"

    "@media(max-width:768px){"
    "body{padding:.75rem}"
    "h1{font-size:1.4rem}"
    ".stats{gap:1rem;padding:.875rem;border-radius:14px;justify-content:space-between}"
    ".stat .n{font-size:1.5rem}"
    ".stat .l{font-size:.6rem}"
    ".scene{grid-template-columns:1fr;gap:.75rem;padding:1rem;border-radius:16px}"
    ".num{font-size:1.6rem}"
    ".txt{font-size:.82rem}"
    ".imgs{grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}"
    ".card img{height:120px}}"
    "@media(max-width:420px){"
    ".stats{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}"
    ".imgs{grid-template-columns:1fr 1fr}}"

    ".modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;"
    "background:rgba(18,18,18,.88);backdrop-filter:blur(32px);-webkit-backdrop-filter:blur(32px);"
    "align-items:center;justify-content:center;flex-direction:column}"
    ".modal img{max-width:92%;max-height:82vh;object-fit:contain;border-radius:18px;"
    "box-shadow:var(--elev3)}"
    ".modal p{color:rgba(235,235,245,.65);margin-top:1rem;font-size:.9rem;"
    "text-align:center;max-width:80%;font-weight:400}"
    ".close{position:absolute;top:20px;right:20px;width:36px;height:36px;"
    "background:rgba(255,255,255,.1);border-radius:50%;display:flex;"
    "align-items:center;justify-content:center;cursor:pointer;transition:.2s;"
    "color:rgba(255,255,255,.7);font-size:18px;font-weight:300;line-height:1;border:none;"
    "box-shadow:var(--elev3)}"
    ".close:hover{background:rgba(255,255,255,.18);color:#fff}"
)

total_img   = sum(len(s["images"]) for s in data)
scenes_full = sum(1 for s in data if len(s["images"]) >= 3)
scenes_ai   = sum(1 for s in data if any("ai" in pathlib.Path(p).stem for p in s["images"]))

lines = [
    '<!DOCTYPE html><html lang="en"><head>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<title>Gulzar Documentary — Visual Storyboard</title>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">',
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
