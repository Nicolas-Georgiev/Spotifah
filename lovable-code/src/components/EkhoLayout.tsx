import { Link, Outlet, useLocation } from "@tanstack/react-router";
import { Music2, Library, Settings, Home, Download, Search, Sparkles } from "lucide-react";

export function EkhoLayout() {
  const loc = useLocation();

  const isActive = (p: string) => loc.pathname === p || (p !== "/" && loc.pathname.startsWith(p));

  const iconBtn = (active: boolean) =>
    `w-10 h-10 rounded-lg grid place-items-center transition ${
      active
        ? "bg-primary/20 text-primary glow-violet"
        : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
    }`;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-30 glass border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 mr-2 shrink-0">
            <div className="w-9 h-9 rounded-lg bg-primary/20 border border-primary/40 grid place-items-center glow-violet">
              <Music2 className="w-5 h-5 text-primary" />
            </div>
            <span className="font-mono text-xl font-bold text-primary text-glow-violet hidden sm:inline">EKHO</span>
          </Link>

          <nav className="flex items-center gap-1">
            <Link to="/" className={iconBtn(loc.pathname === "/")} aria-label="Inicio">
              <Home className="w-5 h-5" />
            </Link>
            <Link to="/library" className={iconBtn(isActive("/library"))} aria-label="Biblioteca">
              <Library className="w-5 h-5" />
            </Link>
            <Link to="/status" className={iconBtn(isActive("/status"))} aria-label="Sistema">
              <Sparkles className="w-5 h-5" />
            </Link>
            <Link to="/convert" className={iconBtn(isActive("/convert"))} aria-label="Conversor">
              <Download className="w-5 h-5" />
            </Link>
          </nav>

          <div className="flex-1 max-w-xl mx-auto relative hidden md:block">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              placeholder="Buscar canciones, artistas, álbumes..."
              className="w-full bg-input/60 border border-border rounded-full pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <Link to="/settings" className={iconBtn(isActive("/settings"))} aria-label="Configuración">
            <Settings className="w-5 h-5" />
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        <Outlet />
      </main>

      <footer className="hidden md:block py-6 text-center text-xs text-muted-foreground font-mono">
        EKHO v0.1.0 — built with ♪ for music lovers
      </footer>
    </div>
  );
}
