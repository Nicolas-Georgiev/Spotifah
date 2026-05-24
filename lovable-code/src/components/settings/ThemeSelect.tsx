import { useTheme } from "../../lib/theme-provider";
import { SegmentedControl } from "./SegmentedControl";

const themes = [
  {
    value: "default",
    label: "Default",
    indicator: "bg-[oklch(0.75_0.21_305)]",
  },
  {
    value: "dark",
    label: "Oscuro",
    indicator: "bg-[oklch(0.7_0.08_285)]",
  },
  {
    value: "light",
    label: "Claro",
    indicator: "bg-[oklch(0.97_0.005_280)] border-2 border-border",
  },
];

export function ThemeSelect() {
  const { theme, setTheme } = useTheme();

  return (
    <SegmentedControl
      value={theme}
      onChange={setTheme}
      options={themes}
    />
  );
}
