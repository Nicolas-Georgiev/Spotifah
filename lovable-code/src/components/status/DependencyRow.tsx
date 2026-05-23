import { StatusBadge } from "./StatusBadge";

interface Props {
  label: string;
  ok: boolean;
}

export function DependencyRow({ label, ok }: Props) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/20">
      <span className="text-sm font-mono">{label}</span>
      <StatusBadge ok={ok} label={ok ? "Instalado" : "No instalado"} />
    </div>
  );
}
