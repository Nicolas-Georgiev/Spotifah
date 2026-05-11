import webview
from api import Api

if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "EKHO",
        "https://ekho-sound-vault.lovable.app",
        js_api=api,
        width=1280,
        height=800,
        min_size=(960, 600),
    )
    webview.start(debug=True)
