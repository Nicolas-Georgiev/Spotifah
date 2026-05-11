import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";

import appCss from "../styles.css?url";
import { EkhoLayout } from "../components/EkhoLayout";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="max-w-md text-center glass rounded-2xl p-10">
        <h1 className="text-7xl font-mono font-bold text-primary text-glow-violet">404</h1>
        <p className="mt-4 text-muted-foreground">Esta pista no existe en la biblioteca.</p>
        <Link to="/" className="mt-6 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90">
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="max-w-md text-center glass rounded-2xl p-10">
        <h1 className="text-xl font-semibold">Algo salió mal</h1>
        <p className="mt-2 text-sm text-muted-foreground">{error.message}</p>
        <button
          onClick={() => { router.invalidate(); reset(); }}
          className="mt-6 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >Reintentar</button>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "EKHO — Tu plataforma musical todo-en-uno" },
      { name: "description", content: "Convierte canciones de Spotify y YouTube a MP3, reproduce tu biblioteca y monitorea el sistema." },
      { property: "og:title", content: "EKHO — Tu plataforma musical todo-en-uno" },
      { property: "og:description", content: "Convierte canciones de Spotify y YouTube a MP3, reproduce tu biblioteca y monitorea el sistema." },
      { property: "og:type", content: "website" },
      { name: "twitter:title", content: "EKHO — Tu plataforma musical todo-en-uno" },
      { name: "twitter:description", content: "Convierte canciones de Spotify y YouTube a MP3, reproduce tu biblioteca y monitorea el sistema." },
      { property: "og:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/77bd06d9-5789-4f45-ba30-ab84239617f6/id-preview-ae7b8adc--c5372792-9e49-4b31-91c6-c37cadc31a13.lovable.app-1778518097035.png" },
      { name: "twitter:image", content: "https://pub-bb2e103a32db4e198524a2e9ed8f35b4.r2.dev/77bd06d9-5789-4f45-ba30-ab84239617f6/id-preview-ae7b8adc--c5372792-9e49-4b31-91c6-c37cadc31a13.lovable.app-1778518097035.png" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <head><HeadContent /></head>
      <body>{children}<Scripts /></body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <EkhoLayout />
    </QueryClientProvider>
  );
}
