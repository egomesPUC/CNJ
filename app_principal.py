import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard - Peças de Pessoas em Situação de Rua",
    layout="wide"
)
 # ==========================
    # Tabela de motivos do alvará (TABELA1)
    # ==========================
MOTIVO_MAP = {
        1: "Revogação de preventiva",
        2: "Liberdade provisória com medidas cautelares",
        3: "Liberdade provisória",
        4: "Progressão de regime",
        5: "Concessão de regime semiaberto harmonizado",
        7: "Relaxamento de prisão",
        8: "Revogação da prisão temporária",
        9: "Extinção de punibilidade",
        10: "Extinção da pena",
        11: "Arquivamento do inquérito",
        12: "Absolvição",
        13: "Trancamento da ação penal",
        14: "Quitação de débito alimentar",
        15: "Revogação de deportação/extradição/expulsão",
        16: "Livramento condicional",
        17: "Arquivamento de ação penal",
        18: "Outras medidas cautelares",
        19: "Relaxamento de Prisão de Pessoa Presa em Lugar de Outra",
        20: "Regime Aberto Monitoramento Eletrônico",
        21: "Prisão domiciliar",
        22: "Liberdade Provisória com fiança",
        23: "Liberdade Provisória sem fiança",
        24: "Habeas Corpus",
        25: "Recolhimento da fiança arbitrada pela autoridade policial",
        26: "Término da Prisão Temporária",
        27: "Rejeição da denúncia ou queixa",
        28: "Impronúncia",
        29: "Condenação em regime aberto",
        30: "Indulto humanitário",
        31: "Regime Especial de semiliberdade aplicada à pessoa indígena",
        99: "Revogação Decorrente de Erro Material no Mandado",
    }
STATUS_MAP = {
    2:"Procurado", 
3:"Foragido", 
4:"Morto", 
5:"Em Liberdade", 
7:"Preso Condenado em Execução Provisória", 
8:"Preso Condenado em Execução Definitiva", 
9:"Preso Provisório (inválido - não utilizar)", 
10:"Internado Provisório", 
11:"Internado em Execução Provisória", 
12:"Internado em Execução Definitiva", 
13:"Preso Civil", 
14:"Em Monitoramento", 
15:"Em Saída Temporária", 
16:"Preso em Saída Temporária Autorizada para Estudo ou Trabalho", 
17:"Evadido", 
18:"Preso em Flagrante", 
19:"Em Tratamento Ambulatorial", 
20:"Em acompanhamento de medidas diversas da prisão", 
21:"Em acompanhamento de medidas diversas da prisão em execução", 
22:"Preso definitivo", 
23:"Internado definitivo", 
24:"Preso preventivo", 
25:"Preso temporário", 
26:"Aguardando soltura", 
27:"Preso para deportação/extradição/expulsão", 
28:"Deportado/extraditado/expulso", 
29:"Procurado para condução coercitiva"
}
# ==========================
# Carregamento de dados
# ==========================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path,sep=";")

    # Garante que os códigos sejam numéricos (quando possível)
    for col in ["SEQ_MUNICIPIO3", "SEQ_MOTIVO_EXPEDICAO_ALVARA"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    return df

 # Funções auxiliares para formatar as opções do filtro
def format_municipio_opt(x, municipio_dict):
    if isinstance(x, str) and x == "SEM_MUNICIPIO":
        return "SEM MUNICÍPIO INFORMADO"
    x=int(x)
    nome = municipio_dict.get(x, "")
    return f"{x} - {nome}"

def format_motivo_opt(x):
    if isinstance(x, str) and x == "SEM_MOTIVO":
        return "SEM MOTIVO INFORMADO"
    # x aqui é código numérico
    cod = int(x)
    desc = MOTIVO_MAP.get(cod, "Não informado / Outro")
    return f"{cod} - {desc}"

def format_status_opt(x):
    if isinstance(x, str) and x == "SEM_STATUS":
        return "SEM STATUS INFORMADO"
    # x aqui é código numérico
    cod = int(x)
    desc = STATUS_MAP.get(cod, "Não informado / Outro")
    return f"{cod} - {desc}"

def gerarFiltroMunicipio(df):
    # Dicionário código -> nome (apenas onde temos código e nome)
    muni_df_dict = (
            df[["SEQ_MUNICIPIO3", "NOM_MUNICIPIO"]]
            .dropna(subset=["SEQ_MUNICIPIO3", "NOM_MUNICIPIO"])
            .drop_duplicates()
        )
    municipio_dict = {
            row["SEQ_MUNICIPIO3"]: row["NOM_MUNICIPIO"]
            for _, row in muni_df_dict.iterrows()
        }
       # Códigos de município distintos (incluindo os que não têm nome)
    muni_codes = (
            df["SEQ_MUNICIPIO3"]
            .drop_duplicates()
            .dropna()
            .sort_values()
            .tolist()
        )
        
    has_null_muni = df["SEQ_MUNICIPIO3"].isna().any()

    municipio_options = muni_codes.copy()
    if has_null_muni:
        municipio_options.append("SEM_MUNICIPIO")

    return municipio_dict,municipio_options

def filtrarMunicipio(selected_municipios,filtered_df):
    mask_muni = pd.Series(False, index=filtered_df.index)
    # valores numéricos (códigos)
    muni_numeric = [m for m in selected_municipios if not isinstance(m, str)]
    if muni_numeric:
        mask_muni |= filtered_df["SEQ_MUNICIPIO3"].isin(muni_numeric)
        # opção "SEM_MUNICIPIO" -> inclui registros sem código
        if "SEM_MUNICIPIO" in selected_municipios:
            mask_muni |= filtered_df["SEQ_MUNICIPIO3"].isna()
        filtered_df = filtered_df[mask_muni]
    return filtered_df

def gerarFiltroMotivo(df):
    motivos_presentes = (
            df["SEQ_MOTIVO_EXPEDICAO_ALVARA"]
            .drop_duplicates()
            .dropna()
            .sort_values()
            .tolist()
        )
    motivo_options = motivos_presentes.copy()
    has_null_motivo = df["SEQ_MOTIVO_EXPEDICAO_ALVARA"].isna().any()
    if has_null_motivo:
        motivo_options.append("SEM_MOTIVO")
    return motivos_presentes,motivo_options

def filtrarMotivo(selected_motivos,filtered_df):
    mask_motivo = pd.Series(False, index=filtered_df.index)
    motivo_numeric = [m for m in selected_motivos if not isinstance(m, str)]
    if motivo_numeric:
        mask_motivo |= filtered_df["SEQ_MOTIVO_EXPEDICAO_ALVARA"].isin(motivo_numeric)

    if "SEM_MOTIVO" in selected_motivos:
        mask_motivo |= filtered_df["SEQ_MOTIVO_EXPEDICAO_ALVARA"].isna()
    filtered_df = filtered_df[mask_motivo]
    return filtered_df

def gerarFiltroStatus(df):
    status_presentes = (
            df["SEQ_STATUS"]
            .drop_duplicates()
            .dropna()
            .sort_values()
            .tolist()
        )
    status_options = status_presentes.copy()
    has_null_motivo = df["SEQ_STATUS"].isna().any()
    if has_null_motivo:
        status_options.append("SEM_STATUS")
    return status_presentes,status_options

def filtrarStatus(selected_status,filtered_df):
    mask_status = pd.Series(False, index=filtered_df.index)
    status_numeric = [m for m in selected_status if not isinstance(m, str)]
    if status_numeric:
        mask_status |= filtered_df["SEQ_STATUS"].isin(status_numeric)

    if "SEM_STATUS" in selected_status:
        mask_status |= filtered_df["SEQ_STATUS"].isna()
    filtered_df = filtered_df[mask_status]
    return filtered_df





def main():
    DATA_PATH = "BNMP_MORADOR_RUA.CSV"  # ajuste o caminho se necessário
    df = load_data(DATA_PATH)

   

    if "SEQ_MOTIVO_EXPEDICAO_ALVARA" in df.columns:
        df["DSC_MOTIVO_EXPEDICAO_ALVARA"] = (
            df["SEQ_MOTIVO_EXPEDICAO_ALVARA"]
            .map(MOTIVO_MAP)
            .fillna("Não informado / Outro")
        )

    # ==========================
    # Sidebar - Filtros (válidos para TODAS as abas)
    # ==========================
    st.sidebar.header("Filtros")

    filtered_df = df.copy()

    # --- Filtro de Município (multiselect) ---
    if "SEQ_MUNICIPIO3" in df.columns and "NOM_MUNICIPIO" in df.columns:
               
        municipio_dict,municipio_options=gerarFiltroMunicipio(df)
        selected_municipios = st.sidebar.multiselect(
            "Município",
            options=municipio_options,
            default=municipio_options,  # todos selecionados por padrão (inclusive SEM_MUNICIPIO se existir)
            format_func=lambda x: format_municipio_opt(x, municipio_dict),
        )
        if selected_municipios:
            filtered_df = filtrarMunicipio(selected_municipios,filtered_df)
            
    # --- Filtro de Motivo do Alvará (multiselect) ---
    motivo_options = []
    if "SEQ_MOTIVO_EXPEDICAO_ALVARA" in df.columns:
        motivos_presentes,motivo_options=gerarFiltroMotivo(df)
    selected_motivos = st.sidebar.multiselect(
        "Motivo do Alvará",
        options=motivo_options,
        default=motivo_options,  # todos selecionados por padrão (incluindo SEM_MOTIVO se existir)
        format_func=lambda x: format_motivo_opt(x),
    )
    if selected_motivos and "SEQ_MOTIVO_EXPEDICAO_ALVARA" in filtered_df.columns:
        filtered_df=filtrarMotivo(selected_motivos,filtered_df)

# --- Filtro de Motivo do Status (multiselect) ---
    status_options = []
    if "SEQ_STATUS" in df.columns:
        status_presentes,status_options=gerarFiltroStatus(df)
        selected_status = st.sidebar.multiselect(
        "Status Pessoa",
        options=status_options,
        default=status_options,  # todos selecionados por padrão (incluindo SEM_STATUS se existir)
        format_func=lambda x: format_status_opt(x),
    )
    if selected_status :
        filtered_df=filtrarStatus(selected_status,filtered_df)
     

    # ==========================
    # Layout principal - Abas
    # ==========================
    st.title("Dashboard - Peças Jurídicas de Pessoas em Situação de Rua")

    tab1, tab2, tab3 = st.tabs(
        [
            "ABA 1 - Visão Geral das Peças",
            "ABA 2 - Peças por Motivo do Alvará",
            "ABA 3 - Peças por Município",
        ]
    )

    # --------------------------
    # ABA 1
    # --------------------------
    with tab1:
        st.subheader("Peças de Pessoas Moradoras de Rua - Visão Geral")

        if filtered_df.empty:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
        else:
            max_registros = len(filtered_df)
            qtd_registros = st.slider(
                "Quantidade de registros a exibir na tabela e no gráfico:",
                min_value=1,
                max_value=max_registros,
                value=max_registros,
            )

            df_exibicao = filtered_df.head(qtd_registros)

            st.markdown("### Tabela de dados (amostra filtrada)")
            st.dataframe(df_exibicao, use_container_width=True)

            # Cálculo das quantidades para o gráfico de barras
            if "SEQ_PECA" in df_exibicao.columns:
                total_pecas = df_exibicao["SEQ_PECA"].count()
            else:
                total_pecas = len(df_exibicao)

            if "SEQ_ALVARA_SOLTURA" in df_exibicao.columns:
                seq_alvara = df_exibicao["SEQ_ALVARA_SOLTURA"]
                sem_alvara_mask = seq_alvara.isna() | (
                    seq_alvara.astype(str).str.strip() == ""
                )
                qtd_sem_alvara = int(sem_alvara_mask.sum())
                qtd_com_alvara = int(len(df_exibicao) - qtd_sem_alvara)
            else:
                qtd_sem_alvara = 0
                qtd_com_alvara = 0

            # Métricas principais
            st.markdown("### Métricas principais (considerando os registros exibidos)")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total de peças", int(total_pecas))
            col2.metric("Peças **sem** alvará de soltura", int(qtd_sem_alvara))
            col3.metric("Peças **com** alvará de soltura", int(qtd_com_alvara))

            # Métricas adicionais
            municipios_distintos = (
                df_exibicao["SEQ_MUNICIPIO3"].nunique()
                if "SEQ_MUNICIPIO3" in df_exibicao.columns
                else 0
            )
            motivos_distintos = (
                df_exibicao["SEQ_MOTIVO_EXPEDICAO_ALVARA"].nunique()
                if "SEQ_MOTIVO_EXPEDICAO_ALVARA" in df_exibicao.columns
                else 0
            )
            pct_com_alvara = (
                round(qtd_com_alvara * 100 / total_pecas, 1)
                if total_pecas > 0
                else 0.0
            )
            pct_sem_alvara = (
                round(qtd_sem_alvara * 100 / total_pecas, 1)
                if total_pecas > 0
                else 0.0
            )

            st.markdown("### Métricas adicionais")
            c4, c5, c6 = st.columns(3)
            c4.metric("Municípios distintos (na amostra)", int(municipios_distintos))
            c5.metric("Motivos distintos de alvará (na amostra)", int(motivos_distintos))
            c6.metric(
                "% com alvará / sem alvará",
                f"{pct_com_alvara}% / {pct_sem_alvara}%",
            )

            # DataFrame para gráfico de barras
            resumo_df = pd.DataFrame(
                {
                    "Categoria": [
                        "Total de peças",
                        "Peças sem alvará de soltura",
                        "Peças com alvará de soltura",
                    ],
                    "Quantidade": [total_pecas, qtd_sem_alvara, qtd_com_alvara],
                }
            )

            st.markdown("### Gráfico de barras - Resumo de peças")
            chart_resumo = (
                alt.Chart(resumo_df)
                .mark_bar()
                .encode(
                    x=alt.X("Categoria:N", sort=None, title="Categoria"),
                    y=alt.Y("Quantidade:Q", title="Quantidade"),
                    tooltip=["Categoria", "Quantidade"],
                )
            )
            st.altair_chart(chart_resumo, use_container_width=True)

    # --------------------------
    # ABA 2
    # --------------------------
    with tab2:
        st.subheader("Peças de Pessoas Moradoras de Rua - Por Motivo do Alvará")

        if filtered_df.empty:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
        else:
            if "SEQ_MOTIVO_EXPEDICAO_ALVARA" not in filtered_df.columns:
                st.error(
                    "Coluna 'SEQ_MOTIVO_EXPEDICAO_ALVARA' não encontrada no conjunto de dados."
                )
            else:
                # Agrupa por motivo, contando quantidade de peças
                if "SEQ_PECA" in filtered_df.columns:
                    motivo_counts = (
                        filtered_df.groupby(
                            [
                                "SEQ_MOTIVO_EXPEDICAO_ALVARA",
                                "DSC_MOTIVO_EXPEDICAO_ALVARA",
                            ],
                            dropna=False  # mantém também os sem motivo
                        )
                        .agg(qtd_pecas=("SEQ_PECA", "count"))
                        .reset_index()
                    )
                else:
                    motivo_counts = (
                        filtered_df.groupby(
                            [
                                "SEQ_MOTIVO_EXPEDICAO_ALVARA",
                                "DSC_MOTIVO_EXPEDICAO_ALVARA",
                            ],
                            dropna=False
                        )
                        .size()
                        .reset_index(name="qtd_pecas")
                    )

                # NÃO remover NaN aqui; queremos mostrar também o "Não informado / Outro"
                motivo_counts = motivo_counts.sort_values(
                    "qtd_pecas", ascending=False
                )

                # Métricas para a aba 2
                total_pecas_tab2 = int(motivo_counts["qtd_pecas"].sum())
                num_motivos_tab2 = int(len(motivo_counts))

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Total de peças (pós-filtro)", total_pecas_tab2)
                col_b.metric("Nº de motivos diferentes", num_motivos_tab2)

                if not motivo_counts.empty:
                    top_row = motivo_counts.iloc[0]
                    top_cod = top_row["SEQ_MOTIVO_EXPEDICAO_ALVARA"]
                    top_desc = top_row["DSC_MOTIVO_EXPEDICAO_ALVARA"]
                    top_qtd = int(top_row["qtd_pecas"])

                    # se top_cod é nulo, tratamos como "Sem motivo"
                    if pd.isna(top_cod):
                        label_top = "SEM MOTIVO INFORMADO"
                    else:
                        label_top = f"{int(top_cod)} - {top_desc}"

                    col_c.metric(
                        "Motivo mais frequente",
                        label_top,
                        f"{top_qtd} peças",
                    )

                st.markdown("### Quantidade de peças por motivo de expedição do alvará")

                chart_motivo = (
                    alt.Chart(motivo_counts)
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "DSC_MOTIVO_EXPEDICAO_ALVARA:N",
                            sort="-y",
                            title="Motivo de expedição do alvará",
                        ),
                        y=alt.Y("qtd_pecas:Q", title="Quantidade de peças"),
                        tooltip=[
                            alt.Tooltip(
                                "SEQ_MOTIVO_EXPEDICAO_ALVARA:Q",
                                title="Código do motivo",
                            ),
                            alt.Tooltip(
                                "DSC_MOTIVO_EXPEDICAO_ALVARA:N", title="Motivo"
                            ),
                            alt.Tooltip("qtd_pecas:Q", title="Quantidade de peças"),
                        ],
                    )
                    .properties(height=500)
                )

                st.altair_chart(chart_motivo, use_container_width=True)

                st.markdown("### Tabela de apoio (motivo x quantidade)")
                st.dataframe(motivo_counts, use_container_width=True)

    # --------------------------
    # ABA 3
    # --------------------------
    with tab3:
        st.subheader("Peças de Pessoas Moradoras de Rua - Por Município")

        if filtered_df.empty:
            st.warning("Nenhum registro encontrado com os filtros selecionados.")
        else:
            if ("SEQ_MUNICIPIO3" not in filtered_df.columns) or (
                "NOM_MUNICIPIO" not in filtered_df.columns
            ):
                st.error(
                    "Colunas 'SEQ_MUNICIPIO3' e/ou 'NOM_MUNICIPIO' não encontradas no conjunto de dados."
                )
            else:
                # Para municípios sem nome, preenchermos "Sem município informado" para exibição
                muni_work = filtered_df.copy()
                muni_work["NOM_MUNICIPIO"] = muni_work["NOM_MUNICIPIO"].fillna(
                    "Sem município informado"
                )

                # Agrupa por município, contando quantidade de peças
                group_cols = ["SEQ_MUNICIPIO3", "NOM_MUNICIPIO"]
                if "SEQ_PECA" in muni_work.columns:
                    muni_counts = (
                        muni_work.groupby(group_cols, dropna=False)
                        .agg(qtd_pecas=("SEQ_PECA", "count"))
                        .reset_index()
                    )
                else:
                    muni_counts = (
                        muni_work.groupby(group_cols, dropna=False)
                        .size()
                        .reset_index(name="qtd_pecas")
                    )

                muni_counts = muni_counts.sort_values("qtd_pecas", ascending=False)

                total_pecas_muni = int(muni_counts["qtd_pecas"].sum())
                num_munis = int(len(muni_counts))

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Total de peças (pós-filtro)", total_pecas_muni)
                col_m2.metric("Nº de municípios (pós-filtro)", num_munis)

                if not muni_counts.empty:
                    top_row = muni_counts.iloc[0]
                    top_nome = top_row["NOM_MUNICIPIO"]
                    top_cod = top_row["SEQ_MUNICIPIO3"]
                    top_qtd = int(top_row["qtd_pecas"])

                    if pd.isna(top_cod):
                        label_muni = f"SEM MUNICÍPIO - {top_nome}"
                    else:
                        label_muni = f"{int(top_cod)} - {top_nome}"

                    col_m3.metric(
                        "Município com mais peças",
                        label_muni,
                        f"{top_qtd} peças",
                    )

                st.markdown("### Quantidade de peças por município")

                chart_muni = (
                    alt.Chart(muni_counts)
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "NOM_MUNICIPIO:N",
                            sort="-y",
                            title="Município",
                        ),
                        y=alt.Y("qtd_pecas:Q", title="Quantidade de peças"),
                        tooltip=[
                            alt.Tooltip("SEQ_MUNICIPIO3:Q", title="Código do Município"),
                            alt.Tooltip("NOM_MUNICIPIO:N", title="Município"),
                            alt.Tooltip("qtd_pecas:Q", title="Quantidade de peças"),
                        ],
                    )
                    .properties(height=500)
                )

                st.altair_chart(chart_muni, use_container_width=True)

                st.markdown("### Tabela de apoio (município x quantidade)")
                st.dataframe(muni_counts, use_container_width=True)
