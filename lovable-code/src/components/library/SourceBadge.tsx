const SOURCE_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  youtube: { bg: "bg-red-500/20", text: "text-red-400", border: "border-red-500/30" },
  spotify: { bg: "bg-green-500/20", text: "text-green-400", border: "border-green-500/30" },
  soundcloud: { bg: "bg-yellow-500/20", text: "text-yellow-400", border: "border-yellow-500/30" },
};

const DEFAULT_STYLE = { bg: "bg-gray-500/20", text: "text-gray-400", border: "border-gray-500/30" };

interface Props {
  source: string;
}

export function SourceBadge({ source }: Props) {
  const style = SOURCE_STYLES[source.toLowerCase()] ?? DEFAULT_STYLE;
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text} ${style.border}`}>
      {source || "local"}
    </span>
  );
}
