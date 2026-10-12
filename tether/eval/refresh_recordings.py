"""Refresh recorded Studio diagnostics/exports with stored agent decisions; no model calls, keep training provenance."""
import json
from pathlib import Path

from tether.paths import REPO
from tether.studio.pipeline import analyze
from tether.studio.session import Session
from tether.studio import export
from tether.studio.verify import verify


def main():
    for path in sorted((REPO/'runs/studio-demo').glob('*.json')):
        raw=json.loads(path.read_text())
        for stage in raw['stages']:
            previous=stage['result']
            s=Session.from_json(previous['session'])
            result=analyze(s,agent_result=previous.get('agent'))
            stage['result']={**previous,**result.to_json()}
            stage['result']['report_json']=export.to_json(s,result.calibration,result.next_experiment,result.agent)
            stage['result']['recording_provenance']='original recorded Nemotron decisions; fitter/diagnostics recomputed offline 2026-10-12'
            for event in stage['events']:
                if event.get('type')=='calibration':event['calibration']=result.calibration.to_json()
                if event.get('type')=='result':event['result']=stage['result']
        raw['verify']=verify(s,result.calibration)
        raw['verification_provenance']='export files and held-out split recomputed offline 2026-10-12; previous retraining recording retained'
        path.write_text(json.dumps(raw,indent=1)+'\n')
        print(path.name,raw['verify']['mode'],raw['verify']['rms_calibrated_m'],flush=True)


if __name__=='__main__':main()
