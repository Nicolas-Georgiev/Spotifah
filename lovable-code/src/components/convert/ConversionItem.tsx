import { Youtube, Music2, Cloud } from "lucide-react";
import { ConversionStatusBadge } from "./ConversionStatusBadge";

interface ConvItem {
  id: number;
  title: string;
  platform: "youtube" | "spotify" | "soundcloud";
  status: "processing" | "done" | "error";
  error?: string;
}

interface Props {
  item: ConvItem;
}

const platformIcon: Record<string, { icon: typeof Youtube; color: string }> = {
  youtube: { icon: Youtube, color: "text-red-400" },
  spotify: { icon: Music2, color: "text-green-400" },
  soundcloud: { icon: Cloud, color: "text-yellow-400" },
};

export function ConversionItem({ item }: Props) {
  const info = platformIcon[item.platform];
  const Icon = info.icon;

  return (
    <li className="flex items-center gap-3 p-3 rounded-lg bg-muted/20">
      <div className="w-9 h-9 rounded-md bg-primary/15 grid place-items-center">
        <Icon className={`w-4 h-4 ${info.color}`} />
      </div>
      <p className="flex-1 truncate text-sm font-mono">{item.title}</p>
      <ConversionStatusBadge status={item.status} error={item.error} />
    </li>
  );
}
