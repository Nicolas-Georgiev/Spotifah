export interface ThemeStyle {
  color: string;
  border: string;
  bg: string;
  glow: string;
  text: string;
}

export type ConvertTheme = "spotify" | "youtube";

export const themeMap: Record<ConvertTheme, ThemeStyle> = {
  spotify: {
    color: "text-[oklch(0.85_0.22_150)]",
    border: "border-[oklch(0.85_0.22_150)]/50",
    bg: "bg-[oklch(0.85_0.22_150)]",
    glow: "glow-green",
    text: "text-glow-green",
  },
  youtube: {
    color: "text-[oklch(0.65_0.25_25)]",
    border: "border-[oklch(0.65_0.25_25)]/50",
    bg: "bg-[oklch(0.65_0.25_25)]",
    glow: "glow-red",
    text: "text-glow-red",
  },
};
