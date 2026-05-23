interface Props {
  message?: string;
  error?: string | null;
  onRetry?: () => void;
}

export function SplashScreen({ message = "Cargando tu biblioteca...", error, onRetry }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center" style={{ background: "var(--gradient-bg)" }}>
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
          <h1 className="text-6xl sm:text-7xl font-bold text-primary text-glow-violet select-none">
            EKHO
          </h1>
          <div className="absolute -inset-6 rounded-full bg-primary/5 blur-3xl animate-pulse-glow" />
        </div>

        {!error && (
          <div className="flex items-center gap-1 h-8 mt-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="w-1.5 bg-primary rounded-full eq-bar"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        )}

        <p className="text-sm text-muted-foreground font-mono animate-pulse">
          {error || message}
        </p>

        {error && onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition"
          >
            Reintentar
          </button>
        )}
      </div>
    </div>
  );
}
