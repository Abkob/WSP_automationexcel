from __future__ import annotations

from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / "app" / "static" / "aub-logo-vertical.jpg"
DESTINATION = PROJECT_ROOT / "app" / "static" / "wsp.ico"


def create_shortcut_icon() -> Path:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Logo image was not found: {SOURCE}")

    image = Image.open(SOURCE).convert("RGBA")
    seal = image.crop((388, 49, 985, 647))

    pixels = []
    for red, green, blue, alpha in seal.getdata():
        if red > 230 and green > 230 and blue > 230:
            pixels.append((red, green, blue, 0))
        else:
            pixels.append((red, green, blue, alpha))
    seal.putdata(pixels)

    canvas = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    resized = seal.resize((596, 596), Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (22, 22))
    canvas.save(
        DESTINATION,
        format="ICO",
        sizes=((16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)),
    )
    return DESTINATION


if __name__ == "__main__":
    print(create_shortcut_icon())
