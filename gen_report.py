"""Build a portable, self-contained HTML incident report with sample data.

Every chart is inline SVG inside <figure data-say="..."> and is coloured by
class names only, so a presenter can re-theme it (for example dark at
night) without redrawing. The raw data also travels in a JSON block.
"""
import json
import math
from html import escape

W, H = 1280, 720
FONT = "'Helvetica Neue',Helvetica,Arial,sans-serif"


def fmt(n):
    a = abs(n)
    if a >= 1e4:
        return f"{n / 1e3:.1f}".rstrip("0").rstrip(".") + "K"
    return f"{n:,.0f}" if a >= 100 or n == int(n) else f"{n:.1f}"


def frame(title, sub, body):
    size = max(26, min(42, int(1160 / (0.55 * len(title)))))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">'
            f'<rect class="bg" width="{W}" height="{H}"/>'
            f'<text class="ink" x="60" y="80" font-size="{size}" font-weight="700">{escape(title)}</text>'
            f'<text class="mut" x="60" y="120" font-size="24">{escape(sub)}</text>{body}</svg>')


def nice_top(v):
    raw = v / 5
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    return step, step * math.ceil(v / step)


def line(title, sub, xs, ys, unit="", limit=None, limit_label="", col="red"):
    x0, x1, y0, y1 = 130, 1100, 170, 630
    step, top = nice_top(max(ys + ([limit] if limit else [])))
    sx = lambda i: x0 + i / (len(xs) - 1) * (x1 - x0)
    sy = lambda v: y1 - v / top * (y1 - y0)
    b = ""
    v = 0
    while v <= top + 1e-9:
        b += (f'<line class="grid" x1="{x0}" y1="{sy(v):.0f}" x2="{x1}" y2="{sy(v):.0f}" stroke-width="2"/>'
              f'<text class="mut" x="{x0 - 14}" y="{sy(v) + 7:.0f}" font-size="20" text-anchor="end">{fmt(v)}{unit}</text>')
        v += step
    for i, x in enumerate(xs):
        if i % 2 == 0 or i == len(xs) - 1:
            b += f'<text class="mut" x="{sx(i):.0f}" y="{y1 + 38}" font-size="20" text-anchor="middle">{x}</text>'
    if limit is not None:
        b += (f'<line class="lim" x1="{x0}" y1="{sy(limit):.0f}" x2="{x1}" y2="{sy(limit):.0f}" stroke-width="3" stroke-dasharray="10 8"/>'
              f'<text class="limT" x="{x0 + 10}" y="{sy(limit) - 10:.0f}" font-size="20">{escape(limit_label)}</text>')
    pts = " ".join(f"{sx(i):.0f},{sy(v):.0f}" for i, v in enumerate(ys))
    b += f'<polyline class="{col}S" points="{pts}" fill="none" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
    pk = ys.index(max(ys))
    b += (f'<circle class="{col}" cx="{sx(pk):.0f}" cy="{sy(ys[pk]):.0f}" r="10"/>'
          f'<text class="{col}" x="{sx(pk) + 18:.0f}" y="{sy(ys[pk]) + 4:.0f}" font-size="30" font-weight="700">{fmt(ys[pk])}{unit}</text>')
    return frame(title, sub, b)


def bars(title, sub, items, unit=""):
    items = sorted(items, key=lambda kv: kv[1], reverse=True)
    x0, x1, y0, y1 = 360, 1080, 170, 670
    top = max(v for _, v in items)
    step = (y1 - y0) / len(items)
    bh = min(60, step * 0.68)
    b = ""
    for i, (k, v) in enumerate(items):
        cy = y0 + step * i + step / 2
        w = max(v / top * (x1 - x0), 3)
        cls, wt = ("acc", ' font-weight="700"') if i == 0 else ("rest", "")
        b += (f'<rect class="{cls}" x="{x0}" y="{cy - bh / 2:.0f}" width="{w:.0f}" height="{bh:.0f}" rx="5"/>'
              f'<text class="ink" x="{x0 - 18}" y="{cy + 9:.0f}" font-size="28" text-anchor="end"{wt}>{escape(k)}</text>'
              f'<text class="ink" x="{x0 + w + 14:.0f}" y="{cy + 9:.0f}" font-size="28"{wt}>{fmt(v)}{unit}</text>')
    b += f'<line class="axis" x1="{x0}" y1="{y0 - 10}" x2="{x0}" y2="{y1}" stroke-width="2"/>'
    return frame(title, sub, b)


def pie(title, sub, items, donut=False):
    items = sorted(items, key=lambda kv: kv[1], reverse=True)
    total = sum(v for _, v in items)
    cx, cy, r, ri = 420, 415, 235, (125 if donut else 0)
    a = -math.pi / 2
    b = ""
    for i, (k, v) in enumerate(items):
        a2 = a + v / total * 2 * math.pi
        big = 1 if a2 - a > math.pi else 0
        p = lambda ang, rad: (cx + rad * math.cos(ang), cy + rad * math.sin(ang))
        (ox1, oy1), (ox2, oy2) = p(a, r), p(a2, r)
        if donut:
            (ix1, iy1), (ix2, iy2) = p(a2, ri), p(a, ri)
            d = (f"M{ox1:.1f},{oy1:.1f} A{r},{r} 0 {big} 1 {ox2:.1f},{oy2:.1f} "
                 f"L{ix1:.1f},{iy1:.1f} A{ri},{ri} 0 {big} 0 {ix2:.1f},{iy2:.1f} Z")
        else:
            d = f"M{cx},{cy} L{ox1:.1f},{oy1:.1f} A{r},{r} 0 {big} 1 {ox2:.1f},{oy2:.1f} Z"
        b += f'<path class="p{i} sep" d="{d}" stroke-width="4"/>'
        ly = 250 + i * 64
        wt = ' font-weight="700"' if i == 0 else ""
        b += (f'<rect class="p{i}" x="760" y="{ly - 24}" width="30" height="30" rx="5"/>'
              f'<text class="ink" x="808" y="{ly}" font-size="30"{wt}>{escape(k)}</text>'
              f'<text class="ink" x="1220" y="{ly}" font-size="30" text-anchor="end"{wt}>{v / total * 100:.0f}%</text>')
        a = a2
    if donut:
        b += (f'<text class="ink" x="{cx}" y="{cy + 14}" font-size="44" font-weight="700" text-anchor="middle">{items[0][1] / total * 100:.0f}%</text>'
              f'<text class="mut" x="{cx}" y="{cy + 50}" font-size="22" text-anchor="middle">{escape(items[0][0])}</text>')
    return frame(title, sub, b)


def _incident():
    times = ["21:30", "21:40", "21:50", "22:00", "22:10", "22:20", "22:30", "22:40", "22:50", "23:00"]
    DATA = {
        "incident": "INC-2041", "title": "Checkout slowdown and payment errors",
        "service": "Northwind Payments (sample data)", "date": "2026-11-25",
        "error_rate_pct": dict(zip(times, [0.2, 0.3, 0.2, 0.4, 3.9, 7.8, 6.2, 2.1, 0.6, 0.3])),
        "p95_latency_ms": dict(zip(times, [180, 190, 185, 200, 1450, 2600, 2300, 900, 260, 210])),
        "errors_by_cause": {"Timeouts": 62, "Database pool full": 23, "Bad config push": 10, "Other": 5},
        "failed_by_service": {"Checkout": 48200, "Refunds": 9100, "Receipts": 3300, "Reporting": 800, "Login": 150},
        "impact_by_region": {"Ontario": 41, "Quebec": 22, "BC": 18, "Prairies": 12, "Atlantic": 7},
        "response_minutes": {"Detect": 4, "Acknowledge": 3, "Mitigate": 31, "Full recovery": 34},
    }
    lat = list(DATA["p95_latency_ms"].values())
    FIGS = [
        ("Error rate peaked at 7.8% at 22:20, far above the 1% limit",
         line("Error rate peaked at 7.8% at 22:20, far above the 1% limit", "Share of payment requests that failed",
              times, list(DATA["error_rate_pct"].values()), "%", 1, "Limit 1%")),
        (f"Checkout got {max(lat) / lat[0]:.0f} times slower at the peak",
         line(f"Checkout got {max(lat) / lat[0]:.0f} times slower at the peak", "Slowest 5% of checkouts, in milliseconds",
              times, lat, "", 500, "Target 500 ms")),
        ("Most errors were timeouts: 62%",
         pie("Most errors were timeouts: 62%", "Errors by cause", list(DATA["errors_by_cause"].items()))),
        ("Checkout took the biggest hit: 48K failed requests",
         bars("Checkout took the biggest hit: 48K failed requests", "Failed requests by service",
              list(DATA["failed_by_service"].items()))),
        ("Ontario saw the most impact: 41% of affected traffic",
         pie("Ontario saw the most impact: 41% of affected traffic", "Affected traffic by region",
             list(DATA["impact_by_region"].items()), donut=True)),
        ("72 minutes from first alert to full recovery",
         bars("72 minutes from first alert to full recovery", "Minutes spent at each stage",
              list(DATA["response_minutes"].items()), " min")),
    ]
    LIGHT = (".bg{fill:#fff}.ink{fill:#1a1a1a}.mut{fill:#6b7280}.grid{stroke:#e5e7eb}.axis{stroke:#9aa0a6}"
             ".acc{fill:#1f6feb}.accS{stroke:#1f6feb}.rest{fill:#c4c9d0}.red{fill:#d1242f}.redS{stroke:#d1242f}.lim{stroke:#c77700}.limT{fill:#c77700}"
             ".p0{fill:#1f6feb}.p1{fill:#5b93f0}.p2{fill:#93b8f5}.p3{fill:#c3d7fa}.p4{fill:#e3ecfc}.sep{stroke:#fff}")
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            f"<title>{DATA['incident']}: {DATA['title']}</title><style>body{{margin:0 auto;max-width:960px;padding:32px;"
            f"font:17px/1.5 {FONT};color:#1a1a1a}}h1{{margin:0 0 4px}}figure{{margin:28px 0}}svg{{width:100%;height:auto;"
            f"border:1px solid #e5e7eb;border-radius:8px}}figcaption{{color:#6b7280;margin-top:6px}}{LIGHT}</style></head><body>"
            f"<h1>{DATA['incident']}: {DATA['title']}</h1><p>{DATA['service']} &middot; {DATA['date']} &middot; "
            "Payments slowed and failed for about 72 minutes after a config push exhausted the database connection pool. "
            "Rolled back at 22:38; fully recovered by 22:46.</p>"
            + "".join(f'<figure data-say="{escape(say)}">{svg}<figcaption>{escape(say)}</figcaption></figure>' for say, svg in FIGS)
            + f"<script type='application/json' id='report-data'>{json.dumps(DATA)}</script></body></html>")
    open("incident-report.html", "w").write(html)
    print(len(html), "bytes,", len(FIGS), "figures")

if __name__ == "__main__":
    _incident()
