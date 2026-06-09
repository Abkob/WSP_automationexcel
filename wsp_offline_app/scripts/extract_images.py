import json, base64, sys
from pathlib import Path

jsonl_path = sys.argv[1]
out_dir = Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

images = []

def find_images(node, depth=0):
    if depth > 15:
        return
    if isinstance(node, dict):
        if node.get("type") == "image":
            src = node.get("source", {})
            if src.get("type") == "base64":
                images.append({
                    "media_type": src.get("media_type", "image/png"),
                    "data": src.get("data", ""),
                })
        for v in node.values():
            find_images(v, depth + 1)
    elif isinstance(node, list):
        for item in node:
            find_images(item, depth + 1)

with open(jsonl_path, encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        find_images(obj)

print(f"Found {len(images)} images")
for i, img in enumerate(images):
    raw = base64.b64decode(img["data"])
    ext = "jpg" if raw[:2] == b"\xff\xd8" else "png"
    out_path = out_dir / f"img_{i:02d}.{ext}"
    out_path.write_bytes(raw)
    print(f"  Saved {out_path.name}  ({len(raw):,} bytes)")
