"""Resize a logistics image and store the source plus a bounded preview."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import logging
from pathlib import Path

from PIL import Image, ImageOps

from infrai_storage import InfraiStorage

LOG = logging.getLogger("logistics-image-upload")


def normalized_jpeg(source: Path, max_size: tuple[int, int]) -> bytes:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()


def upload_shipment_images(
    source: Path,
    bucket: str,
    shipment_id: str,
    storage: InfraiStorage,
) -> dict[str, str]:
    source_bytes = source.read_bytes()
    preview_bytes = normalized_jpeg(source, (480, 480))
    digest = hashlib.sha256(source_bytes).hexdigest()
    original_key = f"shipments/{shipment_id}/original{source.suffix.lower()}"
    preview_key = f"shipments/{shipment_id}/preview.jpg"

    storage.create_bucket(bucket, f"bucket:{bucket}")
    storage.put_object(
        bucket,
        original_key,
        base64.b64encode(source_bytes).decode("ascii"),
        "image/jpeg" if source.suffix.lower() in {".jpg", ".jpeg"} else "image/png",
        f"original:{shipment_id}:{digest}",
    )
    storage.put_object(
        bucket,
        preview_key,
        base64.b64encode(preview_bytes).decode("ascii"),
        "image/jpeg",
        f"preview:{shipment_id}:{digest}:480x480",
    )
    LOG.info("stored shipment=%s original=%s preview=%s", shipment_id, original_key, preview_key)
    return {"original_key": original_key, "preview_key": preview_key}


def main() -> None:
    parser = argparse.ArgumentParser(description="Store a shipment image and its preview")
    parser.add_argument("image", type=Path)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--shipment-id", required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    keys = upload_shipment_images(args.image, args.bucket, args.shipment_id, InfraiStorage())
    print(f"original={keys['original_key']}")
    print(f"preview={keys['preview_key']}")


if __name__ == "__main__":
    main()

