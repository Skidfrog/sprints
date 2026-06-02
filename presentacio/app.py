# app.py · Overtake.GP · Dashboard de presentació
# Streamlit dashboard narratiu amb figures Plotly interactives

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import pycountry
import streamlit.components.v1 as components

# ── Configuració ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Overtake.GP · Dashboard",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR  = Path(__file__).parent
DATA_DIR  = BASE_DIR / "data"

# ── Càrrega de dades ──────────────────────────────────────────────────────────
@st.cache_data
def carregar_dades():
    hist           = pd.read_csv(DATA_DIR / "hist_processed.csv",
                                 parse_dates=['date'])
    posts_dia      = pd.read_csv(DATA_DIR / "posts_dia_combined.csv",
                                 parse_dates=['date'])
    metriques_dia  = pd.read_csv(DATA_DIR / "metriques_dia.csv",
                                 parse_dates=['date'])
    df_llarg      = pd.read_csv(DATA_DIR / "df_llarg_processed.csv", parse_dates=['date'])
    df_curt       = pd.read_csv(DATA_DIR / "df_curt_processed.csv", parse_dates=['date'])
    
    with open(DATA_DIR / "metricool_demografia.json", encoding='utf-8') as f:
        demo_raw = json.load(f)
    return hist, posts_dia, metriques_dia, demo_raw

hist, posts_dia, metriques_dia, demo_raw = carregar_dades()

# ── Preprocessament demografia ────────────────────────────────────────────────
def nom_pais(codi):
    try: return pycountry.countries.get(alpha_2=codi).name
    except: return codi

df_gender  = pd.DataFrame(demo_raw['gender']).rename(
    columns={'key':'genere','value':'pct'})
df_age     = pd.DataFrame(demo_raw['age']).rename(
    columns={'key':'franja','value':'pct'})
df_country = pd.DataFrame(demo_raw['country']).rename(
    columns={'key':'codi_pais','value':'pct'})
df_city    = pd.DataFrame(demo_raw['city']).rename(
    columns={'key':'ciutat','value':'pct'})

df_age     = df_age[df_age['franja'] != 'U'].sort_values('pct', ascending=False)
df_country = df_country.sort_values('pct', ascending=False)
df_city    = df_city.sort_values('pct', ascending=False)
df_country['nom'] = df_country['codi_pais'].apply(nom_pais)

top_countries = df_country.head(8).copy()
altres_pct = df_country.iloc[8:]['pct'].sum()
top_countries = pd.concat([
    top_countries,
    pd.DataFrame([{'codi_pais':'OTHER','pct':round(altres_pct,2),'nom':'Altres'}])
], ignore_index=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image(str(BASE_DIR / "img" / "logo.png"), width=180)
st.sidebar.title("Overtake.GP")
st.sidebar.markdown("**Anàlisi de dades · 2024–2026**")
st.sidebar.divider()

seccio = st.sidebar.radio("Navega", [
    "🏠 Inici",
    "📈 Creixement",
    "📊 Publicacions",
    "👥 Audiència",
    "📊 Benchmarking",
    "🏍️ Pilots",
    "🔬 Metodologia"
])

st.sidebar.divider()
st.sidebar.caption("Bootcamp Data Analytics · Barcelona Activa · 2026")

# ── KPIs globals ──────────────────────────────────────────────────────────────
seg_actual  = int(hist['followers_count'].iloc[-1])
seg_inicial = int(hist['followers_count'].iloc[0])
creix_pct   = (seg_actual - seg_inicial) / seg_inicial * 100
eng_mitja   = metriques_dia['engagement'].mean()

# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: INICI
# ══════════════════════════════════════════════════════════════════════════════
if seccio == "🏠 Inici":
    st.title("🏍️ Overtake.GP · Anàlisi de dades")
    st.markdown("*Desenvolupament d'un mitjà digital esportiu a Instagram · 2024–2026*")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Seguidors actuals", f"{seg_actual:,}")
    col2.metric("Creixement total",  f"+{creix_pct:.1f}%")
    col3.metric("Engagement mitjà",  f"{eng_mitja:.1f}%")
    col4.metric("Posts analitzats",  "419")

    st.divider()
    st.markdown("""
    ### Sobre el projecte
    Overtake.GP és un mitjà digital especialitzat en motorsport creat el 2022 a Instagram.
    Aquest dashboard analitza el seu creixement i rendiment entre **desembre 2023 i juny 2026**.

    | Bloc | Contingut |
    |------|-----------|
    | 📈 Creixement | Evolució de seguidors i balance diari |
    | 📊 Publicacions | Mètriques orgàniques dels posts |
    | 👥 Audiència | Perfil demogràfic dels seguidors |
    | 🔬 Metodologia | Fonts de dades, eines i procés |
    """)

# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: CREIXEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "📈 Creixement":
    st.title("📈 Creixement · Overtake.GP")
    st.divider()

    # ── Figura 1.1 · Evolució de seguidors ───────────────────────────────────
    st.subheader("Evolució de seguidors")

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(
        x=hist['date'], y=hist['followers_count'],
        name='Seguidors', line=dict(color='#1D9E75', width=2),
        fill='tozeroy', fillcolor='rgba(29,158,117,0.1)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Seguidors: %{y:,.0f}<extra></extra>'
    ), secondary_y=False)
    fig1.add_trace(go.Bar(
        x=posts_dia['date'], y=posts_dia['posts_dia'],
        name='Posts/dia', marker_color='rgba(255,165,0,0.5)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Posts: %{y:.0f}<extra></extra>'
    ), secondary_y=True)
    fig1.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.05),
            rangeselector=dict(buttons=[
                dict(count=1,  label='1m', step='month', stepmode='backward'),
                dict(count=3,  label='3m', step='month', stepmode='backward'),
                dict(count=6,  label='6m', step='month', stepmode='backward'),
                dict(count=1,  label='1a', step='year',  stepmode='backward'),
                dict(step='all', label='Tot')
            ])
        ),
        yaxis=dict(title='Seguidors'),
        yaxis2=dict(title='Posts/dia', showgrid=False),
        hovermode='x unified', height=420,
        legend=dict(orientation='h', y=1.08)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Figura 1.2 · Balance diari ────────────────────────────────────────────
    st.subheader("Balance diari de seguidors")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=hist['date'], y=hist['daily_gain'],
        name='Seguidors/dia',
        marker_color=['#1D9E75' if v >= 0 else '#E24B4A'
                      for v in hist['daily_gain']],
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Seguidors: %{y:+.0f}<extra></extra>'
    ))
    fig2.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.05),
            rangeselector=dict(buttons=[
                dict(count=1,  label='1m', step='month', stepmode='backward'),
                dict(count=3,  label='3m', step='month', stepmode='backward'),
                dict(count=6,  label='6m', step='month', stepmode='backward'),
                dict(count=1,  label='1a', step='year',  stepmode='backward'),
                dict(step='all', label='Tot')
            ])
        ),
        yaxis=dict(title='Seguidors/dia'),
        hovermode='x unified', height=380, showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: PUBLICACIONS
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "📊 Publicacions":
    st.title("📊 Mètriques orgàniques de publicacions")
    st.divider()

    eng_total   = metriques_dia['engagement'].mean()
    likes_total = int(metriques_dia['likes'].sum())
    views_total = int(metriques_dia['views'].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Engagement mitjà", f"{eng_total:.2f}%",
                delta="vs 0.45% sector")
    col2.metric("Likes totals",  f"{likes_total:,}")
    col3.metric("Views totals",  f"{views_total:,}")

    st.divider()

    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Scatter(
        x=metriques_dia['date'], y=metriques_dia['engagement'],
        name='Engagement (%)', line=dict(color='#1D9E75', width=1.5),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Engagement: %{y:.1f}%<extra></extra>'
    ), secondary_y=False)
    fig3.add_trace(go.Bar(
        x=metriques_dia['date'], y=metriques_dia['likes'],
        name='Likes', marker_color='rgba(74,144,217,0.4)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Likes: %{y:,.0f}<extra></extra>'
    ), secondary_y=True)
    fig3.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.05),
            rangeselector=dict(buttons=[
                dict(count=1,  label='1m', step='month', stepmode='backward'),
                dict(count=3,  label='3m', step='month', stepmode='backward'),
                dict(count=6,  label='6m', step='month', stepmode='backward'),
                dict(step='all', label='Tot')
            ])
        ),
        yaxis=dict(title='Engagement (%)'),
        yaxis2=dict(title='Likes', showgrid=False),
        hovermode='x unified', height=420,
        legend=dict(orientation='h', y=1.08)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: AUDIÈNCIA
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "👥 Audiència":
    st.title("👥 Perfil de l'audiència · Overtake.GP")
    st.caption("Font: Metricool API · instantània estàtica · maig 2026")
    st.divider()

    colors_pais = [
    '#2E86AB',  # Blau profund · Indonesia
    '#A23B72',  # Magenta fosc · Espanya
    '#F18F01',  # Ambre · França
    '#C73E1D',  # Vermell terra · Itàlia
    '#3B1F2B',  # Pruna · Brasil
    '#44BBA4',  # Verd aiguamarina · Malàisia
    '#E94F37',  # Corall · Regne Unit
    '#393E41',  # Gris antracita · Estats Units
    '#B0B0B0',  # Gris clar · Altres
]
    genere_map = {'M':'Home','F':'Dona','U':'Desconegut'}
    df_gender['label'] = df_gender['genere'].map(genere_map)
    ordre_edat = ['13-17','18-24','25-34','35-44','45-54','55-64','65+']
    df_age_ord = df_age.set_index('franja').reindex(ordre_edat).reset_index()

    # ── Fila 1: Gènere + Edat ─────────────────────────────────────────────────
    fig4a = make_subplots(
        rows=1, cols=2,
        specs=[[{"type":"pie"},{"type":"bar"}]],
        subplot_titles=['Gènere', "Franja d'edat"],
        horizontal_spacing=0.15
    )
    fig4a.add_trace(go.Pie(
        labels=df_gender['label'], values=df_gender['pct'],
        hole=0.55, marker=dict(colors=['#4A90D9','#E24B4A','#aaaaaa']),
        textinfo='percent', textposition='inside',
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
        showlegend=True, legend='legend', name='Gènere'
    ), row=1, col=1)
    fig4a.add_trace(go.Bar(
        x=df_age_ord['franja'], y=df_age_ord['pct'],
        marker=dict(color=df_age_ord['pct'],
                    colorscale=[[0,'#9FE1CB'],[1,'#1D9E75']],
                    showscale=False),
        text=df_age_ord['pct'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>',
        showlegend=False
    ), row=1, col=2)
    fig4a.update_layout(
        height=350,
        margin=dict(t=60, b=40, l=40, r=40),
        legend=dict(orientation='v', x=0.38, y=0.95, xanchor='left',
                    font=dict(size=10),
                    title=dict(text='Gènere', font=dict(size=10)))
    )
    st.plotly_chart(fig4a, use_container_width=True)

    # ── Fila 2: Països + Taula ciutats ────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        fig4b = go.Figure(go.Pie(
            labels=top_countries['nom'], values=top_countries['pct'],
            hole=0.55, marker=dict(colors=colors_pais),
            textinfo='percent', textposition='inside',
            hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
            showlegend=True, name='Països'
        ))
        fig4b.update_layout(
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            title=dict(text='Top països', font=dict(size=12)),
            legend=dict(orientation='v', x=1.02, y=0.95, font=dict(size=10))
        )
        st.plotly_chart(fig4b, use_container_width=True)

    with col2:
        st.markdown("**Top ciutats**")
        df_ciutats = df_city[['ciutat','pct']].head(12).copy()
        df_ciutats.columns = ['Ciutat', '%']
        df_ciutats['%'] = df_ciutats['%'].apply(lambda x: f'{x:.2f}%')
        st.dataframe(df_ciutats, hide_index=True,
                     use_container_width=True, height=320)


# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "📈 Benchmarking":
    st.title("📈 Benchmarking · Comparativa de creixement")
    st.caption("Comparativa d'Overtake.GP amb 6 comptes referents del sector")
    st.divider()

    colors_comptes = {
        'overtake':             '#1D9E75',
        'motorspain_77':        '#4A90D9',
        'motorsportcom':        '#E67E22',
        'moto_gp':              '#E24B4A',
        'motociclismo_es':      '#9B59B6',
        'everithingmotoracing': '#F1C40F',
        'brake_gp':             '#1ABC9C',
    }

    fig_bench = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Taxa creixement diari (mediana) · Període llarg',
            'Índex base 100 · Període llarg',
            'Taxa creixement diari (mediana) · Període curt',
            'Índex base 100 · Període curt',
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.10
    )

    resum_llarg = (
        df_llarg.groupby('account')['daily_growth_rel']
        .median().sort_values(ascending=False).reset_index()
    )
    resum_llarg['daily_growth_pct'] = resum_llarg['daily_growth_rel'] * 100

    fig_bench.add_trace(go.Bar(
        x=resum_llarg['account'],
        y=resum_llarg['daily_growth_pct'],
        marker_color=[colors_comptes.get(c, '#aaa') for c in resum_llarg['account']],
        hovertemplate='<b>%{x}</b><br>Creixement diari: %{y:.3f}%<extra></extra>',
        showlegend=False
    ), row=1, col=1)

    for compte, grup in df_llarg.groupby('account'):
        grup = grup.sort_values('date')
        base = grup['followers_count'].iloc[0]
        idx  = (grup['followers_count'] / base * 100).round(1)
        fig_bench.add_trace(go.Scatter(
            x=grup['date'], y=idx,
            name=compte,
            line=dict(color=colors_comptes.get(compte, '#aaa'), width=1.8),
            hovertemplate='<b>' + compte + '</b><br>%{x|%b %Y}<br>Índex: %{y:.1f}<br>Seguidors: %{customdata:,.0f}<extra></extra>',
            customdata=grup['followers_count'].values,
            legendgroup=compte, showlegend=True
        ), row=1, col=2)

    resum_curt = (
        df_curt.groupby('account')['daily_growth_rel']
        .median().sort_values(ascending=False).reset_index()
    )
    resum_curt['daily_growth_pct'] = resum_curt['daily_growth_rel'] * 100

    fig_bench.add_trace(go.Bar(
        x=resum_curt['account'],
        y=resum_curt['daily_growth_pct'],
        marker_color=[colors_comptes.get(c, '#aaa') for c in resum_curt['account']],
        hovertemplate='<b>%{x}</b><br>Creixement diari: %{y:.3f}%<extra></extra>',
        showlegend=False
    ), row=2, col=1)

    for compte, grup in df_curt.groupby('account'):
        grup = grup.sort_values('date')
        base = grup['followers_count'].iloc[0]
        idx  = (grup['followers_count'] / base * 100).round(1)
        fig_bench.add_trace(go.Scatter(
            x=grup['date'], y=idx,
            name=compte,
            line=dict(color=colors_comptes.get(compte, '#aaa'), width=1.8),
            hovertemplate='<b>' + compte + '</b><br>%{x|%b %Y}<br>Índex: %{y:.1f}<br>Seguidors: %{customdata:,.0f}<extra></extra>',
            customdata=grup['followers_count'].values,
            legendgroup=compte, showlegend=False
        ), row=2, col=2)

    fig_bench.update_layout(
        height=700,
        hovermode='x unified',
        legend=dict(orientation='h', y=-0.08, x=0),
        margin=dict(t=60, b=80, l=60, r=40)
    )
    fig_bench.update_yaxes(title_text='Creixement diari (%)', row=1, col=1)
    fig_bench.update_yaxes(title_text='Creixement diari (%)', row=2, col=1)
    fig_bench.update_yaxes(title_text='Índex (base 100)', row=1, col=2)
    fig_bench.update_yaxes(title_text='Índex (base 100)', row=2, col=2)

    st.plotly_chart(fig_bench, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: Rellevància dels pilots
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "🏍️ Pilots":
    st.title("🏍️ Rànquing de pilots · Overtake.GP")
    st.divider()
    graella_html = (BASE_DIR / "overtake_graella_pilots.html").read_text(encoding='utf-8')
    components.html(graella_html, height=750, scrolling=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÀGINA: METODOLOGIA
# ══════════════════════════════════════════════════════════════════════════════
elif seccio == "🔬 Metodologia":
    st.title("🔬 Metodologia i context")
    st.divider()

    st.markdown("""
    ### Sobre el projecte
    Aquest projecte forma part d'un doble àmbit acadèmic:
    - **TFG** (Grau en Comunicació i Indústries Culturals · UB) — desenvolupat per Christian Duarte
    - **Bootcamp Data Analytics** (Barcelona Activa) — desenvolupat per Jordi Lamarca

    ### Fonts de dades
    | Font | Contingut | Període |
    |------|-----------|---------|
    | **InstaTrack** | Seguiment diari de 7 comptes de motorsport | Des. 2023 → Jun. 2026 |
    | **Metricool** | 419 posts individuals d'Overtake.GP | Ago. 2025 → Jun. 2026 |
    | **Metricool API** | Instantània demogràfica de l'audiència | Maig 2026 |

    ### Eines utilitzades
    | Eina | Ús |
    |------|----|
    | **Python · pandas** | Càrrega, neteja i transformació de dades |
    | **Matplotlib · Seaborn** | Visualitzacions estàtiques |
    | **Plotly** | Visualitzacions interactives |
    | **SciPy · statsmodels** | Tests estadístics i model predictiu |
    | **Hugging Face Transformers** | NER sobre captions (dslim/bert-base-NER) |
    | **CLIP · OpenAI** | Classificació visual de posts (zero-shot) |
    | **Streamlit** | Dashboard interactiu |
    | **MySQL** | Explorat i descartat (vegeu Annex B del notebook) |

    ### Limitacions
    - Les URLs d'Instagram expiren: CLIP cobreix 130 dels 419 posts (31%)
    - Les dades demogràfiques són una instantània estàtica (maig 2026)
    - Els posts/dia abans d'agost 2025 provenen d'InstaTrack (acumulat), no de Metricool

    ### Notebook complet
    """)
    st.link_button("📓 Veure notebook a Streamlit",
                   "https://projecte-overtakegp.streamlit.app/")