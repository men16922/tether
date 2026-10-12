"""Product diagnostics; an OK status is not proof of accuracy or of calibrated interval coverage."""
from __future__ import annotations

MIN_PUSHES = 6  # product policy, audited by eval.reliability_sweep; not statistical sufficiency

LABELS = {
    'ok': {'en':'Within the measured range', 'ko':'측정한 범위 안에서 사용할 수 있습니다'},
    'limited': {'en':'Use with limits', 'ko':'제약을 확인하고 사용해야 합니다'},
    'unreliable': {'en':'More measurements needed', 'ko':'측정이 더 필요합니다'},
}
REASONS = {
    'single_push': {'en':'One push cannot measure between-push uncertainty.', 'ko':'시행 하나로는 시행 간 불확실성을 측정할 수 없습니다.'},
    'few_pushes': {'en':'Fewer than six usable pushes; this is a product policy, not a statistical guarantee.', 'ko':'사용 가능한 시행이 6개 미만입니다. 이는 제품 정책이며 통계적 보장 기준이 아닙니다.'},
    'unexplained_pattern': {'en':'The fitted model leaves a pattern in the measurements.', 'ko':'보정 모델로 설명하지 못한 패턴이 측정값에 남아 있습니다.'},
    'unmeasured_range': {'en':'The target range extends beyond the measured surface.', 'ko':'목표 범위가 측정한 표면 구간을 벗어납니다.'},
    'no_tracks': {'en':'No motion tracks; friction and launch errors may be confounded.', 'ko':'이동 궤적이 없어 마찰과 출발 오차를 구분하기 어려울 수 있습니다.'},
    'large_stop_residual': {'en':'Stop residual exceeds the existing 1 cm model tolerance.', 'ko':'정지 위치 잔차가 기존 모델 허용값인 1 cm를 넘습니다.'},
}


def assess(session, cal) -> dict:
    n=sum(not p.tipped for p in session.pushes)
    reasons=[]
    if n<=1:
        reasons.append({'code':'single_push','params':{'pushes':n}})
    elif n<MIN_PUSHES:
        reasons.append({'code':'few_pushes','params':{'pushes':n,'policy_min':MIN_PUSHES}})
    if not session.has_tracks:
        reasons.append({'code':'no_tracks','params':{}})
    if (cal.residuals.get('patterns') or {}).get('findings') or cal.residuals.get('unexplained'):
        reasons.append({'code':'unexplained_pattern','params':{}})
    if cal.predicted.get('unmeasured_whatif'):
        reasons.append({'code':'unmeasured_range','params':{'reach_m':session.coverage()[1]}})
    if cal.residuals['stop_residual_rms_m']>0.01:
        reasons.append({'code':'large_stop_residual','params':{'rms_m':cal.residuals['stop_residual_rms_m']}})
    return {'level':'unreliable' if n<=1 else 'limited' if reasons else 'ok', 'reasons':reasons,
            'interval_available':n>1 and bool(cal.ensemble), 'usable_pushes':n,
            'policy':'6 pushes is a product policy; status cannot detect shared bias or guarantee coverage'}


def text(status: dict, lang='en') -> str:
    head=LABELS[status['level']][lang]
    reasons=' '.join(REASONS[r['code']][lang] for r in status['reasons'])
    return head + (': '+reasons if reasons else '')
