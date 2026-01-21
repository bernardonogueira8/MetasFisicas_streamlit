import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Consolidador de Metas", layout="wide")
st.title("📊 Consolidador de Metas Físicas")

# 1. Upload de múltiplos ficheiros
uploaded_files = st.file_uploader(
    "Selecione as planilhas de metas (Excel)", type=["xlsx"], accept_multiple_files=True
)

if uploaded_files:
    all_data = []  # Lista para guardar os DataFrames processados

    for file in uploaded_files:
        try:
            # --- Extração do Nome do Mês (Linha 6) ---
            # Lemos apenas o cabeçalho para pegar o "MÊS/ANO: JANEIRO/2025"
            header_info = pd.read_excel(
                file, sheet_name="ACOMPANHAMENTO", skiprows=6, nrows=0
            )
            raw_name = header_info.columns[0]
            mes = raw_name.split(": ")[1].split("/")[0]
            ano = raw_name.split(": ")[1].split("/")[1]

            # --- Processamento dos Dados (Linha 7 em diante) ---
            df = pd.read_excel(file, sheet_name="ACOMPANHAMENTO", skiprows=7)

            # Renomeação de colunas
            df = df.rename(columns={
                'Meta/Produto': 'Meta/Produto - Realizada',
                'Unnamed: 7': 'Meta/Produto - cumulada',
                'Unnamed: 8': 'Meta/Produto - Não iniciada',
                'Unnamed: 9': 'Meta/Produto - Em Execução'
            })

            # Limpeza inicial
            df = df.drop(0, axis=0)
            df = df.dropna(axis=0, thresh=6)
            # Remove coluna vazia se existir
            df = df.drop(
                columns=['Observação', 'Comentários '], errors='ignore'
            )
            # Preenchimento Vertical (ffill)
            list_ffill = [
                'Programa Temático / Compromisso / Iniciativa', 'AÇÕES / RESPONSÁVEIS']
            for col in list_ffill:
                df[col] = df[col].ffill()

            # Preenchimento Lateral (Ações -> Objetivo)
            colunas_laterais = ['AÇÕES / RESPONSÁVEIS', 'Objetivo/Produto']
            df[colunas_laterais] = df[colunas_laterais].ffill(axis=1)
            df = df[['Programa Temático / Compromisso / Iniciativa',
                     'AÇÕES / RESPONSÁVEIS',
                     'Objetivo/Produto', 'Meta/Prod. prog. incial', 'Meta/Prod. atual',
                     'Unidade de medida', 'Meta/Produto - Realizada',
                     'Meta/Produto - cumulada', 'Meta/Produto - Não iniciada',
                     'Meta/Produto - Em Execução']]
            # Substituição de valores
            lista = ['Meta/Prod. prog. incial', 'Meta/Prod. atual',
                     'Unidade de medida', 'Meta/Produto - Realizada',
                     'Meta/Produto - cumulada', 'Meta/Produto - Não iniciada',
                     'Meta/Produto - Em Execução']

            for item in lista:
                df[item] = df[item].replace('-', 0, regex=True)
                df[item] = df[item].replace('_', 0, regex=True)
                df[item] = df[item].replace('c', 0, regex=True)
                df[item] = df[item].replace('c', 0, regex=True)
                df[item] = df[item].replace(np.nan, 0)
            # Adicionar coluna com o nome do mês para identificar a origem
            df['Mês'] = mes
            df['Ano'] = ano

            all_data.append(df)

        except Exception as e:
            st.error(f"Erro ao processar {file.name}: {e}")

    # 3. Consolidação e Download
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        meses_map = {
            'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
            'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
        }

        # Criar coluna temporária de ordenação e ordenar o DataFrame
        df_final['mes_num'] = df_final['Mês'].str.upper().map(meses_map)
        df_final = df_final.sort_values(
            by=['Ano', 'mes_num']).drop(columns=['mes_num'])

        # Validador visual
        st.subheader("Pré-visualização dos Dados Consolidados")
        col1, col2 = st.columns(2)

        with col1:
            anos_processados = sorted(df_final['Ano'].unique())
            st.metric("Anos Identificados", ", ".join(
                map(str, anos_processados)))

        with col2:
            # Mostra os meses únicos na ordem cronológica que definimos
            meses_encontrados = df_final.drop_duplicates(subset=['Ano', 'Mês'])
            resumo_meses = meses_encontrados['Mês'].tolist()
            st.metric("Total de Meses",
                      f"{len(resumo_meses)} meses encaminhados")

        meses_lista = df_final['Mês'].unique().tolist()
        st.info(f"**Meses detetados:** {', '.join(meses_lista)}")
        st.divider()
        st.dataframe(df_final.head(10))

        # Função para converter DF para Excel (em memória)
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Consolidado')
            return output.getvalue()

        excel_data = to_excel(df_final)

        st.download_button(
            label="📥 Descarregar Planilha Consolidada",
            data=excel_data,
            file_name=f"Metas_Consolidadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Aguardando upload de ficheiros para começar...")
