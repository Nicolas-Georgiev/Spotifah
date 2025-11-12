class PlayerUI:
    def __init__(self, controller):
        self.controller = controller

    def run(self):
        print("🎧 Reproductor de Música (comandos: play, pause, resume, stop, next, prev, exit)")
        while True:
            command = input(">> ").strip().lower()
            if command == "play":
                self.controller.play()
            elif command == "pause":
                self.controller.pause()
            elif command == "resume":
                self.controller.resume()
            elif command == "stop":
                self.controller.stop()
            elif command == "next":
                self.controller.next_track()
            elif command == "prev":
                self.controller.previous_track()
            elif command == "exit":
                self.controller.stop()
                print("👋 Saliendo del reproductor...")
                break
            else:
                print("❌ Comando no reconocido.")
