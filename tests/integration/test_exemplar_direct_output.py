def test_exemplar_direct_output_contains_success():
    p = 'C:/Users/Stang3x/Documents/Gemini projects/tests/integration/exemplar_direct_output.txt'
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    assert 'SUCCESS: exemplar found' in txt or '"scraped": true' in txt
