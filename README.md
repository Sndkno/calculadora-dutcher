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

## ¿Cómo uso la calculadora?

1. Introduce la **Cuota de la Casa 1** (ejemplo: `2.60`).
2. Introduce la **Cuota de la Casa 2** (ejemplo: `1.65`).
3. Introduce la **Inversión Total** en euros que quieres apostar (ejemplo: `100`).
4. Pulsa el botón **Calcular** (o presiona `Enter`).

La aplicación te mostrará:
- Si la operación genera **beneficio** (Surebet ✅) o **pérdida** ⚠️, junto con el porcentaje.
- Cuánto dinero apostar exactamente en cada casa.
- El desglose completo de los dos escenarios posibles.
