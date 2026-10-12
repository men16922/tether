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
