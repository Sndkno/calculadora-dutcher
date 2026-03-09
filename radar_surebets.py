"""
Radar de Surebets — The Odds API
=================================
Conecta a The Odds API, detecta oportunidades de arbitraje (surebets)
y genera automáticamente el archivo 'radar_resultados.html'.

Uso:
    python3 radar_surebets.py

Requisitos:
    pip install requests
"""

import sys
import html as html_module
from datetime import datetime, timezone
import requests

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

# ⚠️  Sustituye este valor por tu propia API Key de The Odds API
API_KEY = "60e4187d5ca5237f4a6b82063f8d613a"

# Deporte a consultar (mercado de 2 opciones)
# Opciones populares: "tennis_atp", "basketball_nba", "americanfootball_nfl"
SPORT = "tennis_atp"

# Región de las cuotas
REGIONS = "eu"

# Mercado: H2H (Head to Head / Ganador del partido)
MARKETS = "h2h"

# Formato de cuotas: decimal (europeo)
ODDS_FORMAT = "decimal"

# Casas de apuestas europeas/españolas a filtrar (deja vacío [] para todas)
BOOKMAKERS_FILTER = ["bwin", "betfair_ex_eu", "1xbet", "betway", "unibet_eu",
                     "williamhill", "bet365", "pinnacle", "betsson"]

# URL base de la API
BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"

# Nombre del archivo HTML de salida
OUTPUT_FILE = "radar_resultados.html"

# ─── LÓGICA DE ARBITRAJE ──────────────────────────────────────────────────────


def fetch_odds():
    """Solicita cuotas a The Odds API y devuelve la lista de eventos."""
    url = BASE_URL.format(sport=SPORT)
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.exceptions.ConnectionError:
        print("❌  Error de conexión: no se pudo contactar con The Odds API.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌  Tiempo de espera agotado al conectar con The Odds API.")
        sys.exit(1)

    if response.status_code == 401:
        print("❌  API Key inválida o no autorizada. Revisa tu API_KEY.")
        sys.exit(1)
    if response.status_code == 422:
        print(f"❌  Deporte '{SPORT}' no válido o no disponible en el plan gratuito.")
        sys.exit(1)
    if response.status_code == 429:
        print("❌  Límite de solicitudes alcanzado. Espera antes de volver a intentarlo.")
        sys.exit(1)
    if not response.ok:
        print(f"❌  Error HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()
    remaining = response.headers.get("x-requests-remaining", "?")
    used = response.headers.get("x-requests-used", "?")
    print(f"✅  API respondió correctamente. "
          f"Solicitudes usadas: {used} | Restantes: {remaining}")
    return data


def best_odds_per_outcome(bookmakers):
    """
    Devuelve, para cada resultado posible, la mejor cuota y la casa que la ofrece.

    Returns:
        dict: { outcome_name: {"odds": float, "bookmaker": str} }
    """
    best: dict = {}
    for bookmaker in bookmakers:
        name = bookmaker.get("title", bookmaker.get("key", "Desconocida"))
        key = bookmaker.get("key", "")

        # Aplicar filtro de casas si se ha definido
        if BOOKMAKERS_FILTER and key not in BOOKMAKERS_FILTER:
            continue

        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue
            for outcome in market.get("outcomes", []):
                o_name = outcome["name"]
                o_price = outcome["price"]
                if o_name not in best or o_price > best[o_name]["odds"]:
                    best[o_name] = {"odds": o_price, "bookmaker": name}

    return best


def detect_surebets(events):
    """
    Analiza los eventos y devuelve los que presentan oportunidad de arbitraje.

    Returns:
        list of dict con los detalles de cada surebet detectada.
    """
    surebets = []

    for event in events:
        bookmakers = event.get("bookmakers", [])
        if not bookmakers:
            continue

        best = best_odds_per_outcome(bookmakers)

        # Solo procesar mercados de exactamente 2 resultados
        if len(best) != 2:
            continue

        outcomes = list(best.items())
        name_a, data_a = outcomes[0]
        name_b, data_b = outcomes[1]

        odds_a = data_a["odds"]
        odds_b = data_b["odds"]
        book_a = data_a["bookmaker"]
        book_b = data_b["bookmaker"]

        # Fórmula de arbitraje
        p = (1 / odds_a) + (1 / odds_b)

        if p < 1:
            profit_pct = round((1 / p - 1) * 100, 4)
            surebets.append({
                "home_team":   event.get("home_team", "Equipo Local"),
                "away_team":   event.get("away_team", "Equipo Visitante"),
                "commence_time": event.get("commence_time", ""),
                "sport_title": event.get("sport_title", SPORT),
                "p":           round(p, 6),
                "profit_pct":  profit_pct,
                "outcome_a": {
                    "name": name_a,
                    "odds": odds_a,
                    "bookmaker": book_a,
                },
                "outcome_b": {
                    "name": name_b,
                    "odds": odds_b,
                    "bookmaker": book_b,
                },
            })

    # Ordenar por mayor beneficio primero
    surebets.sort(key=lambda x: x["profit_pct"], reverse=True)
    return surebets


# ─── GENERACIÓN DE HTML ───────────────────────────────────────────────────────

def format_datetime(iso_str: str) -> str:
    """Convierte una cadena ISO 8601 en fecha legible en español."""
    if not iso_str:
        return "Fecha no disponible"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_local = dt.astimezone()
        months = ["ene", "feb", "mar", "abr", "may", "jun",
                  "jul", "ago", "sep", "oct", "nov", "dic"]
        weekdays = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
        wd = weekdays[dt_local.weekday()]
        mo = months[dt_local.month - 1]
        return (f"{wd}. {dt_local.day} {mo}. {dt_local.year} "
                f"— {dt_local.strftime('%H:%M')} (hora local)")
    except (ValueError, OSError):
        return iso_str


def esc(text) -> str:
    """Escapa caracteres HTML especiales."""
    return html_module.escape(str(text))


def generate_html(surebets: list, generated_at: str, year: int) -> str:
    """Genera el contenido HTML completo del radar."""

    # ── Tarjetas de surebets ──────────────────────────────────────────────────
    if not surebets:
        cards_html = """
        <div class="no-results">
          <div class="no-results-icon">🔍</div>
          <h2>Sin surebets detectadas</h2>
          <p>
            No se encontraron oportunidades de arbitraje en este momento
            para el deporte <strong>{sport}</strong> con las casas de apuestas filtradas.<br>
            Prueba más tarde o amplía el filtro de bookmakers.
          </p>
        </div>
        """.format(sport=esc(SPORT))
    else:
        card_parts = []
        for sb in surebets:
            event_title = esc(f"{sb['home_team']} vs {sb['away_team']}")
            sport_title = esc(sb["sport_title"])
            date_str = esc(format_datetime(sb["commence_time"]))
            profit = f"{sb['profit_pct']:.2f}"
            p_total = f"{sb['p'] * 100:.2f}"

            name_a = esc(sb["outcome_a"]["name"])
            odds_a = f"{sb['outcome_a']['odds']:.2f}"
            book_a = esc(sb["outcome_a"]["bookmaker"])

            name_b = esc(sb["outcome_b"]["name"])
            odds_b = f"{sb['outcome_b']['odds']:.2f}"
            book_b = esc(sb["outcome_b"]["bookmaker"])

            card_parts.append(f"""
        <article class="card">
          <div class="card-header">
            <div class="card-meta">
              <span class="sport-badge">{sport_title}</span>
              <span class="card-date">🗓 {date_str}</span>
            </div>
            <h2 class="card-title">⚡ {event_title}</h2>
          </div>

          <div class="profit-banner">
            <div class="profit-label">BENEFICIO GARANTIZADO</div>
            <div class="profit-pct">+{profit}%</div>
            <div class="profit-sub">Probabilidad total: {p_total}%</div>
          </div>

          <div class="bets-grid">
            <div class="bet-block bet-a">
              <div class="bet-side-label">APUESTA 1 — Gana <span class="player-name">{name_a}</span></div>
              <div class="bet-bookmaker">🏠 {book_a}</div>
              <div class="bet-odds">{odds_a}</div>
              <div class="bet-odds-label">cuota</div>
            </div>
            <div class="bet-vs">VS</div>
            <div class="bet-block bet-b">
              <div class="bet-side-label">APUESTA 2 — Gana <span class="player-name">{name_b}</span></div>
              <div class="bet-bookmaker">🏠 {book_b}</div>
              <div class="bet-odds">{odds_b}</div>
              <div class="bet-odds-label">cuota</div>
            </div>
          </div>

          <div class="card-warning">
            ⚠️ Verifica las cuotas antes de apostar: pueden cambiar en cualquier momento.
          </div>
        </article>""")

        cards_html = "\n".join(card_parts)

    n = len(surebets)
    plural = "s" if n != 1 else ""
    count_label = f"{n} surebet{plural} detectada{plural}" if surebets else "Sin resultados"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Radar de Surebets — {esc(SPORT)}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #080f1e;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 0 0 4rem;
    }}

    /* ── Header ── */
    .site-header {{
      background: linear-gradient(135deg, #0f172a 0%, #1a1040 100%);
      border-bottom: 1px solid #1e293b;
      padding: 2rem 1.5rem;
      text-align: center;
    }}

    .site-header h1 {{
      font-size: clamp(1.6rem, 5vw, 2.6rem);
      font-weight: 900;
      background: linear-gradient(135deg, #38bdf8, #a78bfa, #34d399);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: -0.02em;
      line-height: 1.15;
    }}

    .site-header .subtitle {{
      color: #64748b;
      font-size: 0.95rem;
      margin-top: 0.4rem;
    }}

    /* ── Stats bar ── */
    .stats-bar {{
      display: flex;
      justify-content: center;
      gap: 2rem;
      flex-wrap: wrap;
      padding: 1rem 1.5rem;
      background: #0d1629;
      border-bottom: 1px solid #1e293b;
    }}

    .stat-item {{
      text-align: center;
    }}

    .stat-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #475569;
      font-weight: 700;
    }}

    .stat-value {{
      font-size: 1.1rem;
      font-weight: 800;
      color: #f1f5f9;
      margin-top: 0.1rem;
    }}

    .stat-value.green {{ color: #34d399; }}

    /* ── Main container ── */
    .container {{
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }}

    .section-title {{
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #475569;
      margin-bottom: 1.25rem;
    }}

    /* ── Card ── */
    .card {{
      background: #111827;
      border: 1px solid #1e293b;
      border-radius: 1.25rem;
      overflow: hidden;
      margin-bottom: 1.5rem;
      box-shadow: 0 20px 60px -15px rgba(0,0,0,0.6);
      transition: transform 0.2s, box-shadow 0.2s;
    }}

    .card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 28px 70px -12px rgba(0,0,0,0.75);
    }}

    .card-header {{
      padding: 1.25rem 1.5rem 0.75rem;
      border-bottom: 1px solid #1e293b;
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 0.5rem;
    }}

    .sport-badge {{
      background: #1e293b;
      color: #94a3b8;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.2rem 0.65rem;
      border-radius: 9999px;
      border: 1px solid #334155;
    }}

    .card-date {{
      font-size: 0.8rem;
      color: #64748b;
    }}

    .card-title {{
      font-size: clamp(1rem, 3vw, 1.3rem);
      font-weight: 800;
      color: #f1f5f9;
      line-height: 1.3;
    }}

    /* ── Profit banner ── */
    .profit-banner {{
      background: linear-gradient(135deg, #052e16, #064e3b);
      border-bottom: 1px solid #065f46;
      padding: 1rem 1.5rem;
      text-align: center;
    }}

    .profit-label {{
      font-size: 0.7rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #6ee7b7;
      margin-bottom: 0.2rem;
    }}

    .profit-pct {{
      font-size: clamp(2rem, 6vw, 3rem);
      font-weight: 900;
      color: #34d399;
      line-height: 1;
      text-shadow: 0 0 20px rgba(52, 211, 153, 0.4);
    }}

    .profit-sub {{
      font-size: 0.8rem;
      color: #6ee7b7;
      margin-top: 0.3rem;
      opacity: 0.75;
    }}

    /* ── Bets grid ── */
    .bets-grid {{
      display: flex;
      align-items: center;
      padding: 1.25rem 1rem;
      gap: 0.75rem;
    }}

    .bet-block {{
      flex: 1;
      border-radius: 0.875rem;
      padding: 1rem;
      text-align: center;
      min-width: 0;
    }}

    .bet-a {{
      background: linear-gradient(135deg, #0c1a3d, #0f2454);
      border: 1px solid #1d4ed8;
    }}

    .bet-b {{
      background: linear-gradient(135deg, #1a0c3d, #2a0f6b);
      border: 1px solid #7c3aed;
    }}

    .bet-side-label {{
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #94a3b8;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }}

    .player-name {{
      color: #e2e8f0;
      font-weight: 800;
    }}

    .bet-bookmaker {{
      font-size: 0.85rem;
      font-weight: 700;
      color: #cbd5e1;
      margin-bottom: 0.75rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .bet-odds {{
      font-size: clamp(1.8rem, 5vw, 2.5rem);
      font-weight: 900;
      line-height: 1;
    }}

    .bet-a .bet-odds {{ color: #60a5fa; }}
    .bet-b .bet-odds {{ color: #a78bfa; }}

    .bet-odds-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #475569;
      margin-top: 0.2rem;
      font-weight: 600;
    }}

    .bet-vs {{
      font-size: 0.85rem;
      font-weight: 900;
      color: #334155;
      letter-spacing: 0.05em;
      flex-shrink: 0;
    }}

    /* ── Card warning ── */
    .card-warning {{
      background: #1a1208;
      border-top: 1px solid #292206;
      padding: 0.65rem 1.5rem;
      font-size: 0.78rem;
      color: #92400e;
      text-align: center;
    }}

    /* ── No results ── */
    .no-results {{
      text-align: center;
      padding: 4rem 2rem;
      color: #475569;
    }}

    .no-results-icon {{
      font-size: 3rem;
      margin-bottom: 1rem;
    }}

    .no-results h2 {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #64748b;
      margin-bottom: 0.75rem;
    }}

    .no-results p {{
      font-size: 0.9rem;
      line-height: 1.7;
      max-width: 480px;
      margin: 0 auto;
    }}

    .no-results strong {{
      color: #94a3b8;
    }}

    /* ── Footer ── */
    footer {{
      text-align: center;
      color: #1e293b;
      font-size: 0.8rem;
      padding: 2rem 1rem 0;
    }}

    /* ── Responsive ── */
    @media (max-width: 480px) {{
      .bets-grid {{
        flex-direction: column;
      }}
      .bet-vs {{
        transform: rotate(90deg);
      }}
    }}
  </style>
</head>
<body>

  <header class="site-header">
    <h1>📡 Radar de Surebets</h1>
    <p class="subtitle">Arbitraje automático · Deporte: {esc(SPORT)} · Mercado: H2H</p>
  </header>

  <div class="stats-bar">
    <div class="stat-item">
      <div class="stat-label">Generado</div>
      <div class="stat-value">{esc(generated_at)}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Surebets encontradas</div>
      <div class="stat-value green">{len(surebets)}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Deporte</div>
      <div class="stat-value">{esc(SPORT)}</div>
    </div>
  </div>

  <main class="container">
    <p class="section-title">🎯 {esc(count_label)}</p>
    {cards_html}
  </main>

  <footer>Radar de Surebets &copy; {year} — Solo con fines informativos. Apuesta con responsabilidad.</footer>

</body>
</html>"""


# ─── PUNTO DE ENTRADA ─────────────────────────────────────────────────────────

def main():
    print(f"🔍  Consultando cuotas para '{SPORT}' en The Odds API…")

    if API_KEY == "TU_API_KEY_AQUI":
        print("⚠️  No has configurado tu API_KEY. "
              "Edita la variable API_KEY al inicio del script.")
        sys.exit(1)

    events = fetch_odds()

    if not events:
        print("ℹ️  No hay eventos disponibles en este momento.")

    surebets = detect_surebets(events)

    if surebets:
        print(f"\n✅  {len(surebets)} surebet(s) detectada(s):")
        for sb in surebets:
            print(f"   • {sb['home_team']} vs {sb['away_team']} "
                  f"→ +{sb['profit_pct']:.2f}%  "
                  f"({sb['outcome_a']['bookmaker']} {sb['outcome_a']['odds']} / "
                  f"{sb['outcome_b']['bookmaker']} {sb['outcome_b']['odds']})")
    else:
        print("\nℹ️  No se detectaron surebets en este momento.")

    now = datetime.now(timezone.utc)
    generated_at = now.strftime("%d/%m/%Y %H:%M UTC")
    html_content = generate_html(surebets, generated_at, now.year)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n📄  Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
