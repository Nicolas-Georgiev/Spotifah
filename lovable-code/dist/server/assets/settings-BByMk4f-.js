import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { c as createLucideIcon, b as bridge, D as Download, M as Music2 } from "./router-DfCIbLxF.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
const __iconNode$1 = [
  ["path", { d: "M10.268 21a2 2 0 0 0 3.464 0", key: "vwvbt9" }],
  [
    "path",
    {
      d: "M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326",
      key: "11g9vi"
    }
  ]
];
const Bell = createLucideIcon("bell", __iconNode$1);
const __iconNode = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "M12 16v-4", key: "1dtifu" }],
  ["path", { d: "M12 8h.01", key: "e9boi3" }]
];
const Info = createLucideIcon("info", __iconNode);
function SettingsPage() {
  const [settings, setSettings] = reactExports.useState({});
  const [loaded, setLoaded] = reactExports.useState(false);
  reactExports.useEffect(() => {
    bridge.getSettings().then((s) => {
      setSettings(s);
      setLoaded(true);
    });
  }, []);
  const update = async (key, value) => {
    const next = {
      ...settings,
      [key]: value
    };
    setSettings(next);
    await bridge.updateSettings({
      [key]: value
    });
  };
  if (!loaded) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center py-20", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground", children: "Cargando configuracion..." }) });
  }
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-8", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-4xl font-bold", children: "Configuracion" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-2", children: "Personaliza tu experiencia en EKHO" })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs(Card, { icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-5 h-5" }), iconBg: "bg-secondary/25 text-secondary", title: "Calidad de Descarga", subtitle: "Bitrate predeterminado para conversiones a MP3", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("label", { className: "text-xs font-medium text-muted-foreground", children: "Bitrate" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("select", { value: settings.download_quality ?? "192", onChange: (e) => update("download_quality", e.target.value), className: "mt-1.5 w-full bg-input/60 border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "128", children: "128 kbps" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "192", children: "192 kbps" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "256", children: "256 kbps" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("option", { value: "320", children: "320 kbps" })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Bell, { className: "w-5 h-5" }), iconBg: "bg-yellow-500/25 text-yellow-400", title: "Notificaciones", subtitle: "Recibe avisos cuando se completen las conversiones", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Toggle, { label: "Notificaciones del sistema", value: settings.notifications ?? true, onChange: (v) => update("notifications", v) }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Music2, { className: "w-5 h-5" }), iconBg: "bg-primary/25 text-primary", title: "Reproduccion", subtitle: "Comportamiento del reproductor de musica", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Toggle, { label: "Reproduccion automatica al abrir playlist", value: settings.autoplay ?? false, onChange: (v) => update("autoplay", v) }) }),
    /* @__PURE__ */ jsxRuntimeExports.jsx(Card, { icon: /* @__PURE__ */ jsxRuntimeExports.jsx(Info, { className: "w-5 h-5" }), iconBg: "bg-muted/60 text-muted-foreground", title: "Acerca de", subtitle: "Informacion sobre EKHO", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-2 gap-3 text-sm font-mono", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-muted-foreground", children: "Version" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "v0.1.0" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-muted-foreground", children: "Build" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "2026.05.11" })
    ] }) })
  ] });
}
function Card({
  icon,
  iconBg,
  title,
  subtitle,
  children
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsx("section", { className: "glass rounded-2xl p-5 sm:p-6", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-start gap-4", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: `w-11 h-11 rounded-xl grid place-items-center shrink-0 ${iconBg}`, children: icon }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold", children: title }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-0.5", children: subtitle }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "mt-4", children })
    ] })
  ] }) });
}
function Toggle({
  label,
  value,
  onChange
}) {
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("button", { onClick: () => onChange(!value), className: "w-full flex items-center justify-between p-3 rounded-lg bg-muted/20 hover:bg-muted/30 transition", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm", children: label }),
    /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `relative w-11 h-6 rounded-full transition ${value ? "bg-primary" : "bg-muted"}`, children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: `absolute top-0.5 ${value ? "left-5" : "left-0.5"} w-5 h-5 rounded-full bg-background transition-all` }) })
  ] });
}
export {
  SettingsPage as component
};
