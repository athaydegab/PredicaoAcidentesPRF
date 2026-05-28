# 🚦 Predição de Gravidade de Acidentes Rodoviários (PRF & DNIT)

Este projeto de Ciência de Dados e Machine Learning tem como objetivo analisar e prever a gravidade de acidentes de trânsito nas rodovias federais do estado do Pará. O grande diferencial desta modelagem é o cruzamento espacial dos dados de acidentes (PRF) com os índices oficiais de qualidade da infraestrutura rodoviária (DNIT), provando matematicamente o impacto da conservação do asfalto na segurança viária.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Manipulação de Dados:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn
* **Visualização:** Matplotlib, Seaborn, streamlit
* **Ambiente:** Jupyter Notebooks

## 📁 Estrutura do Repositório

Para garantir a organização e a segurança dos dados brutos governamentais, o projeto adota a seguinte arquitetura de diretórios:

```text
├── data/
│   ├── raw/             # Dados originais da PRF e DNIT (CSVs ignorados pelo Git)
│   └── processed/       # Bases limpas e fundidas geradas pelos notebooks (ignorados pelo Git)
├── notebooks/
│   ├── 01_limpeza_prf.ipynb           # Padronização e tratamento de outliers da PRF
│   ├── 02_limpeza_dnit.ipynb          # Imputação de séries temporais na infraestrutura
│   ├── 03_feature_engineering.ipynb   # Merge espacial, One-Hot Encoding e Scaling
│   └── 04_modelagem.ipynb             # (Em desenvolvimento) Treinamento dos modelos preditivos
├── .gitignore           # Oculta o ambiente virtual e arquivos pesados
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação principal
