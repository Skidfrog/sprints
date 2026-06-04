# app.py · Overtake.GP · Anàlisi de dades
# Streamlit app que renderitza el notebook de forma interactiva

import streamlit as st
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os
import json
import base64
from pathlib import Path

# ── Configuració de la pàgina ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Overtake.GP · Anàlisi de dades",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Carreguem el notebook ─────────────────────────────────────────────────────
@st.cache_resource
def carregar_notebook():
    # Substitueix la línia 23 per aquesta:
    BASE_DIR = Path(__file__).parent
    with open(BASE_DIR / "Overtake_analisi_v4_1.ipynb", "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

nb = carregar_notebook()

# ── Sidebar · navegació ───────────────────────────────────────────────────────
st.sidebar.title("🏍️ Overtake.GP")
st.sidebar.markdown("**Anàlisi de dades · 2024–2026**")
st.sidebar.divider()

# Construïm índex de navegació a partir dels títols # del notebook
seccions = []
for cell in nb.cells:
    if cell.cell_type == "markdown":
        for line in cell.source.split("\n"):
            if line.startswith("# ") and not line.startswith("## "):
                seccions.append(line.replace("# ", "").strip())

seccio_activa = st.sidebar.radio("Navega", seccions)
st.sidebar.divider()
st.sidebar.caption("Projecte TFG + Bootcamp Data Analytics · Barcelona Activa · 2026")

# ── Renderitzem el notebook ───────────────────────────────────────────────────
def renderitzar_cel_la(cell, idx):
    """Renderitza una cel·la del notebook segons el seu tipus."""

    if cell.cell_type == "markdown":
        src = cell.source

        # Detectem si és un títol de primer nivell — separador de secció
        if src.strip().startswith("# ") and not src.strip().startswith("## "):
            st.divider()

        st.markdown(cell.source, unsafe_allow_html=True)

    elif cell.cell_type == "code":
        src = cell.source.strip()
        if not src:
            return

        # Codi ocult per defecte, expandible
        with st.expander("📄 Veure codi", expanded=False):
            st.code(src, language="python")

        # Outputs de la cel·la
        for output in cell.outputs:
            tipus = output.get("output_type", "")

            # Text
            if tipus in ("stream", "execute_result", "display_data"):
                text = output.get("text", "")
                if isinstance(text, list):
                    text = "".join(text)
                if text.strip():
                    st.text(text)

            # Imatges (PNG)
            if tipus in ("display_data", "execute_result"):
                data = output.get("data", {})
                if "image/png" in data:
                    img_data = data["image/png"]
                    if isinstance(img_data, list):
                        img_data = "".join(img_data)
                    img_bytes = base64.b64decode(img_data)
                    st.image(img_bytes, use_column_width=True)

                # HTML (graella interactiva)
                if "text/html" in data:
                    html_content = data["text/html"]
                    if isinstance(html_content, list):
                        html_content = "".join(html_content)
                    st.components.v1.html(html_content, height=600, scrolling=True)

# Filtrem les cel·les per secció activa
en_seccio = False
for idx, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        src = cell.source.strip()
        # Detectem si entrem a la secció activa
        for line in src.split("\n"):
            if line.startswith("# ") and not line.startswith("## "):
                titol = line.replace("# ", "").strip()
                if titol == seccio_activa:
                    en_seccio = True
                elif en_seccio:
                    en_seccio = False

    if en_seccio or seccio_activa == seccions[0]:
        renderitzar_cel_la(cell, idx)