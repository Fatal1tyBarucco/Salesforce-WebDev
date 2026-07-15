"""Interactive web dashboard for release exploration.

Generates a static HTML dashboard with JavaScript for:
- Feature search across all releases
- Category filter and drill-down
- Side-by-side release comparison
- Confidence heatmap visualization
- Export filtered results as CSV/JSON

No external dependencies — pure stdlib + inline JS.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR

DASHBOARD_DIR = "analytics"


def _load_all_metas() -> list[dict[str, Any]]:
    """Load all .meta.json files sorted by release_id."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return []
    metas = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                metas.append(meta)
            except json.JSONDecodeError, OSError:
                continue

    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


def _load_features(slug: str) -> list[dict[str, str]]:
    """Load features from all .md files in a release."""
    releases_dir = Path(RELEASES_DIR) / slug
    if not releases_dir.exists():
        return []

    features: list[dict[str, str]] = []
    for md_file in releases_dir.glob("*.md"):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        category = ""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                category = line[3:].strip()
                continue
            if not line or line.startswith("#") or line.startswith("|"):
                continue

            bullet_match = re.match(r"^\*\s+\*\*(.+?)\*\*\s*(?:—\s*_(.+)_)?$", line)
            if bullet_match:
                features.append(
                    {
                        "name": bullet_match.group(1).strip(),
                        "category": category,
                        "availability": (bullet_match.group(2) or "").strip(),
                        "release": slug,
                    }
                )
                continue
            if "\t" in line:
                parts = line.split("\t")
                name = parts[0].strip()
                if name and len(name) > 3:
                    features.append(
                        {
                            "name": name,
                            "category": category,
                            "availability": "",
                            "release": slug,
                        }
                    )
                continue
            if len(line) > 10:
                features.append(
                    {
                        "name": line,
                        "category": category,
                        "availability": "",
                        "release": slug,
                    }
                )

    return features


def _build_dashboard_data() -> dict[str, Any]:
    """Build all data needed for the dashboard."""
    metas = _load_all_metas()
    releases: list[dict[str, Any]] = []
    all_features: list[dict[str, str]] = []

    for meta in metas:
        slug = meta.get("slug", "")
        releases.append(
            {
                "name": meta.get("name", slug),
                "slug": slug,
                "release_id": meta.get("release_id", 0),
                "total_features": meta.get("total_features", 0),
                "avg_confidence": meta.get("avg_confidence", 0),
                "categories": meta.get("categories", []),
            }
        )
        features = _load_features(slug)
        all_features.extend(features)

    return {
        "releases": releases,
        "features": all_features,
        "total_releases": len(releases),
        "total_features": len(all_features),
    }


def generate_dashboard_html(data: dict[str, Any]) -> str:
    """Generate interactive HTML dashboard."""
    data_json = json.dumps(data, ensure_ascii=True)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Salesforce Release Notes — Dashboard Interativo</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#1e293b;padding:20px}}
.container{{max-width:1100px;margin:0 auto}}
h1{{font-size:24px;margin-bottom:4px}}
.subtitle{{color:#64748b;font-size:13px;margin-bottom:20px}}
.tabs{{display:flex;gap:4px;margin-bottom:16px}}
.tab{{padding:8px 16px;border:none;background:#e2e8f0;border-radius:8px;cursor:pointer;font-size:13px}}
.tab.active{{background:#2563eb;color:#fff}}
.panel{{display:none}}.panel.active{{display:block}}
.search-box{{width:100%;padding:10px 14px;border:1px solid #d1d5db;border-radius:8px;font-size:14px;margin-bottom:12px}}
.filters{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}
select{{padding:6px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:13px}}
.card{{background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid #e2e8f0}}
th{{background:#f1f5f9;font-weight:600;color:#475569;position:sticky;top:0}}
tr:hover{{background:#f8fafc}}
.heatmap{{display:grid;grid-template-columns:repeat(auto-fill,minmax(40px,1fr));gap:4px;margin:12px 0}}
.heat-cell{{aspect-ratio:1;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff;font-weight:600;cursor:pointer;position:relative}}
.heat-cell:hover::after{{content:attr(data-tip);position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:#1e293b;color:#fff;padding:4px 8px;border-radius:4px;font-size:11px;white-space:nowrap;z-index:10}}
.btn{{padding:6px 14px;border:none;border-radius:6px;cursor:pointer;font-size:12px}}
.btn-primary{{background:#2563eb;color:#fff}}
.btn-primary:hover{{background:#1d4ed8}}
.stats{{display:flex;gap:16px;margin-bottom:16px}}
.stat{{text-align:center}}.stat .num{{font-size:24px;font-weight:700;color:#2563eb}}.stat .lbl{{font-size:11px;color:#64748b}}
#results-count{{font-size:12px;color:#64748b;margin-bottom:8px}}
</style>
</head>
<body>
<div class="container">
<h1>Salesforce Release Notes — Dashboard</h1>
<p class="subtitle">Exploração interativa de releases</p>

<div class="stats" id="stats-bar"></div>

<div class="tabs">
  <button class="tab active" onclick="showTab('search')">🔍 Busca</button>
  <button class="tab" onclick="showTab('compare')">📊 Comparar</button>
  <button class="tab" onclick="showTab('heatmap')">🗺️ Heatmap</button>
</div>

<div id="tab-search" class="panel active">
  <input type="text" class="search-box" id="search-input" placeholder="Buscar feature..." oninput="filterFeatures()">
  <div class="filters">
    <select id="filter-release" onchange="filterFeatures()"><option value="">Todas as releases</option></select>
    <select id="filter-category" onchange="filterFeatures()"><option value="">Todas as categorias</option></select>
  </div>
  <div id="results-count"></div>
  <div class="card" style="max-height:500px;overflow-y:auto">
    <table><thead><tr><th>Feature</th><th>Categoria</th><th>Release</th><th>Disponibilidade</th></tr></thead>
    <tbody id="features-body"></tbody></table>
  </div>
  <button class="btn btn-primary" onclick="exportCSV()" style="margin-top:8px">📥 Exportar CSV</button>
  <button class="btn btn-primary" onclick="exportJSON()" style="margin-top:8px">📥 Exportar JSON</button>
</div>

<div id="tab-compare" class="panel">
  <div class="filters">
    <select id="compare-a" onchange="compareReleases()"><option value="">Release A</option></select>
    <select id="compare-b" onchange="compareReleases()"><option value="">Release B</option></select>
  </div>
  <div class="card">
    <table><thead><tr><th>Categoria</th><th id="col-a">—</th><th id="col-b">—</th><th>Delta</th></tr></thead>
    <tbody id="compare-body"></tbody></table>
  </div>
</div>

<div id="tab-heatmap" class="panel">
  <p style="font-size:13px;color:#64748b;margin-bottom:8px">Confiança média por categoria (verde = alta, vermelho = baixa)</p>
  <select id="heatmap-release" onchange="renderHeatmap()" style="margin-bottom:12px"><option value="">Selecione uma release</option></select>
  <div class="heatmap" id="heatmap-grid"></div>
</div>

</div>
<script>
const DATA = {data_json};
let filteredFeatures = [];

function init() {{
  document.getElementById('stats-bar').innerHTML =
    '<div class="stat"><div class="num">' + DATA.total_releases + '</div><div class="lbl">Releases</div></div>' +
    '<div class="stat"><div class="num">' + DATA.total_features.toLocaleString() + '</div><div class="lbl">Features</div></div>';
  const relSel = document.getElementById('filter-release');
  const cmpA = document.getElementById('compare-a');
  const cmpB = document.getElementById('compare-b');
  const hmSel = document.getElementById('heatmap-release');
  DATA.releases.forEach(r => {{
    relSel.innerHTML += '<option value="'+r.slug+'">'+r.name+'</option>';
    cmpA.innerHTML += '<option value="'+r.slug+'">'+r.name+'</option>';
    cmpB.innerHTML += '<option value="'+r.slug+'">'+r.name+'</option>';
    hmSel.innerHTML += '<option value="'+r.slug+'">'+r.name+'</option>';
  }});
  const cats = [...new Set(DATA.features.map(f => f.category).filter(Boolean))].sort();
  const catSel = document.getElementById('filter-category');
  cats.forEach(c => {{ catSel.innerHTML += '<option value="'+c+'">'+c+'</option>'; }});
  filteredFeatures = DATA.features;
  renderFeatures();
}}

function showTab(name) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.querySelectorAll('.tab')[['search','compare','heatmap'].indexOf(name)].classList.add('active');
}}

function filterFeatures() {{
  const q = document.getElementById('search-input').value.toLowerCase();
  const rel = document.getElementById('filter-release').value;
  const cat = document.getElementById('filter-category').value;
  filteredFeatures = DATA.features.filter(f => {{
    if (q && !f.name.toLowerCase().includes(q)) return false;
    if (rel && f.release !== rel) return false;
    if (cat && f.category !== cat) return false;
    return true;
  }});
  renderFeatures();
}}

function renderFeatures() {{
  const tbody = document.getElementById('features-body');
  document.getElementById('results-count').textContent = filteredFeatures.length + ' resultados';
  const rows = filteredFeatures.slice(0, 500).map(f =>
    '<tr><td>'+esc(f.name)+'</td><td>'+esc(f.category)+'</td><td>'+esc(f.release)+'</td><td>'+esc(f.availability)+'</td></tr>'
  ).join('');
  tbody.innerHTML = rows || '<tr><td colspan="4" style="text-align:center;color:#999">Nenhum resultado</td></tr>';
}}

function compareReleases() {{
  const a = document.getElementById('compare-a').value;
  const b = document.getElementById('compare-b').value;
  if (!a || !b) return;
  const rA = DATA.releases.find(r => r.slug === a);
  const rB = DATA.releases.find(r => r.slug === b);
  if (!rA || !rB) return;
  document.getElementById('col-a').textContent = rA.name;
  document.getElementById('col-b').textContent = rB.name;
  const catsA = Object.fromEntries(rA.categories.map(c => [c.name, c.count]));
  const catsB = Object.fromEntries(rB.categories.map(c => [c.name, c.count]));
  const allCats = [...new Set([...Object.keys(catsA), ...Object.keys(catsB)])].sort();
  const tbody = document.getElementById('compare-body');
  tbody.innerHTML = allCats.map(name => {{
    const vA = catsA[name] || 0;
    const vB = catsB[name] || 0;
    const delta = vB - vA;
    const color = delta > 0 ? '#16a34a' : delta < 0 ? '#dc2626' : '#64748b';
    return '<tr><td>'+esc(name)+'</td><td>'+vA+'</td><td>'+vB+'</td><td style="color:'+color+';font-weight:600">'+(delta>=0?'+':'')+delta+'</td></tr>';
  }}).join('');
}}

function renderHeatmap() {{
  const slug = document.getElementById('heatmap-release').value;
  const grid = document.getElementById('heatmap-grid');
  if (!slug) {{ grid.innerHTML = ''; return; }}
  const r = DATA.releases.find(x => x.slug === slug);
  if (!r) return;
  grid.innerHTML = r.categories.map(c => {{
    const catConf = c.avg_confidence || r.avg_confidence || 0.85;
    const heat = Math.round(catConf * 100);
    const hue = heat * 1.2;
    const bg = 'hsl('+hue+',70%,45%)';
    return '<div class="heat-cell" style="background:'+bg+'" data-tip="'+esc(c.name)+': '+c.count+' features ('+heat+'% conf)">'+c.count+'</div>';
  }}).join('');
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }}

function exportCSV() {{
  const header = 'Feature,Categoria,Release,Disponibilidade\\n';
  const rows = filteredFeatures.map(f =>
    '"'+f.name.replace(/"/g,'""')+'","'+f.category+'","'+f.release+'","'+f.availability+'"'
  ).join('\\n');
  download('features.csv', header + rows, 'text/csv');
}}

function exportJSON() {{
  download('features.json', JSON.stringify(filteredFeatures, null, 2), 'application/json');
}}

function download(name, content, type) {{
  const blob = new Blob([content], {{type}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
}}

init();
</script>
</body>
</html>"""


def generate_dashboard(output_dir: str = DASHBOARD_DIR) -> str | None:
    """Generate interactive dashboard. Returns output path or None if no data."""
    data = _build_dashboard_data()
    if not data["releases"]:
        return None
    html_content = generate_dashboard_html(data)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / "dashboard.html"
    output_file.write_text(html_content, encoding="utf-8")
    return str(output_file)
