"""Deterministic scientific SVGs for PR9E; matplotlib is a render-only dependency."""
from io import BytesIO
import json

from .ingestion.storage import digest,encode


COLORS={'H1':'#6f42a0','H2':'#007c91','H3':'#9b6b00','H4':'#166534'}


def charts(files,hashes,*,masked=False,selection=None):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib import rc_context
    study=json.loads(files['study.json']);ann=json.loads(files['annotations.json'])
    decisions={d['decision_id']:d for d in study['inventory']}
    selected=set(selection['view_ids']) if selection else {v['view_id'] for v in ann['views']}
    known={v['view_id'] for v in ann['views']}
    if selected-known:raise ValueError('unknown selected chart view')
    outputs={};registry=[]
    with rc_context({'svg.hashsalt':'pr9e-v1','svg.fonttype':'none','font.family':'DejaVu Sans','font.size':9}):
        for view in ann['views']:
            if view['view_id'] not in selected:continue
            d=decisions[view['decision_id']];days=view['chart_sessions'];by_day={r['session_date']:r for r in view['rows']}
            fig,axes=plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[1.25,1]})
            fig.subplots_adjust(left=.065,right=.97,top=.89,bottom=.29,hspace=.35)
            for ax,window in zip(axes,(days,days[-20:])):
                for x,day in enumerate(window):
                    row=by_day.get(day)
                    if not row:
                        ax.axvspan(x-.5,x+.5,color='#eee',zorder=0);continue
                    o,h,l,c=(float(row[k]) for k in ('open','high','low','close'))
                    color='#17734a' if c>=o else '#a83238'
                    ax.vlines(x,l,h,color=color,lw=.8)
                    ax.add_patch(Rectangle((x-.3,min(o,c)),.6,max(abs(c-o),.001),facecolor=color,edgecolor=color,lw=.6))
                observed=[by_day[t] for t in window if t in by_day]
                if observed:
                    lo=min(float(r['low']) for r in observed);hi=max(float(r['high']) for r in observed)
                    if not masked:lo=min(lo,float(d['published_stop']));hi=max(hi,float(d['published_stop']))
                    span=max(hi-lo,.1);ax.set_ylim(lo-span*.08,hi+span*.10)
                for p in view['pivots']:
                    if p['session'] in window:
                        ax.scatter(window.index(p['session']),float(p['level']),marker='v' if p['kind']=='HIGH' else '^',s=22,
                            facecolors='none',edgecolors='#6f42a0',zorder=5)
                for signal in view['signals']:
                    if signal['session'] in window:
                        ax.scatter(window.index(signal['session']),float(signal['level']),marker='s',s=17,facecolors='none',edgecolors='#166534',zorder=5)
                for c in view['candidates']:
                    if c['level'] is not None:
                        ax.axhline(float(c['level']),color=COLORS[c['family']],alpha=.7,lw=.85,ls=':' if c['family']=='H3' else '-.')
                        if c['family']=='H3':
                            ax.axvspan(max(-.5,len(window)-10.5),len(window)-.5,color='#9b6b00',alpha=.045)
                if not masked:ax.axhline(float(d['published_stop']),color='#ba1424',lw=1.35,ls='--')
                ticks=list(range(0,len(window),max(1,len(window)//7)))
                if window:ax.set_xticks(ticks,[window[i][5:] for i in ticks]);ax.set_xlim(-.7,len(window)-.3)
                ax.grid(axis='y',alpha=.18);ax.set_ylabel('Native price units')
                ax.set_title(f'{len(window)} scheduled sessions; grey = unavailable observation',loc='left',fontsize=9)
            stop_text='STOP MASKED' if masked else f"published stop {d['published_stop']}"
            fig.suptitle(f"{d['symbol']} {d['direction']} | {d['decision_type']} | {stop_text}\n"
                f"{d['decision_id']} | {', '.join(view['scenarios'])} | latest eligible {view['expected_session']}",fontsize=12,y=.975)
            rows=[r for r in study['matrix'] if r['view_id']==view['view_id']]
            footer=[f"Source display: {d['publication_display']} | exact publication: {d['observed_publication']}",
                f"Data: {view['status']} ({view['available_bars']} bars). Eligibility before / atomic: {d['eligibility_before']} / {d['atomic_assessment_eligibility']}.",
                'Triangles: strict 3-left/3-right confirmed swings. Squares: closing 20-bar breakouts/breakdowns. H3 box is only a fixed range proxy.']
            for r in rows:
                buffer='' if masked else f" | signed buffer {r['buffer_price']} / ATR {r['buffer_ATR']:.3f}" if r['buffer_ATR'] is not None else ' | residual UNKNOWN'
                footer.append(f"{r['family']}: {r['level'] if r['level'] is not None else 'UNKNOWN'} @ {r['anchor_session'] or 'UNKNOWN'}{buffer}")
            context=[]
            for s,f in view['market_context'].items():
                v=f.get('return20');context.append(f"{s} 20-session price return {v:.2%}" if v is not None else f'{s} context unavailable')
            footer.extend(['; '.join(context),'Conditional native split-adjusted daily prices; actual fills and expert rationale UNKNOWN. No bars after the assumed decision cutoff.'])
            fig.text(.065,.235,'\n'.join(footer),va='top',fontsize=8,linespacing=1.4)
            stream=BytesIO();fig.savefig(stream,format='svg',metadata={'Date':None,'Creator':'equity-research PR9E'});plt.close(fig)
            name=f"{view['view_id']}-{d['symbol']}{'-masked' if masked else ''}.svg";outputs[name]=stream.getvalue()
            preview=BytesIO();fig.savefig(preview,format='png',dpi=120,metadata={'Software':'equity-research PR9E'})
            png=name.replace('.svg','.png');outputs[png]=preview.getvalue()
            registry.append({'filename':name,'view_id':view['view_id'],'decision_id':d['decision_id'],'sha256':digest(outputs[name])})
    outputs['chart-manifest.json']=encode({'schema_version':'structural_charts_v1','study_sha256':hashes['bundle_sha256'],
        'masked':masked,'renderer':{'matplotlib':matplotlib.__version__,'sha256':digest(__import__('pathlib').Path(__file__).read_bytes())},
        'selection':selection,'charts':registry})
    return outputs


def public_evidence(files,hashes,inputs,input_hashes):
    """Compact review packet; native market rows remain in the existing local archive."""
    if any(inputs[k]!=files[k] for k in ('market.json','source.json')):raise ValueError('export and study disagree')
    annotation=json.loads(files['annotations.json'])
    annotation['views']=[{**{k:v for k,v in row.items() if k!='rows'},'rows_sha256':digest(encode(row['rows']))}
                         for row in annotation['views']]
    names=('inventory.csv','matrix.csv','revision-comparisons.csv','summary.json','source.json')
    return {**{k:files[k] for k in names},'annotations-without-bars.json':encode(annotation),
        'protocol.json':inputs['protocol.json'],'provenance.json':inputs['provenance.json'],
        'lineage.json':encode({'schema_version':'structural_public_evidence_v1','study':hashes,'inputs':input_hashes,
            'market_rows_committed':False,'reproduction_requires_existing_local_native_archive':True})}
