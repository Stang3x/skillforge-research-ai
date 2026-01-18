def test_ra_transcript_contains_available_commands():
    p = 'C:/Users/Stang3x/Documents/Gemini projects/tests/integration/ra_session_transcript.txt'
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    assert 'Available commands' in txt or 'Available commands and features' in txt
