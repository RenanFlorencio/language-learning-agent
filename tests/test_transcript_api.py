from unittest.mock import MagicMock, patch
from tools.youtube_transcript import get_transcript
import pytest

def test_get_transcript():
    # Create fake transcript snippets
    mock_snippet = MagicMock()
    mock_snippet.text = "Hallo, willkommen zu diesem Video."
    
    mock_transcript = MagicMock()
    mock_transcript.fetch.return_value = [mock_snippet]
    mock_transcript.language_code = "de"
    
    mock_transcript_list = MagicMock()
    mock_transcript_list.find_transcript.return_value = mock_transcript

    with patch("tools.youtube_transcript.ytt_api.list", return_value=mock_transcript_list):
        lang, text = get_transcript("fake_video_id", ["de"])
        assert lang == "de"
        assert "Hallo" in text

def test_api_call_error():
    with patch("tools.youtube_transcript.ytt_api.list", side_effect=Exception("API failed")):
        with pytest.raises(Exception) as exc_info:
            get_transcript("fake_id", ["de"])
        assert "Could not fetch transcript" in str(exc_info.value)