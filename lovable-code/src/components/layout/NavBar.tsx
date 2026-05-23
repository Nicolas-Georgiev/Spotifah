import { Link, useLocation } from "@tanstack/react-router";
import { Home, Library, Sparkles, Download } from "lucide-react";

function iconBtn(active: boolean) {
  return `w-10 h-10 rounded-lg grid place-items-center transition ${
    active
      ? "bg-primary/20 text-primary glow-violet"
      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
  }`;
}

export function NavBar() {
  const loc = useLocation();
  const isActive = (p: string) => loc.pathname === p || (p !== "/" && loc.pathname.startsWith(p));

  return (
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
  );
}
