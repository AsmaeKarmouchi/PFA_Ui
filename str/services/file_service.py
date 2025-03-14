# services/file_service.py
import pandas as pd

def read_excel(file):
    """Lit un fichier Excel et retourne un DataFrame."""
    return pd.read_excel(file)

def save_to_excel(df, filename):
    """Enregistre un DataFrame dans un fichier Excel."""
    df.to_excel(filename, index=False)

def save_to_txt(text, filename):
    """Enregistre un texte dans un fichier TXT."""
    with open(filename, "w") as file:
        file.write(text)