"""Builds looks/: one self-contained look.json + fonts per site version, for the desktop apps.

Run from anywhere:  python looks/build.py
Colours are read from the real sources (files and git branches), never typed by hand.
When the main page changes version, edit MAIN and run again.
"""
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "looks"
MAIN = "v1"
CDN = "https://cdn.jsdelivr.net/npm/@fontsource"


def local(name):
    return (ROOT / name).read_text(encoding="utf-8")


def branch(ref, name="index.html"):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{name}"],
                          capture_output=True, check=True).stdout.decode("utf-8")


def variables(css, selector):
    """All custom properties of every rule whose selector is exactly `selector`, in cascade order."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = {}
    for body in re.findall(r"(?m)^[ \t]*%s\s*\{([^{}]*)\}" % re.escape(selector), css):
        out.update({k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body)})
    return out


def palette(v, names):
    colours = {}
    for key, var in names.items():
        value = v.get(var, "")
        ref = re.fullmatch(r"var\((--[\w-]+)\)", value)
        value = v.get(ref.group(1), "") if ref else value
        if re.fullmatch(r"#[0-9a-fA-F]{3,8}|transparent", value):
            colours[key] = value.lower()
    assert {"bg", "text", "accent"} <= set(colours), (colours, v)
    return colours


CLASSIC = {"bg": "--bg", "text": "--text", "muted": "--muted", "line": "--line",
           "border": "--border", "accent": "--accent"}
STUDIO = {"bg": "--fondo", "text": "--texto", "muted": "--texto-suave", "line": "--bloque",
          "border": "--bloque", "accent": "--acento", "block": "--bloque", "title": "--titulo",
          "buttonBg": "--boton-fondo", "buttonText": "--boton-texto",
          "hoverBg": "--hover-fondo", "hoverText": "--hover-texto"}


def classic(css, light_selector='[data-theme="light"]'):
    dark = variables(css, ":root")
    light = variables(css, light_selector)
    result = {"dark": palette(dark, CLASSIC)}
    if light:
        result["light"] = palette({**dark, **light}, CLASSIC)
    return result


def studio(v):
    css = local(f"{v}-tokens.css")
    dark = variables(css, ":root")
    light = {**dark, **variables(css, ':root[data-modo="claro"]')}
    return {"dark": palette(dark, STUDIO), "light": palette(light, STUDIO)}


# ---------- fonts: (family, weight, style, source) ; source = repo file or fontsource package ----------
def pkg(family, package, weight=400, style="normal"):
    return (family, weight, style, f"{package}/files/{package}-latin-{weight}-{style}.woff2")


def repo(family, path, weight=400):
    return (family, weight, "normal", "repo:" + path)


DV_FONTS = [
    repo("Duermevela Condensed", "fonts/duermevela-condensed.woff2", 700),
    repo("Fusion Pixel", "fonts/fusion-pixel-12px-proportional-sc-latin-400-normal.woff2"),
    repo("IBM Plex Mono", "fonts/ibm-plex-mono-latin-400-normal.woff2"),
    repo("IBM Plex Mono", "fonts/ibm-plex-mono-latin-700-normal.woff2", 700),
]
DV_ROLES = {"title": "Duermevela Condensed", "ui": "Fusion Pixel", "text": "IBM Plex Mono"}
DV_LICENSES = ["fonts/LICENCIA-duermevela-condensed.txt", "fonts/LICENSE-fusion-pixel.txt",
               "fonts/LICENSE-ibm-plex-mono.txt"]
JOST = [pkg("Jost", "jost", w) for w in (300, 400, 500)]


def all_roles(title, ui, text):
    roles = {"title": title, "ui": ui, "text": text}
    return {"dark": roles, "light": roles}


boca_jost = {"ui": "Jost", "text": "Jost"}

LOOKS = {
    "v1": dict(name="v1 - plum and lime", page="v1.html", colors=studio("v1"),
               roles={"dark": DV_ROLES, "light": DV_ROLES}, fonts=DV_FONTS, licenses=DV_LICENSES),
    "v2": dict(name="v2 - charcoal and celeste", page="v2.html", colors=studio("v2"),
               roles={"dark": DV_ROLES, "light": DV_ROLES}, fonts=DV_FONTS, licenses=DV_LICENSES),
    "boca": dict(name="Boca", page="boca_theme.html", colors=classic(local("boca_theme.html")),
                 roles={"dark": {"title": "Boca 2026", **boca_jost},
                        "light": {"title": "Jamaica Away 26", **boca_jost}},
                 fonts=[repo("Boca 2026", "assets/Boca_Juniors_Font-2026-2027.ttf"),
                        repo("Jamaica Away 26", "assets/Jamaica_Away_26.ttf")] + JOST,
                 packages=["jost"]),
    "index": dict(name="version index - editorial", page=None, colors=classic(branch("version-index")),
                  roles=all_roles("Instrument Serif", "Jost", "Instrument Serif"),
                  fonts=[pkg("Instrument Serif", "instrument-serif"),
                         pkg("Instrument Serif", "instrument-serif", style="italic")] + JOST,
                  packages=["instrument-serif", "jost"]),
    "8bit": dict(name="8bitLook", page=None, colors=classic(branch("8bitLook")),
                 roles=all_roles("Doto", "Space Mono", "Space Grotesk"),
                 fonts=[pkg("Doto", "doto", w) for w in (400, 700, 900)]
                       + [pkg("Space Grotesk", "space-grotesk", w) for w in (400, 500, 600)]
                       + [pkg("Space Mono", "space-mono", w) for w in (400, 700)],
                 packages=["doto", "space-grotesk", "space-mono"]),
}


def download(url, target):
    if not target.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "looks-builder"})
        with urllib.request.urlopen(req, timeout=30) as r:
            target.write_bytes(r.read())


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


for key, look in LOOKS.items():
    folder = OUT / key
    (folder / "fonts").mkdir(parents=True, exist_ok=True)
    fonts = []
    for family, weight, style, source in look["fonts"]:
        filename = source.rsplit("/", 1)[-1]
        target = folder / "fonts" / filename
        if source.startswith("repo:"):
            shutil.copyfile(ROOT / source[5:], target)
        else:
            package, rest = source.split("/", 1)
            download(f"{CDN}/{package}@5/{rest}", target)
        data = target.read_bytes()
        assert data[:4] in (b"wOF2", b"\x00\x01\x00\x00", b"OTTO", b"true"), target
        fonts.append({"family": family, "weight": weight, "style": style, "file": f"fonts/{filename}"})
    for path in look.get("licenses", []):
        shutil.copyfile(ROOT / path, folder / "fonts" / Path(path).name)
    for package in look.get("packages", []):
        download(f"{CDN}/{package}@5/LICENSE", folder / "fonts" / f"LICENSE-{package}.txt")
    write_json(folder / "look.json", {"schema": 1, "id": key, "name": look["name"], "page": look["page"],
                                      "colors": look["colors"], "roles": look["roles"], "fonts": fonts})
    print(key, "fonts:", len(fonts), "modes:", list(look["colors"]),
          {m: (c["bg"], c["text"], c["accent"]) for m, c in look["colors"].items()})

write_json(OUT / "index.json", {
    "schema": 1, "main": MAIN,
    "looks": [{"id": k, "name": v["name"], "path": f"{k}/look.json"} for k, v in LOOKS.items()],
})
