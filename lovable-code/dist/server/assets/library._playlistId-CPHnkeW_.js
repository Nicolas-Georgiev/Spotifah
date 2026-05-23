import { r as reactExports, V as jsxRuntimeExports } from "./server-COpmIOi8.js";
import { c as createLucideIcon, R as Route, b as bridge, L as Link } from "./router-DfCIbLxF.js";
import { C as Clock } from "./clock-CDYGzDXS.js";
import "node:async_hooks";
import "node:stream/web";
import "node:stream";
const __iconNode$1 = [["path", { d: "m15 18-6-6 6-6", key: "1wnfg3" }]];
const ChevronLeft = createLucideIcon("chevron-left", __iconNode$1);
const __iconNode = [
  [
    "path",
    {
      d: "M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z",
      key: "10ikf1"
    }
  ]
];
const Play = createLucideIcon("play", __iconNode);
function fmtDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
function PlaylistDetail() {
  const {
    playlist
  } = Route.useLoaderData();
  const [songs, setSongs] = reactExports.useState([]);
  const [playingId, setPlayingId] = reactExports.useState(null);
  reactExports.useEffect(() => {
    bridge.getPlaylistSongs(playlist.id).then(setSongs);
  }, [playlist.id]);
  const totalSecs = songs.reduce((acc, s) => acc + s.duration, 0);
  const totalMin = Math.round(totalSecs / 60);
  const handlePlay = (songId) => {
    setPlayingId(songId);
    bridge.playSong(songId);
  };
  return /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "space-y-8", children: [
    /* @__PURE__ */ jsxRuntimeExports.jsxs(Link, { to: "/library", className: "inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(ChevronLeft, { className: "w-4 h-4" }),
      " Volver a Biblioteca"
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("header", { className: "flex flex-col sm:flex-row gap-6 items-center sm:items-end", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-40 h-40 sm:w-48 sm:h-48 rounded-2xl bg-primary/20 flex items-center justify-center text-6xl shadow-2xl", children: "♪" }),
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "text-center sm:text-left flex-1", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "flex flex-wrap items-center gap-2 justify-center sm:justify-start", children: /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "px-2.5 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary border border-primary/40", children: "Playlist" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("h1", { className: "text-4xl sm:text-6xl font-bold mt-3", children: playlist.name }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-muted-foreground mt-2", children: playlist.description }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("p", { className: "text-xs text-muted-foreground font-mono mt-3", children: [
          songs.length,
          " canciones · ",
          totalMin,
          " min"
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("button", { onClick: () => songs.length > 0 && handlePlay(songs[0].id), className: "inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground font-semibold glow-violet hover:scale-105 transition", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 fill-current" }),
      " Reproducir todo"
    ] }),
    /* @__PURE__ */ jsxRuntimeExports.jsxs("section", { className: "glass rounded-2xl overflow-hidden", children: [
      /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "hidden md:grid grid-cols-[40px_3fr_2fr_2fr_120px_80px] gap-4 px-5 py-3 text-xs font-mono text-muted-foreground border-b border-border uppercase tracking-wider", children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "#" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Titulo" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Artista" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Album" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: "Origen" }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "flex justify-end", children: /* @__PURE__ */ jsxRuntimeExports.jsx(Clock, { className: "w-3.5 h-3.5" }) })
      ] }),
      /* @__PURE__ */ jsxRuntimeExports.jsx("ul", { children: songs.map((s, i) => /* @__PURE__ */ jsxRuntimeExports.jsxs("li", { onClick: () => handlePlay(s.id), className: `grid grid-cols-[40px_3fr_2fr_2fr_120px_80px] gap-4 px-5 py-3 items-center hover:bg-muted/30 transition group cursor-pointer ${playingId === s.id ? "bg-primary/10" : ""}`, children: [
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm font-mono text-muted-foreground group-hover:hidden", children: i + 1 }),
        /* @__PURE__ */ jsxRuntimeExports.jsx(Play, { className: "w-4 h-4 hidden group-hover:block fill-current text-primary" }),
        /* @__PURE__ */ jsxRuntimeExports.jsxs("div", { className: "flex items-center gap-3 min-w-0", children: [
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "w-10 h-10 rounded bg-muted/40 flex items-center justify-center shrink-0", children: s.cover_url ? /* @__PURE__ */ jsxRuntimeExports.jsx("img", { src: s.cover_url, alt: "", className: "w-full h-full rounded object-cover" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-lg", children: "♪" }) }),
          /* @__PURE__ */ jsxRuntimeExports.jsx("div", { className: "min-w-0", children: /* @__PURE__ */ jsxRuntimeExports.jsx("p", { className: "text-sm font-medium truncate", children: s.title }) })
        ] }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm text-muted-foreground truncate", children: s.artist }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm text-muted-foreground truncate", children: s.album }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { children: s.source === "spotify" ? /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "px-2.5 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30", children: "spotify" }) : /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30", children: s.source || "local" }) }),
        /* @__PURE__ */ jsxRuntimeExports.jsx("span", { className: "text-sm text-muted-foreground font-mono text-right", children: fmtDuration(s.duration) })
      ] }, s.id)) })
    ] })
  ] });
}
export {
  PlaylistDetail as component
};
