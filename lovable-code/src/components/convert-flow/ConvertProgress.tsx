import { StepIndicator } from "./StepIndicator";
import type { ThemeStyle } from "./types";

interface Step { icon: string; label: string; }

interface Props {
  steps: Step[];
  stepIdx: number;
  done: boolean;
  theme: ThemeStyle;
}

export function ConvertProgress({ steps, stepIdx, done, theme }: Props) {
  return (
    <div className="glass rounded-2xl p-6">
      <h3 className="font-mono text-sm text-muted-foreground mb-4">// Progreso</h3>
      <ol className="space-y-3">
        {steps.map((s, i) => (
          <StepIndicator
            key={i}
            step={s}
            index={i}
            completed={i < stepIdx || done}
            active={i === stepIdx && !done}
            theme={theme}
          />
        ))}
      </ol>
    </div>
  );
}
