"""Offline scientific boundaries for the full-population stop study."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from test_prospective_predictions import archive,alert
from equity_research.ingestion.storage import encode,write_bundle
from equity_research.marketlife_intake import source_state
from equity_research.structural_stops import (inventory,source_inventory,annotate,chart_view,structures,pivots,
    compare,summarize,annotation_files_for,study_files,load_study,materiality)


@pytest.fixture
def inputs(archive):
    state=source_state(archive,[],'2026-10-26T23:00:00+00:00')
    decisions=inventory(state)
    market={k:archive[k] for k in ('calendar','prices','coverage')}
    market['decisions']=[{k:d[k] for k in ('decision_id','symbol','direction','cutoffs')} for d in decisions]
    source={'original_alerts':archive['alerts'],'batches':[],'calendar':archive['calendar'],
        'source_asof':'2026-10-26T23:00:00+00:00','native_archive_sha256':'synthetic'}
    return market,source,decisions


def test_inventory_deduplicates_clocks_and_preserves_atomic_underway(archive):
    a=archive['alerts']['alerts'][1]
    a['text']=a['text'].replace('Setup Changed____\nNone','Setup Changed____\nAAPL setup changed to long (underway) from long')
    archive['alerts']['alerts'].append(alert('c',2,'2026-10-20T18:00:00-04:00',stops='AAPL stop moved to 91.00 from 90.00'))
    ds=inventory(source_state(archive,[],'2026-10-26T23:00:00+00:00'))
    assert len(ds)==3 and len({d['decision_id'] for d in ds})==3
    assert ds[1]['copublished_underway'] and ds[1]['eligibility_before']=='ENTERABLE'
    assert ds[1]['atomic_assessment_eligibility']=='UNDERWAY'
    assert ds[2]['revision_role']=='MONITORED_UNDERWAY'
    assert ds[1]['previous_stop']=='95.00'


def test_stop_masking_future_poison_and_clock_deduplication(inputs):
    market,source,ds=inputs
    before=annotate(market)
    assert len(before['views'])==len(ds)==2
    assert 'published_stop' not in json.dumps(market)
    for rows in market['prices'].values():
        for r in rows:
            if r['session_date']>'2026-10-19':r.update(open='POISON',high=None,close='-1')
    assert annotate(market)==before
    changed=deepcopy(ds);changed[0]['published_stop']='1.00'
    assert compare(before,changed)['matrix']!=compare(before,ds)['matrix']
    assert annotate(market)==before


def test_missing_sessions_and_short_history_are_not_filled(inputs):
    market,_,_=inputs;cutoff='2026-10-19T22:19:00+00:00'
    first=chart_view(market,'AAPL','LONG',cutoff)
    assert first['status']=='AVAILABLE'
    market['prices']['AAPL']=[r for r in market['prices']['AAPL'] if r['session_date']!='2026-10-16']
    bad=chart_view(market,'AAPL','LONG',cutoff)
    assert bad['status']=='UNAVAILABLE_MISSING_REQUIRED_SESSION'
    assert bad['missing_sessions']==['2026-10-16'] and bad['candidates']==[]
    market['prices']['AAPL']=first['rows'][-25:]
    short=chart_view(market,'AAPL','LONG',cutoff)
    assert short['status']=='AVAILABLE_SHORT_HISTORY' and len(short['rows'])==25
    assert short['features']['atr14']['value']==first['features']['atr14']['value']
    assert chart_view(market,'ABSENT','SHORT',cutoff)['status']=='UNAVAILABLE_NO_MARKET_EVIDENCE'


def test_pivot_requires_three_completed_right_bars_and_is_stop_free():
    rows=[{'session_date':f'2026-01-{i+1:02d}','open':str(v),'close':str(v),
           'high':str(v+1),'low':str(v-1)} for i,v in enumerate([10,11,12,9,11,12,13,14])]
    assert not [p for p in pivots(rows[:6]) if p['session']=='2026-01-04']
    p=next(p for p in pivots(rows[:7]) if p['session']=='2026-01-04')
    assert p['confirmed_session']=='2026-01-07'
    assert structures(rows[:7],'LONG')['candidates'][0]['level']=='8'
    assert structures(rows[:7],'LONG')['candidates'][-1]['level'] is None


@pytest.mark.parametrize('direction,stop,level,expected',[('LONG','9.90','10','0.10'),('SHORT','10.10','10','0.10'),('LONG','10.10','10','-0.10')])
def test_signed_residuals_and_unidentified_volatility(direction,stop,level,expected,inputs):
    market,_,ds=inputs;ann=annotate(market);view=ann['views'][0]
    ds[0].update(direction=direction,published_stop=stop)
    view['candidates']=[{'family':'H1','level':level,'anchor_session':'2026-10-01','reason':'test'},
                        {'family':'H5','level':None,'anchor_session':None,'reason':'unidentified'}]
    result=compare({'views':[view]},ds[:1])
    r=result['matrix'][0]
    assert r['buffer_price']==expected
    assert float(r['buffer_research_ticks'])==float(expected)*100
    assert r['buffer_ATR']==float(expected)/r['atr14']
    assert result['matrix'][1]['buffer_ATR'] is None


def test_semantic_replay_rejects_resealed_annotations_and_outputs(tmp_path,inputs):
    market,source,_=inputs
    af=annotation_files_for(market);ah=write_bundle(tmp_path/'annotations',af)
    files=study_files(af,ah,encode(source));h=write_bundle(tmp_path/'study',files)
    assert load_study(tmp_path/'study')==(files,h)
    assert write_bundle(tmp_path/'replay',load_study(tmp_path/'study')[0])==h
    with pytest.raises(FileExistsError):write_bundle(tmp_path/'study',files)
    bad=deepcopy(files);r=json.loads(bad['study.json']);r['inventory'][0]['published_stop']='0.01';bad['study.json']=encode(r)
    write_bundle(tmp_path/'resealed',bad)
    with pytest.raises(ValueError,match='semantic replay mismatch'):load_study(tmp_path/'resealed')
    a=json.loads(af['annotations.json']);a['views'][0]['candidates'][0]['level']='0.01';af['annotations.json']=encode(a)
    bh=write_bundle(tmp_path/'changed-annotations',af)
    with pytest.raises(ValueError,match='annotation semantic mismatch'):study_files(af,bh,encode(source))


def test_source_and_market_clocks_must_agree_even_when_resealed(tmp_path,inputs):
    market,source,_=inputs;market['decisions'][0]['cutoffs']['LATE']='2026-10-25T23:00:00+00:00'
    af=annotation_files_for(market);ah=write_bundle(tmp_path/'annotations',af)
    with pytest.raises(ValueError,match='identities/clocks'):study_files(af,ah,encode(source))


def test_summary_counts_decisions_not_scenarios_and_retains_unknown(inputs):
    market,source,ds=inputs
    result=compare(annotate(market),source_inventory(source));summary=summarize(result)
    assert summary['distinct_decisions']==2 and summary['initial_stops']==summary['revisions']==1
    assert all(v['decisions']==2 for v in summary['clocks'].values())
    assert summary['clocks']['LATE']['families']['H5']['verdicts']=={'UNKNOWN':2}
    assert all(d['expert_setup_family']==d['observed_execution']=='UNKNOWN' for d in result['inventory'])


def test_unknown_publication_remains_unknown_with_conditional_views(archive):
    a=archive['alerts']['alerts'][1];a.update(published_at=None,email_received_at='2026-10-25T12:57:45+00:00',original_publication_display='Yesterday at 8:57 AM')
    ds=inventory(source_state(archive,[],'2026-10-26T23:00:00+00:00'))
    assert ds[1]['publication']['published_at'] is None
    assert len(set(ds[1]['cutoffs'].values()))>1


def test_volume_revision_does_not_change_price_structure_and_atr(tmp_path,inputs):
    market,source,_=inputs;af=annotation_files_for(market);ah=write_bundle(tmp_path/'annotations',af)
    files=study_files(af,ah,encode(source));old=market['prices']['AAPL'][-8];fresh={**old,'volume':'12345'}
    rows=[{'symbol':'AAPL','session':old['session_date'],'retained':old,'fresh':fresh,'changed_fields':['volume']}]
    result=json.loads(materiality(files,encode(rows))['materiality.json'])
    assert result['changed_comparisons']==[] and old['volume']=='100'


def test_svg_rendering_is_deterministic_and_masked(tmp_path,inputs):
    pytest.importorskip('matplotlib')
    from equity_research.structural_stop_charts import charts
    market,source,_=inputs;af=annotation_files_for(market);ah=write_bundle(tmp_path/'annotations',af)
    files=study_files(af,ah,encode(source));h=write_bundle(tmp_path/'study',files)
    selection={'view_ids':['v000']}
    first=charts(files,h,selection=selection)
    assert first==charts(files,h,selection=selection)
    masked=charts(files,h,selection=selection,masked=True)['v000-AAPL-masked.svg']
    assert b'STOP MASKED' in masked and b'published stop 95.00' not in masked
    assert b'published stop 95.00' in first['v000-AAPL.svg']


def test_committed_full_population_retains_every_source_stop_and_all_families():
    from equity_research.ingestion.storage import read_bundle
    import csv,io
    root=Path(__file__).resolve().parents[1]
    files,_=read_bundle(root/'docs/evidence/pr9e-structural-stops-v1')
    expected=source_inventory(json.loads(files['source.json']))
    inventory_rows=list(csv.DictReader(io.StringIO(files['inventory.csv'].decode())))
    matrix=list(csv.DictReader(io.StringIO(files['matrix.csv'].decode())))
    summary=json.loads(files['summary.json'])
    assert len(inventory_rows)==len(expected)==77
    assert len({d['setup_id'] for d in expected})==34
    assert sum(d['decision_type']=='INITIAL' for d in expected)==34
    assert sum(d['revision_role']=='MONITORED_UNDERWAY' for d in expected)==6
    assert sum(d['copublished_underway'] for d in expected)==14
    assert [(r['decision_id'],r['published_stop'],r['previous_stop']) for r in inventory_rows]==[
        (d['decision_id'],d['published_stop'],d['previous_stop'] or '') for d in expected]
    assert len(matrix)==565 and len({r['view_id'] for r in matrix})==113
    for decision in expected:
        rows=[r for r in matrix if r['decision_id']==decision['decision_id']]
        for clock in ('EARLY','CLOSE_BOUNDARY','LATE'):
            selected=[r for r in rows if clock in json.loads(r['scenarios'])]
            assert {r['family'] for r in selected}=={'H1','H2','H3','H4','H5'} and len(selected)==5
            for r in selected:
                if r['level']:
                    sign=1 if decision['direction']=='LONG' else -1
                    assert Decimal(r['buffer_price'])==sign*(Decimal(r['level'])-Decimal(decision['published_stop']))
    assert all(c['decisions']==77 for c in summary['clocks'].values())
    # The unavailable episodes are evidence, not silent omissions.
    assert {'PLTR','MRNA','DECK'}<={r['symbol'] for r in matrix if r['data_status']=='UNAVAILABLE_NO_MARKET_EVIDENCE'}
