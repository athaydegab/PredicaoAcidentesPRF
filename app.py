import joblib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.preparar_dados import COLUNAS_TRACADO, TOKENS_TRACADO

st.set_page_config(page_title="IA PRF - Simulador de Risco", layout="wide", page_icon=":material/traffic:")

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
SURFACE_CARD = "#fcfcfb"
GRIDLINE = "#e1e0d9"
BORDER = "rgba(11,11,11,0.10)"

STATUS_GOOD = "#0ca30c"
STATUS_WARNING = "#fab219"
STATUS_CRITICAL = "#d03b3b"
STATUS_COLOR = {"good": STATUS_GOOD, "warning": STATUS_WARNING, "critical": STATUS_CRITICAL}

CATEGORY_COLORS = {
    "Turno": "#2a78d6",
    "Clima": "#1baf7a",
    "Pista": "#eda100",
    "Traçado": "#008300",
    "Veículo": "#4a3aa7",
    "Sexo": "#e34948",
}

# Taxa real de acidente_grave_ou_fatal na base de treino (02_notebook_normalizacao.ipynb).
BASE_RATE_REAL = 0.1298

TURNO_OPTIONS = ["Madrugada", "Manhã", "Tarde", "Noite"]
CLIMA_OPTIONS = ["Chuva", "Céu Claro", "Nublado", "Garoa/Chuvisco", "Nevoeiro/Neblina"]
PISTA_OPTIONS = ["Pista Dupla", "Pista Simples", "Pista Múltipla"]
PISTA_SUFIXO = {"Pista Simples": "Simples", "Pista Múltipla": "Múltipla"}
VEICULO_OPTIONS = ["Automóvel", "Motocicleta", "Bicicleta", "Caminhão"]
SEXO_OPTIONS = ["Feminino", "Masculino"]

# tracado_via no dado real é multi-rótulo (ex: "Curva;Declive"), mas "Reta"+"Curva" e
# "Aclive"+"Declive" nunca coexistem em nenhum dos 216.734 registros (são estados
# mutuamente exclusivos por definição - um trecho não é reto E curvo ao mesmo tempo).
# Os demais 8 rótulos combinam livremente entre si e com formato/inclinação, então
# ficam como seleção múltipla independente.
FORMATO_OPTIONS = ["Reta", "Curva"]
INCLINACAO_OPTIONS = ["Sem inclinação", "Aclive", "Declive"]
ESPECIAIS_OPTIONS = [
    t for t in TOKENS_TRACADO if t not in FORMATO_OPTIONS and t not in ("Aclive", "Declive")
]

# fase_dia é um campo do dataset PRF distinto de turno (turno é derivado do horário; fase_dia
# vem pronto na base). Como o simulador só expõe turno, assume-se a fase_dia mais correlata.
FASE_DIA_POR_TURNO = {"Madrugada": "Plena Noite", "Manhã": None, "Tarde": "Pleno dia", "Noite": "Anoitecer"}

TOKEN_TO_COLUNA = dict(zip(TOKENS_TRACADO, COLUNAS_TRACADO))


@st.cache_resource
def carregar_modelo():
    modelo = joblib.load("models/modelo_xgboost_calibrado.pkl")
    colunas = joblib.load("models/colunas_treino.pkl")
    return modelo, colunas


def montar_vetor(colunas_ativas, colunas_modelo):
    linha = {col: 0 for col in colunas_modelo}
    for col in colunas_ativas:
        if col in linha:
            linha[col] = 1
    return pd.DataFrame([linha])[colunas_modelo]


def classify_risco(p, base=BASE_RATE_REAL):
    if p < base:
        return "Baixo", "good"
    if p < 2 * base:
        return "Moderado", "warning"
    return "Alto", "critical"


st.markdown(f"""
    <style>
    .subtitle {{ color: {INK_SECONDARY}; font-size: 15px; margin-top: -6px; }}
    .risk-box {{ padding: 20px 24px; border-radius: 12px; border: 1px solid {BORDER}; background-color: {SURFACE_CARD}; }}
    </style>
""", unsafe_allow_html=True)

modelo, colunas_modelo = carregar_modelo()

st.markdown("## :material/monitoring: Simulador de Risco de Acidentes de Trânsito")
st.markdown(
    '<p class="subtitle">Probabilidade estimada por XGBoost (calibrado) treinado na base PRF+DNIT — '
    'cada escolha no menu lateral altera a chance de o acidente ser grave ou fatal.</p>',
    unsafe_allow_html=True,
)

st.sidebar.title(":material/filter_alt: Filtros")
st.sidebar.markdown("Escolha as variáveis para simular o risco de letalidade.")

with st.sidebar:
    st.subheader(":material/schedule: Momento")
    turno = st.selectbox("Turno do Dia", TURNO_OPTIONS)

    st.subheader(":material/cloud: Condição")
    clima = st.selectbox("Clima", CLIMA_OPTIONS)

    st.subheader(":material/road: Infraestrutura")
    pista = st.radio("Tipo de Pista", PISTA_OPTIONS)
    formato = st.radio("Formato da Via", FORMATO_OPTIONS)
    inclinacao = st.radio("Inclinação", INCLINACAO_OPTIONS)
    especiais = st.multiselect("Elementos Especiais (opcional)", ESPECIAIS_OPTIONS)

    st.subheader(":material/directions_car: Veículo e Condutor")
    veiculo = st.selectbox("Tipo de Veículo", VEICULO_OPTIONS)
    sexo = st.radio("Sexo do Condutor", SEXO_OPTIONS)

tracado_colunas = (
    [TOKEN_TO_COLUNA[formato]]
    + ([TOKEN_TO_COLUNA[inclinacao]] if inclinacao != "Sem inclinação" else [])
    + [TOKEN_TO_COLUNA[e] for e in especiais]
)

grupos_ativos = {
    "Turno": (
        ([f"turno_{turno}"] if turno != "Madrugada" else [])
        + ([f"fase_dia_{FASE_DIA_POR_TURNO[turno]}"] if FASE_DIA_POR_TURNO[turno] else [])
    ),
    "Clima": [f"condicao_metereologica_{clima}"] if clima != "Chuva" else [],
    "Pista": [f"tipo_pista_{PISTA_SUFIXO[pista]}"] if pista in PISTA_SUFIXO else [],
    "Traçado": tracado_colunas,
    "Veículo": [f"tipo_veiculo_{veiculo}"] if veiculo != "Automóvel" else [],
    "Sexo": [f"sexo_{sexo}"] if sexo != "Feminino" else [],
}

todas_colunas_ativas = [col for cols in grupos_ativos.values() for col in cols]
vetor_completo = montar_vetor(todas_colunas_ativas, colunas_modelo)
vetor_base = montar_vetor([], colunas_modelo)

probabilidade = modelo.predict_proba(vetor_completo)[:, 1][0]
prob_base = modelo.predict_proba(vetor_base)[:, 1][0]
odds_base = prob_base / (1 - prob_base)

danger_label, danger_status = classify_risco(probabilidade)
status_color = STATUS_COLOR[danger_status]

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader(":material/traffic: Nível de Periculosidade")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probabilidade * 100,
        number={"suffix": "%", "font": {"size": 36, "color": INK_PRIMARY}},
        title={"text": "Probabilidade de Acidente Grave/Fatal", "font": {"size": 14, "color": INK_SECONDARY}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": INK_MUTED},
            "bar": {"color": INK_PRIMARY},
            "bgcolor": SURFACE_CARD,
            "borderwidth": 1,
            "bordercolor": BORDER,
            "steps": [
                {"range": [0, BASE_RATE_REAL * 100], "color": "rgba(12,163,12,0.18)"},
                {"range": [BASE_RATE_REAL * 100, 2 * BASE_RATE_REAL * 100], "color": "rgba(250,178,25,0.22)"},
                {"range": [2 * BASE_RATE_REAL * 100, 100], "color": "rgba(208,59,59,0.18)"},
            ],
            "threshold": {"line": {"color": status_color, "width": 3}, "value": probabilidade * 100},
        },
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=50, b=10))
    st.plotly_chart(fig_gauge, width="stretch")

    
    st.markdown(f"""
        <div class="risk-box" style="border-left: 6px solid {status_color};">
            <h3 style="margin:0;"> Periculosidade {danger_label.upper()}</h3>
            <p style="font-size: 15px; color:{INK_SECONDARY}; margin-top:8px;">
                A probabilidade estimada de acidente grave ou fatal neste cenário é de
                <b style="color:{INK_PRIMARY}">{probabilidade:.1%}</b>, frente a uma taxa média de
                <b style="color:{INK_PRIMARY}">{BASE_RATE_REAL:.1%}</b> na base de dados.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader(":material/balance: Como cada escolha pesa no algoritmo")
    tracado_label = formato
    if inclinacao != "Sem inclinação":
        tracado_label += f" + {inclinacao}"
    if especiais:
        tracado_label += " + " + " + ".join(especiais)

    labels_selecionadas = {
        "Turno": turno, "Clima": clima, "Pista": pista,
        "Traçado": tracado_label,
        "Veículo": veiculo, "Sexo": sexo,
    }

    # Peso = odds ratio marginal: para cada categoria, mede o quanto a probabilidade
    # muda quando só ELA sai da referência (as demais permanecem no valor de referência),
    # convertida para razão de chances (odds) em relação ao cenário totalmente neutro.
    # Diferente da Regressão Logística (coeficientes fixos e aditivos), o XGBoost captura
    # interações não-lineares entre variáveis - por isso o efeito de cada categoria aqui é
    # medido isoladamente; o resultado final (velocímetro) usa todas as escolhas juntas,
    # que pode ser diferente do produto desses pesos individuais.
    pesos = {}
    for cat, cols in grupos_ativos.items():
        if not cols:
            pesos[cat] = 1.0
            continue
        p = modelo.predict_proba(montar_vetor(cols, colunas_modelo))[:, 1][0]
        odds = p / (1 - p)
        pesos[cat] = odds / odds_base

    ordem = sorted(pesos, key=lambda cat: pesos[cat])
    labels = [f"{labels_selecionadas[cat]} ({cat})" for cat in ordem]
    valores = [pesos[cat] for cat in ordem]
    cores = [CATEGORY_COLORS[cat] for cat in ordem]

    fig_bar = go.Figure(go.Bar(
        x=valores, y=labels, orientation="h",
        marker_color=cores,
        text=[f"{v:.2f}x" for v in valores], textposition="outside",
    ))
    fig_bar.add_vline(x=1.0, line_dash="dash", line_color=INK_MUTED,
                       annotation_text="Neutro (1.0x)", annotation_position="top")
    fig_bar.update_layout(
        height=380,
        xaxis=dict(title="Odds ratio marginal (peso no modelo)", gridcolor=GRIDLINE, color=INK_MUTED,
                    range=[0, max(valores + [1.0]) * 1.25]),
        yaxis=dict(color=INK_PRIMARY),
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, width="stretch")

    st.caption(
        "Pesos = odds ratio marginal do modelo XGBoost calibrado (`models/modelo_xgboost_calibrado.pkl`), "
        "medido isolando cada categoria contra o cenário de referência.  "
        "Variáveis não expostas aqui (BR, sentido da via, dia da semana, uso do solo, índices de conservação da via) ficam na condição de referência/média."
    )
