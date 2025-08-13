import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Nom du fichier Excel
EXCEL_FILE = 'grocerie.xlsx'

# Fonction pour charger les catégories depuis Feuil1
@st.cache_data
def load_categories():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='Feuil1', header=None)
        categories = {}
        current_category = None
        for index, row in df.iterrows():
            cat = row[0]
            subcat = row[1] if len(row) > 1 and pd.notna(row[1]) else None
            if pd.notna(cat) and pd.isna(subcat):
                current_category = cat
                categories[current_category] = []
            elif current_category and pd.notna(subcat):
                categories[current_category].append(subcat)
        return categories
    except FileNotFoundError:
        st.error("Fichier grocerie.xlsx introuvable.")
        return {}

# Fonction pour charger les dépenses depuis Feuil2
@st.cache_data
def load_expenses():
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name='Feuil2')
    except:
        columns = ['Date', '', 'Marché', 'catégorie', 'sous-catégorie', 'Prix', 'référence ticket', 'Observation']
        return pd.DataFrame(columns=columns)

# Fonction pour sauvegarder les dépenses dans Feuil2
def save_expenses(df):
    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Feuil2', index=False)

# Fonction pour ajouter une dépense
def add_expense(categories):
    st.subheader("Ajouter une dépense")
    date = st.date_input
