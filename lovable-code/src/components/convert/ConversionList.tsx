import { Download } from "lucide-react";
import { ConversionItem } from "./ConversionItem";

interface ConvItem {
  id: number;
  title: string;
  platform: "youtube" | "spotify" | "soundcloud";
  status: "processing" | "done" | "error";
  error?: string;
}

interface Props {
  items: ConvItem[];
}

export function ConversionList({ items }: Props) {
  return (
    <section>
      <h2 className="text-xl font-semibold mb-3">Conversiones Recientes</h2>
      <div className="glass rounded-2xl p-6 min-h-[220px]">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <div className="w-14 h-14 rounded-full bg-muted/40 grid place-items-center mb-4">
              <Download className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground">No hay conversiones todavia</p>
            <p className="text-xs text-muted-foreground/70 mt-2">Pega un enlace arriba para comenzar</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {items.map((i) => (
              <ConversionItem key={i.id} item={i} />
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
