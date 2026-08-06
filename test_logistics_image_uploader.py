import tempfile
import unittest
from pathlib import Path

from PIL import Image

from logistics_image_uploader import normalized_jpeg, upload_shipment_images


class RecordingStorage:
    def __init__(self) -> None:
        self.bucket_calls = []
        self.put_calls = []

    def create_bucket(self, bucket, idempotency_key):
        self.bucket_calls.append((bucket, idempotency_key))
        return {}

    def put_object(self, *args):
        self.put_calls.append(args)
        return {}


class LogisticsImageUploaderTest(unittest.TestCase):
    def test_preview_is_bounded_and_both_objects_are_written(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "dock-photo.png"
            Image.new("RGB", (1200, 800), "white").save(source)
            storage = RecordingStorage()

            keys = upload_shipment_images(source, "logistics-images", "SHP-1042", storage)
            preview = normalized_jpeg(source, (480, 480))

        self.assertEqual(storage.bucket_calls, [("logistics-images", "bucket:logistics-images")])
        self.assertEqual(len(storage.put_calls), 2)
        self.assertEqual(keys["preview_key"], "shipments/SHP-1042/preview.jpg")
        self.assertLess(len(preview), source.stat().st_size if source.exists() else 1000000)


if __name__ == "__main__":
    unittest.main()

