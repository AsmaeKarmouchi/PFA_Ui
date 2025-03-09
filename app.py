import gradio as gr
import pandas as pd
from transformers import pipeline

# Charger un modèle léger pour générer du texte (CPU uniquement)
generator = pipeline("text-generation", model="gpt2", device=-1)

# Chemin du fichier de configuration par défaut
CONFIG_TEMPLATE_PATH = "config_template.xlsx"

# Liste des utilisateurs autorisés (nom d'utilisateur, mot de passe)
AUTH_USERS = {
    "user1": "password1",
    "user2": "password2"
}

# Création du fichier modèle de configuration
def create_config_template():
    config_data = pd.DataFrame({
        "Paramètre": ["max_length", "num_return_sequences", "temperature"],
        "Valeur": [150, 1, 1.0]  # Valeurs par défaut
    })
    config_data.to_excel(CONFIG_TEMPLATE_PATH, index=False)

# Générer le fichier modèle au démarrage
create_config_template()

# Charger les paramètres LLM à partir d'un fichier Excel
def load_llm_config(file):
    try:
        df = pd.read_excel(file)

        # Vérifier si les colonnes nécessaires sont présentes
        required_columns = {"Paramètre", "Valeur"}
        if not required_columns.issubset(set(df.columns)):
            return "❌ Erreur : Le fichier doit contenir les colonnes 'Paramètre' et 'Valeur'.", None

        # Convertir en dictionnaire de paramètres
        params = dict(zip(df["Paramètre"], df["Valeur"]))

        # Appliquer les paramètres (s'assurer qu'ils sont bien convertis)
        max_length = int(params.get("max_length", 150))
        num_return_sequences = int(params.get("num_return_sequences", 1))
        temperature = float(params.get("temperature", 1.0))

        return f"✅ Paramètres chargés : max_length={max_length}, num_return_sequences={num_return_sequences}, temperature={temperature}", params
    except Exception as e:
        return f"❌ Erreur de lecture du fichier : {str(e)}", None

# Fonction pour reformuler un texte avec les paramètres dynamiques
def reformulate_text(text, params={}):
    max_length = int(params.get("max_length", 150))
    num_return_sequences = int(params.get("num_return_sequences", 1))
    temperature = float(params.get("temperature", 1.0))

    result = generator(text, max_length=max_length, num_return_sequences=num_return_sequences, temperature=temperature, truncation=True)
    return result[0]['generated_text']

# Fonction pour traiter un fichier Excel
def process_file(file, params={}):
    try:
        df = pd.read_excel(file)

        if 'Text' not in df.columns:
            return "❌ Erreur : Le fichier doit contenir une colonne nommée 'Text'.", None

        reformulated_texts = [reformulate_text(str(row['Text']), params) for _, row in df.iterrows()]
        df['Reformulated_Text'] = reformulated_texts

        output_path = "reformulated.xlsx"
        df.to_excel(output_path, index=False)

        return df, output_path
    except Exception as e:
        return f"❌ Erreur lors du traitement : {str(e)}", None

# Fonction pour reformuler du texte et générer les fichiers de sortie
def text_interface(text, params={}):
    reformulated = reformulate_text(text, params)
    
    txt_path = "reformulated.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(reformulated)

    df = pd.DataFrame({"Texte original": [text], "Texte reformulé": [reformulated]})
    excel_path = "reformulated_text.xlsx"
    df.to_excel(excel_path, index=False)

    return reformulated, txt_path, excel_path

# Interface Gradio
css_styles = """
.header { text-align: center; font-size: 28px; font-weight: bold; padding: 20px; background: #003366; color: white; border-radius: 10px; }
.footer { text-align: center; font-size: 16px; padding: 15px; background: #003366; color: white; border-radius: 10px; margin-top: 20px; }
.logo { text-align: center; margin-bottom: 10px; }
.btn { background-color: #003366; color: white; font-weight: bold; border-radius: 5px; padding: 10px 20px; }
.btn:hover { background-color: #0055A4; }
"""

# Fonction pour vérifier les identifiants
def check_credentials(username, password):
    if username in AUTH_USERS and AUTH_USERS[username] == password:
        return True
    return False

# Interface de connexion
def auth_interface():
    with gr.Blocks() as auth_ui:
        gr.Markdown("## 🔐 Connexion à la Plateforme de Reformulation")
        username = gr.Textbox(label="Nom d'utilisateur")
        password = gr.Textbox(label="Mot de passe", type="password")
        login_btn = gr.Button("Se connecter")
        status = gr.Textbox(label="Statut de la connexion", interactive=False)

        login_btn.click(
            fn=lambda u, p: "✅ Connexion réussie !" if check_credentials(u, p) else "❌ Échec de la connexion",
            inputs=[username, password],
            outputs=status
        )
    return auth_ui

# Interface de la plateforme de reformulation
def reformulation_interface():
    with gr.Blocks(css=css_styles) as platform_ui:
        # Header avec logo 
        gr.Markdown("<div class='header'>📝 Plateforme de Reformulation - </div>")

        with gr.Tabs():
            # Onglet Reformulation de Texte
            with gr.Tab("📄 Reformulation de Texte"):
                gr.Markdown("### 🔍 Entrez un texte pour générer une reformulation.")
                text_input = gr.Textbox(label="Texte original", placeholder="Tapez ou collez votre texte ici...")
                btn_text = gr.Button("🔄 Reformuler", elem_classes="btn")
                text_output = gr.Textbox(label="Texte reformulé")
                
                gr.Markdown("### 📥 Télécharger la reformulation :")
                with gr.Row():
                    text_download_txt = gr.File(label="Télécharger en .txt")
                    text_download_excel = gr.File(label="Télécharger en .xlsx")
            
            # Onglet Traitement de Fichier
            with gr.Tab("📂 Reformulation de Fichier Excel"):
                gr.Markdown("### 📊 Téléversez un fichier Excel contenant une colonne 'Text'")
                file_input = gr.File(label="📎 Téléverser un fichier Excel")
                btn_file = gr.Button("📊 Traiter le fichier", elem_classes="-btn")
                
                gr.Markdown("### 🔍 Aperçu du fichier reformulé :")
                file_output_table = gr.Dataframe(label="Aperçu des résultats")
                file_download = gr.File(label="📥 Télécharger le fichier reformulé")

            # Onglet Paramètres LLM
            with gr.Tab("⚙️ Paramètres LLM"):
                gr.Markdown("### 📥 Télécharger et modifier le fichier de paramètres")
                config_download = gr.File(value=CONFIG_TEMPLATE_PATH, label="📥 Télécharger le modèle de fichier")
                
                gr.Markdown("### 📤 Charger un fichier de configuration modifié")
                config_input = gr.File(label="📎 Téléverser un fichier de configuration")
                btn_config = gr.Button("⚙️ Appliquer les paramètres", elem_classes="-btn")
                
                config_status = gr.Textbox(label="Statut du chargement", interactive=False)

        # Footer
        gr.Markdown("<div class='footer'>© 2025  - Propulsé par l'IA</div>")

        # Actions des boutons
        btn_text.click(text_interface, inputs=text_input, outputs=[text_output, text_download_txt, text_download_excel])
        btn_file.click(lambda file: process_file(file, {}), inputs=file_input, outputs=[file_output_table, file_download])
        btn_config.click(load_llm_config, inputs=config_input, outputs=[config_status])
    return platform_ui

# Interface principale
with gr.Blocks() as demo:
    # Page d'authentification
    with gr.Tab("🔐 Connexion") as auth_tab:
        gr.Markdown("## 🔐 Connexion à la Plateforme de Reformulation")
        username = gr.Textbox(label="Nom d'utilisateur")
        password = gr.Textbox(label="Mot de passe", type="password")
        login_btn = gr.Button("Se connecter")
        status = gr.Textbox(label="Statut de la connexion", interactive=False)
    
    # Page de reformulation (visible uniquement après authentification réussie)
    with gr.Tab("📝 Plateforme de Reformulation", visible=False) as reformulation_tab:
        platform_ui = reformulation_interface()

    # Logique pour basculer vers la plateforme après une connexion réussie
    def on_login(username, password):
        if check_credentials(username, password):
            return gr.update(visible=True), gr.update(visible=False), "✅ Connexion réussie !"  # Afficher la plateforme, masquer l'authentification
        else:
            return gr.update(visible=False), gr.update(visible=True), "❌ Échec de la connexion"  # Masquer la plateforme, afficher l'authentification

    # Lier la connexion à la logique de basculement
    login_btn.click(
        on_login,
        inputs=[username, password],
        outputs=[reformulation_tab, auth_tab, status]
    )

# Lancer l'application
if __name__ == "__main__":
    demo.launch()