import subprocess

def main():
    # Lista de URLs de Spotify
    urls = [
        "https://open.spotify.com/playlist/6WBfYQJ2au9pDYoRethgoa?si=UXWw1xs5QauePIaBAq_ECQ"
    ]
    output_folder = "data/music"

    try:
        # Ejecuta el CLI de spotDL como si fuera desde la terminal
        subprocess.run(["spotdl",urls[0], "--output",output_folder] , check=True)
        print("✅ Canciones descargadas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al descargar: {e}")

if __name__ == "__main__":
    main()
