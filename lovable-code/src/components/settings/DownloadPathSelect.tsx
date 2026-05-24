import { bridge } from "../../lib/bridge";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function DownloadPathSelect({ value, onChange }: Props) {
  const handleSelect = async () => {
    const result = await bridge.selectFolderDialog();
    if (result.ok && result.data?.path) {
      onChange(result.data.path);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleSelect}
        className="shrink-0 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition"
      >
        Seleccionar carpeta
      </button>
      <span className="text-sm text-muted-foreground truncate min-w-0" title={value}>
        {value || "No configurado"}
      </span>
    </div>
  );
}
