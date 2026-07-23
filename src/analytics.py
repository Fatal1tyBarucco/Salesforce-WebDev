"""Historical analytics dashboard generator.

Loads all release metadata from .meta.json files and generates a static
HTML dashboard with charts for category breakdown, trend analysis, and
confidence tracking. Uses inline SVG — no external JS/CSS dependencies.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR

ANALYTICS_DIR = "analytics"


@dataclass
class CategoryStats:
    """Stats for a single category across releases."""

    name: str
    counts: list[int]
    avg: float
    min_val: int
    max_val: int
    trend: str  # "up" | "down" | "stable"
    trend_delta: int  # change from first to last


@dataclass
class ReleaseStats:
    """Stats for the entire release history."""

    total_releases: int
    total_features: int
    avg_confidence: float
    release_names: list[str]
    feature_counts: list[int]
    confidence_values: list[float]
    categories: list[CategoryStats]
    days_between: list[float]


def load_all_metas() -> list[dict[str, Any]]:
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
            except (json.JSONDecodeError, OSError):
                continue

    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


def _parse_generated_at(meta: dict[str, Any]) -> float:
    """Extract epoch timestamp from generated_at field."""
    from datetime import datetime, timezone

    ts = meta.get("generated_at", "")
    if not ts:
        return 0.0
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return 0.0


def compute_stats(metas: list[dict[str, Any]]) -> ReleaseStats:
    """Compute aggregate statistics from all release metas."""
    if not metas:
        return ReleaseStats(0, 0, 0.0, [], [], [], [], [])

    total_releases = len(metas)
    release_names = [m.get("name", m.get("slug", "?")) for m in metas]
    feature_counts = [m.get("total_features", 0) for m in metas]
    confidence_values = [m.get("avg_confidence", 0.0) for m in metas]
    total_features = sum(feature_counts)
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

    # Category aggregation
    cat_data: dict[str, list[int]] = {}
    for m in metas:
        for c in m.get("categories", []):
            name = c.get("name", "?")
            cat_data.setdefault(name, []).append(c.get("count", 0))

    categories: list[CategoryStats] = []
    for name, counts in cat_data.items():
        avg = sum(counts) / len(counts) if counts else 0
        min_val = min(counts) if counts else 0
        max_val = max(counts) if counts else 0
        if len(counts) >= 2:
            delta = counts[-1] - counts[0]
            if delta > 5:
                trend = "up"
            elif delta < -5:
                trend = "down"
            else:
                trend = "stable"
        else:
            delta = 0
            trend = "stable"
        categories.append(CategoryStats(name, counts, avg, min_val, max_val, trend, delta))

    categories.sort(key=lambda c: c.avg, reverse=True)

    # Release cadence
    days_between: list[float] = []
    timestamps = [_parse_generated_at(m) for m in metas]
    valid_ts = [t for t in timestamps if t > 0]
    if len(valid_ts) >= 2:
        for i in range(1, len(valid_ts)):
            delta_days = (valid_ts[i] - valid_ts[i - 1]) / 86400
            days_between.append(round(delta_days, 1))

    return ReleaseStats(
        total_releases=total_releases,
        total_features=total_features,
        avg_confidence=avg_confidence,
        release_names=release_names,
        feature_counts=feature_counts,
        confidence_values=confidence_values,
        categories=categories,
        days_between=days_between,
    )


def _svg_bar_chart(
    labels: list[str],
    values: list[int],
    width: int = 700,
    bar_height: int = 28,
    color: str = "#2563eb",
) -> str:
    """Generate an SVG horizontal bar chart."""
    n = len(labels)
    if n == 0:
        return "<p>Sem dados</p>"
    chart_height = n * (bar_height + 6) + 10
    max_val = max(values) if values else 1
    bar_area = width - 200
    lines = [f'<svg width="{width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">']
    for i, (label, val) in enumerate(zip(labels, values)):
        y = i * (bar_height + 6) + 5
        bw = int((val / max_val) * bar_area) if max_val > 0 else 0
        escaped = html.escape(label)
        lines.append(
            f'  <text x="5" y="{y + bar_height // 2 + 4}" font-size="12" fill="#333">{escaped}</text>'
        )
        lines.append(
            f'  <rect x="190" y="{y}" width="{bw}" height="{bar_height}" '
            f'fill="{color}" rx="4" opacity="0.85"/>'
        )
        lines.append(
            f'  <text x="{195 + bw}" y="{y + bar_height // 2 + 4}" '
            f'font-size="12" fill="#555">{val}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def _svg_line_chart(
    labels: list[str],
    series: dict[str, list[float]],
    width: int = 700,
    height: int = 250,
) -> str:
    """Generate an SVG line chart with multiple series."""
    n = len(labels)
    if n == 0:
        return "<p>Sem dados</p>"

    all_vals = [v for vs in series.values() for v in vs]
    if not all_vals:
        return "<p>Sem dados</p>"
    max_val = max(all_vals) if all_vals else 1
    min_val = min(all_vals) if all_vals else 0
    val_range = max_val - min_val if max_val != min_val else 1

    colors = ["#2563eb", "#dc2626", "#16a34a", "#ea580c", "#7c3aed"]
    margin_left = 60
    margin_bottom = 40
    chart_w = width - margin_left - 20
    chart_h = height - margin_bottom - 20

    lines = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']

    # Grid lines
    for i in range(5):
        gy = 20 + chart_h - (i / 4) * chart_h
        gval = min_val + (i / 4) * val_range
        lines.append(
            f'  <line x1="{margin_left}" y1="{gy}" x2="{width - 20}" y2="{gy}" stroke="#e5e7eb" stroke-width="1"/>'
        )
        lines.append(
            f'  <text x="{margin_left - 5}" y="{gy + 4}" text-anchor="end" font-size="10" fill="#888">{int(gval)}</text>'
        )

    # X-axis labels
    step = max(1, n // 6)
    for i in range(0, n, step):
        lx = margin_left + (i / max(1, n - 1)) * chart_w
        lines.append(
            f'  <text x="{lx}" y="{height - 10}" text-anchor="middle" font-size="10" fill="#888">{html.escape(labels[i])}</text>'
        )

    # Series
    for si, (name, vals) in enumerate(series.items()):
        color = colors[si % len(colors)]
        points = []
        for i, v in enumerate(vals):
            x = margin_left + (i / max(1, n - 1)) * chart_w
            y = 20 + chart_h - ((v - min_val) / val_range) * chart_h
            points.append(f"{x:.1f},{y:.1f}")
        lines.append(
            f'  <polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
        )
        for i, v in enumerate(vals):
            x = margin_left + (i / max(1, n - 1)) * chart_w
            y = 20 + chart_h - ((v - min_val) / val_range) * chart_h
            lines.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')

    # Legend
    lx = margin_left
    for si, name in enumerate(series.keys()):
        color = colors[si % len(colors)]
        lines.append(
            f'  <rect x="{lx}" y="{height - 30}" width="12" height="12" fill="{color}" rx="2"/>'
        )
        lines.append(
            f'  <text x="{lx + 16}" y="{height - 20}" font-size="11" fill="#555">{html.escape(name)}</text>'
        )
        lx += len(name) * 7 + 30

    lines.append("</svg>")
    return "\n".join(lines)


def _svg_gauge(value: float, max_val: float, label: str, color: str = "#2563eb") -> str:
    """Generate a simple SVG gauge/progress bar."""
    pct = min(value / max_val, 1.0) if max_val > 0 else 0
    w = 200
    bar_w = int(pct * w)
    return (
        f'<div style="display:inline-block;text-align:center;margin:10px 20px">'
        f'<svg width="{w}" height="24" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="{w}" height="20" fill="#e5e7eb" rx="10"/>'
        f'<rect x="0" y="0" width="{bar_w}" height="20" fill="{color}" rx="10"/>'
        f'<text x="{w // 2}" y="15" text-anchor="middle" font-size="12" fill="#fff" font-weight="bold">'
        f"{value:.1f}</text></svg>"
        f'<div style="font-size:11px;color:#666;margin-top:4px">{html.escape(label)}</div>'
        f"</div>"
    )


def generate_dashboard_html(stats: ReleaseStats) -> str:
    """Generate a complete HTML dashboard from computed stats."""
    gauges = ""
    if stats.total_releases > 0:
        gauges += _svg_gauge(stats.avg_confidence * 100, 100, "Confiança Média (%)", "#16a34a")

    cat_chart = _svg_bar_chart(
        [c.name for c in stats.categories[:15]],
        [int(c.avg) for c in stats.categories[:15]],
        color="#2563eb",
    )

    feature_trend = ""
    confidence_trend = ""
    if len(stats.release_names) >= 2:
        feature_trend = _svg_line_chart(
            stats.release_names,
            {"Features": [float(f) for f in stats.feature_counts]},
        )
        confidence_trend = _svg_line_chart(
            stats.release_names,
            {"Confiança": [c * 100 for c in stats.confidence_values]},
        )

    cadence = ""
    if stats.days_between:
        cadence_items = "".join(
            f"<li>{html.escape(stats.release_names[i])} → {html.escape(stats.release_names[i + 1])}: "
            f"<strong>{d} dias</strong></li>"
            for i, d in enumerate(stats.days_between)
            if i + 1 < len(stats.release_names)
        )
        cadence = f"<ul>{cadence_items}</ul>"

    category_table_rows = ""
    for c in stats.categories:
        trend_icon = {"up": "📈", "down": "📉", "stable": "➡️"}[c.trend]
        trend_text = {"up": "Crescendo", "down": "Diminuindo", "stable": "Estável"}[c.trend]
        category_table_rows += (
            f"<tr><td>{html.escape(c.name)}</td><td>{c.min_val}–{c.max_val}</td>"
            f"<td>{int(c.avg)}</td><td>{c.trend_delta:+d}</td><td>{trend_icon} {trend_text}</td></tr>\n"
        )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Salesforce Release Notes — Analytics Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #f8fafc; color: #1e293b; padding: 20px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 24px; margin-bottom: 8px; }}
  h2 {{ font-size: 18px; margin: 24px 0 12px; color: #475569; }}
  .summary {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 16px 0; }}
  .card {{ background: #fff; border-radius: 12px; padding: 16px 20px;
           box-shadow: 0 1px 3px rgba(0,0,0,0.08); min-width: 160px; }}
  .card .num {{ font-size: 28px; font-weight: 700; color: #2563eb; }}
  .card .label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 13px; }}
  th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
  .chart-section {{ background: #fff; border-radius: 12px; padding: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin: 16px 0; }}
  .gauges {{ text-align: center; padding: 12px 0; }}
  footer {{ text-align: center; font-size: 11px; color: #94a3b8; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Salesforce Release Notes — Dashboard</h1>
  <p style="color:#64748b;font-size:13px">Histórico de releases processadas</p>

  <div class="summary">
    <div class="card"><div class="num">{stats.total_releases}</div><div class="label">Releases</div></div>
    <div class="card"><div class="num">{stats.total_features:,}</div><div class="label">Features Totais</div></div>
    <div class="gauges">{gauges}</div>
  </div>

  <div class="chart-section">
    <h2>Features por Categoria (média)</h2>
    {cat_chart}
  </div>

  {"<div class='chart-section'><h2>Evolução de Features</h2>" + feature_trend + "</div>" if feature_trend else ""}

  {"<div class='chart-section'><h2>Evolução da Confiança</h2>" + confidence_trend + "</div>" if confidence_trend else ""}

  <div class="chart-section">
    <h2>Detalhes por Categoria</h2>
    <table>
      <tr><th>Categoria</th><th>Min–Max</th><th>Média</th><th>Delta</th><th>Tendência</th></tr>
      {category_table_rows}
    </table>
  </div>

  {"<div class='chart-section'><h2>Cadência de Releases</h2>" + cadence + "</div>" if cadence else ""}

  <footer>Gerado automaticamente pelo pipeline de Release Notes</footer>
</div>
</body>
</html>"""


def generate_analytics(output_dir: str = ANALYTICS_DIR) -> str | None:
    """Generate analytics dashboard. Returns output path or None if no data."""
    metas = load_all_metas()
    if not metas:
        return None
    stats = compute_stats(metas)
    html_content = generate_dashboard_html(stats)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / "analytics.html"
    output_file.write_text(html_content, encoding="utf-8")
    return str(output_file)
