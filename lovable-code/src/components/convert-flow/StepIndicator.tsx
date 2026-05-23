import { Check, Loader2 } from "lucide-react";
import type { ThemeStyle } from "./types";

interface Props {
  step: { icon: string; label: string };
  index: number;
  completed: boolean;
  active: boolean;
  theme: ThemeStyle;
}

export function StepIndicator({ step, index, completed, active, theme }: Props) {
  return (
    <li className={`flex items-center gap-3 font-mono text-sm ${completed ? theme.color : active ? "text-foreground" : "text-muted-foreground/50"}`}>
      <div className={`w-6 h-6 rounded-full grid place-items-center border ${completed ? `${theme.border} ${theme.bg}/20` : "border-border"}`}>
        {completed ? (
          <Check className="w-3.5 h-3.5" />
        ) : active ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <span className="text-xs">{index + 1}</span>
        )}
      </div>
      <span>{step.icon} {step.label}</span>
    </li>
  );
}
