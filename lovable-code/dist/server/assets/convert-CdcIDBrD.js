import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { c as createLucideIcon, D as Download, M as Music2, b as bridge } from "./router-DfCIbLxF.js";
import { C as Check } from "./check-Bh0eiIFu.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
const __iconNode$3 = [
  ["path", { d: "M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z", key: "p7xjir" }]
];
const Cloud = createLucideIcon("cloud", __iconNode$3);
const __iconNode$2 = [
  ["path", { d: "M9 17H7A5 5 0 0 1 7 7h2", key: "8i5ue5" }],
  ["path", { d: "M15 7h2a5 5 0 1 1 0 10h-2", key: "1b9ql8" }],
  ["line", { x1: "8", x2: "16", y1: "12", y2: "12", key: "1jonct" }]
];
const Link2 = createLucideIcon("link-2", __iconNode$2);
const __iconNode$1 = [["path", { d: "M21 12a9 9 0 1 1-6.219-8.56", key: "13zald" }]];
const LoaderCircle = createLucideIcon("loader-circle", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17",
      key: "1q2vi4"
    }
  ],
  ["path", { d: "m10 15 5-3-5-3z", key: "1jp15x" }]
];
const Youtube = createLucideIcon("youtube", __iconNode);
function detectPlatform(url) {
  const u = url.toLowerCase();
  if (u.includes("youtube.com") || u.includes("youtu.be")) return "youtube";
  if (u.includes("spotify.com")) return "spotify";
  if (u.includes("soundcloud.com")) return "soundcloud";
  return null;
}
function ConvertPage() {
  const [url, setUrl] = reactExports.useState("");
  const [items, setItems] = reactExports.useState([]);
  const [busy, setBusy] = reactExports.useState(false);
  const convert = async () => {
    const platform = detectPlatform(url);
    if (!platform || busy) return;
    setBusy(true);
    const id = Date.now();
    const entryUrl = url;
    setUrl("");
    setItems((prev) => [{
      id,
      title: entryUrl,
      platform,
      status: "processing"
    }, ...prev]);
    try {
      let result;
      if (platform === "youtube") {
        result = await bridge.convertYoutube(entryUrl);
      } else if (platform === "spotify") {
        result = await bridge.convertSpotify(entryUrl);
      } else {
        throw new Error("Plataforma no soportada");
      }
      if (result.ok) {
        setItems((prev) => prev.map((i) => i.id === id ? {
          ...i,
          status: "done"
        } : i));
      } else {
        setItems((prev) => prev.map((i) => i.id === id ? {
          ...i,
          status: "error",
          error: result.error
        } : i));
      }
    } catch (e) {
      setItems((prev) => prev.map((i) => i.id === id ? {
        ...i,
        status: "error",
        error: e.message
      } : i));
    } finally {
      setBusy(false);
    }
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-8", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-4xl font-bold", children: "Conversor de Enlaces" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-2", children: "Convierte canciones de YouTube, Spotify y SoundCloud a MP3" })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "glass rounded-2xl p-5", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col sm:flex-row gap-3", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative flex-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Link2, { className: "w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("input", { value: url, onChange: (e) => setUrl(e.target.value), onKeyDown: (e) => e.key === "Enter" && convert(), placeholder: "Pega aqui el enlace de YouTube, Spotify o SoundCloud...", className: "w-full bg-input/60 border border-border rounded-lg pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("button", { onClick: convert, disabled: !url.trim() || busy, className: "px-6 py-3 rounded-lg font-medium bg-primary text-primary-foreground glow-violet hover:opacity-90 inline-flex items-center gap-2 justify-center disabled:opacity-50", children: [
          busy ? /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-4 h-4 animate-spin" }) : /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-4 h-4" }),
          "Convertir"
        ] })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3 mt-4 text-xs flex-wrap", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-muted-foreground", children: "Plataformas soportadas:" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/15 text-red-400 border border-red-500/30", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Youtube, { className: "w-3 h-3" }),
          " YouTube"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/15 text-green-400 border border-green-500/30", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Music2, { className: "w-3 h-3" }),
          " Spotify"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/30", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Cloud, { className: "w-3 h-3" }),
          " SoundCloud"
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-xl font-semibold mb-3", children: "Conversiones Recientes" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "glass rounded-2xl p-6 min-h-[220px]", children: items.length === 0 ? /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex flex-col items-center justify-center py-10 text-center", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-14 h-14 rounded-full bg-muted/40 grid place-items-center mb-4", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Download, { className: "w-6 h-6 text-muted-foreground" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground", children: "No hay conversiones todavia" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground/70 mt-2", children: "Pega un enlace arriba para comenzar" })
      ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { className: "space-y-2", children: items.map((i) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { className: "flex items-center gap-3 p-3 rounded-lg bg-muted/20", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "w-9 h-9 rounded-md bg-primary/15 grid place-items-center", children: [
          i.platform === "youtube" && /* @__PURE__ */ jsxRuntimeExports.jsx(Youtube, { className: "w-4 h-4 text-red-400" }),
          i.platform === "spotify" && /* @__PURE__ */ jsxRuntimeExports.jsx(Music2, { className: "w-4 h-4 text-green-400" }),
          i.platform === "soundcloud" && /* @__PURE__ */ jsxRuntimeExports.jsx(Cloud, { className: "w-4 h-4 text-yellow-400" })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "flex-1 truncate text-sm font-mono", children: i.title }),
        i.status === "processing" ? /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs text-muted-foreground inline-flex items-center gap-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(LoaderCircle, { className: "w-3 h-3 animate-spin" }),
          " Procesando..."
        ] }) : i.status === "done" ? /* @__PURE__ */ jsxRuntimeExports.jsxs("span", { className: "text-xs text-green-400 inline-flex items-center gap-1", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Check, { className: "w-3 h-3" }),
          " Listo"
        ] }) : /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-xs text-red-400", title: i.error, children: "Error" })
      ] }, i.id)) }) })
    ] })
  ] });
}
export {
  ConvertPage as component
};
