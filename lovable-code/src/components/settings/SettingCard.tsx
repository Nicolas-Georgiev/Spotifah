interface Props {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export function SettingCard({ title, subtitle, children }: Props) {
  return (
    <section className="glass rounded-2xl p-5 sm:p-6">
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>
        <div className="mt-4">{children}</div>
      </div>
    </section>
  );
}
