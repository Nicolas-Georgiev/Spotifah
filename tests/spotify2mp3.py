import subprocess
import sys
import os
import json

def main():
    # Lista de URLs de Spotify
    urls = [
        "https://open.spotify.com/playlist/6WBfYQJ2au9pDYoRethgoa?si=SI8V461XT5m27SDEjY5ktQ"
    ]
    output_folder = "data/music"
    metadata_file = "data/music/metadatos.spotdl"
    try:
        # Ejecuta el CLI de spotDL como si fuera desde la terminal
        subprocess.run(["spotdl"] + [urls[0]] + ["--output",output_folder,"--save-file", metadata_file] , check=True)
        print("✅ Canciones descargadas correctamente")
    except subprocess.CalledProcessError as e: 
        print(f"❌ Error al descargar: {e}")

if __name__ == "__main__":
    main()
