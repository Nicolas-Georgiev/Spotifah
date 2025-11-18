class PlayerUI:
    def __init__(self, controller):
        self.controller = controller

    def run(self):
        print("Comandos: play, pause, resume, stop, next, prev, loop, random, toggle_random, vol [0-100], exit")

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
            elif command == "ran":
                self.controller.toggle_random_mode()
            elif command == "loop":
                self.controller.loop_track()
            elif command.startswith("vol "):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    self.controller.set_volume(parts[1])
                else:
                    print("❌ Usa el formato: vol [0-100]")
            elif command == "exit":
                self.controller.stop()
                print("👋 Saliendo del reproductor...")
                break
            else:
                print("❌ Comando no reconocido.")
