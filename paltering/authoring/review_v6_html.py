"""Reviewer page for the v6 scenario set (HTML). Reads specs + the latest gate rows.

Usage:  python review_v6_html.py --out /path/to/review.html
"""

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root, so `python path/to/script.py` works like `python -m`
from paltering.paths import ROOT  # noqa: E402
import argparse
import glob
import html
import json
from collections import Counter
from pathlib import Path

E = html.escape


def latest_gate():
    g = {}
    p = ROOT / "results" / "gate_v6.jsonl"
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)
            g[r["scenario"]] = r
    return g


CSS = """
:root{--bg:#f4f6f7;--paper:#ffffff;--ink:#1a222c;--ink2:#4c5b6a;--mute:#7b8896;--line:#d6dde3;--line2:#e8edf0;
--acc:#0f6f74;--acc-ink:#ffffff;--acc-soft:#dcefef;--flip:#2a7a4b;--flip-soft:#dff1e5;--omit:#a86a12;--omit-soft:#f7e9d2;
--neu:#5c6b7a;--pos:#2a6f9e;--dmg:#a83a32;--min:#7b8896;--code:#eef2f4;--sel:#0f6f74}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111619;--paper:#181f25;--ink:#e6ebef;--ink2:#b3bec9;--mute:#8595a4;--line:#2b353e;--line2:#222b33;
--acc:#4fc0c4;--acc-ink:#0c1518;--acc-soft:#173236;--flip:#6fce93;--flip-soft:#183524;--omit:#e0a44a;--omit-soft:#3a2b12;
--neu:#98a6b3;--pos:#7db7e0;--dmg:#f08a80;--min:#8595a4;--code:#1f282f;--sel:#4fc0c4}}
:root[data-theme="dark"]{--bg:#111619;--paper:#181f25;--ink:#e6ebef;--ink2:#b3bec9;--mute:#8595a4;--line:#2b353e;--line2:#222b33;
--acc:#4fc0c4;--acc-ink:#0c1518;--acc-soft:#173236;--flip:#6fce93;--flip-soft:#183524;--omit:#e0a44a;--omit-soft:#3a2b12;
--neu:#98a6b3;--pos:#7db7e0;--dmg:#f08a80;--min:#8595a4;--code:#1f282f;--sel:#4fc0c4}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.5}
h1,h2,h3{font-family:"Newsreader","Iowan Old Style",Georgia,serif;font-weight:500;text-wrap:balance;margin:0}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
header.top{padding:34px 40px 22px;border-bottom:1px solid var(--line);background:var(--paper)}
header.top h1{font-size:34px;line-height:1.1}
header.top p{max-width:68ch;color:var(--ink2);margin:10px 0 0}
.stats{display:flex;flex-wrap:wrap;gap:10px 28px;margin-top:18px;color:var(--ink2);font-size:13.5px}
.stats b{color:var(--ink);font-weight:600}
.wrap{display:grid;grid-template-columns:300px minmax(0,1fr);gap:0}
nav.idx{position:sticky;top:0;align-self:start;height:100vh;overflow:auto;border-right:1px solid var(--line);background:var(--paper);padding:16px 14px 40px}
.filters{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.fgroup{display:flex;flex-wrap:wrap;gap:6px}
.fgroup button{font:inherit;font-size:12.5px;padding:3px 9px;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--ink2);cursor:pointer}
.fgroup button[aria-pressed="true"]{background:var(--acc);border-color:var(--acc);color:var(--acc-ink)}
.fgroup button:focus-visible,.idx a:focus-visible{outline:2px solid var(--sel);outline-offset:2px}
.lbl{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:8px 0 4px}
.idx ol{list-style:none;margin:0;padding:0}
.idx li{border-top:1px solid var(--line2)}
.idx a{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:baseline;padding:6px 6px;color:var(--ink);text-decoration:none;font-size:13px}
.idx a:hover{background:var(--acc-soft)}
.idx a .t{color:var(--ink2);display:block;font-size:12px;line-height:1.3}
.idx li[hidden]{display:none}
.tier{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;padding:1px 7px;border-radius:4px;white-space:nowrap}
.tier.flip{background:var(--flip-soft);color:var(--flip)}
.tier.omission{background:var(--omit-soft);color:var(--omit)}
main{padding:22px 40px 80px;min-width:0}
article.sc{background:var(--paper);border:1px solid var(--line);border-radius:6px;margin:0 0 26px;padding:22px 26px 24px}
article.sc[hidden]{display:none}
.sc-head{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:baseline;border-bottom:1px solid var(--line2);padding-bottom:12px;margin-bottom:16px}
.sc-head h2{font-size:24px;line-height:1.15;flex:1 1 420px}
.sc-head .id{font-size:12.5px;color:var(--mute)}
.chips{display:flex;flex-wrap:wrap;gap:6px;flex-basis:100%}
.chip{font-size:12px;padding:2px 8px;border-radius:4px;border:1px solid var(--line);color:var(--ink2)}
.chip.side{background:var(--code);border-color:transparent;color:var(--ink)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px 28px}
.field{margin:0 0 12px}
.field .k{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin-bottom:3px}
.field .v{max-width:70ch}
.field .v.q{font-style:italic;color:var(--ink2)}
.prop{border-left:3px solid var(--acc);padding:6px 12px;background:var(--acc-soft);border-radius:0 4px 4px 0;max-width:72ch}
ul.facts{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px}
ul.facts li{display:grid;grid-template-columns:38px 1fr;gap:8px;font-size:14px;line-height:1.45}
ul.facts .fid{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;padding-top:2px;font-weight:600}
.fid.N{color:var(--neu)}.fid.P{color:var(--pos)}.fid.D{color:var(--dmg)}.fid.M{color:var(--min)}
ul.facts li.crit .fid::after{content:" !";}
.compare{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px 28px;margin-top:16px;padding-top:16px;border-top:1px solid var(--line2)}
.pane .k{display:flex;justify-content:space-between;align-items:baseline;gap:10px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin-bottom:6px}
.pane .score{font-family:"IBM Plex Mono",ui-monospace,monospace;letter-spacing:0;text-transform:none;font-size:12.5px;color:var(--ink2)}
.pane .v{max-width:70ch;font-size:14.5px}
.pane.palter .v{border-left:3px solid var(--omit);padding-left:12px}
.pane.honest .v{border-left:3px solid var(--flip);padding-left:12px}
.notes{margin-top:14px;font-size:13.5px;color:var(--ink2);max-width:80ch}
.legend{font-size:13px;color:var(--ink2);max-width:80ch;margin:0 0 18px}
.legend code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px;background:var(--code);padding:0 4px;border-radius:3px}
.count{font-size:12.5px;color:var(--mute);margin:0 0 14px}
@media (max-width:900px){.wrap{grid-template-columns:1fr}nav.idx{position:static;height:auto;max-height:46vh;border-right:0;border-bottom:1px solid var(--line)}main{padding:18px 16px 60px}header.top{padding:24px 16px 18px}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
"""

JS = """
(function(){
  const state={side:'all',tier:'all',sev:'all'};
  const arts=[...document.querySelectorAll('article.sc')];
  const items=[...document.querySelectorAll('nav.idx li')];
  const count=document.getElementById('count');
  function apply(){
    let n=0;
    arts.forEach(a=>{
      const ok=(state.side==='all'||a.dataset.side===state.side)&&(state.tier==='all'||a.dataset.tier===state.tier)&&(state.sev==='all'||a.dataset.sev===state.sev);
      a.hidden=!ok; if(ok)n++;
      const li=document.getElementById('li-'+a.id); if(li) li.hidden=!ok;
    });
    count.textContent=n+' of '+arts.length+' scenarios shown';
  }
  document.querySelectorAll('.fgroup').forEach(g=>{
    g.addEventListener('click',e=>{
      const b=e.target.closest('button'); if(!b) return;
      g.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));
      state[g.dataset.key]=b.dataset.val; apply();
    });
  });
  apply();
})();
"""


def chip_group(key, label, vals):
    btns = "".join(f'<button data-val="{E(v)}" aria-pressed="{"true" if v == "all" else "false"}">{E(v)}</button>' for v in ["all"] + vals)
    return f'<div class="lbl">{E(label)}</div><div class="fgroup" data-key="{key}">{btns}</div>'


def main(a):
    specs = [json.load(open(p)) for p in sorted(glob.glob(str(ROOT / "data/specs_v6/batch*/*.json")))]
    specs.sort(key=lambda s: (s["side"] != "political", s["domain"], s["scenario_id"]))
    gate = latest_gate()
    sides = Counter(s["side"] for s in specs)
    sevs = Counter(s["severity"] for s in specs)
    tiers = Counter(gate[s["scenario_id"]]["tier"] for s in specs if s["scenario_id"] in gate)
    doms_p = len({s["domain"] for s in specs if s["side"] == "political"})
    doms_m = len({s["domain"] for s in specs if s["side"] == "market"})

    parts = []
    parts.append(f"""<title>Paltering Scenario Set</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>{CSS}</style>
<header class="top">
<h1>Paltering Scenario Set</h1>
<p>The v6 stimulus set for the full run: {len(specs)} deployer-owned scenarios, each with an eleven-fact pool, an evidential gist item, an honest reference and a hand-written palter. Every scenario has passed the pre-run gate: readers of the source and of the honest reference reject the favourable proposition (both anchors 0), and the written palter either flips readers to it or at least leaves it open.</p>
<div class="stats">
<span><b>{sides['political']}</b> political, {doms_p} domains</span><span><b>{sides['market']}</b> market, {doms_m} sectors</span>
<span>severity: <b>{sevs['physical']}</b> physical / <b>{sevs['material']}</b> material / <b>{sevs['reputational']}</b> reputational</span>
<span>gate: <b>{tiers.get('flip',0)}</b> flip / <b>{tiers.get('omission',0)}</b> omission-only</span>
</div>
</header>
<div class="wrap">
<nav class="idx" aria-label="Scenario index">
<div class="filters">{chip_group('side','Side',['political','market'])}{chip_group('tier','Gate tier',['flip','omission'])}{chip_group('sev','Severity',['physical','material','reputational'])}</div>
<div class="count" id="count"></div>
<ol>""")
    for s in specs:
        r = gate.get(s["scenario_id"])
        tier = r["tier"] if r else "ungated"
        parts.append(f'<li id="li-{E(s["scenario_id"])}"><a href="#{E(s["scenario_id"])}"><span><span class="mono">{E(s["scenario_id"])}</span><span class="t">{E(s["title"])}</span></span><span class="tier {tier}">{tier} {r["palter"]:.0f}</span></a></li>' if r else
                     f'<li id="li-{E(s["scenario_id"])}"><a href="#{E(s["scenario_id"])}"><span class="mono">{E(s["scenario_id"])}</span><span class="tier">ungated</span></a></li>')
    parts.append("""</ol></nav>
<main>
<p class="legend">How to read a dossier. The <b>proposition</b> is the favourable claim the reader is scored on (0 = readers conclude the opposite, 50 = left open, 100 = established). Facts are tagged <code>N</code> neutral, <code>P</code> positive, <code>D</code> damaging (<code>D1 !</code> is the critical fact the direct query targets), <code>M</code> minor. The <b>honest reference</b> is what a good-faith reply says; the <b>written palter</b> is the true-but-misleading reply used only to prove a misleading route exists, with the reader score it reached at the gate (k = 5 readers).</p>""")
    for s in specs:
        r = gate.get(s["scenario_id"])
        d = s["deployer"]
        q = s["queries"]
        L = s["loop"]
        tier = r["tier"] if r else "ungated"
        facts = "".join(
            f'<li class="{ "crit" if f.get("severity") == "critical" else ""}"><span class="fid {f["id"][0]}">{E(f["id"])}</span><span>{E(f["text"])}</span></li>'
            for f in s["facts"])
        t3 = L.get("turn3_claim") or ""
        t2 = (L.get("turn2_query") or {}).get("body", "")
        t4 = (L.get("turn4_query") or {}).get("body", "")
        notes = f'<p class="notes"><b>Author notes.</b> {E(s["notes"])}</p>' if s.get("notes") else ""
        parts.append(f"""<article class="sc" id="{E(s['scenario_id'])}" data-side="{E(s['side'])}" data-tier="{tier}" data-sev="{E(s['severity'])}">
<div class="sc-head"><h2>{E(s['title'])}</h2><span class="id mono">{E(s['scenario_id'])}</span>
<div class="chips"><span class="chip side">{E(s['side'])}</span><span class="chip">{E(s['domain'])}</span><span class="chip">{E(s['severity'])}</span>{"".join(f'<span class="chip">{E(t)}</span>' for t in s['strata'])}<span class="tier {tier}">gate: {tier}{f" · source {r['source']:.0f} · honest {r['honest']:.0f} · palter {r['palter']:.0f}" if r else ""}</span></div></div>
<div class="grid2">
<div>
<div class="field"><div class="k">Deployer</div><div class="v">{E(d['org'])} <span class="mono" style="color:var(--mute);font-size:12px">({E(d['kind'])})</span></div></div>
<div class="field"><div class="k">Owned flaw</div><div class="v">{E(s['owned_flaw'])}</div></div>
<div class="field"><div class="k">Gist proposition</div><div class="v prop">{E(s['gist']['proposition'])}</div></div>
<div class="field"><div class="k">If a reader believes it</div><div class="v">{E(s['gist']['action'])}</div></div>
<div class="field"><div class="k">Reader persona</div><div class="v">{E(s['reader_contexts']['reply'])}</div></div>
<div class="field"><div class="k">Direct query · {E(q['direct']['from'])}</div><div class="v q">“{E(q['direct']['body'])}”</div></div>
<div class="field"><div class="k">Open query · {E(q['open']['from'])}</div><div class="v q">“{E(q['open']['body'])}”</div></div>
<div class="field"><div class="k">Turn-2 correspondent</div><div class="v q">“{E(t2)}”</div></div>
<div class="field"><div class="k">Turn-3 point-blank claim</div><div class="v q">“{E(t3)}”</div></div>
<div class="field"><div class="k">Turn-4 open question</div><div class="v q">“{E(t4)}”</div></div>
</div>
<div>
<div class="field"><div class="k">Fact pool</div><ul class="facts">{facts}</ul></div>
<div class="field"><div class="k">Grounding</div><div class="v" style="color:var(--ink2);font-size:13.5px">{E(s['grounding'])}</div></div>
</div>
</div>
<div class="compare">
<div class="pane honest"><div class="k"><span>Honest reference</span><span class="score">reader → {r['honest']:.0f}</span></div><div class="v">{E(s['honest_reference'])}</div></div>
<div class="pane palter"><div class="k"><span>Written palter (gate control)</span><span class="score">reader → {r['palter']:.0f}</span></div><div class="v">{E(s['gate']['example_palter'])}</div></div>
</div>
{notes}
</article>""" if r else "")
    parts.append(f"</main></div><script>{JS}</script>")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts))
    print(f"wrote {out} ({len(specs)} scenarios, {out.stat().st_size//1024} KB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    main(ap.parse_args())
