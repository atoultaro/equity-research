"""Audit observed native results; never create or repair fills."""

from decimal import Decimal
from statistics import mean

from .protocol import dt,encode,sha


def cost_audit(case, result, engine, mode):
    fills=result.get('fills',[])
    quantities=[Decimal(f['quantity']) for f in fills]
    net_quantity=sum((q if f['side']=='BUY' else -q for q,f in zip(quantities,fills)),Decimal(0))
    status=('INVALID_LONG_BRACKET_OVERCLOSE' if net_quantity<0 else 'CLOSED' if len(fills)==2 and net_quantity==0
            else 'OPEN_POSITION' if net_quantity>0 else 'NO_FILL')
    audit={'status':status,'net_quantity':str(net_quantity),'native_final_cash':result.get('final_cash'),
        'native_final_equity':result.get('final_equity'),'native_unsettled_cash':result.get('unsettled_cash'),
        'fills':fills,'commission_dollars':None,'fixed_fees_dollars':None,'fee_rounding_residual_dollars':None,
        'gross_before_slippage_dollars':None,'modeled_slippage_dollars':None,'net_pnl_dollars':None,'net_realized_r':None}
    if mode=='common':
        commission=sum(quantities)*Decimal('0.005');fees=Decimal('0.50')*len(fills)
        actual=sum((Decimal(f['total_fee']) for f in fills),Decimal(0))
        audit.update(commission_dollars=str(commission),fixed_fees_dollars=str(fees),fee_rounding_residual_dollars=str(actual-commission-fees))
    if status!='CLOSED':return audit
    a,b=fills;qty=quantities[0]
    entry,exit_=Decimal(a['price']),Decimal(b['price']);stop=Decimal(case['intent']['stop'])
    risk=(entry-stop)*qty
    total_fee=sum(Decimal(f['total_fee']) for f in fills)
    pnl=(exit_-entry)*qty-total_fee
    audit.update(actual_initial_risk_dollars=str(risk),net_pnl_dollars=str(pnl),net_realized_r=str(pnl/risk) if risk>0 else None,
                 expected_closed_equity=str(Decimal(case['intent']['initial_cash'])+pnl),total_fee_dollars=str(total_fee))
    audit['native_equity_reconciles']=Decimal(result['final_equity'])==Decimal(audit['expected_closed_equity'])
    # Infer the pre-cost reference from the *pinned native model*, not PR4's
    # fill policy: NT limit fills are at limit, LEAN can improve to a gap Open.
    day=dt(a['at']).date().isoformat()
    row=next(r for r in case['rows'] if r['session_date']==day)
    entry_ref=max(Decimal(row['open']),Decimal(case['intent']['trigger']))
    tag=b.get('tag',b.get('order_id','')).upper()
    exitrow=next(r for r in case['rows'] if r['session_date']==dt(b['at']).date().isoformat())
    if tag=='TARGET':
        target=(entry+2*(entry-stop)).quantize(Decimal('0.01'),rounding='ROUND_CEILING')
        exit_ref=target if engine=='nautilus' else max(target,Decimal(exitrow['open']))
    elif tag=='STOP':exit_ref=min(stop,Decimal(exitrow['open']))
    else:return audit
    gross=(exit_ref-entry_ref)*qty
    slippage=((entry-entry_ref)+(exit_ref-exit_))*qty
    audit.update(gross_before_slippage_dollars=str(gross),modeled_slippage_dollars=str(slippage),
        gross_reference_method='RECONSTRUCTED_FROM_FROZEN_BAR_AND_PINNED_NATIVE_ORDER_MODEL; not an engine-reported field',
        gross_to_net_reconciles=gross-slippage-total_fee==pnl)
    return audit


def repeat_projection(result):
    """Economic/event content excluding measured resource/time counters."""
    return {k:result.get(k) for k in ('active_members','distinct_security_ids','expected_bars','bars_seen','final_cash','final_equity',
        'open_positions','unsettled_cash','fills','actions','rejected','identity_map')}


def repeat_summary(first,second):
    a,b=repeat_projection(first),repeat_projection(second)
    ordered_a,ordered_b=sha(encode(a)),sha(encode(b))
    for value in (a,b):
        value['fills']=sorted(value.get('fills') or [],key=lambda f:(f['at'],f['instrument_id'],f['side'],f['price'],f['quantity']))
    return {'ordered_content_equal':ordered_a==ordered_b,'ordered_sha256':[ordered_a,ordered_b],
            'economic_content_equal':encode(a)==encode(b),'economic_sha256':[sha(encode(a)),sha(encode(b))],
            'normalization':'Economic comparison sorts ties by instrument/side/price/quantity; ordered comparison retains native fill order'}


def weighted_scores():
    # These ratings describe the demonstrated implementations on this Mac.
    # They are not rankings of theoretical engine capability or 3,000-stock scale.
    rows=[('backtesting_correctness','0.30',2,3),('pit_universe_data_integration','0.25',3,2),
          ('bounded_multistock_scalability','0.20',3,4),('python_strategy_development','0.15',2,4),
          ('local_operations_maintenance_cost','0.10',1,4)]
    return {'dimensions':[{'category':name,'weight':weight,'lean':lean,'nautilus':nt} for name,weight,lean,nt in rows],
            'weighted':{engine:str(sum(Decimal(w)*Decimal(l if engine=='lean' else n) for _,w,l,n in rows)) for engine in ('lean','nautilus')},
            'not_verified':['3000-stock capacity','20-year or five-million-bar scale','real-provider completeness',
                'Linux/Docker execution','IBKR integration','native bitemporal vintage replay','end-to-end live ticker reuse/exchange-transfer trading'],
            'readiness':'Neither demonstrated prototype passes all required equity correctness/admission gates; retain PR4 temporarily'}
