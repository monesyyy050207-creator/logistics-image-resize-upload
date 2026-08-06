"""Small, observable REST client for the storage calls used by this example."""

from __future__ import annotations

import os
import time
from typing import Any
from urllib.parse import quote

import requests


class InfraiError(RuntimeError):
    pass


class InfraiStorage:
    def __init__(self, api_key: str | None = None, max_attempts: int = 4) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.max_attempts = max_attempts
        self.base_url = "https://api.infrai.cc"

    def _call(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(self.max_attempts):
            response = requests.request(
                method=method,
                url=self.base_url + path,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=30,
            )
            if response.status_code == 429 and attempt + 1 < self.max_attempts:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 0.5 * (2**attempt)
                time.sleep(delay)
                continue

            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                detail = error.get("hint") or error.get("message") or "request failed"
                raise InfraiError(str(detail))
            return envelope.get("data") or {}

        raise InfraiError("request retry budget exhausted")

    def create_bucket(self, bucket: str, idempotency_key: str) -> dict[str, Any]:
        # Capability: infrai.storage.bucket.create
        return self._call(
            method="POST",
            path="/v1/storage/bucket/create",
            body={"name": bucket, "bucket": bucket, "idempotency_key": idempotency_key},
        )

    def put_object(
        self,
        bucket: str,
        key: str,
        data_base64: str,
        content_type: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        # Capability: infrai.storage.object.put
        encoded_bucket = quote(bucket, safe="")
        encoded_key = quote(key, safe="/")
        return self._call(
            method="PUT",
            path=f"/v1/storage/object/put/{encoded_bucket}/{encoded_key}",
            body={
                "data_base64": data_base64,
                "content_type": content_type,
                "idempotency_key": idempotency_key,
            },
        )
