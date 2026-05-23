import { Loader2, Check, TriangleAlert } from "lucide-react";

type Status = "processing" | "done" | "error";

interface Props {
  status: Status;
  error?: string;
}

export function ConversionStatusBadge({ status, error }: Props) {
  if (status === "processing") {
    return (
      <span className="text-xs text-muted-foreground inline-flex items-center gap-1 shrink-0">
        <Loader2 className="w-3 h-3 animate-spin" /> Procesando...
      </span>
    );
  }
  if (status === "done") {
    return (
      <span className="text-xs text-green-400 inline-flex items-center gap-1 shrink-0">
        <Check className="w-3 h-3" /> Listo
      </span>
    );
  }
  return (
    <span className="text-xs text-red-400 inline-flex items-center gap-1 shrink-0" title={error}>
      <TriangleAlert className="w-3 h-3 shrink-0" /> Error
      {error && <span className="max-w-[200px] truncate text-red-300/70">{error}</span>}
    </span>
  );
}
