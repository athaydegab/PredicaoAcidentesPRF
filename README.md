# 🚦 Predição de Gravidade de Acidentes Rodoviários (PRF & DNIT)

Projeto de Ciência de Dados que investiga a gravidade de acidentes nas rodovias federais
da **região Norte**, cruzando os dados de acidentes da **PRF** com os índices oficiais de
condição da infraestrutura do **DNIT** (ICC, ICP e ICM).

> **Status (jun/2026):** **estruturação de dados concluída**. As bases de DNIT e PRF já
> estão limpas, filtradas e cruzadas, prontas para análise exploratória e modelagem.
> A análise exploratória, os modelos preditivos e o deploy (Streamlit) são as próximas etapas.

## 🎯 Escopo dos dados

* **Região:** Norte (AC, AM, AP, PA, RO, RR, TO).
* **Recorte:** as **10 BRs com mais registros** na região — `364, 230, 174, 010, 153, 156,
  317, 319, 242, 155`.
* **Período:** 2024–2026 (janela em que DNIT e PRF se sobrepõem).

## 🛠️ Tecnologias

* **Python 3.x** — Pandas, NumPy
* **Machine Learning:** Scikit-Learn
* **Visualização:** Matplotlib, Seaborn
* **Ambiente:** Jupyter Notebooks

## 📁 Estrutura do Repositório

```text
├── data/
│   ├── raw/             # Brutos: dnit_consolidado.csv + acidentes{ano}.csv (ignorados pelo Git)
│   └── processed/       # Bases estruturadas geradas pelo notebook (ignorados pelo Git)
├── notebooks/
│   ├── notebook_completo.ipynb   # Estruturação (DNIT + PRF) — recorte região Norte
│   └── notebook_brasil.ipynb     # Mesma estruturação — recorte Brasil inteiro (todas as UFs)
├── .gitignore
├── requirements.txt
└── README.md
```

Por conterem dados brutos governamentais pesados, todos os `.csv` são ignorados pelo Git;
apenas a estrutura de pastas sobe via `.gitkeep`.

## 🗂️ Origem dos dados

* **DNIT (ICM):** consolidado em `data/raw/dnit_consolidado.csv` a partir dos levantamentos
  de condição das rodovias. O download em lote falha (o servidor do DNIT derruba arquivos
  grandes), por isso os brutos são baixados pelo navegador antes da consolidação.
* **PRF (acidentes):** Dados Abertos nacionais (formato *datatran* / agrupados por pessoa),
  2024–2026. O próprio notebook **baixa automaticamente** via `gdown` para `data/raw/`.

## ▶️ Como Executar

```bash
# 1. Ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt

# 3. Garantir o dnit_consolidado.csv em data/raw/
#    (a PRF é baixada automaticamente pelo notebook)

# 4. Rodar o notebook em ordem
jupyter notebook notebooks/notebook_completo.ipynb
```

## ✅ O que o notebook faz (estruturação)

| Etapa | Saída |
|------|-------|
| **0** — Configuração (Norte, top 10 BRs, janela 2024–2026) | — |
| **1** — DNIT: filtra Norte → top 10 BRs (por nº de linhas) → remove colunas inúteis (lat/long/obs/mês) → deduplica cada trecho pela avaliação mais recente | `data/processed/dnit_estruturado.csv` |
| **2** — PRF: baixa nacional, filtra Norte + mesmas 10 BRs + mesmo período | `data/processed/prf_estruturado.csv` |
| **3** — Cruzamento: cada acidente recebe o ICM do trecho (`uf + br + km`) | `data/processed/base_modelagem.csv` |

Resultado: **~20 mil trechos** (DNIT) e **~21 mil acidentes** (PRF), com **~95% dos
acidentes** casados ao ICM do trecho.

## 🇧🇷 Variante Brasil (`notebook_brasil.ipynb`)

Mesma estruturação do `notebook_completo`, mas com **escopo nacional**: remove o filtro de UF
(todas as 27 UFs) e recalcula o **Top 10 BRs a nível Brasil** — `364, 230, 116, 101, 158,
153, 316, 174, 242, 010`. Gera arquivos **paralelos** (`*_brasil.csv`), preservando as bases
do Norte. O `base_modelagem_brasil.csv` tem o **mesmo schema** (38 colunas, mesma ordem) do
`base_modelagem.csv`, então a análise exploratória feita sobre o Norte roda **só trocando o
caminho do CSV**.

Resultado: **~44 mil trechos** (DNIT) e **~209 mil acidentes** (PRF).

> ⚠️ **Cobertura de ICM menor no Brasil:** ~**45%** dos acidentes casam com o ICM do trecho
> (contra ~95% no Norte). O volume nacional concentra-se em BR-101 e BR-116, onde a avaliação
> do DNIT é desigual entre UFs. Análises/modelos que dependem do ICM devem tratar os ~55% de
> linhas com `icm`/`icc`/`icp` ausentes (dropna, imputação ou recorte por BRs bem cobertas).

## 📋 Próximas etapas

1. Análise exploratória sobre as bases estruturadas.
2. Definição do alvo (gravidade/feridos/mortos) e *feature engineering* adicional.
3. Treinamento e avaliação dos modelos preditivos.
4. Deploy via **Streamlit**.

> ⚠️ **Escala do ICM a confirmar:** há divergência entre fontes sobre a direção do índice
> (maior = melhor × maior = pior). Os valores são mantidos como no original; a interpretação
> deve ser fixada antes de concluir o modelo.
