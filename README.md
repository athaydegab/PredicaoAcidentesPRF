# Predição de Gravidade de Acidentes Rodoviários (PRF & DNIT)

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-calibrado-006600)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-pipeline%20completo-brightgreen)

Projeto de Ciência de Dados que estima a **probabilidade de um acidente de trânsito ser grave ou fatal** em rodovias federais, cruzando os microdados de acidentes da **PRF** com os índices oficiais de condição da infraestrutura do **DNIT** (ICC, ICP e ICM). O produto final é um **simulador de risco interativo em Streamlit**, movido por um modelo **XGBoost calibrado** que apresenta o medidor de risco na forma de um velocímetro e um gráfico de barras que usa odds ratio para apresentar as variáveis que mais pesam no modelo.

> **Status (jul/2026):** **pipeline completo** — dados estruturados, modelo treinado e **aplicação
> funcional**. O `app.py` (Streamlit) já serve as predições em tempo real; os notebooks reproduzem toda
> a cadeia de estruturação → normalização/*feature engineering* → modelagem.

---

## Escopo dos dados

- **Variante nacional:** o pipeline extraiu a base do site governamental INSIRA LINK AQUI e separou as top 10 rodovias brasileiras com mais dados do DNIT como amostra para o modelo, sendo elas — `364, 230, 116, 101, 158, 153, 316, 174, 242, 010`.
- **Período:** 2024–2026 (janela em que DNIT e PRF se sobrepõem).
- **Base de modelagem:** o modelo em produção foi treinado sobre a base já normalizada
  (~**216 mil registros**), com alvo binário `acidente_grave_ou_fatal`.

## Tecnologias

- **Linguagem:** Python 3.x
- **Manipulação de dados:** pandas, numpy, openpyxl
- **Coleta/download:** kagglehub, requests
- **Machine Learning:** scikit-learn, **XGBoost** (modelo final, calibrado), lightgbm, **Optuna** (tuning)
- **Persistência de modelo:** joblib
- **Visualização:** matplotlib, seaborn, **plotly**
- **Aplicação/Deploy:** Streamlit
- **Ambiente:** Jupyter Notebooks + Dev Container (`.devcontainer/`)

## Estrutura do Repositório

```
├── .devcontainer/                 # Ambiente reproduzível (GitHub Codespaces / Dev Container)
├── .streamlit/                    # Configuração do app Streamlit (tema/config)
├── data/
│   ├── raw/                       # Brutos: DNIT + PRF (ignorados pelo Git)
│   └── processed/                 # Bases estruturadas/normalizadas (ignoradas pelo Git)
├── models/                        # Artefatos treinados (usados pelo app)
│   ├── modelo_xgboost_calibrado.pkl
│   └── colunas_treino.pkl
├── notebooks/                     # Pipeline numerado: estruturação → normalização → modelagem
│   └── 02_notebook_normalizacao.ipynb   # (confirmado — ver nota abaixo)
├── src/
│   └── preparar_dados.py          # Constantes/funções compartilhadas (COLUNAS_TRACADO, TOKENS_TRACADO)
├── .gitignore
├── app.py                         # Aplicação Streamlit — Simulador de Risco
├── requirements.txt
└── README.md
```

Por conterem dados brutos governamentais pesados, todos os `.csv` são ignorados pelo Git; apenas a
estrutura de pastas é preservada.

> **Nota:** confirme os nomes exatos dos demais notebooks em `notebooks/` (a numeração indica um pipeline
> sequencial; apenas `02_notebook_normalizacao.ipynb` foi verificado aqui).

## Origem dos dados

- **DNIT (ICC/ICP/ICM):** consolidado em `data/raw/` a partir dos levantamentos de condição das rodovias.
  O download em lote falha (o servidor do DNIT derruba arquivos grandes), por isso os brutos são baixados
  pelo navegador antes da consolidação.
- **PRF (acidentes):** Dados Abertos nacionais (formato *datatran* / agrupados por pessoa), 2024–2026,
  obtidos programaticamente via `kagglehub`/`requests` para `data/raw/`.

## Como Executar

```bash
# 1. Ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt
```

**Rodar o simulador (recomendado):** requer os artefatos em `models/` (`modelo_xgboost_calibrado.pkl` e
`colunas_treino.pkl`).

```bash
streamlit run app.py
```

**Reproduzir o pipeline do zero:** garanta os brutos em `data/raw/` e execute os notebooks em ordem
numérica (estruturação → normalização → modelagem), que regeram as bases em `data/processed/` e os
artefatos em `models/`.

```bash
jupyter notebook
```

## O modelo e o simulador

O `app.py` carrega o XGBoost calibrado e expõe um **Simulador de Risco**: o usuário monta um cenário e
recebe a probabilidade estimada de o acidente ser grave/fatal, além do peso relativo (odds ratio marginal)
de cada escolha.

- **Alvo:** `acidente_grave_ou_fatal` (binário).
- **Taxa base real na base de treino:** ~**12,98%** (referência para classificar o risco em Baixo /
  Moderado / Alto).
- **Algoritmo:** XGBoost com calibração de probabilidade; ajuste de hiperparâmetros com Optuna.
- **Variáveis expostas no simulador:** turno, clima, tipo de pista, traçado da via
  (formato / inclinação / elementos especiais), tipo de veículo e sexo do condutor.
- **Variáveis não expostas** (BR, sentido da via, dia da semana, uso do solo e os índices de conservação
  ICC/ICP/ICM) permanecem na condição de referência/média.

## O que os notebooks fazem (estruturação)

| Etapa | Saída |
| --- | --- |
| **0** — Configuração (recorte, top 10 BRs, janela 2024–2026) | — |
| **1** — DNIT: filtra → top 10 BRs → remove colunas inúteis → deduplica cada trecho pela avaliação mais recente | `data/processed/dnit_estruturado.csv` |
| **2** — PRF: baixa nacional, filtra recorte + mesmas BRs + mesmo período | `data/processed/prf_estruturado.csv` |
| **3** — Cruzamento: cada acidente recebe o ICM do trecho (`uf + br + km`) | `data/processed/base_modelagem.csv` |

Resultado do recorte Norte: **~20 mil trechos** (DNIT) e **~21 mil acidentes** (PRF), com **~95% dos
acidentes** casados ao ICM do trecho.

## Variante Brasil

Mesma estruturação, mas com **escopo nacional**: remove o filtro de UF (todas as 27 UFs) e recalcula o
Top 10 BRs a nível Brasil. Gera arquivos **paralelos** (`*_brasil.csv`), preservando as bases do Norte, com
o **mesmo schema**, de modo que a análise roda apenas trocando o caminho do CSV.

Resultado: **~44 mil trechos** (DNIT) e **~209 mil acidentes** (PRF).

> **Cobertura de ICM menor no Brasil:** ~**45%** dos acidentes casam com o ICM do trecho (contra ~95%
> no Norte). O volume nacional concentra-se em BR-101 e BR-116, onde a avaliação do DNIT é desigual entre
> UFs. Análises/modelos que dependem do ICM devem tratar os ~55% de linhas com `icm`/`icc`/`icp` ausentes
> (dropna, imputação ou recorte por BRs bem cobertas).

## Próximos passos / melhorias

1. Interpretabilidade do modelo (ex.: SHAP) e validação de calibração.
2. Documentar e fixar a **escala do ICM** (ver observação abaixo) antes de conclusões definitivas.
3. Ampliar cobertura de testes e reprodutibilidade do pipeline.
4. Publicação do app (Streamlit Community Cloud ou similar).

> **Escala do ICM a confirmar:** há divergência entre fontes sobre a direção do índice (maior = melhor
> × maior = pior). Os valores são mantidos como no original; a interpretação deve ser fixada antes de
> concluir o modelo.

---

**Fonte dos dados:** <https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf>
