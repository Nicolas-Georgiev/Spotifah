/* eslint-disable @typescript-eslint/no-explicit-any, no-empty */

export interface Song {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: number;
  genre: string;
  source: string;
  path: string;
  cover_url: string;
  is_downloaded?: boolean;
  download_date?: string;
}
export interface RecommendedSong extends Song {
  score: number;
  reason: string;
  play_count?: number;
  added_at?: string;
}

export interface Playlist {
  id: string;
  name: string;
  description: string;
  is_public: boolean;
  cover_url: string;
}

interface ConvertResult {
  ok: boolean;
  data?: { path: string; filename: string; log: string };
  error?: string;
}

interface ActionResult {
  ok: boolean;
  data?: { message: string };
  error?: string;
}

interface AddToPlaylistResult {
  ok: boolean;
  data?: { message: string; already_exists: boolean };
  error?: string;
}

interface SystemStatus {
  dependencies: Record<string, boolean>;
  ffmpeg: boolean;
  music_count: number;
}

export interface NowPlayingData {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: number;
  cover_url: string;
  is_playing: boolean;
  position: number;
  shuffle: boolean;
  repeat: string;
}

interface NowPlayingResult {
  ok: boolean;
  data?: NowPlayingData | null;
  debug?: Record<string, unknown>;
}

interface PlaybackPosition {
  position: number;
  is_playing: boolean;
}

interface VolumeData {
  volume: number;
}

interface FavoriteData {
  favorite: boolean;
}

interface CreatePlaylistResult {
  ok: boolean;
  data?: { id: string; name: string; description: string; is_public: boolean };
  error?: string;
}

interface UrlTypeResult {
  platform: string | null;
  is_playlist: boolean;
}

interface ImportPlaylistResult {
  ok: boolean;
  data?: { task_id: string; platform: string };
  error?: string;
}

interface ImportProgress {
  status: "starting" | "running" | "done" | "error";
  platform: string;
  current: number;
  total: number;
  playlist_name: string;
  playlist_id: number | null;
  error: string | null;
  log: string;
}

export interface TrackPreview {
  title: string;
  artist: string;
  duration: number;
}

export interface AlbumPreviewData {
  platform: string;
  name: string;
  artist: string;
  year: number | null;
  cover_url: string;
  is_album: boolean;
  total_tracks: number;
  tracks: TrackPreview[];
}

interface AlbumPreviewResult {
  ok: boolean;
  data?: AlbumPreviewData;
  error?: string;
}

function getApi() {
  try {
    return (window as any)?.pywebview?.api ?? null;
  } catch {
    return null;
  }
}

const SETTINGS_KEY = "ekho_settings";

function saveToLocal(key: string, value: any) {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    const data = raw ? JSON.parse(raw) : {};
    data[key] = value;
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(data));
  } catch {}
}

function loadFromLocal(): Record<string, any> {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

async function apiCall<T>(method: string, ...args: any[]): Promise<T | null> {
  const api = getApi();
  if (!api) return null;
  try {
    const fn = api[method];
    if (typeof fn !== "function") return null;
    return (await fn(...args)) as T;
  } catch {
    return null;
  }
}

async function apiCallOk<T = ActionResult>(
  method: string,
  ...args: any[]
): Promise<{ ok: boolean; data?: T; error?: string }> {
  const api = getApi();
  if (!api) return { ok: false, error: "PyWebView no disponible" };
  try {
    const fn = api[method];
    if (typeof fn !== "function") return { ok: false, error: `Metodo ${method} no encontrado` };
    return await fn(...args);
  } catch (e: any) {
    return { ok: false, error: e?.message ?? "Error" };
  }
}

async function apiArray<T>(method: string, ...args: any[]): Promise<T[]> {
  const result = await apiCall<any>(method, ...args);
  return Array.isArray(result) ? result : [];
}

export const bridge = {
  getPlaylists(): Promise<Playlist[]> {
    return apiArray<Playlist>("get_playlists");
  },

  getPlaylistSongs(playlistId: string): Promise<Song[]> {
    return apiArray<Song>("get_playlist_songs", playlistId);
  },

  getSongs(): Promise<Song[]> {
    return bridge.getPlaylistSongs("all");
  },

  getRecommendations(playlistId: string = "all", limit: number = 8): Promise<RecommendedSong[]> {
    return apiArray<RecommendedSong>("get_recommendations", playlistId, limit);
  },

  convertYoutube(url: string): Promise<ConvertResult> {
    return apiCallOk<ConvertResult["data"]>("convert_youtube", url) as Promise<ConvertResult>;
  },

  convertSpotify(url: string): Promise<ConvertResult> {
    return apiCallOk<ConvertResult["data"]>("convert_spotify", url) as Promise<ConvertResult>;
  },

  async playSong(songId: string, songIds?: string[]): Promise<ActionResult> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible" };
    try {
      if (songIds && songIds.length > 0) {
        return await api.play_song(songId, songIds);
      }
      return await api.play_song(songId);
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error al reproducir" };
    }
  },

  pauseSong(): Promise<ActionResult> {
    return apiCallOk("pause_song");
  },

  resumeSong(): Promise<ActionResult> {
    return apiCallOk("resume_song");
  },

  stopSong(): Promise<ActionResult> {
    return apiCallOk("stop_song");
  },

  seekSong(position: number): Promise<ActionResult> {
    return apiCallOk("seek_song", position);
  },

  nextSong(): Promise<ActionResult & { data?: { message: string; now_playing: NowPlayingData | null } }> {
    return apiCallOk("next_song");
  },

  prevSong(): Promise<ActionResult & { data?: { message: string; now_playing: NowPlayingData | null } }> {
    return apiCallOk("prev_song");
  },

  toggleShuffle(): Promise<{ ok: boolean; data?: { shuffle: boolean }; error?: string }> {
    return apiCallOk("toggle_shuffle");
  },

  cycleRepeat(): Promise<{ ok: boolean; data?: { repeat: string }; error?: string }> {
    return apiCallOk("cycle_repeat");
  },

  async getSettings(): Promise<Record<string, any>> {
    const local = loadFromLocal();
    const api = getApi();
    if (!api) return local;
    try {
      const backend = await api.get_settings();
      return { ...backend, ...local };
    } catch {
      return local;
    }
  },

  async updateSettings(data: Record<string, any>): Promise<ActionResult> {
    for (const [key, value] of Object.entries(data)) {
      if (key !== "theme") {
        saveToLocal(key, value);
      }
    }
    return apiCallOk("update_settings", data);
  },

  selectFolderDialog(): Promise<{ ok: boolean; data?: { path: string }; error?: string }> {
    return apiCallOk("select_folder_dialog");
  },

  selectFilesDialog(): Promise<{ ok: boolean; data?: { files: string[] }; error?: string }> {
    return apiCallOk<{ files: string[] }>("select_files_dialog");
  },

  importLocalFiles(filePaths: string[]): Promise<{
    ok: boolean;
    data?: { imported: Song[]; errors: { file: string; error: string }[]; total: number };
    error?: string;
  }> {
    return apiCallOk("import_local_files", filePaths);
  },

  async getSystemStatus(): Promise<SystemStatus> {
    const result = await apiCall<SystemStatus>("get_system_status");
    return result ?? { dependencies: {}, ffmpeg: false, music_count: 0 };
  },

  addSongToPlaylist(playlistId: string, songId: string): Promise<AddToPlaylistResult> {
    return apiCallOk("add_song_to_playlist", playlistId, songId);
  },

  removeSongFromPlaylist(playlistId: string, songId: string): Promise<ActionResult> {
    return apiCallOk("remove_song_from_playlist", playlistId, songId);
  },

  deleteSong(songId: string): Promise<ActionResult> {
    return apiCallOk("delete_song", songId);
  },

  updateSong(
    songId: string,
    data: {
      title?: string;
      artist?: string;
      album?: string;
      genre?: string;
      cover_base64?: string;
    },
  ): Promise<ActionResult> {
    return apiCallOk("update_song", songId, data);
  },

  convertSoundcloud(url: string): Promise<ConvertResult> {
    return apiCallOk("convert_soundcloud", url) as Promise<ConvertResult>;
  },

  async detectUrlType(url: string): Promise<UrlTypeResult> {
    const result = await apiCall<UrlTypeResult>("detect_url_type", url);
    return result ?? { platform: null, is_playlist: false };
  },

  importPlaylist(url: string): Promise<ImportPlaylistResult> {
    return apiCallOk("import_playlist", url);
  },

  getAlbumPreview(url: string): Promise<AlbumPreviewResult> {
    return apiCallOk("get_album_preview", url);
  },

  importAlbum(url: string): Promise<ImportPlaylistResult> {
    return apiCallOk("import_album", url);
  },

  getImportProgress(
    taskId: string,
  ): Promise<{ ok: boolean; data?: ImportProgress; error?: string }> {
    return apiCallOk("get_import_progress", taskId);
  },

  createPlaylist(name: string, description: string = ""): Promise<CreatePlaylistResult> {
    return apiCallOk("create_playlist", name, description);
  },

  deletePlaylist(playlistId: string): Promise<ActionResult> {
    return apiCallOk("delete_playlist", playlistId);
  },

  renamePlaylist(
    playlistId: string,
    name: string,
    description: string = "",
    cover_base64?: string,
  ): Promise<ActionResult> {
    return apiCallOk("rename_playlist", playlistId, name, description, cover_base64 || "");
  },

  searchSongs(query: string): Promise<Song[]> {
    return apiArray<Song>("search_songs", query);
  },

  async toggleFavorite(songId: string): Promise<FavoriteData & { ok: boolean; error?: string }> {
    const api = getApi();
    if (!api) return { ok: false, error: "PyWebView no disponible", favorite: false };
    try {
      const result = await api.toggle_favorite(songId);
      return { ok: result.ok, favorite: result.data?.favorite ?? false, error: result.error };
    } catch (e: any) {
      return { ok: false, error: e?.message ?? "Error", favorite: false };
    }
  },

  async isFavorite(songId: string): Promise<{ ok: boolean; favorite: boolean }> {
    const api = getApi();
    if (!api) return { ok: false, favorite: false };
    try {
      const res = await api.is_favorite(songId);
      return { ok: true, favorite: res.data?.favorite ?? false };
    } catch {
      return { ok: false, favorite: false };
    }
  },

  async getNowPlaying(): Promise<NowPlayingResult> {
    const api = getApi();
    if (!api) return { ok: true, data: null };
    try {
      const fn = api.get_now_playing;
      if (typeof fn !== "function") return { ok: true, data: null };
      return await fn() as NowPlayingResult;
    } catch {
      return { ok: true, data: null };
    }
  },

  async getPlaybackPosition(): Promise<PlaybackPosition> {
    const result = await apiCall<{ data: PlaybackPosition }>("get_playback_position");
    return result?.data ?? { position: 0, is_playing: false };
  },

  setVolume(volume: number): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    return apiCallOk("set_volume", volume);
  },

  async getVolume(): Promise<{ ok: boolean; data?: VolumeData; error?: string }> {
    const result = await apiCall<{ ok: boolean; data?: VolumeData }>("get_volume");
    return result ?? { ok: false, error: "No se pudo obtener el volumen" };
  },

  getRecentlyPlayed(limit: number = 10): Promise<Song[]> {
    return apiArray<Song>("get_recently_played", limit);
  },

  async deletePreviewCover(coverUrl: string): Promise<void> {
    const api = getApi();
    if (!api) return;
    try {
      await api.delete_preview_cover(coverUrl);
    } catch {}
  },
};

export { fmtDuration };
