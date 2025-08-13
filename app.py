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
    date = st.date_input("Date", value=datetime.now())
    marche = st.text_input("Marché")
    categorie = st.selectbox("Catégorie", list(categories.keys()))
    sous_categorie = st.selectbox("Sous-catégorie", categories[categorie])
    prix = st.number_input("Prix", min_value=0.0, step=0.01)
    ref_ticket = st.text_input("Référence ticket")
    observation = st.text_input("Observation")
    
    if st.button("Ajouter"):
        new_row = {}
            'Date': date,
            '': '',
            'Marché': marche,
            'catégorie': categorie,
            'sous-catégorie': sous_categorie,
            'Prix': prix,
            'référence ticket': ref_ticket,
            'Observation': observation
        }
        df = load_expenses()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_expenses(df)
        st.success("Dépense ajoutée avec succès !")
        # Clear cache to refresh data
        st.cache_data.clear()

# Fonction pour afficher le bilan mensuel
def monthly_balance():
    st.subheader("Bilan mensuel")
    df = load_expenses()
    if df.empty:
        st.warning("Aucune dépense enregistrée.")
        return
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M')
    
    month_str = st.text_input("Mois (format YYYY-MM)", value=datetime.now().strftime("%Y-%m"))
    try:
        month_period = pd.Period(month_str, freq='M')
    except ValueError:
        st.error("Format invalide. Utilisation du mois actuel.")
        month_period = pd.Period.now(freq='M')
    
    monthly_df = df[df['Month'] == month_period]
    if monthly_df.empty:
        st.warning("Aucune dépense pour ce mois.")
        return
    
    total = monthly_df['Prix'].sum()
    st.write(f"**Total dépensé pour {month_period} :** {total:.2f}")
    
    st.write("**Bilan par catégorie :**")
    by_category = monthly_df.groupby('catégorie')['Prix'].sum().reset_index()
    st.dataframe(by_category)
    
    st.write("**Bilan par sous-catégorie :**")
    by_subcategory = monthly_df.groupby(['catégorie', 'sous-catégorie'])['Prix'].sum().reset_index()
    st.dataframe(by_subcategory)

# Fonction pour définir un budget
def set_budget(categories):
    st.subheader("Définir des budgets")
    if 'budgets' not in st.session_state:
        st.session_state.budgets = {}
    
    for cat in categories:
        budget = st.number_input(f"Budget pour {cat}", min_value=0.0, step=0.01, key=cat)
        if budget > 0:
            st.session_state.budgets[cat] = budget
            st.write(f"Budget pour {cat} défini à {budget}")

# Fonction pour vérifier les alertes
def check_alerts():
    st.subheader("Vérifier les alertes")
    if 'budgets' not in st.session_state or not st.session_state.budgets:
        st.warning("Aucun budget défini.")
        return
    
    df = load_expenses()
    if df.empty:
        st.warning("Aucune dépense enregistrée.")
        return
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M')
    current_month = pd.Period.now(freq='M')
    monthly_df = df[df['Month'] == current_month]
    
    if monthly_df.empty:
        st.warning("Aucune dépense ce mois-ci.")
        return
    
    by_category = monthly_df.groupby('catégorie')['Prix'].sum()
    for cat, spent in by_category.items():
        if cat in st.session_state.budgets and spent > st.session_state.budgets[cat]:
            st.error(f"ALERTE : Dépenses pour {cat} ({spent:.2f}) dépassent le budget ({st.session_state.budgets[cat]:.2f}) !")

# Interface principale
def main():
    st.title("Gestion des Dépenses")
    st.markdown("""
    ---
    **Astuce mobile :** après déploiement sur Streamlit Cloud, ouvre l'URL sur ton smartphone et utilise **Ajouter à l'écran d'accueil** pour un accès rapide.
    """)
    
    categories = load_categories()
    if not categories:
        st.stop()
    
    menu = ["Ajouter une dépense", "Bilan mensuel", "Définir des budgets", "Vérifier les alertes"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Ajouter une dépense":
        add_expense(categories)
    elif choice == "Bilan mensuel":
        monthly_balance()
    elif choice == "Définir des budgets":
        set_budget(categories)
    elif choice == "Vérifier les alertes":
        check_alerts()

if __name__ == "__main__":
    main()
