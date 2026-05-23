import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { c as createLucideIcon, b as bridge, L as Link } from "./router-DfCIbLxF.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
const __iconNode = [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "M12 5v14", key: "s699le" }]
];
const Plus = createLucideIcon("plus", __iconNode);
function LibraryPage() {
  const [playlists, setPlaylists] = reactExports.useState([]);
  reactExports.useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
  }, []);
  const totalSongs = 0;
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-8", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-4xl font-bold", children: "Mi Biblioteca" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-sm text-muted-foreground mt-1 font-mono", children: [
        playlists.length,
        " playlists · ",
        totalSongs,
        " canciones"
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5", children: [
      playlists.map((p) => /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/library/$playlistId", params: {
        playlistId: p.id
      }, className: "glass rounded-2xl overflow-hidden hover:-translate-y-1 transition group", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "relative aspect-square overflow-hidden bg-muted/40 flex items-center justify-center", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-6xl", children: "♪" }),
          p.id === "all" || p.id === "favorites" ? /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "absolute top-3 right-3 px-2.5 py-1 rounded-full bg-primary/30 backdrop-blur border border-primary/50 text-xs font-medium flex items-center gap-1", children: "♪ Coleccion" }) : null
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "p-4", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("h3", { className: "font-semibold text-lg", children: p.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground mt-1 line-clamp-1", children: p.description }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex justify-between text-xs text-muted-foreground mt-3 font-mono", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: p.is_public ? "Publica" : "Privada" }) })
        ] })
      ] }, p.id)),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("button", { type: "button", className: "glass rounded-2xl border-dashed border-2 border-border/60 flex flex-col items-center justify-center min-h-[280px] hover:bg-muted/20 transition group", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-16 h-16 rounded-full bg-muted/40 grid place-items-center mb-3 group-hover:bg-primary/20 transition", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Plus, { className: "w-7 h-7 text-muted-foreground group-hover:text-primary" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-semibold", children: "Crear Nueva Playlist" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground mt-1", children: "Agrupa tus canciones favoritas" })
      ] })
    ] })
  ] });
}
export {
  LibraryPage as component
};
