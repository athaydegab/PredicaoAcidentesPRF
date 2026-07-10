# Predição de Gravidade de Acidentes Rodoviários (PRF & DNIT)

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-calibrado-006600)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-pipeline%20completo-brightgreen)

Projeto de Ciência de Dados que estima a **probabilidade de um acidente de trânsito ser grave ou fatal** em rodovias federais, cruzando os microdados de acidentes da **PRF** com os índices oficiais de condição da infraestrutura do **DNIT** (ICC, ICP e ICM). O produto final é um **simulador de risco interativo em Streamlit**, movido por um modelo **XGBoost calibrado** que apresenta o risco como um velocímetro de probabilidade e um gráfico de barras com o odds ratio marginal de cada variável escolhida.

> **Status (jul/2026):** pipeline completo — dados estruturados, 4 modelos treinados e comparados, e
> **aplicação funcional** publicada no Streamlit Community Cloud. O `app.py` serve as predições em tempo
> real a partir do modelo vencedor (XGBoost); os notebooks reproduzem toda a cadeia de estruturação →
> normalização/AED → modelagem → comparação final.

---

## Escopo dos dados

- **Escopo nacional:** o pipeline consolida a base de todo o Brasil e recorta as **10 rodovias federais**
  com mais dados de condição de pista no DNIT — `101, 116, 153, 158, 174, 230, 242, 316, 364, 10`.
- **Período:** 2024–2026 (janela em que DNIT e PRF se sobrepõem).
- **Base de modelagem:** ~**216.734 registros** (granularidade por pessoa/veículo envolvido em cada
  acidente), com alvo binário `acidente_grave_ou_fatal` (**~13,0%** de casos positivos).

## Tecnologias

- **Linguagem:** Python 3.x
- **Manipulação de dados:** pandas, numpy, openpyxl
- **Coleta/download:** kagglehub (DNIT), gdown (PRF)
- **Machine Learning:** scikit-learn (Regressão Logística, Random Forest, calibração), **XGBoost**
  (modelo final), lightgbm
- **Persistência de modelo:** joblib
- **Visualização:** matplotlib, seaborn, **plotly**
- **Aplicação/Deploy:** Streamlit (Community Cloud)
- **Ambiente:** Jupyter Notebooks + Dev Container (`.devcontainer/`)

## Estrutura do Repositório

```
├── .devcontainer/                 # Ambiente reproduzível (GitHub Codespaces / Dev Container)
├── .streamlit/                    # Tema do app (config.toml — sidebar com contraste próprio)
├── data/
│   ├── raw/                       # Brutos: DNIT + PRF (ignorados pelo Git)
│   └── processed/                 # Bases estruturadas/normalizadas (ignoradas pelo Git)
├── models/                        # Artefatos treinados (a maioria ignorada pelo Git — só os 2
│   │                               # usados pelo app.py em produção são versionados)
│   ├── modelo_xgboost_calibrado.pkl   # modelo final (rastreado no Git)
│   └── colunas_treino.pkl             # ordem/nome das 77 features (rastreado no Git)
├── notebooks/
│   ├── 01_notebook_brasil.ipynb        # Estruturação: baixa/cruza DNIT + PRF por uf+br+km
│   ├── 02_notebook_normalizacao.ipynb  # Nulos, outliers (capping IQR), variável alvo, top 10 BRs
│   ├── 03_notebook_aed.ipynb           # Análise exploratória + decomposição do traçado multi-rótulo
│   ├── 04_notebook_baselinemodel.ipynb # Modelo 1/4: Regressão Logística
│   ├── 05_notebook_random_forest.ipynb # Modelo 2/4: Random Forest
│   ├── 06_notebook_xgboost.ipynb       # Modelo 3/4: XGBoost (vencedor) + calibração de probabilidade
│   ├── 07_notebook_lightgbm.ipynb      # Modelo 4/4: LightGBM
│   ├── 08_notebook_comparativo.ipynb   # Compara os 4 modelos + taxa base de referência
│   └── archive/                        # Versões anteriores/descontinuadas (região Norte, modelos antigos)
├── src/
│   └── preparar_dados.py          # Feature engineering + split compartilhado pelos notebooks 04-08
├── .gitignore
├── app.py                         # Aplicação Streamlit — Simulador de Risco
├── requirements.txt
└── README.md
```

Por conterem dados brutos governamentais pesados, todos os `.csv` são ignorados pelo Git; apenas a
estrutura de pastas é preservada. Da mesma forma, `models/*.pkl` é ignorado por padrão — apenas os 2
artefatos que o `app.py` carrega em produção têm exceção aberta no `.gitignore`, para o Streamlit Cloud
conseguir clonar e rodar o app sem precisar retreinar nada.

## Origem dos dados

- **DNIT (ICC/ICP/ICM):** consolidado a partir dos levantamentos de condição das rodovias; o notebook 01
  usa um arquivo local se disponível ou baixa automaticamente do Kaggle (`lucasandroliveira/dnit-prf-norte`)
  como fallback.
- **PRF (acidentes):** Dados Abertos oficiais da PRF (2024–2026), espelhados no Google Drive e baixados
  programaticamente pelo notebook 01 (`gdown`) para maior confiabilidade — o servidor oficial derruba
  downloads grandes com frequência.

## Como Executar

```bash
# 1. Ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt
```

**Rodar o simulador (recomendado):** requer os artefatos em `models/` (`modelo_xgboost_calibrado.pkl` e
`colunas_treino.pkl`, já versionados no repositório).

```bash
streamlit run app.py
```

**Reproduzir o pipeline do zero:** garanta os brutos em `data/raw/` e execute os notebooks em ordem
numérica (01 → 08), que regeram as bases em `data/processed/` e os artefatos em `models/`.

```bash
jupyter notebook
```

## O pipeline de modelagem

| Notebook | O que faz |
| --- | --- |
| **01** — Estruturação | Baixa DNIT + PRF, recorta as 10 BRs de maior cobertura, cruza cada acidente com o ICM/ICC/ICP do trecho (`uf+br+km`) |
| **02** — Normalização | Trata nulos (mediana/"Não Informado"), interpola ICM/ICC/ICP espacialmente, cria a variável alvo `acidente_grave_ou_fatal`, remove colunas de vazamento (contagem de vítimas) |
| **03** — AED | Investiga periculosidade por BR e relação ICM×severidade; decompõe `tracado_via` (multi-rótulo, ex. `"Curva;Declive"`) em 12 flags binárias |
| **04-07** — Modelagem | Um modelo por notebook (Regressão Logística, Random Forest, XGBoost, LightGBM), todos sobre a mesma base via `src/preparar_dados.py`: split **agrupado por acidente** (`GroupShuffleSplit`, evita vazamento entre envolvidos do mesmo acidente), tuning de hiperparâmetros (`RandomizedSearchCV` otimizando PR-AUC) e limiar de decisão calibrado para recall ≥ 75% |
| **08** — Comparativo | Reúne os 4 resultados + uma linha de **Taxa Base (Aleatório)** como referência de "puro acaso", para deixar explícito o ganho real de cada modelo sobre a taxa de 13% |

O **XGBoost** (notebook 06) é o modelo usado em produção: além do treino e tuning, esse notebook também
recalibra a probabilidade prevista com `CalibratedClassifierCV` (Platt scaling), porque o `scale_pos_weight`
usado para compensar o desbalanceamento de classes distorce a probabilidade bruta (média de ~38% no teste
contra uma taxa real de ~13%) — a calibração não muda o poder discriminativo do modelo (AUC idêntico),
só a escala da probabilidade exibida ao usuário.

### Resultado final (notebook 08)

| Algoritmo | Accuracy | Precision | Recall | AUC |
| --- | --- | --- | --- | --- |
| Regressão Logística | 69,3% | 26,3% | 75,1% | **0,799** |
| **XGBoost (produção)** | **69,8%** | **26,6%** | 75,0% | 0,798 |
| LightGBM | 69,0% | 26,1% | 75,0% | 0,792 |
| Random Forest | 68,8% | 25,9% | 75,0% | 0,790 |
| Taxa Base (Aleatório) | 77,4% | 13,0% | 13,0% | 0,500 |

Os 4 modelos ficam praticamente empatados em capacidade discriminativa (AUC); XGBoost foi escolhido por
ter a melhor precisão/acurácia entre os individuais e treinar bem mais rápido que Regressão Logística e
Random Forest. A acurácia da Taxa Base (77,4%) ser maior que a dos modelos reais é esperado — é o
["paradoxo da acurácia"](https://en.wikipedia.org/wiki/Accuracy_paradox): o acaso nunca arrisca capturar
os 13% de casos graves, então "acerta" por inércia; os modelos reais sacrificam acurácia de propósito
para atingir 75% de recall na classe que realmente importa.

## O modelo e o simulador

O `app.py` carrega o XGBoost calibrado e expõe um **Simulador de Risco**: o usuário monta um cenário e
recebe a probabilidade estimada de o acidente ser grave/fatal, além do peso relativo (odds ratio marginal)
de cada escolha.

- **Alvo:** `acidente_grave_ou_fatal` (binário).
- **Taxa base real na base de treino:** ~**12,98%** (referência para classificar o risco em Baixo /
  Moderado / Alto).
- **Variáveis expostas no simulador:** turno, clima, tipo de pista, traçado da via (formato Reta/Curva e
  inclinação Aclive/Declive são mutuamente exclusivos por definição — nunca coexistem nos dados reais —,
  enquanto os demais elementos do traçado, como interseção, rotatória e ponte, podem ser combinados
  livremente), tipo de veículo e sexo do condutor.
- **Variáveis não expostas** (BR, sentido da via, dia da semana, uso do solo e os índices de conservação
  ICC/ICP/ICM) permanecem na condição de referência/média.

## Limitações conhecidas

- **Precisão limitada pelo desbalanceamento de classes:** a ~75% de recall, a precisão do melhor modelo
  é ~26,6% (isto é, ~3 em 4 alertas de "grave" são falso alarme). Isso não é um defeito pontual do
  XGBoost — testamos busca de hiperparâmetros mais sofisticada (Optuna, 60 trials), threshold por
  segmento de veículo e features adicionais já existentes na base (`idade`, `ano_fabricacao_veiculo`), e
  nenhuma alternativa superou o modelo atual. O teto de precisão é estrutural: dado que só ~13% dos casos
  são graves, capturar 75% deles exige sinalizar um volume grande de casos, boa parte falso positivo.
- **Motocicletas concentram a maior parte da imprecisão:** ~56% de todas as previsões de "grave" são
  cenários de moto, e é exatamente aí que o modelo menos consegue melhorar sobre a taxa base do próprio
  grupo (25,8% → 27,2%, um ganho quase nulo) — as variáveis disponíveis (clima, horário, traçado) não
  carregam sinal suficiente para diferenciar quais acidentes de moto serão graves. Dados comportamentais
  no momento do acidente (velocidade, uso de capacete) resolveriam isso, mas não estão disponíveis na
  base atual.
- **Escala do ICM a confirmar:** há divergência entre fontes sobre a direção do índice (maior = melhor
  × maior = pior); além disso, a correlação linear de ICM/ICC/ICP com a gravidade é praticamente nula
  (Pearson ≈ 0), então essas variáveis contribuem pouco ao modelo apesar de serem índices de qualidade
  da via.

## Próximos passos / melhorias

1. Coletar ou incorporar variáveis comportamentais (velocidade, uso de EPI) para melhorar a precisão
   especificamente no segmento de motocicletas, hoje o maior gargalo do modelo.
2. Interpretabilidade mais profunda (SHAP) complementando a permutation importance já usada.
3. Ampliar cobertura de testes automatizados do `app.py` e do pipeline de dados.
4. Fixar definitivamente a direção da escala do ICM junto à fonte DNIT.

---

**Fonte dos dados:** <https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf>
