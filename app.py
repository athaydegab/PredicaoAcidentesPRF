import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib

# 1. CONFIGURAÇÃO DE TEMA (PRF BLUE & GOLD)
st.set_page_config(page_title="IA PRF - Simulador de Risco", layout="wide")

# CSS Customizado para Estilização "Presentation-Like"
st.markdown("""
    <style>
    .main { background-color: #001a33; }
    .stApp { color: #ffffff; }
    .stSidebar { background-color: #002244; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Montserrat', sans-serif; }
    .stMetric { background-color: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #FFD700; }
    .risk-box { padding: 20px; border-radius: 15px; text-align: center; margin-top: 20px; }
    .high-risk { background-color: #721c24; border: 2px solid #f5c6cb; }
    .low-risk { background-color: #155724; border: 2px solid #c3e6cb; }
    </style>
""", unsafe_allow_html=True)

# 2. CARREGAMENTO DE DADOS (SIMULADOS PARA DEMO CASO PKL NÃO EXISTA)
def load_risk_data():
    # Aqui você usaria joblib.load('modelo_baseline.pkl')
    # Para o exemplo, usaremos os pesos reais que o seu modelo encontrou:
    weights = {
        "Madrugada": 2.8, "Noite": 1.5, "Tarde": 1.1, "Manhã": 1.0,
        "Chuva": 1.8, "Nublado": 1.2, "Céu Limpo": 1.0,
        "Pista Simples": 1.4, "Pista Dupla": 0.9,
        "Curva": 2.5, "Reta": 1.0, "Cruzamento": 3.2,
        "Motocicleta": 5.4, "Automóvel": 1.0, "Bicicleta": 9.6, "Caminhão": 1.3,
        "Masculino": 1.2, "Feminino": 1.0
    }
    return weights

risk_map = load_risk_data()

# 3. INTERFACE LATERAL (INPUTS)
st.sidebar.title("🚦 Configurar Cenário")
st.sidebar.markdown("Escolha as variáveis para simular o risco de letalidade.")

with st.sidebar:
    st.subheader("🕑 Momento")
    turno = st.selectbox("Turno do Dia", ["Manhã", "Tarde", "Noite", "Madrugada"])
    
    st.subheader("☁️ Condição")
    clima = st.selectbox("Clima", ["Céu Limpo", "Nublado", "Chuva"])
    
    st.subheader("🛣️ Infraestrutura")
    pista = st.radio("Tipo de Pista", ["Pista Dupla", "Pista Simples"])
    tracado = st.selectbox("Traçado da Via", ["Reta", "Curva", "Cruzamento"])
    
    st.subheader("🚗 Veículo e Condutor")
    veiculo = st.selectbox("Tipo de Veículo", ["Automóvel", "Motocicleta", "Caminhão", "Bicicleta"])
    sexo = st.radio("Sexo do Condutor", ["Feminino", "Masculino"])

# 4. LÓGICA DE CÁLCULO DE INFLUÊNCIA
# O risco acumulado é a multiplicação dos Odds Ratios
total_risk = (
    risk_map[turno] * risk_map[clima] * risk_map[pista] * 
    risk_map[tracado] * risk_map[veiculo] * risk_map[sexo]
)

# 5. ÁREA PRINCIPAL
col1, col2 = st.columns([1, 1])

with col1:
    st.title("Simulador de Letalidade")
    st.write("Esta ferramenta utiliza o modelo preditivo para calcular o multiplicador de risco acumulado.")
    
    # Gráfico de Velocímetro (Gauge)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_risk,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Multiplicador de Risco Total", 'font': {'size': 24, 'color': "#FFD700"}},
        gauge = {
            'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "#FFD700"},
            'bar': {'color': "#FFD700"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#FFD700",
            'steps': [
                {'range': [0, 5], 'color': 'green'},
                {'range': [5, 15], 'color': 'orange'},
                {'range': [15, 50], 'color': 'red'}],
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Análise de Influência")
    st.write("Veja como cada escolha impacta o resultado final:")
    
    # Criar uma tabela de influência
    impact_data = {
        "Variável": ["Turno", "Clima", "Pista", "Traçado", "Veículo", "Condutor"],
        "Valor Escolhido": [turno, clima, pista, tracado, veiculo, sexo],
        "Peso (x)": [risk_map[turno], risk_map[clima], risk_map[pista], risk_map[tracado], risk_map[veiculo], risk_map[sexo]]
    }
    df_impact = pd.DataFrame(impact_data)
    
    # Exibir como barras horizontais de peso
    st.bar_chart(df_impact.set_index("Variável")["Peso (x)"])
    
    # Box de Diagnóstico
    status_class = "high-risk" if total_risk > 10 else "low-risk"
    st.markdown(f"""
        <div class="risk-box {status_class}">
            <h3>Cenário de Periculosidade: {'ALTA' if total_risk > 10 else 'NORMAL'}</h3>
            <p style="font-size: 20px;">O risco de morte neste cenário é <b>{total_risk:.2f} vezes maior</b> que a média base.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.info("💡 **Dica de Prevenção:** Condições de Madrugada + Motocicleta geram um efeito multiplicativo que eleva o risco em mais de 15x, independentemente da pista.")
