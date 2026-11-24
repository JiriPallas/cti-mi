"""Vytvoří jazykové verze:  cs/ = ČTI MI,  sv/ = READ-IT  (+ ikony s vlajkou, manifesty).
Kořen /cti-mi/ jen přesměruje na cs/.
Upravuje se jen nastroje/sablona.html a jazyky.js – pak spustit:  python nastroje/sestav_jazyky.py"""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw

KOREN = Path(__file__).resolve().parent.parent
JAZYKY = {   # kód: (krátký název, dlouhý název)
    "cs": ("ČTI MI", "ČTI MI web"),
    "sv": ("READ-IT", "READ-IT"),
}

def vlajka(kod, w, h):
    v = Image.new("RGB", (w, h), "white"); d = ImageDraw.Draw(v)
    if kod == "cs":
        d.rectangle([0, h // 2, w, h], fill="#D7141A")
        d.polygon([(0, 0), (w // 2, h // 2), (0, h)], fill="#11457E")
    elif kod == "sv":
        d.rectangle([0, 0, w, h], fill="#006AA7")
        t = h // 5
        d.rectangle([0, h // 2 - t // 2, w, h // 2 + t // 2], fill="#FECC00")
        x = w * 5 // 16
        d.rectangle([x - t // 2, 0, x + t // 2, h], fill="#FECC00")
    return v

def ikona(kod, cil):
    zaklad = Image.open(KOREN / "nastroje" / "ikona-zaklad-512.png").convert("RGBA")
    w, h = 250, 160
    ram = Image.new("RGBA", (w + 24, h + 24), "white")
    ram.paste(vlajka(kod, w, h), (12, 12))
    zaklad.paste(ram, (512 - w - 24 - 18, 512 - h - 24 - 18))
    cil.mkdir(parents=True, exist_ok=True)
    zaklad.save(cil / "ikona-vlajka-512.png")
    zaklad.resize((192, 192), Image.LANCZOS).save(cil / "ikona-vlajka-192.png")

def manifest(kod, cil):
    kratky, dlouhy = JAZYKY[kod]
    m = {"name": dlouhy, "short_name": kratky, "id": "./", "start_url": "./", "scope": "./", "lang": kod,
         "display": "standalone", "background_color": "#000000", "theme_color": "#000000",
         "icons": [{"src": "ikona-vlajka-192.png", "sizes": "192x192", "type": "image/png"},
                   {"src": "ikona-vlajka-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}]}
    (cil / "manifest.webmanifest").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

sablona = (KOREN / "nastroje" / "sablona.html").read_text(encoding="utf-8")
for kod, (kratky, _) in JAZYKY.items():
    cil = KOREN / kod
    ikona(kod, cil); manifest(kod, cil)
    s = re.sub(r"/\*JAZYK\*/.*?/\*/JAZYK\*/", f'/*JAZYK*/const JAZYK = "{kod}", ZAKLAD = "../";/*/JAZYK*/', sablona, flags=re.S)
    s = s.replace('<html lang="cs">', f'<html lang="{kod}">').replace("<title>ČTI MI</title>", f"<title>{kratky}</title>")
    s = s.replace('<link rel="manifest" href="manifest.webmanifest">', '<link rel="manifest" href="manifest.webmanifest">')
    s = s.replace('<link rel="icon" href="ikona-192.png">', '<link rel="icon" href="ikona-vlajka-192.png">')
    (cil / "index.html").write_text(s, encoding="utf-8")
    print("hotovo:", kod, kratky)

(KOREN / "index.html").write_text("""<!DOCTYPE html>
<html lang="cs"><head><meta charset="utf-8"><title>ČTI MI</title>
<link rel="icon" href="cs/ikona-vlajka-192.png">
<meta http-equiv="refresh" content="0; url=cs/">
<script>location.replace("cs/" + location.search);</script>
</head><body style="font:32px sans-serif;background:#000;color:#fff;padding:40px">
<a href="cs/" style="color:#FFE000">ČTI MI</a> · <a href="sv/" style="color:#FFE000">READ-IT</a></body></html>
""", encoding="utf-8")
print("hotovo: kořen přesměrovává na cs/")
