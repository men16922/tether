"""Offline diagnostics, not a correction of EV-RealPhys truth or a causal claim about its source."""
import json
from pathlib import Path

import numpy as np

from tether.eval.real_benchmark import GT, load, sequences
from tether.paths import REPO


def main():
    rb = json.loads((REPO / 'runs/proof/real_benchmark.json').read_text())
    rows = []
    for seq in sequences():
        d = load(seq)
        if d['obj'] not in GT:
            continue
        row = next(r for r in rb['rows'] if r['sequence'] == f'{seq.parent.name}/{seq.name}')
        gt = json.loads((seq / 'scene_gt.json').read_text())
        start, end = row['release_frame'], row['rest_frame']
        rs = [np.array(gt[str(i)][0]['cam_R_m2w']).reshape(3, 3) for i in range(start, end+1)]
        ref = rs[-1]
        angles = [np.degrees(np.arccos(np.clip((np.trace(r @ ref.T)-1)/2,-1,1))) for r in rs]
        normal_axis=int(np.argmax(np.abs(ref[2,:])))
        tilt=[np.degrees(np.arccos(np.clip(abs(r[:,normal_axis] @ ref[:,normal_axis]),0,1))) for r in rs]
        zs = d['com'][start:end+1,2]
        rows.append({'object': row['object'], 'sequence': row['sequence'], 'log_mu': row['mu_per_push_log'],
                     'video_mu': row.get('mu_per_push_video'), 'height_range_mm': round(float(np.ptp(zs))*1000,3),
                     'orientation_change_deg': round(float(max(angles)),3),
                     'normal_tilt_deg': round(float(max(tilt)),3),
                     'video_vs_mocap_stop_m': row.get('video_vs_mocap_stop_m')})
    summaries={}
    for name, _ in GT.values():
        rs=[r for r in rows if r['object']==name]
        vals=[r['log_mu'] for r in rs if r['log_mu'] is not None]
        summaries[name]={'log_mu_median':float(np.median(vals)), 'log_mu_min_max':[min(vals),max(vals)],
                         'log_mu_cv':float(np.std(vals)/np.mean(vals)),
                         'max_height_range_mm':max(r['height_range_mm'] for r in rs),
                         'max_orientation_change_deg':max(r['orientation_change_deg'] for r in rs)}
        summaries[name]['max_normal_tilt_deg']=max(r['normal_tilt_deg'] for r in rs)
    out={'hypotheses':['RGB tracking error alone', 'large tilt during free slide', 'reference/protocol or clock mismatch'],
         'rows':rows,'summary':summaries,
         'source':'https://arxiv.org/html/2309.15703 (v3, Appendix B.5, C.3; accessed 2026-10-12)',
         'conclusion':'Cracker mismatch exists in mocap and quadratic fits too, so RGB tracking alone cannot explain it. '
         'Maximum surface-normal tilt is 1.798 degrees (yaw alone is not tipping). '
         'The source Appendix C.3 explicitly describes uneven cardboard contact and anisotropic friction; '
         'the measured mismatch is consistent with the constant-friction model limitation, not a demonstrated clock error. '
         'Appendix B.5 reports more variation of cracker tilt-test values. '
         'A shared bias is not detected by fitter/baseline agreement or small scatter. '
         'Source confirms synchronised/downsampled 30 Hz; no truth or clock correction is applied. '
         'This does not independently isolate the physical contact cause in the original lab.',
         'single_push_interval':'One push contributes no between-push bootstrap variation; measurement assumptions alone make its narrow interval. '
         'Such intervals must be unavailable, not interpreted as confidence.'}
    p=REPO/'runs/proof/real_diagnosis.json'; p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(summaries,indent=2)); print(out['conclusion'])


if __name__=='__main__':
    main()
