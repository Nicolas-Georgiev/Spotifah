import { useState, useCallback } from "react";
import { Music, FileUp, CheckCircle2, XCircle, Loader2, FileMusic } from "lucide-react";
import { bridge, type Song } from "../../lib/bridge";

interface PendingFile {
  path: string;
  name: string;
  size: string;
}

interface LocalFileImportResult {
  imported: Song[];
  errors: { file: string; error: string }[];
  total: number;
}

export function LocalFileImport() {
  const [selectedFiles, setSelectedFiles] = useState<PendingFile[]>([]);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<LocalFileImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectFiles = useCallback(async () => {
    setError(null);
    setResult(null);
    const res = await bridge.selectFilesDialog();
    if (res.ok && res.data?.files && res.data.files.length > 0) {
      const files = res.data.files.map((path: string) => {
        const parts = path.replace(/\\/g, "/").split("/");
        return {
          path,
          name: parts[parts.length - 1],
          size: "",
        };
      });
      setSelectedFiles(files);
    } else if (res.error && res.error !== "No se seleccionaron archivos") {
      setError(res.error);
    }
  }, []);

  const handleImport = useCallback(async () => {
    if (selectedFiles.length === 0) return;
    setImporting(true);
    setError(null);
    setResult(null);
    try {
      const res = await bridge.importLocalFiles(selectedFiles.map((f) => f.path));
      if (res.ok && res.data) {
        setResult(res.data);
        if (res.data.imported.length > 0) {
          setSelectedFiles([]);
        }
      } else {
        setError(res.error || "Error al importar archivos");
      }
    } catch (e: any) {
      setError(e?.message || "Error al importar");
    } finally {
      setImporting(false);
    }
  }, [selectedFiles]);

  const formatSize = (path: string): string => {
    try {
      const size = (bridge as any).getFileSize?.(path);
      if (size) {
        const mb = (size / (1024 * 1024)).toFixed(1);
        return `${mb} MB`;
      }
    } catch {}
    return "";
  };

  const clearAll = useCallback(() => {
    setSelectedFiles([]);
    setResult(null);
    setError(null);
  }, []);

  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <FileMusic className="w-5 h-5 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Importar desde local</h2>
      </div>

      <div className="glass rounded-2xl p-5">
        {selectedFiles.length === 0 && !result && (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="w-14 h-14 rounded-full bg-muted/40 grid place-items-center mb-4">
              <FileUp className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground mb-4">Selecciona archivos de audio desde tu computadora</p>
            <button
              onClick={handleSelectFiles}
              disabled={importing}
              className="px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground hover:opacity-90 glow-violet inline-flex items-center gap-2 justify-center text-sm disabled:opacity-50"
            >
              <FileUp className="w-4 h-4" />
              Seleccionar archivos
            </button>
          </div>
        )}

        {selectedFiles.length > 0 && !importing && !result && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {selectedFiles.length} archivo{selectedFiles.length !== 1 ? "s" : ""} seleccionado{selectedFiles.length !== 1 ? "s" : ""}
              </p>
              <button
                onClick={clearAll}
                className="text-xs text-muted-foreground hover:text-foreground transition"
              >
                Limpiar
              </button>
            </div>
            <div className="max-h-60 overflow-y-auto space-y-1">
              {selectedFiles.slice(0, 20).map((file, i) => (
                <div key={i} className="flex items-center gap-3 py-2 px-3 rounded-lg bg-muted/20 text-sm">
                  <Music className="w-4 h-4 text-muted-foreground shrink-0" />
                  <span className="flex-1 truncate">{file.name}</span>
                </div>
              ))}
              {selectedFiles.length > 20 && (
                <p className="text-xs text-muted-foreground px-3 pt-1">
                  y {selectedFiles.length - 20} más...
                </p>
              )}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleSelectFiles}
                className="px-4 py-2 rounded-lg font-medium border border-border text-sm hover:bg-muted/30 transition inline-flex items-center gap-2"
              >
                <FileUp className="w-4 h-4" />
                Agregar más
              </button>
              <button
                onClick={handleImport}
                className="px-6 py-2 rounded-lg font-medium bg-primary text-primary-foreground hover:opacity-90 glow-violet inline-flex items-center gap-2 text-sm"
              >
                <Loader2 className="w-4 h-4" />
                Importar a la biblioteca
              </button>
            </div>
          </div>
        )}

        {importing && (
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Importando canciones...</p>
            </div>
          </div>
        )}

        {result && !importing && (
          <div className="space-y-4">
            {result.imported.length > 0 && (
              <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                <div className="flex items-center gap-3 mb-3">
                  <CheckCircle2 className="w-5 h-5 text-green-400 shrink-0" />
                  <p className="text-sm font-medium text-green-400">
                    {result.total} cancion{result.total !== 1 ? "es" : ""} importada{result.total !== 1 ? "s" : ""} correctamente
                  </p>
                </div>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {result.imported.map((song, i) => (
                    <div key={i} className="flex items-center gap-3 py-1.5 px-3 rounded-lg bg-muted/20 text-sm">
                      <Music className="w-3.5 h-3.5 text-green-400 shrink-0" />
                      <span className="font-medium truncate">{song.title}</span>
                      {song.artist && (
                        <span className="text-muted-foreground truncate">— {song.artist}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {result.errors.length > 0 && (
              <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20">
                <div className="flex items-center gap-3 mb-2">
                  <XCircle className="w-5 h-5 text-destructive shrink-0" />
                  <p className="text-sm font-medium text-destructive">
                    {result.errors.length} error{result.errors.length !== 1 ? "es" : ""}
                  </p>
                </div>
                <div className="space-y-1">
                  {result.errors.map((err, i) => (
                    <p key={i} className="text-xs text-destructive/80">
                      {err.file.split(/[/\\]/).pop()}: {err.error}
                    </p>
                  ))}
                </div>
              </div>
            )}
            <button
              onClick={clearAll}
              className="px-4 py-2 rounded-lg font-medium border border-border text-sm hover:bg-muted/30 transition"
            >
              Importar más archivos
            </button>
          </div>
        )}

        {error && (
          <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
            {error}
          </div>
        )}
      </div>
    </section>
  );
}
