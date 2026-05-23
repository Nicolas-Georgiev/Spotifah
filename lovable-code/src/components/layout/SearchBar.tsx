import { Search } from "lucide-react";

export function SearchBar() {
  return (
    <div className="flex-1 max-w-xl mx-auto relative hidden md:block">
      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
      <input
        placeholder="Buscar canciones, artistas, álbumes..."
        className="w-full bg-input/60 border border-border rounded-full pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>
  );
}
