# Calculadora de Arbitraje Deportivo (Surebet / Dutching)

Aplicación web de una sola página para calcular apuestas de arbitraje deportivo (Surebets). No requiere instalación ni servidor.

## ¿Cómo abro la aplicación?

### Opción 1 — Abrir directamente en el navegador (más sencillo)

1. Descarga o clona este repositorio en tu ordenador.
2. Entra en la carpeta del proyecto.
3. Haz **doble clic** sobre el archivo `index.html`.
4. El archivo se abrirá automáticamente en tu navegador predeterminado (Chrome, Firefox, Edge, Safari…).

> **Nota:** No necesitas instalar nada. El archivo funciona directamente sin conexión a internet.

### Opción 2 — Desde la línea de comandos

```bash
# Clona el repositorio
git clone https://github.com/Sndkno/calculadora-dutcher.git

# Entra en la carpeta
cd calculadora-dutcher

# Abre el archivo en el navegador
# En Windows:
start index.html

# En macOS:
open index.html

# En Linux:
xdg-open index.html
```

### Opción 3 — Con un servidor local (opcional)

Si prefieres servir el archivo a través de un servidor local, puedes usar Python:

```bash
# Python 3
python3 -m http.server 8080
```

Luego abre `http://localhost:8080` en tu navegador.

---

## 📡 Radar de Surebets (script Python)

El archivo `radar_surebets.py` se conecta a [The Odds API](https://the-odds-api.com/) (plan gratuito), detecta oportunidades de arbitraje en tiempo real y genera automáticamente el archivo `radar_resultados.html` con un diseño *dark mode* premium.

### Requisitos

```bash
pip install requests
```

### Configuración

Edita las siguientes variables al inicio de `radar_surebets.py`:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `API_KEY` | Tu clave de The Odds API | `"TU_API_KEY_AQUI"` |
| `SPORT` | Deporte a analizar | `"tennis_atp"` |
| `BOOKMAKERS_FILTER` | Lista de bookmakers a incluir | bwin, betfair, 1xbet… |

Obtén tu API Key gratuita en [https://the-odds-api.com/](https://the-odds-api.com/).

### Uso

```bash
python3 radar_surebets.py
```

El script imprimirá las surebets encontradas en la consola y generará `radar_resultados.html` que puedes abrir directamente en tu navegador.

### Deportes disponibles (ejemplos)

- `tennis_atp` — ATP Tennis
- `basketball_nba` — NBA Basketball
- `americanfootball_nfl` — NFL American Football
- `soccer_epl` — English Premier League

> **Aviso:** Las cuotas cambian constantemente. Verifica siempre los valores antes de apostar. Este software tiene fines informativos.

---

## ¿Cómo uso la calculadora?

1. Introduce la **Cuota de la Casa 1** (ejemplo: `2.60`).
2. Introduce la **Cuota de la Casa 2** (ejemplo: `1.65`).
3. Introduce la **Inversión Total** en euros que quieres apostar (ejemplo: `100`).
4. Pulsa el botón **Calcular** (o presiona `Enter`).

La aplicación te mostrará:
- Si la operación genera **beneficio** (Surebet ✅) o **pérdida** ⚠️, junto con el porcentaje.
- Cuánto dinero apostar exactamente en cada casa.
- El desglose completo de los dos escenarios posibles.
