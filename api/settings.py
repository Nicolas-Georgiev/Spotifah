import os
import json


class SettingsMixin:
    def _apply_settings(self):
        try:
            settings = self._load_settings()
            if "download_path" in settings:
                path = settings["download_path"]
                if os.path.isdir(path) or self._ensure_dir(path):
                    self._music_dir = path
                    self.library.music_folder = path
                    self.library.reload_tracks()
        except Exception:
            pass

    def _ensure_dir(self, path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False

    def _load_settings(self) -> dict:
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                pass
        return {"volume": 100, "theme": "dark", "download_quality": "192"}

    def get_settings(self) -> dict:
        try:
            settings = self._load_settings()
            settings["download_path"] = self._music_dir
            return settings
        except Exception:
            return {"volume": 100, "theme": "dark", "download_quality": "192", "download_path": self._music_dir}

    def update_settings(self, data: dict) -> dict:
        try:
            settings = self._load_settings()
            settings.update(data)
            if "download_path" in data:
                new_path = data["download_path"]
                os.makedirs(new_path, exist_ok=True)
                self._music_dir = new_path
                from model.music_library import MusicLibrary
                self.library = MusicLibrary(self._music_dir)
                self._sync_local_music_library()
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return {"ok": True, "data": settings}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def select_folder_dialog(self) -> dict:
        try:
            import tkinter.filedialog
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            folder = tkinter.filedialog.askdirectory()
            root.destroy()
            if folder:
                return {"ok": True, "data": {"path": folder}}
            return {"ok": False, "error": "No se seleccionó carpeta"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
