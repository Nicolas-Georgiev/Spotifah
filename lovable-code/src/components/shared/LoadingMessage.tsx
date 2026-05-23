interface Props {
  message?: string;
}

export function LoadingMessage({ message = "Cargando..." }: Props) {
  return (
    <div className="flex items-center justify-center py-20">
      <p className="text-muted-foreground">{message}</p>
    </div>
  );
}
