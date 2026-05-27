import { useEffect, useMemo, useState } from "react";
import { Album, ArrowRight, Clock3, Music, Play, RefreshCw, Sparkles, Star } from "lucide-react";
import { bridge, fmtDuration, type RecommendedSong, type Song } from "../../lib/bridge";
import { useAppData } from "../../lib/app-data";
import { GlassCard } from "../shared/GlassCard";
import { CoverArt } from "../shared/CoverArt";
import { SourceBadge } from "../library/SourceBadge";

const FALLBACK_PLAYLIST = {
  id: "all",
  name: "Todas mis canciones",
  description: "Analiza tu biblioteca completa para descubrir nuevos temas.",
  is_public: false,
  cover_url: "/portadas/all-songs.svg",
};

const RECOMMENDATION_LIMIT = 4;

function isSuggestion(song: RecommendedSong) {
  return song.can_import === false && !song.path;
}

export function RecommendationsPage() {
  const { playlists, songs, recentSongs, currentPlayingId, setCurrentPlayingId, triggerPlayerRefresh } = useAppData();
  const availablePlaylists = useMemo(() => {
    const filtered = playlists.length > 0 ? playlists : [FALLBACK_PLAYLIST];
    const hasAll = filtered.some((playlist) => playlist.id === "all");
    return hasAll ? filtered : [FALLBACK_PLAYLIST, ...filtered];
  }, [playlists]);

  const [selectedPlaylistId, setSelectedPlaylistId] = useState("all");
  const [recommendations, setRecommendations] = useState<RecommendedSong[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const selectedPlaylist =
    availablePlaylists.find((playlist) => playlist.id === selectedPlaylistId) ?? availablePlaylists[0];

  const featuredRecommendation = recommendations[0] ?? null;
  const discoverySongs = (recentSongs.length > 0 ? recentSongs : songs).slice(0, 6);
  const recommendationCount = recommendations.length;
  const featuredReason = featuredRecommendation?.reason || "Mezcla de historial, similitud y popularidad";

  useEffect(() => {
    let cancelled = false;

    async function loadRecommendations() {
      setLoading(true);
      setError(null);
      try {
        const items = await bridge.getRecommendations(selectedPlaylistId, RECOMMENDATION_LIMIT, reloadToken);
        if (cancelled) return;
        setRecommendations(items);
      } catch (err: any) {
        if (!cancelled) {
          setRecommendations([]);
          setError(err?.message ?? "No se pudieron cargar las recomendaciones");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadRecommendations();

    return () => {
      cancelled = true;
    };
  }, [selectedPlaylistId, reloadToken]);

  const handlePlay = async (song: RecommendedSong) => {
    const isExternal = song.source?.toLowerCase() !== "local" && !song.path;
    if (isExternal) {
      if (!song.external_url) {
        setError("No se pudo importar la recomendación: URL no disponible");
        return;
      }
      setActionLoadingId(song.id);
      setError(null);
      try {
        const result = await bridge.convertSpotify(song.external_url);
        if (!result.ok) {
          setError(result.error ?? "No se pudo importar la recomendación");
        } else {
          setReloadToken((value) => value + 1);
        }
      } finally {
        setActionLoadingId(null);
      }
      return;
    }

    const queue = recommendations.map((item) => item.id);
    await bridge.playSong(song.id, queue);
    setCurrentPlayingId(song.id);
    triggerPlayerRefresh();
  };

  const handlePlaySong = async (song: Song) => {
    await bridge.playSong(song.id);
    setCurrentPlayingId(song.id);
    triggerPlayerRefresh();
  };

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-border/60 bg-gradient-to-br from-primary/15 via-background to-accent/10 p-6 shadow-2xl shadow-primary/10 sm:p-8">
        <div className="absolute inset-0 opacity-[0.35] [background:radial-gradient(circle_at_top_right,_rgba(255,255,255,0.25),_transparent_28%),radial-gradient(circle_at_bottom_left,_rgba(124,58,237,0.14),_transparent_24%)]" />
        <div className="relative grid gap-6 grid-cols-1">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-background/60 px-3 py-1 text-xs font-medium text-primary backdrop-blur">
              <Sparkles className="h-3.5 w-3.5" />
              Recomendaciones según tu música
            </div>
            <div className="space-y-3">
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
                Descubre lo siguiente que vas a querer escuchar
              </h1>
              <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">
                El motor busca similitud musical con tu playlist de referencia para
                mostrarte recomendaciones que se actualizan con tu biblioteca local.
              </p>
            </div>

            <div className="flex flex-wrap gap-3 text-sm">
              <div className="rounded-2xl border border-border/60 bg-background/70 px-4 py-3 backdrop-blur">
                <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Playlist</div>
                <div className="mt-1 font-semibold text-foreground">{selectedPlaylist.name}</div>
              </div>
              <div className="rounded-2xl border border-border/60 bg-background/70 px-4 py-3 backdrop-blur">
                <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Recomendaciones</div>
                <div className="mt-1 font-semibold text-foreground">{recommendationCount}</div>
              </div>
              <div className="rounded-2xl border border-border/60 bg-background/70 px-4 py-3 backdrop-blur">
                <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Señal dominante</div>
                <div className="mt-1 font-semibold text-foreground">{featuredReason}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <GlassCard>
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold">
          <Music className="h-4 w-4 text-muted-foreground" />
          Selecciona una playlist de referencia
        </div>
        <div className="flex flex-wrap gap-3">
          {availablePlaylists.map((playlist) => {
            const active = playlist.id === selectedPlaylistId;
            return (
              <button
                key={playlist.id}
                type="button"
                onClick={() => setSelectedPlaylistId(playlist.id)}
                className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                  active
                    ? "border-primary/40 bg-primary/15 text-primary shadow-lg shadow-primary/10"
                    : "border-border/60 bg-background/40 text-foreground hover:border-primary/25 hover:bg-primary/10"
                }`}
              >
                <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-xl bg-primary/15 text-lg font-semibold text-primary">
                  <CoverArt src={playlist.cover_url} alt={playlist.name} className="h-full w-full object-cover" />
                </div>
                <div className="min-w-0">
                  <div className="truncate font-medium">{playlist.name}</div>
                  <div className="truncate text-xs text-muted-foreground">
                    {playlist.id === "all" ? "Biblioteca completa" : playlist.description || "Playlist local"}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </GlassCard>

      {error && (
        <GlassCard className="border-destructive/50 bg-destructive/10 text-sm text-destructive">
          {error}
        </GlassCard>
      )}

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Star className="h-4 w-4 text-muted-foreground" />
              Canciones recomendadas para ti
            </h2>
            <p className="text-xs text-muted-foreground">
              Basado en {selectedPlaylist.id === "all" ? "tu actividad reciente" : `la playlist ${selectedPlaylist.name}`}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setReloadToken((value) => value + 1)}
            className="inline-flex items-center gap-2 rounded-xl border border-border/60 bg-background/50 px-3 py-2 text-xs text-muted-foreground transition hover:border-primary/30 hover:text-foreground"
            title="Recargar recomendaciones"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Actualizar
          </button>
        </div>

        {loading ? (
          <GlassCard className="text-sm text-muted-foreground">Calculando recomendaciones...</GlassCard>
        ) : recommendations.length === 0 ? (
          <GlassCard className="text-sm text-muted-foreground">
            {songs.length === 0
              ? "Necesitas tener canciones en tu biblioteca para buscar similitudes."
              : "Hacen falta los tokens de Spotify para buscar recomendaciones."}
          </GlassCard>
        ) : (
          <div className="grid gap-5 lg:grid-cols-2">
            {recommendations.map((song) => {
              const isPlaying = currentPlayingId === song.id;
              const suggestion = isSuggestion(song);
              const isExternal = !suggestion && song.source?.toLowerCase() !== "local" && !song.path;
              const isActionLoading = actionLoadingId === song.id;
              return (
                <button
                  key={song.id}
                  type="button"
                  onClick={() => handlePlay(song)}
                  className={`group flex min-h-[112px] items-center gap-5 rounded-3xl border border-border/60 bg-background/45 p-4 text-left transition sm:p-5 ${
                    suggestion
                      ? "cursor-default"
                      : "hover:-translate-y-0.5 hover:border-primary/35 hover:shadow-lg hover:shadow-primary/10"
                  }`}
                  disabled={isActionLoading || suggestion}
                >
                  <div className="h-20 w-20 shrink-0 overflow-hidden rounded-2xl bg-muted/40 sm:h-24 sm:w-24">
                    <CoverArt src={song.cover_url} alt={song.title} className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.04]" />
                  </div>
                  <div className="min-w-0 flex-1 space-y-2">
                    <div className="flex min-w-0 items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="truncate text-base font-semibold sm:text-lg">{song.title}</div>
                        <div className="truncate text-sm text-muted-foreground sm:text-base">{song.artist}</div>
                      </div>
                      <SourceBadge source={song.source || "local"} />
                    </div>
                    <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground sm:text-sm">
                      <span className="truncate">{song.album || song.genre || "Sin álbum"}</span>
                      <span className={isPlaying ? "text-primary" : ""}>
                        {suggestion
                          ? "Sugerencia"
                          : isExternal
                          ? isActionLoading
                            ? "Importando..."
                            : "Importar"
                          : isPlaying
                          ? "Reproduciendo"
                          : "Escuchar"}
                      </span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
              Sigue con tu biblioteca
            </h2>
            <p className="text-xs text-muted-foreground">
              Canciones recientes para acompañar las recomendaciones principales.
            </p>
          </div>
          <div className="text-xs text-muted-foreground">
            {discoverySongs.length} pistas recientes
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {discoverySongs.map((song) => {
            const isPlaying = currentPlayingId === song.id;
            return (
              <button
                key={song.id}
                type="button"
                onClick={() => handlePlaySong(song)}
                className="group flex items-center gap-4 rounded-3xl border border-border/60 bg-background/40 p-3 text-left transition hover:-translate-y-0.5 hover:border-primary/35 hover:shadow-lg hover:shadow-primary/10"
              >
                <div className="h-16 w-16 shrink-0 overflow-hidden rounded-2xl bg-muted/40">
                  <CoverArt src={song.cover_url} alt={song.title} className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.04]" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate font-semibold">{song.title}</div>
                  <div className="truncate text-sm text-muted-foreground">{song.artist}</div>
                  <div className="mt-1 flex items-center justify-between gap-2 text-xs text-muted-foreground">
                    <span className="truncate">{song.album || song.genre || "Sin álbum"}</span>
                    <span className={isPlaying ? "text-primary" : ""}>{isPlaying ? "Reproduciendo" : "Escuchar"}</span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      <GlassCard>
        <h2 className="mb-2 text-lg font-semibold">Cómo se buscan</h2>
        <ul className="list-inside list-disc space-y-1.5 text-sm text-muted-foreground">
          <li>Se crea una preferencia basada en tu tu historial y tu biblioteca.</li>
          <li>Se identifican canciones similares por artista y género, haciendo cálculos basados en tu preferencia musical.</li>
          <li>Cuando se importa una recomendación externa, el audio se resuelve y descarga desde YouTube.</li>
        </ul>
      </GlassCard>
    </div>
  );
}
