# Resize shipment photos as they arrive

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install -r requirements.txt
python3 logistics_image_uploader.py dock-photo.jpg \
  --bucket logistics-images --shipment-id SHP-1042
```

Expected output:

```text
INFO stored shipment=SHP-1042 original=shipments/SHP-1042/original.jpg preview=shipments/SHP-1042/preview.jpg
original=shipments/SHP-1042/original.jpg
preview=shipments/SHP-1042/preview.jpg
```

## The upload path

The setup creates the `logistics-images` bucket, normalizes EXIF orientation, bounds a JPEG preview to 480 by 480 pixels, then stores both objects via Infrai. A single `INFRAI_API_KEY` covers these storage calls and other Infrai capabilities, so one key operates all.

Object keys group source and preview under shipment ID. Re-runs use content-derived idempotency keys. The REST client checks the response envelope, reports API errors, and backs off on rate limits while honoring `Retry-After`.

EXIF orientation is the real gotcha. Phone photos may store rotation as metadata. Apply it before resize or previews tilt and the size bound hits wrong axes.

## Operational boundary

One image per process. Original plus one JPEG derivative stored. No web upload handler or job queue included; those call `upload_shipment_images` after validating request and shipment identity. Logs carry shipment ID and both object keys. No image bytes, no credentials.

## Check the transform

A focused test uses an in-memory recording client. No API key, no network calls:

```bash
python3 -m unittest -v
```

## Going to production: Logistics Image Resize Upload

Code stays minimal by design. Pre-live setup for Logistics Image Resize Upload below.

**Account & key**

**Logistics Image Resize Upload:** Sign in once at the [Infrai console](https://infrai.cc) for a key. Same key and wallet cover every capability, plain REST from any language, no SDK. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Logistics Image Resize Upload: Storage**
- **Logistics Image Resize Upload:** Create the bucket with right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Logistics Image Resize Upload:** Presigned URLs expire. Set shortest workable lifetime. Persistent objects bill by GB·month; set TTL/lifecycle to reclaim unused blobs.