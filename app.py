import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📈",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# 🎨 CSS personalizado
st.markdown("""
    <style>
    /* Fundo da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #E3E7ED; 
    }

    /* Títulos da barra lateral */
    section[data-testid="stSidebar"] h2 {
        color: #fffff; /* cor escura da paleta */
        font-weight: bold;
    }

    /* Caixas de seleção */
    div[data-baseweb="select"] {
        background-color: #fffff;
        border-radius: 8px;
    }

    /* Estilo das tags selecionadas no multiselect */
    span[data-baseweb="tag"] {
        background-color: #0F1A2B !important; /* cor personalizada */
        color: white !important;
        border-radius: 6px;
        padding: 4px 8px;
    }

    /* Ícone de fechar da tag (X) */
    span[data-baseweb="tag"] svg {
        fill: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby('cargo')['usd']
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )

        # Define uma cor única para todas as barras
        grafico_cargos.update_traces(marker_color="#52677D")

        grafico_cargos.update_layout(
            title_x=0.1,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )

        # Define uma cor única
        grafico_hist.update_traces(
            marker_color="#1C2E4A",
            marker_line_color="#eeeeee",
            marker_line_width=1)

        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        # Normaliza e mapeia valores
        remoto_normalizado = (
            df_filtrado['remoto']
            .astype(str)               # garante string
            .str.strip()               # remove espaços nas pontas
            .str.replace('\xa0', ' ')  # troca espaço invisível
            .str.lower()               # tudo minúsculo para mapear fácil
            .replace({
                'remote': 'Remoto',
                'remoto': 'Remoto',
                'onsite': 'Presencial',
                'on site': 'Presencial',
                'presencial': 'Presencial',
                'hybrid': 'Híbrido',
                'híbrido': 'Híbrido',
                'hibrido': 'Híbrido'
            })
        )

        remoto_contagem = remoto_normalizado.value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']

        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color='tipo_trabalho',
            color_discrete_map={
                'Remoto': '#52677D',
                'Presencial': '#BDC4D4',
                'Híbrido': '#0F1A2B'
            }
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()

        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale=["#0F1A2B", "#1C2E4A", "#52677D", "#BDC4D4"],  # degradê customizado
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
        )

        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)