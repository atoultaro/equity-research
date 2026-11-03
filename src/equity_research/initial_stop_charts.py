"""PR9F annotated daily charts, with stop-masked displays and compression boxes."""
from io import BytesIO
import json
from pathlib import Path

from .ingestion.storage import digest, encode
from .initial_stops import FAMILIES

COLORS = dict(zip(FAMILIES, ('#713ca6', '#007b92', '#9e7100', '#22622d', '#c04b00', '#555555')))


def charts(files, hashes, *, masked=False, selection=None):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D
    from matplotlib import rc_context
    study = json.loads(files['study.json']); annotations = json.loads(files['annotations.json'])
    decisions = {d['decision_id']: d for d in study['inventory']}
    known = {v['view_id'] for v in annotations['views']}
    selected = set(selection['view_ids']) if selection else known
    if selected - known: raise ValueError('unknown initial chart selection')
    output = {}; registry = []
    with rc_context({'svg.hashsalt': 'pr9f-v1', 'svg.fonttype': 'none', 'font.family': 'DejaVu Sans', 'font.size': 9}):
        for view in annotations['views']:
            if view['view_id'] not in selected: continue
            d = decisions[view['decision_id']]; days = view['chart_sessions']
            prices = {r['session_date']: r for r in view['rows']}
            fig, axes = plt.subplots(2, 1, figsize=(14, 10.5))
            fig.subplots_adjust(left=.065, right=.97, top=.89, bottom=.34, hspace=.36)
            for ax, window in zip(axes, (days, days[-20:])):
                for i, day in enumerate(window):
                    row = prices.get(day)
                    if not row:
                        ax.axvspan(i - .5, i + .5, color='#eee', zorder=0); continue
                    o, h, l, c = (float(row[k]) for k in ('open', 'high', 'low', 'close'))
                    color = '#17734a' if c >= o else '#a83238'
                    ax.vlines(i, l, h, color=color, lw=.8)
                    ax.add_patch(Rectangle((i - .3, min(o, c)), .6, max(abs(c - o), .001),
                        facecolor=color, edgecolor=color, lw=.6))
                for candidate in view['candidates']:
                    if candidate['family'] == 'COMPRESSION' and candidate['level'] is not None:
                        common = [t for t in candidate['interval_sessions'] if t in window]
                        if common:
                            x = window.index(common[0]); width = len(common)
                            low, high = float(candidate['box_low']), float(candidate['box_high'])
                            ax.add_patch(Rectangle((x - .45, low), width - .1, high - low,
                                facecolor=COLORS['COMPRESSION'], edgecolor=COLORS['COMPRESSION'],
                                alpha=.12 if candidate['primary'] else .05, lw=1))
                    if candidate['primary'] and candidate['level'] is not None:
                        ax.axhline(float(candidate['level']), color=COLORS[candidate['family']],
                            ls=':' if candidate['family'] == 'RANGE' else '-.', lw=.9, alpha=.8)
                for p in view['pivots']:
                    if p['session'] in window:
                        ax.scatter(window.index(p['session']), float(p['level']), marker='v' if p['kind'] == 'HIGH' else '^',
                            s=20, facecolors='none', edgecolors=COLORS['SWING'], zorder=5)
                for signal in view['signals']:
                    if signal['session'] in window:
                        ax.scatter(window.index(signal['session']), float(signal['level']), marker='s', s=15,
                            facecolors='none', edgecolors=COLORS['SIGNAL_BAR'], zorder=5)
                observed = [prices[t] for t in window if t in prices]
                if observed:
                    lo = min(float(r['low']) for r in observed); hi = max(float(r['high']) for r in observed)
                    if not masked: lo = min(lo, float(d['published_stop'])); hi = max(hi, float(d['published_stop']))
                    span = max(hi - lo, .1); ax.set_ylim(lo - span * .08, hi + span * .1)
                else:
                    ax.set_ylim(0, 1); ax.set_yticks([])
                    ax.text(.5, .5, 'NO ARCHIVED PRE-ALERT PRICE EVIDENCE', ha='center', transform=ax.transAxes)
                if observed and not view['status'].startswith('AVAILABLE'):
                    ax.text(.015, .94, 'INCOMPLETE AT CUTOFF: older bars do not reconstruct this setup',
                        transform=ax.transAxes, color='#a83238', va='top', fontsize=8)
                if not masked: ax.axhline(float(d['published_stop']), color='#bd1527', ls='--', lw=1.4)
                ticks = sorted(set(range(0, len(window), max(1, len(window) // 7))) | {len(window) - 1})
                if window: ax.set_xticks(ticks, [window[i][5:] for i in ticks]); ax.set_xlim(-.7, len(window) - .3)
                ax.grid(axis='y', alpha=.18); ax.set_ylabel('Native price units')
                ax.set_title(f'{len(window)} scheduled sessions; grey = unavailable; orange boxes = all qualifying contractions', loc='left', fontsize=9)
            headline = 'STOP MASKED' if masked else f"initial stop {d['published_stop']}"
            fig.suptitle(f"{d['symbol']} {d['direction']} | INITIAL ONLY | {headline}\n"
                f"{d['decision_id']} | {', '.join(view['scenarios'])} | latest eligible {view['expected_session']}", fontsize=12, y=.975)
            handles = [Line2D([0], [0], color=COLORS[f], ls='-.', label=f) for f in FAMILIES[:-1]]
            axes[0].legend(handles=handles, loc='upper left', ncol=5, fontsize=8)
            rows = [r for r in study['matrix'] if r['view_id'] == view['view_id'] and r['primary']]
            footer = [f"Source: {d['publication_display']} | exact publication: {d['observed_publication']} | reported TYPE: {d['marketlife_type']}",
                f"Evidence: {view['status']}; {view['available_bars']} observed bars. Candidates selected before stop comparison; expert rationale UNKNOWN.",
                'Triangles = confirmed 3-left/3-right pivots; squares = closing 20-bar signals. Primary contraction chosen by recency, never stop fit.']
            for row in rows:
                residual = '' if masked else (f" | outward buffer {row['buffer_price']} / ATR14 {row['buffer_ATR14']:.3f}"
                    if row['buffer_ATR14'] is not None else ' | residual UNKNOWN')
                footer.append(f"{row['family']}: {row['level'] or 'UNKNOWN'} @ {row['anchor_session'] or 'UNKNOWN'}{residual}")
            compression = next(r for r in rows if r['family'] == 'COMPRESSION')
            if compression['level'] is not None:
                footer.extend([f"Primary compression {compression['interval_start']} to {compression['interval_end']}: ranges {', '.join(compression['daily_ranges'])}.",
                    f"Shared price region: {compression['common_price_overlap']}; subsequent boundary breaches: {compression['anchor_breaches_after_confirmation'] or 'none'}."])
            context = []
            for symbol, f in view['market_context'].items():
                r = f.get('return20'); context.append(f'{symbol} 20-session price return {r:.2%}' if r is not None else f'{symbol} context unavailable')
            footer.extend(['; '.join(context), 'Conditional native split-adjusted prices. ATR normalizes level residuals only. No entry, risk evaluation or later-stop analysis.'])
            fig.text(.065, .285, '\n'.join(footer), va='top', fontsize=8, linespacing=1.5)
            svg = BytesIO(); fig.savefig(svg, format='svg', metadata={'Date': None, 'Creator': 'equity-research PR9F'})
            name = f"{view['view_id']}-{d['symbol']}{'-masked' if masked else ''}"
            output[name + '.svg'] = ('\n'.join(line.rstrip() for line in svg.getvalue().decode().splitlines()) + '\n').encode()
            png = BytesIO(); fig.savefig(png, format='png', dpi=120, metadata={'Software': 'equity-research PR9F'})
            output[name + '.png'] = png.getvalue(); plt.close(fig)
            registry.append({'view_id': view['view_id'], 'decision_id': d['decision_id'],
                'svg': name + '.svg', 'svg_sha256': digest(output[name + '.svg']),
                'png': name + '.png', 'png_sha256': digest(output[name + '.png'])})
    output['chart-manifest.json'] = encode({'schema_version': 'initial_stop_charts_v1',
        'study_sha256': hashes['bundle_sha256'], 'masked': masked, 'selection': selection,
        'renderer': {'matplotlib': matplotlib.__version__, 'source_sha256': digest(Path(__file__).read_bytes()),
            'svg_trailing_whitespace_normalized': True}, 'charts': registry})
    return output
