import pandas as pd
import numpy as np
import streamlit as st

st.title("Consolidador de Metas Físicas")

name_df = pd.read_excel(
    "raw/test.xlsx", sheet_name="ACOMPANHAMENTO", skiprows=6, nrows=0)
name_df = name_df.columns[0]
name_df = name_df.split(": ")[1].replace("/", "_")
name_df

df = pd.read_excel("raw/test.xlsx", sheet_name="ACOMPANHAMENTO", skiprows=7)
df = df.rename(columns={
    'Meta/Produto': 'Meta/Produto - Realizada',
    'Unnamed: 7': 'Meta/Produto - cumulada',
    'Unnamed: 8': 'Meta/Produto - Não iniciada',
    'Unnamed: 9': 'Meta/Produto - Em Execução'
})
df = df.drop(0, axis=0)
df = df.reset_index(drop=True)
list_ffill = [
    'Programa Temático / Compromisso / Iniciativa',
    'AÇÕES / RESPONSÁVEIS'
]

for col in list_ffill:
    df[col] = df[col].ffill()

colunas_laterais = [
    'AÇÕES / RESPONSÁVEIS',
    'Objetivo/Produto'
]

df[colunas_laterais] = df[colunas_laterais].ffill(axis=1)
df.head(3)
