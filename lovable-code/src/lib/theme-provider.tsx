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
    const loadTheme = () => {
      bridge.getSettings().then((s) => {
        // Only apply if we got a valid theme from the API.
        // If the API wasn't ready yet, s.theme will be undefined (no theme in
        // localStorage) and we must NOT fall back to "default" — that would
        // override the correct theme already injected by the server into the DOM.
        if (isValidTheme(s.theme)) {
          applyTheme(s.theme);
          setThemeState(s.theme);
        }
      });
    };

    loadTheme(); // Attempt immediately (works when pywebview API is already ready)

    // Also listen for pywebviewready in case the JS bridge isn't injected yet
    // when React first mounts (common timing issue with pywebview).
    window.addEventListener("pywebviewready", loadTheme);
    return () => window.removeEventListener("pywebviewready", loadTheme);
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
