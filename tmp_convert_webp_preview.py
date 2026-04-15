from PIL import Image
import pathlib

webps = [
    r"C:\Mini project\Gulzar\gulzar_video_images\048_meghna_son_samay_grandfather\048_img_serp1.jpg",
    r"C:\Mini project\Gulzar\gulzar_video_images\048_meghna_son_samay_grandfather\048_refill_1.webp",
    r"C:\Mini project\Gulzar\gulzar_video_images\048_meghna_son_samay_grandfather\048_refill_3.webp",
    r"C:\Mini project\Gulzar\gulzar_video_images\054_gulzar_javed_akhtar_together\054_refill_1.webp",
]

for p in webps:
    fp = pathlib.Path(p)
    if not fp.exists():
        print("missing", fp)
        continue
    out = fp.with_suffix(".preview.jpg")
    img = Image.open(fp).convert("RGB")
    img.save(out, "JPEG", quality=92)
    print("saved", out)
