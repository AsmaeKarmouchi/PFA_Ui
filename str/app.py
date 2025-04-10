# app.py
import streamlit as st
import pandas as pd
from services.prompt_service import reformulate_text
from services.file_service import read_excel, save_to_excel, save_to_txt
from services.config_service import get_default_config, save_config, load_config

# Titre de l'application
st.title("Interface de Chat avec DeepSeek via OpenRouter")

# Barre latérale pour la navigation
st.sidebar.title("Navigation Principale")
section = st.sidebar.radio(
    "Choisissez une section :",
    ["📄 Texte", "📂 Fichier Excel", "⚙️ Paramètres"]
)

# Section "📄 Texte"
if section == "📄 Texte":
    st.header("📄 Reformulation de Texte")

    # Zone de saisie de texte
    user_prompt = st.text_area("Entrez votre texte à reformuler ici :", height=200)
    pre_prompt = st.text_area("Entrez votre pré-prompt ici (optionnel) :", height=100)

    # Bouton de reformulation
    if st.button("🔄 Reformuler"):
        if user_prompt:
            with st.spinner("Reformulation en cours..."):
                try:
                    reformulated_text = reformulate_text(user_prompt, pre_prompt)
                    st.success("Texte reformulé avec succès !")
                    st.text_area("Texte reformulé :", reformulated_text, height=200)

                    # Téléchargement des résultats
                    st.download_button(
                        label="📥 Télécharger en format TXT",
                        data=reformulated_text,
                        file_name="texte_reformule.txt",
                        mime="text/plain"
                    )

                    # Téléchargement en format Excel
                    df = pd.DataFrame({
                        "Texte original": [user_prompt],
                        "Texte reformulé": [reformulated_text]
                    })
                    st.download_button(
                        label="📥 Télécharger en format Excel",
                        data=df.to_csv(index=False),
                        file_name="texte_reformule.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {e}")
        else:
            st.warning("Veuillez entrer un texte à reformuler.")

# Section "📂 Fichier Excel"
elif section == "📂 Fichier Excel":
    st.header("📂 Traitement de Fichier Excel")

    # Téléversement de fichier
    uploaded_file = st.file_uploader("Téléversez un fichier Excel (.xlsx)fichier avec les colonnes Text et Preprompt ", type=["xlsx"])
    if uploaded_file:
        try:
            df = read_excel(uploaded_file)
            if "Text" not in df.columns or "Preprompt" not in df.columns:
                st.error("Le fichier doit contenir les colonnes 'Text' et 'Preprompt'.")
            else:
                st.success("Fichier téléversé avec succès !")
                st.write("Aperçu du fichier :")
                st.dataframe(df.head())

                # Bouton pour lancer le traitement
                if st.button("🔄 Traiter le fichier"):
                    with st.spinner("Traitement en cours..."):
                        df["Reformulated_Text"] = df.apply(
                            lambda row: reformulate_text(row["Text"], row["Preprompt"]),
                            axis=1
                        )
                        st.success("Traitement terminé !")
                        st.write("Résultats :")
                        st.dataframe(df)

                        # Téléchargement du fichier reformulé
                        st.download_button(
                            label="📥 Télécharger le fichier reformulé",
                            data=df.to_csv(index=False),
                            file_name="fichier_reformule.csv",
                            mime="text/csv"
                        )
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

# Section "⚙️ Paramètres"
elif section == "⚙️ Paramètres":
    st.header("⚙️ Paramètres du Modèle")

    # Téléchargement du modèle de configuration
    st.subheader("Télécharger un modèle de configuration")
    default_config = get_default_config()
    st.download_button(
        label="📥 Télécharger le modèle Excel",
        data=default_config.to_csv(index=False),
        file_name="modele_configuration.csv",
        mime="text/csv"
    )

    # Téléversement de configuration
    st.subheader("Téléverser une configuration")
    config_file = st.file_uploader("Téléversez un fichier Excel de configuration", type=["xlsx"])
    if config_file:
        try:
            config_df = load_config(config_file)
            st.success("Fichier de configuration téléversé avec succès !")
            st.write("Paramètres actuels :")
            st.dataframe(config_df)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier de configuration : {e}")

#streamlit run app.py