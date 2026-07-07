"""Preparação de dados compartilhada pelos notebooks de modelagem (04-07).

Centraliza a engenharia de atributos, o encoding e o split treino/teste
para que os 4 modelos comparados (Regressão Logística, Random Forest,
XGBoost e LightGBM) sejam treinados exatamente sobre a mesma base.
"""
import re
import unicodedata

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.preprocessing import StandardScaler

CAMINHO_PADRAO = '../data/processed/data_model/dados_model.csv'

# tracado_via é um campo multi-rótulo (ex: "Reta;Declive") em que a ordem dos
# tokens varia entre registros do mesmo tipo de trecho (ex: "Reta;Declive" e
# "Declive;Reta" aparecem como categorias distintas). Decompor em uma flag
# binária por característica evita fragmentar ~680 categorias de one-hot
# encoding em combinações que, na prática, representam o mesmo trecho.
TOKENS_TRACADO = [
    'Reta', 'Curva', 'Aclive', 'Declive', 'Interseção de Vias', 'Rotatória',
    'Ponte', 'Viaduto', 'Túnel', 'Em Obras', 'Desvio Temporário',
    'Retorno Regulamentado',
]

VARIAVEIS_CATEGORICAS = [
    'turno', 'condicao_metereologica', 'fase_dia', 'br',
    'tipo_pista', 'sentido_via', 'tipo_veiculo', 'sexo', 'dia_semana', 'uso_solo',
]

VARIAVEIS_NUMERICAS = ['icm', 'icc', 'icp']


def _slugify(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]+', '_', texto).strip('_').lower()


COLUNAS_TRACADO = [f'tracado_{_slugify(t)}' for t in TOKENS_TRACADO]


def _categorizar_turno(hora):
    if 0 <= hora < 6:
        return 'Madrugada'
    if 6 <= hora < 12:
        return 'Manhã'
    if 12 <= hora < 18:
        return 'Tarde'
    return 'Noite'


def _criar_turno(df):
    hora_pura = pd.to_datetime(df['horario'], format='%H:%M:%S', errors='coerce').dt.hour
    if hora_pura.isnull().all():
        hora_pura = pd.to_datetime(df['horario'], format='%H:%M', errors='coerce').dt.hour
    df['turno'] = hora_pura.apply(_categorizar_turno)
    return df


def decompor_tracado_via(df):
    """Decompõe o campo multi-rótulo tracado_via em uma flag binária por
    característica. Usada em 03_notebook_aed.ipynb para persistir as colunas
    em dados_model.csv; mantida aqui também como fallback para CSVs antigos
    que ainda não passaram por essa etapa.
    """
    tracado = df['tracado_via'].fillna('')
    for token, coluna in zip(TOKENS_TRACADO, COLUNAS_TRACADO):
        df[coluna] = tracado.str.contains(token, regex=False).astype(int)
    return df


def carregar_dados(caminho_csv=CAMINHO_PADRAO, test_size=0.3, random_state=42):
    """Carrega o dataset consolidado PRF+DNIT e devolve X_train, X_test,
    y_train, y_test prontos para o treinamento (feature engineering + OHE +
    padronização das variáveis numéricas de infraestrutura).
    """
    df = pd.read_csv(caminho_csv, sep=';')
    df = _criar_turno(df)

    # dados_model.csv já sai de 03_notebook_aed.ipynb com as colunas
    # tracado_* persistidas; recalcular só é necessário para CSVs gerados
    # antes dessa etapa ter sido movida para a normalização/AED.
    if not set(COLUNAS_TRACADO).issubset(df.columns):
        df = decompor_tracado_via(df)

    colunas_features = VARIAVEIS_CATEGORICAS + COLUNAS_TRACADO + VARIAVEIS_NUMERICAS
    X_bruto = df[colunas_features]
    y = df['acidente_grave_ou_fatal']

    X_final = pd.get_dummies(X_bruto, columns=VARIAVEIS_CATEGORICAS, drop_first=True)
    for col in X_final.columns:
        if X_final[col].dtype == 'bool':
            X_final[col] = X_final[col].astype(int)

    # Nomes de colunas seguros para XGBoost/LightGBM, que rejeitam [ ] < >
    X_final.columns = X_final.columns.str.replace(r'[\[\]<>]', '', regex=True)

    if 'id' in df.columns:
        # Split por grupo (acidente): cada acidente pode gerar várias linhas (uma por
        # envolvido/veículo). Um split aleatório por linha deixaria envolvidos do MESMO
        # acidente em treino e teste simultaneamente, vazando as condições da via/clima
        # daquele acidente entre os dois conjuntos. GroupShuffleSplit garante que todo
        # acidente cai inteiramente em um lado só.
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
        idx_train, idx_test = next(splitter.split(X_final, y, groups=df['id']))
        X_train, X_test = X_final.iloc[idx_train].copy(), X_final.iloc[idx_test].copy()
        y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    else:
        # Fallback para CSVs gerados antes da coluna 'id' ser preservada no notebook 02
        X_train, X_test, y_train, y_test = train_test_split(
            X_final, y, test_size=test_size, random_state=random_state, stratify=y
        )

    scaler = StandardScaler()
    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train[VARIAVEIS_NUMERICAS] = scaler.fit_transform(X_train[VARIAVEIS_NUMERICAS])
    X_test[VARIAVEIS_NUMERICAS] = scaler.transform(X_test[VARIAVEIS_NUMERICAS])

    return X_train, X_test, y_train, y_test
