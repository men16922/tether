from tether.eval.presubmit import inventory,PUBLIC


def test_public_placeholders_are_reported_with_file_and_line(tmp_path):
    for name in PUBLIC:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('Demo: YOUTUBE_LINK\nhttps://example.com/demo\n')
    r=inventory(tmp_path)
    assert len(r['public_placeholders'])==len(PUBLIC)
    assert r['public_placeholders'][0]['line']==1
    assert r['links']==['https://example.com/demo']
    assert not r['missing_files']


def test_link_inventory_deduplicates_prose_markdown_and_quoted_urls(tmp_path):
    text = '\n'.join([
        'Demo: https://example.com/demo.',
        '[Demo](https://example.com/demo)',
        '{"base_url": "https://example.com/api/",}',
        "<a href='https://example.com/api/'>API</a>",
        'Query: https://example.com/search?next=a,b&version=1.2;',
    ])
    for name in PUBLIC:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    assert inventory(tmp_path)['links'] == [
        'https://example.com/api/',
        'https://example.com/demo',
        'https://example.com/search?next=a,b&version=1.2',
    ]
