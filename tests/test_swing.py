"""Synthetic causal geometry, independent lifecycle, immutable research and PR4 reuse."""

from copy import deepcopy
from dataclasses import asdict, replace
from datetime import timedelta
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

from equity_research.cli import main
from equity_research.data import load_dataset
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.models import Config, timestamp
from equity_research.swing import Configuration, CONTINUATION, FAILED, evaluate, freeze_strategy, load_strategy
from equity_research.swing.engine import features
from equity_research.swing.model import prior_boundary
from equity_research.swing.execution import freeze_replay, replay_plans, strict_inventory


@pytest.fixture(scope="module")
def fixture_path(tmp_path_factory):
    root = tmp_path_factory.mktemp("swing-fixture") / "inputs"
    spec = importlib.util.spec_from_file_location("swing_example", Path(__file__).parents[1] / "scripts/make_swing_strategy_example.py")
    script = importlib.util.module_from_spec(spec); spec.loader.exec_module(script)
    script.make_fixture(root)
    return root


@pytest.fixture
def inputs(fixture_path):
    ds = load_dataset(fixture_path / "data.csv", fixture_path / "manifest.json")
    rows = [{"session_date": b.session.session_date.isoformat(), "symbol": b.symbol, "security_id": "strict:SYNTH",
             **{k: str(getattr(b, k)) for k in ("open", "high", "low", "close", "volume")}} for b in ds.bars]
    return rows, {"sessions": deepcopy(ds.manifest["sessions"])}


def run(inputs, config=None, **kwargs):
    rows, cal = inputs
    return evaluate(rows, cal, "SYNTH", "strict:SYNTH", "a"*64, config or Configuration(),
                    start=rows[0]["session_date"], end=rows[-1]["session_date"], **kwargs)


def setprice(row, o, h, l, c):
    row.update(dict(zip(("open", "high", "low", "close"), map(str, (o,h,l,c)))))


def test_prior_boundary_excludes_current_high_and_records_causal_window(inputs):
    rows, _ = inputs
    r = run(inputs)
    s = next(s for s in r["signals"] if s["trigger"]["session_date"] == rows[199]["session_date"])
    b = s["setup"]["boundary"]
    assert Decimal(b["value"]) == Decimal("140.6")
    assert b["window_start"] == rows[179]["session_date"]
    assert b["latest_input_session"] == rows[198]["session_date"]
    assert b["configuration_sha256"] == Configuration().sha256
    assert b["price_dataset_sha256"] == "a"*64
    assert s["features"]["sma200"] is not None


@pytest.mark.parametrize("close,expected", [("140.6",False),("140.59",False),("140.61",True)])
def test_strict_close_boundary(inputs,close,expected):
    rows,_ = inputs;rows[199]["close"]=close
    assert any(s["trigger"]["session_date"]==rows[199]["session_date"] for s in run(inputs)["signals"]) is expected


def test_exact_sma_and_atr_warmup(inputs):
    rows,_=inputs
    assert features(rows[:14])["atr14"] is None
    assert features(rows[:15])["atr14"] == "2.0"
    assert features(rows[:49])["sma50"] is None
    assert features(rows[:50])["sma50"] is not None
    assert features(rows[:199])["sma200"] is None
    assert features(rows[:200])["sma200"] is not None
    quality=run(inputs)["quality_report"]
    assert quality["incomplete_unavailable_observations"]==199
    assert quality["evaluable_sessions"]==6


def test_trend_gate_and_no_future_indicators(inputs):
    rows,_=inputs
    before=run(inputs)
    for row in rows[200:]:
        for k in ("open","high","low","close"):row[k]=str(Decimal(row[k])*2)
    after=run(inputs)
    assert before["signals"][0]==after["signals"][0]
    assert before["signals"][0]["feature_observation_cutoffs"]["latest_price_input"]==rows[199]["session_date"]
    # Reversed full history fails the trend gate without manufactured warmup.
    for i,row in enumerate(rows):setprice(row,200-i/5,201-i/5,199-i/5,200-i/5)
    assert run(inputs)["signals"]==[]
    assert any(e["reasons"]==["TREND_GATE_FAILED"] for e in run(inputs)["exclusions"])


def failed_scenario(inputs):
    rows,cal=inputs
    # Flat prior resistance 101, then independent overlapping highs 103 and104.
    for row in rows:setprice(row,100,101,99,100)
    setprice(rows[25],100,103,99,102)
    setprice(rows[26],102,104,100,103)
    setprice(rows[27],102,103,99,100)
    return rows,cal


def test_failed_boundaries_are_fixed_and_overlapping_attempts_independent(inputs):
    rows,cal=failed_scenario(inputs)
    result=run((rows,cal),Configuration(FAILED))
    signals=[s for s in result["signals"] if s["trigger"]["session_date"]==rows[27]["session_date"]]
    assert len(signals)==2
    assert {s["setup"]["boundary"]["value"] for s in signals}=={"101","103"}
    assert {s["trigger"]["direction"] for s in signals}=={"SHORT"}
    assert len({s["signal_id"] for s in signals})==2
    assert all(p["execution_eligibility_status"]=="SHORT_EXECUTION_UNSUPPORTED" for p in result["trade_plans"])
    assert all(Decimal(p["initial_stop_reference"])>Decimal(p["planned_entry_reference"]) for p in result["trade_plans"])


@pytest.mark.parametrize("failure_day,outcome", [(26,"CONFIRMED"),(28,"CONFIRMED"),(29,"EXPIRED")])
def test_failure_following_session_K_boundary_and_expiry(inputs,failure_day,outcome):
    rows,cal=failed_scenario(inputs)
    for row in rows[26:]:setprice(row,102,102,101,102)
    setprice(rows[failure_day],102,102,99,100)
    r=run((rows,cal),Configuration(FAILED))
    sid=next(s["setup_id"] for s in r["setup_observations"] if s["session_date"]==rows[25]["session_date"])
    lifecycle=[e for e in r["setup_outcomes"] if e["setup_id"]==sid]
    assert len(lifecycle)==1 and lifecycle[0]["outcome"]==outcome
    assert lifecycle[0]["following_sessions_seen"]==min(failure_day-25,3)


def test_failed_close_equality_does_not_confirm_and_immediate_failure_is_not_signal(inputs):
    rows,cal=failed_scenario(inputs)
    setprice(rows[25],100,103,99,100)
    r=run((rows,cal),Configuration(FAILED))
    sid=next(s["setup_id"] for s in r["setup_observations"] if s["session_date"]==rows[25]["session_date"])
    assert next(e for e in r["setup_outcomes"] if e["setup_id"]==sid)["outcome"]=="IMMEDIATE_FAILURE_OBSERVATION_ONLY"
    assert not any(s["setup"]["setup_id"]==sid for s in r["signals"])
    rows,cal=failed_scenario(inputs)
    for row in rows[26:]:setprice(row,101,102,100,101)
    r=run((rows,cal),Configuration(FAILED))
    assert r["signals"]==[]


@pytest.mark.parametrize("problem", ["missing","off_calendar","duplicate","identity","nonfinite","bad_range"])
def test_invalid_history_fails_without_imputation(inputs,problem):
    rows,cal=inputs
    if problem=="missing":rows.pop(100)
    if problem=="off_calendar":rows[100]["session_date"]="2025-09-07"
    if problem=="duplicate":rows[100]=deepcopy(rows[99])
    if problem=="identity":rows[100]["security_id"]="GOOGL"
    if problem=="nonfinite":rows[100]["close"]="NaN"
    if problem=="bad_range":rows[100]["high"]="1"
    with pytest.raises(ValueError):run((rows,cal))


def test_stable_setup_signal_ids_and_different_configuration(inputs):
    a,b=run(inputs),run(inputs)
    assert a==b
    assert len({s["signal_id"] for s in a["signals"]})==len(a["signals"])
    c=run(inputs,Configuration(stop_atr_multiple="2"))
    assert a["signals"][0]["signal_id"]!=c["signals"][0]["signal_id"]


class Context:
    content_sha256="c"*64
    def __init__(self,state):self.state=state
    def context_as_of(self,decision):
        if self.state is None:return {"status":"UNAVAILABLE","reason":"UNKNOWN_AVAILABILITY"}
        return {"status":"AVAILABLE_UNDER_RECONSTRUCTED_ASSUMPTION", "context":{"descriptive_state":self.state,
                "available_at":(timestamp(decision)-timedelta(days=1)).isoformat()},"historical_dissemination_verified":False}


@pytest.mark.parametrize("state", ["UPTREND","DOWNTREND","MIXED",None])
def test_context_never_changes_raw_detection(inputs,state):
    a,b=run(inputs),run(inputs,context=Context(state))
    assert a["triggers"]==b["triggers"]
    assert [s["signal_id"] for s in a["signals"]]==[s["signal_id"] for s in b["signals"]]
    assert a["trade_plans"]==b["trade_plans"]
    assert b["market_context_links"][0]["context_bundle_sha256"]=="c"*64


def test_real_context_reader_strict_availability_used_at_signal_time(inputs):
    from equity_research.market_context.dataset import MarketContext
    rows,_=inputs
    result=run(inputs)
    decision=result["signals"][0]["trigger"]["available_at"]
    # Exercise the actual PR7A lookup on a minimal in-memory indexed snapshot.
    ctx=object.__new__(MarketContext)
    ctx._rows=[{"session_date":"previous", "available_at":(timestamp(decision)-timedelta(days=1)).isoformat()},
               {"session_date":"equal", "available_at":decision},
               {"session_date":"future", "available_at":(timestamp(decision)+timedelta(seconds=1)).isoformat()}]
    ctx._eligible=[(timestamp(r["available_at"]),i) for i,r in enumerate(ctx._rows)]
    ctx._hashes={"bundle_sha256":"c"*64}
    ctx._manifest={"market_reference_set_id":"r", "source_dataset_hashes":{}}
    linked=run(inputs,context=ctx)["market_context_links"][0]
    assert linked["context"]["session_date"]=="previous"
    ctx._eligible=ctx._eligible[1:]
    assert run(inputs,context=ctx)["market_context_links"][0]["status"]=="UNAVAILABLE"


class Events:
    def __init__(self,day,published,unknown=False):self.day,self.published,self.unknown=day,published,unknown
    def as_known(self,cutoff):
        action={"event_type":"DIVIDEND","effective_date":None if self.unknown else self.day,"event_id":"action"}
        return {"events":[action] if timestamp(self.published)<timestamp(cutoff) else []}


def test_corporate_discontinuity_known_only_and_unknown_dates_never_overlap(inputs):
    rows,cal=failed_scenario(inputs)
    known=Events(rows[26]["session_date"],cal["sessions"][24]["closes_at"])
    r=run((rows,cal),Configuration(FAILED),events=known)
    assert any(e["outcome"]=="INVALIDATED_CORPORATE_ACTION" for e in r["setup_outcomes"])
    future=Events(rows[26]["session_date"],cal["sessions"][-1]["closes_at"])
    assert run((rows,cal),Configuration(FAILED),events=future)==run((rows,cal),Configuration(FAILED))
    unknown=Events(rows[26]["session_date"],cal["sessions"][24]["closes_at"],unknown=True)
    assert run((rows,cal),Configuration(FAILED),events=unknown)==run((rows,cal),Configuration(FAILED))


def test_long_plan_is_reference_not_fill_and_risk_is_provisional(inputs):
    rows,cal=inputs;r=run(inputs)
    p=r["trade_plans"][0];s=r["signals"][0]
    assert p["planned_entry_reference"]=="143"
    assert Decimal(p["planned_risk_per_share"])==Decimal(s["features"]["atr14"])*Decimal("1.5")
    assert Decimal(p["initial_stop_reference"])==Decimal("143")-Decimal(p["planned_risk_per_share"])
    assert p["earliest_entry_session"]==rows[200]["session_date"]
    assert p["expiry_session"]==rows[202]["session_date"]
    assert p["planned_position_size"] is None and p["planned_risk_dollars"] is None
    assert all(v is None for k,v in p["outcome_link"].items() if k!="signal_id")


def test_strict_synthetic_gap_sizing_costs_R_and_no_same_close(fixture_path):
    r=replay_plans(fixture_path/"data.csv",fixture_path/"manifest.json")
    e=r["executions"][0];p=r["research"]["trade_plans"][0];t=e["trade"]
    assert e["fills"][0]["session_date"].isoformat()==p["earliest_entry_session"]
    assert e["fills"][0]["price"]==Decimal("146.01")>Decimal(p["planned_entry_reference"])
    assert t["quantity"]==int(Decimal("100")/(t["entry_price"]-t["initial_stop"]))
    assert t["initial_risk_dollars"]==(t["entry_price"]-t["initial_stop"])*t["quantity"]
    assert t["net_pnl_dollars"]==t["gross_pnl_dollars"]-t["commission_dollars"]-t["fees_dollars"]-t["modeled_slippage_dollars"]
    assert t["realized_r"]==t["net_pnl_dollars"]/t["initial_risk_dollars"]
    assert t["exit_reason"]=="target"
    assert r["cancellation"]=="UNSUPPORTED_NO_EXTERNAL_CANCEL_EVENTS"


def revised_fixture(fixture_path,tmp_path,prices):
    import csv,io
    rows=list(csv.DictReader((fixture_path/"data.csv").read_text().splitlines()))
    for row,v in zip(rows[200:],prices):row.update(dict(zip(("open","high","low","close"),map(str,v))))
    stream=io.StringIO();w=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    data=stream.getvalue().encode();m=json.loads((fixture_path/"manifest.json").read_bytes());m["data_sha256"]=digest(data)
    (tmp_path/"data.csv").write_bytes(data);(tmp_path/"manifest.json").write_bytes(encode(m))
    return tmp_path/"data.csv",tmp_path/"manifest.json"


def test_existing_stop_first_ambiguity_and_actual_risk(fixture_path,tmp_path):
    data,m=revised_fixture(fixture_path,tmp_path,[(146,170,130,150)])
    r=replay_plans(data,m)["executions"][0]
    assert r["trade"]["exit_reason"]=="stop" and r["trade"]["stop_target_ambiguous"]
    assert r["trade"]["realized_r"]<Decimal("-1")


def test_existing_order_expiry_never_fills_later(fixture_path,tmp_path):
    data,m=revised_fixture(fixture_path,tmp_path,[(140,142,139,141)]*3+[(150,160,149,155)])
    result=replay_plans(data,m)
    r=result["executions"][0]
    assert r["status"]=="EXPIRED" and r["fills"]==[]
    assert r["order"]["eligible_sessions_seen"]==3


def test_one_security_reservation_and_duplicate_selection(fixture_path,tmp_path):
    data,m=revised_fixture(fixture_path,tmp_path,[(146,147,145,146),(148,149,147,148),(150,151,149,150)])
    cfg=Config.from_dict({"target_r":None})
    r=replay_plans(data,m,execution_configuration=cfg)
    assert len(r["research"]["signals"])>=2
    assert sum(x["trade"] is not None for x in r["executions"])==1
    assert any(x["reason_codes"]==["SECURITY_RESERVED_BY_PRIOR_SIGNAL"] for x in r["executions"])
    sid=r["selection"][0]
    assert len(replay_plans(data,m,signal_ids=[sid,sid])["executions"])==1


def test_unsupported_short_and_signal_identity_are_blocked(fixture_path):
    with pytest.raises(ValueError,match="SHORT_EXECUTION_UNSUPPORTED"):
        replay_plans(fixture_path/"data.csv",fixture_path/"manifest.json",configuration=Configuration(FAILED))
    with pytest.raises(ValueError,match="signal identity"):
        replay_plans(fixture_path/"data.csv",fixture_path/"manifest.json",signal_ids=["foreign"])


@pytest.mark.parametrize("adjustment,actions", [("IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED",[]),("raw",[{"type":"DIVIDEND"}])])
def test_native_basis_and_corporate_actions_rejected_by_unchanged_strict_loader(fixture_path,tmp_path,adjustment,actions):
    m=json.loads((fixture_path/"manifest.json").read_bytes());m.update(adjustment=adjustment,corporate_actions=actions)
    (tmp_path/"manifest.json").write_bytes(encode(m))
    with pytest.raises(ValueError,match="only raw"):
        replay_plans(fixture_path/"data.csv",tmp_path/"manifest.json")


def test_strict_cli_immutable_reproducible(fixture_path,tmp_path,capsys):
    args=["swing","replay","--data",str(fixture_path/"data.csv"),"--manifest",str(fixture_path/"manifest.json")]
    assert main(args+["--output",str(tmp_path/"a")])==0
    assert main(args+["--output",str(tmp_path/"b")])==0
    assert read_bundle(tmp_path/"a")==read_bundle(tmp_path/"b")
    assert main(args+["--output",str(tmp_path/"a")])==2


# Reuse prior synthetic evidence builders; no actual local market rows in tests.
from test_events import price_bundle, event, source
from equity_research.events.model import freeze_events
from equity_research.events.dataset import freeze_study


@pytest.fixture
def study_path(price_bundle,tmp_path):
    price_path,_=price_bundle
    e=event("DIVIDEND")
    freeze_events([e],[source([e])],tmp_path/"events")
    freeze_study(price_path,tmp_path/"events","AAPL",tmp_path/"study")
    return tmp_path/"study"


def test_frozen_research_reproducible_embedded_inputs_and_complete_inventory(study_path,tmp_path):
    cfg=Configuration(FAILED)
    args=dict(configuration=cfg,start="2024-10-01",end="2024-12-20")
    a=freeze_strategy(study_path,None,tmp_path/"a",**args)
    b=freeze_strategy(study_path,None,tmp_path/"b",**args)
    assert a==b
    loaded=load_strategy(tmp_path/"a")
    assert loaded.content_sha256==a["bundle_sha256"]
    assert loaded.results["quality_report"]["fills"]=="NOT_COMPUTED_RESEARCH_MODE"
    inventory=json.loads(read_bundle(tmp_path/"a")[0]["corporate_action_inventory.json"])
    assert len(inventory["events"])==1
    assert inventory["events"][0]["effective_date"] is None
    assert inventory["events"][0]["payload"]["ex_date_status"]=="UNKNOWN"
    with pytest.raises(FileExistsError):freeze_strategy(study_path,None,tmp_path/"a",**args)
    import shutil
    shutil.rmtree(study_path)
    assert load_strategy(tmp_path/"a").results==loaded.results


@pytest.mark.parametrize("part",["identity","signal","lineage","inventory","config"])
def test_resealed_semantic_tampering_is_rejected(study_path,tmp_path,part):
    freeze_strategy(study_path,None,tmp_path/"a",configuration=Configuration(FAILED),start="2024-10-01",end="2024-12-20")
    files,_=read_bundle(tmp_path/"a")
    filename={"identity":"strategy_manifest.json","signal":"signals.json","lineage":"strategy_manifest.json",
              "inventory":"corporate_action_inventory.json","config":"strategy_config.json"}[part]
    raw=json.loads(files[filename])
    if part=="identity":raw["security_id"]="GOOGL"
    elif part=="signal":raw.append({"forged":"signal"})
    elif part=="lineage":raw["inputs"]["study"]["bundle_sha256"]="0"*64
    elif part=="inventory":raw["events"]=[]
    else:raw["risk"]["atr_period"]=1
    files[filename]=encode(raw)
    write_bundle(tmp_path/"bad",files)
    with pytest.raises(ValueError):load_strategy(tmp_path/"bad")


def test_offline_research_cli_and_reader_without_any_optional_sdk(study_path,tmp_path):
    config=tmp_path/"config.json";config.write_bytes(encode(Configuration(FAILED).record()))
    assert main(["swing","research","--study",str(study_path),"--strategy-config",str(config),
                 "--start","2024-10-01","--end","2024-12-20","--output",str(tmp_path/"research")])==0
    code='''
import importlib.abc,sys,socket
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,name,*args):
  if name.split('.')[0] in {'ib_async','yfinance','pandas','numpy','pyarrow','exchange_calendars'} or name.startswith('equity_research.providers'):
   raise AssertionError('optional/acquisition import: '+name)
sys.meta_path.insert(0,Deny())
def forbidden(*a,**k):raise AssertionError('network/account/order operation')
socket.socket.connect=forbidden
socket.socket.connect_ex=forbidden
socket.create_connection=forbidden
from equity_research.swing import load_strategy
print(load_strategy(sys.argv[1]).results['quality_report']['confirmed_triggers'])
'''
    import os
    env={**os.environ,"PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    result=subprocess.run([sys.executable,"-c",code,str(tmp_path/"research")],env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr


@pytest.mark.parametrize("kwargs",[{"strategy_id":"unknown"},{"lookback_sessions":0},{"failure_sessions":True},
                                    {"stop_atr_multiple":"NaN"},{"stop_atr_multiple":"0"},{"delay_minutes":361}])
def test_invalid_strategy_configuration(kwargs):
    with pytest.raises(ValueError):Configuration(**kwargs)


def test_future_bar_availability_cannot_leak_into_prior_features(inputs):
    rows,cal=inputs
    rows[198]["available_at"]=cal["sessions"][201]["closes_at"]
    with pytest.raises(ValueError,match="availability"):
        run(inputs)


def test_engine_is_independent_of_caller_decimal_precision(inputs):
    from decimal import localcontext
    expected=run(inputs)
    with localcontext() as ctx:
        ctx.prec=6
        assert run(inputs)==expected


from test_market_context import inputs as context_prices


def test_embedded_context_reader_is_self_contained(study_path,context_prices,tmp_path):
    from equity_research.market_context import freeze_market_context
    freeze_market_context({s:context_prices for s in ("SPY","QQQ","RSP")},"2024-11-25","2024-12-03",tmp_path/"context")
    result=freeze_strategy(study_path,tmp_path/"context",tmp_path/"strategy",configuration=Configuration(FAILED),
                           start="2024-10-01",end="2024-12-20")
    assert load_strategy(tmp_path/"strategy").content_sha256==result["bundle_sha256"]
    files,hashes=read_bundle(tmp_path/"strategy")
    m=json.loads(files["strategy_manifest.json"])
    assert m["context_bundle_sha256"] is not None
    import shutil
    shutil.rmtree(tmp_path/"context")
    assert load_strategy(tmp_path/"strategy").manifest==m


def test_missing_frozen_input_fails_with_no_provider_fallback(tmp_path,capsys):
    assert main(["swing","research","--study",str(tmp_path/"missing"),"--output",str(tmp_path/"out")])==2
    assert not (tmp_path/"out").exists()


def test_nonpositive_stop_remains_an_invalid_plan(inputs,fixture_path):
    cfg=Configuration(stop_atr_multiple="1000")
    result=run(inputs,cfg)
    assert result["signals"]
    assert all(p["invalidation_reason"]=="NONPOSITIVE_STOP" for p in result["trade_plans"])
    replay=replay_plans(fixture_path/"data.csv",fixture_path/"manifest.json",configuration=cfg)
    assert all(e["status"]=="REJECTED" and e["fills"]==[] for e in replay["executions"])


def test_synthetic_hand_reconciliation_includes_all_signals_and_losing_fill(fixture_path):
    r=replay_plans(fixture_path/"data.csv",fixture_path/"manifest.json")
    assert len(r["research"]["signals"])==len(r["executions"])==2
    winner,loser=[e["trade"] for e in r["executions"]]
    assert winner["initial_stop"]==Decimal("139.67")
    assert winner["initial_risk_dollars"]==Decimal("95.10")
    assert winner["quantity"]==15
    assert winner["gross_pnl_dollars"]==Decimal("190.35")
    assert winner["net_pnl_dollars"]==Decimal("188.90")
    assert loser["initial_risk_dollars"]==Decimal("98.80")
    assert loser["net_pnl_dollars"]==Decimal("-100.20")
    assert loser["stop_target_ambiguous"] and loser["entry_exit_order_ambiguous"]
    assert loser["realized_r"]==Decimal("-100.20")/Decimal("98.80")
