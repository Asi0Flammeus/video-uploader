import os

from peertube_uploader.utils import (
    generate_title,
    generate_description,
    extract_course_index,
    extract_part_chapter,
    extract_language,
    get_chapter_name,
)

def test_generate_title(tmp_path):
    # Create a dummy mp4 file
    file_path = tmp_path / "My Video Title.mp4"
    file_path.write_bytes(b"")
    title = generate_title(str(file_path))
    assert title == "My Video Title"

def test_generate_description(tmp_path):
    file_path = tmp_path / "video.mp4"
    file_path.write_bytes(b"")
    description = generate_description(str(file_path))
    # Default implementation returns empty string
    assert description == "test"

def test_extract_course_index():
    assert extract_course_index('btc101_2.1_es.txt') == 'btc101'
    assert extract_course_index('/path/to/ECO201-3.2-fr.MP4') == 'eco201'

def test_extract_part_chapter():
    assert extract_part_chapter('btc101_2.1_es.txt') == (2, 1)
    assert extract_part_chapter('cyp201-4.7-fr.txt') == (4, 7)

def test_extract_language():
    assert extract_language('btc101_2.1_es.txt') == 'es'
    assert extract_language('btc101_2.1-es.txt') == 'es'
    assert extract_language('cyp201_4.7_fr_test.txt') == 'fr'
    assert extract_language('cyp201_1.1_Loic_en-US.mp4') == 'en'

def test_get_chapter_name(tmp_path, monkeypatch):
    import textwrap
    # Set required environment variables for Config
    monkeypatch.setenv('UPLOAD_URL', 'http://example.com')
    monkeypatch.setenv('PEERTUBE_INSTANCE', 'http://example.com')
    monkeypatch.setenv('CLIENT_ID', 'id')
    monkeypatch.setenv('CLIENT_SECRET', 'secret')
    monkeypatch.setenv('USERNAME', 'user')
    monkeypatch.setenv('PASSWORD', 'pass')
    # Create course markdown structure
    courses_dir = tmp_path / 'courses'
    # BTC101 in en and fr
    btc_dir = courses_dir / 'btc101'
    btc_dir.mkdir(parents=True)
    en_md = btc_dir / 'en.md'
    en_md.write_text(textwrap.dedent('''
        +++
        # FrontMatter
        +++
        # Part 1
        ## Intro
        # Part 2
        ## Basics
        # Part 3
        ## What are Bitcoin wallets?
        ## Extra
    '''), encoding='utf-8')
    fr_md = btc_dir / 'fr.md'
    fr_md.write_text(textwrap.dedent('''
        +++
        # FrontMatter
        +++
        # Part 1
        ## Intro FR
        # Part 2
        ## Base FR
        # Part 3
        ## Qu'est-ce qu'un portefeuille Bitcoin ?
        ## Autre
    '''), encoding='utf-8')
    # LNP201 in es
    lnp_dir = courses_dir / 'lnp201'
    lnp_dir.mkdir(parents=True)
    es_md = lnp_dir / 'es.md'
    es_md.write_text(textwrap.dedent('''
        +++
        # Meta
        +++
        # Part 1
        ## Capítulo 1
        # Part 2
        ## Capítulo 2
        # Part 3
        ## Cap 3
        # Part 4
        ## Cap 4
        # Part 5
        ## Primer Tema
        ## Gestionando Tu Liquidez
        ## Otro Tema
    '''), encoding='utf-8')
    # Point PATH_TO_COURSES env to our tmp structure
    monkeypatch.setenv('PATH_TO_COURSES', str(courses_dir))
    # Assertions
    from peertube_uploader.utils import get_chapter_name
    assert get_chapter_name('btc101', (3, 1), 'en') == 'What are Bitcoin wallets?'
    assert get_chapter_name('btc101', (3, 1), 'fr') == "Qu'est-ce qu'un portefeuille Bitcoin ?"
    assert get_chapter_name('lnp201', (5, 2), 'es') == 'Gestionando Tu Liquidez'
