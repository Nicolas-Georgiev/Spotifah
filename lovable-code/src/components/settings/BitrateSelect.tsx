interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function BitrateSelect({ value, onChange }: Props) {
  return (
    <>
      <label className="text-xs font-medium text-muted-foreground">Bitrate</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1.5 w-full bg-input/60 border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="128">128 kbps</option>
        <option value="192">192 kbps</option>
        <option value="256">256 kbps</option>
        <option value="320">320 kbps</option>
      </select>
    </>
  );
}
