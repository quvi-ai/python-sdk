"""Basic unit tests for the QUVIAI Python SDK.

These tests mock the HTTP layer so they run without a real API key.
"""
import base64
import json
import unittest
from unittest.mock import MagicMock, patch

from quviai import QuviClient, GenerateResult
from quviai.exceptions import AuthError, TaskFailedError, TaskTimeoutError


def _b64_png() -> str:
    # Minimal 1x1 transparent PNG
    return base64.b64encode(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    ).decode()


class TestQuviClient(unittest.TestCase):
    def _client(self) -> QuviClient:
        return QuviClient(api_key="quvi_test_key")

    @patch("quviai.http.urllib.request.urlopen")
    def test_submit_image_returns_task_id(self, mock_urlopen):
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"task_id": "abc-123", "status": "queued", "credit": 10, "credit_used": 2}
        ).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp

        client = self._client()
        task_id = client.submit_image(b"fake-png-bytes", h_angle=63, v_angle=29, zoom=5.0)
        self.assertEqual(task_id, "abc-123")

    @patch("quviai.http.urllib.request.urlopen")
    def test_poll_task_completed_with_base64(self, mock_urlopen):
        b64 = _b64_png()
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "status": "completed",
            "result": {"images": [b64]},
            "position": 0,
            "queue_position": 0,
            "eta": {"eta_seconds": 0, "eta_formatted": "Completed"},
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp

        client = self._client()
        result = client.poll_task("abc-123")
        self.assertIsInstance(result, GenerateResult)
        self.assertIsNotNone(result.image_data)

    @patch("quviai.http.urllib.request.urlopen")
    def test_poll_task_completed_with_url(self, mock_urlopen):
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "status": "completed",
            "result": {"urls": ["https://s3.example.com/result.png"]},
            "position": 0,
            "queue_position": 0,
            "eta": {},
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp

        client = self._client()
        result = client.poll_task("abc-123")
        self.assertEqual(result.url, "https://s3.example.com/result.png")
        self.assertIsNone(result.image_data)

    def test_missing_api_key_raises(self):
        import os
        os.environ.pop("QUVI_API_KEY", None)
        with self.assertRaises(ValueError):
            QuviClient()

    @patch("quviai.http.urllib.request.urlopen")
    def test_failed_task_raises(self, mock_urlopen):
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "status": "failed",
            "error": "GPU out of memory",
            "position": 0,
            "queue_position": 0,
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp

        client = self._client()
        with self.assertRaises(TaskFailedError):
            client.poll_task("abc-123")

    def test_timeout_raises(self):
        client = QuviClient(api_key="quvi_test", poll_timeout=0.001)

        with patch("quviai.http.urllib.request.urlopen") as mock_urlopen:
            resp = MagicMock()
            resp.read.return_value = json.dumps(
                {"status": "queued", "position": 1, "queue_position": 1, "eta": {}}
            ).encode()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = resp

            with self.assertRaises(TaskTimeoutError):
                client.poll_task("abc-123")


if __name__ == "__main__":
    unittest.main()
