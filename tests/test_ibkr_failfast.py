"""Apparent persistence is a bounded stopping heuristic, not error-string lore."""

from datetime import datetime, timedelta
import json
from types import SimpleNamespace

import pytest

from equity_research.history.contracts import Security
from equity_research.history.cache import HistoryCache, history
from equity_research.ingestion.storage import read_bundle
from equity_research.providers.ibkr import classify
from test_history import MockIB, bars, ib_provider


class Failure(Exception):
    def __init__(self, code, message="private text must not be retained"):
        self.code = code
        super().__init__(message)


@pytest.mark.parametrize("callback",[False,True])
def test_two_consecutive_generic_failures_stop_later_chunks_and_preserve_attempts(tmp_path,callback):
    security=Security("SPY","synthetic:SPY","synthetic","SPY","SPY","ARCA","ARCX")
    backend=MockIB(event_errors=[{"code":162,"category":"PROVIDER_ERROR"}]*2) if callback else MockIB(failures=[Failure(162)]*2)
    fresh=ib_provider(backend).fetch_daily(security,"2024-01-02","2024-04-30",tmp_path/"attempt")
    a=fresh["acquisition"]
    assert a["status"]=="PARTIAL_RESPONSE"
    assert len(a["requests"])==2
    assert a["termination"]["reason"]=="REPEATED_NONTRANSIENT_PROVIDER_FAILURE"
    assert a["termination"]["unattempted_from"]=="2024-03-02"
    assert a["termination"]["consecutive_failed_chunks"]==2
    files,_=read_bundle(tmp_path/"attempt")
    if callback:
        assert len(json.loads(files["returned_bars.json"])["bars"])==2*len(backend.frame)
        assert all(r["native_rows_retained_but_not_selected"]==len(backend.frame) for r in a["requests"])
    assert b"private text" not in files["acquisition.json"]
    assert backend.disconnected
    assert all(c[0] in {"connect","qualify","historical","disconnect"} for c in backend.calls)


@pytest.mark.parametrize("scenario",["different_codes","no_data","transient","success_resets"])
def test_different_transient_and_date_specific_failures_do_not_trigger_persistence(tmp_path,scenario):
    s=Security("SPY","synthetic:SPY","synthetic","SPY","SPY","ARCA","ARCX")
    sequence={"different_codes":[Failure(162),Failure(999),Failure(998)],
              "no_data":[Failure(165),Failure(165),Failure(165)],
              "transient":[TimeoutError()]*3,
              "success_resets":[Failure(162),None,Failure(162)]}[scenario]
    class Responses(MockIB):
        async def historical(self,contract,params):
            self.calls.append(("historical",contract,params))
            item=sequence.pop(0) if sequence else None
            if item is not None:raise item
            end=datetime.strptime(params["endDateTime"],"%Y%m%d-%H:%M:%S").date()-timedelta(days=1)
            start=end-timedelta(days=int(params["durationStr"].split()[0])-1)
            return [SimpleNamespace(date=d.date(),**{k.lower():v for k,v in row.items()}) for d,row in bars(start.isoformat(),end.isoformat(),adjusted=False).iterrows()]
    backend=Responses()
    fresh=ib_provider(backend).fetch_daily(s,"2024-01-02","2024-04-30",tmp_path/"attempt")
    assert "termination" not in fresh["acquisition"]
    assert fresh["acquisition"]["requests"][-1]["end"]=="2024-04-30"


def test_generic_162_is_not_reclassified_as_permission_from_one_session_message():
    assert classify(162,"different IP")=="PROVIDER_ERROR"
    assert classify(162,"pacing violation")=="PACING"
    assert classify(162,"no market data permissions")=="DATA_PERMISSION"


def test_batch_report_exposes_termination_and_keeps_failed_capture(tmp_path):
    s=Security("SPY","synthetic:SPY","synthetic","SPY","SPY","ARCA","ARCX")
    report=history(HistoryCache(tmp_path/"cache"),ib_provider(MockIB(failures=[Failure(162)]*2)),[s],"2024-01-02","2024-04-30")
    r=report["results"][0]
    assert report["status"]=="PARTIAL_OR_FAILED" and r["cache_status"]=="NOT_PROMOTED"
    assert r["termination"]["reason"]=="REPEATED_NONTRANSIENT_PROVIDER_FAILURE"
    assert r["snapshot_sha256"]==read_bundle(r["snapshot_reference"])[1]["bundle_sha256"]
