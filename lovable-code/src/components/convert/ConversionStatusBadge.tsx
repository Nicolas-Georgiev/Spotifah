import { Loader2, Check } from "lucide-react";

type Status = "processing" | "done" | "error";

interface Props {
  status: Status;
  error?: string;
}

export function ConversionStatusBadge({ status, error }: Props) {
  if (status === "processing") {
    return (
      <span className="text-xs text-muted-foreground inline-flex items-center gap-1">
        <Loader2 className="w-3 h-3 animate-spin" /> Procesando...
      </span>
    );
  }
  if (status === "done") {
    return (
      <span className="text-xs text-green-400 inline-flex items-center gap-1">
        <Check className="w-3 h-3" /> Listo
      </span>
    );
  }
  return (
    <span className="text-xs text-red-400" title={error}>
      Error
    </span>
  );
}
