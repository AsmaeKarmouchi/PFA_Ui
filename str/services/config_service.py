# services/config_service.py
import pandas as pd

def get_default_config():
    """Retourne un DataFrame avec les paramètres par défaut."""
    return pd.DataFrame({
        "Paramètre": ["Modèle", "Température", "Max Tokens"],
        "Valeur": ["deepseek/deepseek-r1:free", "0.7", "1000"]
    })

def save_config(config_df, filename):
    """Enregistre la configuration dans un fichier Excel."""
    config_df.to_excel(filename, index=False)

def load_config(file):
    """Charge la configuration à partir d'un fichier Excel."""
    return pd.read_excel(file)