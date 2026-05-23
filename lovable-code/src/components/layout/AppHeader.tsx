import { Link } from "@tanstack/react-router";
import { Music2, Settings } from "lucide-react";
import { NavBar } from "./NavBar";
import { SearchBar } from "./SearchBar";

function iconBtn(active: boolean) {
  return `w-10 h-10 rounded-lg grid place-items-center transition ${
    active
      ? "bg-primary/20 text-primary glow-violet"
      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
  }`;
}

export function AppHeader() {
  return (
    <header className="sticky top-0 z-30 glass border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2 mr-2 shrink-0">
          <div className="w-9 h-9 rounded-lg bg-primary/20 border border-primary/40 grid place-items-center glow-violet">
            <Music2 className="w-5 h-5 text-primary" />
          </div>
          <span className="font-mono text-xl font-bold text-primary text-glow-violet hidden sm:inline">EKHO</span>
        </Link>

        <NavBar />

        <SearchBar />

        <Link
          to="/settings"
          className={iconBtn(false)}
          aria-label="Configuración"
        >
          <Settings className="w-5 h-5" />
        </Link>
      </div>
    </header>
  );
}
