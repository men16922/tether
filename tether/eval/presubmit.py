"""Offline submission checks, unresolved public placeholders, and a deduplicated link inventory."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from tether.paths import REPO

PUBLIC=['README.md','docs/submission/DEVPOST.md','docs/article/tether.en.md','docs/article/tether.ko.md',
        'submission/about-the-project.md','submission/youtube-description.txt']
PLACEHOLDER=re.compile(r'YOUTUBE_LINK|\[YOUTUBE_URL\]|TODO(?:\b)|TBD(?:\b)')


def media(root=REPO):
    movie=root/'submission/tether_film.mp4'
    if not movie.exists():return {'status':'missing'}
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(movie)],
                          check=True,capture_output=True,text=True)
    meta=json.loads(result.stdout);seconds=float(meta['format']['duration'])
    scenes=('appInput','appAgent','appResult','appExport','appAsk')
    frames=root/'film/out/film/frames'
    core=sum(len(list((frames/s).glob('f*.jpg')))/30 for s in scenes)
    video=next(x for x in meta['streams'] if x['codec_type']=='video')
    return {'seconds':seconds,'width':video['width'],'height':video['height'],'core_app_footage_seconds':core,
            'under_3_minutes':0<seconds<180,'core_at_least_1_minute':core>=60,
            'note':'scene frames show recorded application modules; this does not verify YouTube publication or Devpost submission'}


def inventory(root=REPO):
    placeholders=[]; links=set(); missing=[]
    for name in PUBLIC:
        p=root/name
        if not p.exists():missing.append(name);continue
        for n,line in enumerate(p.read_text().splitlines(),1):
            if PLACEHOLDER.search(line):placeholders.append({'file':name,'line':n,'text':line[:220]})
            # Quotes delimit URLs in code/HTML; prose punctuation is not part of the link.
            links.update(url.rstrip('.,;') for url in re.findall(r"https?://[^\s<>`\)\]\"']+",line))
    return {'public_placeholders':placeholders,'missing_files':missing,'links':sorted(links),
            'scope':'offline gates only; links listed, not network-verified; no deployment/publication/submission implied'}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-gate',action='store_true',help='use only after the current make check completed')
    ap.add_argument('--allow-pending',action='store_true',help='report unresolved owner tasks without exit failure')
    a=ap.parse_args(argv)
    if not a.skip_gate:
        subprocess.run(['make','check'],cwd=REPO,check=True)
    out=inventory()
    out['media']=media()
    out['gate']='skipped' if a.skip_gate else 'make check passed'
    (REPO/'runs/proof/presubmit.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in out['public_placeholders']: print(f"PENDING {r['file']}:{r['line']} {r['text']}")
    for p in out['missing_files']:print('MISSING',p)
    print('Links (not network-verified):');print('\n'.join(out['links']))
    print(out['scope'])
    bad_media=not out['media'].get('under_3_minutes') or not out['media'].get('core_at_least_1_minute')
    return 1 if (out['public_placeholders'] or out['missing_files'] or bad_media) and not a.allow_pending else 0


if __name__=='__main__':sys.exit(main())
