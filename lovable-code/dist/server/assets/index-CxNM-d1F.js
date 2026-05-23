import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { b as bridge, L as Link } from "./router-DfCIbLxF.js";
import { C as Clock } from "./clock-CDYGzDXS.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
function getGreeting() {
  const h = (/* @__PURE__ */ new Date()).getHours();
  if (h < 6) return "Buenas noches";
  if (h < 13) return "Buenos dias";
  if (h < 20) return "Buenas tardes";
  return "Buenas noches";
}
function Home() {
  const [playlists, setPlaylists] = reactExports.useState([]);
  const [songs, setSongs] = reactExports.useState([]);
  reactExports.useEffect(() => {
    bridge.getPlaylists().then(setPlaylists);
    bridge.getSongs().then(setSongs);
  }, []);
  const greeting = getGreeting();
  const recent = songs.slice(0, 4);
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-10", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-4xl sm:text-5xl font-bold", children: greeting }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground mt-2", children: "Que te gustaria escuchar hoy?" })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("h2", { className: "text-lg font-semibold mb-4", children: "Acceso Rapido" }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3", children: playlists.map((p) => /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/library/$playlistId", params: {
        playlistId: p.id
      }, className: "glass rounded-xl p-3 flex items-center gap-4 hover:bg-muted/30 transition group", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-14 h-14 rounded-md bg-primary/20 flex items-center justify-center text-lg shrink-0", children: "♪" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex-1 min-w-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "font-semibold truncate", children: p.name }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-xs text-muted-foreground", children: p.description })
        ] })
      ] }, p.id)) })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center justify-between mb-4", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsxs("h2", { className: "text-lg font-semibold flex items-center gap-2", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-4 h-4 text-muted-foreground" }),
          "Canciones en tu Biblioteca"
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Link, { to: "/library", className: "text-xs text-muted-foreground hover:text-foreground", children: "Ver todas" })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4", children: recent.map((s) => /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/library/$playlistId", params: {
        playlistId: "all"
      }, className: "group", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "relative rounded-xl overflow-hidden aspect-square bg-muted/40 flex items-center justify-center", children: s.cover_url ? /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: s.cover_url, alt: s.title, className: "w-full h-full object-cover transition group-hover:scale-105" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-4xl", children: "♪" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "mt-3 font-semibold truncate", children: s.title }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm text-muted-foreground truncate", children: s.artist })
      ] }, s.id)) })
    ] })
  ] });
}
export {
  Home as component
};
