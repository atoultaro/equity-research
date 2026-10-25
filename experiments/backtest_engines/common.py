"""Shared frozen experiments and standard records, not a replacement fill engine."""

import argparse
from dataclasses import replace
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR
import json
from pathlib import Path

from equity_research.data import load_dataset
from equity_research.execution import simulate
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.models import Candidate, Config
from equity_research.reporting import canonical
from equity_research.universe import HistoricalUniverse

ROOT = Path(__file__).resolve().parents[2]


def freeze_inputs(output, *, universe_root=None, pilot_root=None):
    """Copy original inputs, create named post-signal variations and capture PR4."""
    original = ROOT / "tests/fixtures"
    data = load_dataset(original / "synthetic_daily.csv", original / "data_manifest.json")
    candidate = Candidate.from_dict(json.loads((original / "candidate.json").read_bytes()))
    config = Config.from_dict({})
    cases = {"favorable_entry_gap": None,
        "losing_stop": [(132,134,131,133),(126,128,124,125)],
        "stop_gap": [(132,134,131,133),(120,122,119,121)],
        "target_gap": [(132,134,131,133),(150,152,149,151)],
        "expired": [(129,130,128,129)]*3+[(132,160,131,150)],
        "ambiguous": [(132,134,131,133),(133,146,124,130)],
        "expiry_third_session": [(129,130,128,129)]*2+[(129,131,128,130.8),(132,150,131,148)],
        "intraday_entry_ambiguity": [(124,132,123,131)],
        "delayed_availability": None}
    experiments = []
    for name, future in cases.items():
        bars = list(data.bars)
        if future is not None:
            bars = bars[:60]+[replace(b, **dict(zip(("open","high","low","close"), map(Decimal,map(str,values)))))
                              for b,values in zip(bars[60:],future)]
        observed = replace(candidate, available_at=datetime.fromisoformat("2026-03-11T14:00:00+00:00")) if name=="delayed_availability" else candidate
        reference = simulate(replace(data,bars=tuple(bars)),observed,config)
        order = reference["order"]
        # Quantity is fixed before the unknown next-session Open. PR4's native
        # fill-price sizing remains separate and may diverge on gaps.
        planned_entry = order["trigger"]+config.slippage_per_share
        qty = int((config.initial_equity*config.risk_fraction/(planned_entry-order["initial_stop"])).to_integral_value(rounding=ROUND_FLOOR))
        rows = [{"session_date": b.session.session_date.isoformat(), "opens_at": b.session.opens_at.isoformat(),
                 "closes_at": b.session.closes_at.isoformat(), **{k: str(getattr(b,k)) for k in ("open","high","low","close","volume")}}
                for b in bars]
        experiments.append({"case": name, "security_id": "synthetic:PR4", "symbol": "SYNTH", "rows": rows,
            "intent": {"signal_available_at": observed.available_at.isoformat(),"signal_session": observed.candidate_session.isoformat(),
                       "activation_at": order["activation_at"].isoformat(), "expires_at": order["expires_at"].isoformat() if order["expires_at"] else None,
                       "trigger":str(order["trigger"]),"stop":str(order["initial_stop"]),"target_r":"2", "quantity":qty,
                       "quantity_policy":"PRECOMMITTED_USING_TRIGGER_PLUS_SLIPPAGE; PR4_NATIVE_SIZES_AT_EXECUTABLE_FILL",
                       "initial_cash":"10000","risk_fraction":"0.01", "slippage_per_share":"0.01", "commission_per_share":"0.005","fee_per_order":"0.50"},
            "reference":json.loads(canonical(reference))})
    files = {"cases.json":encode(experiments), "source_data.csv":(original/"synthetic_daily.csv").read_bytes(),
             "source_manifest.json":(original/"data_manifest.json").read_bytes(), "source_candidate.json":(original/"candidate.json").read_bytes()}
    if pilot_root is not None:
        pilot=Path(pilot_root)
        from equity_research.swing.model import Signal,Setup,Trigger,Boundary,Configuration,build_plan
        from equity_research.strategy import price_grid
        from equity_research.models import timestamp
        from equity_research.universe import ResearchPanel
        embedded,signal_hashes=read_bundle(pilot/'integration')
        signal=json.loads(embedded['signals.json'])[0]
        typed=Signal(**{**signal,'setup':Setup(**{**signal['setup'],'boundary':Boundary(**signal['setup']['boundary'])}),
                        'trigger':Trigger(**signal['trigger'])})
        panel=ResearchPanel(pilot/'research_panel')
        history=[r for r in panel.rows_as_of(signal['security_id'],'2026-10-24T00:00:00Z') if r['session_date']>='2026-01-01']
        sessionmap={s['session_date']:s for s in panel.calendar['sessions']}
        current=next(r for r in history if r['session_date']==signal['trigger']['session_date'])
        future=[s for s in panel.calendar['sessions'] if timestamp(s['opens_at'])>timestamp(signal['trigger']['available_at'])]
        plan=build_plan(typed,current['close'],signal['features']['atr14'],[s['session_date'] for s in future],Configuration())
        trigger=price_grid(Decimal(plan.entry_trigger),Decimal('0.01'),up=True)
        stop=price_grid(Decimal(plan.initial_stop_reference),Decimal('0.01'),up=False)
        experiments.append({'case':'frozen_pr7b_signal','security_id':signal['security_id'],'symbol':signal['symbol'],
            'rows':[{**r,**{k:sessionmap[r['session_date']][k] for k in ['opens_at','closes_at']}} for r in history],
            'intent':{'signal_available_at':signal['trigger']['available_at'],'signal_session':signal['trigger']['session_date'],
                'activation_at':future[0]['opens_at'],'expires_at':future[2]['closes_at'] if len(future)>=3 else None,
                'trigger':str(trigger),'stop':str(stop),'target_r':'2','quantity':int(Decimal('100')/(trigger+Decimal('0.01')-stop)),
                'quantity_policy':'PRECOMMITTED_AT_SIGNAL','initial_cash':'10000','risk_fraction':'0.01',
                'slippage_per_share':'0.01','commission_per_share':'0.005','fee_per_order':'0.50'},
            'source_signal_id':signal['signal_id'],'source_signal_bundle_sha256':signal_hashes['bundle_sha256'],
            'admission':'SYNTHETIC_ENGINE_EVALUATION_ONLY; strict_execution NOT_ADMITTED','reference':None})
        controlsessions=[s for s in panel.calendar['sessions'] if '2022-04-11'<=s['session_date']<='2022-04-22']
        controlrows=[]
        for session in controlsessions:
            if session['session_date'] in ['2022-04-13','2022-04-19'] or session['session_date']>'2022-04-20':continue
            close=100 if session['session_date']<'2022-04-18' else 50 if session['session_date']<'2022-04-20' else 49
            controlrows.append({**session,'open':str(close),'high':str(close),'low':str(close),'close':str(close),'volume':'1000000'})
        control={'origin':'ADDITIONAL_SYNTHETIC_CONTROL_DERIVED_FROM_PR8A_CALENDAR_AND_LIFECYCLE_CONTRACTS',
            'source_panel_sha256':panel.content_sha256,'source_signal_bundle_sha256':signal_hashes['bundle_sha256'],
            'sessions':controlsessions,'rows':controlrows,'ticker_change':'2022-04-18','split_date':'2022-04-18','split_ratio':'0.5',
            'dividend_date':'2022-04-20','dividend_per_share':'1','delisting_date':'2022-04-22','terminal_value':None,
            'missing_session':'2022-04-13','halt_date':'2022-04-19','disclaimer':'No verified terminal value; engine-generated liquidations are diagnostics, never admitted fills'}
        files.update({'cases.json':encode(experiments),'compatibility.json':encode(control),'frozen_pr7b_signals.json':embedded['signals.json']})
    if universe_root:
        u = HistoricalUniverse(universe_root/"universe",master=universe_root/"security_master",panel=universe_root/"research_panel")
        # Use the complete 1,000-ID scale panel for bounded portfolio depth and
        # precomputed membership. The original 100-ID pilot supplies hard cases.
        files["portfolio.json"] = encode({"source_universe_sha256":u.content_sha256,
            "source_panel_sha256":u.panel.content_sha256,"definition_sha256":u.manifest["universe_definition_sha256"],
            "calendar":u.panel.calendar,"securities":[{"security_id":sid,"symbol":u.master.as_of(sid,"2022-04-29","2022-05-02T12:00:00Z")["symbol"],
                "rows":u.panel.observations(sid)} for sid in sorted(u.panel.index)],
            "snapshots":u.snapshots,"initial_cash":"1000000",
            "candidate_policy":"Monthly selected IDs; one precomputed 1-share LONG market intent on first effective session; exit after 5 expected sessions; no alpha study"})
    return write_bundle(Path(output),files)


def load_inputs(path):
    files, hashes = read_bundle(Path(path))
    return {name:json.loads(content) for name,content in files.items() if name.endswith('.json')},hashes["bundle_sha256"]



if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--universe-root',type=Path)
    parser.add_argument('--pilot-root',type=Path)
    args=parser.parse_args()
    print(freeze_inputs(args.output,universe_root=args.universe_root,pilot_root=args.pilot_root))
