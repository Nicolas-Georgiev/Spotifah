import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { bridge } from "./bridge";

type Theme = "default" | "dark" | "light";

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function isValidTheme(t: string): t is Theme {
  return t === "default" || t === "dark" || t === "light";
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.setAttribute("data-theme", theme);
  if (theme === "dark" || theme === "default") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

function getDOMTheme(): Theme {
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr === "default" || attr === "dark" || attr === "light") return attr;
  return "default";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(getDOMTheme);

  useEffect(() => {
    bridge.getSettings().then((s) => {
      const t = isValidTheme(s.theme) ? s.theme : "default";
      applyTheme(t);
      setThemeState(t);
    });
  }, []);

  const setTheme = (t: Theme) => {
    applyTheme(t);
    setThemeState(t);
    bridge.updateSettings({ theme: t });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within <ThemeProvider>");
  return ctx;
}
