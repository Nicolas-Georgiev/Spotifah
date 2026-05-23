import { Check, X } from "lucide-react";

interface Props {
  ok: boolean;
  label: string;
}

export function StatusBadge({ ok, label }: Props) {
  if (ok) {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-green-400">
        <Check className="w-3.5 h-3.5" /> {label}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs text-red-400">
      <X className="w-3.5 h-3.5" /> {label}
    </span>
  );
}
