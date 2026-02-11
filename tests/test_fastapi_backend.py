import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import backend.main as api


class FakeAgent:
    def __init__(self) -> None:
        self.sp = object()
        self.spotify_auth_mode = "oauth"

    def get_current_track(self):
        return {"status": "playing", "name": "Track", "artist": "Artist"}

    def handle_command(self, command: str) -> str:
        return f"handled:{command}"


class FastApiBackendTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["playback_backend"], "spotify_web_api")

    @patch("backend.main.get_agent")
    def test_status_endpoint(self, mock_get_agent):
        mock_get_agent.return_value = FakeAgent()

        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["spotify_auth_mode"], "oauth")
        self.assertEqual(body["current_track"]["name"], "Track")

    @patch("backend.main.get_agent")
    def test_command_endpoint(self, mock_get_agent):
        mock_get_agent.return_value = FakeAgent()

        response = self.client.post("/api/command", json={"command": "sync"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["message"], "handled:sync")


if __name__ == "__main__":
    unittest.main()
