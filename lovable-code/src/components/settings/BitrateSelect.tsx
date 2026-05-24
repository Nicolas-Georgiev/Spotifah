import { SegmentedControl } from "./SegmentedControl";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const bitrates = [
  { value: "128", label: "128k" },
  { value: "192", label: "192k" },
  { value: "256", label: "256k" },
  { value: "320", label: "320k" },
];

export function BitrateSelect({ value, onChange }: Props) {
  return (
    <>
      <label className="text-xs font-medium text-muted-foreground">Bitrate</label>
      <div className="mt-1.5">
        <SegmentedControl
          value={value}
          onChange={onChange}
          options={bitrates}
        />
      </div>
    </>
  );
}
