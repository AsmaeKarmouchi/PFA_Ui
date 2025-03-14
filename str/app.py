import streamlit as st
import pandas as pd
from openai import OpenAI

# Configuration de l'API OpenAI avec OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Clé API directement dans le code
)

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
                    # Appel à l'API pour obtenir la réponse
                    completion = client.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "",  # Optionnel
                            "X-Title": "",  # Optionnel
                        },
                        model="deepseek/deepseek-r1:free",
                        messages=[
                            {
                                "role": "user",
                                "content": f"{pre_prompt}\n\n{user_prompt}" if pre_prompt else user_prompt
                            }
                        ]
                    )
                    # Affichage du résultat
                    reformulated_text = completion.choices[0].message.content
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
    uploaded_file = st.file_uploader("Téléversez un fichier Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            if "Text" not in df.columns or "Preprompt" not in df.columns:
                st.error("Le fichier doit contenir les colonnes 'Text' et 'Prepromt'.")
            else:
                st.success("Fichier téléversé avec succès !")
                st.write("Aperçu du fichier :")
                st.dataframe(df.head())

                # Bouton pour lancer le traitement
                if st.button("🔄 Traiter le fichier"):
                    with st.spinner("Traitement en cours..."):
                        reformulated_texts = []
                        for index, row in df.iterrows():
                            try:
                                completion = client.chat.completions.create(
                                    extra_headers={
                                        "HTTP-Referer": "",  # Optionnel
                                        "X-Title": "",  # Optionnel
                                    },
                                    model="deepseek/deepseek-r1:free",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": f"{row['Preprompt']}\n\n{row['Text']}" if row['Preprompt'] else row['Text']
                                        }
                                    ]
                                )
                                reformulated_texts.append(completion.choices[0].message.content)
                            except Exception as e:
                                st.error(f"Erreur lors de la reformulation de la ligne {index + 1} : {e}")
                                reformulated_texts.append("")

                        # Ajout de la colonne reformulée
                        df["Reformulated_Text"] = reformulated_texts
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
    st.download_button(
        label="📥 Télécharger le modèle Excel",
        data=pd.DataFrame({
            "Paramètre": ["Exemple"],
            "Valeur": ["Valeur par défaut"]
        }).to_csv(index=False),
        file_name="modele_configuration.csv",
        mime="text/csv"
    )

    # Téléversement de configuration
    st.subheader("Téléverser une configuration")
    config_file = st.file_uploader("Téléversez un fichier Excel de configuration", type=["xlsx"])
    if config_file:
        try:
            config_df = pd.read_excel(config_file)
            st.success("Fichier de configuration téléversé avec succès !")
            st.write("Paramètres actuels :")
            st.json(config_df.to_dict(orient="records"))
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier de configuration : {e}")