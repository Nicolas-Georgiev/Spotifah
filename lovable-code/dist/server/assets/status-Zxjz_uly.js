import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { c as createLucideIcon, b as bridge, S as Sparkles, M as Music2 } from "./router-DfCIbLxF.js";
import { C as Check } from "./check-Bh0eiIFu.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
const __iconNode = [
  ["path", { d: "M18 6 6 18", key: "1bl5f8" }],
  ["path", { d: "m6 6 12 12", key: "d8bk6v" }]
];
const X = createLucideIcon("x", __iconNode);
const DEP_NAMES = {
  spotdl: "SpotDL",
  yt_dlp: "yt-dlp",
  moviepy: "MoviePy",
  mutagen: "Mutagen",
  requests: "Requests",
  pytubefix: "PyTubefix",
  pygame: "PyGame"
};
function StatusPage() {
  const [status, setStatus] = reactExports.useState(null);
  reactExports.useEffect(() => {
    bridge.getSystemStatus().then(setStatus);
  }, []);
  if (!status) {
    return /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex items-center justify-center py-20", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground", children: "Cargando estado del sistema..." }) });
  }
  const depEntries = Object.entries(DEP_NAMES);
  const okCount = depEntries.filter(([k]) => status.dependencies[k]).length;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-8", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { className: "flex items-center gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-accent grid place-items-center glow-violet", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-7 h-7 text-primary-foreground" }) }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-3xl sm:text-4xl font-bold", children: "Estado del Sistema" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-1", children: "Verifica las dependencias y recursos de EKHO" })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-3 gap-4", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "glass rounded-2xl p-5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-sm text-muted-foreground", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Music2, { className: "w-4 h-4" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Biblioteca" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-3xl font-semibold mt-4", children: status.music_count }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground mt-3", children: "canciones en tu biblioteca" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "glass rounded-2xl p-5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-sm text-muted-foreground", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-4 h-4" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Dependencias" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-3xl font-semibold mt-4", children: [
          okCount,
          "/",
          depEntries.length
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground mt-3", children: "librerias instaladas" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "glass rounded-2xl p-5", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-2 text-sm text-muted-foreground", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Sparkles, { className: "w-4 h-4" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "FFmpeg" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-3xl font-semibold mt-4", children: status.ffmpeg ? "Si" : "No" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground mt-3", children: "motor de conversion de audio" })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "glass rounded-2xl p-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-base font-semibold mb-5", children: "Dependencias del Sistema" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-3", children: depEntries.map(([key, label]) => {
        const ok = status.dependencies[key];
        return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between p-3 rounded-lg bg-muted/20", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", children: label }),
          ok ? /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1 text-xs text-green-400", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3.5 h-3.5" }),
            " Instalado"
          ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1 text-xs text-red-400", children: [
            /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-3.5 h-3.5" }),
            " No instalado"
          ] })
        ] }, key);
      }) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "glass rounded-2xl p-6", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-base font-semibold mb-5", children: "Componentes del Sistema" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "space-y-3", children: /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between p-3 rounded-lg bg-muted/20", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono", children: "FFmpeg" }),
        status.ffmpeg ? /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1 text-xs text-green-400", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3.5 h-3.5" }),
          " Disponible"
        ] }) : /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1 text-xs text-red-400", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(X, { className: "w-3.5 h-3.5" }),
          " No encontrado en PATH"
        ] })
      ] }) })
    ] })
  ] });
}
export {
  StatusPage as component
};
