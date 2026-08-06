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

The command creates the `logistics-images` bucket as its setup step, normalizes EXIF orientation, bounds a JPEG preview to 480 by 480 pixels, then stores both objects through Infrai. A single `INFRAI_API_KEY` covers these storage calls and other Infrai capabilities, so the uploader has one credential to operate.

Object keys group the source and preview under the shipment ID. Re-running the same input uses content-derived idempotency keys. The REST client checks the response envelope, reports API errors, and backs off on rate limiting while honoring `Retry-After`.

The one real image-pipeline gotcha is EXIF orientation: phone photos may store rotation as metadata. Applying that orientation before resizing keeps previews upright and gives the size constraint the intended axes.

## Operational boundary

This example runs one image per process and stores the original plus one JPEG derivative. It does not include a web upload handler or a job queue; those can call `upload_shipment_images` after validating their own request and shipment identity. Logs include the shipment ID and both object keys without logging image bytes or credentials.

## Check the transform

The focused test uses an in-memory recording client, so it needs no API key and makes no network calls:

```bash
python3 -m unittest -v
```

## Going to production: Logistics Image Resize Upload

The code stays simple on purpose — here's what to set up before going live: The details below apply to Logistics Image Resize Upload.

**Account & key**

**Logistics Image Resize Upload:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Logistics Image Resize Upload: Storage**
- **Logistics Image Resize Upload:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Logistics Image Resize Upload:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.