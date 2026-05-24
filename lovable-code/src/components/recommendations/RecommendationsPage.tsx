import { Sparkles, Music, Star } from "lucide-react";
import { GlassCard } from "../shared/GlassCard";
import { SongCard } from "../shared/SongCard";
import type { Song } from "../../lib/bridge";

const MOCK_PLAYLISTS = [
  { id: "p1", name: "Favoritos", cover: "" },
  { id: "p2", name: "Energía", cover: "" },
  { id: "p3", name: "Chill", cover: "" },
  { id: "p4", name: "Descubrimientos", cover: "" },
];

const MOCK_RECOMMENDATIONS: Song[] = [
  { id: "r1", title: "Neón Dreams", artist: "Luna Vortex", album: "Synthwave Vol.2", duration: 237, genre: "Electronic", source: "youtube", path: "", cover_url: "" },
  { id: "r2", title: "Midnight Signal", artist: "The Echoes", album: "Signals", duration: 284, genre: "Indie", source: "spotify", path: "", cover_url: "" },
  { id: "r3", title: "Aurora", artist: "Solar Drift", album: "Northern Lights", duration: 312, genre: "Ambient", source: "soundcloud", path: "", cover_url: "" },
  { id: "r4", title: "Lost Frequencies", artist: "Crimson Tide", album: "Waves", duration: 198, genre: "Pop", source: "youtube", path: "", cover_url: "" },
  { id: "r5", title: "Cyber Rain", artist: "Neon Pulse", album: "Digital Horizons", duration: 265, genre: "Electronic", source: "spotify", path: "", cover_url: "" },
  { id: "r6", title: "Velvet Sky", artist: "Mira Sol", album: "Dusk", duration: 243, genre: "Lo-Fi", source: "soundcloud", path: "", cover_url: "" },
  { id: "r7", title: "Ironclad", artist: "Hammerfall", album: "Steel Dawn", duration: 321, genre: "Rock", source: "youtube", path: "", cover_url: "" },
  { id: "r8", title: "Brisa", artist: "Valentina Ríos", album: "Tropical", duration: 212, genre: "Latin", source: "spotify", path: "", cover_url: "" },
];

export function RecommendationsPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-primary" />
          Recomendaciones
        </h1>
        <p className="text-sm text-muted-foreground mt-2">
          Descubre nueva música basada en tus playlists favoritas
        </p>
      </header>

      <GlassCard>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Music className="w-4 h-4 text-muted-foreground" />
          Selecciona una playlist de referencia
        </h2>
        <div className="flex flex-wrap gap-3">
          {MOCK_PLAYLISTS.map((p) => (
            <button
              key={p.id}
              className="glass rounded-xl px-4 py-3 flex items-center gap-3 hover:bg-primary/20 hover:text-primary transition border border-transparent hover:border-primary/30 cursor-pointer"
            >
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-lg shrink-0">
                ♪
              </div>
              <span className="font-medium">{p.name}</span>
            </button>
          ))}
        </div>
        <p className="text-xs text-muted-foreground mt-3">
          Próximamente: selección funcional con análisis real de canciones
        </p>
      </GlassCard>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Star className="w-4 h-4 text-muted-foreground" />
            Canciones recomendadas para ti
          </h2>
          <span className="text-xs text-muted-foreground">Basado en tu playlist — {MOCK_PLAYLISTS[0].name}</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {MOCK_RECOMMENDATIONS.map((s) => (
            <SongCard key={s.id} song={s} />
          ))}
        </div>
      </section>

      <GlassCard>
        <h2 className="text-lg font-semibold mb-2">¿Cómo funcionarán las recomendaciones?</h2>
        <ul className="text-sm text-muted-foreground space-y-1.5 list-disc list-inside">
          <li>Se analizarán los géneros, artistas y estilos de tu playlist seleccionada</li>
          <li>El sistema buscará canciones similares en tu biblioteca y fuentes externas</li>
          <li>Recibirás sugerencias personalizadas con vista previa y reproducción directa</li>
        </ul>
        <p className="text-xs text-muted-foreground mt-4 border-t border-border/40 pt-3">
          🚧 Esta sección está en desarrollo — los datos mostrados son solo una maqueta visual
        </p>
      </GlassCard>
    </div>
  );
}
