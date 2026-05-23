interface Props {
  source: string;
}

export function SourceBadge({ source }: Props) {
  if (source === "spotify") {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
        spotify
      </span>
    );
  }
  return (
    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30">
      {source || "local"}
    </span>
  );
}
