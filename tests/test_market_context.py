"""Deterministic synthetic market context, no trading policy or real market rows."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from equity_research.cli import main
from equity_research.history.cache import HistoryCache, history
from equity_research.history.contracts import Security
from equity_research.history.dataset import freeze, load_research_dataset
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from equity_research.market_context import Configuration, freeze_market_context, load_market_context, required_history_sessions
from equity_research.market_context.model import build_rows, feature_definitions
from test_history import MockIB, VirtualTime, ib_provider, bars

START, END = "2024-11-25", "2024-12-03"


@pytest.fixture(scope="module")
def inputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("market-references")
    securities = [Security(s, "synthetic:" + s, "synthetic reviewed ETF identity", s, s, x, v, con_id=i)
                  for s, x, v, i in (("SPY", "ARCA", "ARCX", 101), ("QQQ", "NASDAQ", "XNAS", 202), ("RSP", "ARCA", "ARCX", 303))]

    class Bounded(MockIB):
        async def historical(self, contract, params):
            end = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date() - timedelta(days=1)
            start = end - timedelta(days=int(params["durationStr"].split()[0]) - 1)
            frame = bars(start.isoformat(), end.isoformat(), adjusted=False).astype(float)
            for i, d in enumerate(frame.index):
                n = (d.date() - datetime(2023, 1, 3).date()).days
                close = 100 + contract.conId / 10 + n / 100
                frame.loc[d, ["Open", "High", "Low", "Close"]] = [close - .2, close + 2, close - 2, close]
            return [SimpleNamespace(date=d.date(), **{k.lower(): v for k, v in row.items()}) for d, row in frame.iterrows()]

    cache = HistoryCache(root / "cache")
    provider = ib_provider(Bounded(), clock=lambda: datetime(2025, 1, 1, tzinfo=UTC))
    result = history(cache, provider, securities, "2023-01-03", "2024-12-06")
    assert result["status"] == "SUCCESS"
    freeze(cache, "ibkr", securities, "2023-01-03", "2024-12-06", root / "prices")
    return root / "prices"


def datasets(inputs):
    ds = load_research_dataset(inputs)
    return {s: ds for s in ("SPY", "QQQ", "RSP")}


def calculate(inputs, *, start=START, end=END, config=None, transform=None):
    refs = datasets(inputs)
    if transform:
        refs = transform(refs)
    return build_rows(refs, schedule("2023-01-03", end), start, end, config or Configuration())


class Changed:
    def __init__(self, original, *, rows=None, manifest=None, quality=None):
        self.original, self.rows = original, rows
        self.manifest = manifest or original.manifest
        self.content_sha256 = original.content_sha256
        self.changed_quality = quality
    def bars(self, symbol): return self.rows if self.rows is not None else self.original.bars(symbol)
    def quality(self, symbol): return self.changed_quality or self.original.quality(symbol)


def test_continuous_formulas_and_exact_warmup(inputs):
    from statistics import mean, pstdev
    from market_shared import atr_simple_series, true_range
    assert required_history_sessions() == 220
    row = calculate(inputs)[0]
    ds = load_research_dataset(inputs)
    a = [r for r in ds.bars("SPY") if r["session_date"] <= START]
    c = [float(r["close"]) for r in a]
    t, v = row["trend_features"], row["volatility_features"]
    for n in (50, 150, 200):
        assert t[f"SPY.close_sma{n}"]["value"] == pytest.approx(c[-1] / mean(c[-n:]) - 1)
    for x, y in ((50, 200), (50, 150), (150, 200)):
        assert t[f"SPY.sma{x}_sma{y}"]["value"] == pytest.approx(mean(c[-x:]) / mean(c[-y:]) - 1)
    assert t["SPY.sma200_slope20"]["value"] == pytest.approx(mean(c[-200:]) / mean(c[-220:-20]) - 1)
    for n in (20, 60):
        assert t[f"SPY.return{n}"]["value"] == pytest.approx(c[-1] / c[-n-1] - 1)
    changes = [b / a - 1 for a, b in zip(c[-21:], c[-20:])]
    assert v["SPY.realized_volatility20"]["value"] == pytest.approx(pstdev(changes))
    atr_bars = a[-15:]
    tr = [true_range(float(b["high"]), float(b["low"]), float(a["close"])) for a, b in zip(atr_bars, atr_bars[1:])]
    assert v["SPY.atr14_close"]["value"] == pytest.approx(atr_simple_series(tr, 14)[-1] / c[-1])
    assert v["SPY.range20_close"]["value"] == pytest.approx((max(float(r["high"]) for r in a[-20:])-min(float(r["low"]) for r in a[-20:]))/c[-1])


def test_participation_is_native_ratio_not_breadth(inputs):
    row = calculate(inputs)[0]
    ds = load_research_dataset(inputs)
    spy = [float(r["close"]) for r in ds.bars("SPY") if r["session_date"] <= START]
    rsp = [float(r["close"]) for r in ds.bars("RSP") if r["session_date"] <= START]
    ratio = [a/b for a,b in zip(rsp,spy)]
    from statistics import mean
    p = row["participation_proxies"]
    assert p["RSP_SPY.level"]["value"] == ratio[-1]
    assert p["RSP_SPY.change20"]["value"] == ratio[-1]/ratio[-21]-1
    assert p["RSP_SPY.relative_sma50"]["value"] == ratio[-1]/mean(ratio[-50:])-1
    assert all(v == {"value":None,"status":"UNAVAILABLE","reason":"HISTORICAL_CONSTITUENT_DATA_NOT_PROVIDED","last_included_observation":None} for v in row["breadth_features"].values())
    assert row["descriptive_state"] == "UPTREND"  # Missing breadth is not bearish.


def test_expected_session_gaps_only_invalidate_affected_windows(inputs):
    def missing(refs):
        ds=refs["RSP"]
        refs["RSP"]=Changed(ds, rows=[r for r in ds.bars("RSP") if r["session_date"]!="2024-11-22"])
        return refs
    row=calculate(inputs,transform=missing)[0]
    assert all(v["status"]=="AVAILABLE" for k,v in row["trend_features"].items() if not k.startswith("RSP."))
    assert row["participation_proxies"]["RSP_SPY.level"]["status"]=="AVAILABLE"
    assert row["participation_proxies"]["RSP_SPY.relative_sma50"]["reason"]=="MISSING_EXPECTED_SESSION"
    assert row["trend_features"]["RSP.return20"]["value"] is None


def test_partial_warmup_is_explicit_and_never_filled(inputs):
    rows=calculate(inputs,start="2023-01-03",end="2023-03-20")
    assert rows[0]["trend_features"]["SPY.close_sma50"]["reason"]=="INSUFFICIENT_WARMUP"
    assert rows[0]["descriptive_state"]=="UNCLASSIFIED"
    last=rows[-1]
    assert last["trend_features"]["SPY.close_sma50"]["value"] is not None
    assert last["trend_features"]["SPY.sma200_slope20"]["value"] is None
    assert last["participation_proxies"]["RSP_SPY.relative_sma50"]["value"] is not None


@pytest.mark.parametrize("problem",["nonfinite","off_calendar","duplicate","price_basis","different_basis","conflict","identity","qualified_identity"])
def test_invalid_reference_evidence_rejected(inputs,problem):
    def change(refs):
        ds=refs["QQQ"];rows=list(ds.bars("QQQ"));m=ds.manifest;q=ds.quality("QQQ")
        if problem=="nonfinite":rows[0]["close"]="NaN"
        if problem=="off_calendar":rows[0]["session_date"]="2023-01-07"
        if problem=="duplicate":rows.append(rows[0])
        if problem=="price_basis":rows[0]["price_basis"]="RAW_VERIFIED"
        if problem=="different_basis":m["securities"]["QQQ"]["basis"]["verified"]=True
        if problem=="conflict":q["issues"]=[{"status":"FAIL","code":"CONFLICTING_SOURCE"}]
        if problem=="identity":m["securities"]["QQQ"]["security"]["security_id"]=m["securities"]["SPY"]["security"]["security_id"]
        if problem=="qualified_identity":m["securities"]["QQQ"]["qualified_contract"]["symbol"]="SPY"
        refs["QQQ"]=Changed(ds,rows=rows,manifest=m,quality=q)
        return refs
    with pytest.raises(ValueError):calculate(inputs,transform=change)


def test_future_price_poisoning_does_not_change_prior_features(inputs):
    before=calculate(inputs)
    def poison(refs):
        for role,ds in list(refs.items()):
            rows=list(ds.bars(role))
            for r in rows:
                if r["session_date"]>START:
                    for k in ("open","high","low","close"):r[k]=str(float(r[k])*10)
            refs[role]=Changed(ds,rows=rows)
        return refs
    after=calculate(inputs,transform=poison)
    assert before[0]==after[0]
    assert before[-1]!=after[-1]


def test_slope_first_available_at_exactly_220_observations(inputs):
    days=schedule("2023-01-03","2023-12-01")["sessions"]
    rows=calculate(inputs,start=days[218]["session_date"],end=days[219]["session_date"])
    assert rows[0]["trend_features"]["SPY.sma200_slope20"]["reason"]=="INSUFFICIENT_WARMUP"
    assert rows[1]["trend_features"]["SPY.sma200_slope20"]["status"]=="AVAILABLE"


@pytest.mark.parametrize("mode,expected",[("down","DOWNTREND"),("mixed","MIXED")])
def test_descriptors_are_symmetric_and_do_not_require_breadth(inputs,mode,expected):
    def descending(refs):
        for role in (("SPY","QQQ") if mode=="down" else ("QQQ",)):
            ds=refs[role];rows=list(ds.bars(role))
            for r in rows:
                close=500-float(r["close"])
                r.update(open=str(close-.2),high=str(close+2),low=str(close-2),close=str(close))
            refs[role]=Changed(ds,rows=rows)
        return refs
    r=calculate(inputs,transform=descending)[0]
    assert r["descriptive_state"]==expected
    assert all(v["status"]=="UNAVAILABLE" for v in r["breadth_features"].values())


@pytest.fixture
def bundle(inputs,tmp_path):
    target=tmp_path/"context"
    freeze_market_context({s:inputs for s in ("SPY","QQQ","RSP")},START,END,target)
    return target


def test_completed_session_as_of_and_no_same_session_lookahead(bundle):
    c=load_market_context(bundle)
    assert c.context_as_of("2024-11-25T15:59:59-05:00")["status"]=="UNAVAILABLE"
    assert c.context_as_of("2024-11-25T17:00:00-05:00")["status"]=="UNAVAILABLE"
    assert c.context_as_of("2024-11-25T17:00:01-05:00")["context"]["session_date"]==START
    r=c.context_as_of("2024-11-26T09:30:00-05:00")
    assert r["context"]["session_date"]==START
    assert r["status"]=="AVAILABLE_UNDER_RECONSTRUCTED_ASSUMPTION"
    assert r["historical_dissemination_verified"] is False
    with pytest.raises(ValueError):c.context_as_of("2024-11-26T10:00:00")


def test_early_close_holiday_and_weekend_lookup(bundle):
    c=load_market_context(bundle)
    assert c.context_as_of("2024-11-28T12:00:00-05:00")["context"]["session_date"]=="2024-11-27"
    assert c.context_as_of("2024-11-29T13:30:00-05:00")["context"]["session_date"]=="2024-11-27"
    assert c.context_as_of("2024-11-29T14:00:01-05:00")["context"]["session_date"]=="2024-11-29"
    assert c.context_as_of("2024-12-01T12:00:00-05:00")["context"]["session_date"]=="2024-11-29"


def test_dst_and_unknown_availability(inputs,tmp_path):
    r=calculate(inputs,start="2024-03-08",end="2024-03-11")
    assert r[0]["available_at"]=="2024-03-08T22:00:00+00:00"
    assert r[1]["available_at"]=="2024-03-11T21:00:00+00:00"
    output=tmp_path/"unknown"
    freeze_market_context({s:inputs for s in ("SPY","QQQ","RSP")},START,END,output,configuration=Configuration(availability="UNKNOWN"))
    c=load_market_context(output)
    assert c.observations()[0]["available_at"] is None
    assert c.context_as_of("2030-01-01T00:00:00+00:00")["status"]=="UNAVAILABLE"
    with pytest.raises(ValueError):Configuration(availability="VERIFIED")


def test_deterministic_self_contained_provenance_and_immutable_output(inputs,bundle,tmp_path):
    copy=tmp_path/"copy"
    expected=read_bundle(bundle)
    freeze_market_context({s:inputs for s in ("SPY","QQQ","RSP")},START,END,copy)
    assert read_bundle(copy)==expected
    with pytest.raises(FileExistsError):freeze_market_context({s:inputs for s in ("SPY","QQQ","RSP")},START,END,bundle)
    c=load_market_context(copy)
    assert c.quality["complete_core_rows"]==6
    assert c.quality["rows_with_missing_optional_features"]==6
    assert len(set(c.manifest["source_dataset_hashes"].values()))==1
    script='''
import importlib.abc,sys,socket
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in {'ib_async','yfinance','pandas','numpy','pyarrow','exchange_calendars'} or fullname.startswith('equity_research.providers'):
   raise AssertionError(fullname)
sys.meta_path.insert(0,Deny())
def no(*a,**k):raise AssertionError('network')
socket.socket.connect=no
socket.create_connection=no
from equity_research.market_context import load_market_context
c=load_market_context(sys.argv[1]);assert len(c.observations())==6
'''
    # Copy only the composed bundle to a different directory; no source lookup.
    r=subprocess.run([sys.executable,"-c",script,str(copy)],capture_output=True,text=True,cwd=tmp_path,
                     env=os.environ | {"PYTHONPATH":str(Path(__file__).resolve().parents[1]/"src")})
    assert r.returncode==0,r.stderr


def test_resealed_lookahead_or_feature_tampering_rejected(bundle,tmp_path):
    files,_=read_bundle(bundle)
    rows=json.loads(files["market_context_daily.json"])
    rows[0]["available_at"]="2024-11-25T09:00:00-05:00"
    files["market_context_daily.json"]=encode(rows)
    write_bundle(tmp_path/"bad",files)
    with pytest.raises(ValueError,match="causal"):load_market_context(tmp_path/"bad")


def test_cli_and_state_extension_has_no_trade_permission(inputs,tmp_path):
    output=tmp_path/"cli"
    assert main(["data","market-context","--spy-dataset",str(inputs),"--qqq-dataset",str(inputs),"--rsp-dataset",str(inputs),"--start",START,"--end",END,"--output",str(output),"--no-state"])==0
    c=load_market_context(output)
    assert all(r["descriptive_state"] is None for r in c.observations())
    assert c.manifest["assumed_availability"]["trading_permission_rule"]=="NONE"
    assert len(feature_definitions())==33
