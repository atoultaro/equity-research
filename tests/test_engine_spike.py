"""Small offline transport/intent tests; framework dependencies remain isolated."""

from decimal import Decimal
import json

import pytest

from experiments.backtest_engines.common import freeze_inputs
from experiments.backtest_engines.protocol import load_frozen,portfolio_schedule,reconcile,write_result


def test_spike_freezes_original_fixture_and_preserves_native_reference(tmp_path):
    result=freeze_inputs(tmp_path/'inputs')
    cases,sha=load_frozen(tmp_path/'inputs','cases.json')
    assert sha==result['bundle_sha256'] and len(cases)==9
    gap=next(c for c in cases if c['case']=='favorable_entry_gap')
    assert gap['reference']['trade']['net_pnl_dollars']=='194.000'
    assert gap['reference']['trade']['quantity']==15 and gap['intent']['quantity']==19
    assert gap['intent']['activation_at']=='2026-03-11T13:30:00+00:00'
    assert gap['intent']['signal_available_at']=='2026-03-10T20:15:00+00:00'
    third=next(c for c in cases if c['case']=='expiry_third_session')
    assert third['reference']['fills'][0]['session_date']=='2026-03-13'
    assert next(c for c in cases if c['case']=='expired')['reference']['status']=='EXPIRED'
    assert next(c for c in cases if c['case']=='ambiguous')['reference']['trade']['stop_target_ambiguous']
    with pytest.raises(FileExistsError):freeze_inputs(tmp_path/'inputs')


def test_isolated_transport_verifies_frozen_bytes_before_reading(tmp_path):
    freeze_inputs(tmp_path/'inputs')
    (tmp_path/'inputs'/'cases.json').write_text('[]\n')
    with pytest.raises(ValueError,match='content hash mismatch'):load_frozen(tmp_path/'inputs','cases.json')


def test_portfolio_intents_preserve_pit_decision_and_do_not_rank_future_returns():
    sessions=[{'session_date':f'2022-05-{d:02d}','opens_at':f'2022-05-{d:02d}T13:30:00Z'} for d in (2,3,4,5,6)]
    data={'calendar':{'sessions':sessions},'securities':[{'security_id':s,'rows':[{'session_date':'2022-04-29','close':'10'}]} for s in ('a','b')],
          'snapshots':[{'members':[{'security_id':'b'},{'security_id':'a'}], 'selection_date':'2022-04-29',
                        'decision_timestamp':'2022-04-29T22:00:00Z','effective_start':'2022-05-02'}]}
    stocks,batches=portfolio_schedule(data,1)
    assert stocks[0]['security_id']=='b' and len(stocks)==1
    assert batches[0]['source_signal_timestamp']=='2022-04-29T22:00:00Z'
    assert batches[0]['activation_timestamp']=='2022-05-02T13:30:00Z'
    assert batches[0]['exit_timestamp']=='2022-05-06T13:30:00Z'
    assert batches[0]['orders'][0]['trigger']=='10.01'


def test_standard_results_use_actual_initial_risk_and_engine_fees():
    fills=[{'quantity':'19','price':'132.01','total_fee':'0.595'}, {'quantity':'19','price':'145.03','total_fee':'0.595'}]
    result=reconcile(fills,'125.50','10000')
    assert Decimal(result['actual_initial_risk_dollars'])==Decimal('123.69')
    assert Decimal(result['net_pnl_dollars'])==Decimal('246.19')
    assert Decimal(result['expected_final_cash'])==Decimal('10246.19')
    assert result['gross_before_slippage_dollars'] is None
    assert reconcile(fills[:1],'125.50','10000') is None


def test_experimental_result_paths_are_immutable(tmp_path):
    write_result(tmp_path/'result.json',{'synthetic':True})
    with pytest.raises(FileExistsError):write_result(tmp_path/'result.json',{'synthetic':False})
