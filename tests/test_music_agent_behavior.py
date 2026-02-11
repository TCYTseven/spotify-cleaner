import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from music_agent import ComprehensiveMusicAgent


class BaseMusicAgentTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_music_agent.db")

        # Keep tests fully local and deterministic.
        self.setup_patch = patch.object(
            ComprehensiveMusicAgent,
            "setup_spotify_connection",
            autospec=True,
            return_value=None,
        )
        self.applescript_patch = patch.object(
            ComprehensiveMusicAgent,
            "_is_applescript_available",
            return_value=False,
        )
        self.setup_patch.start()
        self.applescript_patch.start()

    def tearDown(self):
        self.setup_patch.stop()
        self.applescript_patch.stop()
        self.temp_dir.cleanup()

    def build_agent(self) -> ComprehensiveMusicAgent:
        return ComprehensiveMusicAgent(db_path=self.db_path)


class LyricsCommandRoutingTests(BaseMusicAgentTest):
    def test_plain_lyrics_command_uses_current_track_lyrics_lookup(self):
        agent = self.build_agent()
        agent.get_current_track = MagicMock(
            return_value={"status": "playing", "name": "High Hopes", "artist": "Pink Floyd"}
        )
        agent.get_track_lyrics = MagicMock(return_value="line one\nline two")
        agent.search_by_lyrics = MagicMock(return_value={"name": "Wrong", "artist": "Route"})

        response = agent.handle_command("lyrics")

        self.assertIn("First few lines", response)
        agent.get_track_lyrics.assert_called_once_with("Pink Floyd", "High Hopes")
        agent.search_by_lyrics.assert_not_called()

    def test_lyric_fragment_request_uses_lyric_search(self):
        agent = self.build_agent()
        agent.search_by_lyrics = MagicMock(return_value={"name": "High Hopes", "artist": "Pink Floyd"})
        agent.get_track_lyrics = MagicMock(return_value="should not be called")

        response = agent.handle_command("what's that song where they say 'encumbered forever'")

        self.assertIn("Found: High Hopes by Pink Floyd", response)
        agent.search_by_lyrics.assert_called_once()
        agent.get_track_lyrics.assert_not_called()


class PlaybackFallbackTests(BaseMusicAgentTest):
    def test_start_playback_uses_spotify_api_when_applescript_unavailable(self):
        agent = self.build_agent()
        agent.spotify_auth_mode = "oauth"
        agent.sp = MagicMock()

        with patch.object(agent, "_get_spotify_device_id", return_value="device123"):
            ok = agent._start_playback(track_uri="spotify:track:abc")

        self.assertTrue(ok)
        agent.sp.start_playback.assert_called_once_with(
            device_id="device123",
            uris=["spotify:track:abc"],
        )

    @patch("music_agent.time.sleep", return_value=None)
    def test_next_track_uses_spotify_api_without_applescript(self, _mock_sleep):
        agent = self.build_agent()
        agent.spotify_auth_mode = "oauth"
        agent.sp = MagicMock()
        agent.get_current_track = MagicMock(
            return_value={"status": "playing", "name": "Track B", "artist": "Artist B"}
        )

        with patch.object(agent, "_get_spotify_device_id", return_value="device123"):
            response = agent.next_track()

        self.assertIn("Skipped to", response)
        agent.sp.next_track.assert_called_once_with(device_id="device123")


if __name__ == "__main__":
    unittest.main()
