import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Consolidador de Metas", layout="wide")
st.title("📊 Consolidador de Metas Físicas")

# 1. Upload de múltiplos ficheiros
uploaded_files = st.file_uploader("Selecione as planilhas de metas (Excel)", type=[
                                  "xlsx"], accept_multiple_files=True)

if uploaded_files:
    all_data = []  # Lista para guardar os DataFrames processados

    for file in uploaded_files:
        try:
            # --- Extração do Nome do Mês (Linha 6) ---
            # Lemos apenas o cabeçalho para pegar o "MÊS/ANO: JANEIRO/2025"
            header_info = pd.read_excel(
                file, sheet_name="ACOMPANHAMENTO", skiprows=6, nrows=0)
            raw_name = header_info.columns[0]
            mes_ano = raw_name.split(": ")[1].replace("/", "_")

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
            df = df.drop(0, axis=0)  # Remove a primeira linha de lixo

            # Preenchimento Vertical (ffill)
            list_ffill = [
                'Programa Temático / Compromisso / Iniciativa', 'AÇÕES / RESPONSÁVEIS']
            for col in list_ffill:
                df[col] = df[col].ffill()

            # Preenchimento Lateral (Ações -> Objetivo)
            colunas_laterais = ['AÇÕES / RESPONSÁVEIS', 'Objetivo/Produto']
            df[colunas_laterais] = df[colunas_laterais].ffill(axis=1)

            # Adicionar coluna com o nome do mês para identificar a origem
            df['Mês de Referência'] = mes_ano

            all_data.append(df)
            st.success(f"Ficheiro processado: {file.name} (Mês: {mes_ano})")

        except Exception as e:
            st.error(f"Erro ao processar {file.name}: {e}")

    # 3. Consolidação e Download
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)

        st.subheader("Pré-visualização dos Dados Consolidados")
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