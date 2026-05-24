interface Option {
  value: string;
  label: string;
  indicator?: string;
}

interface Props {
  value: string;
  onChange: (value: string) => void;
  options: Option[];
}

export function SegmentedControl({ value, onChange, options }: Props) {
  return (
    <div className="bg-input/30 rounded-xl p-1 flex gap-1 w-full">
      {options.map((opt) => {
        const active = value === opt.value;
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={`flex-1 rounded-lg py-2 px-3 text-sm font-medium flex items-center justify-center gap-2 transition-all ${
              active
                ? "bg-card shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {opt.indicator && (
              <span className={`w-3.5 h-3.5 rounded-full shrink-0 ${opt.indicator}`} />
            )}
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
