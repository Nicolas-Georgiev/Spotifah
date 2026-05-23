import { useState, useRef, useEffect } from "react";
import { ListMusic, Check, TriangleAlert, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { bridge } from "../../lib/bridge";
import type { ImportProgress } from "../../lib/bridge";

interface Props {
  taskId: string;
  onComplete: (playlistId: number) => void;
}

export function PlaylistImport({ taskId, onComplete }: Props) {
  const [progress, setProgress] = useState<ImportProgress | null>(null);
  const [showLog, setShowLog] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    pollRef.current = setInterval(async () => {
      const res = await bridge.getImportProgress(taskId);
      if (res.ok && res.data) {
        setProgress(res.data);
        if (res.data.status === "done" || res.data.status === "error") {
          if (pollRef.current) clearInterval(pollRef.current);
          if (res.data.status === "done" && res.data.playlist_id) {
            onComplete(res.data.playlist_id);
          }
        }
      }
    }, 1000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [taskId, onComplete]);

  if (!progress) {
    return (
      <div className="p-4 rounded-lg bg-muted/20 flex items-center gap-3">
        <Loader2 className="w-5 h-5 animate-spin text-primary" />
        <span className="text-sm text-muted-foreground">Iniciando importación...</span>
      </div>
    );
  }

  const isRunning = progress.status === "starting" || progress.status === "running";
  const isDone = progress.status === "done";
  const isError = progress.status === "error";
  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0;
  const hasLog = progress.log?.trim().length > 0;

  return (
    <div className="p-4 rounded-lg bg-muted/20 space-y-3">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-md bg-primary/15 grid place-items-center shrink-0">
          {isDone ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : isError ? (
            <TriangleAlert className="w-4 h-4 text-red-400" />
          ) : (
            <ListMusic className="w-4 h-4 text-primary" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">
            {progress.playlist_name || "Importando playlist..."}
          </p>
          {isRunning && progress.total > 0 && (
            <p className="text-xs text-muted-foreground mt-0.5">
              {progress.current} de {progress.total} canciones
            </p>
          )}
          {isDone && (
            <p className="text-xs text-green-400 mt-0.5">
              {progress.total} canciones importadas
            </p>
          )}
          {isError && (
            <p className="text-xs text-red-400 mt-0.5 truncate">
              {progress.error || "Error al importar"}
            </p>
          )}
        </div>
        {isRunning && (
          <span className="text-xs text-muted-foreground shrink-0">{pct}%</span>
        )}
        {isDone && (
          <span className="text-xs text-green-400 shrink-0">Listo</span>
        )}
        {isError && (
          <span className="text-xs text-red-400 shrink-0">Error</span>
        )}
      </div>

      {isRunning && progress.total > 0 && (
        <div className="w-full bg-muted/40 rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}

      {hasLog && (
        <>
          <button
            onClick={() => setShowLog(!showLog)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
          >
            {showLog ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            {showLog ? "Ocultar detalles" : "Ver detalles"}
          </button>
          {showLog && (
            <pre className="p-2 rounded bg-black/40 text-xs text-muted-foreground font-mono whitespace-pre-wrap max-h-48 overflow-y-auto">
              {progress.log}
            </pre>
          )}
        </>
      )}
    </div>
  );
}
