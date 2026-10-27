"""Synthetic offline source and price evidence; no subscriber originals or broker."""

from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
import json
from pathlib import Path

import pytest

from equity_research.cli import main
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.history.depth_store import freeze_report
from equity_research.lifecycle.model import compatible, simulate
from equity_research.lifecycle.source import CLOSED, OPEN, UNIVERSE, parse_alerts, reconstruct
from equity_research.lifecycle.study import derive, freeze_inputs, freeze_study, load_study, read_inputs
from test_ibkr_depth import Fake, auditor

ROOT = Path(__file__).parents[1]
METHOD = json.loads((ROOT / "experiments/grimes-current-methodology-v1.json").read_bytes())


def alerts_fixture():
    # Synthetic render of public task facts, not the captured newsletter bodies.
    adds = ["AAPL long 339.00;CLMT long 55.25;TEVA long 40.40;CAT short 748.75;CDE short 16.40;T short 24.00",
        "", "ELF long 110.50;HUM long 404.00;SIG long 111.80;ASST short 28.45;OMER short 17.20",
        "GME long 25.01;AAOI short 89.82;AMD short 569.90;ANET short 191.25;SNDK short 1458.00", "",
        "ABBV long 276.30;CNQ long 53.30;EBAY long 119.20;GTLB long 51.60;MMM long 169.90;SNOW short 330.70",
        "SAIL long 20.90;SLB long 51.10;GE short 295.80;SCCO short 191.70"]
    changes = ["", "AAPL 337.80 339.00;CLMT 53.40 55.25;CDE 16.24 16.40;T 23.80 24.00",
        "AAPL 336.25 337.80;CLMT 53.02 53.40", "TEVA 39.35 40.40;T 22.20 23.80",
        "ELF 108.60 110.50;GME 24.78 25.01;HUM 408.10 404.00;TEVA 39.05 39.35;AAPL 343.50 336.25;OMER 17.35 17.20;AAOI 70.70 89.82;AMD 519.35 569.90;ANET 176.80 191.25;CDE 14.30 16.24;SNDK 1296.00 1458.00",
        "ELF 109.20 108.60;GME 24.40 24.78;SIG 112.50 111.80;AAPL 344.70 343.50;ANET 175.20 176.80;CDE 13.90 14.30",
        "EBAY 117.50 119.20;GTLB 52.10 51.60"]
    setup = ["", "T short", "", "", "AAPL long;AAOI short;AMD short;ANET short;CDE short;SNDK short", "", ""]
    drops = ["PLTR long;PEP short", "", "CAT short", "CLMT long;ASST short", "T short (underway)",
        "TEVA long;AAOI short (underway);AMD short (underway);SNDK short (underway)",
        "GME long;AAPL long (underway);SNOW short;ANET short (underway)"]
    dates = ["2026-10-18T15:20:00-04:00", "2026-10-19T18:19:00-04:00", "2026-10-20T18:25:00-04:00",
        "2026-10-21T18:50:00-04:00", "2026-10-22T18:27:00-04:00", None, "2026-10-26T18:10:00-04:00"]
    result = []
    for i in range(7):
        actions = [[], [], [], []]
        for a in filter(None, adds[i].split(";")):
            s, d, stop = a.split(); actions[0].append(f"{s} added {d} with stop {stop}")
        for a in filter(None, changes[i].split(";")):
            s, new, old = a.split(); actions[1].append(f"{s} stop moved to {new} from {old}")
        for a in filter(None, setup[i].split(";")):
            s, d = a.split(); actions[2].append(f"{s} setup changed to {d} (underway) from {d}")
        for a in filter(None, drops[i].split(";")):
            s, rest = a.split(" ", 1); actions[3].append(f"{s} dropped from {rest}")
        text = "Synthetic market preamble; no actual expert commentary.\n"+"\n".join(
            h+"________\n"+("\n".join(a) if a else "None") for h, a in zip(
                ("Added", "Stop Changed", "Setup Changed", "Dropped"), actions))+"\n---\n"
        result.append({"alert_id": f"alert-{i+1}", "source_sequence": i, "text": text, "html": "<p>Synthetic</p>",
            "source_reference": "Synthetic test only", "published_at": dates[i],
            "publication_precision": "MINUTE" if dates[i] else "UNKNOWN",
            "original_publication_display": dates[i] or "Yesterday at 8:57 AM",
            "email_received_at": "2026-10-25T12:57:45Z" if i == 5 else None})
    return {"schema_version": "grimes_alerts_v1", "origin": "synthetic", "alerts": result}


def ledger(alerts=None, bound=True):
    events, _, _ = parse_alerts(alerts or alerts_fixture(), allow_email_bound=bound)
    return reconstruct(events)


def test_exact_inventory_seven_verbatim_and_source_states():
    alerts = alerts_fixture()
    original = deepcopy(alerts)
    events, excluded, commentary = parse_alerts(alerts, allow_email_bound=True)
    trades, history, transitions = reconstruct(events)
    assert alerts == original and len(alerts["alerts"]) == len(commentary) == 7
    assert {t["symbol"] for t in trades} == set(UNIVERSE) and len(trades) == 26
    assert {t["symbol"] for t in trades if t["position_state"] == "CLOSED"} == set(CLOSED)
    assert {t["symbol"] for t in trades if t["position_state"] == "OPEN"} == set(OPEN)
    assert {e["symbol"] for e in excluded} == {"PEP", "PLTR"}
    assert not {e["symbol"] for e in events} & {"PEP", "PLTR"}
    assert len(events) == 72 and len(history) == 53 and len(transitions) == 7
    assert all(e["source"]["source_text"] in alerts["alerts"][int(e["source"]["alert_id"][-1])-1]["text"] for e in events)


def test_setup_is_same_open_position_and_nonmonotone_stop_history():
    trades, history, transitions = ledger()
    apple = next(t for t in trades if t["symbol"] == "AAPL")
    assert len({e["trade_id"] for e in apple["events"]}) == 1
    assert [r["change"] for r in history if r["symbol"] == "AAPL"] == ["INITIAL", "WIDENING", "WIDENING", "TIGHTENING", "TIGHTENING"]
    assert next(r for r in history if r["symbol"] == "OMER" and r["change"] != "INITIAL")["change"] == "WIDENING"
    last = next(r for r in history if r["symbol"] == "AAPL" and r["reported_stop"] == "344.70")
    assert last["setup_availability"] == "UNDERWAY"
    t = next(t for t in trades if t["symbol"] == "CDE")
    assert t["position_state"] == "OPEN" and t["setup_availability"] == "UNDERWAY"


def test_unknown_weekly_publication_stays_unknown_with_optional_separate_bound():
    no, _, _ = parse_alerts(alerts_fixture())
    yes, _, _ = parse_alerts(alerts_fixture(), allow_email_bound=True)
    weekly = [e for e in yes if e["source"]["alert_id"] == "alert-6"]
    assert all(e["published_at"] is None and e["publication_display"] == "Yesterday at 8:57 AM" for e in weekly)
    assert all(e["effective_at"] is None for e in no if e["source"]["alert_id"] == "alert-6")
    assert all(e["effective_clock"] == "EMAIL_AVAILABILITY_BOUND_NOT_EXACT_PUBLICATION" for e in weekly)


def test_capture_original_input_and_plain_text_only_bodies(tmp_path):
    record = alerts_fixture()
    del record["alerts"][0]["html"]
    original = encode(record)
    (tmp_path / "original.json").write_bytes(original)
    assert main(["lifecycle", "capture-alerts", "--input", str(tmp_path / "original.json"), "--output", str(tmp_path / "capture")]) == 0
    files, _ = read_bundle(tmp_path / "capture")
    assert files["original-input.json"] == original
    assert files["alert-1.html"] == b""
    assert all(files[a["alert_id"]+".txt"] == a["text"].encode() for a in record["alerts"])
    assert json.loads(files["alerts.json"])["alerts"][5]["published_at"] is None


def episode(direction="LONG", stop="95", opening="2026-10-18T15:20:00-04:00", extra=()):
    event = {"event_id": "open", "source_order": 0, "type": "OPEN_NEW_POSITION", "symbol": "EBAY",
        "direction": direction, "stop": stop, "published_at": opening, "effective_at": opening,
        "effective_clock": "SYNTHETIC_SECOND_PRECISION"}
    return reconstruct([event]+list(extra), validate_pilot=False)[0]


def revision(stop, old="95", when="2026-10-19T18:00:00-04:00", kind="STOP_CHANGED"):
    return {"event_id": "revision", "source_order": 1, "symbol": "EBAY", "type": kind,
        "stop": stop, "previous_stop": old, "published_at": when, "effective_at": when,
        "effective_clock": "SYNTHETIC_SECOND_PRECISION"}


def model_case(trades, bars, *, basis=True, cutoff="2026-10-26T18:11:00-04:00"):
    calendar = schedule("2026-10-16", "2026-11-09")
    rows = [{"session_date": d, "open": str(o), "high": str(h), "low": str(l), "close": str(c)} for d, o, h, l, c in bars]
    cov = {"EBAY": {"contract": {"conId": 1}, "origin": "synthetic", "source_bundle_sha256": "test"}}
    evidence = [{"symbol": "EBAY", "con_id": 1, "status": "SYNTHETIC_COMPATIBLE", "origin": "synthetic", "source_reference": "Synthetic"}] if basis else []
    return simulate(trades, {"EBAY": rows}, cov, calendar, METHOD, cutoff=cutoff, basis_evidence=evidence)


@pytest.mark.parametrize("direction,stop,bar,closed", [("LONG", "95", (100, 103, 94, 101), True),
    ("LONG", "95", (100, 103, 96, 101), False), ("SHORT", "105", (100, 106, 98, 101), True),
    ("SHORT", "105", (100, 104, 98, 101), False)])
def test_directional_stop_touch_and_no_actual_fill(direction, stop, bar, closed):
    models, events, _ = model_case(episode(direction, stop), [("2026-10-19", *bar)], cutoff="2026-10-19T18:00:00-04:00")
    assert (models[0]["state"] == "MODELED_CLOSED") == closed
    if closed:
        trigger = next(e for e in events if e["type"] == "ASSUMED_STOP_TRIGGERED")
        assert trigger["actual_fill"] is None and trigger["fill_and_slippage"] == "UNKNOWN"


def test_ebay_old_stop_cannot_be_rescued_and_source_never_rewritten():
    t = episode(stop="119.20", opening="2026-10-25T08:57:45-04:00", extra=[revision("117.50", "119.20", "2026-10-26T18:11:00-04:00")])
    original = deepcopy(t)
    models, events, windows = model_case(t, [("2026-10-26", 121.24, 121.61, 117.87, 118.62)])
    assert t == original and t[0]["position_state"] == "OPEN" and t[0]["current_stop"] == "117.50"
    assert models[0]["state"] == "MODELED_CLOSED" and models[0]["original_per_share_risk"] == "2.04"
    assert len([e for e in events if e["type"] == "ASSUMED_STOP_TRIGGERED"]) == 1
    assert any(e["type"] == "SOURCE_MODEL_CONFLICT" and e.get("reported_stop") == "117.50" for e in events)
    assert len(models) == 1 and models[0]["actual_entry"] is None
    assert all(w["status"] == "MODELED_CLOSED_BEFORE_OR_DURING_HORIZON" for w in windows)


def test_no_reentry_without_new_open_but_explicit_reopen_gets_new_id():
    drop = {"event_id": "drop", "source_order": 1, "type": "DROPPED", "symbol": "EBAY", "direction": "LONG",
        "reported_underway": False, "published_at": "2026-10-19T18:00:00-04:00", "effective_at": "2026-10-19T18:00:00-04:00"}
    t = episode(extra=[drop])
    new = deepcopy(t[0]["events"][0]);new.update(event_id="new", source_order=2, published_at="2026-10-20T18:00:00-04:00", effective_at="2026-10-20T18:00:00-04:00")
    result, _, _ = reconstruct([t[0]["events"][0], drop, new], validate_pilot=False)
    assert [r["trade_id"] for r in result] == ["EBAY-001", "EBAY-002"]
    with pytest.raises(ValueError, match="already open"):
        reconstruct([t[0]["events"][0], new], validate_pilot=False)


def test_after_hours_next_open_no_same_day_cross_and_missing_entry_not_skipped():
    t = episode(opening="2026-10-19T18:00:00-04:00")
    models, events, _ = model_case(t, [("2026-10-19", 100, 102, 90, 99), ("2026-10-20", 100, 102, 99, 101)], cutoff="2026-10-20T18:00:00-04:00")
    assert models[0]["first_eligible_at"] == "2026-10-20T13:30:00+00:00"
    assert not any(e["type"] == "ASSUMED_STOP_TRIGGERED" for e in events)
    models, _, _ = model_case(t, [("2026-10-21", 100, 102, 99, 101)])
    assert models[0]["state"] == "UNRESOLVED_MISSING_SESSION" and models[0]["modeled_entry"] is None


def test_intraday_revision_daily_extremes_ambiguous():
    t = episode(extra=[revision("101", when="2026-10-19T12:00:00-04:00")])
    models, events, _ = model_case(t, [("2026-10-19", 100, 103, 99, 102)], cutoff="2026-10-19T18:00:00-04:00")
    assert models[0]["state"] == "TIMING_AMBIGUOUS"
    assert not any(e["type"] == "ASSUMED_STOP_TRIGGERED" for e in events)


def test_unknown_timing_or_basis_never_claims_certain_stop():
    t = episode(stop="119.20")
    models, events, _ = model_case(t, [("2026-10-19", 121, 122, 117, 120)], basis=False)
    assert models[0]["state"] == "UNRESOLVED_BASIS" and not events
    t[0]["events"][0]["effective_at"] = None
    models, events, _ = model_case(t, [("2026-10-19", 121, 122, 117, 120)])
    assert models[0]["state"] == "UNRESOLVED_TIMING" and not events


@pytest.mark.parametrize("direction,stop,bar,state", [("LONG", "95", (100, 106, 99, 104), "MODELED_OPEN_WITH_UNSPECIFIED_RUNNER"),
    ("SHORT", "105", (100, 102, 94, 96), "MODELED_CLOSED")])
def test_1r_long_minimum_partial_and_short_full(direction, stop, bar, state):
    models, events, _ = model_case(episode(direction, stop), [("2026-10-19", *bar)], cutoff="2026-10-19T18:00:00-04:00")
    m = models[0]
    assert m["state"] == state and m["original_per_share_risk"] == "5"
    target = next(e for e in events if e["type"] == "HYPOTHETICAL_TARGET_REACHED")
    assert target["management"]["exact_exit_fraction_of_original"] == (None if direction == "LONG" else "1")
    assert m["exact_long_exit_fraction"] is None and m["actual_fill"] is None


def test_r_fixed_after_stop_widening_and_time_windows_are_exploratory():
    t = episode(extra=[revision("90")])
    bars = [(d, 100, 101, 99, 99.5) for d in ("2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23")]
    models, events, windows = model_case(t, bars)
    assert models[0]["original_per_share_risk"] == "5" and models[0]["target_1R"] == "105"
    assert [w["horizon_sessions"] for w in windows] == [2, 3, 5]
    assert all(w["possible_time_stop"] is True and w["definitive_time_exit"] is False for w in windows)
    assert models[0]["state"] == "UNRESOLVED_MISSING_SESSION"  # October 26 missing, never filled.
    assert not any(e["type"] == "MODELED_CLOSED" for e in events)


def test_same_bar_stop_target_order_and_gap_uncertainty():
    models, events, _ = model_case(episode(), [("2026-10-19", 100, 106, 94, 102)], cutoff="2026-10-19T18:00:00-04:00")
    assert models[0]["state"] == "TIMING_AMBIGUOUS" and models[0]["target_status"] == "STOP_TARGET_ORDER_UNKNOWN"
    assert not any(e["type"] == "MODELED_CLOSED" for e in events)
    models, events, _ = model_case(episode(), [("2026-10-19", 93, 106, 92, 102)], cutoff="2026-10-19T18:00:00-04:00")
    assert models[0]["state"] == "MODELED_CLOSED"
    assert next(e for e in events if e["type"] == "ASSUMED_STOP_TRIGGERED")["gap_through_stop"]


def test_long_runner_stop_after_prior_partial_and_no_time_flag_after_full_close():
    bars = [("2026-10-19", 100, 106, 99, 104), ("2026-10-20", 106, 107, 94, 96)]
    models, events, windows = model_case(episode(), bars, cutoff="2026-10-20T18:00:00-04:00")
    assert models[0]["state"] == "MODELED_CLOSED" and models[0]["minimum_long_exit_fraction"] == "1/3"
    assert len([e for e in events if e["type"] == "HYPOTHETICAL_TARGET_REACHED"]) == 1
    assert len([e for e in events if e["type"] == "ASSUMED_STOP_TRIGGERED"]) == 1
    assert all(w["possible_time_stop"] is None for w in windows)


def test_price_units_require_matching_identity_exact_quote_and_complete_session_scope():
    e = {"con_id": 1, "status": "OPERATOR_QUOTE_ANCHORED_SESSION_SCALE", "source_reference": "Operator",
        "anchors": [{"session_date": "2026-10-26", "field": "low", "nominal_quote": "117.87",
            "source_status": "OPERATOR_PROVIDED_CONTEMPORANEOUS_QUOTE"}]}
    rows = {"2026-10-26": {"low": "117.87"}}
    assert compatible(e, {"conId": 1}, rows, ["2026-10-26"], "ibkr_client")
    assert not compatible(e, {"conId": 2}, rows, ["2026-10-26"], "ibkr_client")
    assert not compatible(e, {"conId": 1}, rows, ["2026-10-23", "2026-10-26"], "ibkr_client")
    assert not compatible(e, {"conId": 1}, {"2026-10-26": {"low": "58.935"}}, ["2026-10-26"], "ibkr_client")
    assert not compatible({**e, "status": "VERIFIED"}, {"conId": 1}, rows, ["2026-10-26"], "ibkr_client")
    assert not compatible({**e, "status": "SYNTHETIC_COMPATIBLE", "origin": "synthetic"}, {"conId": 1}, rows, ["2026-10-26"], "ibkr_client")


def test_source_drop_horizon_never_measures_subsequent_held_exposure():
    drop = {"event_id": "drop", "source_order": 1, "type": "DROPPED", "symbol": "EBAY", "direction": "LONG",
        "reported_underway": False, "published_at": "2026-10-19T18:00:00-04:00", "effective_at": "2026-10-19T18:00:00-04:00"}
    models, events, windows = model_case(episode(extra=[drop]), [("2026-10-19", 100, 101, 99, 100),
        ("2026-10-20", 100, 101, 99, 99.5)], cutoff="2026-10-20T18:00:00-04:00")
    assert models[0]["closed_session"] == "2026-10-19"
    assert windows[0]["status"] == "MODELED_CLOSED_BEFORE_OR_DURING_HORIZON"
    assert not any(e["type"] == "POSSIBLE_TIME_STOP" for e in events)


def test_source_closes_before_next_eligible_open_no_fictitious_modeled_entry():
    drop = {"event_id": "drop", "source_order": 1, "type": "DROPPED", "symbol": "EBAY", "direction": "LONG",
        "reported_underway": False, "published_at": "2026-10-18T18:00:00-04:00", "effective_at": "2026-10-18T18:00:00-04:00"}
    models, events, _ = model_case(episode(extra=[drop]), [("2026-10-19", 100, 102, 99, 101)])
    assert models[0]["state"] == "SOURCE_CLOSED_BEFORE_MODELED_ENTRY" and models[0]["modeled_entry"] is None
    assert not events


def test_intraday_source_drop_records_current_session_without_claiming_daily_extreme_order():
    drop = {"event_id": "drop", "source_order": 1, "type": "DROPPED", "symbol": "EBAY", "direction": "LONG",
        "reported_underway": False, "published_at": "2026-10-19T12:00:00-04:00", "effective_at": "2026-10-19T12:00:00-04:00"}
    models, events, _ = model_case(episode(extra=[drop]), [("2026-10-19", 100, 106, 94, 101)], cutoff="2026-10-19T18:00:00-04:00")
    assert models[0]["closed_session"] == "2026-10-19"
    assert models[0]["warnings"] == ["2026-10-19:DAILY_CANDLE_STRADDLES_SOURCE_REVISION_OR_CLOSURE"]
    assert [e["type"] for e in events] == ["MODELED_CLOSED"]
    assert events[0]["actual_fill"] is None and events[0]["source_closure_effective_bound"] == drop["effective_at"]


@pytest.fixture(scope="module")
def frozen(tmp_path_factory):
    root = tmp_path_factory.mktemp("lifecycle")
    symbols = UNIVERSE+("SPY", "QQQ", "RSP", "IWM", "XLK")
    ids = {s: 5000+i for i, s in enumerate(symbols)}

    class Broker(Fake):
        async def qualify(self, security):
            self.con_id = ids[security.symbol]
            return await super().qualify(security)

    mappings = [{"kind": "stock" if s in UNIVERSE else "sector_etf", "security": {"symbol": s, "security_id": f"synthetic:{s}",
        "reference": "Synthetic lifecycle only", "ibkr_symbol": s, "yahoo_symbol": s, "primary_exchange": "ARCA", "listing_venue": "ARCX"}} for s in symbols]
    config = {"schema_version": "ibkr_depth_config_v1", "start": "2026-09-01", "end": "2026-10-26", "window_days": 60,
        "head_timestamp": False, "instruments": mappings}
    audits = []
    for i, batch in enumerate((mappings[:16], mappings[16:])):
        auditor(Broker(), clock=lambda: datetime(2026, 10, 27, 1, tzinfo=UTC)).run(
            {**config, "instruments": batch}, root / f"audit-{i}")
        freeze_report(root / f"audit-{i}", root / f"audit-report-{i}")
        audits.append((root / f"audit-report-{i}", [r["security"]["symbol"] for r in batch]))
    alerts = alerts_fixture()
    files = {"alerts.json": encode(alerts)}
    for a in alerts["alerts"]:
        files[a["alert_id"]+".txt"] = a["text"].encode(); files[a["alert_id"]+".html"] = a["html"].encode()
    write_bundle(root / "alerts", files)
    spec = {"schema_version": "grimes_lifecycle_inputs_v1", "start": "2026-09-01", "end": "2026-10-26",
        "analysis_cutoff": "2026-10-26T18:11:00-04:00", "allow_email_availability_bound": True,
        "entry_rule": "NEXT_ELIGIBLE_REGULAR_OPEN", "basis_evidence": [{"symbol": s, "con_id": ids[s],
            "status": "SYNTHETIC_COMPATIBLE", "origin": "synthetic", "source_reference": "Synthetic only"} for s in UNIVERSE],
        "sector_proxies": [{"symbol": s, "con_id": ids[s], "proxy": "XLK", "proxy_con_id": ids["XLK"],
            "source_reference": "Synthetic", "evidence": "Synthetic mapping only"} for s in UNIVERSE], "dated_events": []}
    freeze_inputs(spec, root / "alerts", audits, ROOT / "experiments/grimes-current-methodology-v1.json", root / "inputs")
    inputs, _ = read_bundle(root / "inputs")
    return root, inputs, read_inputs(inputs)


def test_frozen_semantic_reproduction_cli_and_dossiers(frozen, tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: pytest.fail("offline study attempted network"))
    seal = freeze_study(frozen[0] / "inputs", tmp_path / "study")
    checked = load_study(tmp_path / "study")
    assert seal == checked["hashes"]
    assert {f"dossier-{s}.md" for s in UNIVERSE} <= set(checked["files"])
    assert main(["lifecycle", "replay", "--study", str(tmp_path / "study"), "--output", str(tmp_path / "replay")]) == 0
    assert read_bundle(tmp_path / "replay")[1] == seal
    with pytest.raises(FileExistsError):
        freeze_study(frozen[0] / "inputs", tmp_path / "study")


@pytest.mark.parametrize("artifact", ["source_stop_history.json", "source_trade_lifecycles.json", "modeled_trade_lifecycles.json", "comparison.json"])
def test_resealed_semantic_corruption_rejected(frozen, tmp_path, artifact):
    freeze_study(frozen[0] / "inputs", tmp_path / "original")
    files, _ = read_bundle(tmp_path / "original")
    value = json.loads(files[artifact])
    if isinstance(value, dict):
        value["invented"] = 1
    else:
        value[0]["invented"] = 1
    # The list artifacts are altered without breaking their valid JSON container type.
    files[artifact] = encode(value)
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        load_study(tmp_path / "resealed")


def test_future_prices_do_not_change_historical_event_context_and_gaps_unavailable(frozen):
    spec, alerts, prices, cov, cal, method = deepcopy(frozen[2])
    before = derive(spec, alerts, prices, cov, cal, method)
    for symbol, rows in prices.items():
        row = deepcopy(rows[-1]);row.update(session_date="2026-10-27", close="999999", price_basis="POISON")
        rows.append(row)
    after = derive(spec, alerts, prices, cov, cal, method)
    assert before == after
    prices["AAPL"] = [r for r in prices["AAPL"] if r["session_date"] != "2026-10-19"]
    result = derive(spec, alerts, prices, cov, cal, method)
    context = next(c for c in result["stock_context_at_events.json"] if c["symbol"] == "AAPL" and c["last_available_session"] == "2026-10-20")
    assert context["features"]["return_5d"]["status"] == "UNAVAILABLE"


def test_source_proof_native_frame_and_raw_alert_integrity(frozen):
    for artifact in ("alert-capture-alert-1.txt", "source-proofs.json"):
        files = deepcopy(frozen[1])
        if artifact.endswith(".txt"):
            files[artifact] += b"tampered"
        else:
            proofs = json.loads(files[artifact]); key = next(k for k in proofs[0]["files"] if k.endswith("returned_frame.json"))
            proofs[0]["files"][key] += " "
            files[artifact] = encode(proofs)
        with pytest.raises(ValueError, match="hash mismatch"):
            read_inputs(files)
